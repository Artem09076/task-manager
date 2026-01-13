from src.api.dependencies import get_current_user
import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from jose import JWTError

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    monkeypatch.setattr(
        "src.api.dependencies.jwt.decode",
        lambda *args, **kwargs: (_ for _ in ()).throw(JWTError())
    )

    with pytest.raises(HTTPException):
        await get_current_user(token="bad", db=AsyncMock())
