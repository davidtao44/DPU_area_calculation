import asyncio
import io
import sys
import zipfile
from contextlib import asynccontextmanager, suppress
from uuid import uuid4

import httpx
import pytest

from area_lab.domain.models import Experiment, JobStatus
from area_lab.infrastructure.designs import DESIGNS
from area_lab.infrastructure.process_runner import ProcessRunner
from area_lab.infrastructure.settings import Settings
from area_lab.main import create_app


class FailingGateway:
    def run(self, *_args):
        raise RuntimeError("Intentional tool failure")


def test_artifact_zip_includes_nested_sources_for_other_designs(tmp_path):
    app = create_app(Settings(data_dir=tmp_path), synthesis=FailingGateway())
    identifier = str(uuid4())
    app.state.service.repository.save(
        Experiment(identifier, "fp16", "nangate45", status=JobStatus.FAILED, error="test")
    )
    directory = tmp_path / "runs" / identifier
    relative = "sources/rtl/fp16/needed_flopoco_files/FP16_FMA.vhd"
    source = directory / relative
    source.parent.mkdir(parents=True)
    source.write_text("-- source snapshot\n")
    unit = directory / "compilation/ieee_helper.vhdl"
    unit.parent.mkdir()
    unit.write_text("-- generated compilation unit\n")
    (directory / "run.log").write_text("test diagnostics\n")
    (directory / "yosys.log").write_text("full Yosys diagnostics\n")

    async def scenario():
        async with client_for(app) as client:
            response = await client.get(f"/api/v1/experiments/{identifier}/artifacts")
            assert response.status_code == 200
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                assert archive.read(relative) == source.read_bytes()
                assert archive.read("run.log") == b"test diagnostics\n"
                assert archive.read("yosys.log") == b"full Yosys diagnostics\n"
                assert archive.read("compilation/ieee_helper.vhdl") == unit.read_bytes()

    asyncio.run(asyncio.wait_for(scenario(), timeout=10))


@asynccontextmanager
async def client_for(app):
    async def timer():
        # Restricted runners can prohibit the asyncio self-pipe's cross-thread send.
        # A timer keeps the test loop responsive without changing application code.
        while True:
            await asyncio.sleep(0.01)

    tick = asyncio.create_task(timer())
    try:
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app), base_url="http://test"
            ) as client:
                yield client
    finally:
        await asyncio.get_running_loop().shutdown_default_executor()
        tick.cancel()
        with suppress(asyncio.CancelledError):
            await tick


def test_unavailable_technology_and_unknown_inputs_are_rejected(tmp_path):
    app = create_app(
        Settings(data_dir=tmp_path, assets_dir=tmp_path / "missing-assets"),
        synthesis=FailingGateway(),
    )

    async def scenario():
        async with client_for(app) as client:
            assert (await client.get("/api/health")).status_code == 200
            catalog = (await client.get("/api/v1/catalog")).json()
            technology = next(t for t in catalog["technologies"] if t["id"] == "nangate45")
            assert not technology["available"]
            response = await client.post("/api/v1/experiments", json={"technology_id": "nangate45"})
            assert response.status_code == 400
            assert "Liberty" in response.json()["detail"]
            response = await client.post("/api/v1/experiments", json={"technology_id": "unknown"})
            assert response.status_code == 422
            assert (await client.get(f"/api/v1/experiments/{uuid4()}")).status_code == 404
            assert (await client.get("/api/v1/experiments/not-a-uuid/logs")).status_code == 422
            assert (await client.get("/api/v1/experiments")).json() == []

    asyncio.run(asyncio.wait_for(scenario(), timeout=10))


def test_catalog_and_requests_support_all_reviewed_dpu_profiles(tmp_path):
    app = create_app(
        Settings(data_dir=tmp_path, queue_capacity=len(DESIGNS)), synthesis=FailingGateway()
    )

    async def scenario():
        async with client_for(app) as client:
            catalog = (await client.get("/api/v1/catalog")).json()
            assert {item["id"] for item in catalog["designs"]} == {d.id for d in DESIGNS}
            for design in DESIGNS:
                response = await client.post(
                    "/api/v1/experiments",
                    json={"design_id": design.id, "technology_id": "nangate45"},
                )
                assert response.status_code == 202
                assert response.json()["design_id"] == design.id
            invalid = await client.post(
                "/api/v1/experiments",
                json={"design_id": "../../other.vhd", "technology_id": "nangate45"},
            )
            assert invalid.status_code == 422
        assert len(app.state.service.list()) == len(DESIGNS)

    asyncio.run(asyncio.wait_for(scenario(), timeout=10))


@pytest.mark.parametrize("technology_id", ["ihp130", "nangate45"])
def test_failed_worker_persists_failure_without_area(tmp_path, technology_id):
    app = create_app(Settings(data_dir=tmp_path), synthesis=FailingGateway())

    async def scenario():
        async with client_for(app) as client:
            catalog = (await client.get("/api/v1/catalog")).json()
            technology = next(t for t in catalog["technologies"] if t["id"] == technology_id)
            assert technology["available"]
            response = await client.post(
                "/api/v1/experiments", json={"technology_id": technology_id}
            )
            assert response.status_code == 202
            identifier = response.json()["id"]
        experiment = app.state.service.get(identifier)
        assert experiment.status == "failed"
        assert experiment.report is None
        assert experiment.error == "Intentional tool failure"

    asyncio.run(asyncio.wait_for(scenario(), timeout=10))


def test_timeout_diagnostics_reach_api_logs_and_artifacts(tmp_path, caplog):
    class TimeoutGateway:
        def run(self, experiment_id, *_args):
            directory = tmp_path / "runs" / experiment_id
            directory.mkdir(parents=True)
            ProcessRunner(None, timeout=1).run(
                sys.executable,
                [
                    "-u",
                    "-c",
                    "import sys, time; print('synthesis stage diagnostic'); "
                    "print('synthesis stderr diagnostic', file=sys.stderr); time.sleep(20)",
                ],
                directory,
            )

    app = create_app(Settings(data_dir=tmp_path), synthesis=TimeoutGateway())

    async def scenario():
        async with client_for(app) as client:
            response = await client.post("/api/v1/experiments", json={"technology_id": "nangate45"})
            assert response.status_code == 202
            identifier = response.json()["id"]
            await asyncio.wait_for(app.state.service.queue.join(), timeout=5)
            experiment = (await client.get(f"/api/v1/experiments/{identifier}")).json()
            assert experiment["status"] == "failed"
            assert experiment["report"] is None
            assert "synthesis stage diagnostic" in experiment["error"]
            assert "synthesis stderr diagnostic" in experiment["error"]
            logs = (await client.get(f"/api/v1/experiments/{identifier}/logs")).json()
            assert "synthesis stage diagnostic" in logs["content"]
            artifacts = await client.get(f"/api/v1/experiments/{identifier}/artifacts")
            assert artifacts.status_code == 200
            with zipfile.ZipFile(io.BytesIO(artifacts.content)) as archive:
                assert "synthesis stage diagnostic" in archive.read("run.log").decode()
        assert "synthesis stage diagnostic" in caplog.text

    asyncio.run(asyncio.wait_for(scenario(), timeout=10))
