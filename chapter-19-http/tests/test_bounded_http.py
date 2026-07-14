import http.client
from http.server import HTTPServer
import json
import socket
import threading
import time
import unittest

from bounded_http import EchoHandler


class FastEchoHandler(EchoHandler):
    MAX_BODY = 64
    READ_TIMEOUT = 0.1


class BoundedHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), FastEchoHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.host, cls.port = cls.server.server_address

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, method: str, path: str, body: bytes | None, headers: dict[str, str]):
        connection = http.client.HTTPConnection(self.host, self.port, timeout=1)
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        payload = json.loads(response.read())
        connection.close()
        return response.status, payload

    def raw_status(self, request: bytes) -> int:
        with socket.create_connection((self.host, self.port), timeout=1) as client:
            client.sendall(request)
            chunks = []
            while chunk := client.recv(4096):
                chunks.append(chunk)
        response = b"".join(chunks)
        return int(response.split(b" ", 2)[1])

    def test_accepts_documented_json_request(self) -> None:
        body = b'{"message":"hello"}'
        status, payload = self.request(
            "POST",
            "/echo",
            body,
            {"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        self.assertEqual(200, status)
        self.assertEqual({"message": "hello"}, payload["received"])

    def test_accepts_length_at_inclusive_limit(self) -> None:
        body = b'"' + (b"a" * (FastEchoHandler.MAX_BODY - 2)) + b'"'
        status, payload = self.request(
            "POST",
            "/echo",
            body,
            {"Content-Type": "application/json", "Content-Length": str(len(body))},
        )
        self.assertEqual(200, status)
        self.assertEqual("a" * (FastEchoHandler.MAX_BODY - 2), payload["received"])

    def test_rejects_negative_malformed_and_oversized_lengths_promptly(self) -> None:
        missing = (
            b"POST /echo HTTP/1.1\r\n"
            b"Host: 127.0.0.1\r\n"
            b"Content-Type: application/json\r\n"
            b"Connection: close\r\n\r\n"
        )
        self.assertEqual(411, self.raw_status(missing))

        cases = (("-1", 400), ("nope", 400), ("65", 413), ("9" * 5000, 413))
        for declared, expected in cases:
            with self.subTest(declared=declared):
                started = time.monotonic()
                status, _ = self.request(
                    "POST",
                    "/echo",
                    None,
                    {"Content-Type": "application/json", "Content-Length": declared},
                )
                self.assertEqual(expected, status)
                self.assertLess(time.monotonic() - started, 0.5)

    def test_rejects_wrong_route_and_media_type(self) -> None:
        status, _ = self.request(
            "POST",
            "/other",
            b"{}",
            {"Content-Type": "application/json", "Content-Length": "2"},
        )
        self.assertEqual(404, status)
        status, _ = self.request(
            "POST",
            "/echo",
            b"{}",
            {"Content-Type": "text/plain", "Content-Length": "2"},
        )
        self.assertEqual(415, status)


if __name__ == "__main__":
    unittest.main()
