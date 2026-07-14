from __future__ import annotations

import asyncio
import contextlib
import json
import socket
import ssl
import sys
import threading
import unittest
from datetime import UTC, datetime
from pathlib import Path

EXAMPLES = Path(__file__).parents[1]
sys.path.insert(0, str(EXAMPLES))

from telemetry.address_demo import ipv6_loopback_available  # noqa: E402
from telemetry.async_hub import (  # noqa: E402
    MAX_ACCEPTED_READINGS,
    MAX_CLIENTS,
    AsyncTelemetryHub,
    send_readings,
)
from telemetry.echo import request_echo, serve_one  # noqa: E402
from telemetry.protocol import MAX_RETAINED_READINGS, encode_frame  # noqa: E402
from telemetry.selector_hub import (  # noqa: E402
    MAX_CLIENTS as SELECTOR_MAX_CLIENTS,
    SelectorTelemetryHub,
)
from telemetry.tls import client_context, server_context  # noqa: E402
from telemetry.udp_demo import round_trip  # noqa: E402


def reading(sensor: str, sequence: int = 0) -> dict[str, object]:
    return {
        "version": 1,
        "type": "reading",
        "sensor_id": sensor,
        "sequence": sequence,
        "value": 21.5,
    }


async def wait_until(predicate: object, timeout: float = 1.0) -> None:
    async def poll() -> None:
        while not predicate():  # type: ignore[operator]
            await asyncio.sleep(0)

    await asyncio.wait_for(poll(), timeout=timeout)


class DatagramAndSelectorTests(unittest.TestCase):
    def test_blocking_tcp_echo_round_trip_and_eof_cleanup(self) -> None:
        with socket.create_server(("127.0.0.1", 0)) as listener:
            thread = threading.Thread(target=serve_one, args=(listener,), daemon=True)
            thread.start()
            self.assertEqual(request_echo(listener.getsockname()[1], "hej å"), "hej å")
            thread.join(timeout=1.0)
            self.assertFalse(thread.is_alive(), "blocking echo did not stop after EOF")

    def test_udp_round_trip_preserves_one_datagram(self) -> None:
        self.assertEqual(round_trip(b"edge"), b"received:edge")

    def test_udp_empty_datagram_is_data_not_eof(self) -> None:
        self.assertEqual(round_trip(b""), b"received:")

    def test_udp_timeout_is_bounded(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("127.0.0.1", 0))
            receiver.settimeout(0.02)
            with self.assertRaises(socket.timeout):
                receiver.recvfrom(64)

    def test_selector_hub_serves_two_clients_and_coalesced_frames(self) -> None:
        hub = SelectorTelemetryHub(timeout=0.01)
        thread = threading.Thread(target=hub.serve, daemon=True)
        thread.start()
        clients: list[socket.socket] = []
        try:
            for index in range(2):
                client = socket.create_connection(hub.address, timeout=1.0)
                client.settimeout(1.0)
                clients.append(client)
                client.sendall(
                    encode_frame(reading(f"selector-{index}", 0))
                    + encode_frame(reading(f"selector-{index}", 1))
                )
            for client in clients:
                stream = client.makefile("rb")
                first = json.loads(stream.readline())
                second = json.loads(stream.readline())
                self.assertEqual((first["sequence"], second["sequence"]), (0, 1))
        finally:
            for client in clients:
                client.close()
            hub.running = False
            thread.join(timeout=1.0)
            if thread.is_alive():
                hub.close()
                self.fail("selector hub did not stop within its bound")
        self.assertEqual(hub.peers, {})

    def test_selector_hub_closes_thirty_third_client(self) -> None:
        hub = SelectorTelemetryHub()
        clients: list[socket.socket] = []
        try:
            for _ in range(32):
                client = socket.create_connection(hub.address, timeout=1.0)
                clients.append(client)
                hub._accept()
            self.assertEqual(len(hub.peers), 32)

            excess = socket.create_connection(hub.address, timeout=1.0)
            excess.settimeout(1.0)
            clients.append(excess)
            hub._accept()
            self.assertEqual(excess.recv(1), b"")
            self.assertEqual(len(hub.peers), 32)
        finally:
            for client in clients:
                client.close()
            hub.close()

    def test_selector_hub_expires_thirty_two_idle_partial_clients(self) -> None:
        now = [10.0]
        hub = SelectorTelemetryHub(
            timeout=0.01, idle_timeout=0.5, clock=lambda: now[0]
        )
        clients: list[socket.socket] = []
        try:
            for _ in range(SELECTOR_MAX_CLIENTS):
                client = socket.create_connection(hub.address, timeout=1.0)
                clients.append(client)
                hub._accept()
                client.sendall(b"{")
            for connection, peer in tuple(hub.peers.items()):
                hub._read(connection, peer)
            self.assertEqual(len(hub.peers), SELECTOR_MAX_CLIENTS)
            self.assertTrue(all(peer.decoder.buffered_bytes == 1 for peer in hub.peers.values()))

            now[0] += 0.5
            hub._expire_idle_peers()
            self.assertEqual(hub.peers, {})
            for client in clients:
                client.settimeout(1.0)
                self.assertEqual(client.recv(1), b"")

            replacement = socket.create_connection(hub.address, timeout=1.0)
            clients.append(replacement)
            hub._accept()
            self.assertEqual(len(hub.peers), 1)
        finally:
            for client in clients:
                client.close()
            hub.close()


class AsyncHubTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.hub = AsyncTelemetryHub(client_timeout=0.15)
        self.host, self.port = await self.hub.start()

    async def asyncTearDown(self) -> None:
        await self.hub.close()

    async def test_happy_path_schema_error_and_recovery_share_connection(self) -> None:
        bad = reading("async-a", 1)
        bad["extra"] = "not allowed"
        responses = await send_readings(
            self.host,
            self.port,
            [reading("async-a", 0), bad, reading("async-a", 2)],
        )
        self.assertEqual([item["type"] for item in responses], ["ack", "error", "ack"])
        self.assertEqual(responses[1]["code"], "invalid_message")
        self.assertEqual([item[1] for item in self.hub.accepted], [0, 2])

    async def test_long_session_bounds_connection_and_observer_history(self) -> None:
        count = max(MAX_RETAINED_READINGS, MAX_ACCEPTED_READINGS) + 19
        responses = await send_readings(
            self.host,
            self.port,
            [reading("bounded", sequence) for sequence in range(count)],
        )
        self.assertEqual(len(responses), count)
        self.assertTrue(all(item["status"] == "accepted" for item in responses))
        self.assertEqual(len(self.hub.accepted), MAX_ACCEPTED_READINGS)
        self.assertEqual(self.hub.accepted[0][1], count - MAX_ACCEPTED_READINGS)
        self.assertEqual(self.hub.accepted[-1][1], count - 1)

    async def test_slow_peer_does_not_block_fast_peer(self) -> None:
        slow_reader, slow_writer = await asyncio.open_connection(self.host, self.port)
        slow_writer.write(b'{"version":1')
        await slow_writer.drain()
        try:
            fast = await asyncio.wait_for(
                send_readings(self.host, self.port, [reading("fast")]), timeout=0.5
            )
            self.assertEqual(fast[0]["status"], "accepted")
        finally:
            slow_writer.close()
            await slow_writer.wait_closed()
            del slow_reader

    async def test_pending_output_timeout_is_bounded(self) -> None:
        class StalledWriter:
            def __init__(self) -> None:
                self.output = b""

            def write(self, data: bytes) -> None:
                self.output += data

            async def drain(self) -> None:
                await asyncio.Event().wait()

        self.hub.client_timeout = 0.02
        writer = StalledWriter()
        with self.assertRaises(TimeoutError):
            await self.hub._send(  # type: ignore[arg-type]
                writer, {"version": 1, "type": "ack", "status": "accepted"}
            )
        self.assertLessEqual(len(writer.output), 256)

    async def test_idle_and_partial_peers_are_cleaned_up(self) -> None:
        reader, writer = await asyncio.open_connection(self.host, self.port)
        writer.write(b"{")
        await writer.drain()
        await asyncio.wait_for(reader.read(), timeout=0.5)
        writer.close()
        await writer.wait_closed()
        await wait_until(lambda: not self.hub._tasks)
        self.assertEqual(self.hub._writers, set())

    async def test_thirty_third_client_is_closed_in_bounded_time(self) -> None:
        # Keep the first clients alive while the operating system completes the
        # bounded burst of connection handshakes on slower CI machines.
        self.hub.client_timeout = 2.0
        clients: list[tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []
        try:
            for _ in range(MAX_CLIENTS):
                clients.append(await asyncio.open_connection(self.host, self.port))
            await wait_until(lambda: len(self.hub._tasks) == MAX_CLIENTS)
            reader, writer = await asyncio.open_connection(self.host, self.port)
            self.assertEqual(await asyncio.wait_for(reader.read(1), timeout=0.5), b"")
            writer.close()
            await writer.wait_closed()
        finally:
            for _reader, writer in clients:
                writer.close()
            await asyncio.gather(
                *(writer.wait_closed() for _reader, writer in clients),
                return_exceptions=True,
            )

    async def test_shutdown_closes_listener_and_handlers(self) -> None:
        _reader, writer = await asyncio.open_connection(self.host, self.port)
        await wait_until(lambda: bool(self.hub._tasks))
        await self.hub.close()
        self.assertIsNone(self.hub.server)
        self.assertEqual(self.hub._tasks, set())
        self.assertEqual(self.hub._writers, set())
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()

    async def test_ipv6_loopback_or_explained_skip(self) -> None:
        if not ipv6_loopback_available():
            self.skipTest("IPv6 loopback is unavailable; IPv4 remains the required path")
        hub = AsyncTelemetryHub()
        host, port = await hub.start("::1", family=socket.AF_INET6)
        try:
            result = await send_readings(host, port, [reading("ipv6")])
            self.assertEqual(result[0]["status"], "accepted")
        finally:
            await hub.close()


class TLSTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.previous_exception_handler = self.loop.get_exception_handler()
        self.unexpected_loop_errors: list[dict[str, object]] = []
        self.allow_handshake_timeout = False
        self.observed_handshake_timeouts = 0

        def capture_expected_handshake_reset(
            _loop: asyncio.AbstractEventLoop, context: dict[str, object]
        ) -> None:
            # A client that rejects a server certificate resets that server-side
            # handshake. It is the expected negative-test result, not a leak.
            exception = context.get("exception")
            if isinstance(exception, ConnectionResetError):
                return
            if (
                self.allow_handshake_timeout
                and isinstance(exception, ConnectionAbortedError)
            ):
                self.observed_handshake_timeouts += 1
                return
            self.unexpected_loop_errors.append(context)

        self.loop.set_exception_handler(capture_expected_handshake_reset)

    async def asyncTearDown(self) -> None:
        await asyncio.sleep(0)
        self.loop.set_exception_handler(self.previous_exception_handler)
        self.assertEqual(self.unexpected_loop_errors, [])

    async def _start_tls_hub(
        self, certificate: str, key: str
    ) -> tuple[AsyncTelemetryHub, str, int]:
        hub = AsyncTelemetryHub()
        host, port = await hub.start(
            ssl_context=server_context(certificate=certificate, key=key)
        )
        return hub, host, port

    async def test_trusted_localhost_completes_handshake_and_protocol(self) -> None:
        hub, host, port = await self._start_tls_hub(
            "localhost-cert.pem", "localhost-key.pem"
        )
        try:
            result = await send_readings(
                host,
                port,
                [reading("tls")],
                ssl_context=client_context(),
                server_hostname="localhost",
            )
            self.assertEqual(result[0]["status"], "accepted")
        finally:
            await hub.close()

    async def test_tls_handshake_timeout_releases_pre_handler_peer(self) -> None:
        hub = AsyncTelemetryHub(client_timeout=0.05)
        self.allow_handshake_timeout = True
        host, port = await hub.start(
            ssl_context=server_context(
                certificate="localhost-cert.pem", key="localhost-key.pem"
            )
        )
        writer: asyncio.StreamWriter | None = None
        try:
            _reader, writer = await asyncio.open_connection(host, port)
            # Yield readiness once so the server accepts the TCP peer. The TLS
            # handshake then waits for a ClientHello before _accept can run.
            await asyncio.sleep(0)
            self.assertEqual(hub._tasks, set())
            await asyncio.wait_for(hub.close(), timeout=0.5)
            await wait_until(
                lambda: self.observed_handshake_timeouts == 1, timeout=0.5
            )
            self.assertEqual(self.observed_handshake_timeouts, 1)
            self.assertIsNone(hub.server)
        finally:
            if writer is not None:
                writer.close()
                with contextlib.suppress(ConnectionError):
                    await writer.wait_closed()
            await hub.close()

    async def test_hostname_mismatch_fails_closed(self) -> None:
        hub, host, port = await self._start_tls_hub(
            "localhost-cert.pem", "localhost-key.pem"
        )
        try:
            with self.assertRaises(ssl.SSLCertVerificationError):
                await send_readings(
                    host,
                    port,
                    [reading("tls")],
                    ssl_context=client_context(),
                    server_hostname="wrong.example",
                )
        finally:
            await hub.close()

    async def test_expired_certificate_fails_closed(self) -> None:
        hub, host, port = await self._start_tls_hub(
            "expired-cert.pem", "expired-key.pem"
        )
        try:
            with self.assertRaises(ssl.SSLCertVerificationError):
                await send_readings(
                    host,
                    port,
                    [reading("tls")],
                    ssl_context=client_context(),
                    server_hostname="localhost",
                )
        finally:
            await hub.close()

    async def test_untrusted_certificate_fails_closed(self) -> None:
        hub, host, port = await self._start_tls_hub(
            "untrusted-cert.pem", "untrusted-key.pem"
        )
        try:
            with self.assertRaises(ssl.SSLCertVerificationError):
                await send_readings(
                    host,
                    port,
                    [reading("tls")],
                    ssl_context=client_context(),
                    server_hostname="localhost",
                )
        finally:
            await hub.close()

    async def test_valid_certificate_has_more_than_ten_years_remaining(self) -> None:
        hub, host, port = await self._start_tls_hub(
            "localhost-cert.pem", "localhost-key.pem"
        )
        writer: asyncio.StreamWriter | None = None
        try:
            _reader, writer = await asyncio.open_connection(
                host,
                port,
                ssl=client_context(),
                server_hostname="localhost",
            )
            ssl_object = writer.get_extra_info("ssl_object")
            self.assertIsNotNone(ssl_object)
            certificate = ssl_object.getpeercert()
            self.assertIn("notAfter", certificate)
            expiry = datetime.fromtimestamp(
                ssl.cert_time_to_seconds(certificate["notAfter"]), UTC
            )
            remaining = expiry - datetime.now(UTC)
            self.assertGreater(remaining.days, 3650, "renew the public teaching fixture")
        finally:
            if writer is not None:
                writer.close()
                await writer.wait_closed()
            await hub.close()


if __name__ == "__main__":
    unittest.main()
