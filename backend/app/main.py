"""FastAPI application exposing the platform demo endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import schemas, storage

app = FastAPI(title="Foundation Model Platform Demo", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"]
,
    allow_headers=["*"],
)


@app.on_event("startup")
async def seed_data() -> None:
    """Populate the in-memory store with illustrative entries."""
    store = storage.store
    if store.list_models():
        return

    vision_model = schemas.ModelMetadata(
        name="Vision-Expert",
        task_type="image-classification",
        description="High-accuracy classifier for product imagery.",
        tags=["vision", "retail"],
        owner="computer-vision-team@demo.io",
        status="active",
        current_version="v1.2.0",
    )
    nlp_model = schemas.ModelMetadata(
        name="Chat-Assistant",
        task_type="nlp-dialog",
        description="Conversational agent tuned for customer support.",
        tags=["nlp", "customer-support"],
        owner="language-platform@demo.io",
        status="training",
        current_version="v0.9.1",
    )

    template = schemas.Template(
        name="Transformer Pretraining",
        description="General purpose transformer training recipe.",
        parameters=[
            schemas.TemplateParameter(
                name="sequence_length",
                type="integer",
                default="2048",
                description="Token sequence length",
            ),
            schemas.TemplateParameter(
                name="optimizer",
                type="string",
                default="adamw",
                description="Optimizer to use during training",
            ),
        ],
    )

    job = schemas.TrainingJob(
        model_id=vision_model.id,
        dataset="s3://datasets/retail/vision-latest",
        pipeline="airflow://pipelines/vision-train",
        status="running",
        metrics={"accuracy": 0.0},
    )

    store.seed(models=[vision_model, nlp_model], templates=[template], jobs=[job])


# --------------------------- Models ---------------------------
@app.get("/models", response_model=List[schemas.ModelMetadata])
async def list_models() -> List[schemas.ModelMetadata]:
    return storage.store.list_models()


@app.post("/models", response_model=schemas.ModelMetadata, status_code=201)
async def create_model(payload: schemas.ModelCreate) -> schemas.ModelMetadata:
    model = schemas.ModelMetadata(
        name=payload.name,
        task_type=payload.task_type,
        description=payload.description,
        tags=payload.tags,
        owner=payload.owner,
        current_version=payload.current_version,
        status="draft",
    )
    return storage.store.upsert_model(model)


@app.get("/models/{model_id}", response_model=schemas.ModelMetadata)
async def get_model(model_id: UUID) -> schemas.ModelMetadata:
    model = storage.store.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@app.patch("/models/{model_id}", response_model=schemas.ModelMetadata)
async def update_model(model_id: UUID, payload: schemas.ModelUpdate) -> schemas.ModelMetadata:
    model = storage.store.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    updated_fields = payload.dict(exclude_none=True)
    for key, value in updated_fields.items():
        setattr(model, key, value)
    model.updated_at = datetime.utcnow()

    return storage.store.upsert_model(model)


@app.delete("/models/{model_id}", status_code=204)
async def delete_model(model_id: UUID) -> None:
    storage.store.delete_model(model_id)


# --------------------------- Templates ---------------------------
@app.get("/templates", response_model=List[schemas.Template])
async def list_templates() -> List[schemas.Template]:
    return storage.store.list_templates()


@app.post("/templates", response_model=schemas.Template, status_code=201)
async def create_template(payload: schemas.TemplateCreate) -> schemas.Template:
    template = schemas.Template(**payload.dict())
    return storage.store.upsert_template(template)


@app.delete("/templates/{template_id}", status_code=204)
async def delete_template(template_id: UUID) -> None:
    storage.store.delete_template(template_id)


# --------------------------- Training jobs ---------------------------
@app.get("/jobs", response_model=List[schemas.TrainingJob])
async def list_jobs() -> List[schemas.TrainingJob]:
    return storage.store.list_jobs()


@app.post("/jobs", response_model=schemas.TrainingJob, status_code=201)
async def create_job(payload: schemas.TrainingJobCreate) -> schemas.TrainingJob:
    if not storage.store.get_model(payload.model_id):
        raise HTTPException(status_code=400, detail="Model does not exist")

    job = schemas.TrainingJob(
        model_id=payload.model_id,
        dataset=payload.dataset,
        pipeline=payload.pipeline,
        status="pending",
    )
    return storage.store.upsert_job(job)


@app.patch("/jobs/{job_id}", response_model=schemas.TrainingJob)
async def update_job(job_id: UUID, payload: schemas.TrainingJobUpdate) -> schemas.TrainingJob:
    job = storage.store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    updated_fields = payload.dict(exclude_none=True)
    for key, value in updated_fields.items():
        setattr(job, key, value)
    return storage.store.upsert_job(job)


@app.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: UUID) -> None:
    storage.store.delete_job(job_id)

