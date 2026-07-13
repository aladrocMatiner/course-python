"""A blocking TCP echo lab for two terminals."""

from __future__ import annotations

import argparse
import socket

HOST = "127.0.0.1"
TIMEOUT = 30.0


def run_server(port: int) -> None:
    with socket.create_server((HOST, port), family=socket.AF_INET) as listener:
        actual_port = listener.getsockname()[1]
        print(f"listening on {HOST}:{actual_port}", flush=True)
        serve_one(listener)


def serve_one(listener: socket.socket) -> None:
    """Serve exactly one peer so the lab has a deterministic ending."""
    listener.settimeout(TIMEOUT)
    connection, _ = listener.accept()
    with connection:
        connection.settimeout(TIMEOUT)
        while data := connection.recv(4096):
            connection.sendall(data)


def request_echo(port: int, text: str) -> str:
    try:
        with socket.create_connection((HOST, port), timeout=TIMEOUT) as connection:
            connection.sendall(text.encode("utf-8"))
            connection.shutdown(socket.SHUT_WR)
            chunks: list[bytes] = []
            while chunk := connection.recv(4096):
                chunks.append(chunk)
        return b"".join(chunks).decode("utf-8")
    except (ConnectionRefusedError, TimeoutError, socket.timeout) as exc:
        raise SystemExit(f"connection failed safely: {exc}") from exc


def run_client(port: int, text: str) -> None:
    print(request_echo(port, text))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("server", "client"))
    parser.add_argument("--port", type=int, default=65432)
    parser.add_argument("--text", default="hello, network")
    args = parser.parse_args()
    if args.mode == "server":
        run_server(args.port)
    else:
        run_client(args.port, args.text)


if __name__ == "__main__":
    main()
