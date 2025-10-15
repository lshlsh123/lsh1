"""Pydantic schemas used by the demo backend."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class ModelMetadata(BaseModel):
    """Representation of a managed model."""

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=128)
    task_type: str = Field(..., description="Type of problem the model solves")
    description: Optional[str] = Field(
        None, description="Short summary shown in the catalog UI"
    )
    current_version: str = Field("v1", description="Semantic version of the active build")
    tags: List[str] = Field(default_factory=list)
    owner: str = Field(..., description="Primary contact for the asset")
    status: str = Field("draft", description="Lifecycle state of the model")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("tags", each_item=True)
    def _normalize_tags(cls, value: str) -> str:
        return value.lower()


class ModelCreate(BaseModel):
    name: str
    task_type: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    owner: str
    current_version: str = "v1"


class ModelUpdate(BaseModel):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    current_version: Optional[str] = None
    status: Optional[str] = None


class TemplateParameter(BaseModel):
    name: str
    type: str
    default: Optional[str] = None
    description: Optional[str] = None


class Template(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str] = None
    parameters: List[TemplateParameter] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: List[TemplateParameter] = Field(default_factory=list)


class TrainingJob(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    model_id: UUID
    dataset: str
    pipeline: str
    status: str = Field("pending", description="Execution status of the training job")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, float] = Field(default_factory=dict)


class TrainingJobCreate(BaseModel):
    model_id: UUID
    dataset: str
    pipeline: str


class TrainingJobUpdate(BaseModel):
    status: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None

