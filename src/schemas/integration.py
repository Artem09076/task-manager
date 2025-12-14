from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class IntegrationBase(BaseModel):
    project_id: UUID
    type: str
    external_id: str
    config: dict
    enabled: bool = True


class IntegrationCreate(IntegrationBase):
    pass


class IntegrationUpdate(BaseModel):
    config: dict | None = None
    enabled: bool | None = None


class IntegrationRead(IntegrationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
