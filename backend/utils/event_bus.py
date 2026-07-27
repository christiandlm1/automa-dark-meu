"""
AUTOMA Utils - Event Bus.

Internal Publish-Subscribe Event Bus for decoupling modules and services.
Provides async and sync event broadcasting to registered subscribers.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Union

logger = logging.getLogger("automa.event_bus")

# Event names defined by system specifications
EVENT_JOB_CREATED = "JobCreated"
EVENT_JOB_STARTED = "JobStarted"
EVENT_JOB_PAUSED = "JobPaused"
EVENT_JOB_FINISHED = "JobFinished"
EVENT_JOB_FAILED = "JobFailed"
EVENT_TEMPLATE_CREATED = "TemplateCreated"
EVENT_TEMPLATE_UPDATED = "TemplateUpdated"
EVENT_EXPORT_COMPLETED = "ExportCompleted"


# Listener type: Can be a normal sync function or an async coroutine function
ListenerCallback = Callable[..., Union[None, Coroutine[Any, Any, None]]]


class EventBus:
    """Singleton Event Bus facilitating decoupled message passing."""

    _instance: "EventBus | None" = None

    def __new__(cls, *args, **kwargs) -> "EventBus":
        if not cls._instance:
            cls._instance = super(EventBus, cls).__new__(cls, *args, **kwargs)
            cls._instance._listeners = {}
        return cls._instance

    def __init__(self) -> None:
        # Avoid re-initialization if initialized
        if hasattr(self, "_initialized"):
            return
        self._listeners: dict[str, set[ListenerCallback]] = {}
        self._initialized = True

    def subscribe(self, event_name: str, callback: ListenerCallback) -> None:
        """Register a subscriber callback for a specific event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = set()
        self._listeners[event_name].add(callback)
        logger.debug(f"Subscribed callback to event: {event_name}")

    def unsubscribe(self, event_name: str, callback: ListenerCallback) -> None:
        """Remove a subscriber callback from an event."""
        if event_name in self._listeners:
            self._listeners[event_name].discard(callback)
            logger.debug(f"Unsubscribed callback from event: {event_name}")

    async def publish(self, event_name: str, *args, **kwargs) -> None:
        """Publish an event to all subscribers asynchronously."""
        if event_name not in self._listeners or not self._listeners[event_name]:
            return

        callbacks = list(self._listeners[event_name])
        logger.info(f"Publishing event '{event_name}' to {len(callbacks)} listener(s).")
        
        # We fire callbacks concurrently without blocking the engine
        tasks = []
        for cb in callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    tasks.append(self._safe_await(cb, event_name, *args, **kwargs))
                else:
                    # Run sync callback inside loop thread pool executor
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(None, self._safe_call, cb, event_name, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error scheduling listener for {event_name}: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_await(self, cb: ListenerCallback, event_name: str, *args, **kwargs) -> None:
        try:
            await cb(*args, **kwargs)  # type: ignore
        except Exception as e:
            logger.error(f"Error in async listener for '{event_name}': {e}", exc_info=True)

    def _safe_call(self, cb: ListenerCallback, event_name: str, *args, **kwargs) -> None:
        try:
            cb(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in sync listener for '{event_name}': {e}", exc_info=True)


# Global singleton instance
event_bus = EventBus()
