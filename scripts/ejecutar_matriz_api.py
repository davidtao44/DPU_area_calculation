"""Execute the catalog through HTTP, excluding LNS, and download each API ZIP.

Runs one job at a time. Resume the same output directory without reposting jobs.
Use inside the existing container when the host runner restricts HTTP sockets.
"""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile


def event(kind, **values):
    print(json.dumps({"event": kind, **values}, ensure_ascii=False), flush=True)


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def request(base, path, body=None):
    data = None if body is None else json.dumps(body).encode()
    req = Request(base + path, data=data, headers={"Content-Type": "application/json"})
    # Never retry a POST: an ambiguous response must not create duplicate jobs.
    with urlopen(req, timeout=20) as response:
        return json.load(response)


def get(base, path):
    for attempt in range(5):
        try:
            return request(base, path)
        except (URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(3)


def host_memory():
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        name, value = line.split(":", 1)
        values[name] = int(value.split()[0]) / 1024
    return values["MemAvailable"], values["SwapFree"]


def stop_own_tools(identifier, data_root):
    """Stop only this experiment's EDA process groups in a resource emergency."""
    directory = (data_root / "runs" / identifier).resolve()
    groups = set()
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            if (path / "cwd").resolve() == directory:
                group = os.getpgid(int(path.name))
                if group != os.getpgrp():
                    groups.add(group)
        except (OSError, RuntimeError):
            continue
    for group in groups:
        try:
            os.killpg(group, signal.SIGTERM)
        except ProcessLookupError:
            pass
    return sorted(groups)


def await_capacity(args, design):
    threshold = max(args.min_available_mib, 1536 if design == "fxp16_32" else 0)
    last_event = 0
    while True:
        active = [j for j in get(args.base_url, "/api/v1/experiments") if j["status"] in ("queued", "running")]
        available, swap = host_memory()
        free = shutil.disk_usage(args.output).free / 1024**3
        if free < args.min_disk_gib:
            raise RuntimeError(f"Disk guard: only {free:.2f} GiB free; no new job submitted.")
        if not active and available >= threshold:
            return
        if time.monotonic() - last_event >= 30:
            event("waiting_capacity", design=design, available_mib=round(available), required_mib=threshold,
                  swap_free_mib=round(swap), active=[j["id"] for j in active])
            last_event = time.monotonic()
        time.sleep(5)


def download(args, case, job):
    directory = args.output / case["design_id"] / case["technology_id"]
    directory.mkdir(parents=True, exist_ok=True)
    name = f'{case["design_id"]}__{case["technology_id"]}__{case["id"]}.zip'
    destination = directory / name
    temporary = destination.with_suffix(".zip.part")
    for attempt in range(3):
        try:
            with urlopen(args.base_url + f'/api/v1/experiments/{case["id"]}/artifacts', timeout=120) as response, temporary.open("wb") as stream:
                shutil.copyfileobj(response, stream, length=1024 * 1024)
            break
        except (URLError, TimeoutError):
            temporary.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(3)
    with ZipFile(temporary) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Corrupt downloaded ZIP")
        names = set(archive.namelist())
        if job["status"] == "succeeded":
            required = {"report.json", "report.csv", "manifest.json", "mapped.v", "mapped.json", "design.v",
                        "stat.json", "synth.ys", "run.log", "stimuli.txt", "rtl-results.txt", "vectors.txt",
                        "validation_tb.vhd", "validation_tb.v", "simulation_cells.ys", "cells_sim.v"}
            if not required <= names:
                raise RuntimeError(f"Incomplete ZIP: {required - names}")
            report = json.loads(archive.read("report.json"))
            if report != job["report"] or report["design_id"] != case["design_id"] or report["technology_id"] != case["technology_id"]:
                raise RuntimeError("API report and ZIP mismatch")
            if report["validation"]["rtl"] != "passed" or report["validation"]["mapped"] != "passed" or report["validation"]["vectors"] != 256:
                raise RuntimeError("Functional validation not confirmed")
            manifest = json.loads(archive.read("manifest.json"))
            if manifest != report["manifest"]:
                raise RuntimeError("ZIP manifest mismatch")
            for relative, digest in manifest["source_sha256"].items():
                if hashlib.sha256(archive.read("sources/" + relative)).hexdigest() != digest:
                    raise RuntimeError("Source snapshot mismatch")
            for filename, key in [("stimuli.txt", "stimuli_sha256"), ("rtl-results.txt", "rtl_results_sha256"), ("vectors.txt", "vectors_sha256")]:
                if hashlib.sha256(archive.read(filename)).hexdigest() != manifest["functional_test"][key]:
                    raise RuntimeError("Vector hash mismatch")
            for unit in manifest.get("compilation", {}).get("units", []):
                if hashlib.sha256(archive.read(unit["file"])).hexdigest() != unit["sha256"]:
                    raise RuntimeError("Compilation unit mismatch")
            if archive.read("run.log").count(b"VALIDATION_OK 256") != 2:
                raise RuntimeError("Validation markers absent from log")
    temporary.replace(destination)
    case["archive"] = destination.relative_to(args.output).as_posix()
    digest = hashlib.sha256()
    with destination.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    case["sha256"] = digest.hexdigest()
    case["bytes"] = destination.stat().st_size
    atomic_json(directory / (destination.stem + ".estado.json"), job)


def save(args, state):
    atomic_json(args.output / "ejecuciones.json", state)
    with (args.output / "resumen.csv").open("w", newline="") as stream:
        columns = ["design_id", "technology_id", "id", "status", "stage", "total_area", "area_unit",
                   "combinational_area", "sequential_area", "flip_flops", "duration_seconds", "archive", "sha256", "error"]
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(state["cases"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-available-mib", type=int, default=1024)
    parser.add_argument("--min-disk-gib", type=float, default=2)
    parser.add_argument("--data-root", type=Path, default=Path("/app/data"))
    args = parser.parse_args()
    args.base_url = args.base_url.rstrip("/")
    args.output.mkdir(parents=True, exist_ok=True)
    catalog = get(args.base_url, "/api/v1/catalog")
    atomic_json(args.output / "catalogo.json", catalog)
    designs = [d for d in catalog["designs"] if "lns" not in d["id"].lower()]
    # Schedule the only >900 MiB historical Yosys case after all lighter designs.
    designs.sort(key=lambda d: d["id"] == "fxp16_32")
    technologies = [t for t in catalog["technologies"] if t["available"]]
    if len(designs) != 10 or len(technologies) != 3:
        raise RuntimeError("Unexpected catalog: review before submitting a different matrix.")
    for item in [*designs, *technologies]:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", item["id"]):
            raise RuntimeError("Unsafe catalog ID")
    path = args.output / "ejecuciones.json"
    state = json.loads(path.read_text()) if path.exists() else {
        "base_url": args.base_url, "excluded_designs": ["lns16"], "planned": 30,
        "execution_policy": "sequential_api_only_with_resource_guards", "cases": []}
    cases = {(c["design_id"], c["technology_id"]): c for c in state["cases"]}
    for design in designs:
        for technology in technologies:
            key = (design["id"], technology["id"])
            case = cases.get(key)
            if case and case.get("archive") and (args.output / case["archive"]).is_file():
                continue
            if case is None:
                await_capacity(args, design["id"])
                job = request(args.base_url, "/api/v1/experiments", {"design_id": key[0], "technology_id": key[1]})
                case = {"design_id": key[0], "technology_id": key[1], "id": job["id"],
                        "status": job["status"], "stage": job["stage"], "created_at": job["created_at"]}
                state["cases"].append(case)
                cases[key] = case
                save(args, state)
                event("submitted", index=len(state["cases"]), total=30, **case)
            last_stage = None
            emergency = False
            while True:
                job = get(args.base_url, f'/api/v1/experiments/{case["id"]}')
                case.update(status=job["status"], stage=job["stage"], error=job.get("error"))
                if last_stage != (job["status"], job["stage"]):
                    save(args, state)
                    event("progress", design=key[0], technology=key[1], id=case["id"], status=job["status"], stage=job["stage"])
                    last_stage = (job["status"], job["stage"])
                if job["status"] not in ("queued", "running"):
                    break
                available, swap = host_memory()
                if not emergency and available < 256 and swap < 128:
                    groups = stop_own_tools(case["id"], args.data_root)
                    emergency = True
                    event("resource_emergency", experiment=case["id"], stopped_own_process_groups=groups,
                          available_mib=round(available), swap_free_mib=round(swap))
                time.sleep(3)
            if job["report"]:
                r = job["report"]
                case.update(total_area=r["total_area"], area_unit=r["area_unit"],
                            combinational_area=r["combinational_area"], sequential_area=r["sequential_area"],
                            flip_flops=r["cell_counts"]["flip_flop"], duration_seconds=r["duration_seconds"])
            download(args, case, job)
            save(args, state)
            event("downloaded", completed=sum(bool(c.get("archive")) for c in state["cases"]), **case)
            if emergency:
                raise RuntimeError("Stopped after own experiment hit resource emergency; remaining cases not submitted.")
    state["complete"] = len(state["cases"]) == 30 and all(c.get("archive") for c in state["cases"])
    state["succeeded"] = sum(c["status"] == "succeeded" for c in state["cases"])
    save(args, state)
    event("finished", complete=state["complete"], succeeded=state["succeeded"], cases=len(state["cases"]))


if __name__ == "__main__":
    main()
