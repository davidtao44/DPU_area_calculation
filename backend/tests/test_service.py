import asyncio

import pytest

from area_lab.application.services import ExperimentService
from area_lab.domain.errors import QueueFull
from area_lab.infrastructure.catalog import build_catalog
from area_lab.infrastructure.settings import Settings
from area_lab.infrastructure.sqlite_repository import SQLiteExperimentRepository


def test_queue_capacity_does_not_create_orphan_jobs(tmp_path):
    designs, technologies = build_catalog(Settings().assets_dir)
    repository = SQLiteExperimentRepository(tmp_path / "jobs.sqlite3")
    service = ExperimentService(repository, None, designs, technologies, queue_capacity=1)

    async def scenario():
        await service.submit("int8_16", "ihp130")
        with pytest.raises(QueueFull):
            await service.submit("int8_16", "ihp130")

    asyncio.run(scenario())
    assert len(repository.list()) == 1
