from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from area_lab.domain.models import JobStatus


class CreateExperimentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    design_id: Literal[
        "int8_16",
        "int16_32",
        "fxp8_16",
        "fxp16_32",
        "fp8",
        "fp16",
        "fp32",
        "posit8",
        "posit16",
        "posit32",
        "lns16",
    ] = "int8_16"
    technology_id: Literal["ihp130", "nangate15", "nangate45"]


class ExperimentResponse(BaseModel):
    id: str
    design_id: str
    technology_id: str
    status: JobStatus
    stage: str
    created_at: str
    updated_at: str
    error: str | None
    report: dict[str, Any] | None


class ErrorResponse(BaseModel):
    detail: str
