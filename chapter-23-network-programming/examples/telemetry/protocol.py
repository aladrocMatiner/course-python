"""Version-1 telemetry protocol shared by the chapter's servers."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any

MAX_CONTENT_BYTES = 65_536
MAX_SENSORS = 64
MAX_SEQUENCE = 2**31 - 1
MAX_ABS_VALUE = 1_000_000
SENSOR_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
READING_FIELDS = {"version", "type", "sensor_id", "sequence", "value"}


class ProtocolError(ValueError):
    """A bounded diagnostic suitable for a peer and an operator log."""

    def __init__(self, code: str, message: str, *, fatal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.fatal = fatal

    def response(self) -> dict[str, object]:
        return {
            "version": 1,
            "type": "error",
            "code": self.code,
            "message": self.message,
        }


class NDJSONDecoder:
    """Incrementally decode bounded UTF-8 JSON lines from a byte stream."""

    def __init__(self, max_content_bytes: int = MAX_CONTENT_BYTES) -> None:
        self._buffer = bytearray()
        self.max_content_bytes = max_content_bytes

    @property
    def buffered_bytes(self) -> int:
        return len(self._buffer)

    def feed(self, data: bytes) -> list[Any]:
        if not isinstance(data, bytes):
            raise TypeError("data must be bytes")
        self._buffer.extend(data)
        messages: list[Any] = []

        while True:
            newline = self._buffer.find(b"\n")
            if newline < 0:
                if len(self._buffer) > self.max_content_bytes:
                    self._buffer.clear()
                    raise ProtocolError(
                        "resource_limit", "frame exceeds 65536 bytes", fatal=True
                    )
                return messages
            if newline > self.max_content_bytes:
                self._buffer.clear()
                raise ProtocolError(
                    "resource_limit", "frame exceeds 65536 bytes", fatal=True
                )

            raw = bytes(self._buffer[:newline])
            del self._buffer[: newline + 1]
            try:
                text = raw.decode("utf-8")
                value = json.loads(
                    text,
                    parse_constant=lambda token: (_ for _ in ()).throw(
                        ValueError(f"invalid JSON constant: {token}")
                    ),
                )
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
                self._buffer.clear()
                raise ProtocolError(
                    "invalid_message", "frame is not valid UTF-8 JSON", fatal=True
                ) from exc
            messages.append(value)

    def finish(self) -> None:
        """Report an incomplete frame when the peer closes its write side."""
        if self._buffer:
            self._buffer.clear()
            raise ProtocolError(
                "invalid_message", "connection ended with an incomplete frame", fatal=True
            )


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_reading(message: object) -> tuple[str, int, int | float]:
    """Validate without mutating connection state."""
    if not isinstance(message, dict):
        raise ProtocolError("invalid_message", "frame must contain one JSON object")
    if set(message) != READING_FIELDS:
        raise ProtocolError("invalid_message", "reading fields do not match the schema")
    version = message["version"]
    if not _is_int(version) or version != 1:
        raise ProtocolError("unsupported_version", "only protocol version 1 is supported")
    if message["type"] != "reading":
        raise ProtocolError("invalid_message", "type must be reading")

    sensor_id = message["sensor_id"]
    if not isinstance(sensor_id, str) or SENSOR_ID.fullmatch(sensor_id) is None:
        raise ProtocolError("invalid_message", "sensor_id has an invalid format")

    sequence = message["sequence"]
    if not _is_int(sequence) or not 0 <= sequence <= MAX_SEQUENCE:
        raise ProtocolError("invalid_message", "sequence is outside its allowed range")

    value = message["value"]
    if not _is_number(value):
        raise ProtocolError("invalid_message", "value must be a JSON number")
    try:
        numeric = float(value)
    except OverflowError as exc:
        raise ProtocolError("invalid_message", "value is outside its allowed range") from exc
    if not math.isfinite(numeric) or abs(numeric) > MAX_ABS_VALUE:
        raise ProtocolError("invalid_message", "value is outside its allowed range")
    return sensor_id, sequence, value


@dataclass
class ConnectionState:
    """Sequence state belongs to one connection and changes transactionally."""

    sequences: dict[str, int] = field(default_factory=dict)
    readings: list[tuple[str, int, int | float]] = field(default_factory=list)

    def process(self, message: object) -> dict[str, object]:
        sensor_id, sequence, value = validate_reading(message)
        previous = self.sequences.get(sensor_id)
        if previous is not None and sequence <= previous:
            raise ProtocolError(
                "out_of_order", "sequence must be greater than the last accepted value"
            )
        if previous is None and len(self.sequences) >= MAX_SENSORS:
            raise ProtocolError("resource_limit", "connection already tracks 64 sensors")

        self.sequences[sensor_id] = sequence
        self.readings.append((sensor_id, sequence, value))
        return {
            "version": 1,
            "type": "ack",
            "sensor_id": sensor_id,
            "sequence": sequence,
            "status": "accepted",
        }


def encode_frame(message: dict[str, object]) -> bytes:
    """Encode one compact NDJSON response and enforce the shared bound."""
    content = json.dumps(
        message, ensure_ascii=True, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")
    if len(content) > MAX_CONTENT_BYTES:
        raise ValueError("encoded frame exceeds 65536 bytes")
    return content + b"\n"
