"""TLS contexts that always verify trust and host identity."""

from __future__ import annotations

import ssl
from pathlib import Path

CERTIFICATES = Path(__file__).parents[1] / "certificates"


def server_context(
    certificate: str = "localhost-cert.pem", key: str = "localhost-key.pem"
) -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(CERTIFICATES / certificate, CERTIFICATES / key)
    return context


def client_context(ca: str = "lab-ca-cert.pem") -> ssl.SSLContext:
    context = ssl.create_default_context(cafile=CERTIFICATES / ca)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    # create_default_context keeps CERT_REQUIRED and check_hostname enabled.
    return context
