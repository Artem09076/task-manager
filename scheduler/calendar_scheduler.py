import asyncio
from scheduler.job import run_calender_scheduler
from celery import Celery
from config.settings import settings

app = Celery("task_scheduler", broker=settings.rabbit_url, backend=settings.redis_url)

app.conf.update(
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,
    broker_connection_retry_delay=5,
)

@app.task()
def schedule_calendar_sync():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_calender_scheduler())

app.conf.beat_schedule = {
    "schedule-calendar-sync-every-5-minutes": {
        "task": "scheduler.calendar_scheduler.schedule_calendar_sync",
        "schedule": 30.0, 
    },
}