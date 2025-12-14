import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging
import uvicorn
from fastapi import FastAPI
from src.storage.db.db import get_db
from src.api.router import router


from src.logger import setup_logging
from src.api.auth import router as auth_router
from src.api.users import router as users_router
from src.api.project import router as projects_router
from src.api.tasks import router as tasks_router
from src.api.events import router as events_router
from src.api.integrations import router as integrations_router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(docs_url="/swagger")
    app.include_router(router)

    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(projects_router)
    app.include_router(tasks_router) 
    app.include_router(events_router)
    app.include_router(integrations_router)

    return app


if __name__ == "__main__":
    uvicorn.run(
        "src.app:create_app", factory=True, host="0.0.0.0", port=8001, workers=1
    )