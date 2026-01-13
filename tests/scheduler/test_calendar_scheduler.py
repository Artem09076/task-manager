import pytest
from scheduler.job import run_calender_scheduler
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_calendar_scheduler_no_integrations(monkeypatch):
    fake_session = AsyncMock()
    fake_session.scalars.return_value = []

    monkeypatch.setattr(
        "scheduler.job.async_session",
        lambda: fake_session
    )

    monkeypatch.setattr(
        "scheduler.job.channel_pool",
        MagicMock()
    )

    await run_calender_scheduler()
