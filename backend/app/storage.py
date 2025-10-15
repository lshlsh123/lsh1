"""Thread-safe in-memory data store for the demo backend."""

from __future__ import annotations

from threading import Lock
from typing import Dict, Iterable, List, Optional
from uuid import UUID

from . import schemas


class InMemoryStore:
    """A light-weight repository used to simulate persistence."""

    def __init__(self) -> None:
        self._models: Dict[UUID, schemas.ModelMetadata] = {}
        self._templates: Dict[UUID, schemas.Template] = {}
        self._jobs: Dict[UUID, schemas.TrainingJob] = {}
        self._lock = Lock()

    # ---------------------- Model management ----------------------
    def upsert_model(self, model: schemas.ModelMetadata) -> schemas.ModelMetadata:
        with self._lock:
            self._models[model.id] = model
            return model

    def list_models(self) -> List[schemas.ModelMetadata]:
        return sorted(self._models.values(), key=lambda m: m.created_at)

    def get_model(self, model_id: UUID) -> Optional[schemas.ModelMetadata]:
        return self._models.get(model_id)

    def delete_model(self, model_id: UUID) -> None:
        with self._lock:
            self._models.pop(model_id, None)

    # ---------------------- Template management ----------------------
    def upsert_template(self, template: schemas.Template) -> schemas.Template:
        with self._lock:
            self._templates[template.id] = template
            return template

    def list_templates(self) -> List[schemas.Template]:
        return sorted(self._templates.values(), key=lambda t: t.created_at)

    def get_template(self, template_id: UUID) -> Optional[schemas.Template]:
        return self._templates.get(template_id)

    def delete_template(self, template_id: UUID) -> None:
        with self._lock:
            self._templates.pop(template_id, None)

    # ---------------------- Training jobs ----------------------
    def upsert_job(self, job: schemas.TrainingJob) -> schemas.TrainingJob:
        with self._lock:
            self._jobs[job.id] = job
            return job

    def list_jobs(self) -> List[schemas.TrainingJob]:
        return sorted(self._jobs.values(), key=lambda j: j.submitted_at)

    def get_job(self, job_id: UUID) -> Optional[schemas.TrainingJob]:
        return self._jobs.get(job_id)

    def delete_job(self, job_id: UUID) -> None:
        with self._lock:
            self._jobs.pop(job_id, None)

    # ---------------------- Seeding helpers ----------------------
    def seed(self, models: Iterable[schemas.ModelMetadata], templates: Iterable[schemas.Template], jobs: Iterable[schemas.TrainingJob]) -> None:
        for model in models:
            self.upsert_model(model)
        for template in templates:
            self.upsert_template(template)
        for job in jobs:
            self.upsert_job(job)


store = InMemoryStore()
"""Singleton store used by the FastAPI application."""

