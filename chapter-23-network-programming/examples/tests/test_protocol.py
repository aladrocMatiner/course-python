from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

EXAMPLES = Path(__file__).parents[1]
sys.path.insert(0, str(EXAMPLES))

from telemetry.protocol import (  # noqa: E402
    ConnectionState,
    NDJSONDecoder,
    ProtocolError,
    encode_frame,
)


def reading(
    sensor_id: str = "lab.temperature",
    sequence: int = 0,
    value: int | float = 21.5,
) -> dict[str, object]:
    return {
        "version": 1,
        "type": "reading",
        "sensor_id": sensor_id,
        "sequence": sequence,
        "value": value,
    }


class DecoderTests(unittest.TestCase):
    def test_fragmentation_and_coalescing_preserve_frames(self) -> None:
        first = encode_frame(reading(sequence=1))
        second = encode_frame(reading(sequence=2))
        decoder = NDJSONDecoder()
        self.assertEqual(decoder.feed(first[:7]), [])
        self.assertEqual(decoder.feed(first[7:] + second), [reading(sequence=1), reading(sequence=2)])
        self.assertEqual(decoder.buffered_bytes, 0)

    def test_exact_content_limit_is_accepted(self) -> None:
        decoder = NDJSONDecoder()
        result = decoder.feed(b" " * 65_534 + b"{}\n")
        self.assertEqual(result, [{}])

    def test_byte_beyond_limit_is_rejected_and_buffer_cleared(self) -> None:
        decoder = NDJSONDecoder()
        with self.assertRaisesRegex(ProtocolError, "65536") as caught:
            decoder.feed(b"x" * 65_537)
        self.assertTrue(caught.exception.fatal)
        self.assertEqual(decoder.buffered_bytes, 0)

    def test_bad_utf8_json_constant_and_partial_eof_are_fatal(self) -> None:
        for data in (b"\xff\n", b'{"value":NaN}\n'):
            with self.subTest(data=data):
                with self.assertRaises(ProtocolError) as caught:
                    NDJSONDecoder().feed(data)
                self.assertTrue(caught.exception.fatal)
        decoder = NDJSONDecoder()
        decoder.feed(b'{"still":"open"}')
        with self.assertRaises(ProtocolError) as caught:
            decoder.finish()
        self.assertTrue(caught.exception.fatal)

    def test_json_array_is_decoded_then_rejected_as_safe_schema_error(self) -> None:
        messages = NDJSONDecoder().feed(b"[]\n")
        self.assertEqual(messages, [[]])
        with self.assertRaises(ProtocolError) as caught:
            ConnectionState().process(messages[0])
        self.assertEqual(caught.exception.code, "invalid_message")
        self.assertFalse(caught.exception.fatal)


class ContractTests(unittest.TestCase):
    def test_acceptance_ack_and_state_are_exact(self) -> None:
        state = ConnectionState()
        self.assertEqual(
            state.process(reading(sequence=7)),
            {
                "version": 1,
                "type": "ack",
                "sensor_id": "lab.temperature",
                "sequence": 7,
                "status": "accepted",
            },
        )
        self.assertEqual(state.sequences, {"lab.temperature": 7})

    def test_schema_type_identifier_sequence_and_value_boundaries(self) -> None:
        valid = [
            reading("A", 0, -1_000_000),
            reading("a" + "-" * 63, 2**31 - 1, 1_000_000),
        ]
        for item in valid:
            with self.subTest(item=item):
                ConnectionState().process(item)

        invalid: list[dict[str, object]] = []
        missing = reading()
        missing.pop("value")
        invalid.append(missing)
        extra = reading()
        extra["extra"] = 1
        invalid.append(extra)
        for sensor in ("", "-bad", "é", "a" * 65):
            invalid.append(reading(sensor_id=sensor))
        for sequence in (True, -1, 2**31, 1.5):
            item = reading()
            item["sequence"] = sequence
            invalid.append(item)
        for value in (True, -1_000_001, 1_000_001, float("inf"), 10**1000):
            invalid.append(reading(value=value))

        for item in invalid:
            with self.subTest(item=item):
                with self.assertRaises(ProtocolError) as caught:
                    ConnectionState().process(item)
                self.assertEqual(caught.exception.code, "invalid_message")

    def test_wrong_version_is_distinct_and_rejection_is_transactional(self) -> None:
        state = ConnectionState()
        state.process(reading(sequence=2))
        snapshot = (state.sequences.copy(), state.readings.copy())
        wrong = reading(sequence=3)
        wrong["version"] = 2
        with self.assertRaises(ProtocolError) as caught:
            state.process(wrong)
        self.assertEqual(caught.exception.code, "unsupported_version")
        self.assertEqual((state.sequences, state.readings), snapshot)

    def test_duplicate_and_backward_sequence_do_not_mutate_state(self) -> None:
        state = ConnectionState()
        state.process(reading(sequence=5))
        for sequence in (5, 4):
            snapshot = (state.sequences.copy(), state.readings.copy())
            with self.assertRaises(ProtocolError) as caught:
                state.process(reading(sequence=sequence))
            self.assertEqual(caught.exception.code, "out_of_order")
            self.assertEqual((state.sequences, state.readings), snapshot)

    def test_sixty_fifth_sensor_is_rejected_without_evicting_state(self) -> None:
        state = ConnectionState()
        for index in range(64):
            state.process(reading(f"sensor-{index}"))
        with self.assertRaises(ProtocolError) as caught:
            state.process(reading("sensor-64"))
        self.assertEqual(caught.exception.code, "resource_limit")
        self.assertEqual(len(state.sequences), 64)
        ack = state.process(reading("sensor-0", sequence=1))
        self.assertEqual(ack["status"], "accepted")

    def test_error_envelope_is_bounded_and_does_not_echo_payload(self) -> None:
        error = ProtocolError("invalid_message", "value has an invalid type")
        encoded = encode_frame(error.response())
        body = json.loads(encoded)
        self.assertEqual(set(body), {"version", "type", "code", "message"})
        self.assertNotIn("secret-reading", encoded.decode())
        self.assertLessEqual(len(encoded) - 1, 65_536)


if __name__ == "__main__":
    unittest.main()
