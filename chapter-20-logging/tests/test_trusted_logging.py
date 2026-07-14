import json
from pathlib import Path
import tempfile
import unittest

from trusted_logging import apply_trusted_json_logging_config, build_logging_config


class TrustedLoggingTests(unittest.TestCase):
    def test_accepts_allowlisted_level(self) -> None:
        config = build_logging_config({"level": "INFO"})
        self.assertEqual("INFO", config["root"]["level"])

    def test_rejects_factory_or_handler_in_untrusted_settings(self) -> None:
        with self.assertRaises(ValueError):
            build_logging_config({"level": "INFO", "()": "package.factory"})
        with self.assertRaises(ValueError):
            build_logging_config({"handlers": {}})

    def test_loads_application_owned_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "logging.json")
            path.write_text(json.dumps({"level": "WARNING"}), encoding="utf-8")
            apply_trusted_json_logging_config(path)


if __name__ == "__main__":
    unittest.main()
