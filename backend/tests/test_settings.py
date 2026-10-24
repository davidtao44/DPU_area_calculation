import pytest
from pydantic import ValidationError

from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.synthesis import GhdlYosysSynthesis


def test_command_timeout_environment_reaches_process_runner(monkeypatch):
    monkeypatch.setenv("AREA_LAB_COMMAND_TIMEOUT_SECONDS", "3600")
    settings = Settings()
    assert settings.command_timeout_seconds == 3600
    assert GhdlYosysSynthesis(settings).runner.timeout == 3600


@pytest.mark.parametrize("value", ["0", "-1", "invalid"])
def test_command_timeout_rejects_invalid_values(monkeypatch, value):
    monkeypatch.setenv("AREA_LAB_COMMAND_TIMEOUT_SECONDS", value)
    with pytest.raises(ValidationError):
        Settings()
