"""Bounded process-local Publish/Subscribe with enqueue-only semantics."""

from __future__ import annotations

from collections import deque


MAX_SUBSCRIBERS = 4
MAX_QUEUED_PER_SUBSCRIBER = 8
MAX_CONFIGURED_SUBSCRIBERS = 64
MAX_CONFIGURED_QUEUED = 1_024
MAX_SUBSCRIBER_ID_CHARACTERS = 64
MAX_EVENT_CHARACTERS = 256


class InvalidInput(ValueError):
    """A local identifier or event exceeds the published input contract."""


def _bounded_positive_int(value: object, code: str, maximum: int) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 1 <= value <= maximum
    ):
        raise ValueError(code)
    return value


def _bounded_text(value: object, code: str, maximum: int) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise InvalidInput(code)
    return value


class ResourceLimit(Exception):
    """A new subscription would exceed the fixed subscriber bound."""


class UnknownSubscriber(Exception):
    """No active queue belongs to that opaque subscriber ID."""


class NoPendingEvent(Exception):
    """The subscriber has no event available to consume now."""


class DisconnectedSubscriber:
    def __init__(self, subscriber_id: str, discarded_count: int) -> None:
        self.subscriber_id = subscriber_id
        self.discarded_count = discarded_count


class PublishResult:
    def __init__(
        self,
        enqueued: tuple[str, ...],
        disconnected: tuple[DisconnectedSubscriber, ...],
    ) -> None:
        self.enqueued = enqueued
        self.disconnected = disconnected


class LocalPubSub:
    """Own at most four finite FIFO queues; own no consumer task."""

    def __init__(
        self,
        *,
        max_subscribers: int = MAX_SUBSCRIBERS,
        max_queued: int = MAX_QUEUED_PER_SUBSCRIBER,
    ) -> None:
        self.max_subscribers = _bounded_positive_int(
            max_subscribers,
            "max_subscribers_must_be_bounded_positive_int",
            MAX_CONFIGURED_SUBSCRIBERS,
        )
        self.max_queued = _bounded_positive_int(
            max_queued,
            "max_queued_must_be_bounded_positive_int",
            MAX_CONFIGURED_QUEUED,
        )
        self._queues: dict[str, deque[str]] = {}

    @property
    def subscriber_ids(self) -> tuple[str, ...]:
        return tuple(self._queues)

    def subscribe(self, subscriber_id: str) -> None:
        checked_id = _bounded_text(
            subscriber_id,
            "subscriber_id_must_be_bounded_non_empty_text",
            MAX_SUBSCRIBER_ID_CHARACTERS,
        )
        if checked_id in self._queues:
            return
        if len(self._queues) >= self.max_subscribers:
            raise ResourceLimit("resource_limit")
        self._queues[checked_id] = deque(maxlen=self.max_queued)

    def unsubscribe(self, subscriber_id: str) -> None:
        checked_id = _bounded_text(
            subscriber_id,
            "subscriber_id_must_be_bounded_non_empty_text",
            MAX_SUBSCRIBER_ID_CHARACTERS,
        )
        self._queues.pop(checked_id, None)

    def publish(self, event: str) -> PublishResult:
        checked_event = _bounded_text(
            event, "event_must_be_bounded_non_empty_text", MAX_EVENT_CHARACTERS
        )
        enqueued: list[str] = []
        disconnected: list[DisconnectedSubscriber] = []
        for subscriber_id in tuple(self._queues):
            queue = self._queues[subscriber_id]
            if len(queue) >= self.max_queued:
                disconnected.append(DisconnectedSubscriber(subscriber_id, len(queue)))
                del self._queues[subscriber_id]
                continue
            queue.append(checked_event)
            enqueued.append(subscriber_id)
        return PublishResult(tuple(enqueued), tuple(disconnected))

    def consume_one(self, subscriber_id: str) -> str:
        checked_id = _bounded_text(
            subscriber_id,
            "subscriber_id_must_be_bounded_non_empty_text",
            MAX_SUBSCRIBER_ID_CHARACTERS,
        )
        try:
            queue = self._queues[checked_id]
        except KeyError as error:
            raise UnknownSubscriber("unknown_subscriber") from error
        if not queue:
            raise NoPendingEvent("no_pending_event")
        return queue.popleft()

    def queued_count(self, subscriber_id: str) -> int:
        checked_id = _bounded_text(
            subscriber_id,
            "subscriber_id_must_be_bounded_non_empty_text",
            MAX_SUBSCRIBER_ID_CHARACTERS,
        )
        try:
            return len(self._queues[checked_id])
        except KeyError as error:
            raise UnknownSubscriber("unknown_subscriber") from error


def main() -> None:
    bus = LocalPubSub()
    bus.subscribe("fast")
    bus.subscribe("slow")

    first = bus.publish("event-0")
    observed = bus.consume_one("fast")
    print(
        f"happy enqueued={list(first.enqueued)} observed_by_fast={observed} "
        "delivery_claim=no"
    )

    for number in range(1, MAX_QUEUED_PER_SUBSCRIBER):
        bus.publish(f"event-{number}")
        bus.consume_one("fast")
    boundary = bus.publish("event-8")
    print(
        f"boundary enqueued={list(boundary.enqueued)} "
        f"disconnected={[(item.subscriber_id, item.discarded_count) for item in boundary.disconnected]}"
    )

    bus.subscribe("replacement")
    before_invalid = tuple(
        (subscriber_id, bus.queued_count(subscriber_id))
        for subscriber_id in bus.subscriber_ids
    )
    try:
        bus.publish("x" * (MAX_EVENT_CHARACTERS + 1))
    except InvalidInput as error:
        after_invalid = tuple(
            (subscriber_id, bus.queued_count(subscriber_id))
            for subscriber_id in bus.subscriber_ids
        )
        print(
            f"input_boundary code={error} unchanged={before_invalid == after_invalid}"
        )

    recovery = bus.publish("event-9")
    print(
        f"recovery subscribers={list(bus.subscriber_ids)} "
        f"enqueued={list(recovery.enqueued)}"
    )

    registration_bus = LocalPubSub()
    for number in range(MAX_SUBSCRIBERS):
        registration_bus.subscribe(f"subscriber-{number}")
    before = registration_bus.subscriber_ids
    try:
        registration_bus.subscribe("subscriber-4")
    except ResourceLimit as error:
        print(
            f"limit code={error} unchanged={before == registration_bus.subscriber_ids}"
        )

    try:
        LocalPubSub(max_subscribers=True)
    except ValueError as error:
        print(f"config_recovery code={error} active={len(bus.subscriber_ids)}")


if __name__ == "__main__":
    main()
