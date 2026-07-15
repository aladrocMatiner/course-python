from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from order_tracker.domain import (
    InvalidTransitionError,
    Order,
    OrderValidationError,
)


class OrderTests(unittest.TestCase):
    def test_normalizes_text_and_advances_immutably(self) -> None:
        pending = Order("  ORD-001  ", "  widget  ", 2)
        packed = pending.advanced()

        self.assertEqual(
            (pending.order_id, pending.item, pending.status),
            ("ORD-001", "widget", "pending"),
        )
        self.assertEqual(packed.status, "packed")
        self.assertEqual(pending.status, "pending")
        self.assertIsNot(pending, packed)
        with self.assertRaises(FrozenInstanceError):
            pending.status = "shipped"  # type: ignore[misc]

    def test_accepts_inclusive_boundaries(self) -> None:
        for quantity in (1, 1_000):
            with self.subTest(quantity=quantity):
                order = Order("I" * 32, "x" * 80, quantity)
                self.assertEqual(order.quantity, quantity)

    def test_rejects_first_values_outside_each_boundary(self) -> None:
        cases = (
            (("", "widget", 1), "order_id"),
            ((("I" * 33), "widget", 1), "order_id"),
            (("ORD-1", " ", 1), "item"),
            (("ORD-1", "x" * 81, 1), "item"),
            (("ORD-1", "widget", 0), "quantity"),
            (("ORD-1", "widget", 1_001), "quantity"),
        )
        for arguments, field in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaises(OrderValidationError) as raised:
                    Order(*arguments)
                self.assertEqual(raised.exception.field, field)

    def test_rejects_boolean_and_non_builtin_integer_quantities(self) -> None:
        class Quantity(int):
            pass

        for value in (True, False, Quantity(2), 2.0, "2"):
            with self.subTest(value=value):
                with self.assertRaises(OrderValidationError):
                    Order("ORD-1", "widget", value)

    def test_rejects_non_string_and_unknown_status(self) -> None:
        with self.assertRaises(OrderValidationError):
            Order(7, "widget", 1)
        with self.assertRaises(OrderValidationError):
            Order("ORD-1", object(), 1)
        with self.assertRaises(OrderValidationError):
            Order("ORD-1", "widget", 1, "cancelled")

    def test_terminal_status_rejects_advance_without_mutation(self) -> None:
        shipped = Order("ORD-1", "widget", 1, "shipped")
        with self.assertRaises(InvalidTransitionError) as raised:
            shipped.advanced()
        self.assertEqual(raised.exception.code, "invalid-transition")
        self.assertEqual(shipped.status, "shipped")


if __name__ == "__main__":
    unittest.main()
