"""Optional bounded, enqueue-only Pub/Sub example.

``publish`` reports queue admission, never delivery or processing.  There are no
background consumers, network transports, replay logs, or retained history.
"""

from __future__ import annotations

from collections import deque
from typing import NamedTuple


MAX_SUBSCRIBERS = 4
MAX_QUEUED_PER_SUBSCRIBER = 8


class PubSubError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class ResourceLimit(PubSubError):
    def __init__(self) -> None:
        super().__init__("resource_limit", "the subscriber limit was reached")


class UnknownSubscriber(PubSubError):
    def __init__(self) -> None:
        super().__init__("unknown_subscriber", "the subscriber is not registered")


class NoPendingEvent(PubSubError):
    def __init__(self) -> None:
        super().__init__("no_pending_event", "the subscriber queue is empty")


class DisconnectedSubscriber(NamedTuple):
    subscriber_id: str
    code: str
    discarded_count: int


class PublishResult(NamedTuple):
    enqueued: tuple[str, ...]
    disconnected: tuple[DisconnectedSubscriber, ...]


class PubSub:
    """Process-local fan-out with exact subscriber and queue bounds."""

    def __init__(
        self,
        *,
        max_subscribers: int = MAX_SUBSCRIBERS,
        max_pending: int = MAX_QUEUED_PER_SUBSCRIBER,
    ) -> None:
        if max_subscribers < 1 or max_pending < 1:
            raise ValueError("Pub/Sub limits must be positive")
        if max_subscribers > MAX_SUBSCRIBERS:
            raise ValueError(f"max_subscribers cannot exceed {MAX_SUBSCRIBERS}")
        if max_pending > MAX_QUEUED_PER_SUBSCRIBER:
            raise ValueError(
                f"max_pending cannot exceed {MAX_QUEUED_PER_SUBSCRIBER}"
            )
        self.max_subscribers = max_subscribers
        self.max_pending = max_pending
        self._next_id = 1
        self._queues: dict[str, deque[object]] = {}

    @property
    def subscriber_count(self) -> int:
        return len(self._queues)

    def subscribe(self) -> str:
        if len(self._queues) >= self.max_subscribers:
            raise ResourceLimit()
        subscriber_id = f"subscriber-{self._next_id}"
        self._next_id += 1
        self._queues[subscriber_id] = deque()
        return subscriber_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove a subscriber; repeated removal is a harmless no-op."""

        return self._queues.pop(subscriber_id, None) is not None

    def publish(self, event: object) -> PublishResult:
        enqueued: list[str] = []
        disconnected: list[DisconnectedSubscriber] = []
        for subscriber_id, queue in tuple(self._queues.items()):
            if len(queue) >= self.max_pending:
                discarded_count = len(queue)
                del self._queues[subscriber_id]
                disconnected.append(
                    DisconnectedSubscriber(
                        subscriber_id,
                        "slow_subscriber",
                        discarded_count,
                    )
                )
                continue
            queue.append(event)
            enqueued.append(subscriber_id)
        return PublishResult(tuple(enqueued), tuple(disconnected))

    def pending_count(self, subscriber_id: str) -> int:
        return len(self._queue_for(subscriber_id))

    def receive(self, subscriber_id: str) -> object:
        queue = self._queue_for(subscriber_id)
        if not queue:
            raise NoPendingEvent()
        return queue.popleft()

    def _queue_for(self, subscriber_id: str) -> deque[object]:
        try:
            return self._queues[subscriber_id]
        except KeyError as exc:
            raise UnknownSubscriber() from exc
