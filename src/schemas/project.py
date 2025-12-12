from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: UUID
    owner_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
