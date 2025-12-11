import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging
import uvicorn
from fastapi import FastAPI
from src.storage.db.db import get_db
from src.api.router import router




def create_app() -> FastAPI:
    app = FastAPI(docs_url="/swagger")
    app.include_router(router)
    return app


if __name__ == "__main__":
    uvicorn.run(
        "src.app:create_app", factory=True, host="0.0.0.0", port=8001, workers=1
    )