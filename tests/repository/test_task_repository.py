import pytest
from src.storage.db.repositories import TaskRepository
from src.storage.db.model.models import TaskStatus
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_task_creates_event(async_session_mock):
    repo = TaskRepository(async_session_mock)

    task = await repo.create(
        project_id=uuid4(),
        title="Test",
        description="Desc",
    )

    async_session_mock.add.assert_called()
    async_session_mock.commit.assert_awaited()
    async_session_mock.refresh.assert_awaited()

@pytest.mark.asyncio
async def test_update_task_updates_fields(async_session_mock):
    repo = TaskRepository(async_session_mock)
    task = type("Task", (), {
        "id": uuid4(),
        "title": "Old",
        "description": None,
        "status": TaskStatus.TODO,
        "updated_at": None
    })()

    updated = await repo.update(
        task,
        title="New",
        status=TaskStatus.IN_PROGRESS,
    )

    assert updated.title == "New"
    assert updated.status == TaskStatus.IN_PROGRESS
