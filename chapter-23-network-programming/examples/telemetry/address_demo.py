"""Resolve only local addresses and report an IPv6 capability check."""

from __future__ import annotations

import socket


def local_addresses() -> list[tuple[int, tuple[object, ...]]]:
    return [
        (family, address)
        for family, _kind, _proto, _name, address in socket.getaddrinfo(
            "localhost", 0, type=socket.SOCK_STREAM
        )
    ]


def ipv6_loopback_available() -> bool:
    if not socket.has_ipv6:
        return False
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as probe:
            probe.bind(("::1", 0))
    except OSError:
        return False
    return True


if __name__ == "__main__":
    for family, address in local_addresses():
        print(socket.AddressFamily(family).name, address)
    print("IPv6 loopback available:", ipv6_loopback_available())
