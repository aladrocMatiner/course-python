from __future__ import annotations

import unittest

from order_tracker import (
    DuplicateOrderError,
    InMemoryOrderRepository,
    InvalidTransitionError,
    OrderService,
    RepositoryError,
    UnknownOrderError,
)


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = OrderService(InMemoryOrderRepository())

    def tearDown(self) -> None:
        self.service.close()

    def test_happy_lifecycle_and_deterministic_listing(self) -> None:
        second = self.service.create("ORD-002", "cable", 1)
        first = self.service.create("ORD-001", "widget", 2)

        self.assertEqual(first.status, "pending")
        self.assertEqual(self.service.advance(first.order_id).status, "packed")
        self.assertEqual(self.service.advance(first.order_id).status, "shipped")
        self.assertEqual(
            [order.order_id for order in self.service.list_orders()],
            ["ORD-001", "ORD-002"],
        )
        self.assertEqual(second.status, "pending")

    def test_duplicate_rejection_preserves_original_and_unique_retry_succeeds(self) -> None:
        original = self.service.create("ORD-001", "widget", 2)
        with self.assertRaises(DuplicateOrderError):
            self.service.create("ORD-001", "replacement", 9)

        self.assertEqual(self.service.get("ORD-001"), original)
        recovered = self.service.create("ORD-002", "replacement", 9)
        self.assertEqual(recovered.order_id, "ORD-002")

    def test_invalid_transition_preserves_shipped_state(self) -> None:
        self.service.create("ORD-001", "widget", 2)
        self.service.advance("ORD-001")
        shipped = self.service.advance("ORD-001")

        with self.assertRaises(InvalidTransitionError):
            self.service.advance("ORD-001")
        self.assertEqual(self.service.get("ORD-001"), shipped)

    def test_unknown_order_is_stable(self) -> None:
        with self.assertRaises(UnknownOrderError) as raised:
            self.service.get("ORD-404")
        self.assertEqual(raised.exception.code, "unknown-order")

    def test_close_is_idempotent_and_rejects_later_work(self) -> None:
        self.service.close()
        self.service.close()
        with self.assertRaises(RepositoryError):
            self.service.list_orders()


if __name__ == "__main__":
    unittest.main()
