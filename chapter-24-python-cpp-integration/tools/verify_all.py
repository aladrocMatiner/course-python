from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

from _support import CHAPTER, create_dev_environment, environment_with, executable, run


def verify_survival(environment: Path, temporary: Path) -> None:
    source = CHAPTER / "examples" / "00-cpp-survival"
    build = temporary / "survival-build"
    env = environment_with(environment)
    run(["cmake", "-S", source, "-B", build, "-DCMAKE_BUILD_TYPE=Debug"], cwd=temporary, env=env)
    run(["cmake", "--build", build, "--config", "Debug"], cwd=temporary, env=env)
    run(["ctest", "--test-dir", build, "--output-on-failure", "-C", "Debug"], cwd=temporary, env=env)
    binary = build / ("Debug/cpp_survival.exe" if os.name == "nt" else "cpp_survival")
    result = run([binary], cwd=temporary, env=env, capture=True)
    if "mean=8" not in result.stdout:
        raise RuntimeError(f"unexpected survival output: {result.stdout!r}")


def verify_first_extension(environment: Path, temporary: Path) -> None:
    source = CHAPTER / "examples" / "01-first-extension"
    wheelhouse = temporary / "first-wheelhouse"
    wheelhouse.mkdir()
    env = environment_with(environment)
    python = executable(environment, "python")
    run([python, "-m", "build", "--wheel", "--outdir", wheelhouse, source], cwd=temporary, env=env, timeout=600)
    wheel = next(wheelhouse.glob("*.whl"))
    run([python, "-m", "pip", "install", "--force-reinstall", "--no-deps", wheel], cwd=temporary, env=env)
    run([python, "-m", "pytest", source / "tests"], cwd=temporary, env=env)


def verify_embedding(environment: Path, temporary: Path) -> None:
    source = CHAPTER / "examples" / "embed-python"
    build = temporary / "embed-build"
    env = environment_with(environment)
    python = executable(environment, "python")
    pybind_dir = run(
        [python, "-m", "pybind11", "--cmakedir"], cwd=temporary, env=env, capture=True
    ).stdout.strip()
    run(
        ["cmake", "-S", source, "-B", build, f"-Dpybind11_DIR={pybind_dir}", "-DCMAKE_BUILD_TYPE=Release"],
        cwd=temporary,
        env=env,
    )
    run(["cmake", "--build", build, "--config", "Release"], cwd=temporary, env=env)
    binary = build / ("Release/embed_strategy.exe" if os.name == "nt" else "embed_strategy")
    decoy = temporary / "foreign-cwd"
    decoy.mkdir()
    (decoy / "trusted_strategy.py").write_text(
        "raise RuntimeError('the current working directory must not win')\n", encoding="utf-8"
    )
    strategies = source / "strategies"
    good = run([binary, "--strategy-dir", strategies / "good"], cwd=decoy, env=env, capture=True)
    if good.stdout.strip() != "score=6":
        raise RuntimeError(f"trusted strategy returned unexpected output: {good.stdout!r}")
    for name, expected_code in (("raises", 3), ("invalid", 4), ("missing", 2)):
        result = subprocess.run(
            [str(binary), "--strategy-dir", str(strategies / name)],
            cwd=decoy,
            env=env,
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode != expected_code:
            raise RuntimeError(
                f"embedding {name} returned {result.returncode}, expected {expected_code}: {result.stderr}"
            )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="course-cpp-") as directory:
        temporary = Path(directory)
        requested_python = os.environ.get("COURSE_CPP_VERIFY_PYTHON")
        if requested_python:
            python = Path(requested_python)
            environment = python.parent.parent
        else:
            environment = temporary / "dev-venv"
            python = create_dev_environment(environment)
        env = environment_with(environment, COURSE_CPP_VERIFY_PYTHON=str(python))
        run([python, CHAPTER / "tools" / "preflight.py"], cwd=temporary, env=env)
        verify_survival(environment, temporary)
        verify_first_extension(environment, temporary)
        native = CHAPTER / "examples" / "faststats-cpp" / "tools" / "verify_native.py"
        run([python, native, "--profile", "debug"], cwd=temporary, env=env, timeout=900)
        run([python, native, "--profile", "release"], cwd=temporary, env=env, timeout=900)
        run([python, native, "--profile", "sanitized"], cwd=temporary, env=env, timeout=900)
        artifacts = CHAPTER / "examples" / "faststats-cpp" / "tools" / "verify_artifacts.py"
        run([python, artifacts], cwd=temporary, env=env, timeout=1200)
        verify_embedding(environment, temporary)
    print(
        "chapter 24 native verification completed; individual capability checks "
        "report passed or an explicit supported skip, and all generated outputs "
        "used temporary paths"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
