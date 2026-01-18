from src.storage.db.repositories import TaskRepository
from config.settings import settings
import hmac
import hashlib
from starlette.responses import Response
from fastapi import HTTPException
from src.storage.db.model.models import TaskStatus

class GitHubService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def handle_issue_event(self, payload: dict):
        action = payload.get("action")
        issue = payload.get("issue", {})
        if not issue:
            return Response(content="No issue data", status_code=400)
        git_repo = payload["repository"]["full_name"]
        if action == "opened":
            await self.task_repository.create_or_update_from_external(
                source="github",
                external_id=str(issue.get("id")),
                title=issue.get("title"),
                description=issue.get("body"),
                repo_full_name=git_repo
            )
        elif action == "closed":
            await self.task_repository.update_status_from_external(
                repo_full_name=git_repo,
                external_id=str(issue.get("id")),
                status=TaskStatus.COMPLETED
                )
        elif action == "reopened":
            await self.task_repository.update_status_from_external(
                repo_full_name=git_repo,
                external_id=str(issue.get("id")),
                status=TaskStatus.IN_PROGRESS
                )
        elif action == "deleted":
            await self.task_repository.delete_task_from_external(
                repo_full_name=git_repo,
                external_id=str(issue.get("id")),
                )

        return Response(content="Issue event processed", status_code=200)
    
    
    def verify_signature(self, signature: str, body: bytes) -> bool:
        if signature is None:
            raise HTTPException(status_code=401, detail="Missing signature")
        secret = settings.GIT_SECRET
        mac = hmac.new(secret.encode(), msg=body, digestmod=hashlib.sha256)
        expected_signature = f"sha256={mac.hexdigest()}"
        if not hmac.compare_digest(expected_signature, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")