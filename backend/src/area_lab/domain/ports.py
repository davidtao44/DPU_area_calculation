from collections.abc import Callable
from typing import Any, Protocol

from area_lab.domain.models import Design, Experiment, Technology


class ExperimentRepository(Protocol):
    def save(self, experiment: Experiment) -> None: ...
    def get(self, experiment_id: str) -> Experiment | None: ...
    def list(self, limit: int = 100) -> list[Experiment]: ...
    def interrupt_unfinished(self) -> None: ...


class SynthesisGateway(Protocol):
    def run(
        self,
        experiment_id: str,
        design: Design,
        technology: Technology,
        progress: Callable[[str], None],
    ) -> dict[str, Any]: ...
