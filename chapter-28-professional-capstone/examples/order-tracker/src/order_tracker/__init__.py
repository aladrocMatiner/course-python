"""Public API for the course order tracker."""

from .domain import (
    DuplicateOrderError,
    InvalidTransitionError,
    Order,
    OrderError,
    OrderValidationError,
    RepositoryError,
    UnknownOrderError,
)
from .repositories import InMemoryOrderRepository, SQLiteOrderRepository
from .service import OrderService

__all__ = [
    "DuplicateOrderError",
    "InMemoryOrderRepository",
    "InvalidTransitionError",
    "Order",
    "OrderError",
    "OrderService",
    "OrderValidationError",
    "RepositoryError",
    "SQLiteOrderRepository",
    "UnknownOrderError",
]

__version__ = "1.0.0"

