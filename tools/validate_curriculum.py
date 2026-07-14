#!/usr/bin/env python3
"""Validate the declared curriculum graph without claiming pedagogical approval."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Iterable


SCHEMA_VERSION = 1


@dataclass(frozen=True, order=True)
class Issue:
    code: str
    path: str
    message: str


class ContractError(Exception):
    """Raised when the contract itself cannot be parsed or has the wrong shape."""


def _safe_relative(root: Path, candidate: Path) -> str:
    try:
        return candidate.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return "<outside-repository>"


def _slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"[\s\-]+", "-", text).strip("-")


def markdown_anchors(text: str) -> set[str]:
    """Return conservative GitHub-style heading anchors and explicit HTML IDs."""
    anchors: set[str] = set(re.findall(r"<a\s+(?:[^>]*?\s)?id=[\"']([^\"']+)[\"']", text, re.I))
    counts: dict[str, int] = {}
    in_fence = False
    fence = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        match = re.match(r"(`{3,}|~{3,})", stripped)
        if match:
            marker = match.group(1)
            if not in_fence:
                in_fence = True
                fence = marker[0]
            elif marker[0] == fence:
                in_fence = False
                fence = ""
            continue
        if in_fence:
            continue
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not heading:
            continue
        base = _slug(heading.group(1))
        if not base:
            continue
        duplicate = counts.get(base, 0)
        counts[base] = duplicate + 1
        anchors.add(base if duplicate == 0 else f"{base}-{duplicate}")
    return anchors


def _table_list(data: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ContractError(f"'{key}' must be an array of tables")
    return value


def _required_string(table: dict[str, Any], key: str, owner: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{owner}.{key} must be a non-empty string")
    return value


def _string_list(table: dict[str, Any], key: str, owner: str) -> list[str]:
    value = table.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ContractError(f"{owner}.{key} must be an array of non-empty strings")
    if len(value) != len(set(value)):
        raise ContractError(f"{owner}.{key} contains duplicate entries")
    return value


def load_contract(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ContractError(f"cannot read curriculum contract: {exc}") from exc
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ContractError(f"schema_version must be {SCHEMA_VERSION}")
    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ContractError("'metadata' must be a table")
    _required_string(metadata, "evidence_scope", "metadata")
    _table_list(data, "concept")
    _table_list(data, "checkpoint")
    _table_list(data, "route")
    return data


def _indexed(tables: Iterable[dict[str, Any]], kind: str, issues: list[Issue]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for position, table in enumerate(tables, start=1):
        owner = f"{kind}[{position}]"
        try:
            identifier = _required_string(table, "id", owner)
        except ContractError as exc:
            issues.append(Issue("CURRICULUM_SCHEMA", "tools/curriculum_map.toml", str(exc)))
            continue
        if identifier in result:
            issues.append(Issue("CURRICULUM_DUPLICATE_ID", "tools/curriculum_map.toml", f"duplicate {kind} id: {identifier}"))
            continue
        result[identifier] = table
    return result


def _prerequisite_closure(checkpoint_id: str, checkpoints: dict[str, dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    pending = [checkpoint_id]
    while pending:
        current = pending.pop()
        if current in result or current not in checkpoints:
            continue
        result.add(current)
        pending.extend(checkpoints[current].get("prerequisites", []))
    return result


def _cycles(checkpoints: dict[str, dict[str, Any]]) -> list[list[str]]:
    state: dict[str, int] = {}
    stack: list[str] = []
    found: list[list[str]] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for dependency in checkpoints[node].get("prerequisites", []):
            if dependency not in checkpoints:
                continue
            if state.get(dependency, 0) == 0:
                visit(dependency)
            elif state.get(dependency) == 1:
                start = stack.index(dependency)
                cycle = stack[start:] + [dependency]
                if cycle not in found:
                    found.append(cycle)
        stack.pop()
        state[node] = 2

    for checkpoint_id in checkpoints:
        if state.get(checkpoint_id, 0) == 0:
            visit(checkpoint_id)
    return found


def validate_contract(root: Path, data: dict[str, Any]) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    concepts = _indexed(_table_list(data, "concept"), "concept", issues)
    checkpoints = _indexed(_table_list(data, "checkpoint"), "checkpoint", issues)
    routes = _indexed(_table_list(data, "route"), "route", issues)

    orders: dict[str, int] = {}
    for checkpoint_id, checkpoint in checkpoints.items():
        owner = f"checkpoint.{checkpoint_id}"
        order = checkpoint.get("order")
        if isinstance(order, bool) or not isinstance(order, int) or order < 1:
            issues.append(Issue("CURRICULUM_SCHEMA", "tools/curriculum_map.toml", f"{owner}.order must be a positive integer"))
        else:
            orders[checkpoint_id] = order

    for checkpoint_id, checkpoint in checkpoints.items():
        owner = f"checkpoint.{checkpoint_id}"
        try:
            rel_path = _required_string(checkpoint, "path", owner)
            anchor = _required_string(checkpoint, "anchor", owner)
            prerequisites = _string_list(checkpoint, "prerequisites", owner)
            required_concepts = _string_list(checkpoint, "requires", owner)
            taught_concepts = _string_list(checkpoint, "teaches", owner)
        except ContractError as exc:
            issues.append(Issue("CURRICULUM_SCHEMA", "tools/curriculum_map.toml", str(exc)))
            continue

        raw_path = Path(rel_path)
        target = (root / raw_path).resolve()
        if raw_path.is_absolute() or ".." in raw_path.parts or _safe_relative(root, target) == "<outside-repository>":
            issues.append(Issue("CURRICULUM_PATH_ESCAPE", "tools/curriculum_map.toml", f"checkpoint {checkpoint_id} path must stay inside the repository"))
        elif not target.is_file():
            issues.append(Issue("CURRICULUM_MISSING_PATH", rel_path, f"checkpoint {checkpoint_id} target does not exist"))
        else:
            try:
                anchors = markdown_anchors(target.read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                issues.append(Issue("CURRICULUM_UNREADABLE_PATH", rel_path, f"checkpoint {checkpoint_id} target is not readable UTF-8"))
            else:
                if anchor not in anchors:
                    issues.append(Issue("CURRICULUM_MISSING_ANCHOR", rel_path, f"checkpoint {checkpoint_id} anchor not found: {anchor}"))

        for dependency in prerequisites:
            if dependency not in checkpoints:
                issues.append(Issue("CURRICULUM_UNKNOWN_CHECKPOINT", "tools/curriculum_map.toml", f"checkpoint {checkpoint_id} references unknown prerequisite: {dependency}"))
            elif checkpoint_id in orders and dependency in orders and orders[dependency] >= orders[checkpoint_id]:
                issues.append(Issue("CURRICULUM_FORWARD_DEPENDENCY", "tools/curriculum_map.toml", f"checkpoint {checkpoint_id} requires non-earlier checkpoint: {dependency}"))
        for concept_id in required_concepts + taught_concepts:
            if concept_id not in concepts:
                issues.append(Issue("CURRICULUM_UNKNOWN_CONCEPT", "tools/curriculum_map.toml", f"checkpoint {checkpoint_id} references unknown concept: {concept_id}"))

    for concept_id, concept in concepts.items():
        owner = f"concept.{concept_id}"
        try:
            provider = _required_string(concept, "introduced_by", owner)
        except ContractError as exc:
            issues.append(Issue("CURRICULUM_SCHEMA", "tools/curriculum_map.toml", str(exc)))
            continue
        if provider not in checkpoints:
            issues.append(Issue("CURRICULUM_UNKNOWN_CHECKPOINT", "tools/curriculum_map.toml", f"concept {concept_id} has unknown provider: {provider}"))
        elif concept_id not in checkpoints[provider].get("teaches", []):
            issues.append(Issue("CURRICULUM_PROVIDER_MISMATCH", "tools/curriculum_map.toml", f"concept {concept_id} is not taught by its provider: {provider}"))

    for checkpoint_id, checkpoint in checkpoints.items():
        closure: set[str] = set()
        for dependency in checkpoint.get("prerequisites", []):
            closure.update(_prerequisite_closure(dependency, checkpoints))
        for concept_id in checkpoint.get("requires", []):
            concept = concepts.get(concept_id)
            if not concept:
                continue
            provider = concept.get("introduced_by")
            if provider != checkpoint_id and provider not in closure:
                issues.append(Issue("CURRICULUM_FORWARD_CONCEPT", "tools/curriculum_map.toml", f"checkpoint {checkpoint_id} requires {concept_id} before provider {provider}"))

    for cycle in _cycles(checkpoints):
        issues.append(Issue("CURRICULUM_CYCLE", "tools/curriculum_map.toml", "checkpoint cycle: " + " -> ".join(cycle)))

    for route_id, route in routes.items():
        owner = f"route.{route_id}"
        try:
            for key in ("title", "duration", "outcome", "completion", "stopping_point"):
                _required_string(route, key, owner)
            entry = _string_list(route, "entry_checkpoints", owner)
            route_checkpoints = _string_list(route, "checkpoints", owner)
        except ContractError as exc:
            issues.append(Issue("CURRICULUM_SCHEMA", "tools/curriculum_map.toml", str(exc)))
            continue
        available: set[str] = set()
        for checkpoint_id in entry:
            if checkpoint_id not in checkpoints:
                issues.append(Issue("CURRICULUM_UNKNOWN_CHECKPOINT", "tools/curriculum_map.toml", f"route {route_id} has unknown entry checkpoint: {checkpoint_id}"))
            else:
                available.update(_prerequisite_closure(checkpoint_id, checkpoints))
        previous_order = 0
        for checkpoint_id in route_checkpoints:
            if checkpoint_id not in checkpoints:
                issues.append(Issue("CURRICULUM_UNKNOWN_CHECKPOINT", "tools/curriculum_map.toml", f"route {route_id} references unknown checkpoint: {checkpoint_id}"))
                continue
            order = orders.get(checkpoint_id, 0)
            if order <= previous_order:
                issues.append(Issue("CURRICULUM_ROUTE_ORDER", "tools/curriculum_map.toml", f"route {route_id} is not in increasing order at: {checkpoint_id}"))
            previous_order = order
            missing = set(checkpoints[checkpoint_id].get("prerequisites", [])) - available
            if missing:
                issues.append(Issue("CURRICULUM_ROUTE_PREREQUISITE", "tools/curriculum_map.toml", f"route {route_id} reaches {checkpoint_id} before: {', '.join(sorted(missing))}"))
            available.add(checkpoint_id)

    return sorted(set(issues))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate declared curriculum evidence; this does not approve pedagogy.")
    script_root = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo-root", type=Path, default=script_root)
    parser.add_argument("--map", dest="map_path", type=Path, default=script_root / "tools" / "curriculum_map.toml")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = load_contract(args.map_path)
        issues = validate_contract(args.repo_root, data)
    except ContractError as exc:
        issue = Issue("CURRICULUM_CONFIG", "tools/curriculum_map.toml", str(exc))
        if args.json:
            print(json.dumps({"schema_version": SCHEMA_VERSION, "status": "error", "issues": [asdict(issue)]}, sort_keys=True))
        else:
            print(f"{issue.code} {issue.path}: {issue.message}")
        return 2

    status = "pass" if not issues else "fail"
    if args.json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "status": status, "evidence_scope": "declared-contract-only", "issues": [asdict(issue) for issue in issues]}, sort_keys=True))
    else:
        for issue in issues:
            print(f"{issue.code} {issue.path}: {issue.message}")
        print(f"curriculum contract: {status} ({len(issues)} issue(s)); declared evidence only, not pedagogical approval")
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
