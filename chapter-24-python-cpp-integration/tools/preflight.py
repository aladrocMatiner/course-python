from __future__ import annotations

import platform
import re
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path


def version(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError as error:
        return f"MISSING ({error})"
    output = (result.stdout or result.stderr).splitlines()
    return output[0] if output else f"UNAVAILABLE (exit {result.returncode})"


def numeric_version(text: str) -> tuple[int, ...]:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text)
    return tuple(int(part) for part in match.groups(default="0")) if match else (0,)


def distribution_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "MISSING"


def compiler_command() -> tuple[str | None, list[str]]:
    if shutil.which("c++"):
        return shutil.which("c++"), ["c++", "--version"]
    if shutil.which("cl"):
        return shutil.which("cl"), ["cl"]
    return None, ["c++", "--version"]


def supports_cpp17() -> bool:
    compiler, _version_command = compiler_command()
    if compiler is None:
        return False
    with tempfile.TemporaryDirectory(prefix="course-cpp-preflight-") as directory:
        root = Path(directory)
        source = root / "probe.cpp"
        output = root / ("probe.exe" if platform.system() == "Windows" else "probe")
        source.write_text(
            "#include <optional>\nint main(){std::optional<int> value=17; return *value==17 ? 0 : 1;}\n",
            encoding="utf-8",
        )
        command = (
            [compiler, "/nologo", "/std:c++17", "/EHsc", str(source), f"/Fe:{output}"]
            if Path(compiler).name.lower() in {"cl", "cl.exe"}
            else [compiler, "-std=c++17", str(source), "-o", str(output)]
        )
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        return completed.returncode == 0


def main() -> int:
    active_venv = sys.prefix != sys.base_prefix
    _compiler, version_command = compiler_command()
    compiler_text = version(version_command)
    cmake_text = version(["cmake", "--version"])
    pip_text = version([sys.executable, "-m", "pip", "--version"])
    packages = {
        name: distribution_version(name)
        for name in ("pybind11", "scikit-build-core", "build", "pytest", "mypy")
    }
    print(f"interpreter={sys.executable}")
    print(
        f"python={platform.python_version()} implementation={platform.python_implementation()} "
        f"architecture={platform.architecture()[0]}"
    )
    print(f"venv={'active' if active_venv else 'inactive'}")
    print(f"compiler={compiler_text}")
    cpp17 = supports_cpp17()
    print(f"cxx17={'supported' if cpp17 else 'unsupported'}")
    print(f"cmake={cmake_text}")
    print(f"pip={pip_text}")
    for package, installed in packages.items():
        print(f"{package}={installed}")

    problems: list[str] = []
    if platform.python_implementation() != "CPython" or sys.version_info < (3, 11):
        problems.append("CPython >=3.11")
    if not active_venv:
        problems.append("active virtual environment")
    if not cpp17:
        problems.append("working C++17 compiler")
    if numeric_version(cmake_text) < (3, 20, 0):
        problems.append("CMake >=3.20")
    if numeric_version(pip_text) < (25, 3, 0):
        problems.append("pip >=25.3")
    if not (numeric_version(packages["pybind11"]) >= (3, 0, 4) and numeric_version(packages["pybind11"]) < (4, 0, 0)):
        problems.append("pybind11 >=3.0.4,<4")
    if not (
        numeric_version(packages["scikit-build-core"]) >= (1, 0, 3)
        and numeric_version(packages["scikit-build-core"]) < (2, 0, 0)
    ):
        problems.append("scikit-build-core >=1.0.3,<2")
    for package in ("build", "pytest", "mypy"):
        if packages[package] == "MISSING":
            problems.append(package)
    if problems:
        print(f"preflight failed; missing/unsupported={problems}")
        return 1
    print("preflight passed for the active environment")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
