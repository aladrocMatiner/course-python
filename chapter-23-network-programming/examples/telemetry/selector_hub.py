"""A bounded selectors implementation for the intermediate route."""

from __future__ import annotations

import selectors
import socket
from collections import deque
from dataclasses import dataclass, field

from .protocol import ConnectionState, NDJSONDecoder, ProtocolError, encode_frame

MAX_CLIENTS = 32


@dataclass
class Peer:
    decoder: NDJSONDecoder = field(default_factory=NDJSONDecoder)
    state: ConnectionState = field(default_factory=ConnectionState)
    output: bytes = b""
    decoded: deque[object] = field(default_factory=deque)
    close_after_write: bool = False


class SelectorTelemetryHub:
    """One event loop; each peer may hold at most one pending response."""

    def __init__(self, timeout: float = 0.1) -> None:
        self.timeout = timeout
        self.selector = selectors.DefaultSelector()
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen()
        self.listener.setblocking(False)
        self.selector.register(self.listener, selectors.EVENT_READ, None)
        self.running = False
        self.peers: dict[socket.socket, Peer] = {}

    @property
    def address(self) -> tuple[str, int]:
        host, port = self.listener.getsockname()
        return str(host), int(port)

    def _close_peer(self, connection: socket.socket) -> None:
        self.peers.pop(connection, None)
        try:
            self.selector.unregister(connection)
        except (KeyError, ValueError):
            pass
        connection.close()

    def _accept(self) -> None:
        connection, _ = self.listener.accept()
        if len(self.peers) >= MAX_CLIENTS:
            connection.close()
            return
        connection.setblocking(False)
        peer = Peer()
        self.peers[connection] = peer
        self.selector.register(connection, selectors.EVENT_READ, peer)

    def _read(self, connection: socket.socket, peer: Peer) -> None:
        try:
            data = connection.recv(4096)
            if not data:
                peer.decoder.finish()
                self._close_peer(connection)
                return
            peer.decoded.extend(peer.decoder.feed(data))
            if not peer.decoded:
                return
            self._prepare_one_response(connection, peer)
        except ProtocolError as exc:
            peer.output = encode_frame(exc.response())
            peer.close_after_write = exc.fatal
            self.selector.modify(connection, selectors.EVENT_WRITE, peer)
        except ConnectionError:
            self._close_peer(connection)

    def _prepare_one_response(self, connection: socket.socket, peer: Peer) -> None:
        # One response is encoded at a time. A single bounded recv may already
        # contain several complete frames, so parsed frames wait here.
        message = peer.decoded.popleft()
        try:
            response = peer.state.process(message)
        except ProtocolError as exc:
            response = exc.response()
        peer.output = encode_frame(response)
        self.selector.modify(connection, selectors.EVENT_WRITE, peer)

    def _write(self, connection: socket.socket, peer: Peer) -> None:
        try:
            sent = connection.send(peer.output)
        except ConnectionError:
            self._close_peer(connection)
            return
        peer.output = peer.output[sent:]
        if not peer.output:
            if peer.close_after_write:
                self._close_peer(connection)
            elif peer.decoded:
                self._prepare_one_response(connection, peer)
            else:
                self.selector.modify(connection, selectors.EVENT_READ, peer)

    def serve(self) -> None:
        self.running = True
        try:
            while self.running:
                for key, mask in self.selector.select(self.timeout):
                    if key.fileobj is self.listener:
                        self._accept()
                    elif mask & selectors.EVENT_READ:
                        self._read(key.fileobj, key.data)
                    else:
                        self._write(key.fileobj, key.data)
        finally:
            self.close()

    def close(self) -> None:
        self.running = False
        for connection in tuple(self.peers):
            self._close_peer(connection)
        try:
            self.selector.unregister(self.listener)
        except (KeyError, ValueError):
            pass
        self.listener.close()
        self.selector.close()


if __name__ == "__main__":
    hub = SelectorTelemetryHub()
    print(f"selector hub listening on {hub.address[0]}:{hub.address[1]}", flush=True)
    try:
        hub.serve()
    except KeyboardInterrupt:
        hub.close()
