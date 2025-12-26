import msgpack
import logging
from src.storage.rabbit import channel_pool
from worker.handler.handle_calendar_sync import handle_calendar_sync


async def main() -> None:
    queue_name = "calendar.sync"
    async with channel_pool.acquire() as channel:
        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(
            queue_name,
            durable=True
        )
        logging.info("AAAAAAAAAAAAAA")
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = msgpack.unpackb(message.body)
                    await handle_calendar_sync(data)