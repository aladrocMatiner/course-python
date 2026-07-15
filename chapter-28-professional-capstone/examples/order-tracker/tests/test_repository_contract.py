from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from order_tracker import (
    DuplicateOrderError,
    InMemoryOrderRepository,
    InvalidTransitionError,
    Order,
    RepositoryError,
    SQLiteOrderRepository,
    UnknownOrderError,
)


class RepositoryContractMixin:
    repository: InMemoryOrderRepository | SQLiteOrderRepository

    def test_create_get_list_and_advance_contract(self) -> None:
        self.repository.add(Order("ORD-002", "cable", 1))
        self.repository.add(Order("ORD-001", "widget", 2))
        self.assertEqual(self.repository.get("ORD-001").item, "widget")
        self.assertEqual(
            [order.order_id for order in self.repository.list_orders()],
            ["ORD-001", "ORD-002"],
        )
        self.assertEqual(self.repository.advance("ORD-001").status, "packed")
        self.assertEqual(self.repository.advance("ORD-001").status, "shipped")

    def test_duplicate_unknown_and_invalid_transition_preserve_state(self) -> None:
        original = self.repository.add(Order("ORD-001", "widget", 2))
        with self.assertRaises(DuplicateOrderError):
            self.repository.add(Order("ORD-001", "replacement", 3))
        self.assertEqual(self.repository.get("ORD-001"), original)

        with self.assertRaises(UnknownOrderError):
            self.repository.get("ORD-404")
        self.assertEqual(self.repository.list_orders(), [original])

        self.repository.advance("ORD-001")
        shipped = self.repository.advance("ORD-001")
        with self.assertRaises(InvalidTransitionError):
            self.repository.advance("ORD-001")
        self.assertEqual(self.repository.get("ORD-001"), shipped)


class InMemoryRepositoryContractTests(RepositoryContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.repository = InMemoryOrderRepository()

    def tearDown(self) -> None:
        self.repository.close()


class SQLiteRepositoryContractTests(RepositoryContractMixin, unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.database = Path(self.temporary.name) / "orders.sqlite3"
        self.repository = SQLiteOrderRepository(self.database, busy_timeout_ms=50)

    def tearDown(self) -> None:
        self.repository.close()
        self.temporary.cleanup()

    def test_schema_creation_is_idempotent(self) -> None:
        self.repository.close()
        self.repository = SQLiteOrderRepository(self.database, busy_timeout_ms=50)
        self.repository.add(Order("ORD-001", "widget", 1))
        self.assertEqual(self.repository.get("ORD-001").status, "pending")

    def test_triggered_update_failure_rolls_back_then_recovers(self) -> None:
        self.repository.add(Order("ORD-001", "widget", 1))
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                CREATE TRIGGER reject_advance
                BEFORE UPDATE OF status ON orders
                BEGIN
                    SELECT RAISE(ABORT, 'controlled failure');
                END
                """
            )

        with self.assertRaises(RepositoryError):
            self.repository.advance("ORD-001")
        self.assertEqual(self.repository.get("ORD-001").status, "pending")

        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TRIGGER reject_advance")
        self.assertEqual(self.repository.advance("ORD-001").status, "packed")

    def test_non_duplicate_insert_failure_maps_to_repository_error_and_recovers(self) -> None:
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                """
                CREATE TRIGGER reject_insert
                BEFORE INSERT ON orders
                BEGIN
                    SELECT RAISE(ABORT, 'controlled failure');
                END
                """
            )

        with self.assertRaises(RepositoryError) as raised:
            self.repository.add(Order("ORD-001", "widget", 1))
        self.assertEqual(str(raised.exception), "database add failed")
        self.assertEqual(self.repository.list_orders(), [])

        with sqlite3.connect(self.database) as connection:
            connection.execute("DROP TRIGGER reject_insert")
        self.assertEqual(self.repository.add(Order("ORD-001", "widget", 1)).status, "pending")

    def test_lock_timeout_preserves_state_and_release_allows_retry(self) -> None:
        lock = sqlite3.connect(self.database, isolation_level=None)
        try:
            lock.execute("BEGIN EXCLUSIVE")
            with self.assertRaises(RepositoryError) as raised:
                self.repository.add(Order("ORD-001", "widget", 1))
            self.assertEqual(str(raised.exception), "database add failed")
        finally:
            lock.rollback()
            lock.close()

        self.assertEqual(self.repository.list_orders(), [])
        self.repository.add(Order("ORD-001", "widget", 1))
        self.assertEqual(self.repository.get("ORD-001").status, "pending")

    def test_corrupt_database_fails_in_initialization_phase(self) -> None:
        other = Path(self.temporary.name) / "corrupt.sqlite3"
        other.write_bytes(b"not a sqlite database")
        with self.assertRaises(RepositoryError) as raised:
            SQLiteOrderRepository(other)
        self.assertEqual(str(raised.exception), "database initialization failed")


if __name__ == "__main__":
    unittest.main()
