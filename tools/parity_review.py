#!/usr/bin/env python3
"""Build and validate the multilingual semantic-review inventory.

Counts and Markdown structure are triage signals only. A localized document can
reach ``accepted`` only after its twelve semantic dimensions and both human
review roles are recorded as passed against the current canonical digest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Sequence

import validate_book


SCHEMA_VERSION = 1
MANIFEST = "tools/parity_manifest.json"
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


def scoped_units(root: Path) -> list[Path]:
    units = [
        path
        for path in root.iterdir()
        if path.is_dir()
        and (
            (re.fullmatch(r"chapter-(?:0[1-9]|1[0-9]|2[0-2])-.+", path.name) is not None)
            or path.name in {"appendix-cli-parser", "appendix-algorithms"}
        )
    ]
    return sorted(units, key=lambda path: path.name)


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
    if locale == "ca" and (chapter_number is not None and 15 <= chapter_number <= 22):
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


def load_existing(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        (record["unit"], record["locale"]): record
        for record in payload.get("records", [])
        if isinstance(record, dict) and "unit" in record and "locale" in record
    }


def load_existing_sources(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        source["unit"]: source
        for source in payload.get("sources", [])
        if isinstance(source, dict) and "unit" in source
    }


def build_manifest(root: Path, previous_path: Path | None = None) -> dict[str, Any]:
    config = validate_book.load_config(root)
    previous = load_existing(previous_path) if previous_path else {}
    previous_sources = load_existing_sources(previous_path) if previous_path else {}
    units = scoped_units(root)
    if len(units) != 24:
        raise ParityError(f"expected 24 canonical units, found {len(units)}")
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
    if not isinstance(sources, list) or len(sources) != 24:
        raise ParityError("manifest must contain exactly 24 canonical sources")
    if not isinstance(records, list) or len(records) != 96:
        raise ParityError("manifest must contain exactly 96 localized records")
    source_map: dict[str, dict[str, Any]] = {}
    for source in sources:
        unit = source.get("unit")
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
        key = (str(record.get("unit", "")), str(record.get("locale", "")))
        if key in seen or key[0] not in source_map or key[1] not in LOCALES:
            raise ParityError(f"invalid or duplicate localized record: {key}")
        seen.add(key)
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
            if not isinstance(exception, dict) or not required <= set(exception):
                raise ParityError(f"malformed parity exception: {key}")
            if not exception["justification"] or not exception["linguistic_approved"] or not exception["technical_approved"]:
                raise ParityError(f"unapproved parity exception: {key}")
            exception_dimensions.add(exception["dimension"])
        for dimension, result in contract.items():
            if result == "exception" and dimension not in exception_dimensions:
                raise ParityError(f"contract exception has no approval: {key}/{dimension}")
        reviews = (record.get("linguistic_review"), record.get("technical_review"))
        for review in reviews:
            if not isinstance(review, dict) or review.get("result") not in REVIEW_RESULTS:
                raise ParityError(f"malformed human review: {key}")
        if status == "accepted":
            if any(result not in {"pass", "exception"} for result in contract.values()):
                raise ParityError(f"accepted record has incomplete contract: {key}")
            if any(review.get("result") != "approved" or not review.get("role") or not review.get("review_date") for review in reviews):
                raise ParityError(f"accepted record lacks both human approvals: {key}")
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
    blocked_paths = {
        diagnostic.path for diagnostic in diagnostics if diagnostic.severity in {"error", "warning"}
    }
    promoted = 0
    for record in payload.get("records", []):
        if record.get("status") != "drafted" or record.get("path") in blocked_paths:
            continue
        validate_transition("drafted", "automated-signals-pass")
        record["status"] = "automated-signals-pass"
        record["automated_commands"] = [
            "python -B tools/validate_book.py",
            "python -B tools/parity_review.py",
        ]
        promoted += 1
    return promoted


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


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    """Atomically replace a validated manifest in the same directory."""

    temporary = path.with_name(f".{path.name}.tmp")
    try:
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


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
    parser.add_argument("--manifest", default=MANIFEST)
    parser.add_argument(
        "--require-accepted",
        action="store_true",
        help="publication gate for the historical 22 chapters and two appendices",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    path = (root / args.manifest).resolve()
    try:
        validate_book.safe_relative(path, root)
        mutating = args.write or args.record_automated or args.reconcile_drafts
        if mutating:
            if args.reconcile_drafts and not path.is_file():
                raise ParityError("--reconcile-drafts requires an existing manifest")
            payload = build_manifest(root, path if path.is_file() else None)
            if args.reconcile_drafts:
                reconciled = reconcile_draft_records(payload)
                print(f"Reconciled {reconciled} stale/inventoried variants to drafted.")
            if args.record_automated:
                diagnostics = validate_book.collect_diagnostics(root, validate_book.load_config(root), [])
                promoted = record_automated_results(payload, diagnostics)
                print(f"Recorded automated-signals-pass for {promoted} drafted variants.")
            validate_manifest(payload, root, require_accepted=args.require_accepted)
            write_manifest(path, payload)
        else:
            payload = json.loads(path.read_text(encoding="utf-8"))
            validate_manifest(payload, root, require_accepted=args.require_accepted)
        print(f"Parity inventory valid: {len(payload['sources'])} sources, {len(payload['records'])} variants.")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR parity.inventory {args.manifest}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
