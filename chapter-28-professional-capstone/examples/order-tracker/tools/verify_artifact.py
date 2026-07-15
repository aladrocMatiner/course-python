"""Build and verify course-order-tracker without implicit acquisition.

The verifier requires an already provisioned ``build`` frontend and an
offline wheelhouse named by ``ORDER_TRACKER_WHEELHOUSE``.  It never uploads,
publishes, signs, attests, or contacts an index.
"""

from __future__ import annotations

import base64
import csv
import email.parser
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import tomllib
import venv
import zipfile
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Final, Iterable

PROJECT: Final = Path(__file__).resolve().parents[1]
EXPECTED_BUILD_FRONTEND: Final = "1.3.0"
EXPECTED_BACKEND: Final = "80.9.0"
EXPECTED_WHEEL_TOOL: Final = "0.45.1"
EXPECTED_WHEELHOUSE_INPUTS: Final = {
    "setuptools": (
        EXPECTED_BACKEND,
        "setuptools-80.9.0-py3-none-any.whl",
        "062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922",
    ),
    "wheel": (
        EXPECTED_WHEEL_TOOL,
        "wheel-0.45.1-py3-none-any.whl",
        "708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248",
    ),
}
MAX_CAPTURE: Final = 16_384
BUILD_TIMEOUT_SECONDS: Final = 180
COMMAND_TIMEOUT_SECONDS: Final = 30
MAX_MEMBER_BYTES: Final = 2 * 1024 * 1024
MAX_PROJECT_BYTES: Final = 8 * 1024 * 1024
MAX_ARCHIVE_BYTES: Final = 12 * 1024 * 1024

FORBIDDEN_PARTS: Final = {
    ".env",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
}
FORBIDDEN_NAMES: Final = {
    ".coverage",
    "coverage.xml",
    "credentials.json",
    "junit.xml",
    "report.json",
    "secrets.json",
}
FORBIDDEN_SUFFIXES: Final = {
    ".db",
    ".dll",
    ".dylib",
    ".exe",
    ".key",
    ".log",
    ".p12",
    ".pem",
    ".pfx",
    ".pyc",
    ".pyo",
    ".so",
    ".sqlite",
    ".sqlite3",
    ".whl",
    ".zip",
}


class PrerequisiteMissing(RuntimeError):
    """An explicitly provisioned build input is absent."""


class VerificationFailure(RuntimeError):
    """One named verification phase failed."""


@dataclass(frozen=True)
class Evidence:
    sdist: Path
    initial_wheel: Path
    rebuilt_wheel: Path
    pip_version: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            result[path.relative_to(root).as_posix()] = "symlink:" + os.readlink(path)
        elif path.is_file():
            result[path.relative_to(root).as_posix()] = sha256(path)
    return result


def _safe_relative(name: str) -> PurePosixPath:
    if "\\" in name:
        raise VerificationFailure("archive member paths must use POSIX separators")
    candidate = PurePosixPath(name)
    if candidate.is_absolute() or not candidate.parts or ".." in candidate.parts:
        raise VerificationFailure("archive contains an unsafe member path")
    return candidate


def _is_forbidden(
    name: str,
    *,
    allow_archive_name: bool = False,
    allow_egg_info: bool = False,
) -> bool:
    path = _safe_relative(name)
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & FORBIDDEN_PARTS:
        return True
    if any(part.startswith(".env") for part in lowered_parts):
        return True
    if path.name.lower() in FORBIDDEN_NAMES or name.lower().endswith(".tar.gz"):
        return True
    suffix = path.suffix.lower()
    if suffix in FORBIDDEN_SUFFIXES and not (allow_archive_name and suffix == ".whl"):
        return True
    if any(part.lower().endswith(".egg-info") for part in path.parts):
        return not allow_egg_info
    return False


def scan_source_hygiene(root: Path) -> None:
    offenders: list[str] = []
    total_bytes = 0
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or _is_forbidden(relative):
            offenders.append(relative)
        elif path.is_file():
            size = path.stat().st_size
            total_bytes += size
            if size > MAX_MEMBER_BYTES:
                offenders.append(relative)
        if len(offenders) >= 10:
            break
    if offenders:
        raise VerificationFailure("source hygiene rejected: " + ", ".join(offenders))
    if total_bytes > MAX_PROJECT_BYTES:
        raise VerificationFailure("source hygiene rejected an oversized project snapshot")


def wheel_metadata(path: Path) -> tuple[str, str]:
    with zipfile.ZipFile(path) as archive:
        metadata_members = [
            name
            for name in archive.namelist()
            if len(PurePosixPath(name).parts) == 2
            and PurePosixPath(name).parts[0].endswith(".dist-info")
            and PurePosixPath(name).parts[1] == "METADATA"
        ]
        if len(metadata_members) != 1:
            raise VerificationFailure(
                "wheel must contain exactly one top-level dist-info METADATA file"
            )
        parsed = email.parser.BytesParser().parsebytes(archive.read(metadata_members[0]))
    return parsed.get("Name", ""), parsed.get("Version", "")


def _inspect_project_metadata(parsed: object) -> None:
    get = getattr(parsed, "get")
    get_all = getattr(parsed, "get_all")
    if get("Name") != "course-order-tracker" or get("Version") != "1.0.0":
        raise VerificationFailure("artifact name/version metadata does not match the project")
    if get("Requires-Python") != ">=3.11":
        raise VerificationFailure("artifact Requires-Python metadata is not >=3.11")
    if get_all("Requires-Dist"):
        raise VerificationFailure("artifact unexpectedly declares runtime dependencies")
    if get("License-Expression") != "CC-BY-SA-4.0":
        raise VerificationFailure("artifact license expression is not CC-BY-SA-4.0")
    if "LICENSE" not in get_all("License-File", []):
        raise VerificationFailure("artifact metadata does not declare LICENSE")
    if get("Description-Content-Type") != "text/markdown":
        raise VerificationFailure("artifact readme metadata is not Markdown")
    payload = getattr(parsed, "get_payload")()
    if not isinstance(payload, str) or "# `course-order-tracker` companion project" not in payload:
        raise VerificationFailure("artifact metadata does not contain the declared readme")


def _inspect_entry_points(content: bytes) -> None:
    lines = [line.strip() for line in content.decode("utf-8").splitlines() if line.strip()]
    if lines != ["[console_scripts]", "order-tracker = order_tracker.cli:run"]:
        raise VerificationFailure("artifact console entry point does not match the project")


def _inspect_record(archive: zipfile.ZipFile, record_name: str) -> None:
    file_names = [name for name in archive.namelist() if not name.endswith("/")]
    rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
    if any(len(row) != 3 for row in rows):
        raise VerificationFailure("wheel RECORD contains a malformed row")
    recorded_names = [row[0] for row in rows]
    if len(recorded_names) != len(set(recorded_names)) or set(recorded_names) != set(file_names):
        raise VerificationFailure("wheel RECORD does not enumerate each member exactly once")
    for name, encoded_hash, encoded_size in rows:
        _safe_relative(name)
        if name == record_name:
            if encoded_hash or encoded_size:
                raise VerificationFailure("wheel RECORD self-entry must omit hash and size")
            continue
        content = archive.read(name)
        digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
        if encoded_hash != f"sha256={digest}" or encoded_size != str(len(content)):
            raise VerificationFailure("wheel RECORD hash or size does not match a member")


def require_prerequisites() -> Path:
    if sys.version_info < (3, 11):
        raise PrerequisiteMissing("CPython 3.11 or newer is required")
    if os.name != "posix":
        raise PrerequisiteMissing(
            "artifact-verifier child-process cleanup currently requires POSIX process groups"
        )
    try:
        build_version = importlib.metadata.version("build")
    except importlib.metadata.PackageNotFoundError as exc:
        raise PrerequisiteMissing(
            f"build=={EXPECTED_BUILD_FRONTEND} must already be installed"
        ) from exc
    if build_version != EXPECTED_BUILD_FRONTEND:
        raise PrerequisiteMissing(
            f"build=={EXPECTED_BUILD_FRONTEND} is required; found {build_version}"
        )
    configured = os.environ.get("ORDER_TRACKER_WHEELHOUSE")
    if not configured:
        raise PrerequisiteMissing(
            "ORDER_TRACKER_WHEELHOUSE must name an offline build-input directory"
        )
    wheelhouse = Path(configured).expanduser()
    if not wheelhouse.is_dir():
        raise PrerequisiteMissing("the configured offline wheelhouse is not a directory")

    expected_filenames = {details[1] for details in EXPECTED_WHEELHOUSE_INPUTS.values()}
    observed_wheels = [path for path in wheelhouse.glob("*.whl") if path.is_file()]
    unexpected = sorted(
        path.name for path in observed_wheels if path.name not in expected_filenames
    )
    if unexpected:
        displayed = unexpected[:10]
        remainder = f" (+{len(unexpected) - 10} more)" if len(unexpected) > 10 else ""
        raise PrerequisiteMissing(
            "offline wheelhouse contains unreviewed wheel inputs: "
            + ", ".join(displayed)
            + remainder
        )

    missing: list[str] = []
    mismatched: list[str] = []
    for name, (version, filename, digest) in EXPECTED_WHEELHOUSE_INPUTS.items():
        wheel = wheelhouse / filename
        if not wheel.is_file() or wheel.is_symlink():
            missing.append(f"{name}=={version}")
            continue
        try:
            observed_name, observed_version = wheel_metadata(wheel)
        except (OSError, zipfile.BadZipFile, VerificationFailure):
            mismatched.append(f"{name}=={version}")
            continue
        normalized = observed_name.lower().replace("_", "-")
        if normalized != name or observed_version != version or sha256(wheel) != digest:
            mismatched.append(f"{name}=={version}")
    if missing:
        raise PrerequisiteMissing(
            "offline wheelhouse is missing exact build inputs: " + ", ".join(missing)
        )
    if mismatched:
        raise PrerequisiteMissing(
            "offline wheelhouse inputs do not match recorded metadata/SHA-256: "
            + ", ".join(mismatched)
        )
    return wheelhouse.resolve()


def bounded_run(
    command: Iterable[os.PathLike[str] | str],
    *,
    phase: str,
    cwd: Path,
    environment: dict[str, str],
    timeout: float = COMMAND_TIMEOUT_SECONDS,
    expected: int = 0,
) -> subprocess.CompletedProcess[str]:
    arguments = [str(part) for part in command]
    try:
        process = subprocess.Popen(
            arguments,
            cwd=cwd,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
    except OSError as exc:
        raise VerificationFailure(f"{phase} could not start") from exc

    captured = {"stdout": bytearray(), "stderr": bytearray()}
    total = 0
    capture_lock = threading.Lock()
    overflow = threading.Event()

    def drain(stream: object, name: str) -> None:
        nonlocal total
        read = getattr(stream, "read")
        while chunk := read(4_096):
            with capture_lock:
                remaining = max(0, MAX_CAPTURE - total)
                captured[name].extend(chunk[:remaining])
                total += len(chunk[:remaining])
                if len(chunk) > remaining:
                    overflow.set()

    assert process.stdout is not None and process.stderr is not None
    readers = (
        threading.Thread(target=drain, args=(process.stdout, "stdout"), daemon=True),
        threading.Thread(target=drain, args=(process.stderr, "stderr"), daemon=True),
    )
    for reader in readers:
        reader.start()

    deadline = time.monotonic() + timeout
    timed_out = False
    while process.poll() is None:
        if overflow.is_set():
            break
        if time.monotonic() >= deadline:
            timed_out = True
            break
        time.sleep(0.01)

    def kill_process_group() -> None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    if process.poll() is None:
        kill_process_group()
    process.wait()
    for reader in readers:
        reader.join(timeout=0.2)
    if any(reader.is_alive() for reader in readers):
        kill_process_group()
        for reader in readers:
            reader.join(timeout=1)
    process.stdout.close()
    process.stderr.close()
    for reader in readers:
        reader.join(timeout=0.1)
    if any(reader.is_alive() for reader in readers):
        raise VerificationFailure(f"{phase} output readers did not terminate")

    stdout = bytes(captured["stdout"]).decode("utf-8", errors="replace")
    stderr = bytes(captured["stderr"]).decode("utf-8", errors="replace")
    result = subprocess.CompletedProcess(arguments, process.returncode, stdout, stderr)
    if timed_out:
        raise VerificationFailure(f"{phase} exceeded the {timeout}-second bound")
    if overflow.is_set():
        raise VerificationFailure(f"{phase} output exceeded the 16384-byte bound")
    if result.returncode != expected:
        raise VerificationFailure(
            f"{phase} exited {result.returncode}, expected {expected}"
        )
    return result


def isolated_environment(wheelhouse: Path, temporary_home: Path) -> dict[str, str]:
    allowed = {
        key: os.environ[key]
        for key in ("PATH", "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT")
        if key in os.environ
    }
    allowed.update(
        {
            "HOME": str(temporary_home),
            "PIP_CACHE_DIR": str(temporary_home / "pip-cache"),
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_FIND_LINKS": str(wheelhouse),
            "PIP_NO_INDEX": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "SOURCE_DATE_EPOCH": "1704067200",
            "TEMP": str(temporary_home / "tmp"),
            "TMP": str(temporary_home / "tmp"),
            "TMPDIR": str(temporary_home / "tmp"),
            "USERPROFILE": str(temporary_home),
        }
    )
    (temporary_home / "tmp").mkdir(parents=True)
    return allowed


def inspect_sdist(archive_path: Path) -> None:
    expected_root = "course_order_tracker-1.0.0"
    if archive_path.name != f"{expected_root}.tar.gz":
        raise VerificationFailure("sdist filename does not match the project")
    if archive_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise VerificationFailure("sdist exceeds the compressed-size bound")
    expected_files = {
        "BUILD_INPUTS.md",
        "LICENSE",
        "MANIFEST.in",
        "PKG-INFO",
        "README.md",
        "pyproject.toml",
        "requirements-build.txt",
        "src/course_order_tracker.egg-info/PKG-INFO",
        "src/course_order_tracker.egg-info/SOURCES.txt",
        "src/course_order_tracker.egg-info/dependency_links.txt",
        "src/course_order_tracker.egg-info/entry_points.txt",
        "src/course_order_tracker.egg-info/top_level.txt",
        "src/order_tracker/__init__.py",
        "src/order_tracker/__main__.py",
        "src/order_tracker/cli.py",
        "src/order_tracker/domain.py",
        "src/order_tracker/loopback.py",
        "src/order_tracker/repositories.py",
        "src/order_tracker/service.py",
    }
    optional_generated_files = {
        "setup.cfg",
        "src/course_order_tracker.egg-info/requires.txt",
    }
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise VerificationFailure("sdist contains duplicate member paths")
        observed_files: set[str] = set()
        total_size = 0
        for member in members:
            relative = _safe_relative(member.name)
            if not relative.parts or relative.parts[0] != expected_root:
                raise VerificationFailure("sdist member escaped the expected root directory")
            if member.issym() or member.islnk() or member.isdev():
                raise VerificationFailure("sdist contains a link or device member")
            if _is_forbidden(member.name, allow_egg_info=True):
                raise VerificationFailure("sdist contains forbidden generated material")
            if member.isfile():
                total_size += member.size
                if member.size > MAX_MEMBER_BYTES:
                    raise VerificationFailure("sdist member exceeds the size bound")
                if len(relative.parts) == 1:
                    raise VerificationFailure("sdist contains a file at its root marker")
                observed_files.add(PurePosixPath(*relative.parts[1:]).as_posix())
            elif not member.isdir():
                raise VerificationFailure("sdist contains a non-regular member")
        if total_size > MAX_ARCHIVE_BYTES:
            raise VerificationFailure("sdist expanded content exceeds the size bound")
        unexpected = observed_files - expected_files - optional_generated_files
        missing = expected_files - observed_files
        if unexpected:
            raise VerificationFailure(
                "sdist contains undeclared members: " + ", ".join(sorted(unexpected))
            )
        if missing:
            raise VerificationFailure(
                "sdist is missing required members: " + ", ".join(sorted(missing))
            )
        metadata = email.parser.BytesParser().parsebytes(
            archive.extractfile(f"{expected_root}/PKG-INFO").read()
        )
        _inspect_project_metadata(metadata)
        _inspect_entry_points(
            archive.extractfile(
                f"{expected_root}/src/course_order_tracker.egg-info/entry_points.txt"
            ).read()
        )


def extract_sdist(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True)
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            relative = _safe_relative(member.name)
            target = destination.joinpath(*relative.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise VerificationFailure("sdist contains a non-regular member")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise VerificationFailure("sdist member could not be read")
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
    roots = [path for path in destination.iterdir() if path.is_dir()]
    if len(roots) != 1:
        raise VerificationFailure("sdist must contain exactly one root directory")
    return roots[0]


def inspect_wheel(path: Path) -> None:
    if path.name != "course_order_tracker-1.0.0-py3-none-any.whl":
        raise VerificationFailure("wheel filename does not declare py3-none-any")
    if path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise VerificationFailure("wheel exceeds the compressed-size bound")
    package_files = {
        "order_tracker/__init__.py",
        "order_tracker/__main__.py",
        "order_tracker/cli.py",
        "order_tracker/domain.py",
        "order_tracker/loopback.py",
        "order_tracker/repositories.py",
        "order_tracker/service.py",
    }
    dist_info = "course_order_tracker-1.0.0.dist-info"
    metadata_files = {
        f"{dist_info}/METADATA",
        f"{dist_info}/WHEEL",
        f"{dist_info}/entry_points.txt",
        f"{dist_info}/licenses/LICENSE",
        f"{dist_info}/RECORD",
        f"{dist_info}/top_level.txt",
    }
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise VerificationFailure("wheel contains duplicate member paths")
        for name in names:
            _safe_relative(name)
            if _is_forbidden(name, allow_archive_name=True):
                raise VerificationFailure("wheel contains forbidden generated material")
        members = archive.infolist()
        if any(member.file_size > MAX_MEMBER_BYTES for member in members):
            raise VerificationFailure("wheel member exceeds the size bound")
        if sum(member.file_size for member in members) > MAX_ARCHIVE_BYTES:
            raise VerificationFailure("wheel expanded content exceeds the size bound")
        file_names = {name for name in names if not name.endswith("/")}
        expected_files = package_files | metadata_files
        missing = expected_files - file_names
        unexpected = file_names - expected_files
        if missing:
            raise VerificationFailure("wheel is missing members: " + ", ".join(sorted(missing)))
        if unexpected:
            raise VerificationFailure(
                "wheel contains undeclared members: " + ", ".join(sorted(unexpected))
            )
        metadata = email.parser.BytesParser().parsebytes(
            archive.read(f"{dist_info}/METADATA")
        )
        wheel_text = archive.read(f"{dist_info}/WHEEL").decode("utf-8")
        _inspect_project_metadata(metadata)
        _inspect_entry_points(archive.read(f"{dist_info}/entry_points.txt"))
        if archive.read(f"{dist_info}/top_level.txt").decode("utf-8").strip() != "order_tracker":
            raise VerificationFailure("wheel top-level package metadata changed")
        if b"CC BY-SA 4.0" not in archive.read(f"{dist_info}/licenses/LICENSE"):
            raise VerificationFailure("wheel license file content changed")
        _inspect_record(archive, f"{dist_info}/RECORD")
    if "Root-Is-Purelib: true" not in wheel_text or "Tag: py3-none-any" not in wheel_text:
        raise VerificationFailure("wheel does not contain the pure py3-none-any declaration")


def one_artifact(directory: Path, pattern: str) -> Path:
    matches = sorted(directory.glob(pattern))
    if len(matches) != 1:
        raise VerificationFailure(f"expected one {pattern} artifact, found {len(matches)}")
    return matches[0]


def environment_python(environment: Path) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / "python.exe"
    return environment / "bin" / "python"


def environment_script(environment: Path, name: str) -> Path:
    if os.name == "nt":
        return environment / "Scripts" / f"{name}.exe"
    return environment / "bin" / name


def verify_installed(
    python: Path,
    command: Path,
    *,
    foreign: Path,
    environment: dict[str, str],
) -> str:
    import_probe = bounded_run(
        [
            python,
            "-I",
            "-B",
            "-c",
            (
                "import importlib.metadata as m,json,order_tracker,pathlib;"
                "print(json.dumps({'distribution':m.version('course-order-tracker'),"
                "'package':order_tracker.__version__,'file':order_tracker.__file__}))"
            ),
        ],
        phase="installed import metadata",
        cwd=foreign,
        environment=environment,
    )
    imported = json.loads(import_probe.stdout)
    if imported["distribution"] != "1.0.0" or imported["package"] != "1.0.0":
        raise VerificationFailure("installed distribution and package versions disagree")
    imported_path = Path(imported["file"]).resolve()
    if not imported_path.is_relative_to(python.parents[1].resolve()):
        raise VerificationFailure("installed import escaped the clean environment")
    if imported_path.is_relative_to(PROJECT.resolve()):
        raise VerificationFailure("installed import leaked from the source checkout")

    domain_script = """
from order_tracker import InMemoryOrderRepository, OrderService, OrderValidationError
s = OrderService(InMemoryOrderRepository())
assert s.create('ART-001', 'widget', 1).status == 'pending'
assert s.advance('ART-001').status == 'packed'
before = s.list_orders()
try:
    s.create('ART-BOOL', 'widget', True)
except OrderValidationError:
    pass
else:
    raise AssertionError('boolean quantity accepted')
assert s.list_orders() == before
assert s.create('I' * 32, 'x' * 80, 1000).quantity == 1000
print('domain-smoke: pass')
"""
    bounded_run(
        [python, "-I", "-B", "-c", domain_script],
        phase="installed domain smoke",
        cwd=foreign,
        environment=environment,
    )

    missing = bounded_run(
        [command, "list"],
        phase="installed CLI missing-configuration smoke",
        cwd=foreign,
        environment=environment,
        expected=2,
    )
    if "database path required" not in missing.stderr:
        raise VerificationFailure("installed CLI missing-config recovery is unstable")
    database = foreign / "artifact-smoke.sqlite3"
    added = bounded_run(
        [command, "--database", database, "add", "ART-CLI", "widget", "2"],
        phase="installed CLI add smoke",
        cwd=foreign,
        environment=environment,
    )
    if added.stdout != '{"order_id":"ART-CLI","status":"pending"}\n':
        raise VerificationFailure("installed CLI add output changed")
    duplicate = bounded_run(
        [command, "--database", database, "add", "ART-CLI", "other", "9"],
        phase="installed CLI duplicate smoke",
        cwd=foreign,
        environment=environment,
        expected=1,
    )
    if "error[duplicate-order]" not in duplicate.stderr or "Traceback" in duplicate.stderr:
        raise VerificationFailure("installed CLI duplicate recovery changed")
    listed = bounded_run(
        [command, "--database", database, "list"],
        phase="installed CLI list smoke",
        cwd=foreign,
        environment=environment,
    )
    if '"item":"widget"' not in listed.stdout or '"quantity":2' not in listed.stdout:
        raise VerificationFailure("installed CLI list output changed")
    pip_probe = bounded_run(
        [python, "-I", "-B", "-c", "import importlib.metadata as m; print(m.version('pip'))"],
        phase="installed pip metadata",
        cwd=foreign,
        environment=environment,
    )
    return pip_probe.stdout.strip()


def verify(wheelhouse: Path) -> Evidence:
    scan_source_hygiene(PROJECT)
    before = tree_digest(PROJECT)
    roots: list[Path] = []
    with ExitStack() as stack:
        def temporary_root(prefix: str) -> Path:
            return Path(stack.enter_context(tempfile.TemporaryDirectory(prefix=prefix)))

        source_root = temporary_root("order-source-")
        output_root = temporary_root("order-output-")
        unpack_root = temporary_root("order-unpack-")
        install_root = temporary_root("order-install-")
        foreign_root = temporary_root("order-foreign-")
        home_root = temporary_root("order-home-")
        roots.extend((source_root, output_root, unpack_root, install_root, foreign_root, home_root))

        snapshot = source_root / "course-order-tracker"
        shutil.copytree(PROJECT, snapshot)
        environment = isolated_environment(wheelhouse, home_root)

        initial = output_root / "initial"
        initial.mkdir()
        bounded_run(
            [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "build",
                "--sdist",
                "--wheel",
                "--outdir",
                initial,
                snapshot,
            ],
            phase="initial isolated sdist/wheel build",
            cwd=source_root,
            environment=environment,
            timeout=BUILD_TIMEOUT_SECONDS,
        )
        sdist = one_artifact(initial, "*.tar.gz")
        initial_wheel = one_artifact(initial, "*.whl")
        inspect_sdist(sdist)
        inspect_wheel(initial_wheel)

        unpacked = extract_sdist(sdist, unpack_root / "source")
        rebuilt_output = output_root / "rebuilt"
        rebuilt_output.mkdir()
        bounded_run(
            [
                sys.executable,
                "-I",
                "-B",
                "-m",
                "build",
                "--wheel",
                "--outdir",
                rebuilt_output,
                unpacked,
            ],
            phase="isolated wheel rebuild from sdist",
            cwd=unpack_root,
            environment=environment,
            timeout=BUILD_TIMEOUT_SECONDS,
        )
        rebuilt_wheel = one_artifact(rebuilt_output, "*.whl")
        inspect_wheel(rebuilt_wheel)

        clean_environment = install_root / "venv"
        venv.EnvBuilder(with_pip=True, clear=True).create(clean_environment)
        clean_python = environment_python(clean_environment)
        clean_command = environment_script(clean_environment, "order-tracker")
        install_environment = isolated_environment(wheelhouse, home_root / "install")
        bounded_run(
            [
                clean_python,
                "-I",
                "-B",
                "-m",
                "pip",
                "install",
                "--no-index",
                "--no-deps",
                rebuilt_wheel,
            ],
            phase="clean rebuilt-wheel install",
            cwd=foreign_root,
            environment=install_environment,
            timeout=BUILD_TIMEOUT_SECONDS,
        )
        bounded_run(
            [clean_python, "-I", "-B", "-m", "pip", "check"],
            phase="clean-environment pip check",
            cwd=foreign_root,
            environment=install_environment,
        )
        pip_version = verify_installed(
            clean_python,
            clean_command,
            foreign=foreign_root,
            environment=install_environment,
        )
        evidence = Evidence(
            sdist=Path(sdist.name),
            initial_wheel=Path(initial_wheel.name),
            rebuilt_wheel=Path(rebuilt_wheel.name),
            pip_version=pip_version,
        )
        digests = {
            "sdist": sha256(sdist),
            "initial_wheel": sha256(initial_wheel),
            "rebuilt_wheel": sha256(rebuilt_wheel),
        }

    leftovers = [path.name for path in roots if path.exists()]
    if leftovers:
        raise VerificationFailure("temporary-root cleanup failed")
    if tree_digest(PROJECT) != before:
        raise VerificationFailure("repository source changed during verification")
    print(
        "toolchain:",
        f"python={platform.python_implementation()} {platform.python_version()}",
        f"build={EXPECTED_BUILD_FRONTEND}",
        f"setuptools={EXPECTED_BACKEND}",
        f"wheel={EXPECTED_WHEEL_TOOL}",
        f"pip={evidence.pip_version}",
        f"host={sys.platform}",
    )
    print("artifacts:", json.dumps({"files": {
        "sdist": evidence.sdist.name,
        "initial_wheel": evidence.initial_wheel.name,
        "rebuilt_wheel": evidence.rebuilt_wheel.name,
    }, "sha256": digests}, sort_keys=True))
    print("artifact verification: pass (local build, no publication)")
    return evidence


def main() -> int:
    try:
        wheelhouse = require_prerequisites()
        verify(wheelhouse)
        return 0
    except PrerequisiteMissing as exc:
        print(f"prerequisite missing: {exc}", file=sys.stderr)
        return 3
    except (
        OSError,
        subprocess.SubprocessError,
        VerificationFailure,
        zipfile.BadZipFile,
        tarfile.TarError,
    ) as exc:
        message = str(exc).replace(str(PROJECT), "<project>")
        print(f"artifact verification failed: {message[:1000]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
