from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CHAPTER / "tools"))

from _support import create_dev_environment, environment_with, executable, run  # noqa: E402


def bootstrap_if_needed() -> None:
    if os.environ.get("COURSE_CPP_VERIFY_PYTHON"):
        return
    temporary = tempfile.TemporaryDirectory(prefix="faststats-artifact-bootstrap-")
    environment = Path(temporary.name) / "dev-venv"
    python = create_dev_environment(environment)
    env = environment_with(environment, COURSE_CPP_VERIFY_PYTHON=str(python))
    result = subprocess.run([str(python), str(Path(__file__).resolve())], env=env, check=False)
    temporary.cleanup()
    raise SystemExit(result.returncode)


def safe_extract(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as package:
        package.extractall(destination, filter="data")
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"sdist must contain one root directory, found {roots}")
    return roots[0]


def inspect_sdist(archive: Path) -> None:
    with tarfile.open(archive, "r:gz") as package:
        names = package.getnames()
    required_suffixes = (
        "CMakeLists.txt",
        "cpp/include/faststats_cpp/core.hpp",
        "cpp/src/core.cpp",
        "cpp/src/bindings.cpp",
        "python/faststats_cpp/_native.pyi",
        "python/faststats_cpp/py.typed",
    )
    for suffix in required_suffixes:
        if not any(name.endswith(suffix) for name in names):
            raise RuntimeError(f"sdist is missing {suffix}")
    forbidden = ("/__pycache__/", "/.venv/", "/build/", "/dist/", ".whl", ".so", ".pyd")
    offenders = [name for name in names if any(marker in name for marker in forbidden)]
    if offenders:
        raise RuntimeError(f"sdist includes generated output: {offenders[:5]}")


def inspect_wheel(wheel: Path) -> None:
    from packaging.utils import parse_wheel_filename

    _name, _version, _build, tags = parse_wheel_filename(wheel.name)
    if not tags:
        raise RuntimeError("wheel has no generated Python/ABI/platform tags")
    if any(tag.abi == "abi3" for tag in tags):
        raise RuntimeError("the chapter must not claim or retag abi3")
    with zipfile.ZipFile(wheel) as package:
        names = package.namelist()
    for suffix in ("faststats_cpp/__init__.py", "faststats_cpp/_native.pyi", "faststats_cpp/py.typed"):
        if not any(name.endswith(suffix) for name in names):
            raise RuntimeError(f"wheel is missing {suffix}")
    native = [
        name
        for name in names
        if "faststats_cpp/_native" in name and name.endswith((".so", ".pyd", ".dylib"))
    ]
    if len(native) != 1:
        raise RuntimeError(f"wheel must contain one private native module, found {native}")
    if any("_faststats_test" in name for name in names):
        raise RuntimeError("test-only rendezvous leaked into the wheel")
    print("wheel tags:", ", ".join(str(tag) for tag in sorted(tags, key=str)))


def audit_native_dependencies(environment_python: Path, cwd: Path, env: dict[str, str]) -> None:
    command = [
        environment_python,
        "-c",
        "import faststats_cpp._native as n; print(n.__file__)",
    ]
    native_path = Path(run(command, cwd=cwd, env=env, capture=True).stdout.strip())
    if sys.platform.startswith("linux") and shutil.which("ldd"):
        result = run(["ldd", native_path], cwd=cwd, env=env, capture=True)
        dependency_output = result.stdout + result.stderr
        if "not found" in dependency_output.lower():
            raise RuntimeError(
                "native dependency audit found an unresolved shared library:\n"
                + dependency_output
            )
        print(dependency_output, end="")
    elif sys.platform == "darwin" and shutil.which("otool"):
        result = run(["otool", "-L", native_path], cwd=cwd, env=env, capture=True)
        if not result.stdout.strip():
            raise RuntimeError("otool returned no dependency evidence")
        print(result.stdout, end="")
    elif os.name == "nt" and shutil.which("dumpbin"):
        result = run(
            ["dumpbin", "/DEPENDENTS", native_path], cwd=cwd, env=env, capture=True
        )
        if not result.stdout.strip():
            raise RuntimeError("dumpbin returned no dependency evidence")
        print(result.stdout, end="")
    else:
        print("shared-library dependency audit skipped: no supported local inspector")
    print(f"compiler/C++ ABI audit is separate from wheel tags; host={platform.platform()}")


def main() -> int:
    bootstrap_if_needed()
    python = Path(os.environ["COURSE_CPP_VERIFY_PYTHON"])
    environment = python.parent.parent
    env = environment_with(environment)

    with tempfile.TemporaryDirectory(prefix="faststats-artifacts-") as directory:
        temporary = Path(directory)
        sdist_out = temporary / "sdist"
        sdist_out.mkdir()
        run(
            [python, "-m", "build", "--sdist", "--outdir", sdist_out, PROJECT],
            cwd=temporary,
            env=env,
            timeout=600,
        )
        sdist = next(sdist_out.glob("*.tar.gz"))
        inspect_sdist(sdist)
        unpacked = safe_extract(sdist, temporary / "unpacked")

        wheelhouse = temporary / "wheelhouse"
        wheelhouse.mkdir()
        run(
            [python, "-m", "build", "--wheel", "--outdir", wheelhouse, unpacked],
            cwd=temporary,
            env=env,
            timeout=600,
        )
        wheel = next(wheelhouse.glob("*.whl"))
        inspect_wheel(wheel)

        clean = temporary / "clean-venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(clean)
        clean_python = executable(clean, "python")
        clean_env = environment_with(clean)
        run(
            [clean_python, "-m", "pip", "install", "pip==25.3", "mypy==1.18.2", wheel],
            cwd=temporary,
            env=clean_env,
            timeout=600,
        )
        run([clean_python, "-m", "pip", "check"], cwd=temporary, env=clean_env)
        run(
            [
                clean_python,
                "-c",
                "import faststats_cpp; assert faststats_cpp.summarize([1, 2, 3]).mean == 2; import faststats_cpp._native as n; assert not hasattr(n, 'summarize_after_rendezvous')",
            ],
            cwd=temporary,
            env=clean_env,
        )
        run(
            [
                clean_python,
                "-m",
                "mypy.stubtest",
                "faststats_cpp",
                "--allowlist",
                PROJECT / "stubtest.allowlist",
            ],
            cwd=temporary,
            env=clean_env,
        )
        run(
            [clean_python, "-m", "mypy", "--strict", PROJECT / "tests" / "typing_consumer.py"],
            cwd=temporary,
            env=clean_env,
        )
        rejected = subprocess.run(
            [
                str(clean_python),
                "-m",
                "mypy",
                "--strict",
                str(PROJECT / "tests" / "typing_rejections.py"),
            ],
            cwd=temporary,
            env=clean_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
            check=False,
        )
        normalized_rejections = rejected.stdout.replace("\\", "/")
        expected_rejection_lines = (11, 15, 19)
        missing_rejections = [
            line_number
            for line_number in expected_rejection_lines
            if (
                f"tests/typing_rejections.py:{line_number}: error:"
                not in normalized_rejections
            )
        ]
        if (
            rejected.returncode == 0
            or missing_rejections
            or normalized_rejections.count(": error:") != len(expected_rejection_lines)
        ):
            raise RuntimeError(
                "typing rejection probe did not emit exactly one diagnostic at "
                "each native-only constructor "
                f"(missing lines: {missing_rejections}):\n{rejected.stdout}"
            )
        audit_native_dependencies(clean_python, temporary, clean_env)
    print("sdist -> rebuilt wheel -> clean install verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
