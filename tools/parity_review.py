#!/usr/bin/env python3
"""Build and validate the multilingual semantic-review inventory.

Counts and Markdown structure are triage signals only. A localized document can
reach ``accepted`` only after its twelve semantic dimensions and both human
review roles are recorded as passed against the current canonical digest.
"""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import errno
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

import validate_book


SCHEMA_VERSION = 1
INDEX_SCHEMA_VERSION = 2
LEAF_SCHEMA_VERSION = 1
MANIFEST = "tools/parity_manifest.json"
STORE_ROOT = "tools/parity"
SOURCE_STORE = "sources"
RECORD_STORE = "records"
EXPECTED_CANONICAL_SOURCES = 27
EXPECTED_LOCALIZED_RECORDS = EXPECTED_CANONICAL_SOURCES * 4
LOCALES = {
    "es": "README.es.md",
    "ca": "README.ca.md",
    "sv": "README.sv.md",
    "ar": "README.ar.md",
}
CONTRACT_DIMENSIONS = (
    "purpose_objectives_prerequisites",
    "concept_order_definitions",
    "context_prediction_observation",
    "examples_outputs_explanations",
    "guided_modification_hint_success",
    "happy_edge_error_recovery",
    "non_blameful_common_errors",
    "explained_solutions",
    "checkpoint_summary_reflection",
    "safety_compatibility_scope",
    "navigation_accessibility",
    "technical_contract_source_refs",
)
STATES = (
    "inventoried",
    "source-frozen",
    "drafted",
    "automated-signals-pass",
    "linguistic-reviewed",
    "technical-reviewed",
    "accepted",
    "stale",
    "blocked",
)
REVIEW_RESULTS = {"pending", "approved", "changes-requested"}
CONTRACT_RESULTS = {"pending", "pass", "exception"}
SOURCE_AUDITS = {"pending-human-review", "approved"}


class ParityError(ValueError):
    """A stable, user-actionable manifest validation error."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_bytes(payload: Any) -> bytes:
    """Return the repository's deterministic JSON representation."""

    return (
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ParityError(f"malformed {label}") from exc
    if not isinstance(payload, dict):
        raise ParityError(f"{label} must be a JSON object")
    return payload


def expected_unit_ids(root: Path) -> list[str]:
    config = validate_book.load_config(root)
    units = scoped_units(root, config)
    if len(units) != EXPECTED_CANONICAL_SOURCES:
        raise ParityError(
            f"expected {EXPECTED_CANONICAL_SOURCES} canonical units, found {len(units)}"
        )
    return [unit.name for unit in units]


def partition_index(payload: dict[str, Any], units: Sequence[str]) -> dict[str, Any]:
    notice = payload.get("notice")
    if not isinstance(notice, str) or not notice:
        raise ParityError("manifest notice must be a non-empty string")
    return {
        "schema_version": INDEX_SCHEMA_VERSION,
        "notice": notice,
        "store_root": STORE_ROOT,
        "units": list(units),
        "locales": list(LOCALES),
    }


def validate_index(
    index: dict[str, Any], root: Path, expected_units: Sequence[str] | None = None
) -> tuple[list[str], Path]:
    expected_keys = {"schema_version", "notice", "store_root", "units", "locales"}
    if set(index) != expected_keys or index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ParityError("unsupported or malformed parity index schema")
    notice = index.get("notice")
    units = index.get("units")
    locales = index.get("locales")
    if not isinstance(notice, str) or not notice:
        raise ParityError("parity index notice must be a non-empty string")
    if (
        not isinstance(units, list)
        or any(not isinstance(unit, str) or not unit for unit in units)
        or len(set(units)) != len(units)
    ):
        raise ParityError("parity index units must be unique non-empty strings")
    if units != sorted(units) or any(
        re.fullmatch(r"(?:chapter|appendix)-[a-z0-9][a-z0-9-]*", unit) is None
        for unit in units
    ):
        raise ParityError("parity index units are unsafe or not deterministically ordered")
    if locales != list(LOCALES):
        raise ParityError("parity index locales must be ordered as es, ca, sv, ar")
    if len(units) != EXPECTED_CANONICAL_SOURCES:
        raise ParityError(
            f"parity index must contain exactly {EXPECTED_CANONICAL_SOURCES} units"
        )
    if expected_units is not None and list(units) != list(expected_units):
        raise ParityError("parity index units do not match published unit discovery")
    if index.get("store_root") != STORE_ROOT:
        raise ParityError(f"parity index store_root must be {STORE_ROOT}")
    store = root / STORE_ROOT
    try:
        validate_book.safe_relative(store, root)
    except validate_book.ConfigError as exc:
        raise ParityError("partition store escapes repository") from exc
    return list(units), store


def source_leaf_path(store: Path, unit: str) -> Path:
    return store / SOURCE_STORE / f"{unit}.json"


def record_leaf_path(store: Path, unit: str, locale: str) -> Path:
    return store / RECORD_STORE / unit / f"{locale}.json"


def leaf_payload(kind: str, value: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": LEAF_SCHEMA_VERSION, kind: value}


def expected_leaf_paths(store: Path, units: Sequence[str]) -> set[Path]:
    paths = {source_leaf_path(store, unit) for unit in units}
    paths.update(
        record_leaf_path(store, unit, locale)
        for unit in units
        for locale in LOCALES
    )
    return paths


def load_partition_store(
    index: dict[str, Any],
    root: Path,
    *,
    expected_units: Sequence[str] | None = None,
    store_override: Path | None = None,
) -> dict[str, Any]:
    units, declared_store = validate_index(index, root, expected_units)
    store = store_override if store_override else declared_store
    try:
        validate_book.safe_relative(store, root)
    except validate_book.ConfigError as exc:
        raise ParityError("partition store escapes repository") from exc
    if not store.is_dir() or store.is_symlink():
        raise ParityError("partition store is missing or unsafe")

    expected = expected_leaf_paths(store, units)
    actual: set[Path] = set()
    for candidate in store.rglob("*"):
        if candidate.is_symlink():
            raise ParityError(f"partition store contains symlink under {STORE_ROOT}")
        if candidate.is_file():
            actual.add(candidate)
    missing = sorted(path.relative_to(root).as_posix() for path in expected - actual)
    extra = sorted(path.relative_to(root).as_posix() for path in actual - expected)
    if missing:
        raise ParityError(f"partition store is missing evidence: {missing[0]}")
    if extra:
        raise ParityError(f"partition store contains extra evidence under {STORE_ROOT}")

    sources: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for unit in units:
        source_path = source_leaf_path(store, unit)
        source_leaf = read_json_object(source_path, "canonical source leaf")
        if source_path.read_bytes() != canonical_json_bytes(source_leaf):
            raise ParityError(f"non-canonical canonical source leaf: {unit}")
        if set(source_leaf) != {"schema_version", "source"} or source_leaf.get(
            "schema_version"
        ) != LEAF_SCHEMA_VERSION:
            raise ParityError(f"malformed canonical source leaf: {unit}")
        source = source_leaf.get("source")
        if not isinstance(source, dict) or source.get("unit") != unit:
            raise ParityError(f"canonical source leaf identity mismatch: {unit}")
        sources.append(source)
        for locale in LOCALES:
            record_path = record_leaf_path(store, unit, locale)
            record_leaf = read_json_object(record_path, "localized record leaf")
            if record_path.read_bytes() != canonical_json_bytes(record_leaf):
                raise ParityError(f"non-canonical localized record leaf: {unit}:{locale}")
            if set(record_leaf) != {"schema_version", "record"} or record_leaf.get(
                "schema_version"
            ) != LEAF_SCHEMA_VERSION:
                raise ParityError(f"malformed localized record leaf: {unit}:{locale}")
            record = record_leaf.get("record")
            if (
                not isinstance(record, dict)
                or record.get("unit") != unit
                or record.get("locale") != locale
            ):
                raise ParityError(f"localized record leaf identity mismatch: {unit}:{locale}")
            records.append(record)
    return {
        "schema_version": SCHEMA_VERSION,
        "notice": index["notice"],
        "sources": sources,
        "records": records,
    }


def load_manifest(
    path: Path, root: Path, expected_units: Sequence[str] | None = None
) -> dict[str, Any]:
    payload = read_json_object(path, "parity manifest")
    version = payload.get("schema_version")
    if version == SCHEMA_VERSION:
        return payload
    if version == INDEX_SCHEMA_VERSION:
        if path.read_bytes() != canonical_json_bytes(payload):
            raise ParityError("parity index is non-canonical or changed while loading")
        units = list(expected_units) if expected_units is not None else expected_unit_ids(root)
        return load_partition_store(payload, root, expected_units=units)
    raise ParityError("unsupported parity manifest schema_version")


def snapshot_manifest(
    path: Path, root: Path, expected_units: Sequence[str] | None = None
) -> tuple[dict[str, Any], dict[Path, bytes]]:
    """Load one aggregate together with the exact storage bytes it came from."""

    manifest_bytes = path.read_bytes()
    aggregate = load_manifest(path, root, expected_units)
    if path.read_bytes() != manifest_bytes:
        raise ParityError("parity manifest changed while taking a storage snapshot")
    snapshot = {path: manifest_bytes}
    index = json.loads(manifest_bytes)
    if isinstance(index, dict) and index.get("schema_version") == INDEX_SCHEMA_VERSION:
        units = list(expected_units) if expected_units is not None else expected_unit_ids(root)
        units, store = validate_index(index, root, units)
        planned = partition_files(aggregate, units, store)
        for target, expected in planned.items():
            current = target.read_bytes()
            if current != expected:
                raise ParityError(
                    "partition evidence is non-canonical or changed while taking a snapshot"
                )
            snapshot[target] = current
        if path.read_bytes() != manifest_bytes:
            raise ParityError("parity index changed while taking a storage snapshot")
    return aggregate, snapshot


def aggregate_maps(
    payload: dict[str, Any], units: Sequence[str]
) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    sources = payload.get("sources")
    records = payload.get("records")
    if not isinstance(sources, list) or not isinstance(records, list):
        raise ParityError("aggregate sources and records must be lists")
    source_map = {
        str(source.get("unit")): source
        for source in sources
        if isinstance(source, dict) and source.get("unit")
    }
    record_map = {
        (str(record.get("unit")), str(record.get("locale"))): record
        for record in records
        if isinstance(record, dict) and record.get("unit") and record.get("locale")
    }
    if len(source_map) != len(sources) or set(source_map) != set(units):
        raise ParityError("aggregate canonical source identities do not match the index")
    expected_records = {(unit, locale) for unit in units for locale in LOCALES}
    if len(record_map) != len(records) or set(record_map) != expected_records:
        raise ParityError("aggregate localized record identities do not match the index")
    return source_map, record_map


def ordered_aggregate(payload: dict[str, Any], units: Sequence[str]) -> dict[str, Any]:
    source_map, record_map = aggregate_maps(payload, units)
    return {
        "schema_version": SCHEMA_VERSION,
        "notice": payload.get("notice"),
        "sources": [source_map[unit] for unit in units],
        "records": [record_map[(unit, locale)] for unit in units for locale in LOCALES],
    }


def partition_files(
    payload: dict[str, Any], units: Sequence[str], store: Path
) -> dict[Path, bytes]:
    source_map, record_map = aggregate_maps(payload, units)
    files = {
        source_leaf_path(store, unit): canonical_json_bytes(
            leaf_payload("source", source_map[unit])
        )
        for unit in units
    }
    files.update(
        {
            record_leaf_path(store, unit, locale): canonical_json_bytes(
                leaf_payload("record", record_map[(unit, locale)])
            )
            for unit in units
            for locale in LOCALES
        }
    )
    return files


NO_EXPECTED_BYTES = object()
RENAME_NOREPLACE = 1
RENAME_EXCHANGE = 2


class AtomicRecoveryError(ParityError):
    """An atomic rollback failed, so the temporary evidence must be retained."""


def linux_renameat2(source: Path, target: Path, flags: int) -> None:
    """Call Linux renameat2 with explicit no-replace or exchange semantics."""

    if not sys.platform.startswith("linux"):
        raise ParityError("atomic parity publication is unavailable on this platform")
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is None:
        raise ParityError("atomic parity publication is unavailable")
    renameat2.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    renameat2.restype = ctypes.c_int
    result = renameat2(
        -100,
        os.fsencode(source),
        -100,
        os.fsencode(target),
        flags,
    )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(error_number, "atomic parity rename failed")


def cooperative_lock_path(target: Path) -> Path:
    """Return a non-secret, per-user/per-target lock name outside the repo."""

    user_id = str(os.getuid()) if hasattr(os, "getuid") else str(Path.home())
    identity = f"{target.absolute()}\0{user_id}".encode("utf-8")
    suffix = hashlib.sha256(identity).hexdigest()[:32]
    user_tag = user_id if user_id.isdecimal() else hashlib.sha256(
        user_id.encode("utf-8")
    ).hexdigest()[:8]
    base = Path("/tmp") if os.name != "nt" else Path(tempfile.gettempdir())
    return base / f"course-python-parity-{user_tag}-{suffix}.lock"


@contextlib.contextmanager
def cooperative_mutation_lock(target: Path):
    """Serialize fallback writers without creating repository artifacts."""

    lock_path = cooperative_lock_path(target)
    flags = os.O_CREAT | os.O_RDWR
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd: int | None = None
    try:
        fd = os.open(lock_path, flags, 0o600)
        path_stat = lock_path.lstat()
        file_stat = os.fstat(fd)
        owner_is_safe = not hasattr(os, "getuid") or file_stat.st_uid == os.getuid()
        if (
            not stat.S_ISREG(path_stat.st_mode)
            or (path_stat.st_dev, path_stat.st_ino)
            != (file_stat.st_dev, file_stat.st_ino)
            or file_stat.st_nlink != 1
            or file_stat.st_size != 0
            or file_stat.st_mode & 0o077
            or not owner_is_safe
        ):
            os.close(fd)
            fd = None
            raise ParityError("unsafe cooperative parity lock")
    except OSError as exc:
        if fd is not None:
            os.close(fd)
        raise ParityError("unsafe or unavailable cooperative parity lock") from exc
    try:
        with os.fdopen(fd, "r+b", closefd=True) as stream:
            fd = None
            try:
                if os.name == "nt":
                    import msvcrt

                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (BlockingIOError, OSError) as exc:
                raise ParityError(
                    "another parity mutation holds the cooperative lock"
                ) from exc
            try:
                yield
            finally:
                if os.name == "nt":
                    import msvcrt

                    stream.seek(0)
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    finally:
        if fd is not None:
            os.close(fd)


def cooperative_compare_exchange(
    temporary: Path, target: Path, data: bytes, expected: bytes | None
) -> None:
    """Portable fallback protecting cooperating tool writers.

    Unlike Linux ``RENAME_EXCHANGE``, this cannot protect against an external
    editor that deliberately ignores the shared lock.  It therefore rechecks
    under the lock and makes no stronger cross-process claim.
    """

    with cooperative_mutation_lock(target):
        observed = read_optional_bytes(target)
        if observed == data:
            return
        if observed != expected:
            raise ParityError(
                "concurrent evidence change detected during cooperative publication"
            )
        if expected is None:
            try:
                os.link(temporary, target)
            except FileExistsError as exc:
                raise ParityError(
                    "concurrent evidence change detected during cooperative publication"
                ) from exc
        else:
            os.replace(temporary, target)


def atomic_compare_exchange(
    temporary: Path, target: Path, data: bytes, expected: bytes | None
) -> None:
    """Publish ``data`` only if the target still contains ``expected`` bytes."""

    if not sys.platform.startswith("linux"):
        cooperative_compare_exchange(temporary, target, data, expected)
        return

    if expected is None:
        try:
            linux_renameat2(temporary, target, RENAME_NOREPLACE)
        except OSError as exc:
            if exc.errno in {errno.EEXIST, errno.ENOTEMPTY}:
                raise ParityError(
                    "concurrent evidence change detected during atomic publication"
                ) from exc
            raise
        return

    try:
        linux_renameat2(temporary, target, RENAME_EXCHANGE)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            raise ParityError(
                "concurrent evidence change detected during atomic publication"
            ) from exc
        raise
    observed = temporary.read_bytes()
    if observed in {expected, data}:
        return
    try:
        linux_renameat2(temporary, target, RENAME_EXCHANGE)
    except OSError as exc:
        raise AtomicRecoveryError(
            f"atomic rollback failed; retained recovery evidence: {temporary.name}"
        ) from exc
    raise ParityError("concurrent evidence change detected during atomic publication")


def read_optional_bytes(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def atomic_write(
    path: Path,
    data: bytes,
    *,
    refuse_conflict: bool = False,
    expected: bytes | None | object = NO_EXPECTED_BYTES,
) -> bool:
    current = read_optional_bytes(path)
    if current == data:
        return False
    if expected is not NO_EXPECTED_BYTES and current != expected:
        raise ParityError("concurrent evidence change detected before atomic publication")
    if refuse_conflict and current is not None:
        raise ParityError("refusing to replace conflicting output")
    operation_expected = current
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            stream.write(data)
            stream.flush()
            temporary = Path(stream.name)
        if temporary.read_bytes() != data:
            raise ParityError("temporary write verification failed")
        compare_with = expected if expected is not NO_EXPECTED_BYTES else operation_expected
        try:
            atomic_compare_exchange(temporary, path, data, compare_with)
        except AtomicRecoveryError:
            temporary = None
            raise
        if temporary.exists():
            temporary.unlink()
        temporary = None
        return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_partition_store(
    store: Path,
    payload: dict[str, Any],
    units: Sequence[str],
    *,
    owned: bool = False,
) -> None:
    if owned:
        if store.is_symlink() or not store.is_dir() or any(store.iterdir()):
            raise ParityError("owned partition destination is not an empty directory")
    else:
        try:
            store.mkdir()
        except FileExistsError as exc:
            raise ParityError("partition staging destination already exists") from exc
    for path, data in partition_files(payload, units, store).items():
        atomic_write(path, data, expected=None)


def write_partitioned_manifest(
    path: Path,
    payload: dict[str, Any],
    root: Path,
    baseline: dict[Path, bytes] | None,
) -> list[str]:
    if baseline is None:
        raise ParityError("partition write requires an old-to-new storage snapshot")
    index = read_json_object(path, "parity index")
    units, store = validate_index(index, root, expected_unit_ids(root))
    # The baseline may be digest-stale precisely because --write or
    # --reconcile-drafts is refreshing changed Markdown.  Loading the store
    # still proves topology/schema/canonical bytes; only the next aggregate
    # must validate against the current content digests.
    load_partition_store(index, root, expected_units=units)
    ordered = ordered_aggregate(payload, units)
    validate_manifest(ordered, root)
    planned = partition_files(ordered, units, store)
    expected_paths = {path, *planned}
    if set(baseline) != expected_paths:
        raise ParityError("storage snapshot does not match the partition topology")
    if path.read_bytes() != baseline[path]:
        raise ParityError("parity index changed after the old-to-new snapshot")
    baseline_index = json.loads(baseline[path])
    if ordered.get("notice") != baseline_index.get("notice"):
        raise ParityError("ordinary review cannot change the parity index notice")
    desired = {
        target: data
        for target, data in planned.items()
        if data != baseline[target]
    }
    for target, data in desired.items():
        current_bytes = target.read_bytes()
        if current_bytes not in {baseline[target], data}:
            raise ParityError(
                f"concurrent evidence change detected: {target.relative_to(root).as_posix()}"
            )
    changed: list[str] = []
    for target, data in desired.items():
        if atomic_write(target, data, expected=baseline[target]):
            changed.append(target.relative_to(root).as_posix())
    reloaded = load_partition_store(index, root, expected_units=units)
    validate_manifest(reloaded, root)
    for target, data in desired.items():
        if target.read_bytes() != data:
            raise ParityError("partition write did not preserve its old-to-new leaf plan")
    return sorted(changed)


def publish_directory_noreplace(source: Path, target: Path) -> None:
    """Atomically publish one complete directory without replacing any path.

    Linux exposes the required no-clobber directory rename through
    ``renameat2(RENAME_NOREPLACE)``.  Other platforms fail closed because a
    check followed by ``Path.rename`` would reintroduce a destructive race.
    """

    try:
        linux_renameat2(source, target, RENAME_NOREPLACE)
    except OSError as exc:
        if exc.errno in {errno.EEXIST, errno.ENOTEMPTY}:
            raise ParityError("partition store appeared during migration") from exc
        raise


def migrate_partitioned(path: Path, root: Path) -> None:
    legacy = read_json_object(path, "schema-v1 parity manifest")
    if legacy.get("schema_version") != SCHEMA_VERSION:
        raise ParityError("--migrate-partitioned requires a schema-v1 manifest")
    units = expected_unit_ids(root)
    validate_manifest(legacy, root)
    ordered = ordered_aggregate(legacy, units)
    legacy_bytes = canonical_json_bytes(ordered)
    if path.read_bytes() != legacy_bytes:
        raise ParityError("schema-v1 manifest is not in canonical deterministic form")
    index = partition_index(ordered, units)
    store = root / STORE_ROOT
    staging = store.with_name(f".{store.name}.staging")
    if staging.exists() or staging.is_symlink():
        raise ParityError("partition migration staging path already exists")
    if store.is_symlink():
        raise ParityError("partition store is missing or unsafe")
    created_staging = False
    try:
        if store.exists():
            existing = load_partition_store(
                index, root, expected_units=units, store_override=store
            )
            if canonical_json_bytes(existing) != legacy_bytes:
                raise ParityError("existing partition store conflicts with schema-v1 manifest")
        else:
            try:
                staging.mkdir()
            except FileExistsError as exc:
                raise ParityError("partition migration staging path already exists") from exc
            created_staging = True
            write_partition_store(staging, ordered, units, owned=True)
            staged = load_partition_store(
                index, root, expected_units=units, store_override=staging
            )
            validate_manifest(staged, root)
            if canonical_json_bytes(staged) != legacy_bytes:
                raise ParityError("staged partition does not match schema-v1 manifest")
            publish_directory_noreplace(staging, store)
            created_staging = False
            published = load_partition_store(index, root, expected_units=units)
            validate_manifest(published, root)
            if canonical_json_bytes(published) != legacy_bytes:
                raise ParityError("published partition store does not match schema-v1 manifest")
        if path.read_bytes() != legacy_bytes:
            raise ParityError("schema-v1 manifest changed during partition migration")
        atomic_write(path, canonical_json_bytes(index), expected=legacy_bytes)
        reloaded = load_manifest(path, root, expected_units=units)
        validate_manifest(reloaded, root)
        if canonical_json_bytes(reloaded) != legacy_bytes:
            raise ParityError("published partition does not match schema-v1 manifest")
    finally:
        if created_staging and staging.exists() and not staging.is_symlink():
            shutil.rmtree(staging)


def export_monolith(path: Path, output: Path, root: Path) -> None:
    index = read_json_object(path, "parity index")
    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ParityError("--export-monolith requires a schema-v2 parity index")
    output = output.resolve(strict=False)
    try:
        validate_book.safe_relative(output, root)
    except validate_book.ConfigError as exc:
        raise ParityError("monolith export path escapes repository") from exc
    live_store = (root / STORE_ROOT).resolve(strict=False)
    if output == path.resolve(strict=False) or output == live_store or live_store in output.parents:
        raise ParityError("monolith export must not replace live partition storage")
    units = expected_unit_ids(root)
    aggregate = load_partition_store(index, root, expected_units=units)
    validate_manifest(aggregate, root)
    data = canonical_json_bytes(ordered_aggregate(aggregate, units))
    atomic_write(output, data, refuse_conflict=True)
    if output.read_bytes() != data:
        raise ParityError("monolith export failed byte verification")


def scoped_units(root: Path, config: dict[str, Any]) -> list[Path]:
    """Discover the exact publication scope owned by the root validator."""
    return validate_book.discover_units(root, config)


def signals(path: Path, root: Path, config: dict[str, Any]) -> dict[str, Any]:
    scan = validate_book.scan_markdown(path, root, config)
    text = path.read_text(encoding="utf-8")
    return {
        "words": len(re.findall(r"\b\w+\b", text, re.UNICODE)),
        "headings": len(scan.headings),
        "fences": len(scan.fences),
        "source_refs": sum(fence.classification == "source-ref" for fence in scan.fences),
        "fence_sequence_sha256": hashlib.sha256(
            json.dumps(
                [
                    [
                        fence.classification,
                        fence.metadata.get("path") if fence.classification == "source-ref" else None,
                        fence.metadata.get("check") if fence.classification == "source-ref" else None,
                    ]
                    for fence in scan.fences
                ],
                sort_keys=True,
            ).encode()
        ).hexdigest(),
    }


def initial_priority(locale: str, canonical: dict[str, Any], localized: dict[str, Any], unit: str) -> str:
    word_ratio = localized["words"] / max(1, canonical["words"])
    chapter_match = re.match(r"chapter-(\d+)-", unit)
    chapter_number = int(chapter_match.group(1)) if chapter_match else None
    if locale in {"sv", "ar"} or word_ratio < 0.65:
        return "high"
    if locale == "ca" and (chapter_number is not None and 15 <= chapter_number <= 25):
        return "high"
    if word_ratio < 0.85 or localized["fence_sequence_sha256"] != canonical["fence_sequence_sha256"]:
        return "medium"
    return "normal"


def empty_review() -> dict[str, Any]:
    return {"result": "pending", "role": "", "review_date": "", "notes": ""}


def gap_signals(canonical: dict[str, Any], localized: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    word_ratio = localized["words"] / max(1, canonical["words"])
    if word_ratio < 0.75:
        gaps.append(f"word-count triage ratio is {word_ratio:.2f}; semantic review required")
    if localized["headings"] < canonical["headings"]:
        gaps.append(
            f"heading-count triage signal is {localized['headings']}/{canonical['headings']}; structure may be condensed"
        )
    if localized["fence_sequence_sha256"] != canonical["fence_sequence_sha256"]:
        gaps.append("classified fence/source-evidence sequence differs from canonical")
    if localized["source_refs"] != canonical["source_refs"]:
        gaps.append(f"source-ref count differs: {localized['source_refs']}/{canonical['source_refs']}")
    return gaps


def load_existing(path: Path, root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_manifest(path, root)
    return {
        (record["unit"], record["locale"]): record
        for record in payload.get("records", [])
        if isinstance(record, dict) and "unit" in record and "locale" in record
    }


def load_existing_sources(path: Path, root: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = load_manifest(path, root)
    return {
        source["unit"]: source
        for source in payload.get("sources", [])
        if isinstance(source, dict) and "unit" in source
    }


def build_manifest(
    root: Path,
    previous_path: Path | None = None,
    *,
    previous_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = validate_book.load_config(root)
    units = scoped_units(root, config)
    if len(units) != EXPECTED_CANONICAL_SOURCES:
        raise ParityError(
            f"expected {EXPECTED_CANONICAL_SOURCES} canonical units, found {len(units)}"
        )
    if previous_payload is not None and previous_path is not None:
        raise ParityError("provide either a previous path or a previous aggregate, not both")
    if previous_payload is None and previous_path is not None:
        previous_payload = load_manifest(previous_path, root)
    if previous_payload is None:
        previous: dict[tuple[str, str], dict[str, Any]] = {}
        previous_sources: dict[str, dict[str, Any]] = {}
    else:
        previous_sources, previous = aggregate_maps(
            previous_payload, [unit.name for unit in units]
        )
    records: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    for unit in units:
        canonical_path = unit / "README.md"
        if not canonical_path.is_file():
            raise ParityError(f"missing canonical source: {canonical_path.relative_to(root).as_posix()}")
        canonical_digest = digest(canonical_path)
        canonical_signals = signals(canonical_path, root, config)
        previous_source = previous_sources.get(unit.name, {})
        source_audit = (
            previous_source.get("audit")
            if previous_source.get("sha256") == canonical_digest
            and previous_source.get("audit") in SOURCE_AUDITS
            else "pending-human-review"
        )
        sources.append(
            {
                "unit": unit.name,
                "path": canonical_path.relative_to(root).as_posix(),
                "sha256": canonical_digest,
                "signals": canonical_signals,
                "audit": source_audit,
            }
        )
        for locale, filename in LOCALES.items():
            localized_path = unit / filename
            if not localized_path.is_file():
                raise ParityError(f"missing localized variant: {localized_path.relative_to(root).as_posix()}")
            localized_signals = signals(localized_path, root, config)
            localized_digest = digest(localized_path)
            prior = previous.get((unit.name, locale))
            if prior and prior.get("canonical_sha256") == canonical_digest:
                record = dict(prior)
                record["signals"] = localized_signals
                if prior.get("localized_sha256") != localized_digest:
                    record.update(
                        {
                            "status": "drafted",
                            "contract": {dimension: "pending" for dimension in CONTRACT_DIMENSIONS},
                            "exceptions": [],
                            "automated_commands": [],
                            "linguistic_review": empty_review(),
                            "technical_review": empty_review(),
                        }
                    )
                record["localized_sha256"] = localized_digest
                record["priority"] = initial_priority(locale, canonical_signals, localized_signals, unit.name)
                record["observed_gaps"] = gap_signals(canonical_signals, localized_signals)
            else:
                record = {
                    "unit": unit.name,
                    "locale": locale,
                    "path": localized_path.relative_to(root).as_posix(),
                    "canonical_sha256": canonical_digest,
                    "localized_sha256": localized_digest,
                    "status": "stale" if prior else "inventoried",
                    "priority": initial_priority(locale, canonical_signals, localized_signals, unit.name),
                    "signals": localized_signals,
                    "observed_gaps": gap_signals(canonical_signals, localized_signals),
                    "contract": {dimension: "pending" for dimension in CONTRACT_DIMENSIONS},
                    "exceptions": [],
                    "automated_commands": [],
                    "linguistic_review": empty_review(),
                    "technical_review": empty_review(),
                }
            records.append(record)
    return {
        "schema_version": SCHEMA_VERSION,
        "notice": "Structural metrics are triage signals, never proof of semantic or linguistic parity.",
        "sources": sources,
        "records": records,
    }


def validate_transition(previous: str, current: str) -> None:
    if previous not in STATES or current not in STATES:
        raise ParityError("unknown review state")
    if current in {"stale", "blocked"} or previous in {"stale", "blocked"}:
        return
    order = [state for state in STATES if state not in {"stale", "blocked"}]
    if order.index(current) < order.index(previous):
        raise ParityError(f"state regression is not allowed: {previous} -> {current}")


def validate_manifest(
    payload: dict[str, Any], root: Path, *, require_accepted: bool = False
) -> None:
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ParityError("unsupported parity manifest schema_version")
    sources = payload.get("sources")
    records = payload.get("records")
    if not isinstance(sources, list) or len(sources) != EXPECTED_CANONICAL_SOURCES:
        raise ParityError(
            f"manifest must contain exactly {EXPECTED_CANONICAL_SOURCES} canonical sources"
        )
    if not isinstance(records, list) or len(records) != EXPECTED_LOCALIZED_RECORDS:
        raise ParityError(
            f"manifest must contain exactly {EXPECTED_LOCALIZED_RECORDS} localized records"
        )
    source_map: dict[str, dict[str, Any]] = {}
    for source in sources:
        if not isinstance(source, dict):
            raise ParityError("canonical sources must be JSON objects")
        unit = source.get("unit")
        if source.get("path") != f"{unit}/README.md":
            raise ParityError(f"canonical source path mismatch: {unit}")
        path = (root / str(source.get("path", ""))).resolve(strict=False)
        try:
            validate_book.safe_relative(path, root)
        except validate_book.ConfigError as exc:
            raise ParityError(f"canonical source escapes repository: {unit}") from exc
        if (
            unit in source_map
            or source.get("audit") not in SOURCE_AUDITS
            or not path.is_file()
            or digest(path) != source.get("sha256")
        ):
            raise ParityError(f"invalid or stale canonical source: {unit}")
        source_map[str(unit)] = source
    seen: set[tuple[str, str]] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ParityError("localized records must be JSON objects")
        key = (str(record.get("unit", "")), str(record.get("locale", "")))
        if key in seen or key[0] not in source_map or key[1] not in LOCALES:
            raise ParityError(f"invalid or duplicate localized record: {key}")
        seen.add(key)
        if record.get("path") != f"{key[0]}/{LOCALES[key[1]]}":
            raise ParityError(f"localized record path mismatch: {key}")
        path = (root / str(record.get("path", ""))).resolve(strict=False)
        try:
            validate_book.safe_relative(path, root)
        except validate_book.ConfigError as exc:
            raise ParityError(f"localized record escapes repository: {key}") from exc
        if not path.is_file() or digest(path) != record.get("localized_sha256"):
            raise ParityError(f"localized record is stale: {key}")
        if record.get("canonical_sha256") != source_map[key[0]]["sha256"]:
            raise ParityError(f"canonical digest mismatch: {key}")
        status = record.get("status")
        if status not in STATES:
            raise ParityError(f"unknown status: {key}")
        automated_commands = record.get("automated_commands")
        if not isinstance(automated_commands, list) or any(
            not isinstance(command, str) or not command
            for command in automated_commands
        ):
            raise ParityError(f"malformed automated evidence: {key}")
        contract = record.get("contract")
        if not isinstance(contract, dict) or set(contract) != set(CONTRACT_DIMENSIONS):
            raise ParityError(f"incomplete parity contract: {key}")
        if any(result not in CONTRACT_RESULTS for result in contract.values()):
            raise ParityError(f"unknown contract result: {key}")
        exceptions = record.get("exceptions", [])
        if not isinstance(exceptions, list):
            raise ParityError(f"exceptions must be a list: {key}")
        exception_dimensions = set()
        for exception in exceptions:
            required = {"dimension", "justification", "linguistic_approved", "technical_approved"}
            if not isinstance(exception, dict) or set(exception) != required:
                raise ParityError(f"malformed parity exception: {key}")
            dimension = exception["dimension"]
            justification = exception["justification"]
            if (
                dimension not in CONTRACT_DIMENSIONS
                or dimension in exception_dimensions
                or not isinstance(justification, str)
                or not justification.strip()
            ):
                raise ParityError(f"malformed parity exception: {key}")
            if (
                exception["linguistic_approved"] is not True
                or exception["technical_approved"] is not True
            ):
                raise ParityError(f"unapproved parity exception: {key}")
            exception_dimensions.add(dimension)
        required_exception_dimensions = {
            dimension for dimension, result in contract.items() if result == "exception"
        }
        if exception_dimensions != required_exception_dimensions:
            raise ParityError(f"contract exceptions do not match approvals: {key}")
        reviews = (record.get("linguistic_review"), record.get("technical_review"))
        for review in reviews:
            if (
                not isinstance(review, dict)
                or set(review) != {"result", "role", "review_date", "notes"}
                or review.get("result") not in REVIEW_RESULTS
                or any(
                    not isinstance(review.get(field), str)
                    for field in ("role", "review_date", "notes")
                )
            ):
                raise ParityError(f"malformed human review: {key}")
        if status == "accepted":
            if any(result not in {"pass", "exception"} for result in contract.values()):
                raise ParityError(f"accepted record has incomplete contract: {key}")
            if any(
                review.get("result") != "approved"
                or not review.get("role", "").strip()
                or not review.get("review_date", "").strip()
                for review in reviews
            ):
                raise ParityError(f"accepted record lacks both human approvals: {key}")
            if source_map[key[0]].get("audit") != "approved":
                raise ParityError(f"accepted record lacks canonical source audit: {key}")
            required_commands = {
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            }
            if not required_commands <= set(automated_commands):
                raise ParityError(f"accepted record lacks automated evidence: {key}")
    if require_accepted:
        pending_sources = sorted(
            str(source.get("unit")) for source in sources if source.get("audit") != "approved"
        )
        pending_records = sorted(
            f"{record.get('unit')}:{record.get('locale')}"
            for record in records
            if record.get("status") != "accepted"
        )
        if pending_sources or pending_records:
            raise ParityError(
                "publication review incomplete: "
                f"{len(pending_sources)} canonical audits and {len(pending_records)} localized reviews pending"
            )


def record_automated_results(
    payload: dict[str, Any], diagnostics: Sequence[validate_book.Diagnostic]
) -> int:
    source_units = {
        str(source.get("unit"))
        for source in payload.get("sources", [])
        if isinstance(source, dict) and source.get("unit")
    }
    record_paths = {
        str(record.get("path"))
        for record in payload.get("records", [])
        if isinstance(record, dict) and record.get("path")
    }
    blocked_paths: set[str] = set()
    blocked_units: set[str] = set()
    global_blocker = False
    for diagnostic in diagnostics:
        if diagnostic.severity not in {"error", "warning"}:
            continue
        path = diagnostic.path
        if path in record_paths:
            blocked_paths.add(path)
            continue
        unit = path.split("/", 1)[0] if path not in {"", "."} else ""
        if unit and unit in source_units:
            # A canonical README, companion source, or unit-level diagnostic
            # invalidates automated evidence for every localized sibling.
            blocked_units.add(unit)
        else:
            # Root/config/tooling failures mean the shared gate did not pass;
            # no individual record may be promoted from that run.
            global_blocker = True
    if global_blocker:
        return 0
    promoted = 0
    for record in payload.get("records", []):
        if (
            record.get("status") != "drafted"
            or record.get("path") in blocked_paths
            or record.get("unit") in blocked_units
        ):
            continue
        validate_transition("drafted", "automated-signals-pass")
        record["status"] = "automated-signals-pass"
        record["automated_commands"] = [
            "python -B tools/validate_book.py",
            "python -B tools/parity_review.py",
        ]
        promoted += 1
    return promoted


def automated_gate_diagnostics(
    root: Path, config: dict[str, Any]
) -> list[validate_book.Diagnostic]:
    """Return the same effective failures as the full generic validator.

    ``collect_diagnostics`` includes exact reviewed baseline debt. Promotion
    must ignore that accepted legacy evidence while still failing closed when
    a baseline fingerprint is stale.
    """
    collected = validate_book.collect_diagnostics(root, config, [])
    failures, stale = validate_book.apply_baseline(root, config, collected, set())
    for fingerprint in stale:
        failures.append(
            validate_book.Diagnostic(
                "baseline.stale",
                str(config["baseline"]),
                "resolved baseline fingerprint must be removed",
                "remove the stale reviewed fingerprint before recording automated evidence",
                construct=fingerprint,
            )
        )
    return failures


def reconcile_draft_records(payload: dict[str, Any]) -> int:
    """Explicitly reset stale/inventoried records to a reviewable draft.

    This transition intentionally discards evidence attached to an older
    canonical or localized digest.  It never changes a progressed or accepted
    record and never records either human approval.
    """

    records = payload.get("records")
    if not isinstance(records, list):
        raise ParityError("manifest records must be a list before reconciliation")
    reconciled = 0
    for record in records:
        if not isinstance(record, dict):
            raise ParityError("manifest records must be objects before reconciliation")
        status = record.get("status")
        if status not in STATES:
            raise ParityError("unknown review state before reconciliation")
        if status not in {"stale", "inventoried"}:
            continue
        validate_transition(status, "drafted")
        record.update(
            {
                "status": "drafted",
                "contract": {dimension: "pending" for dimension in CONTRACT_DIMENSIONS},
                "exceptions": [],
                "automated_commands": [],
                "linguistic_review": empty_review(),
                "technical_review": empty_review(),
            }
        )
        reconciled += 1
    return reconciled


def write_manifest(
    path: Path,
    payload: dict[str, Any],
    root: Path,
    baseline: dict[Path, bytes] | None = None,
) -> list[str]:
    """Write a legacy monolith or only changed partition leaves."""

    if path.is_file():
        current = read_json_object(path, "parity manifest")
        if current.get("schema_version") == INDEX_SCHEMA_VERSION:
            return write_partitioned_manifest(path, payload, root, baseline)
    expected = None if not path.exists() else (
        baseline[path] if baseline is not None and path in baseline else NO_EXPECTED_BYTES
    )
    if path.exists() and expected is NO_EXPECTED_BYTES:
        raise ParityError("manifest write requires an old-to-new storage snapshot")
    changed = atomic_write(path, canonical_json_bytes(payload), expected=expected)
    return [path.relative_to(root).as_posix()] if changed else []


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true", help="create or refresh the deterministic inventory")
    actions.add_argument(
        "--record-automated",
        action="store_true",
        help="refresh the inventory and promote drafted records whose automated path diagnostics pass",
    )
    actions.add_argument(
        "--reconcile-drafts",
        action="store_true",
        help=(
            "explicitly refresh the inventory and reset only stale/inventoried "
            "records to drafted for a new human review cycle"
        ),
    )
    actions.add_argument(
        "--migrate-partitioned",
        action="store_true",
        help="losslessly migrate the current schema-v1 manifest to unit files",
    )
    actions.add_argument(
        "--export-monolith",
        metavar="PATH",
        help="write a validated schema-v1 rollback export without changing live storage",
    )
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument(
        "--require-accepted",
        action="store_true",
        help="publication gate for all 25 chapters and two appendices",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    path = (root / args.manifest).resolve()
    manifest_label = MANIFEST if args.manifest == MANIFEST else "<custom-manifest>"
    try:
        validate_book.safe_relative(path, root)
        if args.migrate_partitioned:
            migrate_partitioned(path, root)
            payload = load_manifest(path, root)
            print(
                f"Migrated parity inventory: {len(payload['sources'])} sources, "
                f"{len(payload['records'])} variants."
            )
            return 0
        if args.export_monolith:
            output = (root / args.export_monolith).resolve(strict=False)
            export_monolith(path, output, root)
            print(f"Exported schema-v1 parity manifest: {output.relative_to(root).as_posix()}")
            return 0
        mutating = args.write or args.record_automated or args.reconcile_drafts
        if mutating:
            if args.reconcile_drafts and not path.is_file():
                raise ParityError("--reconcile-drafts requires an existing manifest")
            previous_payload: dict[str, Any] | None = None
            baseline: dict[Path, bytes] | None = None
            if path.is_file():
                previous_payload, baseline = snapshot_manifest(path, root)
            payload = build_manifest(root, previous_payload=previous_payload)
            if args.reconcile_drafts:
                reconciled = reconcile_draft_records(payload)
                print(f"Reconciled {reconciled} stale/inventoried variants to drafted.")
            if args.record_automated:
                diagnostics = automated_gate_diagnostics(
                    root, validate_book.load_config(root)
                )
                promoted = record_automated_results(payload, diagnostics)
                print(f"Recorded automated-signals-pass for {promoted} drafted variants.")
            validate_manifest(payload, root, require_accepted=args.require_accepted)
            write_manifest(path, payload, root, baseline)
        else:
            payload = load_manifest(path, root)
            validate_manifest(payload, root, require_accepted=args.require_accepted)
        print(f"Parity inventory valid: {len(payload['sources'])} sources, {len(payload['records'])} variants.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR parity.inventory {manifest_label}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
