from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.storage.db.db import get_db
from src.storage.db.repositories import EventRepository
from src.schemas.event import EventRead

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/{event_id}", response_model=EventRead)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = EventRepository(db)
    event = await repo.get_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.get("/task/{task_id}", response_model=List[EventRead])
async def get_task_events(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = EventRepository(db)
    events = await repo.get_by_task(task_id)
    return events


@router.get("/", response_model=List[EventRead])
async def get_all_events(
    db: AsyncSession = Depends(get_db),
):
    """
    Получить абсолютно все события в системе.
    """
    repo = EventRepository(db)
    events = await repo.get_all()
    return events

