import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """
    Implementasi event bus sederhana untuk komunikasi antar service.
    Mendukung pattern publish-subscribe asynchronous.
    """

    def __init__(self):
        """Inisialisasi event bus."""
        self.subscribers: Dict[str, List[Callable]] = {}
        logger.debug("Event bus initialized")

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe ke suatu event.

        Args:
            event_type: Nama event yang ingin di-subscribe
            callback: Fungsi yang akan dipanggil saat event terjadi
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe dari suatu event.

        Args:
            event_type: Nama event
            callback: Fungsi callback yang terdaftar
        """
        if event_type in self.subscribers and callback in self.subscribers[event_type]:
            self.subscribers[event_type].remove(callback)
            logger.debug(f"Unsubscribed from event: {event_type}")

    async def publish(self, event_type: str, **kwargs: Any) -> None:
        """
        Publish suatu event ke semua subscriber.

        Args:
            event_type: Nama event
            **kwargs: Data yang disertakan dalam event
        """
        if event_type not in self.subscribers:
            logger.debug(f"No subscribers for event: {event_type}")
            return

        logger.debug(f"Publishing event: {event_type} with data: {kwargs}")
        tasks = []

        for callback in self.subscribers[event_type]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Async callback
                    tasks.append(asyncio.create_task(callback(**kwargs)))
                else:
                    # Sync callback
                    callback(**kwargs)
            except Exception as e:
                logger.error(f"Error in event callback for {event_type}: {e}")

        # Await all async tasks
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Singleton instance
event_bus = EventBus()
