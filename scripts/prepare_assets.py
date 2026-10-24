"""Copy the existing RTL/libraries into this standalone example without editing originals."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    # This preparation command also works before installing the backend package.
    sys.path.insert(0, str(project / "backend/src"))
    from area_lab.infrastructure.designs import DESIGNS

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=project.parent)
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    source = workspace / "ParametricTensorCoreUnit/DPU_Performance_Area_Comparison/src"
    copies = []
    for design in DESIGNS:
        for relative in design.source_files:
            copies.append((source / Path(relative).relative_to("rtl"), relative))
        copies.append(
            (source / "wrappers" / Path(design.wrapper_file).name, design.wrapper_file)
        )
    copies.extend(
        [
            (
                workspace / "syn_libraries/130nm/lib/sg13g2_stdcell_typ_1p20V_25C.lib",
                "libraries/ihp130/cells.lib",
            ),
            (
                workspace
                / "syn_libraries/15nm/NLDM/NanGate_15nm_OCL_typical_conditional_nldm.lib",
                "libraries/nangate15/cells.lib",
            ),
            (
                workspace
                / "syn_libraries/NangateOpenCellLibrary_PDKv1_3_v2010_12"
                / "Front_End/Liberty/NLDM/NangateOpenCellLibrary_typical.lib",
                "libraries/nangate45/cells.lib",
            ),
        ]
    )
    records = []
    for original, relative in copies:
        destination = project / "assets" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)
        records.append(
            {
                "original": str(original.relative_to(workspace)),
                "snapshot": relative,
                "sha256": digest(destination),
            }
        )
    result = subprocess.run(
        ["git", "-C", str(workspace / "ParametricTensorCoreUnit"), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    manifest = {
        "repository_commit": result.stdout.strip() if result.returncode == 0 else None,
        "files": records,
        "note": "Hashes identify exact source bytes even if the repository has local changes.",
    }
    (project / "assets/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Prepared {len(records)} assets; original RTL and libraries were not modified."
    )


if __name__ == "__main__":
    main()
