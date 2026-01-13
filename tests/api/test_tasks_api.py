import pytest
from httpx import AsyncClient, ASGITransport
from src.main import create_app
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, UTC
from src.api.dependencies import get_current_user
from types import SimpleNamespace


@pytest.mark.asyncio
async def test_create_task(monkeypatch):
    app = create_app()

    project_id = uuid4()
    now = datetime.now(UTC)

    fake_repo = AsyncMock()
    fake_repo.create.return_value = {
        "id": uuid4(),
        "project_id": project_id,
        "title": "Test",
        "description": "Desc",
        "status": "TODO",         
        "created_at": now,
        "updated_at": now,
    }

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4()
    )

    monkeypatch.setattr(
        "src.api.tasks.TaskRepository",
        lambda db: fake_repo
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/tasks",
            json={
                "title": "Test",
                "description": "Desc",
                "project_id": str(project_id),
            }
        )

    assert res.status_code == 201
