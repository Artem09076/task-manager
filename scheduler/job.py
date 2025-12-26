from src.storage.db.db import async_session
from src.storage.db.model.models import Integration
from sqlalchemy.future import select
from src.storage.rabbit import channel_pool
import aio_pika
from datetime import datetime
import msgpack

async def run_calender_scheduler():
    async with async_session() as session:
        res = await session.scalars(
            select(Integration).where(
                Integration.type == "google_calendar",
                Integration.enabled == True
                )
        )
        integrations = list(res)
        print(f"Found {len(integrations)} google calendar integrations")
        async with channel_pool.acquire() as channel:
            for integration in integrations:
                exchange = await channel.declare_exchange(
                    "calendar_tasks",
                    aio_pika.ExchangeType.TOPIC,
                    durable=True)
                queue_name = f"calendar.sync"
                queue = await channel.declare_queue(
                    queue_name,
                    durable=True)
                await queue.bind(exchange, routing_key="calendar.sync")
                
                message={
                    "source": "google_calendar",
                    "event_type": "calendar.sync",
                    "integration_id": str(integration.id),
                    "requested_at": datetime.utcnow().isoformat()
                }
                print(
                    f"Publishing calendar.sync for integration {integration.id}, "
                    f"calendar_id={integration.external_id}"
                )
                await exchange.publish(aio_pika.Message(body=msgpack.packb(message)), routing_key="calendar.sync")
                print("Published message to RabbitMQ")
                

