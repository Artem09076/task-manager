from src.storage.db.db import async_session
from src.storage.db.model.models import Integration, TaskStatus
from src.storage.db.repositories import TaskRepository
from worker.clients.google import GoogleCalendarClient
async def handle_calendar_sync(data):
    async with async_session() as session:
        integration_id = data.get("integration_id")
        integration = await session.get(Integration, integration_id)
        if not integration or not integration.enabled:
            return
        
        client =  GoogleCalendarClient()
        events= client.list_events(calendar_id=integration.external_id)
        task_service = TaskRepository(session)
        for event in events:
            status = TaskStatus.COMPLETED if event.get("status") == "cancelled" else TaskStatus.TODO
            print(event["id"])
            await task_service.create_or_update_from_google_cal(
                project_id=integration.project_id,
                source="google_calendar",
                external_id=event["id"],
                title=event["summary"],
                description=event.get("description"),
                status=status
            )

        await session.commit()
        
