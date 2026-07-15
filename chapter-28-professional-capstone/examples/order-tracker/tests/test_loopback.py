from __future__ import annotations

import asyncio
import json
import unittest

from order_tracker import InMemoryOrderRepository, OrderService
from order_tracker.loopback import (
    LOOPBACK_HOST,
    MIN_RESPONSE_BYTES,
    LoopbackOrderServer,
    send_request,
)


async def raw_request(address: tuple[str, int], payload: bytes) -> dict[str, object]:
    reader, writer = await asyncio.wait_for(asyncio.open_connection(*address), timeout=1)
    try:
        writer.write(payload)
        await asyncio.wait_for(writer.drain(), timeout=1)
        response = await asyncio.wait_for(reader.readline(), timeout=1)
        return json.loads(response)
    finally:
        writer.close()
        await writer.wait_closed()


class LoopbackTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.service = OrderService(InMemoryOrderRepository())

    async def asyncTearDown(self) -> None:
        self.service.close()

    async def test_constructor_rejects_values_that_cannot_preserve_bounds(self) -> None:
        invalid_options = (
            {"max_request_bytes": True},
            {"max_response_bytes": MIN_RESPONSE_BYTES - 1},
            {"max_requests": 101},
            {"max_concurrency": 33},
            {"max_list_orders": 101},
            {"idle_timeout": 10.1},
        )
        for options in invalid_options:
            with self.subTest(options=options), self.assertRaises(ValueError):
                LoopbackOrderServer(self.service, **options)

    async def test_happy_request_reuses_service_on_ephemeral_loopback(self) -> None:
        async with LoopbackOrderServer(self.service) as server:
            host, port = server.address
            self.assertEqual(host, LOOPBACK_HOST)
            self.assertGreater(port, 0)
            added = await send_request(
                server.address,
                {"action": "add", "order_id": "NET-1", "item": "widget", "quantity": 2},
            )
            listed = await send_request(server.address, {"action": "list"})
            self.assertTrue(added["ok"])
            self.assertEqual(added["order"]["status"], "pending")
            self.assertEqual(listed["orders"][0]["order_id"], "NET-1")
        self.assertEqual(server.owned_task_count, 0)

    async def test_malformed_and_oversized_requests_fail_closed_then_recover(self) -> None:
        async with LoopbackOrderServer(self.service, max_request_bytes=128) as server:
            malformed = await raw_request(server.address, b"not-json\n")
            base = b'{"action":"list"}'
            exact_boundary = base + (b" " * (128 - len(base) - 1)) + b"\n"
            accepted = await raw_request(server.address, exact_boundary)
            invalid_utf8 = await raw_request(server.address, b"\xff\n")
            oversized = await raw_request(server.address, (b"x" * 129) + b"\n")
            recovered = await send_request(server.address, {"action": "list"})
            self.assertEqual(malformed, {"error": "malformed-request", "ok": False})
            self.assertEqual(accepted, {"ok": True, "orders": []})
            self.assertEqual(invalid_utf8, {"error": "malformed-request", "ok": False})
            self.assertEqual(oversized, {"error": "request-too-large", "ok": False})
            self.assertEqual(recovered, {"ok": True, "orders": []})

    async def test_list_item_cap_returns_bounded_error(self) -> None:
        for number in range(3):
            self.service.create(f"NET-{number}", "widget", 1)
        async with LoopbackOrderServer(self.service, max_list_orders=2) as server:
            response = await send_request(server.address, {"action": "list"})
            self.assertEqual(response, {"error": "response-limit", "ok": False})

    async def test_busy_connection_releases_capacity_without_fixed_sleep(self) -> None:
        async with LoopbackOrderServer(
            self.service,
            max_concurrency=1,
            idle_timeout=0.5,
        ) as server:
            first_reader, first_writer = await asyncio.open_connection(*server.address)
            await asyncio.wait_for(server.connection_started.wait(), timeout=1)
            self.assertEqual(server.active_connections, 1)
            busy = await send_request(server.address, {"action": "list"})
            self.assertEqual(busy, {"error": "busy", "ok": False})

            first_writer.write(b'{"action":"list"}\n')
            await first_writer.drain()
            self.assertEqual(json.loads(await first_reader.readline()), {"ok": True, "orders": []})
            first_writer.close()
            await first_writer.wait_closed()
            await asyncio.wait_for(server.capacity_available.wait(), timeout=1)
            recovered = await send_request(server.address, {"action": "list"})
            self.assertTrue(recovered["ok"])

    async def test_idle_peer_times_out_and_capacity_recovers(self) -> None:
        async with LoopbackOrderServer(
            self.service,
            max_concurrency=1,
            idle_timeout=0.05,
        ) as server:
            reader, writer = await asyncio.open_connection(*server.address)
            await asyncio.wait_for(server.connection_started.wait(), timeout=1)
            response = json.loads(await asyncio.wait_for(reader.readline(), timeout=1))
            self.assertEqual(response, {"error": "timeout", "ok": False})
            writer.close()
            await writer.wait_closed()
            await asyncio.wait_for(server.capacity_available.wait(), timeout=1)
            recovered = await send_request(server.address, {"action": "list"})
            self.assertTrue(recovered["ok"])

    async def test_total_request_limit_has_stable_outcome_and_clean_shutdown(self) -> None:
        async with LoopbackOrderServer(self.service, max_requests=1) as server:
            self.assertTrue((await send_request(server.address, {"action": "list"}))["ok"])
            rejected = await send_request(server.address, {"action": "list"})
            self.assertEqual(rejected, {"error": "request-limit", "ok": False})
        self.assertEqual(server.active_connections, 0)
        self.assertEqual(server.owned_task_count, 0)

    async def test_close_cancels_stalled_handler_and_closes_socket(self) -> None:
        server = LoopbackOrderServer(self.service, idle_timeout=10)
        await server.start()
        reader, writer = await asyncio.open_connection(*server.address)
        await asyncio.wait_for(server.connection_started.wait(), timeout=1)
        await server.close()
        self.assertEqual(await asyncio.wait_for(reader.read(), timeout=1), b"")
        self.assertEqual(server.active_connections, 0)
        self.assertEqual(server.owned_task_count, 0)
        writer.close()
        await writer.wait_closed()


if __name__ == "__main__":
    unittest.main()
