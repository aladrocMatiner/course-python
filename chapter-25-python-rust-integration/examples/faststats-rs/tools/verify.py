#!/usr/bin/env python3
"""End-to-end verification for the chapter 25 mixed package.

All build targets, wheels, virtual environments, caches, and working directories
live below one temporary directory outside the source tree.
"""

from __future__ import annotations

import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
CHAPTER = PROJECT.parents[1]
SURVIVAL = CHAPTER / "examples" / "00-rust-survival"
FIRST = CHAPTER / "examples" / "01-first-extension"
RUST = "1.97.0"


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: int = 600,
    expect_success: bool = True,
) -> subprocess.CompletedProcess[str]:
    print(f"+ ({cwd}) {' '.join(command)}", flush=True)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    if bool(completed.returncode == 0) != expect_success:
        print(completed.stdout)
        expected = "success" if expect_success else "failure"
        raise RuntimeError(f"command did not produce expected {expected}: {command}")
    if completed.stdout.strip():
        print(completed.stdout.rstrip())
    return completed


def python_in(venv_dir: Path) -> Path:
    folder = "Scripts" if os.name == "nt" else "bin"
    executable = "python.exe" if os.name == "nt" else "python"
    return venv_dir / folder / executable


def make_venv(path: Path, env: dict[str, str]) -> Path:
    venv.EnvBuilder(with_pip=True, clear=True).create(path)
    python = python_in(path)
    run([str(python), "-m", "pip", "--version"], cwd=path, env=env, timeout=120)
    return python


def find_one(folder: Path, pattern: str) -> Path:
    matches = sorted(folder.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected one {pattern} below {folder}, found {matches}")
    return matches[0]


def safe_extract(archive: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:gz") as package:
        for member in package.getmembers():
            target = (destination / member.name).resolve()
            if destination.resolve() not in (target, *target.parents):
                raise RuntimeError(f"unsafe sdist member: {member.name}")
        package.extractall(destination, filter="data")
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise RuntimeError(f"expected one unpacked sdist root, found {roots}")
    return roots[0]


def inspect_sdist(archive: Path) -> None:
    required_suffixes = {
        "Cargo.toml",
        "Cargo.lock",
        "LICENSE",
        "README.md",
        "pyproject.toml",
        "requirements-dev.lock",
        "rust-toolchain.toml",
        "src/domain.rs",
        "src/lib.rs",
        "python/faststats_rs/__init__.py",
        "python/faststats_rs/__init__.pyi",
        "python/faststats_rs/_native.pyi",
        "python/faststats_rs/py.typed",
    }
    with tarfile.open(archive, "r:gz") as package:
        names = {member.name for member in package.getmembers()}
    for suffix in required_suffixes:
        if not any(name.endswith(suffix) for name in names):
            raise RuntimeError(f"sdist is missing {suffix}")
    forbidden = ("src/test_hooks.rs", "/target/", "__pycache__", ".pytest_cache", ".mypy_cache")
    for name in names:
        if any(marker in name for marker in forbidden):
            raise RuntimeError(f"sdist contains forbidden test/build content: {name}")


def inspect_wheel(wheel: Path, *, abi3: bool) -> None:
    with zipfile.ZipFile(wheel) as package:
        names = package.namelist()
        payloads = {
            name: package.read(name)
            for name in names
            if name.endswith((".so", ".pyd", ".dll", ".dylib"))
        }
    required = ("faststats_rs/__init__.py", "faststats_rs/__init__.pyi", "faststats_rs/_native.pyi", "faststats_rs/py.typed")
    for suffix in required:
        if not any(name.endswith(suffix) for name in names):
            raise RuntimeError(f"wheel is missing {suffix}")
    if not payloads:
        raise RuntimeError("wheel does not contain a native extension")
    if any(b"summarize_with_rendezvous" in payload for payload in payloads.values()):
        raise RuntimeError("release wheel exposes test rendezvous symbol")
    filename = wheel.name
    if abi3 and not re.search(r"-cp311-abi3-", filename):
        raise RuntimeError(f"expected cp311-abi3 tag, got {filename}")
    if not abi3 and "-abi3-" in filename:
        raise RuntimeError(f"version-specific wheel unexpectedly has abi3 tag: {filename}")


def install_and_smoke(
    wheel: Path,
    venv_dir: Path,
    work_dir: Path,
    env: dict[str, str],
    *,
    typing: bool,
) -> None:
    work_dir.mkdir(parents=True, exist_ok=True)
    python = make_venv(venv_dir, env)
    if typing:
        run(
            [str(python), "-m", "pip", "install", "-r", str(PROJECT / "requirements-dev.lock")],
            cwd=work_dir,
            env=env,
            timeout=600,
        )
    run(
        [str(python), "-m", "pip", "install", "--no-deps", str(wheel)],
        cwd=work_dir,
        env=env,
        timeout=300,
    )
    run([str(python), "-m", "pip", "check"], cwd=work_dir, env=env, timeout=120)
    smoke = (
        "import faststats_rs; "
        "s=faststats_rs.summarize([1,2,3], threshold=1); "
        "assert (s.count,s.mean)==(3,2.0); "
        "assert 'chapter-25-python-rust-integration' not in str(faststats_rs.__file__)"
    )
    run([str(python), "-I", "-B", "-c", smoke], cwd=work_dir, env=env, timeout=120)
    if typing:
        run(
            [str(python), "-m", "mypy.stubtest", "faststats_rs"],
            cwd=work_dir,
            env=env,
            timeout=180,
        )
        run(
            [str(python), "-m", "mypy", "--strict", str(PROJECT / "tests" / "typing_consumer.py")],
            cwd=work_dir,
            env=env,
            timeout=180,
        )


def assert_clean_source_tree() -> None:
    forbidden_names = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".venv",
        "target",
        "dist",
    }
    forbidden_suffixes = (".whl", ".tar.gz", ".so", ".pyd", ".dll", ".dylib", ".pyc")
    offenders: list[str] = []
    for path in CHAPTER.rglob("*"):
        relative = path.relative_to(CHAPTER).as_posix()
        if path.name in forbidden_names or (path.is_file() and path.name.endswith(forbidden_suffixes)):
            offenders.append(relative)
    if offenders:
        raise RuntimeError(f"generated artifacts remain in chapter tree: {offenders}")


def main() -> int:
    if sys.version_info < (3, 11):
        raise RuntimeError("CPython 3.11 or later is required")
    print(
        f"validation host: {platform.system()} {platform.machine()}, "
        f"Python {platform.python_version()}, pinned Rust {RUST}"
    )
    with tempfile.TemporaryDirectory(prefix="faststats-rs-verify-") as temporary:
        temp = Path(temporary)
        env = os.environ.copy()
        env.update(
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONNOUSERSITE="1",
            PIP_DISABLE_PIP_VERSION_CHECK="1",
            CARGO_TERM_COLOR="never",
        )
        cargo = ["rustup", "run", RUST, "cargo"]
        rustc = ["rustup", "run", RUST, "rustc"]

        for name, project in (("survival", SURVIVAL), ("first", FIRST), ("capstone", PROJECT)):
            project_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / name)}
            run(cargo + ["fmt", "--all", "--", "--check"], cwd=project, env=project_env)
            run(
                cargo + ["clippy", "--all-targets", "--locked", "--", "-D", "warnings"],
                cwd=project,
                env=project_env,
                timeout=600,
            )
            run(cargo + ["test", "--locked"], cwd=project, env=project_env, timeout=600)

        hooks_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "hooks-check")}
        run(
            cargo + ["clippy", "--all-targets", "--locked", "--features", "test-hooks", "--", "-D", "warnings"],
            cwd=PROJECT,
            env=hooks_env,
            timeout=600,
        )

        (temp / "expected-error").mkdir()
        expected_error = run(
            rustc
            + [
                "--edition",
                "2024",
                str(SURVIVAL / "lessons" / "ownership_move_error.rs"),
                "--out-dir",
                str(temp / "expected-error"),
            ],
            cwd=temp,
            env=env,
            expect_success=False,
        )
        if "borrow of moved value" not in expected_error.stdout:
            raise RuntimeError("ownership expected-error no longer demonstrates a move")
        (temp / "ownership-solution").mkdir()
        run(
            rustc
            + [
                "--edition",
                "2024",
                str(SURVIVAL / "lessons" / "ownership_borrow_solution.rs"),
                "--out-dir",
                str(temp / "ownership-solution"),
            ],
            cwd=temp,
            env=env,
        )

        tools_venv = temp / "tools-venv"
        tools_python = make_venv(tools_venv, env)
        run(
            [str(tools_python), "-m", "pip", "install", "-r", str(PROJECT / "requirements-dev.lock")],
            cwd=temp,
            env=env,
            timeout=600,
        )
        run(
            [str(tools_python), str(CHAPTER / "tools" / "preflight.py"), "--require-venv"],
            cwd=temp,
            env=env,
        )
        maturin = [str(tools_python), "-m", "maturin"]

        first_develop = temp / "first-develop-source"
        shutil.copytree(FIRST, first_develop)
        first_develop_env = env | {
            "CARGO_TARGET_DIR": str(temp / "targets" / "first-develop"),
            "VIRTUAL_ENV": str(tools_venv),
        }
        run(
            maturin + ["develop", "--release", "--locked"],
            cwd=first_develop,
            env=first_develop_env,
            timeout=600,
        )
        run(
            [
                str(tools_python),
                "-I",
                "-B",
                "-c",
                "import first_pyo3_extension as m; assert m.double(21) == 42",
            ],
            cwd=temp,
            env=env,
        )

        first_out = temp / "first-wheel"
        first_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "first-wheel")}
        run(
            maturin + ["build", "--release", "--locked", "--out", str(first_out)],
            cwd=FIRST,
            env=first_env,
            timeout=600,
        )
        first_wheel = find_one(first_out, "*.whl")
        run(
            [str(tools_python), "-m", "pip", "install", "--force-reinstall", "--no-deps", str(first_wheel)],
            cwd=temp,
            env=env,
        )
        run(
            [str(tools_python), "-m", "pytest", "-p", "no:cacheprovider", "-q", str(FIRST / "tests")],
            cwd=temp,
            env=env,
            timeout=180,
        )

        hooks_out = temp / "hooks-wheel"
        hooks_build_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "hooks-wheel")}
        run(
            maturin
            + [
                "build",
                "--release",
                "--locked",
                "--features",
                "test-hooks",
                "--out",
                str(hooks_out),
            ],
            cwd=PROJECT,
            env=hooks_build_env,
            timeout=600,
        )
        hooks_wheel = find_one(hooks_out, "*.whl")
        run(
            [str(tools_python), "-m", "pip", "install", "--force-reinstall", "--no-deps", str(hooks_wheel)],
            cwd=temp,
            env=env,
        )
        run(
            [
                str(tools_python),
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-q",
                str(PROJECT / "tests" / "test_threads.py"),
            ],
            cwd=temp,
            env=env | {"FASTSTATS_REQUIRE_TEST_HOOKS": "1"},
            timeout=180,
        )

        sdist_out = temp / "sdist"
        sdist_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "sdist")}
        run(
            maturin + ["sdist", "--out", str(sdist_out)],
            cwd=PROJECT,
            env=sdist_env,
            timeout=600,
        )
        sdist = find_one(sdist_out, "*.tar.gz")
        inspect_sdist(sdist)
        unpacked = safe_extract(sdist, temp / "unpacked")

        develop_env = env | {
            "CARGO_TARGET_DIR": str(temp / "targets" / "capstone-develop"),
            "VIRTUAL_ENV": str(tools_venv),
        }
        run(
            maturin + ["develop", "--release", "--locked"],
            cwd=unpacked,
            env=develop_env,
            timeout=600,
        )
        run(
            [
                str(tools_python),
                "-I",
                "-B",
                "-c",
                "import faststats_rs; assert faststats_rs.summarize([1], threshold=0).count == 1",
            ],
            cwd=temp,
            env=env,
        )

        version_out = temp / "version-wheel"
        version_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "version-wheel")}
        run(
            maturin
            + [
                "build",
                "--release",
                "--locked",
                "--interpreter",
                str(tools_python),
                "--out",
                str(version_out),
            ],
            cwd=unpacked,
            env=version_env,
            timeout=600,
        )
        version_wheel = find_one(version_out, "*.whl")
        inspect_wheel(version_wheel, abi3=False)
        install_and_smoke(
            version_wheel,
            temp / "version-install",
            temp / "external-version-cwd",
            env,
            typing=True,
        )

        run(
            [str(tools_python), "-m", "pip", "install", "--force-reinstall", "--no-deps", str(version_wheel)],
            cwd=temp,
            env=env,
        )
        run(
            [str(tools_python), "-m", "pytest", "-p", "no:cacheprovider", "-q", str(PROJECT / "tests")],
            cwd=temp,
            env=env,
            timeout=300,
        )
        run(
            [str(tools_python), str(PROJECT / "benchmarks" / "benchmark.py"), "--smoke"],
            cwd=temp,
            env=env,
            timeout=180,
        )

        abi3_out = temp / "abi3-wheel"
        abi3_env = env | {"CARGO_TARGET_DIR": str(temp / "targets" / "abi3-wheel")}
        run(
            maturin
            + [
                "build",
                "--release",
                "--locked",
                "--features",
                "abi3-py311",
                "--interpreter",
                str(tools_python),
                "--out",
                str(abi3_out),
            ],
            cwd=unpacked,
            env=abi3_env,
            timeout=600,
        )
        abi3_wheel = find_one(abi3_out, "*.whl")
        inspect_wheel(abi3_wheel, abi3=True)
        install_and_smoke(
            abi3_wheel,
            temp / "abi3-install",
            temp / "external-abi3-cwd",
            env,
            typing=False,
        )

        print(f"verified version-specific wheel: {version_wheel.name}")
        print(f"verified stable-ABI wheel: {abi3_wheel.name}")

    assert_clean_source_tree()
    print("faststats-rs verification passed without source-tree artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
