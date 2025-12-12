from src.api.router import router  
from starlette.responses import Response
from starlette.requests import Request
from config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.db.db import get_db
from fastapi import Depends 
from src.storage.db.repositories import TaskRepository
from src.services.github import GitHubService


@router.post("/github")
async def github_webhook(request: Request, db: AsyncSession = Depends(get_db) ) -> Response:
    payload = await request.json()
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()
    service = GitHubService(TaskRepository(db))
    service.verify_signature(signature, body)
    event = request.headers.get("X-GitHub-Event")
    if event == "ping":
        return Response(content="Pong", status_code=200)
    
    if event == "issues":
        return await service.handle_issue_event(payload)
    return Response(content="Webhook received", status_code=200)

