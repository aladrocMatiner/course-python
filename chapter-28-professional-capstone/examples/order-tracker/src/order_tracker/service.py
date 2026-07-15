"""Application service shared by every adapter."""

from __future__ import annotations

from types import TracebackType

from .domain import Order
from .repositories import OrderRepository


class OrderService:
    """Coordinate the domain without knowing the storage technology."""

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            from .domain import RepositoryError

            raise RepositoryError("service is closed")

    def create(self, order_id: str, item: str, quantity: int) -> Order:
        self._ensure_open()
        order = Order(order_id=order_id, item=item, quantity=quantity)
        return self._repository.add(order)

    def get(self, order_id: str) -> Order:
        self._ensure_open()
        return self._repository.get(order_id)

    def list_orders(self) -> list[Order]:
        self._ensure_open()
        return self._repository.list_orders()

    def advance(self, order_id: str) -> Order:
        self._ensure_open()
        return self._repository.advance(order_id)

    def close(self) -> None:
        if not self._closed:
            self._repository.close()
            self._closed = True

    def __enter__(self) -> OrderService:
        self._ensure_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

