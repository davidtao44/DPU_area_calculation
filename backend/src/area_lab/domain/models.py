from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class Design:
    id: str
    label: str
    numeric_format: str
    top: str
    source_files: tuple[str, ...]
    wrapper_file: str
    declared_register_bits: int
    library: str
    operand_bits: int
    result_bits: int
    family: str
    reference: str
    expected_flip_flops: int | None
    numeric_notes: str
    compilation: str


@dataclass(frozen=True)
class Technology:
    id: str
    label: str
    node_nm: int
    corner: str
    voltage_v: float
    temperature_c: float
    liberty_file: str | None
    available: bool
    reason: str | None = None
    area_unit: str = "um2"
    unit_basis: str = "Library documentation convention; not a Liberty-declared SI unit."


@dataclass
class Experiment:
    id: str
    design_id: str
    technology_id: str
    status: JobStatus = JobStatus.QUEUED
    stage: str = "queued"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    error: str | None = None
    report: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Experiment":
        return cls(**{**value, "status": JobStatus(value["status"])})
