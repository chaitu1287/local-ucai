"""Callback registry for environment events."""

from __future__ import annotations

from collections import defaultdict
from typing import Awaitable, Callable, Iterable

from enum import StrEnum

Callback = Callable[[object], Awaitable[None]]


class CallbackEvent(StrEnum):
    UPDATE = "update"


class CallbackRegistry:
    """Registry that maps event names to async callbacks."""

    def __init__(self) -> None:
        self._listeners: dict[CallbackEvent, list[Callback]] = defaultdict(list)

    def on(
        self, event: CallbackEvent | Iterable[CallbackEvent], callback: Callback
    ) -> None:
        """Register callback(s) for one or many event names."""

        names = [event] if isinstance(event, CallbackEvent) else list(event)
        for name in names:
            self._listeners[name].append(callback)

    def clear(self, event: CallbackEvent | Iterable[CallbackEvent]) -> None:
        """Remove all callbacks for one or many events."""

        names = [event] if isinstance(event, CallbackEvent) else list(event)
        for name in names:
            self._listeners.pop(name, None)

    async def emit(self, event: CallbackEvent, payload: object) -> None:
        """Invoke all callbacks for an event with the given payload."""

        for callback in self._listeners.get(event, []):
            await callback(payload)
