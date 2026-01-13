import pytest
from src.services.github import GitHubService
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock
import hmac, hashlib
from config.settings import settings

def test_verify_signature_ok():
    body = b"test"
    secret = settings.GIT_SECRET.encode()
    mac = hmac.new(secret, body, hashlib.sha256)
    signature = f"sha256={mac.hexdigest()}"

    service = GitHubService(MagicMock())
    assert service.verify_signature(signature, body) is None

def test_verify_signature_invalid():
    service = GitHubService(MagicMock())
    with pytest.raises(HTTPException):
        service.verify_signature("sha256=wrong", b"data")

@pytest.mark.asyncio
async def test_handle_issue_opened():
    repo = AsyncMock()
    service = GitHubService(repo)

    payload = {
        "action": "opened",
        "issue": {"id": 1, "title": "Bug", "body": "Desc"},
        "repository": {"full_name": "org/repo"},
    }

    response = await service.handle_issue_event(payload)

    repo.create_or_update_from_external.assert_awaited_once()
    assert response.status_code == 200
