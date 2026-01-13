import pytest
from httpx import AsyncClient, ASGITransport
from src.main import create_app
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, UTC
from types import SimpleNamespace

@pytest.mark.asyncio
async def test_signup_user(monkeypatch):
    app = create_app()

    fake_repo = AsyncMock()
    fake_repo.get_user_by_username.return_value = None
    fake_repo.create_user.return_value = {
        "id": uuid4(),
        "username": "test",
        "email": "t@test.com",
        "created_at": datetime.now(UTC),
    }

    monkeypatch.setattr(
        "src.api.auth.UserRepository",
        lambda db: fake_repo
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/auth/signup",
            json={"username": "test", "email": "t@test.com"}
        )

    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "test"
    assert data["email"] == "t@test.com"

@pytest.mark.asyncio
async def test_login_user(monkeypatch):
    app = create_app()

    fake_repo = AsyncMock()
    fake_repo.get_user_by_username.return_value = SimpleNamespace(
        id="123",
        username="test",
        email="t@test.com",
    )
    monkeypatch.setattr(
        "src.api.auth.UserRepository",
        lambda db: fake_repo
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/auth/login",
            params={"username": "test"}  
        )

    assert res.status_code == 200
    assert "access_token" in res.json()

