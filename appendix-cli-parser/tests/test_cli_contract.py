from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cli_contract import main


class CLIContractTests(unittest.TestCase):
    def test_valid_note_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "note.txt")
            path.write_text("hello", encoding="utf-8")
            output = StringIO()
            self.assertEqual(0, main(["show", str(path)], stdout=output))
            self.assertEqual("hello\n", output.getvalue())

    def test_missing_file_returns_one_without_raw_exception(self) -> None:
        errors = StringIO()
        self.assertEqual(1, main(["show", "missing.txt"], stderr=errors))
        self.assertIn("note not found", errors.getvalue())

    def test_invalid_arguments_return_two(self) -> None:
        errors = StringIO()
        self.assertEqual(2, main([], stderr=errors))
        self.assertIn("usage error", errors.getvalue())

    def test_unexpected_programming_error_is_not_hidden(self) -> None:
        with patch.object(Path, "read_text", side_effect=RuntimeError("bug")):
            with self.assertRaisesRegex(RuntimeError, "bug"):
                main(["show", "note.txt"], stderr=StringIO())


if __name__ == "__main__":
    unittest.main()
