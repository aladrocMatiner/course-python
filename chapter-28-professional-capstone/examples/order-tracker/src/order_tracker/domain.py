"""Immutable order values and stable domain failures."""

from __future__ import annotations

from dataclasses import dataclass, replace

STATUSES: tuple[str, ...] = ("pending", "packed", "shipped")
_NEXT_STATUS: dict[str, str] = {
    "pending": "packed",
    "packed": "shipped",
}


class OrderError(Exception):
    """Base class for stable learner-facing order failures."""

    code = "order-error"


class OrderValidationError(OrderError):
    """An order value is outside the bounded domain."""

    code = "validation-error"

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        super().__init__(f"{field} {reason}")


class DuplicateOrderError(OrderError):
    """An order identifier already exists."""

    code = "duplicate-order"

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"order {order_id} already exists")


class UnknownOrderError(OrderError):
    """An order identifier is not present."""

    code = "unknown-order"

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"order {order_id} does not exist")


class InvalidTransitionError(OrderError):
    """An order cannot move from its current status."""

    code = "invalid-transition"

    def __init__(self, order_id: str, status: str) -> None:
        self.order_id = order_id
        self.status = status
        super().__init__(f"order {order_id} cannot advance from {status}")


class RepositoryError(OrderError):
    """Persistence failed without exposing paths, SQL, or bound values."""

    code = "repository-error"


def _bounded_text(value: object, *, field: str, maximum: int) -> str:
    if type(value) is not str:
        raise OrderValidationError(field, "must be a string")
    normalized = value.strip()
    if not normalized:
        raise OrderValidationError(field, "must not be empty")
    if len(normalized) > maximum:
        raise OrderValidationError(field, f"must contain at most {maximum} characters")
    return normalized


@dataclass(frozen=True)
class Order:
    """A validated immutable snapshot of one synthetic order."""

    order_id: str
    item: str
    quantity: int
    status: str = "pending"

    def __post_init__(self) -> None:
        order_id = _bounded_text(self.order_id, field="order_id", maximum=32)
        item = _bounded_text(self.item, field="item", maximum=80)
        if type(self.quantity) is not int:
            raise OrderValidationError("quantity", "must be a built-in integer")
        if not 1 <= self.quantity <= 1_000:
            raise OrderValidationError("quantity", "must be between 1 and 1000")
        if self.status not in STATUSES:
            raise OrderValidationError("status", "must be pending, packed, or shipped")
        object.__setattr__(self, "order_id", order_id)
        object.__setattr__(self, "item", item)

    def advanced(self) -> Order:
        """Return the next immutable snapshot or reject a terminal order."""

        next_status = _NEXT_STATUS.get(self.status)
        if next_status is None:
            raise InvalidTransitionError(self.order_id, self.status)
        return replace(self, status=next_status)
