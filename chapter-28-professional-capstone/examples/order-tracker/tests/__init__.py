"""Make the src-layout package importable only for this source test suite."""

from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE))

