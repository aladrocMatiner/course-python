from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

CHAPTER = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CHAPTER / "tools"))

from _support import create_dev_environment, environment_with, executable, run  # noqa: E402


def bootstrap_if_needed() -> None:
    if os.environ.get("COURSE_CPP_VERIFY_PYTHON"):
        return
    temporary = tempfile.TemporaryDirectory(prefix="faststats-bootstrap-")
    environment = Path(temporary.name) / "dev-venv"
    python = create_dev_environment(environment)
    env = environment_with(environment, COURSE_CPP_VERIFY_PYTHON=str(python))
    result = subprocess.run(
        [str(python), str(Path(__file__).resolve()), *sys.argv[1:]], env=env, check=False
    )
    temporary.cleanup()
    raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=("debug", "release", "sanitized"), required=True)
    args = parser.parse_args()
    bootstrap_if_needed()

    python = Path(os.environ["COURSE_CPP_VERIFY_PYTHON"])
    environment = python.parent.parent
    env = environment_with(environment)
    build_type = "Debug" if args.profile in ("debug", "sanitized") else "Release"

    with tempfile.TemporaryDirectory(prefix=f"faststats-{args.profile}-") as directory:
        temporary = Path(directory)
        build = temporary / "cmake-build"
        pybind_dir = run(
            [python, "-m", "pybind11", "--cmakedir"],
            cwd=temporary,
            env=env,
            capture=True,
        ).stdout.strip()
        configure = [
            "cmake",
            "-S",
            PROJECT,
            "-B",
            build,
            f"-DCMAKE_BUILD_TYPE={build_type}",
            f"-Dpybind11_DIR={pybind_dir}",
        ]
        if args.profile == "sanitized":
            configure.append("-DFASTSTATS_ENABLE_SANITIZERS=ON")
        else:
            configure.append("-DFASTSTATS_BUILD_TEST_EXTENSION=ON")
        run(configure, cwd=temporary, env=env)

        if args.profile == "sanitized":
            status_path = build / "faststats-sanitizer-status.txt"
            if not status_path.is_file():
                raise RuntimeError("CMake did not emit sanitizer capability evidence")
            sanitizer_status = status_path.read_text(encoding="utf-8").strip()
            if sanitizer_status.startswith("unsupported:"):
                compiler = sanitizer_status.partition(":")[2] or "unknown"
                print(
                    "sanitizer audit skipped: "
                    f"compiler {compiler} does not satisfy the GCC/Clang contract"
                )
                return 0
            if not sanitizer_status.startswith("enabled:"):
                raise RuntimeError(
                    f"sanitizers were requested but not enabled: {sanitizer_status!r}"
                )
            run(
                ["cmake", "--build", build, "--config", build_type, "--target", "faststats_core_tests"],
                cwd=temporary,
                env=env,
            )
            sanitizer_env = env | {
                "ASAN_OPTIONS": "detect_leaks=1:halt_on_error=1",
                "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1",
            }
            # Desktop launchers sometimes preload UI shims before libasan. The
            # autonomous test needs the sanitizer runtime first, so do not
            # inherit an unrelated preload into this bounded subprocess.
            sanitizer_env.pop("LD_PRELOAD", None)
            run(
                ["ctest", "--test-dir", build, "--output-on-failure", "-C", build_type],
                cwd=temporary,
                env=sanitizer_env,
            )
            compiler = sanitizer_status.partition(":")[2]
            print(
                "sanitizer audit passed on the autonomous core; "
                f"CMake confirmed enabled:{compiler}"
            )
            return 0

        run(["cmake", "--build", build, "--config", build_type], cwd=temporary, env=env)
        run(
            ["ctest", "--test-dir", build, "--output-on-failure", "-C", build_type],
            cwd=temporary,
            env=env,
        )

        wheelhouse = temporary / "wheelhouse"
        wheelhouse.mkdir()
        run(
            [
                python,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                wheelhouse,
                "--config-setting",
                f"cmake.build-type={build_type}",
                PROJECT,
            ],
            cwd=temporary,
            env=env,
            timeout=600,
        )
        wheel = next(wheelhouse.glob("*.whl"))
        run(
            [python, "-m", "pip", "install", "--force-reinstall", "--no-deps", wheel],
            cwd=temporary,
            env=env,
        )
        test_module_paths = [str(build), str(build / build_type)]
        pytest_env = env | {"PYTHONPATH": os.pathsep.join(test_module_paths)}
        run(
            [python, "-m", "pytest", PROJECT / "tests"],
            cwd=temporary,
            env=pytest_env,
            timeout=600,
        )
    print(f"faststats native {args.profile} verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
