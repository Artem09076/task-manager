from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Dict


class EventRead(BaseModel):
    id: UUID
    task_id: UUID
    event_type: str
    payload: Optional[Dict]
    created_at: datetime

    class Config:
        from_attributes = True
