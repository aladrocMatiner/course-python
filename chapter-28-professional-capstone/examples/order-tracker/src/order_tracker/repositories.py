"""In-memory and SQLite repositories behind one bounded contract."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .domain import (
    DuplicateOrderError,
    Order,
    RepositoryError,
    UnknownOrderError,
)

DEFAULT_BUSY_TIMEOUT_MS = 250


class OrderRepository:
    """Inheritance contract for storage used by ``OrderService``."""

    def add(self, order: Order) -> Order:
        raise NotImplementedError

    def get(self, order_id: str) -> Order:
        raise NotImplementedError

    def list_orders(self) -> list[Order]:
        raise NotImplementedError

    def advance(self, order_id: str) -> Order:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class InMemoryOrderRepository(OrderRepository):
    """Deterministic storage for the foundation stage."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RepositoryError("repository is closed")

    def add(self, order: Order) -> Order:
        self._ensure_open()
        if order.order_id in self._orders:
            raise DuplicateOrderError(order.order_id)
        self._orders[order.order_id] = order
        return order

    def get(self, order_id: str) -> Order:
        self._ensure_open()
        try:
            return self._orders[order_id]
        except KeyError:
            raise UnknownOrderError(order_id) from None

    def list_orders(self) -> list[Order]:
        self._ensure_open()
        return [self._orders[key] for key in sorted(self._orders)]

    def advance(self, order_id: str) -> Order:
        self._ensure_open()
        current = self.get(order_id)
        updated = current.advanced()
        self._orders[order_id] = updated
        return updated

    def close(self) -> None:
        self._closed = True


class SQLiteOrderRepository(OrderRepository):
    """SQLite persistence with short connections and explicit transactions."""

    def __init__(
        self,
        database: str | Path,
        *,
        busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
    ) -> None:
        if type(busy_timeout_ms) is not int or not 1 <= busy_timeout_ms <= 5_000:
            raise ValueError("busy_timeout_ms must be an integer from 1 through 5000")
        self._database = Path(database)
        self._busy_timeout_ms = busy_timeout_ms
        self._closed = False
        self._initialize()

    def _ensure_open(self) -> None:
        if self._closed:
            raise RepositoryError("repository is closed")

    def _connect(self) -> sqlite3.Connection:
        self._ensure_open()
        connection = sqlite3.connect(
            self._database,
            timeout=self._busy_timeout_ms / 1_000,
            isolation_level=None,
        )
        connection.execute(f"PRAGMA busy_timeout = {self._busy_timeout_ms}")
        return connection

    @staticmethod
    def _row_to_order(row: tuple[object, ...]) -> Order:
        return Order(
            order_id=row[0],
            item=row[1],
            quantity=row[2],
            status=row[3],
        )

    @staticmethod
    def _rollback(connection: sqlite3.Connection) -> None:
        try:
            connection.rollback()
        except sqlite3.DatabaseError:
            pass

    def _initialize(self) -> None:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id TEXT PRIMARY KEY,
                    item TEXT NOT NULL,
                    quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 1000),
                    status TEXT NOT NULL CHECK(status IN ('pending', 'packed', 'shipped'))
                )
                """
            )
            connection.commit()
        except sqlite3.DatabaseError as exc:
            if connection is not None:
                self._rollback(connection)
            raise RepositoryError("database initialization failed") from exc
        finally:
            if connection is not None:
                connection.close()

    def add(self, order: Order) -> Order:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT 1 FROM orders WHERE order_id = ?", (order.order_id,)
            ).fetchone()
            if existing is not None:
                raise DuplicateOrderError(order.order_id)
            connection.execute(
                "INSERT INTO orders(order_id, item, quantity, status) VALUES (?, ?, ?, ?)",
                (order.order_id, order.item, order.quantity, order.status),
            )
            connection.commit()
            return order
        except DuplicateOrderError:
            if connection is not None:
                self._rollback(connection)
            raise
        except sqlite3.DatabaseError as exc:
            if connection is not None:
                self._rollback(connection)
            raise RepositoryError("database add failed") from exc
        finally:
            if connection is not None:
                connection.close()

    def get(self, order_id: str) -> Order:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            row = connection.execute(
                "SELECT order_id, item, quantity, status FROM orders WHERE order_id = ?",
                (order_id,),
            ).fetchone()
        except sqlite3.DatabaseError as exc:
            raise RepositoryError("database read failed") from exc
        finally:
            if connection is not None:
                connection.close()
        if row is None:
            raise UnknownOrderError(order_id)
        return self._row_to_order(row)

    def list_orders(self) -> list[Order]:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            rows = connection.execute(
                "SELECT order_id, item, quantity, status FROM orders ORDER BY order_id"
            ).fetchall()
            return [self._row_to_order(row) for row in rows]
        except sqlite3.DatabaseError as exc:
            raise RepositoryError("database list failed") from exc
        finally:
            if connection is not None:
                connection.close()

    def advance(self, order_id: str) -> Order:
        connection: sqlite3.Connection | None = None
        try:
            connection = self._connect()
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT order_id, item, quantity, status FROM orders WHERE order_id = ?",
                (order_id,),
            ).fetchone()
            if row is None:
                raise UnknownOrderError(order_id)
            current = self._row_to_order(row)
            updated = current.advanced()
            cursor = connection.execute(
                "UPDATE orders SET status = ? WHERE order_id = ? AND status = ?",
                (updated.status, order_id, current.status),
            )
            if cursor.rowcount != 1:
                raise RepositoryError("database transition conflict")
            connection.commit()
            return updated
        except (UnknownOrderError, RepositoryError):
            if connection is not None:
                self._rollback(connection)
            raise
        except sqlite3.DatabaseError as exc:
            if connection is not None:
                self._rollback(connection)
            raise RepositoryError("database advance failed") from exc
        except Exception:
            if connection is not None:
                self._rollback(connection)
            raise
        finally:
            if connection is not None:
                connection.close()

    def close(self) -> None:
        self._closed = True
