"""A bounded loopback UDP round trip."""

from __future__ import annotations

import socket


def round_trip(message: bytes = b"temperature=21.5") -> bytes:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(1.0)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.settimeout(1.0)
            sender.sendto(message, receiver.getsockname())
            data, address = receiver.recvfrom(1024)
            receiver.sendto(b"received:" + data, address)
            reply, _ = sender.recvfrom(1024)
            return reply


if __name__ == "__main__":
    print(round_trip().decode("ascii"))
