from area_lab.domain.models import Experiment, JobStatus
from area_lab.infrastructure.sqlite_repository import SQLiteExperimentRepository


def test_restart_marks_all_unfinished_jobs_even_beyond_list_limit(tmp_path):
    repository = SQLiteExperimentRepository(tmp_path / "jobs.sqlite3")
    for index in range(105):
        repository.save(Experiment(str(index), "int8_16", "ihp130"))
    completed = Experiment("done", "int8_16", "ihp130", status=JobStatus.SUCCEEDED)
    repository.save(completed)
    repository.interrupt_unfinished()
    assert repository.get("0").status == JobStatus.INTERRUPTED
    assert repository.get("104").status == JobStatus.INTERRUPTED
    assert repository.get("done").status == JobStatus.SUCCEEDED
    assert len(repository.list()) == 100
