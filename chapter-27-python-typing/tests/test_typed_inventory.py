"""Runtime contract tests for the Chapter 27 companion."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
sys.path.insert(0, str(EXAMPLES))

from typed_inventory import Inventory, first_matching, parse_row  # noqa: E402


class ParseRowTests(unittest.TestCase):
    def test_normalizes_valid_row_and_preserves_zero(self) -> None:
        raw: dict[str, object] = {"sku": "  part-7 ", "quantity": 0}
        before = dict(raw)

        parsed = parse_row(raw)

        self.assertEqual({"sku": "PART-7", "quantity": 0}, parsed)
        self.assertEqual(before, raw)
        self.assertIsNot(parsed, raw)

    def test_accepts_inclusive_upper_bounds(self) -> None:
        raw: dict[str, object] = {"sku": "x" * 32, "quantity": 1_000_000}
        self.assertEqual(
            {"sku": "X" * 32, "quantity": 1_000_000},
            parse_row(raw),
        )

    def test_missing_fields_raise_type_error(self) -> None:
        cases: tuple[dict[str, object], ...] = (
            {"quantity": 1},
            {"sku": "PART-7"},
        )
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises(TypeError):
                    parse_row(raw)

    def test_wrong_runtime_types_raise_type_error(self) -> None:
        cases: tuple[dict[str, object], ...] = (
            {"sku": 7, "quantity": 1},
            {"sku": "PART-7", "quantity": 1.5},
            {"sku": "PART-7", "quantity": "1"},
            {"sku": "PART-7", "quantity": True},
            {"sku": "PART-7", "quantity": False},
        )
        for raw in cases:
            with self.subTest(raw=raw):
                before = dict(raw)
                with self.assertRaises(TypeError):
                    parse_row(raw)
                self.assertEqual(before, raw)

    def test_invalid_domain_values_raise_value_error_without_mutation(self) -> None:
        cases: tuple[dict[str, object], ...] = (
            {"sku": "", "quantity": 1},
            {"sku": "   ", "quantity": 1},
            {"sku": "x" * 33, "quantity": 1},
            {"sku": "PART-7", "quantity": -1},
            {"sku": "PART-7", "quantity": 1_000_001},
        )
        for raw in cases:
            with self.subTest(raw=raw):
                before = dict(raw)
                with self.assertRaises(ValueError):
                    parse_row(raw)
                self.assertEqual(before, raw)


class FirstMatchingTests(unittest.TestCase):
    def test_returns_first_match_without_evaluating_later_values(self) -> None:
        observed: list[int] = []

        def is_three(value: int) -> bool:
            observed.append(value)
            return value == 3

        result = first_matching((value for value in [1, 2, 3, 4]), is_three)

        self.assertEqual(3, result)
        self.assertEqual([1, 2, 3], observed)

    def test_returns_none_for_empty_or_unmatched_input(self) -> None:
        self.assertIsNone(first_matching([], lambda value: bool(value)))
        self.assertIsNone(first_matching([1, 2], lambda value: value > 5))

    def test_one_shot_iterator_keeps_its_observable_position(self) -> None:
        cursor = iter([1, 2, 3, 4])
        self.assertEqual(3, first_matching(cursor, lambda value: value == 3))
        self.assertEqual(4, next(cursor))
        with self.assertRaises(StopIteration):
            next(cursor)


class InventoryTests(unittest.TestCase):
    def test_add_returns_same_instance_and_owns_a_normalized_copy(self) -> None:
        row = {"sku": " part-7 ", "quantity": 2}
        inventory = Inventory()

        returned = inventory.add(row)
        row["sku"] = "CHANGED"

        self.assertIs(inventory, returned)
        self.assertEqual(({"sku": "PART-7", "quantity": 2},), inventory.rows)

        exposed = inventory.rows[0]
        exposed["quantity"] = 99
        self.assertEqual(2, inventory.rows[0]["quantity"])

    def test_rejected_add_preserves_all_prior_rows(self) -> None:
        inventory = Inventory().add({"sku": "PART-7", "quantity": 2})
        before = inventory.rows

        with self.assertRaises(TypeError):
            inventory.add({"sku": "BROKEN", "quantity": True})

        self.assertEqual(before, inventory.rows)

    def test_subclass_add_returns_same_subclass_instance(self) -> None:
        class LabelledInventory(Inventory):
            pass

        inventory = LabelledInventory()
        returned = inventory.add({"sku": "PART-7", "quantity": 2})

        self.assertIs(inventory, returned)
        self.assertIsInstance(returned, LabelledInventory)


if __name__ == "__main__":
    unittest.main()
