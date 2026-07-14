"""Bounded asyncio telemetry hub used by the chapter capstone."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import ssl
from collections import deque
from collections.abc import Iterable

from .protocol import ConnectionState, NDJSONDecoder, ProtocolError, encode_frame

LOGGER = logging.getLogger("telemetry.hub")
MAX_CLIENTS = 32
MAX_ACCEPTED_READINGS = 256
READ_SIZE = 4096


class AsyncTelemetryHub:
    """A loopback server with bounded clients, frames, state, and waits."""

    def __init__(self, *, client_timeout: float = 1.0) -> None:
        self.client_timeout = client_timeout
        self.server: asyncio.Server | None = None
        self._tasks: set[asyncio.Task[None]] = set()
        self._writers: set[asyncio.StreamWriter] = set()
        self.accepted: deque[tuple[str, int, int | float]] = deque(
            maxlen=MAX_ACCEPTED_READINGS
        )

    async def start(
        self,
        host: str = "127.0.0.1",
        port: int = 0,
        *,
        ssl_context: ssl.SSLContext | None = None,
        family: int = 0,
    ) -> tuple[str, int]:
        if self.server is not None:
            raise RuntimeError("hub is already started")
        self.server = await asyncio.start_server(
            self._accept,
            host,
            port,
            ssl=ssl_context,
            ssl_handshake_timeout=(
                self.client_timeout if ssl_context is not None else None
            ),
            ssl_shutdown_timeout=(
                self.client_timeout if ssl_context is not None else None
            ),
            family=family,
            limit=65_537,
        )
        socket = self.server.sockets[0]
        address = socket.getsockname()
        return str(address[0]), int(address[1])

    def _accept(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        if len(self._tasks) >= MAX_CLIENTS:
            writer.close()
            return
        task = asyncio.create_task(self._serve_client(reader, writer))
        self._tasks.add(task)
        self._writers.add(writer)
        task.add_done_callback(self._tasks.discard)

    async def _send(
        self, writer: asyncio.StreamWriter, message: dict[str, object]
    ) -> None:
        writer.write(encode_frame(message))
        await asyncio.wait_for(writer.drain(), timeout=self.client_timeout)

    async def _serve_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        decoder = NDJSONDecoder()
        state = ConnectionState()
        peer = writer.get_extra_info("peername")
        try:
            while True:
                try:
                    data = await asyncio.wait_for(
                        reader.read(READ_SIZE), timeout=self.client_timeout
                    )
                except TimeoutError:
                    LOGGER.info("closing inactive peer %r", peer)
                    break
                if not data:
                    try:
                        decoder.finish()
                    except ProtocolError as exc:
                        LOGGER.info("peer %r ended mid-frame: %s", peer, exc.message)
                    break
                try:
                    messages = decoder.feed(data)
                except ProtocolError as exc:
                    with contextlib.suppress(Exception):
                        await self._send(writer, exc.response())
                    if exc.fatal:
                        LOGGER.info("closing peer %r: %s", peer, exc.message)
                        break
                    continue

                for message in messages:
                    try:
                        response = state.process(message)
                    except ProtocolError as exc:
                        response = exc.response()
                    else:
                        self.accepted.append(state.readings[-1])
                    await self._send(writer, response)
        except (ConnectionError, TimeoutError) as exc:
            LOGGER.info("peer %r disconnected: %s", peer, type(exc).__name__)
        finally:
            self._writers.discard(writer)
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

    async def close(self) -> None:
        """Stop accepting, close clients, then await every handler."""
        if self.server is not None:
            self.server.close()
            await self.server.wait_closed()
            self.server = None
        for writer in tuple(self._writers):
            writer.close()
        for writer in tuple(self._writers):
            with contextlib.suppress(Exception):
                await writer.wait_closed()
        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
        self._writers.clear()


async def send_readings(
    host: str,
    port: int,
    readings: Iterable[dict[str, object]],
    *,
    ssl_context: ssl.SSLContext | None = None,
    server_hostname: str | None = None,
) -> list[dict[str, object]]:
    """Small capstone client with one pending request per response."""
    import json

    reader, writer = await asyncio.wait_for(
        asyncio.open_connection(
            host,
            port,
            ssl=ssl_context,
            server_hostname=server_hostname,
            limit=65_537,
        ),
        timeout=2.0,
    )
    responses: list[dict[str, object]] = []
    try:
        for reading in readings:
            writer.write(encode_frame(reading))
            await asyncio.wait_for(writer.drain(), timeout=1.0)
            line = await asyncio.wait_for(reader.readline(), timeout=1.0)
            if not line:
                raise ConnectionError("hub closed before responding")
            responses.append(json.loads(line))
    finally:
        writer.close()
        with contextlib.suppress(Exception):
            await writer.wait_closed()
    return responses


async def _demo() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    hub = AsyncTelemetryHub()
    host, port = await hub.start()
    print(f"hub listening on {host}:{port}")
    try:
        response = await send_readings(
            host,
            port,
            [
                {
                    "version": 1,
                    "type": "reading",
                    "sensor_id": "lab.temperature",
                    "sequence": 0,
                    "value": 21.5,
                }
            ],
        )
        print(response[0])
    finally:
        await hub.close()


if __name__ == "__main__":
    asyncio.run(_demo())
