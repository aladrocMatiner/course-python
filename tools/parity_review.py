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
import tomllib
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit

import validate_book


LEGACY_SCHEMA_VERSION = 1
SCHEMA_VERSION = 2
INDEX_SCHEMA_VERSION = 2
LEGACY_LEAF_SCHEMA_VERSION = 1
LEAF_SCHEMA_VERSION = 2
MANIFEST = "tools/parity_manifest.json"
STORE_ROOT = "tools/parity"
SOURCE_STORE = "sources"
RECORD_STORE = "records"
ROOT_PUBLICATION_LEAF = "root-publication.json"
RENDER_PROFILE = "tools/render_review_profile.json"
ATTRIBUTIONS = "ATTRIBUTIONS.toml"
PUBLICATION_SIGNOFF = "tools/publication_signoff.json"
EXPECTED_CANONICAL_SOURCES = 27
EXPECTED_LOCALIZED_RECORDS = EXPECTED_CANONICAL_SOURCES * 4
EXPECTED_UNIT_LEAVES = EXPECTED_CANONICAL_SOURCES + EXPECTED_LOCALIZED_RECORDS
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
LEGACY_STATES = (
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
STATES = (
    "inventoried",
    "source-frozen",
    "drafted",
    "automated-signals-pass",
    "human-review-in-progress",
    "accepted",
    "stale",
    "blocked",
)
REVIEW_RESULTS = {"pending", "approved", "changes-requested"}
CONTRACT_RESULTS = {"pending", "pass", "exception"}
SOURCE_AUDITS = {"pending-human-review", "approved"}
ROOT_PATHS = (
    "README.md",
    "README.en.md",
    "README.es.md",
    "README.ca.md",
    "README.sv.md",
    "README.ar.md",
)
LOCALIZED_ROOT_PATHS = {
    "README.es.md",
    "README.ca.md",
    "README.sv.md",
    "README.ar.md",
}
REVIEW_BASE_FIELDS = {"result", "role", "review_date", "notes"}
ENVIRONMENT_FIELDS = {
    "renderer",
    "renderer_version",
    "browser",
    "browser_version",
    "os",
    "os_version",
    "assistive_technology",
    "assistive_technology_version",
}
RESOLVED_PROVENANCE_STATES = {
    "original-declared",
    "licensed-recorded",
    "public-domain-recorded",
}


class ParityError(ValueError):
    """A stable, user-actionable manifest validation error."""


class PublicationIncompleteError(ParityError):
    """Valid evidence is pending, changes-requested, or stale."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json_bytes(payload: Any) -> bytes:
    """Return the repository's deterministic JSON representation."""

    return (
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def write_stdout_bytes(data: bytes) -> None:
    stream = getattr(sys.stdout, "buffer", None)
    if stream is not None:
        stream.write(data)
    else:
        sys.stdout.write(data.decode("utf-8"))


def read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ParityError(f"malformed {label}") from exc
    if not isinstance(payload, dict):
        raise ParityError(f"{label} must be a JSON object")
    return payload


def safe_repository_path(root: Path, value: str, label: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ParityError(f"unsafe {label}")
    candidate = (root / value).resolve(strict=False)
    try:
        validate_book.safe_relative(candidate, root)
    except validate_book.ConfigError as exc:
        raise ParityError(f"unsafe {label}") from exc
    if candidate.relative_to(root.resolve()).as_posix() != value:
        raise ParityError(f"non-canonical {label}")
    return candidate


def empty_environment() -> dict[str, str]:
    return {field: "" for field in sorted(ENVIRONMENT_FIELDS)}


def pending_review(**bindings: Any) -> dict[str, Any]:
    review: dict[str, Any] = {
        "result": "pending",
        "role": "",
        "review_date": "",
        "notes": "",
    }
    review.update(bindings)
    return review


def load_render_profile(root: Path) -> tuple[dict[str, Any], str]:
    path = root / RENDER_PROFILE
    profile = read_json_object(path, "render review profile")
    if path.read_bytes() != canonical_json_bytes(profile):
        raise ParityError("render review profile must use canonical JSON")
    if set(profile) != {
        "schema_version",
        "targets",
        "accessibility_checks",
        "bidi_checks",
        "global_assets",
    } or profile.get("schema_version") != 1:
        raise ParityError("unsupported or malformed render review profile")
    targets = profile.get("targets")
    if not isinstance(targets, list) or len(targets) != 3:
        raise ParityError("render review profile must declare exactly three targets")
    expected_targets = (
        ("narrow", 320, 568, 100),
        ("wide", 1280, 800, 100),
        ("reflow-200", 320, 568, 200),
    )
    observed_targets: list[tuple[Any, Any, Any, Any]] = []
    for target in targets:
        if not isinstance(target, dict) or set(target) != {
            "id",
            "width",
            "height",
            "zoom_percent",
        }:
            raise ParityError("malformed render review target")
        observed_targets.append(
            (
                target.get("id"),
                target.get("width"),
                target.get("height"),
                target.get("zoom_percent"),
            )
        )
    if tuple(observed_targets) != expected_targets:
        raise ParityError("render review targets do not match the publication matrix")
    for field in ("accessibility_checks", "bidi_checks"):
        checks = profile.get(field)
        if (
            not isinstance(checks, list)
            or not checks
            or any(not isinstance(item, str) or not item.strip() for item in checks)
            or len(set(checks)) != len(checks)
        ):
            raise ParityError(f"render review profile has malformed {field}")
    assets = profile.get("global_assets")
    if (
        not isinstance(assets, list)
        or assets != sorted(assets)
        or len(set(assets)) != len(assets)
        or any(not isinstance(item, str) or not item for item in assets)
    ):
        raise ParityError("render review profile has malformed global_assets")
    for asset in assets:
        candidate = safe_repository_path(root, asset, "render asset path")
        if not candidate.is_file() or candidate.is_symlink():
            raise ParityError("render review profile references a missing or unsafe asset")
    return profile, digest(path)


def render_assets(root: Path, profile: dict[str, Any]) -> list[dict[str, str]]:
    assets: list[dict[str, str]] = []
    for relative in profile["global_assets"]:
        candidate = safe_repository_path(root, relative, "render asset path")
        if not candidate.is_file() or candidate.is_symlink():
            raise ParityError("render review profile references a missing or unsafe asset")
        assets.append({"path": relative, "sha256": digest(candidate)})
    return assets


def render_input_sha256(
    path: str,
    page_sha256: str,
    profile_sha256: str,
    assets: Sequence[dict[str, str]],
    environment: dict[str, str],
) -> str:
    return hashlib.sha256(
        canonical_json_bytes(
            {
                "path": path,
                "page_sha256": page_sha256,
                "profile_sha256": profile_sha256,
                "assets": list(assets),
                "environment": environment,
            }
        )
    ).hexdigest()


def pending_render_review(
    page_sha256: str,
    profile_sha256: str,
    *,
    canonical_sha256: str | None = None,
    localized_sha256: str | None = None,
) -> dict[str, Any]:
    bindings: dict[str, Any] = {
        "page_sha256": page_sha256,
        "profile_sha256": profile_sha256,
        "render_input_sha256": "",
        "environment": empty_environment(),
    }
    if canonical_sha256 is not None:
        bindings["canonical_sha256"] = canonical_sha256
    if localized_sha256 is not None:
        bindings["localized_sha256"] = localized_sha256
    return pending_review(**bindings)


def read_attribution_inventory(root: Path) -> dict[str, Any]:
    path = root / ATTRIBUTIONS
    try:
        with path.open("rb") as stream:
            payload = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ParityError("malformed attribution inventory") from exc
    if set(payload) != {"schema_version", "entries"} or payload.get(
        "schema_version"
    ) != 1:
        raise ParityError("unsupported or malformed attribution inventory schema")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ParityError("attribution entries must be a list")
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - validate_book.ATTRIBUTION_ENTRY_FIELDS:
            raise ParityError("attribution entry contains unknown fields")
        identifier = entry.get("id")
        paths = entry.get("paths")
        if (
            not isinstance(identifier, str)
            or not identifier
            or identifier in seen_ids
            or not isinstance(paths, list)
            or not paths
            or any(not isinstance(item, str) or not item for item in paths)
        ):
            raise ParityError("malformed attribution entry identity or paths")
        seen_ids.add(identifier)
        normalized = sorted(paths)
        if len(set(normalized)) != len(normalized):
            raise ParityError("attribution entry contains duplicate paths")
        for covered in normalized:
            if covered in seen_paths:
                raise ParityError("attribution path is covered by multiple entries")
            seen_paths.add(covered)
            candidate = safe_repository_path(root, covered, "attribution evidence path")
            if not candidate.exists() or candidate.is_symlink():
                raise ParityError("attribution evidence path is missing or unsafe")
        status = entry.get("status")
        if status == "review-required":
            continue
        if status not in RESOLVED_PROVENANCE_STATES:
            raise ParityError("attribution entry has an unknown review status")
        if status == "original-declared":
            required_fields = {"declaration", "review_date", "review_role"}
        else:
            required_fields = {
                "source_title",
                "source_url",
                "author_or_holder",
                "license",
                "required_notice",
                "notice_location",
                "adaptation",
                "review_date",
                "review_role",
            }
        if any(
            not isinstance(entry.get(field), str) or not entry[field].strip()
            for field in required_fields
        ):
            raise ParityError(
                "resolved attribution entry lacks human-reviewed evidence"
            )
        if status != "original-declared":
            source_url = urlsplit(entry["source_url"])
            if source_url.scheme not in {"http", "https"} or not source_url.netloc:
                raise ParityError("resolved attribution entry has an invalid source URL")
            notice_path = safe_repository_path(
                root, entry["notice_location"], "attribution notice path"
            )
            if not notice_path.is_file() or notice_path.is_symlink():
                raise ParityError("attribution notice path is missing or unsafe")
            try:
                notice_text = notice_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ParityError("attribution notice cannot be verified") from exc
            if entry["required_notice"] not in notice_text:
                raise ParityError("required attribution notice is not present")
    return payload


def provenance_reference(
    root: Path, inventory_schema_version: int, entry: dict[str, Any]
) -> dict[str, Any]:
    normalized_entry = dict(entry)
    normalized_entry["paths"] = sorted(entry["paths"])
    evidence = []
    for relative in normalized_entry["paths"]:
        candidate = safe_repository_path(root, relative, "attribution evidence path")
        if not candidate.is_file() or candidate.is_symlink():
            raise ParityError("attribution evidence path is missing or unsafe")
        evidence.append({"path": relative, "sha256": digest(candidate)})
    evidence.sort(key=lambda item: item["path"])
    provenance_sha256 = hashlib.sha256(
        canonical_json_bytes(
            {
                "inventory_schema_version": inventory_schema_version,
                "entry": normalized_entry,
                "evidence": evidence,
            }
        )
    ).hexdigest()
    return {
        "id": entry["id"],
        "status": entry.get("status", ""),
        "provenance_sha256": provenance_sha256,
        "covered_paths": normalized_entry["paths"],
    }


def provenance_references(root: Path) -> list[dict[str, Any]]:
    inventory = read_attribution_inventory(root)
    references = [
        provenance_reference(root, inventory["schema_version"], entry)
        for entry in inventory["entries"]
    ]
    return sorted(references, key=lambda item: item["id"])


def unit_provenance_references(
    root: Path,
    unit: str,
    references: Sequence[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    prefix = f"{unit}/"
    return [
        reference
        for reference in (
            references if references is not None else provenance_references(root)
        )
        if any(path.startswith(prefix) for path in reference["covered_paths"])
    ]


def source_provenance_references(
    root: Path,
    unit: str,
    references: Sequence[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    localized_paths = {f"{unit}/{filename}" for filename in LOCALES.values()}
    return [
        reference
        for reference in unit_provenance_references(root, unit, references)
        if any(path not in localized_paths for path in reference["covered_paths"])
    ]


def locale_provenance_references(
    root: Path,
    unit: str,
    locale: str,
    references: Sequence[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    localized_path = f"{unit}/{LOCALES[locale]}"
    return [
        reference
        for reference in unit_provenance_references(root, unit, references)
        if localized_path in reference["covered_paths"]
    ]


def root_provenance_references(
    root: Path,
    profile: dict[str, Any],
    references: Sequence[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    root_targets = {*ROOT_PATHS, "LICENSE", *profile["global_assets"]}
    for relative in ROOT_PATHS:
        source = root / relative
        scan = validate_book.scan_markdown(source, root, {})
        for is_image, _label, target, _line in scan.links:
            parsed = urlsplit(target.strip().strip("<>"))
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            try:
                resolved, _fragment = validate_book.resolve_local_target(
                    source, target, root
                )
            except validate_book.ConfigError as exc:
                raise ParityError("unsafe local target in root publication index") from exc
            if resolved.is_file() and (
                is_image
                or resolved.suffix.lower() != ".md"
                or resolved.name.upper() in {"LICENSE", "COPYING", "NOTICE"}
            ):
                root_targets.add(resolved.relative_to(root).as_posix())
    return [
        reference
        for reference in (
            references if references is not None else provenance_references(root)
        )
        if any(path in root_targets for path in reference["covered_paths"])
    ]


def build_pending_root_publication(root: Path) -> dict[str, Any]:
    profile, profile_sha256 = load_render_profile(root)
    all_provenance = provenance_references(root)
    canonical_sha256 = digest(root / "README.md")
    mirror_sha256 = digest(root / "README.en.md")
    if canonical_sha256 != mirror_sha256:
        raise ParityError("root English mirrors are not byte-identical")
    pages: list[dict[str, Any]] = []
    for relative in ROOT_PATHS:
        page_path = safe_repository_path(root, relative, "root publication path")
        if not page_path.is_file() or page_path.is_symlink():
            raise ParityError("root publication path is missing or unsafe")
        page_sha256 = digest(page_path)
        page: dict[str, Any] = {
            "path": relative,
            "sha256": page_sha256,
            "rendered_accessibility_review": pending_render_review(
                page_sha256, profile_sha256
            ),
        }
        if relative in LOCALIZED_ROOT_PATHS:
            page["linguistic_review"] = pending_review(
                canonical_sha256=canonical_sha256,
                localized_sha256=page_sha256,
            )
            page["technical_review"] = pending_review(
                canonical_sha256=canonical_sha256,
                localized_sha256=page_sha256,
            )
        if relative == "README.ar.md":
            page["bidi_review"] = pending_render_review(
                page_sha256,
                profile_sha256,
                canonical_sha256=canonical_sha256,
                localized_sha256=page_sha256,
            )
        pages.append(page)
    return {
        "state": "pending",
        "canonical_review": pending_review(
            canonical_sha256=canonical_sha256,
            mirror_sha256=mirror_sha256,
        ),
        "pages": pages,
        "provenance": root_provenance_references(
            root, profile, all_provenance
        ),
    }


def bind_legacy_review(
    review: Any, canonical_sha256: str, localized_sha256: str
) -> dict[str, Any]:
    if (
        not isinstance(review, dict)
        or set(review) != REVIEW_BASE_FIELDS
        or review.get("result") not in REVIEW_RESULTS
        or any(not isinstance(review.get(field), str) for field in REVIEW_BASE_FIELDS - {"result"})
    ):
        return pending_review(
            canonical_sha256=canonical_sha256,
            localized_sha256=localized_sha256,
        )
    if review["result"] in {"approved", "changes-requested"} and any(
        not review[field].strip() for field in ("role", "review_date", "notes")
    ):
        return pending_review(
            canonical_sha256=canonical_sha256,
            localized_sha256=localized_sha256,
        )
    return {
        **review,
        "canonical_sha256": canonical_sha256,
        "localized_sha256": localized_sha256,
    }


def map_v1_to_v2(payload: dict[str, Any], root: Path) -> dict[str, Any]:
    if payload.get("schema_version") != LEGACY_SCHEMA_VERSION:
        raise ParityError("review-schema migration requires a schema-v1 aggregate")
    validate_manifest(payload, root)
    _profile, profile_sha256 = load_render_profile(root)
    all_provenance = provenance_references(root)
    sources: list[dict[str, Any]] = []
    for source in payload["sources"]:
        sources.append(
            {
                "unit": source["unit"],
                "path": source["path"],
                "sha256": source["sha256"],
                "signals": source["signals"],
                "provenance": source_provenance_references(
                    root, source["unit"], all_provenance
                ),
                "canonical_review": pending_review(
                    canonical_sha256=source["sha256"]
                ),
                "rendered_accessibility_review": pending_render_review(
                    source["sha256"], profile_sha256
                ),
            }
        )
    records: list[dict[str, Any]] = []
    for record in payload["records"]:
        linguistic_review = bind_legacy_review(
            record.get("linguistic_review"),
            record["canonical_sha256"],
            record["localized_sha256"],
        )
        technical_review = bind_legacy_review(
            record.get("technical_review"),
            record["canonical_sha256"],
            record["localized_sha256"],
        )
        mapped = {
            key: value
            for key, value in record.items()
            if key not in {"linguistic_review", "technical_review"}
        }
        if mapped.get("status") in {
            "linguistic-reviewed",
            "technical-reviewed",
            "accepted",
        }:
            mapped["status"] = "human-review-in-progress"
        human_results = {
            linguistic_review["result"], technical_review["result"]
        }
        human_progress = (
            "approved" in human_results
            or any(value != "pending" for value in record["contract"].values())
            or bool(record["exceptions"])
        )
        if "changes-requested" in human_results:
            mapped["status"] = "blocked"
        elif human_progress and mapped["status"] not in {"stale", "blocked"}:
            mapped["status"] = "human-review-in-progress"
        elif mapped["status"] == "human-review-in-progress":
            mapped["status"] = "drafted"
        mapped["provenance"] = locale_provenance_references(
            root, record["unit"], record["locale"], all_provenance
        )
        mapped["linguistic_review"] = linguistic_review
        mapped["technical_review"] = technical_review
        mapped["rendered_accessibility_review"] = pending_render_review(
            record["localized_sha256"],
            profile_sha256,
            canonical_sha256=record["canonical_sha256"],
            localized_sha256=record["localized_sha256"],
        )
        if record["locale"] == "ar":
            mapped["bidi_review"] = pending_render_review(
                record["localized_sha256"],
                profile_sha256,
                canonical_sha256=record["canonical_sha256"],
                localized_sha256=record["localized_sha256"],
            )
        records.append(mapped)
    return {
        "schema_version": SCHEMA_VERSION,
        "notice": payload["notice"],
        "sources": sources,
        "records": records,
        "root_publication": build_pending_root_publication(root),
    }


def validate_review_object(
    review: Any,
    label: str,
    expected_bindings: dict[str, str],
) -> None:
    expected_fields = REVIEW_BASE_FIELDS | set(expected_bindings)
    if (
        not isinstance(review, dict)
        or set(review) != expected_fields
        or review.get("result") not in REVIEW_RESULTS
        or any(
            not isinstance(review.get(field), str)
            for field in expected_fields
        )
    ):
        raise ParityError(f"malformed {label}")
    if any(review.get(key) != value for key, value in expected_bindings.items()):
        raise ParityError(f"stale {label}")
    if review["result"] in {"approved", "changes-requested"} and any(
        not review[field].strip() for field in ("role", "review_date", "notes")
    ):
        raise ParityError(f"incomplete {label}")


def validate_render_review(
    review: Any,
    label: str,
    *,
    root: Path,
    path: str,
    page_sha256: str,
    profile: dict[str, Any],
    profile_sha256: str,
    extra_bindings: dict[str, str] | None = None,
) -> None:
    extra_bindings = extra_bindings or {}
    expected_fields = REVIEW_BASE_FIELDS | {
        "page_sha256",
        "profile_sha256",
        "render_input_sha256",
        "environment",
        *extra_bindings,
    }
    if not isinstance(review, dict) or set(review) != expected_fields:
        raise ParityError(f"malformed {label}")
    if review.get("result") not in REVIEW_RESULTS or any(
        not isinstance(review.get(field), str)
        for field in REVIEW_BASE_FIELDS | {
            "page_sha256",
            "profile_sha256",
            "render_input_sha256",
        }
        | set(extra_bindings)
    ):
        raise ParityError(f"malformed {label}")
    environment = review.get("environment")
    if (
        not isinstance(environment, dict)
        or set(environment) != ENVIRONMENT_FIELDS
        or any(not isinstance(value, str) for value in environment.values())
    ):
        raise ParityError(f"malformed {label} environment")
    if (
        review.get("page_sha256") != page_sha256
        or review.get("profile_sha256") != profile_sha256
        or any(review.get(key) != value for key, value in extra_bindings.items())
    ):
        raise ParityError(f"stale {label}")
    result = review["result"]
    if result == "pending":
        if review["render_input_sha256"] or any(environment.values()):
            raise ParityError(f"pending {label} contains fabricated render evidence")
        return
    if any(not review[field].strip() for field in ("role", "review_date", "notes")):
        raise ParityError(f"incomplete {label}")
    if any(not environment[field].strip() for field in ENVIRONMENT_FIELDS):
        raise ParityError(f"incomplete {label} environment")
    expected_input = render_input_sha256(
        path,
        page_sha256,
        profile_sha256,
        render_assets(root, profile),
        environment,
    )
    if review["render_input_sha256"] != expected_input:
        raise ParityError(f"stale {label} render input")


def render_review_is_current(
    review: Any,
    *,
    root: Path,
    path: str,
    page_sha256: str,
    profile: dict[str, Any],
    profile_sha256: str,
    extra_bindings: dict[str, str] | None = None,
) -> bool:
    """Return whether reusable human render evidence still binds every input."""

    try:
        validate_render_review(
            review,
            "previous rendered review",
            root=root,
            path=path,
            page_sha256=page_sha256,
            profile=profile,
            profile_sha256=profile_sha256,
            extra_bindings=extra_bindings,
        )
    except ParityError:
        return False
    return True


def validate_provenance_reference(reference: Any, label: str) -> None:
    if (
        not isinstance(reference, dict)
        or set(reference) != {
            "id",
            "status",
            "provenance_sha256",
            "covered_paths",
        }
        or not isinstance(reference.get("id"), str)
        or not reference["id"]
        or not isinstance(reference.get("status"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", str(reference.get("provenance_sha256")))
        or not isinstance(reference.get("covered_paths"), list)
        or reference["covered_paths"] != sorted(reference["covered_paths"])
        or any(not isinstance(path, str) or not path for path in reference["covered_paths"])
    ):
        raise ParityError(f"malformed {label}")


def validate_provenance_bindings(
    references: Any,
    label: str,
    expected: list[dict[str, Any]],
) -> None:
    if not isinstance(references, list):
        raise ParityError(f"malformed {label}")
    for reference in references:
        validate_provenance_reference(reference, label)
    if references != expected:
        raise ParityError(f"stale {label}")


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


def root_leaf_path(store: Path) -> Path:
    return store / ROOT_PUBLICATION_LEAF


def leaf_payload(
    kind: str, value: dict[str, Any], *, schema_version: int = LEAF_SCHEMA_VERSION
) -> dict[str, Any]:
    return {"schema_version": schema_version, kind: value}


def root_leaf_payload(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": LEAF_SCHEMA_VERSION,
        "leaf_kind": "root-publication",
        "root_publication": value,
    }


def expected_unit_leaf_paths(store: Path, units: Sequence[str]) -> set[Path]:
    paths = {source_leaf_path(store, unit) for unit in units}
    paths.update(
        record_leaf_path(store, unit, locale)
        for unit in units
        for locale in LOCALES
    )
    return paths


def expected_leaf_paths(
    store: Path, units: Sequence[str], leaf_schema_version: int
) -> set[Path]:
    paths = expected_unit_leaf_paths(store, units)
    if leaf_schema_version == LEAF_SCHEMA_VERSION:
        paths.add(root_leaf_path(store))
    return paths


def inspect_partition_store(
    index: dict[str, Any],
    root: Path,
    *,
    expected_units: Sequence[str] | None = None,
    store_override: Path | None = None,
) -> tuple[list[str], Path, int]:
    units, declared_store = validate_index(index, root, expected_units)
    store = store_override if store_override else declared_store
    try:
        validate_book.safe_relative(store, root)
    except validate_book.ConfigError as exc:
        raise ParityError("partition store escapes repository") from exc
    if not store.is_dir() or store.is_symlink():
        raise ParityError("partition store is missing or unsafe")

    unit_paths = expected_unit_leaf_paths(store, units)
    allowed = {*unit_paths, root_leaf_path(store)}
    actual: set[Path] = set()
    for candidate in store.rglob("*"):
        if candidate.is_symlink():
            raise ParityError(f"partition store contains symlink under {STORE_ROOT}")
        if candidate.is_file():
            actual.add(candidate)
    missing_units = sorted(
        path.relative_to(root).as_posix() for path in unit_paths - actual
    )
    if missing_units:
        raise ParityError(f"partition store is missing evidence: {missing_units[0]}")
    if actual - allowed:
        raise ParityError(f"partition store contains extra evidence under {STORE_ROOT}")

    observed_versions: dict[str, Any] = {}
    for path in sorted(unit_paths):
        label = (
            "localized record leaf"
            if RECORD_STORE in path.parts
            else "canonical source leaf"
        )
        leaf = read_json_object(path, label)
        observed_versions[path.relative_to(root).as_posix()] = leaf.get(
            "schema_version"
        )
    versions = set(observed_versions.values())
    if len(versions) != 1 or next(iter(versions)) not in {
        LEGACY_LEAF_SCHEMA_VERSION,
        LEAF_SCHEMA_VERSION,
    }:
        representatives: dict[Any, str] = {}
        for relative, version in sorted(observed_versions.items()):
            representatives.setdefault(version, relative)
        details = ", ".join(
            f"{relative}=schema-{version}"
            for version, relative in sorted(
                representatives.items(), key=lambda item: str(item[0])
            )
        )
        raise ParityError(
            "partition store mixes or has unsupported leaf schema versions: "
            f"{details}"
        )
    leaf_schema_version = int(next(iter(versions)))
    root_exists = root_leaf_path(store) in actual
    if (leaf_schema_version == LEGACY_LEAF_SCHEMA_VERSION and root_exists) or (
        leaf_schema_version == LEAF_SCHEMA_VERSION and not root_exists
    ):
        root_relative = root_leaf_path(store).relative_to(root).as_posix()
        root_state = "present" if root_exists else "missing"
        raise ParityError(
            "partition store mixes leaf schema and root topology: "
            f"{root_relative} is {root_state} for leaf schema "
            f"{leaf_schema_version}"
        )
    return units, store, leaf_schema_version


def load_partition_store(
    index: dict[str, Any],
    root: Path,
    *,
    expected_units: Sequence[str] | None = None,
    store_override: Path | None = None,
    required_leaf_version: int | None = None,
) -> dict[str, Any]:
    units, store, leaf_schema_version = inspect_partition_store(
        index,
        root,
        expected_units=expected_units,
        store_override=store_override,
    )
    if (
        required_leaf_version is not None
        and leaf_schema_version != required_leaf_version
    ):
        raise ParityError("partition store leaf schema does not match the requested operation")

    sources: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for unit in units:
        source_path = source_leaf_path(store, unit)
        source_leaf = read_json_object(source_path, "canonical source leaf")
        if source_path.read_bytes() != canonical_json_bytes(source_leaf):
            raise ParityError(f"non-canonical canonical source leaf: {unit}")
        if set(source_leaf) != {"schema_version", "source"} or source_leaf.get(
            "schema_version"
        ) != leaf_schema_version:
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
            ) != leaf_schema_version:
                raise ParityError(f"malformed localized record leaf: {unit}:{locale}")
            record = record_leaf.get("record")
            if (
                not isinstance(record, dict)
                or record.get("unit") != unit
                or record.get("locale") != locale
            ):
                raise ParityError(f"localized record leaf identity mismatch: {unit}:{locale}")
            records.append(record)
    aggregate = {
        "schema_version": leaf_schema_version,
        "notice": index["notice"],
        "sources": sources,
        "records": records,
    }
    if leaf_schema_version == LEAF_SCHEMA_VERSION:
        path = root_leaf_path(store)
        root_leaf = read_json_object(path, "root publication leaf")
        if path.read_bytes() != canonical_json_bytes(root_leaf):
            raise ParityError("non-canonical root publication leaf")
        if set(root_leaf) != {
            "schema_version",
            "leaf_kind",
            "root_publication",
        } or root_leaf.get("schema_version") != LEAF_SCHEMA_VERSION or root_leaf.get(
            "leaf_kind"
        ) != "root-publication":
            raise ParityError("malformed root publication leaf")
        root_publication = root_leaf.get("root_publication")
        if not isinstance(root_publication, dict):
            raise ParityError("root publication leaf must contain an object")
        aggregate["root_publication"] = root_publication
    return aggregate


def load_manifest(
    path: Path, root: Path, expected_units: Sequence[str] | None = None
) -> dict[str, Any]:
    payload = read_json_object(path, "parity manifest")
    version = payload.get("schema_version")
    if version == LEGACY_SCHEMA_VERSION and {"sources", "records"} <= set(payload):
        return payload
    if version == INDEX_SCHEMA_VERSION and "store_root" in payload:
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
    version = payload.get("schema_version")
    if version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
        raise ParityError("unsupported aggregate schema_version")
    ordered = {
        "schema_version": version,
        "notice": payload.get("notice"),
        "sources": [source_map[unit] for unit in units],
        "records": [record_map[(unit, locale)] for unit in units for locale in LOCALES],
    }
    if version == SCHEMA_VERSION:
        root_publication = payload.get("root_publication")
        if not isinstance(root_publication, dict):
            raise ParityError("schema-v2 aggregate lacks root publication evidence")
        ordered["root_publication"] = root_publication
    return ordered


def partition_files(
    payload: dict[str, Any], units: Sequence[str], store: Path
) -> dict[Path, bytes]:
    source_map, record_map = aggregate_maps(payload, units)
    version = payload.get("schema_version")
    if version not in {LEGACY_SCHEMA_VERSION, SCHEMA_VERSION}:
        raise ParityError("unsupported aggregate schema_version")
    leaf_version = (
        LEGACY_LEAF_SCHEMA_VERSION
        if version == LEGACY_SCHEMA_VERSION
        else LEAF_SCHEMA_VERSION
    )
    files = {
        source_leaf_path(store, unit): canonical_json_bytes(
            leaf_payload("source", source_map[unit], schema_version=leaf_version)
        )
        for unit in units
    }
    files.update(
        {
            record_leaf_path(store, unit, locale): canonical_json_bytes(
                leaf_payload(
                    "record",
                    record_map[(unit, locale)],
                    schema_version=leaf_version,
                )
            )
            for unit in units
            for locale in LOCALES
        }
    )
    if version == SCHEMA_VERSION:
        root_publication = payload.get("root_publication")
        if not isinstance(root_publication, dict):
            raise ParityError("schema-v2 aggregate lacks root publication evidence")
        files[root_leaf_path(store)] = canonical_json_bytes(
            root_leaf_payload(root_publication)
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
    if legacy.get("schema_version") != LEGACY_SCHEMA_VERSION:
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


def store_snapshot(store: Path) -> dict[str, tuple[str, bytes]]:
    """Capture every directory entry without following symlinks."""

    snapshot: dict[str, tuple[str, bytes]] = {}
    for path in sorted(store.rglob("*")):
        relative = path.relative_to(store).as_posix()
        if path.is_symlink():
            target = os.readlink(path).encode("utf-8", "surrogateescape")
            snapshot[relative] = ("symlink", target)
        elif path.is_dir():
            snapshot[relative] = ("directory", b"")
        elif path.is_file():
            snapshot[relative] = ("file", path.read_bytes())
        else:
            snapshot[relative] = ("other", b"")
    return snapshot


def verify_store_snapshot(
    store: Path, snapshot: dict[str, tuple[str, bytes]]
) -> None:
    observed = store_snapshot(store)
    if observed != snapshot:
        raise ParityError("partition store changed during review-schema migration")


def migrate_review_schema(path: Path, root: Path) -> list[str]:
    index_bytes = path.read_bytes()
    index = read_json_object(path, "parity index")
    if path.read_bytes() != canonical_json_bytes(index):
        raise ParityError("parity index is non-canonical or changed while loading")
    units, store, leaf_schema_version = inspect_partition_store(
        index, root, expected_units=expected_unit_ids(root)
    )
    recoveries = sorted(store.parent.glob(".parity-review-v2.*"))
    if recoveries:
        relative = recoveries[0].relative_to(root).as_posix()
        raise AtomicRecoveryError(
            f"review-schema recovery store requires manual resolution: {relative}"
        )
    if leaf_schema_version == LEAF_SCHEMA_VERSION:
        current = load_partition_store(
            index,
            root,
            expected_units=units,
            required_leaf_version=LEAF_SCHEMA_VERSION,
        )
        validate_manifest(current, root)
        return []
    if leaf_schema_version != LEGACY_LEAF_SCHEMA_VERSION:
        raise ParityError("unsupported review-schema migration source")

    legacy = load_partition_store(
        index,
        root,
        expected_units=units,
        required_leaf_version=LEGACY_LEAF_SCHEMA_VERSION,
    )
    validate_manifest(legacy, root)
    original_snapshot = store_snapshot(store)
    migrated = map_v1_to_v2(legacy, root)
    validate_manifest(migrated, root)

    staging = Path(
        tempfile.mkdtemp(prefix=".parity-review-v2.", dir=store.parent)
    )
    exchanged = False
    retain_recovery = False
    try:
        write_partition_store(staging, migrated, units, owned=True)
        staged = load_partition_store(
            index,
            root,
            expected_units=units,
            store_override=staging,
            required_leaf_version=LEAF_SCHEMA_VERSION,
        )
        validate_manifest(staged, root)
        if canonical_json_bytes(ordered_aggregate(staged, units)) != canonical_json_bytes(
            ordered_aggregate(migrated, units)
        ):
            raise ParityError("staged review-schema store does not match migration plan")
        if path.read_bytes() != index_bytes:
            raise ParityError("parity index changed during review-schema migration")
        verify_store_snapshot(store, original_snapshot)
        linux_renameat2(staging, store, RENAME_EXCHANGE)
        exchanged = True
        retained_v1 = store_snapshot(staging)
        if retained_v1 != original_snapshot:
            raise ParityError(
                "partition store changed during atomic review-schema publication"
            )
        if path.read_bytes() != index_bytes:
            raise ParityError("parity index changed during atomic review-schema publication")
        published = load_partition_store(
            index,
            root,
            expected_units=units,
            required_leaf_version=LEAF_SCHEMA_VERSION,
        )
        validate_manifest(published, root)
        if canonical_json_bytes(ordered_aggregate(published, units)) != canonical_json_bytes(
            ordered_aggregate(migrated, units)
        ):
            raise ParityError("published review-schema store differs from staged evidence")
        shutil.rmtree(staging)
        exchanged = False
        return sorted(
            target.relative_to(root).as_posix()
            for target in expected_leaf_paths(store, units, LEAF_SCHEMA_VERSION)
        )
    except Exception as original_error:
        if exchanged:
            recovery_relative = staging.relative_to(root).as_posix()
            retained_snapshot: dict[str, tuple[str, bytes]] | None = None
            try:
                retained_snapshot = store_snapshot(staging)
                linux_renameat2(staging, store, RENAME_EXCHANGE)
                exchanged = False
                verify_store_snapshot(store, retained_snapshot)
            except Exception as rollback_error:
                retain_recovery = True
                raise AtomicRecoveryError(
                    "review-schema rollback failed; retained recovery store: "
                    f"{recovery_relative}"
                ) from rollback_error
        raise original_error
    finally:
        if (
            not retain_recovery
            and staging.exists()
            and not staging.is_symlink()
        ):
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
    _units, _store, leaf_schema_version = inspect_partition_store(
        index, root, expected_units=units
    )
    if leaf_schema_version == LEAF_SCHEMA_VERSION:
        raise ParityError(
            "--export-monolith cannot represent leaf schema 2; "
            "use --export-review-bundle"
        )
    aggregate = load_partition_store(
        index,
        root,
        expected_units=units,
        required_leaf_version=LEGACY_LEAF_SCHEMA_VERSION,
    )
    validate_manifest(aggregate, root)
    data = canonical_json_bytes(ordered_aggregate(aggregate, units))
    atomic_write(output, data, refuse_conflict=True)
    if output.read_bytes() != data:
        raise ParityError("monolith export failed byte verification")


def export_review_bundle(path: Path, output: Path, root: Path) -> None:
    index = read_json_object(path, "parity index")
    if index.get("schema_version") != INDEX_SCHEMA_VERSION:
        raise ParityError("--export-review-bundle requires a schema-v2 parity index")
    output = output.resolve(strict=False)
    try:
        validate_book.safe_relative(output, root)
    except validate_book.ConfigError as exc:
        raise ParityError("review bundle export path escapes repository") from exc
    live_store = (root / STORE_ROOT).resolve(strict=False)
    if output == path.resolve(strict=False) or output == live_store or live_store in output.parents:
        raise ParityError("review bundle export must not replace live partition storage")
    units = expected_unit_ids(root)
    aggregate = load_partition_store(
        index,
        root,
        expected_units=units,
        required_leaf_version=LEAF_SCHEMA_VERSION,
    )
    validate_manifest(aggregate, root)
    ordered = ordered_aggregate(aggregate, units)
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "index": index,
        "sources": ordered["sources"],
        "records": ordered["records"],
        "root_publication": ordered["root_publication"],
    }
    data = canonical_json_bytes(bundle)
    atomic_write(output, data, refuse_conflict=True)
    if output.read_bytes() != data:
        raise ParityError("review bundle export failed byte verification")


def load_v2_evidence(root: Path) -> tuple[Path, dict[str, Any], list[str], Path, dict[str, Any]]:
    index_path = root / MANIFEST
    index = read_json_object(index_path, "parity index")
    units, store = validate_index(index, root, expected_unit_ids(root))
    aggregate = load_partition_store(
        index,
        root,
        expected_units=units,
        required_leaf_version=LEAF_SCHEMA_VERSION,
    )
    validate_manifest(aggregate, root)
    return index_path, index, units, store, aggregate


def evidence_projection(path: Path, root: Path, value: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_path": path.relative_to(root).as_posix(),
        "evidence_sha256": digest(path),
        "value": value,
    }


def build_unit_review_packet(root: Path, unit: str) -> dict[str, Any]:
    if re.fullmatch(r"(?:chapter|appendix)-[a-z0-9][a-z0-9-]*", unit) is None:
        raise ParityError("unsafe review packet unit")
    index_path, index, units, store, aggregate = load_v2_evidence(root)
    if unit not in units:
        raise ParityError("unknown review packet unit")
    source_map, record_map = aggregate_maps(aggregate, units)
    profile, profile_sha256 = load_render_profile(root)
    attribution_path = root / ATTRIBUTIONS
    references = unit_provenance_references(root, unit)
    return {
        "packet_kind": "unit-review",
        "packet_schema_version": 1,
        "unit": unit,
        "index": {
            "path": index_path.relative_to(root).as_posix(),
            "sha256": digest(index_path),
        },
        "canonical_source": evidence_projection(
            source_leaf_path(store, unit), root, source_map[unit]
        ),
        "localized_records": [
            evidence_projection(
                record_leaf_path(store, unit, locale),
                root,
                record_map[(unit, locale)],
            )
            for locale in LOCALES
        ],
        "render_profile": {
            "path": RENDER_PROFILE,
            "sha256": profile_sha256,
            "assets": render_assets(root, profile),
            "value": profile,
        },
        "provenance": {
            "authority_path": ATTRIBUTIONS,
            "authority_sha256": digest(attribution_path),
            "references": references,
        },
        "required_automated_commands": [
            "python -B tools/validate_book.py",
            "python -B tools/parity_review.py",
        ],
    }


def decision_reference(
    decision_id: str, path: str, review: dict[str, Any]
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "path": path,
        "decision_sha256": hashlib.sha256(
            canonical_json_bytes(
                {"decision_id": decision_id, "path": path, "review": review}
            )
        ).hexdigest(),
    }


def root_decision_references(root_publication: dict[str, Any]) -> list[dict[str, str]]:
    decisions = [
        decision_reference(
            "root:README.md:canonical",
            "README.md",
            root_publication["canonical_review"],
        )
    ]
    for page in root_publication["pages"]:
        path = page["path"]
        decisions.append(
            decision_reference(
                f"root:{path}:rendered-accessibility",
                path,
                page["rendered_accessibility_review"],
            )
        )
        for field, gate in (
            ("linguistic_review", "linguistic"),
            ("technical_review", "technical"),
            ("bidi_review", "bidi"),
        ):
            if field in page:
                decisions.append(
                    decision_reference(
                        f"root:{path}:{gate}", path, page[field]
                    )
                )
    return sorted(decisions, key=lambda item: item["decision_id"])


def build_root_review_packet(root: Path) -> dict[str, Any]:
    index_path, _index, _units, store, aggregate = load_v2_evidence(root)
    profile, profile_sha256 = load_render_profile(root)
    root_publication = aggregate["root_publication"]
    return {
        "packet_kind": "root-publication-review",
        "packet_schema_version": 1,
        "index": {
            "path": index_path.relative_to(root).as_posix(),
            "sha256": digest(index_path),
        },
        "root_publication": evidence_projection(
            root_leaf_path(store), root, root_publication
        ),
        "decisions": root_decision_references(root_publication),
        "render_profile": {
            "path": RENDER_PROFILE,
            "sha256": profile_sha256,
            "assets": render_assets(root, profile),
            "value": profile,
        },
        "provenance": {
            "authority_path": ATTRIBUTIONS,
            "authority_sha256": digest(root / ATTRIBUTIONS),
            "references": root_provenance_references(root, profile),
        },
        "required_automated_commands": [
            "python -B tools/validate_book.py",
            "python -B tools/parity_review.py",
        ],
    }


QUALITY_CONTRACT_PATHS = (
    "BOOK_STYLE.md",
    "tools/parity_review.py",
    "tools/validate_book.py",
    "tools/run_quality.py",
    "tools/book_quality.toml",
    "tools/quality_matrix.toml",
)


def digest_reference_list(references: Sequence[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical_json_bytes(list(references))).hexdigest()


def publication_signoff_inputs(root: Path) -> dict[str, Any]:
    index_path, _index, units, store, aggregate = load_v2_evidence(root)
    all_provenance = provenance_references(root)
    unit_leaf_references = [
        {
            "path": path.relative_to(root).as_posix(),
            "sha256": digest(path),
        }
        for path in sorted(expected_unit_leaf_paths(store, units))
    ]
    unit_provenance: list[dict[str, Any]] = []
    for unit in units:
        for reference in unit_provenance_references(
            root, unit, all_provenance
        ):
            unit_provenance.append({"unit": unit, **reference})
    unit_provenance.sort(key=lambda item: (item["unit"], item["id"]))
    quality_contract = []
    for relative in sorted(QUALITY_CONTRACT_PATHS):
        path = safe_repository_path(root, relative, "quality contract path")
        if not path.is_file() or path.is_symlink():
            raise ParityError("quality contract path is missing or unsafe")
        quality_contract.append({"path": relative, "sha256": digest(path)})
    return {
        "attributions_sha256": digest(root / ATTRIBUTIONS),
        "parity_index_sha256": digest(index_path),
        "quality_contract_sha256": digest_reference_list(quality_contract),
        "render_profile_sha256": digest(root / RENDER_PROFILE),
        "root_decisions": [
            {
                "decision_id": reference["decision_id"],
                "decision_sha256": reference["decision_sha256"],
            }
            for reference in root_decision_references(
                aggregate["root_publication"]
            )
        ],
        "root_leaf_sha256": digest(root_leaf_path(store)),
        "unit_evidence_sha256": digest_reference_list(unit_leaf_references),
        "unit_provenance_sha256": digest_reference_list(unit_provenance),
    }


def signoff_input_sha256(inputs: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(inputs)).hexdigest()


def pending_publication_signoff(root: Path) -> dict[str, Any]:
    inputs = publication_signoff_inputs(root)
    input_sha256 = signoff_input_sha256(inputs)
    review = pending_review(signoff_input_sha256=input_sha256)
    return {
        "book_editor_review": dict(review),
        "accessibility_review": dict(review),
        "inputs": inputs,
        "provenance_review": dict(review),
        "schema_version": 1,
        "signoff_input_sha256": input_sha256,
        "state": "pending",
    }


def validate_signoff_review(
    review: Any, label: str, current_input_sha256: str
) -> None:
    expected_fields = REVIEW_BASE_FIELDS | {"signoff_input_sha256"}
    if (
        not isinstance(review, dict)
        or set(review) != expected_fields
        or review.get("result") not in REVIEW_RESULTS
        or any(not isinstance(review.get(field), str) for field in expected_fields)
    ):
        raise ParityError(f"malformed publication {label}")
    if review["signoff_input_sha256"] != current_input_sha256:
        raise PublicationIncompleteError(f"publication {label} is stale")
    if review["result"] in {"approved", "changes-requested"} and any(
        not review[field].strip() for field in ("role", "review_date", "notes")
    ):
        raise ParityError(f"incomplete publication {label}")


def verify_publication_signoff(root: Path, relative_path: str) -> None:
    path = safe_repository_path(root, relative_path, "publication sign-off path")
    if not path.is_file() or path.is_symlink():
        raise ParityError("publication sign-off is missing or unsafe")
    signoff = read_json_object(path, "publication sign-off")
    if path.read_bytes() != canonical_json_bytes(signoff):
        raise ParityError("publication sign-off must use canonical JSON")
    if set(signoff) != {
        "schema_version",
        "state",
        "inputs",
        "signoff_input_sha256",
        "book_editor_review",
        "accessibility_review",
        "provenance_review",
    } or signoff.get("schema_version") != 1 or signoff.get("state") not in {
        "pending",
        "changes-requested",
        "stale",
        "approved",
    }:
        raise ParityError("unsupported or malformed publication sign-off schema")
    try:
        current_inputs = publication_signoff_inputs(root)
    except ParityError as exc:
        if "stale" in str(exc).lower():
            raise PublicationIncompleteError(
                "publication sign-off upstream evidence is stale"
            ) from exc
        raise
    current_input_sha256 = signoff_input_sha256(current_inputs)
    if (
        signoff.get("inputs") != current_inputs
        or signoff.get("signoff_input_sha256") != current_input_sha256
    ):
        raise PublicationIncompleteError("publication sign-off inputs are stale")
    reviews = []
    for field, label in (
        ("book_editor_review", "book-editor review"),
        ("accessibility_review", "accessibility review"),
        ("provenance_review", "provenance review"),
    ):
        review = signoff[field]
        validate_signoff_review(review, label, current_input_sha256)
        reviews.append(review)
    _index_path, _index, _units, _store, aggregate = load_v2_evidence(root)
    try:
        validate_manifest(aggregate, root, require_accepted=True)
    except ParityError as exc:
        if str(exc).startswith("publication review incomplete"):
            raise PublicationIncompleteError(str(exc)) from exc
        raise
    if any(
        reference["status"] not in RESOLVED_PROVENANCE_STATES
        for reference in provenance_references(root)
    ):
        raise PublicationIncompleteError(
            "publication provenance review is incomplete"
        )
    if any(review["result"] != "approved" for review in reviews):
        raise PublicationIncompleteError("publication sign-off reviews are pending")
    if signoff["state"] != "approved":
        raise PublicationIncompleteError("publication sign-off state is not approved")


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


def build_legacy_manifest(
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
    if previous_payload is not None and previous_payload.get(
        "schema_version"
    ) != LEGACY_SCHEMA_VERSION:
        raise ParityError("legacy manifest refresh requires schema-v1 evidence")
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
        "schema_version": LEGACY_SCHEMA_VERSION,
        "notice": "Structural metrics are triage signals, never proof of semantic or linguistic parity.",
        "sources": sources,
        "records": records,
    }


def review_has_bindings(review: Any, expected: dict[str, str]) -> bool:
    return isinstance(review, dict) and all(
        review.get(key) == value for key, value in expected.items()
    )


def refresh_root_publication(
    root: Path, previous: dict[str, Any] | None
) -> dict[str, Any]:
    refreshed = build_pending_root_publication(root)
    profile, profile_sha256 = load_render_profile(root)
    if not isinstance(previous, dict):
        return refreshed
    try:
        previous_reviews = root_review_objects(previous)
    except (KeyError, TypeError) as exc:
        raise ParityError("malformed previous root publication evidence") from exc
    had_human_evidence = any(
        review.get("result") != "pending" for review in previous_reviews
    )
    inputs_changed = previous.get("provenance") != refreshed["provenance"]
    previous_pages = {
        page.get("path"): page
        for page in previous.get("pages", [])
        if isinstance(page, dict) and isinstance(page.get("path"), str)
    }
    canonical_bindings = {
        key: refreshed["canonical_review"][key]
        for key in ("canonical_sha256", "mirror_sha256")
    }
    if review_has_bindings(previous.get("canonical_review"), canonical_bindings):
        refreshed["canonical_review"] = previous["canonical_review"]
    else:
        inputs_changed = True
    for page in refreshed["pages"]:
        old = previous_pages.get(page["path"])
        if not isinstance(old, dict) or old.get("sha256") != page["sha256"]:
            inputs_changed = True
            continue
        for field in (
            "linguistic_review",
            "technical_review",
            "rendered_accessibility_review",
            "bidi_review",
        ):
            if field not in page or field not in old:
                continue
            if field in {"rendered_accessibility_review", "bidi_review"}:
                extra_bindings = None
                if field == "bidi_review":
                    extra_bindings = {
                        "canonical_sha256": refreshed["canonical_review"][
                            "canonical_sha256"
                        ],
                        "localized_sha256": page["sha256"],
                    }
                current = render_review_is_current(
                    old[field],
                    root=root,
                    path=page["path"],
                    page_sha256=page["sha256"],
                    profile=profile,
                    profile_sha256=profile_sha256,
                    extra_bindings=extra_bindings,
                )
            else:
                expected = {
                    key: value
                    for key, value in page[field].items()
                    if key in {"canonical_sha256", "localized_sha256"}
                }
                current = review_has_bindings(old[field], expected)
            if current:
                page[field] = old[field]
            else:
                inputs_changed = True
    reviews = root_review_objects(refreshed)
    if any(review.get("result") == "changes-requested" for review in reviews):
        refreshed["state"] = "blocked"
    elif inputs_changed and (
        had_human_evidence
        or previous.get("state")
        in {"human-review-in-progress", "accepted", "stale", "blocked"}
    ):
        refreshed["state"] = "stale"
    elif previous.get("state") == "stale":
        # A refresh never clears a stale human gate.  A maintainer must record
        # the repeated review explicitly in the authoritative root leaf.
        refreshed["state"] = "stale"
    elif all(review.get("result") == "approved" for review in reviews) and all(
        reference["status"] in RESOLVED_PROVENANCE_STATES
        for reference in refreshed["provenance"]
    ):
        refreshed["state"] = (
            "accepted"
            if previous.get("state") == "accepted"
            else "human-review-in-progress"
        )
    elif any(review.get("result") != "pending" for review in reviews):
        refreshed["state"] = "human-review-in-progress"
    return refreshed


def build_v2_manifest(root: Path, previous_payload: dict[str, Any]) -> dict[str, Any]:
    if previous_payload.get("schema_version") != SCHEMA_VERSION:
        raise ParityError("schema-v2 refresh requires schema-v2 evidence")
    config = validate_book.load_config(root)
    units = scoped_units(root, config)
    if len(units) != EXPECTED_CANONICAL_SOURCES:
        raise ParityError(
            f"expected {EXPECTED_CANONICAL_SOURCES} canonical units, found {len(units)}"
        )
    previous_sources, previous_records = aggregate_maps(
        previous_payload, [unit.name for unit in units]
    )
    profile, profile_sha256 = load_render_profile(root)
    all_provenance = provenance_references(root)
    sources: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for unit in units:
        canonical_path = unit / "README.md"
        canonical_sha256 = digest(canonical_path)
        canonical_signals = signals(canonical_path, root, config)
        old_source = previous_sources[unit.name]
        source_provenance = source_provenance_references(
            root, unit.name, all_provenance
        )
        source_provenance_changed = (
            old_source.get("provenance") != source_provenance
        )
        if old_source.get("sha256") == canonical_sha256:
            canonical_review = old_source.get("canonical_review")
            if not review_has_bindings(
                canonical_review, {"canonical_sha256": canonical_sha256}
            ):
                canonical_review = pending_review(
                    canonical_sha256=canonical_sha256
                )
            rendered_review = old_source.get("rendered_accessibility_review")
            if not render_review_is_current(
                rendered_review,
                root=root,
                path=canonical_path.relative_to(root).as_posix(),
                page_sha256=canonical_sha256,
                profile=profile,
                profile_sha256=profile_sha256,
            ):
                rendered_review = pending_render_review(
                    canonical_sha256, profile_sha256
                )
        else:
            canonical_review = pending_review(canonical_sha256=canonical_sha256)
            rendered_review = pending_render_review(
                canonical_sha256, profile_sha256
            )
        sources.append(
            {
                "unit": unit.name,
                "path": canonical_path.relative_to(root).as_posix(),
                "sha256": canonical_sha256,
                "signals": canonical_signals,
                "provenance": source_provenance,
                "canonical_review": canonical_review,
                "rendered_accessibility_review": rendered_review,
            }
        )
        for locale, filename in LOCALES.items():
            localized_path = unit / filename
            localized_sha256 = digest(localized_path)
            localized_signals = signals(localized_path, root, config)
            old = previous_records[(unit.name, locale)]
            locale_provenance = locale_provenance_references(
                root, unit.name, locale, all_provenance
            )
            provenance_changed = (
                source_provenance_changed
                or old.get("provenance") != locale_provenance
            )
            both_current = (
                old.get("canonical_sha256") == canonical_sha256
                and old.get("localized_sha256") == localized_sha256
            )
            if both_current:
                record = dict(old)
                record["signals"] = localized_signals
                record["priority"] = initial_priority(
                    locale, canonical_signals, localized_signals, unit.name
                )
                record["observed_gaps"] = gap_signals(
                    canonical_signals, localized_signals
                )
                record["provenance"] = locale_provenance
                if provenance_changed and record.get("status") in {
                    "human-review-in-progress",
                    "accepted",
                }:
                    record["status"] = "stale"
                bindings = {
                    "canonical_sha256": canonical_sha256,
                    "localized_sha256": localized_sha256,
                }
                for field in ("linguistic_review", "technical_review"):
                    if not review_has_bindings(record.get(field), bindings):
                        record[field] = pending_review(**bindings)
                render_fields = ["rendered_accessibility_review"]
                if locale == "ar":
                    render_fields.append("bidi_review")
                reset_render = False
                for field in render_fields:
                    if not render_review_is_current(
                        record.get(field),
                        root=root,
                        path=localized_path.relative_to(root).as_posix(),
                        page_sha256=localized_sha256,
                        profile=profile,
                        profile_sha256=profile_sha256,
                        extra_bindings=bindings,
                    ):
                        record[field] = pending_render_review(
                            localized_sha256,
                            profile_sha256,
                            canonical_sha256=canonical_sha256,
                            localized_sha256=localized_sha256,
                        )
                        reset_render = True
                if reset_render and record.get("status") == "accepted":
                    record["status"] = "human-review-in-progress"
            else:
                record = {
                    "unit": unit.name,
                    "locale": locale,
                    "path": localized_path.relative_to(root).as_posix(),
                    "canonical_sha256": canonical_sha256,
                    "localized_sha256": localized_sha256,
                    "status": "stale"
                    if old.get("canonical_sha256") != canonical_sha256
                    else "drafted",
                    "priority": initial_priority(
                        locale, canonical_signals, localized_signals, unit.name
                    ),
                    "signals": localized_signals,
                    "observed_gaps": gap_signals(
                        canonical_signals, localized_signals
                    ),
                    "provenance": locale_provenance,
                    "contract": {
                        dimension: "pending" for dimension in CONTRACT_DIMENSIONS
                    },
                    "exceptions": [],
                    "automated_commands": [],
                    "linguistic_review": pending_review(
                        canonical_sha256=canonical_sha256,
                        localized_sha256=localized_sha256,
                    ),
                    "technical_review": pending_review(
                        canonical_sha256=canonical_sha256,
                        localized_sha256=localized_sha256,
                    ),
                    "rendered_accessibility_review": pending_render_review(
                        localized_sha256,
                        profile_sha256,
                        canonical_sha256=canonical_sha256,
                        localized_sha256=localized_sha256,
                    ),
                }
                if locale == "ar":
                    record["bidi_review"] = pending_render_review(
                        localized_sha256,
                        profile_sha256,
                        canonical_sha256=canonical_sha256,
                        localized_sha256=localized_sha256,
                    )
            records.append(record)
    return {
        "schema_version": SCHEMA_VERSION,
        "notice": previous_payload["notice"],
        "sources": sources,
        "records": records,
        "root_publication": refresh_root_publication(
            root, previous_payload.get("root_publication")
        ),
    }


def build_manifest(
    root: Path,
    previous_path: Path | None = None,
    *,
    previous_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if previous_payload is not None and previous_path is not None:
        raise ParityError("provide either a previous path or a previous aggregate, not both")
    if previous_payload is None and previous_path is not None:
        previous_payload = load_manifest(previous_path, root)
    if previous_payload is not None and previous_payload.get(
        "schema_version"
    ) == SCHEMA_VERSION:
        return build_v2_manifest(root, previous_payload)
    return build_legacy_manifest(root, previous_payload=previous_payload)


def validate_transition(previous: str, current: str) -> None:
    vocabulary = (
        LEGACY_STATES
        if previous in LEGACY_STATES
        and current in LEGACY_STATES
        and ({previous, current} & {"linguistic-reviewed", "technical-reviewed"})
        else STATES
    )
    if previous not in vocabulary or current not in vocabulary:
        raise ParityError("unknown review state")
    if current in {"stale", "blocked"} or previous in {"stale", "blocked"}:
        return
    order = [state for state in vocabulary if state not in {"stale", "blocked"}]
    if order.index(current) < order.index(previous):
        raise ParityError(f"state regression is not allowed: {previous} -> {current}")


def validate_legacy_manifest(
    payload: dict[str, Any], root: Path, *, require_accepted: bool = False
) -> None:
    if payload.get("schema_version") != LEGACY_SCHEMA_VERSION:
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
        if status not in LEGACY_STATES:
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


def validate_record_contract(record: dict[str, Any], key: tuple[str, str]) -> None:
    automated_commands = record.get("automated_commands")
    if not isinstance(automated_commands, list) or any(
        not isinstance(command, str) or not command for command in automated_commands
    ):
        raise ParityError(f"malformed automated evidence: {key}")
    contract = record.get("contract")
    if not isinstance(contract, dict) or set(contract) != set(CONTRACT_DIMENSIONS):
        raise ParityError(f"incomplete parity contract: {key}")
    if any(result not in CONTRACT_RESULTS for result in contract.values()):
        raise ParityError(f"unknown contract result: {key}")
    exceptions = record.get("exceptions")
    if not isinstance(exceptions, list):
        raise ParityError(f"exceptions must be a list: {key}")
    exception_dimensions: set[str] = set()
    for exception in exceptions:
        required = {
            "dimension",
            "justification",
            "linguistic_approved",
            "technical_approved",
        }
        if not isinstance(exception, dict) or set(exception) != required:
            raise ParityError(f"malformed parity exception: {key}")
        dimension = exception["dimension"]
        if (
            dimension not in CONTRACT_DIMENSIONS
            or dimension in exception_dimensions
            or not isinstance(exception["justification"], str)
            or not exception["justification"].strip()
            or exception["linguistic_approved"] is not True
            or exception["technical_approved"] is not True
        ):
            raise ParityError(f"malformed or unapproved parity exception: {key}")
        exception_dimensions.add(dimension)
    required_dimensions = {
        dimension for dimension, result in contract.items() if result == "exception"
    }
    if exception_dimensions != required_dimensions:
        raise ParityError(f"contract exceptions do not match approvals: {key}")


def validate_record_state(
    record: dict[str, Any],
    key: tuple[str, str],
    reviews: Sequence[dict[str, Any]],
) -> None:
    human_started = (
        any(review["result"] != "pending" for review in reviews)
        or any(result != "pending" for result in record["contract"].values())
        or bool(record["exceptions"])
    )
    changes_requested = any(
        review["result"] == "changes-requested" for review in reviews
    )
    status = record["status"]
    if changes_requested and status != "blocked":
        raise ParityError(f"record state does not reflect requested changes: {key}")
    if status == "human-review-in-progress" and not human_started:
        raise ParityError(f"record state claims absent human evidence: {key}")
    if status in {
        "inventoried",
        "source-frozen",
        "drafted",
        "automated-signals-pass",
    } and human_started:
        raise ParityError(f"record state omits existing human evidence: {key}")


def root_review_objects(root_publication: dict[str, Any]) -> list[dict[str, Any]]:
    reviews = [root_publication["canonical_review"]]
    for page in root_publication["pages"]:
        reviews.append(page["rendered_accessibility_review"])
        for field in ("linguistic_review", "technical_review", "bidi_review"):
            if field in page:
                reviews.append(page[field])
    return reviews


def validate_root_publication(
    root_publication: Any,
    root: Path,
    profile: dict[str, Any],
    profile_sha256: str,
    all_provenance: Sequence[dict[str, Any]] | None = None,
) -> None:
    if not isinstance(root_publication, dict) or set(root_publication) != {
        "state",
        "canonical_review",
        "pages",
        "provenance",
    }:
        raise ParityError("malformed root publication evidence")
    if root_publication.get("state") not in {
        "pending",
        "human-review-in-progress",
        "accepted",
        "stale",
        "blocked",
    }:
        raise ParityError("unknown root publication state")
    canonical_sha256 = digest(root / "README.md")
    mirror_sha256 = digest(root / "README.en.md")
    if canonical_sha256 != mirror_sha256:
        raise ParityError("root English mirrors are not byte-identical")
    validate_review_object(
        root_publication["canonical_review"],
        "root canonical review",
        {
            "canonical_sha256": canonical_sha256,
            "mirror_sha256": mirror_sha256,
        },
    )
    pages = root_publication.get("pages")
    if (
        not isinstance(pages, list)
        or [page.get("path") if isinstance(page, dict) else None for page in pages]
        != list(ROOT_PATHS)
    ):
        raise ParityError("root publication pages do not match the six-path inventory")
    for page in pages:
        relative = page["path"]
        expected_fields = {"path", "sha256", "rendered_accessibility_review"}
        if relative in LOCALIZED_ROOT_PATHS:
            expected_fields |= {"linguistic_review", "technical_review"}
        if relative == "README.ar.md":
            expected_fields.add("bidi_review")
        if set(page) != expected_fields:
            raise ParityError(f"malformed root page evidence: {relative}")
        page_path = safe_repository_path(root, relative, "root publication path")
        if not page_path.is_file() or page_path.is_symlink():
            raise ParityError(f"root publication page is missing: {relative}")
        page_sha256 = digest(page_path)
        if page.get("sha256") != page_sha256:
            raise ParityError(f"stale root publication page: {relative}")
        validate_render_review(
            page["rendered_accessibility_review"],
            f"root rendered review: {relative}",
            root=root,
            path=relative,
            page_sha256=page_sha256,
            profile=profile,
            profile_sha256=profile_sha256,
        )
        if relative in LOCALIZED_ROOT_PATHS:
            bindings = {
                "canonical_sha256": canonical_sha256,
                "localized_sha256": page_sha256,
            }
            validate_review_object(
                page["linguistic_review"],
                f"root linguistic review: {relative}",
                bindings,
            )
            validate_review_object(
                page["technical_review"],
                f"root technical review: {relative}",
                bindings,
            )
        if relative == "README.ar.md":
            validate_render_review(
                page["bidi_review"],
                "root bidi review: README.ar.md",
                root=root,
                path=relative,
                page_sha256=page_sha256,
                profile=profile,
                profile_sha256=profile_sha256,
                extra_bindings={
                    "canonical_sha256": canonical_sha256,
                    "localized_sha256": page_sha256,
                },
            )
    provenance = root_publication.get("provenance")
    validate_provenance_bindings(
        provenance,
        "root provenance references",
        root_provenance_references(root, profile, all_provenance),
    )
    reviews = root_review_objects(root_publication)
    if any(review["result"] == "changes-requested" for review in reviews) and (
        root_publication["state"] != "blocked"
    ):
        raise ParityError("root state does not reflect requested changes")
    if root_publication["state"] == "pending" and any(
        review["result"] != "pending" for review in reviews
    ):
        raise ParityError("root state omits existing human evidence")
    if root_publication["state"] == "human-review-in-progress" and all(
        review["result"] == "pending" for review in reviews
    ):
        raise ParityError("root state claims absent human evidence")
    if root_publication["state"] == "accepted":
        if any(review.get("result") != "approved" for review in reviews):
            raise ParityError("accepted root publication lacks human approvals")
        if any(
            reference["status"] not in RESOLVED_PROVENANCE_STATES
            for reference in provenance
        ):
            raise ParityError("accepted root publication lacks resolved provenance")


def validate_v2_manifest(
    payload: dict[str, Any], root: Path, *, require_accepted: bool = False
) -> None:
    if set(payload) != {
        "schema_version",
        "notice",
        "sources",
        "records",
        "root_publication",
    } or payload.get("schema_version") != SCHEMA_VERSION:
        raise ParityError("unsupported parity manifest schema_version")
    if not isinstance(payload.get("notice"), str) or not payload["notice"]:
        raise ParityError("manifest notice must be a non-empty string")
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
    profile, profile_sha256 = load_render_profile(root)
    all_provenance = provenance_references(root)
    source_map: dict[str, dict[str, Any]] = {}
    for source in sources:
        if not isinstance(source, dict) or set(source) != {
            "unit",
            "path",
            "sha256",
            "signals",
            "provenance",
            "canonical_review",
            "rendered_accessibility_review",
        }:
            raise ParityError("malformed schema-v2 canonical source")
        unit = source.get("unit")
        if not isinstance(unit, str) or unit in source_map:
            raise ParityError("duplicate schema-v2 canonical source")
        if source.get("path") != f"{unit}/README.md":
            raise ParityError(f"canonical source path mismatch: {unit}")
        path = safe_repository_path(root, source["path"], "canonical source path")
        if not path.is_file() or path.is_symlink() or digest(path) != source.get("sha256"):
            raise ParityError(f"invalid or stale canonical source: {unit}")
        if not isinstance(source.get("signals"), dict):
            raise ParityError(f"malformed canonical source signals: {unit}")
        validate_provenance_bindings(
            source["provenance"],
            f"canonical source provenance: {unit}",
            source_provenance_references(root, unit, all_provenance),
        )
        validate_review_object(
            source["canonical_review"],
            f"canonical source review: {unit}",
            {"canonical_sha256": source["sha256"]},
        )
        validate_render_review(
            source["rendered_accessibility_review"],
            f"canonical source rendered review: {unit}",
            root=root,
            path=source["path"],
            page_sha256=source["sha256"],
            profile=profile,
            profile_sha256=profile_sha256,
        )
        source_map[unit] = source
    seen: set[tuple[str, str]] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ParityError("localized records must be JSON objects")
        key = (str(record.get("unit", "")), str(record.get("locale", "")))
        expected_fields = {
            "unit",
            "locale",
            "path",
            "canonical_sha256",
            "localized_sha256",
            "status",
            "priority",
            "signals",
            "observed_gaps",
            "provenance",
            "contract",
            "exceptions",
            "automated_commands",
            "linguistic_review",
            "technical_review",
            "rendered_accessibility_review",
        }
        if key[1] == "ar":
            expected_fields.add("bidi_review")
        if (
            set(record) != expected_fields
            or key in seen
            or key[0] not in source_map
            or key[1] not in LOCALES
        ):
            raise ParityError(f"invalid or duplicate localized record: {key}")
        seen.add(key)
        if record["path"] != f"{key[0]}/{LOCALES[key[1]]}":
            raise ParityError(f"localized record path mismatch: {key}")
        path = safe_repository_path(root, record["path"], "localized record path")
        if not path.is_file() or path.is_symlink() or digest(path) != record["localized_sha256"]:
            raise ParityError(f"localized record is stale: {key}")
        if record["canonical_sha256"] != source_map[key[0]]["sha256"]:
            raise ParityError(f"canonical digest mismatch: {key}")
        if record.get("status") not in STATES:
            raise ParityError(f"unknown status: {key}")
        if not isinstance(record.get("signals"), dict) or not isinstance(
            record.get("observed_gaps"), list
        ):
            raise ParityError(f"malformed localized triage evidence: {key}")
        validate_provenance_bindings(
            record["provenance"],
            f"localized provenance: {key}",
            locale_provenance_references(
                root, key[0], key[1], all_provenance
            ),
        )
        validate_record_contract(record, key)
        bindings = {
            "canonical_sha256": record["canonical_sha256"],
            "localized_sha256": record["localized_sha256"],
        }
        validate_review_object(
            record["linguistic_review"], f"linguistic review: {key}", bindings
        )
        validate_review_object(
            record["technical_review"], f"technical review: {key}", bindings
        )
        validate_render_review(
            record["rendered_accessibility_review"],
            f"localized rendered review: {key}",
            root=root,
            path=record["path"],
            page_sha256=record["localized_sha256"],
            profile=profile,
            profile_sha256=profile_sha256,
            extra_bindings=bindings,
        )
        reviews = [
            record["linguistic_review"],
            record["technical_review"],
            record["rendered_accessibility_review"],
        ]
        if key[1] == "ar":
            validate_render_review(
                record["bidi_review"],
                f"bidi review: {key}",
                root=root,
                path=record["path"],
                page_sha256=record["localized_sha256"],
                profile=profile,
                profile_sha256=profile_sha256,
                extra_bindings=bindings,
            )
            reviews.append(record["bidi_review"])
        validate_record_state(record, key, reviews)
        if record["status"] == "accepted":
            if any(
                result not in {"pass", "exception"}
                for result in record["contract"].values()
            ):
                raise ParityError(f"accepted record has incomplete contract: {key}")
            if any(review["result"] != "approved" for review in reviews):
                raise ParityError(f"accepted record lacks human approvals: {key}")
            source = source_map[key[0]]
            if (
                source["canonical_review"]["result"] != "approved"
                or source["rendered_accessibility_review"]["result"] != "approved"
            ):
                raise ParityError(f"accepted record lacks canonical source approvals: {key}")
            required_commands = {
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            }
            if not required_commands <= set(record["automated_commands"]):
                raise ParityError(f"accepted record lacks automated evidence: {key}")
            if any(
                reference["status"] not in RESOLVED_PROVENANCE_STATES
                for reference in (
                    source_map[key[0]]["provenance"] + record["provenance"]
                )
            ):
                raise ParityError(f"accepted record lacks resolved provenance: {key}")
    validate_root_publication(
        payload["root_publication"],
        root,
        profile,
        profile_sha256,
        all_provenance,
    )
    if require_accepted:
        pending_sources = [
            source["unit"]
            for source in sources
            if source["canonical_review"]["result"] != "approved"
            or source["rendered_accessibility_review"]["result"] != "approved"
        ]
        pending_records = [
            f"{record['unit']}:{record['locale']}"
            for record in records
            if record["status"] != "accepted"
        ]
        root_pending = payload["root_publication"]["state"] != "accepted"
        if pending_sources or pending_records or root_pending:
            raise ParityError(
                "publication review incomplete: "
                f"{len(pending_sources)} canonical source reviews, "
                f"{len(pending_records)} localized reviews, and "
                f"{int(root_pending)} root publication packet pending"
            )


def validate_manifest(
    payload: dict[str, Any], root: Path, *, require_accepted: bool = False
) -> None:
    version = payload.get("schema_version")
    if version == LEGACY_SCHEMA_VERSION:
        validate_legacy_manifest(payload, root, require_accepted=require_accepted)
        return
    if version == SCHEMA_VERSION:
        validate_v2_manifest(payload, root, require_accepted=require_accepted)
        return
    raise ParityError("unsupported parity manifest schema_version")


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
    version = payload.get("schema_version")
    vocabulary = LEGACY_STATES if version == LEGACY_SCHEMA_VERSION else STATES
    reconciled = 0
    for record in records:
        if not isinstance(record, dict):
            raise ParityError("manifest records must be objects before reconciliation")
        status = record.get("status")
        if status not in vocabulary:
            raise ParityError("unknown review state before reconciliation")
        if status not in {"stale", "inventoried"}:
            continue
        validate_transition(status, "drafted")
        reset: dict[str, Any] = {
            "status": "drafted",
            "contract": {dimension: "pending" for dimension in CONTRACT_DIMENSIONS},
            "exceptions": [],
            "automated_commands": [],
        }
        if version == SCHEMA_VERSION:
            bindings = {
                "canonical_sha256": record["canonical_sha256"],
                "localized_sha256": record["localized_sha256"],
            }
            profile_sha256 = record["rendered_accessibility_review"][
                "profile_sha256"
            ]
            reset["linguistic_review"] = pending_review(**bindings)
            reset["technical_review"] = pending_review(**bindings)
            reset["rendered_accessibility_review"] = pending_render_review(
                record["localized_sha256"],
                profile_sha256,
                **bindings,
            )
            if record["locale"] == "ar":
                reset["bidi_review"] = pending_render_review(
                    record["localized_sha256"],
                    profile_sha256,
                    **bindings,
                )
        else:
            reset["linguistic_review"] = empty_review()
            reset["technical_review"] = empty_review()
        record.update(reset)
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
        "--migrate-review-schema",
        action="store_true",
        help="atomically migrate all partition leaves from review schema 1 to 2",
    )
    actions.add_argument(
        "--export-monolith",
        metavar="PATH",
        help="write a validated schema-v1 rollback export without changing live storage",
    )
    actions.add_argument(
        "--export-review-bundle",
        metavar="PATH",
        help="write a lossless canonical schema-v2 review bundle",
    )
    actions.add_argument(
        "--review-packet",
        metavar="UNIT",
        help="emit one deterministic read-only unit review packet",
    )
    actions.add_argument(
        "--root-review-packet",
        action="store_true",
        help="emit the deterministic read-only root publication packet",
    )
    actions.add_argument(
        "--verify-publication-signoff",
        metavar="PATH",
        help="verify the external common publication sign-off read-only",
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
        packet_action = bool(
            args.review_packet is not None
            or args.root_review_packet
            or args.verify_publication_signoff is not None
        )
        if packet_action and args.manifest != MANIFEST:
            raise ParityError(
                "packet and sign-off commands require the default parity index"
            )
        gate_incompatible_action = bool(
            args.migrate_partitioned
            or args.migrate_review_schema
            or args.export_monolith is not None
            or args.export_review_bundle is not None
            or packet_action
        )
        if gate_incompatible_action and args.require_accepted:
            raise ParityError(
                "--require-accepted cannot be combined with this explicit operation"
            )
        if args.migrate_partitioned:
            migrate_partitioned(path, root)
            payload = load_manifest(path, root)
            print(
                f"Migrated parity inventory: {len(payload['sources'])} sources, "
                f"{len(payload['records'])} variants."
            )
            return 0
        if args.migrate_review_schema:
            changed = migrate_review_schema(path, root)
            payload = load_manifest(path, root)
            if changed:
                print(
                    f"Migrated review evidence: {len(changed)} leaves; "
                    f"{len(payload['sources'])} sources, "
                    f"{len(payload['records'])} variants, 1 root packet."
                )
            else:
                print("Review evidence already uses schema 2; no files changed.")
            return 0
        if args.export_monolith is not None:
            output = (root / args.export_monolith).resolve(strict=False)
            export_monolith(path, output, root)
            print(f"Exported schema-v1 parity manifest: {output.relative_to(root).as_posix()}")
            return 0
        if args.export_review_bundle is not None:
            output = (root / args.export_review_bundle).resolve(strict=False)
            export_review_bundle(path, output, root)
            print(
                "Exported schema-v2 review bundle: "
                f"{output.relative_to(root).as_posix()}"
            )
            return 0
        if args.review_packet is not None:
            packet = build_unit_review_packet(root, args.review_packet)
            write_stdout_bytes(canonical_json_bytes(packet))
            return 0
        if args.root_review_packet:
            packet = build_root_review_packet(root)
            write_stdout_bytes(canonical_json_bytes(packet))
            return 0
        if args.verify_publication_signoff is not None:
            verify_publication_signoff(root, args.verify_publication_signoff)
            print("Publication sign-off approved and current.")
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
        packet_action = bool(
            getattr(args, "review_packet", None) is not None
            or getattr(args, "root_review_packet", False)
            or getattr(args, "verify_publication_signoff", None) is not None
        )
        if packet_action:
            print(
                f"ERROR parity.inventory {manifest_label}: {exc}",
                file=sys.stderr,
            )
            return 1 if isinstance(exc, PublicationIncompleteError) else 2
        print(f"ERROR parity.inventory {manifest_label}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
