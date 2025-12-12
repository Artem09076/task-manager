from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.schemas.project import ProjectCreate, ProjectRead
from src.storage.db.db import get_db
from src.storage.db.repositories import Repository
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectRead)
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    repo = Repository(db)
    created = await repo.create_project(project.name, current_user.id)
    return created


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = Repository(db)
    project = await repo.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return project
