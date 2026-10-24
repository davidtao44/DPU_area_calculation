import asyncio
import logging
from uuid import uuid4

from area_lab.domain.errors import InvalidConfiguration, NotFound, QueueFull
from area_lab.domain.models import Design, Experiment, JobStatus, Technology, utc_now
from area_lab.domain.ports import ExperimentRepository, SynthesisGateway

logger = logging.getLogger(__name__)


class ExperimentService:
    """One bounded worker: EDA does not block HTTP or multiply CPU usage."""

    def __init__(
        self,
        repository: ExperimentRepository,
        synthesis: SynthesisGateway,
        designs: list[Design],
        technologies: list[Technology],
        queue_capacity: int = 4,
    ) -> None:
        self.repository = repository
        self.synthesis = synthesis
        self.designs = {item.id: item for item in designs}
        self.technologies = {item.id: item for item in technologies}
        self.queue: asyncio.Queue[str] = asyncio.Queue(maxsize=queue_capacity)

    async def submit(self, design_id: str, technology_id: str) -> Experiment:
        if design_id not in self.designs:
            raise InvalidConfiguration("Diseño no soportado.")
        technology = self.technologies.get(technology_id)
        if technology is None:
            raise InvalidConfiguration("Tecnología no soportada.")
        if not technology.available:
            raise InvalidConfiguration(technology.reason or "Biblioteca no disponible.")
        if self.queue.full():
            raise QueueFull("La cola está llena. Espera a que termine una evaluación.")
        experiment = Experiment(str(uuid4()), design_id, technology_id)
        self.repository.save(experiment)
        self.queue.put_nowait(experiment.id)
        return experiment

    def get(self, experiment_id: str) -> Experiment:
        experiment = self.repository.get(experiment_id)
        if experiment is None:
            raise NotFound("Evaluación no encontrada.")
        return experiment

    def list(self) -> list[Experiment]:
        return self.repository.list()

    async def work(self) -> None:
        while True:
            experiment_id = await self.queue.get()
            try:
                await asyncio.to_thread(self._execute, experiment_id)
            finally:
                self.queue.task_done()

    def _execute(self, experiment_id: str) -> None:
        experiment = self.get(experiment_id)
        experiment.status = JobStatus.RUNNING

        def progress(stage: str) -> None:
            experiment.stage = stage
            experiment.updated_at = utc_now()
            self.repository.save(experiment)

        progress("preparing")
        try:
            experiment.report = self.synthesis.run(
                experiment.id,
                self.designs[experiment.design_id],
                self.technologies[experiment.technology_id],
                progress,
            )
            experiment.status = JobStatus.SUCCEEDED
            experiment.stage = "completed"
        except Exception as exc:
            logger.exception("Synthesis failed: %s", experiment_id)
            experiment.status = JobStatus.FAILED
            experiment.stage = "failed"
            experiment.error = str(exc)
        experiment.updated_at = utc_now()
        self.repository.save(experiment)
