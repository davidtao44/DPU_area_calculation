from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AREA_LAB_", extra="ignore")

    assets_dir: Path = PROJECT_ROOT / "assets"
    data_dir: Path = PROJECT_ROOT / "data"
    frontend_dir: Path = PROJECT_ROOT / "frontend" / "dist"
    toolchain_bin: Path | None = None
    command_timeout_seconds: int = Field(default=900, gt=0)
    queue_capacity: int = 4
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
