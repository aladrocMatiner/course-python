"""Bounded loopback HTTP handler used by the Chapter 19 regression tests."""

from http.server import BaseHTTPRequestHandler
import json
import socket
from urllib.parse import urlsplit


class EchoHandler(BaseHTTPRequestHandler):
    MAX_BODY = 1_000_000
    READ_TIMEOUT = 1.0

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path in {"/health", "/search"}:
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/echo":
            self._send_json(404, {"error": "not found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "application/json required"})
            return

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._send_json(411, {"error": "content length required"})
            return
        if not raw_length.isascii() or not raw_length.isdecimal():
            self._send_json(400, {"error": "invalid content length"})
            return

        normalized_length = raw_length.lstrip("0") or "0"
        maximum = str(self.MAX_BODY)
        if len(normalized_length) > len(maximum) or (
            len(normalized_length) == len(maximum) and normalized_length > maximum
        ):
            self._send_json(413, {"error": "payload too large"})
            return
        length = int(normalized_length)

        self.connection.settimeout(self.READ_TIMEOUT)
        try:
            data = self.rfile.read(length)
        except (TimeoutError, socket.timeout):
            self._send_json(408, {"error": "request body timeout"})
            return
        if len(data) != length:
            self._send_json(400, {"error": "incomplete request body"})
            return

        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid json"})
            return
        self._send_json(200, {"ok": True, "received": payload})

    def log_message(self, format: str, *args: object) -> None:
        """Keep automated lesson tests quiet."""
