"""Safe path-based loader for Appendix C pattern examples.

Pattern directories are display-oriented and intentionally contain spaces and
hyphens. They are not Python packages. Tests load their ``example.py`` files by
validated path so the learner-facing names never leak into import semantics.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType


def load_example(path: Path, appendix_root: Path) -> ModuleType:
    """Load one regular example file contained by ``appendix_root``."""

    root = appendix_root.resolve(strict=True)
    source = path.resolve(strict=True)
    source.relative_to(root)
    if source.is_symlink() or not source.is_file() or source.name != "example.py":
        raise ValueError("example must be a regular Appendix C example.py file")

    module_name = "appendix_c_" + source.parent.name.lower().replace(" ", "_").replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot create a loader for {source.relative_to(root)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module
