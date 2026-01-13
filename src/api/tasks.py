from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.schemas.task import TaskCreate, TaskRead, TaskUpdate
from src.storage.db.db import get_db
from src.storage.db.repositories import TaskRepository
from src.storage.db.model.models import User
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])



@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(db)
    task = await repo.create(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        created_by=current_user.id,
    )
    return task


# ---------------------------
# LIST (public)
# ---------------------------
@router.get("", response_model=list[TaskRead])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
):
    repo = TaskRepository(db)
    return await repo.list()


# ---------------------------
# GET BY ID (public)
# ---------------------------
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = TaskRepository(db)
    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ---------------------------
# UPDATE (auth + owner only)
# ---------------------------
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(db)

    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this task",
        )

    task = await repo.update(
        task=task,
        title=data.title,
        description=data.description,
        status=data.status,
    )
    return task


# ---------------------------
# DELETE (auth + owner only)
# ---------------------------
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = TaskRepository(db)

    task = await repo.get_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this task",
        )

    await repo.delete(task)
