import io
import zipfile
from dataclasses import asdict
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse

from area_lab.api.schemas import CreateExperimentRequest, ErrorResponse, ExperimentResponse
from area_lab.application.services import ExperimentService
from area_lab.infrastructure.synthesis import ARTIFACTS

router = APIRouter(prefix="/api/v1")


def get_service(request: Request) -> ExperimentService:
    return request.app.state.service


Service = Annotated[ExperimentService, Depends(get_service)]


@router.get("/catalog", tags=["catalog"])
def catalog(service: Service):
    return {
        "designs": [asdict(item) for item in service.designs.values()],
        "technologies": [asdict(item) for item in service.technologies.values()],
        "scope": "standard_cell_area_only",
    }


@router.post(
    "/experiments",
    response_model=ExperimentResponse,
    status_code=202,
    tags=["experiments"],
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}},
)
async def create_experiment(body: CreateExperimentRequest, service: Service):
    return (await service.submit(body.design_id, body.technology_id)).to_dict()


@router.get("/experiments", response_model=list[ExperimentResponse], tags=["experiments"])
def list_experiments(service: Service):
    return [experiment.to_dict() for experiment in service.list()]


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse, tags=["experiments"])
def get_experiment(experiment_id: UUID, service: Service):
    return service.get(str(experiment_id)).to_dict()


@router.get("/experiments/{experiment_id}/logs", tags=["artifacts"])
def get_logs(experiment_id: UUID, request: Request, service: Service):
    service.get(str(experiment_id))
    path = request.app.state.settings.data_dir / "runs" / str(experiment_id) / "run.log"
    if not path.exists():
        return {"content": "", "truncated": False}
    with path.open("rb") as stream:
        size = path.stat().st_size
        stream.seek(max(0, size - 100_000))
        content = stream.read().decode(errors="replace")
    return {"content": content, "truncated": size > 100_000}


@router.get("/experiments/{experiment_id}/artifacts", tags=["artifacts"])
def download_artifacts(experiment_id: UUID, request: Request, service: Service):
    experiment = service.get(str(experiment_id))
    if experiment.status in ("queued", "running"):
        raise HTTPException(409, "La evaluación sigue en ejecución.")
    directory = request.app.state.settings.data_dir / "runs" / str(experiment_id)
    if not directory.exists():
        raise HTTPException(404, "Esta evaluación todavía no generó archivos.")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in ARTIFACTS:
            path = directory / name
            if path.is_file():
                archive.write(path, arcname=name)
        for path in sorted((directory / "sources").rglob("*.vhd")):
            archive.write(path, arcname=str(path.relative_to(directory)))
        for path in sorted((directory / "compilation").glob("*.vhdl")):
            archive.write(path, arcname=str(path.relative_to(directory)))
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="area-{experiment_id}.zip"'},
    )


@router.get("/experiments/{experiment_id}/report.csv", tags=["artifacts"])
def download_csv(experiment_id: UUID, request: Request, service: Service):
    experiment = service.get(str(experiment_id))
    if experiment.status != "succeeded":
        raise HTTPException(409, "Todavía no hay un reporte válido.")
    path = request.app.state.settings.data_dir / "runs" / str(experiment_id) / "report.csv"
    return FileResponse(path, media_type="text/csv", filename=f"area-{experiment_id}.csv")
