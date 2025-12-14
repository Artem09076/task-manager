from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.storage.db.db import get_db
from src.storage.db.repositories import IntegrationRepository
from src.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationRead
)
from src.api.dependencies import get_current_user
from src.storage.db.model.models import User

router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.post("/", response_model=IntegrationRead, status_code=status.HTTP_201_CREATED)
async def create_integration(
    data: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IntegrationRepository(db)
    return await repo.create(data)


@router.get("/", response_model=List[IntegrationRead])
async def get_all_integrations(
    db: AsyncSession = Depends(get_db),
):
    repo = IntegrationRepository(db)
    return await repo.get_all()


@router.get("/project/{project_id}", response_model=List[IntegrationRead])
async def get_project_integrations(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = IntegrationRepository(db)
    return await repo.get_by_project(project_id)


@router.put("/{integration_id}", response_model=IntegrationRead)
async def update_integration(
    integration_id: UUID,
    data: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IntegrationRepository(db)
    integration = await repo.get_by_id(integration_id)

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    return await repo.update(integration, data)


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    integration_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = IntegrationRepository(db)
    integration = await repo.get_by_id(integration_id)

    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    await repo.delete(integration)
