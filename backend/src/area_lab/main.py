import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from area_lab.api.routes import router
from area_lab.application.services import ExperimentService
from area_lab.domain.errors import AreaLabError, InvalidConfiguration, NotFound, QueueFull
from area_lab.domain.ports import ExperimentRepository, SynthesisGateway
from area_lab.infrastructure.catalog import build_catalog
from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.sqlite_repository import SQLiteExperimentRepository
from area_lab.infrastructure.synthesis import GhdlYosysSynthesis


def create_app(
    settings: Settings | None = None,
    repository: ExperimentRepository | None = None,
    synthesis: SynthesisGateway | None = None,
) -> FastAPI:
    configuration = settings or Settings()
    store = repository or SQLiteExperimentRepository(configuration.data_dir / "experiments.sqlite3")
    gateway = synthesis or GhdlYosysSynthesis(configuration)
    designs, technologies = build_catalog(configuration.assets_dir)
    service = ExperimentService(store, gateway, designs, technologies, configuration.queue_capacity)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        store.interrupt_unfinished()
        worker = asyncio.create_task(service.work(), name="synthesis-worker")
        yield
        # Drain already authorized work before closing the single process.
        # Each subprocess has a hard timeout; new HTTP requests have stopped.
        await service.queue.join()
        worker.cancel()
        with suppress(asyncio.CancelledError):
            await worker

    app = FastAPI(
        title="ASIC Area Lab",
        version="0.1.0",
        description=(
            "Área de celdas de las 11 DPU registradas del repositorio; sin diseño físico."
        ),
        lifespan=lifespan,
    )
    app.state.service = service
    app.state.settings = configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuration.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(AreaLabError)
    async def domain_exception(_request: Request, error: AreaLabError):
        status = {InvalidConfiguration: 400, NotFound: 404, QueueFull: 429}.get(type(error), 500)
        return JSONResponse(status_code=status, content={"detail": str(error)})

    @app.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok", "version": "0.1.0"}

    app.include_router(router)
    frontend = configuration.frontend_dir
    if (frontend / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=frontend / "assets"), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def index():
        if (frontend / "index.html").is_file():
            return FileResponse(frontend / "index.html")
        return JSONResponse(
            {
                "message": "API disponible. Inicia Vite para desarrollo o compila frontend.",
                "docs": "/docs",
            }
        )

    @app.get("/favicon.svg", include_in_schema=False)
    def favicon():
        path = Path(frontend) / "favicon.svg"
        if path.is_file():
            return FileResponse(path)
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    return app


logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
