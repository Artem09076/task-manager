from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

from src.storage.db.model.models import TaskStatus


class TaskCreate(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None


class TaskRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
