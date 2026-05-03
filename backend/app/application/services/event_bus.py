from collections import defaultdict
from typing import Callable, Type

from app.domain.events import DomainEvent


class EventBus:
    """Singleton event bus. Subscribers register by event type (Observer pattern)."""

    _instance: "EventBus | None" = None

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers: dict[Type[DomainEvent], list[Callable]] = defaultdict(list)
        return cls._instance

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable[[DomainEvent], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._subscribers[type(event)]:
            handler(event)

    def reset(self) -> None:
        """Solo para tests — limpia todos los suscriptores."""
        self._subscribers = defaultdict(list)
