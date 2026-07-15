"""Optional bounded newline-JSON adapter for loopback learning labs.

This is deliberately not a production server.  It accepts one request per
connection, never binds a public interface, and owns every handler task.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from typing import Final

from .domain import Order, OrderError
from .service import OrderService

LOOPBACK_HOST: Final = "127.0.0.1"
DEFAULT_MAX_REQUEST_BYTES: Final = 1_024
DEFAULT_MAX_RESPONSE_BYTES: Final = 4_096
DEFAULT_MAX_REQUESTS: Final = 8
DEFAULT_MAX_CONCURRENCY: Final = 4
DEFAULT_MAX_LIST_ORDERS: Final = 20
DEFAULT_IDLE_TIMEOUT_SECONDS: Final = 0.5
_RESPONSE_LIMIT_FRAME: Final = b'{"error":"response-limit","ok":false}\n'
MIN_RESPONSE_BYTES: Final = len(_RESPONSE_LIMIT_FRAME)


def _positive_int(value: object, *, name: str, maximum: int, minimum: int = 1) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} through {maximum}")
    return value


def _timeout(value: object) -> float:
    if type(value) not in (int, float) or isinstance(value, bool):
        raise ValueError("idle_timeout must be numeric")
    result = float(value)
    if not 0.05 <= result <= 10.0:
        raise ValueError("idle_timeout must be from 0.05 through 10 seconds")
    return result


def _order_data(order: Order) -> dict[str, object]:
    return {
        "item": order.item,
        "order_id": order.order_id,
        "quantity": order.quantity,
        "status": order.status,
    }


class LoopbackOrderServer:
    """Own a bounded ephemeral loopback listener and its handler tasks."""

    def __init__(
        self,
        service: OrderService,
        *,
        max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
        max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        max_list_orders: int = DEFAULT_MAX_LIST_ORDERS,
        idle_timeout: float = DEFAULT_IDLE_TIMEOUT_SECONDS,
    ) -> None:
        self._service = service
        self.max_request_bytes = _positive_int(
            max_request_bytes, name="max_request_bytes", maximum=65_536
        )
        self.max_response_bytes = _positive_int(
            max_response_bytes,
            name="max_response_bytes",
            minimum=MIN_RESPONSE_BYTES,
            maximum=65_536,
        )
        self.max_requests = _positive_int(max_requests, name="max_requests", maximum=100)
        self.max_concurrency = _positive_int(
            max_concurrency, name="max_concurrency", maximum=32
        )
        self.max_list_orders = _positive_int(
            max_list_orders, name="max_list_orders", maximum=100
        )
        self.idle_timeout = _timeout(idle_timeout)
        self._server: asyncio.AbstractServer | None = None
        self._tasks: set[asyncio.Task[object]] = set()
        self._active = 0
        self._request_count = 0
        self.connection_started = asyncio.Event()
        self.capacity_available = asyncio.Event()
        self.capacity_available.set()

    @property
    def address(self) -> tuple[str, int]:
        if self._server is None or not self._server.sockets:
            raise RuntimeError("loopback server has not started")
        host, port = self._server.sockets[0].getsockname()[:2]
        return str(host), int(port)

    @property
    def active_connections(self) -> int:
        return self._active

    @property
    def owned_task_count(self) -> int:
        return sum(not task.done() for task in self._tasks)

    async def start(self) -> tuple[str, int]:
        if self._server is not None:
            raise RuntimeError("loopback server already started")
        self._server = await asyncio.start_server(
            self._handle,
            LOOPBACK_HOST,
            0,
            limit=self.max_request_bytes + 1,
        )
        return self.address

    async def close(self) -> None:
        server = self._server
        self._server = None
        if server is not None:
            server.close()
        current = asyncio.current_task()
        pending = [task for task in tuple(self._tasks) if task is not current and not task.done()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        if server is not None:
            await server.wait_closed()
        self._tasks = {task for task in self._tasks if not task.done()}

    async def __aenter__(self) -> LoopbackOrderServer:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, traceback) -> None:
        await self.close()

    async def _write(self, writer: asyncio.StreamWriter, payload: Mapping[str, object]) -> None:
        encoded = (
            json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
            + b"\n"
        )
        if len(encoded) > self.max_response_bytes:
            encoded = _RESPONSE_LIMIT_FRAME
        writer.write(encoded)
        await asyncio.wait_for(writer.drain(), timeout=self.idle_timeout)

    @staticmethod
    def _exact_fields(request: Mapping[str, object], expected: set[str]) -> bool:
        return set(request) == expected

    def _dispatch(self, request: object) -> dict[str, object]:
        if not isinstance(request, dict):
            return {"error": "invalid-request", "ok": False}
        action = request.get("action")
        try:
            if action == "add" and self._exact_fields(
                request, {"action", "order_id", "item", "quantity"}
            ):
                order = self._service.create(
                    request["order_id"], request["item"], request["quantity"]
                )
                return {"ok": True, "order": _order_data(order)}
            if action == "advance" and self._exact_fields(request, {"action", "order_id"}):
                order = self._service.advance(request["order_id"])
                return {"ok": True, "order": _order_data(order)}
            if action == "list" and self._exact_fields(request, {"action"}):
                orders = self._service.list_orders()
                if len(orders) > self.max_list_orders:
                    return {"error": "response-limit", "ok": False}
                return {"ok": True, "orders": [_order_data(order) for order in orders]}
            return {"error": "invalid-request", "ok": False}
        except OrderError as exc:
            return {"error": exc.code, "ok": False}

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        task = asyncio.current_task()
        if task is not None:
            self._tasks.add(task)
        if self._active >= self.max_concurrency:
            try:
                try:
                    await self._write(writer, {"error": "busy", "ok": False})
                except (ConnectionError, asyncio.TimeoutError):
                    pass
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except ConnectionError:
                    pass
                if task is not None:
                    self._tasks.discard(task)
            return

        self._active += 1
        self.connection_started.set()
        if self._active >= self.max_concurrency:
            self.capacity_available.clear()
        try:
            if self._request_count >= self.max_requests:
                await self._write(writer, {"error": "request-limit", "ok": False})
                return
            self._request_count += 1
            try:
                data = await asyncio.wait_for(reader.readline(), timeout=self.idle_timeout)
            except asyncio.TimeoutError:
                await self._write(writer, {"error": "timeout", "ok": False})
                return
            except ValueError:
                await self._write(writer, {"error": "request-too-large", "ok": False})
                return
            if not data or not data.endswith(b"\n"):
                await self._write(writer, {"error": "incomplete-request", "ok": False})
                return
            if len(data) > self.max_request_bytes:
                await self._write(writer, {"error": "request-too-large", "ok": False})
                return
            try:
                request = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                await self._write(writer, {"error": "malformed-request", "ok": False})
                return
            await self._write(writer, self._dispatch(request))
        except asyncio.CancelledError:
            raise
        except (ConnectionError, asyncio.TimeoutError):
            return
        finally:
            self._active -= 1
            if self._active < self.max_concurrency:
                self.capacity_available.set()
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass
            if task is not None:
                self._tasks.discard(task)


async def send_request(
    address: tuple[str, int],
    request: Mapping[str, object],
    *,
    timeout: float = 1.0,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
) -> dict[str, object]:
    """Send one bounded request to a loopback server and close the client."""

    host, port = address
    if host != LOOPBACK_HOST:
        raise ValueError("client address must use the declared loopback host")
    client_timeout = _timeout(timeout)
    response_limit = _positive_int(
        max_response_bytes,
        name="max_response_bytes",
        minimum=MIN_RESPONSE_BYTES,
        maximum=65_536,
    )
    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(host, port), timeout=client_timeout
    )
    try:
        payload = (
            json.dumps(request, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )
            + b"\n"
        )
        writer.write(payload)
        await asyncio.wait_for(writer.drain(), timeout=client_timeout)
        response = await asyncio.wait_for(reader.readline(), timeout=client_timeout)
        if not response.endswith(b"\n") or len(response) > response_limit:
            raise RuntimeError("loopback response violated its framing bound")
        decoded = json.loads(response.decode("utf-8"))
        if not isinstance(decoded, dict):
            raise RuntimeError("loopback response must be an object")
        return decoded
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except ConnectionError:
            pass
