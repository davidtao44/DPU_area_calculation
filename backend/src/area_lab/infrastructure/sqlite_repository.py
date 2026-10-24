import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from area_lab.domain.models import Experiment, JobStatus, utc_now


class SQLiteExperimentRepository:
    """A connection per operation; threads never share a sqlite connection."""

    def __init__(self, database: Path) -> None:
        self.database = database
        database.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS experiments "
                "(id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)"
            )

    @contextmanager
    def _connection(self):
        connection = sqlite3.connect(self.database, timeout=10)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def save(self, experiment: Experiment) -> None:
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO experiments VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                (experiment.id, experiment.created_at, json.dumps(experiment.to_dict())),
            )

    def get(self, experiment_id: str) -> Experiment | None:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT payload FROM experiments WHERE id=?", (experiment_id,)
            ).fetchone()
        return Experiment.from_dict(json.loads(row[0])) if row else None

    def list(self, limit: int = 100) -> list[Experiment]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT payload FROM experiments ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [Experiment.from_dict(json.loads(row[0])) for row in rows]

    def interrupt_unfinished(self) -> None:
        with self._connection() as connection:
            rows = connection.execute("SELECT payload FROM experiments").fetchall()
            for row in rows:
                experiment = Experiment.from_dict(json.loads(row[0]))
                if experiment.status not in (JobStatus.QUEUED, JobStatus.RUNNING):
                    continue
                experiment.status = JobStatus.INTERRUPTED
                experiment.stage = "interrupted"
                experiment.updated_at = utc_now()
                experiment.error = (
                    "El servicio se reinició antes de terminar. Crea otra evaluación."
                )
                connection.execute(
                    "UPDATE experiments SET payload=? WHERE id=?",
                    (json.dumps(experiment.to_dict()), experiment.id),
                )
