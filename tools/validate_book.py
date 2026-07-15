#!/usr/bin/env python3
"""Deterministic, standard-library quality checks for the course.

The snippet runner reduces accidents for trusted repository content. Static
screening can be bypassed by Python introspection, so this is not an OS security
sandbox. It must never receive hostile snippets, secrets, elevated permissions,
or a writable privileged checkout; repository snapshots only fail-detect writes.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
import tomllib
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence
from urllib.parse import unquote, urlsplit


SCHEMA_VERSION = 1
RULE_VERSION = 1
CLASSIFICATIONS = {
    "runnable",
    "expected-error",
    "compile-only",
    "source-ref",
    "todo",
    "illustrative",
    "output",
}
LANGUAGE_FILES = {
    "README.md": "English",
    "README.es.md": "Spanish",
    "README.ca.md": "Catalan",
    "README.sv.md": "Swedish",
    "README.ar.md": "Arabic",
}
SELECTOR_LABELS = {
    "README.md": "English",
    "README.es.md": "Español",
    "README.ca.md": "Català",
    "README.sv.md": "Svenska",
    "README.ar.md": "العربية",
}
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"(`+)(.*?)\1")
HTML_IMAGE_RE = re.compile(r"<img\b([^>]*?)>", re.I)
HTML_LINK_RE = re.compile(r"<a\b([^>]*?\bhref=[\"']([^\"']+)[\"'][^>]*)>(.*?)</a>", re.I)
HTML_ATTR_RE = re.compile(r"\b(alt|src)=[\"']([^\"']*)[\"']", re.I)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
METADATA_RE = re.compile(r"^\s*<!--\s*bookcheck:\s*(.*?)\s*-->\s*$")
HTML_ANCHOR_RE = re.compile(r"<a\s+(?:name|id)=[\"']([^\"']+)[\"']", re.I)
GENERIC_LINK_TEXT = {
    "",
    "click here",
    "here",
    "read more",
    "haz clic aquí",
    "aquí",
    "clica aquí",
    "här",
    "اضغط هنا",
}
GENERIC_IMAGE_ALT = {
    "image",
    "photo",
    "picture",
    "screenshot",
    "diagram",
    "icon",
    "imagen",
    "foto",
    "captura",
    "diagrama",
    "icono",
    "imatge",
    "skärmbild",
    "bild",
    "صورة",
    "لقطة شاشة",
}
STRUCTURAL_MARKERS = {"visual-text-equivalent", "decorative", "table-alternative"}
ATTRIBUTION_ENTRY_FIELDS = {
    "id", "paths", "kind", "status", "review_date", "review_role", "note",
    "source_title", "source_url", "author_or_holder", "license", "required_notice",
    "notice_location", "adaptation", "declaration",
}
PLUGIN_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
SAFE_PLUGIN_SECRET_RE = re.compile(
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|"
    r"xox[baprs]-[A-Za-z0-9-]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
SAFE_PLUGIN_ABSOLUTE_PATH_RE = re.compile(
    r"(?<![:/\w.])/(?:[^\s/:]+/)+[^\s:]+|\b[A-Za-z]:[\\/][^\s]+"
)
PLUGIN_PROTOCOL_RULES = {
    "plugin.path",
    "plugin.timeout",
    "plugin.output_limit",
    "plugin.descendant",
    "plugin.failure",
    "plugin.schema",
    "plugin.registration",
    "plugin.timeout_contract",
    "plugin.diagnostic_schema",
    "plugin.source_mutation",
}


@dataclass(frozen=True, order=True)
class Diagnostic:
    rule_id: str
    path: str
    message: str
    remediation: str
    severity: str = "error"
    line: int | None = None
    column: int | None = None
    construct: str = ""
    schema_version: int = SCHEMA_VERSION

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("construct", None)
        return {key: value for key, value in data.items() if value is not None}


@dataclass
class Fence:
    language: str
    classification: str | None
    code: str
    line: int
    metadata: dict[str, str] = field(default_factory=dict)
    end_line: int | None = None


@dataclass
class ScanResult:
    headings: list[tuple[int, str, int]] = field(default_factory=list)
    anchors: set[str] = field(default_factory=set)
    fences: list[Fence] = field(default_factory=list)
    links: list[tuple[bool, str, str, int]] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)


class ConfigError(ValueError):
    pass


class OutputLimitExceeded(RuntimeError):
    pass


class SurvivingDescendantError(RuntimeError):
    pass


def diagnostic_key(item: Diagnostic) -> tuple[Any, ...]:
    return (
        item.rule_id,
        item.path,
        item.line if item.line is not None else -1,
        item.column if item.column is not None else -1,
        item.severity,
        item.message,
        item.remediation,
        item.construct,
    )


def run_bounded(
    command: Sequence[str],
    *,
    cwd: str | os.PathLike[str],
    timeout: int,
    env: dict[str, str] | None = None,
    stdin: int | None = subprocess.DEVNULL,
    output_limit: int | None = None,
) -> subprocess.CompletedProcess[bytes]:
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdin=stdin,
            stdout=stdout_file,
            stderr=stderr_file,
            start_new_session=True,
        )

        def terminate_process_group() -> None:
            try:
                if hasattr(os, "killpg"):
                    os.killpg(process.pid, signal.SIGKILL)
                else:  # pragma: no cover - platform-specific fallback.
                    process.kill()
            except ProcessLookupError:
                pass

        deadline = time.monotonic() + timeout
        while process.poll() is None:
            stdout_size = os.fstat(stdout_file.fileno()).st_size
            stderr_size = os.fstat(stderr_file.fileno()).st_size
            if output_limit is not None and stdout_size + stderr_size > output_limit:
                terminate_process_group()
                process.wait()
                raise OutputLimitExceeded(f"child output exceeded {output_limit} bytes")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                terminate_process_group()
                process.wait()
                raise subprocess.TimeoutExpired(command, timeout)
            time.sleep(min(0.01, remaining))
        descendant_survived = False
        if hasattr(os, "killpg"):
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                pass
            else:
                descendant_survived = True
        if descendant_survived:
            # The direct child has been reaped, so a live process group means a
            # descendant survived it. Terminate the group and fail closed.
            terminate_process_group()
            raise SurvivingDescendantError("child left a surviving descendant")
        stdout_size = os.fstat(stdout_file.fileno()).st_size
        stderr_size = os.fstat(stderr_file.fileno()).st_size
        if output_limit is not None and stdout_size + stderr_size > output_limit:
            raise OutputLimitExceeded(f"child output exceeded {output_limit} bytes")
        stdout_file.seek(0)
        stderr_file.seek(0)
        return subprocess.CompletedProcess(command, process.returncode, stdout_file.read(), stderr_file.read())


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def safe_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ConfigError("path escapes repository") from exc


def load_config(root: Path) -> dict[str, Any]:
    path = root / "tools" / "book_quality.toml"
    with path.open("rb") as stream:
        config = tomllib.load(stream)
    allowed = {
        "schema_version",
        "plugin_api_version",
        "python_min",
        "snippet_timeout_seconds",
        "snippet_timeout_hard_max_seconds",
        "plugin_timeout_seconds",
        "output_limit_bytes",
        "max_text_scan_bytes",
        "max_table_columns",
        "attributions",
        "baseline",
        "unit_prefixes",
        "required_locales",
        "root_indexes",
        "known_check_ids",
        "allowlists",
        "path_migrations",
    }
    unknown = set(config) - allowed
    if unknown:
        raise ConfigError(f"unknown config keys: {', '.join(sorted(unknown))}")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError("unsupported config schema_version")
    if config.get("plugin_api_version") != 1:
        raise ConfigError("unsupported plugin_api_version")
    required_keys = allowed - {"allowlists", "path_migrations"}
    missing = sorted(required_keys - set(config))
    if missing:
        raise ConfigError(f"missing config keys: {', '.join(missing)}")
    try:
        hard = int(config.get("snippet_timeout_hard_max_seconds", 10))
        default = int(config.get("snippet_timeout_seconds", 5))
        plugin_timeout = int(config.get("plugin_timeout_seconds", 30))
        output_limit = int(config.get("output_limit_bytes", 0))
        max_text = int(config.get("max_text_scan_bytes", 0))
        max_columns = int(config.get("max_table_columns", 0))
    except (TypeError, ValueError) as exc:
        raise ConfigError("numeric limits must be integers") from exc
    if not 0 < default <= hard <= 60:
        raise ConfigError("invalid snippet timeout bounds")
    if not 0 < plugin_timeout <= 60:
        raise ConfigError("invalid plugin_timeout_seconds")
    if output_limit not in range(1024, 1_048_577):
        raise ConfigError("invalid output_limit_bytes")
    if max_text not in range(1024, 16_777_217):
        raise ConfigError("invalid max_text_scan_bytes")
    if not 2 <= max_columns <= 20:
        raise ConfigError("invalid max_table_columns")
    if not re.fullmatch(r"3\.\d+", str(config.get("python_min", ""))):
        raise ConfigError("python_min must be a Python 3 minor version")
    if config.get("required_locales") != list(LANGUAGE_FILES):
        raise ConfigError("required_locales must use the canonical five-document contract")
    expected_indexes = ["README.md", "README.en.md", "README.es.md", "README.ca.md", "README.sv.md", "README.ar.md"]
    if config.get("root_indexes") != expected_indexes:
        raise ConfigError("root_indexes must use the canonical six-document contract")
    prefixes = config.get("unit_prefixes")
    if not isinstance(prefixes, list) or not prefixes or any(
        not isinstance(item, str) or not item or "/" in item or "\\" in item for item in prefixes
    ):
        raise ConfigError("unit_prefixes must be non-empty directory-name prefixes")
    known_check_ids = config.get("known_check_ids")
    if (
        not isinstance(known_check_ids, list)
        or len(known_check_ids) != len(set(known_check_ids))
        or any(
            not isinstance(item, str)
            or not re.fullmatch(r"[a-z][a-z0-9_-]*(?::[a-z][a-z0-9_-]*)+", item)
            for item in known_check_ids
        )
    ):
        raise ConfigError("known_check_ids must be unique stable namespaced identifiers")
    for key in ("attributions", "baseline"):
        value = config.get(key)
        if not isinstance(value, str) or not value:
            raise ConfigError(f"{key} must be a repository-relative path")
        safe_relative(root / value, root)
    migrations = config.get("path_migrations", [])
    if not isinstance(migrations, list):
        raise ConfigError("path_migrations must be a list")
    old_paths: set[str] = set()
    for migration in migrations:
        if not isinstance(migration, dict) or set(migration) != {"old", "new"}:
            raise ConfigError("each path migration must contain only old and new")
        old = migration["old"]
        new = migration["new"]
        if not isinstance(old, str) or not isinstance(new, str) or old in old_paths:
            raise ConfigError("path migrations require unique string paths")
        if any(token in old + new for token in ("*", "?", "[")):
            raise ConfigError("wildcard path migrations are forbidden")
        safe_relative(root / old, root)
        safe_relative(root / new, root)
        old_paths.add(old)
    allowlists = config.get("allowlists", {})
    unknown_allowlists = set(allowlists) - {"artifact_paths", "sensitive_rules"}
    if unknown_allowlists:
        raise ConfigError(f"unknown allowlist keys: {', '.join(sorted(unknown_allowlists))}")
    artifact_paths = allowlists.get("artifact_paths", [])
    if not isinstance(artifact_paths, list) or len(artifact_paths) != len(set(artifact_paths)):
        raise ConfigError("allowlists.artifact_paths must contain unique exact paths")
    for value in artifact_paths:
        if not isinstance(value, str) or not value:
            raise ConfigError("allowlists.artifact_paths requires non-empty string paths")
        if any(token in value for token in ("*", "?", "[")):
            raise ConfigError("wildcard allowlists are forbidden")
        candidate = (root / value).resolve(strict=False)
        safe_relative(candidate, root)
        if not candidate.is_file() or candidate.is_symlink():
            raise ConfigError(f"allowlists.artifact_paths path must be an existing regular file: {value}")
    sensitive_rules = allowlists.get("sensitive_rules", [])
    if not isinstance(sensitive_rules, list):
        raise ConfigError("allowlists.sensitive_rules must be a list")
    normalized_sensitive: set[tuple[str, str]] = set()
    for item in sensitive_rules:
        if not isinstance(item, dict) or set(item) != {"path", "rule"}:
            raise ConfigError("each sensitive allowlist must contain only path and rule")
        value = item["path"]
        rule = item["rule"]
        if rule not in {"hygiene.sensitive", "hygiene.personal_data"}:
            raise ConfigError("sensitive allowlist rule must name one supported hygiene rule")
        if not isinstance(value, str) or not value or any(token in value for token in ("*", "?", "[")):
            raise ConfigError("sensitive allowlists require exact non-wildcard paths")
        if (value, rule) in normalized_sensitive:
            raise ConfigError("allowlists.sensitive_rules contains a duplicate path/rule")
        normalized_sensitive.add((value, rule))
        candidate = (root / value).resolve(strict=False)
        safe_relative(candidate, root)
        if not candidate.is_file() or candidate.is_symlink():
            raise ConfigError(f"sensitive allowlist path must be an existing regular file: {value}")
    return config


def discover_units(root: Path, config: dict[str, Any]) -> list[Path]:
    units: list[Path] = []
    prefixes = tuple(config["unit_prefixes"])
    for child in sorted(root.iterdir(), key=lambda item: item.name):
        if child.is_symlink():
            if child.name.startswith(prefixes):
                raise ConfigError(f"content unit may not be a symlink: {child.name}")
            continue
        if child.is_dir() and child.name.startswith(prefixes):
            units.append(child)
    return units


def github_slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[`*_~]", "", text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text)


def parse_metadata(payload: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in shlex.split(payload):
        if "=" not in token:
            raise ValueError("metadata entries must use key=value")
        key, value = token.split("=", 1)
        if key in result:
            raise ValueError(f"duplicate metadata key: {key}")
        if key not in {"timeout", "expect", "expect-error", "path", "check", "fixture"}:
            raise ValueError(f"unknown metadata key: {key}")
        result[key] = value
    return result


def scan_markdown(path: Path, root: Path, config: dict[str, Any]) -> ScanResult:
    rel = safe_relative(path, root)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    result = ScanResult()
    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_language = ""
    fence_class: str | None = None
    fence_start = 0
    fence_lines: list[str] = []
    fence_metadata: dict[str, str] = {}
    pending_metadata: dict[str, str] = {}
    pending_metadata_line: int | None = None
    heading_levels: list[int] = []
    slug_counts: Counter[str] = Counter()

    for number, line in enumerate(lines, 1):
        match = FENCE_RE.match(line)
        if match:
            delimiter, info = match.groups()
            if not in_fence:
                if pending_metadata and pending_metadata_line != number - 1:
                    result.diagnostics.append(
                        Diagnostic(
                            "fence.metadata_orphan",
                            rel,
                            "bookcheck metadata is not immediately adjacent to its fenced block",
                            "place one metadata comment directly above the fence with no blank line",
                            line=pending_metadata_line,
                            construct=repr(sorted(pending_metadata.items())),
                        )
                    )
                    pending_metadata = {}
                fence_metadata = dict(pending_metadata)
                pending_metadata = {}
                pending_metadata_line = None
                in_fence = True
                fence_char = delimiter[0]
                fence_len = len(delimiter)
                fence_start = number
                tokens = info.strip().split()
                fence_language = tokens[0] if tokens else ""
                classes = [token for token in tokens[1:] if token in CLASSIFICATIONS]
                fence_class = classes[0] if len(classes) == 1 else None
                if not fence_language or len(classes) != 1:
                    result.diagnostics.append(
                        Diagnostic(
                            "fence.classification",
                            rel,
                            "fenced block must declare one language and exactly one accepted classification",
                            "use '<language> runnable|expected-error|compile-only|source-ref|todo|illustrative|output'",
                            line=number,
                            construct=line.strip(),
                        )
                    )
                unknown_classes = set(tokens[1:]) - CLASSIFICATIONS
                if unknown_classes:
                    result.diagnostics.append(
                        Diagnostic(
                            "fence.info_unknown",
                            rel,
                            "fenced block contains an unknown info-string token",
                            "remove the token or use the documented classification taxonomy",
                            line=number,
                            construct=" ".join(sorted(unknown_classes)),
                        )
                    )
                fence_lines = []
            elif delimiter[0] == fence_char and len(delimiter) >= fence_len and not info.strip():
                in_fence = False
                result.fences.append(
                    Fence(
                        fence_language,
                        fence_class,
                        "\n".join(fence_lines),
                        fence_start,
                        fence_metadata,
                        number,
                    )
                )
                fence_metadata = {}
            else:
                fence_lines.append(line)
            continue
        if in_fence:
            fence_lines.append(line)
            continue

        if pending_metadata:
            result.diagnostics.append(
                Diagnostic(
                    "fence.metadata_orphan",
                    rel,
                    "bookcheck metadata is not immediately adjacent to its fenced block",
                    "place one metadata comment directly above the fence with no blank line",
                    line=pending_metadata_line,
                    construct=repr(sorted(pending_metadata.items())),
                )
            )
            pending_metadata = {}
            pending_metadata_line = None

        metadata = METADATA_RE.match(line)
        if metadata:
            if metadata.group(1).strip() in STRUCTURAL_MARKERS:
                continue
            try:
                pending_metadata = parse_metadata(metadata.group(1))
                pending_metadata_line = number
            except ValueError as exc:
                result.diagnostics.append(
                    Diagnostic(
                        "fence.metadata",
                        rel,
                        str(exc),
                        "use unique documented bookcheck key=value metadata",
                        line=number,
                        construct=metadata.group(1),
                    )
                )
            continue

        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            heading_levels.append(level)
            slug = github_slug(title)
            ordinal = slug_counts[slug]
            slug_counts[slug] += 1
            anchor = slug if ordinal == 0 else f"{slug}-{ordinal}"
            if anchor in result.anchors:
                result.diagnostics.append(
                    Diagnostic(
                        "markdown.anchor_collision",
                        rel,
                        "heading anchor collides with an explicit anchor",
                        "rename the explicit anchor or heading to keep fragments unambiguous",
                        line=number,
                        construct=anchor,
                    )
                )
            result.headings.append((level, title, number))
            result.anchors.add(anchor)
        for explicit_anchor in HTML_ANCHOR_RE.findall(line):
            if explicit_anchor in result.anchors:
                result.diagnostics.append(
                    Diagnostic(
                        "markdown.anchor_collision",
                        rel,
                        "explicit anchor is duplicated or collides with a heading",
                        "use one unique stable anchor ID",
                        line=number,
                        construct=explicit_anchor,
                    )
                )
            result.anchors.add(explicit_anchor)
        markdown_link_spans = [match.span() for match in LINK_RE.finditer(line)]
        prose_characters = list(line)
        for inline_match in INLINE_CODE_RE.finditer(line):
            start, end = inline_match.span()
            contained_in_link = any(
                link_start <= start and end <= link_end
                for link_start, link_end in markdown_link_spans
            )
            if contained_in_link:
                delimiter_length = len(inline_match.group(1))
                prose_characters[start:start + delimiter_length] = " " * delimiter_length
                prose_characters[end - delimiter_length:end] = " " * delimiter_length
            else:
                prose_characters[start:end] = " " * (end - start)
        prose_line = "".join(prose_characters)
        link_candidates: list[tuple[bool, str, str]] = [
            (bool(image), label, target) for image, label, target in LINK_RE.findall(prose_line)
        ]
        for attributes, target, body in HTML_LINK_RE.findall(prose_line):
            label = re.sub(r"<[^>]+>", "", body).strip()
            link_candidates.append((False, label, target))
        for image_match in HTML_IMAGE_RE.finditer(prose_line):
            attributes = {key.lower(): value for key, value in HTML_ATTR_RE.findall(image_match.group(1))}
            if "src" in attributes:
                link_candidates.append((True, attributes.get("alt", ""), attributes["src"]))
        for image, label, target in link_candidates:
            result.links.append((bool(image), label, target.strip(), number))
            if not image and not label.strip():
                result.diagnostics.append(
                    Diagnostic(
                        "a11y.link_text",
                        rel,
                        "link text is empty",
                        "add concise text that describes the destination",
                        line=number,
                        construct=target,
                    )
                )
            elif not image and label.strip().lower() in GENERIC_LINK_TEXT:
                result.diagnostics.append(
                    Diagnostic(
                        "a11y.link_text",
                        rel,
                        "link text is generic or positional",
                        "describe the destination in the link text",
                        severity="warning",
                        line=number,
                        construct=label.strip().lower(),
                    )
                )
            if image and not label.strip() and "bookcheck: decorative" not in "\n".join(lines[max(0, number - 3):number]):
                result.diagnostics.append(
                    Diagnostic(
                        "a11y.image_alt",
                        rel,
                        "meaningful image has empty alt text",
                        "add concise alt text or the documented decorative marker",
                        line=number,
                        construct=target,
                    )
                )
            if image and label.strip():
                nearby = "\n".join(lines[max(0, number - 4):min(len(lines), number + 3)])
                nearby_lines = lines[max(0, number - 4):min(len(lines), number + 3)]
                prose_equivalent = any(
                    candidate.strip()
                    and not candidate.lstrip().startswith("<!--")
                    and HEADING_RE.match(candidate) is None
                    and not LINK_RE.fullmatch(candidate.strip())
                    and not HTML_IMAGE_RE.fullmatch(candidate.strip())
                    for candidate in nearby_lines
                    if candidate != line
                )
                if label.strip().lower() in GENERIC_IMAGE_ALT:
                    result.diagnostics.append(
                        Diagnostic(
                            "a11y.image_alt",
                            rel,
                            "meaningful image alt text is generic or positional",
                            "describe the visual's relevant content or purpose",
                            line=number,
                            construct=label.strip().lower(),
                        )
                    )
                if "bookcheck: visual-text-equivalent" not in nearby or not prose_equivalent:
                    result.diagnostics.append(
                        Diagnostic(
                            "a11y.visual_equivalent",
                            rel,
                            "meaningful image has no marked nearby prose equivalent",
                            "add nearby explanatory prose plus <!-- bookcheck: visual-text-equivalent -->",
                            line=number,
                            construct=target,
                        )
                    )
    if pending_metadata:
        result.diagnostics.append(
            Diagnostic(
                "fence.metadata_orphan",
                rel,
                "bookcheck metadata is not immediately adjacent to a fenced block",
                "place the metadata directly above the fence or remove it",
                line=pending_metadata_line,
                construct=repr(sorted(pending_metadata.items())),
            )
        )

    if in_fence:
        result.diagnostics.append(
            Diagnostic(
                "markdown.fence_unclosed",
                rel,
                "fenced block is not closed",
                "close it with the same delimiter type and at least the opening length",
                line=fence_start,
                construct=f"{fence_char}:{fence_len}",
            )
        )
    h1_count = sum(level == 1 for level, _, _ in result.headings)
    if h1_count != 1:
        result.diagnostics.append(
            Diagnostic(
                "markdown.h1_count",
                rel,
                f"document has {h1_count} H1 headings",
                "use exactly one H1 per document",
                construct=str(h1_count),
            )
        )
    previous = 0
    for level, title, number in result.headings:
        if previous and level > previous + 1:
            result.diagnostics.append(
                Diagnostic(
                    "markdown.heading_skip",
                    rel,
                    "heading hierarchy skips a level",
                    "introduce headings one level at a time",
                    line=number,
                    construct=f"{previous}>{level}:{github_slug(title)}",
                )
            )
        previous = level
    for slug, count in slug_counts.items():
        if slug and count > 1:
            result.diagnostics.append(
                Diagnostic(
                    "markdown.duplicate_anchor",
                    rel,
                    "multiple headings produce the same base anchor",
                    "rename headings or add deliberate unique aliases",
                    construct=f"{slug}:{count}",
                )
            )
    for index, fence in enumerate(result.fences):
        allowed_metadata = {
            "runnable": {"timeout", "expect", "fixture"},
            "expected-error": {"timeout", "expect-error", "fixture"},
            "compile-only": set(),
            "source-ref": {"path", "check"},
            "todo": set(),
            "illustrative": set(),
            "output": set(),
        }.get(fence.classification, set())
        incompatible = set(fence.metadata) - allowed_metadata
        if incompatible:
            result.diagnostics.append(
                Diagnostic(
                    "fence.metadata_incompatible",
                    rel,
                    "bookcheck metadata is incompatible with this fence classification",
                    "keep only the metadata keys documented for this classification",
                    line=fence.line,
                    construct=f"{fence.classification}:{','.join(sorted(incompatible))}",
                )
            )
        if fence.classification in {"runnable", "expected-error"} and fence.language != "python":
            result.diagnostics.append(
                Diagnostic(
                    "fence.execution_language",
                    rel,
                    "generic runnable and expected-error fences must use Python",
                    "classify non-Python behavior as source-ref with a domain check or as illustrative",
                    line=fence.line,
                    construct=f"{fence.language}:{fence.classification}",
                )
            )
        if fence.classification == "compile-only" and fence.language != "python":
            result.diagnostics.append(
                Diagnostic(
                    "fence.compile_language",
                    rel,
                    "generic compile-only verification supports Python only",
                    "use source-ref with a stable domain check for other languages",
                    line=fence.line,
                    construct=fence.language,
                )
            )
        if fence.classification == "output":
            previous = result.fences[index - 1] if index else None
            intervening = []
            if previous is not None and previous.end_line is not None:
                intervening = [
                    item for item in lines[previous.end_line:fence.line - 1] if item.strip()
                ]
            if (
                previous is None
                or previous.classification not in {"runnable", "expected-error"}
                or intervening
            ):
                result.diagnostics.append(
                    Diagnostic(
                        "fence.output_orphan",
                        rel,
                        "output block is not associated with a runnable or expected-error block",
                        "place it directly after the executable evidence it documents",
                        line=fence.line,
                        construct=hashlib.sha256(fence.code.encode()).hexdigest(),
                    )
                )
    return result


def check_unit_shape(root: Path, config: dict[str, Any], units: Sequence[Path]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    required = tuple(config["required_locales"])
    for unit in units:
        for filename in required:
            candidate = unit / filename
            if candidate.is_symlink():
                diagnostics.append(
                    Diagnostic(
                        "unit.locale_symlink",
                        safe_relative(candidate, root),
                        "localized public document may not be a symlink",
                        "store the document as a regular repository file",
                        construct=filename,
                    )
                )
            elif not candidate.is_file():
                diagnostics.append(
                    Diagnostic(
                        "unit.locale_missing",
                        safe_relative(unit, root),
                        f"required localized document is missing: {filename}",
                        "add the complete localized sibling before publishing the unit",
                        construct=filename,
                    )
                )
        for candidate in sorted(unit.glob("README*.md")):
            if candidate.name not in required:
                diagnostics.append(
                    Diagnostic(
                        "unit.locale_unexpected",
                        safe_relative(candidate, root),
                        "unit contains an unsupported or misnamed localized README",
                        "use only README.md plus the es, ca, sv, and ar siblings",
                        construct=candidate.name,
                    )
                )
    for filename in config["root_indexes"]:
        if not (root / filename).is_file():
            diagnostics.append(
                Diagnostic(
                    "root.index_missing",
                    filename,
                    "required root index is missing",
                    "restore the localized root index",
                    construct=filename,
                )
            )
    english = root / "README.md"
    mirror = root / "README.en.md"
    if english.exists() and mirror.exists() and english.read_bytes() != mirror.read_bytes():
        diagnostics.append(
            Diagnostic(
                "root.english_mirror",
                "README.en.md",
                "root English index is not byte-identical to README.md",
                "copy the canonical root README.md content exactly",
                construct=hashlib.sha256(mirror.read_bytes()).hexdigest(),
            )
        )
    return diagnostics


def check_selectors(path: Path, root: Path) -> list[Diagnostic]:
    rel = safe_relative(path, root)
    first = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
    diagnostics: list[Diagnostic] = []
    selector_links = [
        (label.strip(), target.strip())
        for image, label, target in LINK_RE.findall(first)
        if not image
    ]
    own_target = (path.parent / path.name).resolve()
    for label, target in selector_links:
        try:
            resolved, fragment = resolve_local_target(path, target, root)
        except ConfigError:
            continue
        if resolved == own_target:
            diagnostics.append(
                Diagnostic(
                    "navigation.selector_self_link",
                    rel,
                    "language selector links the currently selected language to itself",
                    "render the current language as text and link only the other variants",
                    construct=target,
                )
            )
    for filename, language in LANGUAGE_FILES.items():
        if path.name == filename:
            continue
        expected = (path.parent / filename).resolve()
        candidates = [target for label, target in selector_links if label == SELECTOR_LABELS[filename]]
        if not candidates:
            diagnostics.append(
                Diagnostic(
                    "navigation.selector_missing",
                    rel,
                    f"language selector does not link {language}",
                    "restore the standard English, Spanish, Catalan, Swedish, Arabic selector",
                    construct=filename,
                )
            )
            continue
        valid = False
        for target in candidates:
            try:
                resolved, fragment = resolve_local_target(path, target, root)
            except ConfigError:
                continue
            if resolved == expected and not fragment:
                valid = True
                break
        if not valid:
            diagnostics.append(
                Diagnostic(
                    "navigation.selector_target",
                    rel,
                    f"language selector points {language} outside its exact sibling document",
                    "link the language label to its matching README in the same unit",
                    construct=f"{filename}:{'|'.join(candidates)}",
                )
            )
    labels = ("English", "Español", "Català", "Svenska", "العربية")
    positions = [first.find(label) for label in labels]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        diagnostics.append(
            Diagnostic(
                "navigation.selector_order",
                rel,
                "language selector is missing a label or uses a non-standard order",
                "use English, Español, Català, Svenska, العربية in that order",
                construct=":".join(map(str, positions)),
            )
        )
    return diagnostics


def check_root_navigation(path: Path, root: Path, scan: ScanResult) -> list[Diagnostic]:
    if path.parent != root:
        return []
    expected = {
        "README.md": "README.md",
        "README.en.md": "README.md",
        "README.es.md": "README.es.md",
        "README.ca.md": "README.ca.md",
        "README.sv.md": "README.sv.md",
        "README.ar.md": "README.ar.md",
    }.get(path.name)
    if expected is None:
        return []
    diagnostics: list[Diagnostic] = []
    chapter_numbers: list[int] = []
    unit_targets: list[str] = []
    for is_image, _label, target, line in scan.links:
        if is_image:
            continue
        parsed = urlsplit(target.strip().strip("<>"))
        normalized = unquote(parsed.path)
        if not normalized.startswith(("chapter-", "appendix-")):
            continue
        unit_targets.append(normalized)
        if normalized.startswith("chapter-"):
            match = re.match(r"chapter-(\d+)-", normalized)
            if match:
                chapter_numbers.append(int(match.group(1)))
        if PurePosixPath(normalized).name != expected:
            diagnostics.append(
                Diagnostic(
                    "navigation.root_language",
                    path.name,
                    "root index points a unit entry to the wrong language file",
                    "link each root index entry to its matching localized README",
                    line=line,
                    construct=normalized,
                )
            )
    expected_targets: set[str] = set()
    for unit in root.iterdir():
        if not unit.is_dir() or not unit.name.startswith(("chapter-", "appendix-")):
            continue
        target = unit / expected
        if target.is_file():
            expected_targets.add(f"{unit.name}/{expected}")
    actual_counts = Counter(unit_targets)
    for target in sorted(expected_targets - set(actual_counts)):
        diagnostics.append(
            Diagnostic(
                "navigation.unit_missing",
                path.name,
                "root index omits an implemented unit",
                "add the localized unit target in chapter/appendix order",
                construct=target,
            )
        )
    for target, count in sorted(actual_counts.items()):
        if count > 1:
            diagnostics.append(
                Diagnostic(
                    "navigation.unit_duplicate",
                    path.name,
                    "root index links the same unit more than once",
                    "keep one navigation entry per implemented unit",
                    construct=f"{target}:{count}",
                )
            )
    if chapter_numbers != sorted(chapter_numbers):
        diagnostics.append(
            Diagnostic(
                "navigation.chapter_order",
                path.name,
                "root chapter entries are not in numeric order",
                "keep implemented chapters in numeric order before appendices",
                construct=":".join(map(str, chapter_numbers)),
            )
        )
    first_appendix = next(
        (index for index, target in enumerate(unit_targets) if target.startswith("appendix-")),
        None,
    )
    if first_appendix is not None and any(
        target.startswith("chapter-") for target in unit_targets[first_appendix + 1:]
    ):
        diagnostics.append(
            Diagnostic(
                "navigation.appendix_order",
                path.name,
                "a chapter entry appears after an appendix",
                "list every implemented chapter in numeric order before the appendices",
                construct=hashlib.sha256(repr(unit_targets).encode()).hexdigest(),
            )
        )
    return diagnostics


def resolve_local_target(source: Path, target: str, root: Path) -> tuple[Path, str]:
    parsed = urlsplit(target.strip().strip("<>"))
    raw_path = unquote(parsed.path)
    fragment = unquote(parsed.fragment)
    candidate = source if not raw_path else source.parent / raw_path
    resolved = candidate.resolve(strict=False)
    safe_relative(resolved, root)
    return resolved, fragment


def check_links(path: Path, root: Path, scan: ScanResult, scans: dict[Path, ScanResult]) -> list[Diagnostic]:
    rel = safe_relative(path, root)
    diagnostics: list[Diagnostic] = []
    for is_image, label, target, line in scan.links:
        parsed = urlsplit(target.strip().strip("<>"))
        if parsed.scheme in {"http", "https", "mailto"}:
            if parsed.scheme in {"http", "https"} and not parsed.netloc:
                diagnostics.append(
                    Diagnostic(
                        "link.external_syntax",
                        rel,
                        "external URL has no host",
                        "use a syntactically complete URL; availability is not checked",
                        line=line,
                        construct=target,
                    )
                )
            continue
        try:
            resolved, fragment = resolve_local_target(path, target, root)
        except ConfigError:
            diagnostics.append(
                Diagnostic(
                    "link.path_escape",
                    rel,
                    "local link escapes the repository",
                    "use a repository-relative target",
                    line=line,
                    construct=target,
                )
            )
            continue
        if not resolved.exists():
            diagnostics.append(
                Diagnostic(
                    "link.missing",
                    rel,
                    "local link target does not exist",
                    "fix the relative path or add the target before linking it",
                    line=line,
                    construct=target,
                )
            )
            continue
        if fragment and resolved.suffix.lower() == ".md":
            target_scan = scans.get(resolved)
            if target_scan is None:
                target_scan = scan_markdown(resolved, root, {})
                scans[resolved] = target_scan
            if fragment not in target_scan.anchors:
                diagnostics.append(
                    Diagnostic(
                        "link.fragment_missing",
                        rel,
                        "local heading fragment does not exist",
                        "use an existing heading anchor or add an explicit stable alias",
                        line=line,
                        construct=f"{safe_relative(resolved, root)}#{fragment}",
                    )
                )
    return diagnostics


def check_arabic(path: Path, root: Path) -> list[Diagnostic]:
    if path.name != "README.ar.md":
        return []
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    bidi_controls = set("\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
    control_lines = [
        number for number, line in enumerate(raw_lines, 1) if any(character in bidi_controls for character in line)
    ]
    if control_lines:
        return [
            Diagnostic(
                "rtl.invisible_control",
                safe_relative(path, root),
                "Arabic document contains invisible bidi control characters",
                "remove invisible controls and use visible Markdown/HTML structure for LTR technical text",
                line=control_lines[0],
                construct=":".join(map(str, control_lines)),
            )
        ]
    visible_lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in raw_lines:
        match = FENCE_RE.match(line)
        if match:
            delimiter, info = match.groups()
            if not in_fence:
                in_fence = True
                fence_char = delimiter[0]
                fence_len = len(delimiter)
            elif delimiter[0] == fence_char and len(delimiter) >= fence_len and not info.strip():
                in_fence = False
            visible_lines.append("")
            continue
        visible_lines.append("" if in_fence else line)
    text = "\n".join(visible_lines)
    opens = len(re.findall(r"<div\s+dir=[\"']rtl[\"']\s*>", text, re.I))
    closes = len(re.findall(r"</div\s*>", text, re.I))
    nonblank = [line.strip() for line in visible_lines if line.strip()]
    encloses = bool(nonblank) and re.fullmatch(r"<div\s+dir=[\"']rtl[\"']\s*>", nonblank[0], re.I) is not None and nonblank[-1].lower() == "</div>"
    if opens == 1 and closes == 1 and encloses:
        return []
    return [
        Diagnostic(
            "rtl.outer_wrapper",
            safe_relative(path, root),
            f"Arabic document has {opens} RTL opens, {closes} closes, outer={encloses}",
            "wrap the document in exactly one balanced outer <div dir=\"rtl\">",
            construct=f"{opens}:{closes}:{encloses}",
        )
    ]


def table_diagnostics(path: Path, root: Path, config: dict[str, Any]) -> list[Diagnostic]:
    text = path.read_text(encoding="utf-8")
    raw_lines = text.splitlines()
    lines: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in raw_lines:
        match = FENCE_RE.match(line)
        if match:
            delimiter, info = match.groups()
            if not in_fence:
                in_fence = True
                fence_char = delimiter[0]
                fence_len = len(delimiter)
            elif delimiter[0] == fence_char and len(delimiter) >= fence_len and not info.strip():
                in_fence = False
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    diagnostics: list[Diagnostic] = []

    def cells(line: str) -> list[str]:
        return [part.strip() for part in line.strip().strip("|").split("|")]

    def table_like(line: str) -> bool:
        return "|" in line and len(cells(line)) >= 2

    def separator(line: str) -> bool:
        return table_like(line) and all(re.fullmatch(r":?-{3,}:?", part) for part in cells(line))

    for index in range(len(lines) - 1):
        if not table_like(lines[index]):
            continue
        if table_like(lines[index + 1]) and not separator(lines[index + 1]):
            if index == 0 or not table_like(lines[index - 1]):
                diagnostics.append(
                    Diagnostic(
                        "a11y.table_header",
                        safe_relative(path, root),
                        "table-like rows have no Markdown header separator",
                        "add a header row followed by a matching --- separator row",
                        line=index + 1,
                        construct=hashlib.sha256(lines[index].encode()).hexdigest(),
                    )
                )
            continue
        if not separator(lines[index + 1]):
            continue
        columns = len(cells(lines[index]))
        if len(cells(lines[index + 1])) != columns:
            diagnostics.append(
                Diagnostic(
                    "a11y.table_columns",
                    safe_relative(path, root),
                    "table header and separator use different column counts",
                    "make the separator define exactly one cell per header cell",
                    line=index + 1,
                    construct=f"{columns}:{len(cells(lines[index + 1]))}",
                )
            )
        if columns > int(config.get("max_table_columns", 4)):
            nearby = "\n".join(lines[max(0, index - 3):index + 1])
            if "bookcheck: table-alternative" not in nearby:
                diagnostics.append(
                    Diagnostic(
                        "a11y.table_alternative",
                        safe_relative(path, root),
                        "wide table has no marked text/list alternative",
                        "add a nearby <!-- bookcheck: table-alternative --> marker and readable alternative",
                        line=index + 1,
                        construct=f"columns:{columns}",
                    )
                )
    return diagnostics


def unsafe_python_reason(code: str) -> str | None:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    forbidden_imports = {
        "socket",
        "subprocess",
        "multiprocessing",
        "requests",
        "urllib",
        "http",
        "ftplib",
        "ctypes",
    }
    stdlib_modules = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    directly_called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    def import_is_dormant(node: ast.AST) -> bool:
        parent = parents.get(node)
        while parent is not None:
            if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return parent.name not in directly_called
            parent = parents.get(parent)
        return False

    destructive_aliases: set[str] = set()
    path_constructor_names = {"Path"}
    pathlib_aliases = {"pathlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".")[0]
                if root_name not in stdlib_modules and not import_is_dormant(node):
                    return f"dependency import {alias.name}"
                if root_name in forbidden_imports:
                    return f"forbidden import {alias.name}"
                if root_name in {"os", "shutil"}:
                    destructive_aliases.add(alias.asname or root_name)
                if root_name == "pathlib":
                    pathlib_aliases.add(alias.asname or root_name)
        if isinstance(node, ast.ImportFrom):
            root_name = (node.module or "").split(".")[0]
            if (
                node.level
                or not root_name
                or (root_name not in stdlib_modules and not import_is_dormant(node))
            ):
                return f"dependency import {node.module or '<relative>'}"
            if root_name in forbidden_imports:
                return f"forbidden import {node.module}"
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in {"os", "shutil"}:
            for alias in node.names:
                if alias.name in {
                    "remove", "unlink", "rmdir", "removedirs", "rmtree", "system", "popen",
                    "fork", "forkpty", "posix_spawn", "posix_spawnp", "kill", "killpg",
                    "setuid", "seteuid", "setgid", "setegid", "chown", "chmod",
                }:
                    destructive_aliases.add(alias.asname or alias.name)
        if isinstance(node, ast.ImportFrom) and node.module == "pathlib":
            for alias in node.names:
                if alias.name == "Path":
                    path_constructor_names.add(alias.asname or alias.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in destructive_aliases | {"eval", "exec", "__import__"}:
                return f"forbidden operation {node.func.id}"
            if node.func.id == "open" and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str) and Path(node.args[0].value).is_absolute():
                    return "absolute file path"
            if node.func.id in path_constructor_names and node.args and isinstance(node.args[0], ast.Constant):
                if isinstance(node.args[0].value, str) and Path(node.args[0].value).is_absolute():
                    return "absolute file path"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (
                node.func.attr == "Path"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in pathlib_aliases
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and Path(node.args[0].value).is_absolute()
            ):
                return "absolute file path"
            # ``list.remove`` is an ordinary in-memory teaching operation. File
            # deletion through pathlib remains forbidden here, while imports of
            # os/shutil/subprocess are rejected above before calls can run.
            if node.func.attr in {
                "system", "popen", "unlink", "rmdir", "rmtree", "fork", "forkpty",
                "posix_spawn", "posix_spawnp", "kill", "killpg", "setuid", "seteuid",
                "setgid", "setegid", "chown", "chmod", "open_connection", "start_server",
                "create_connection", "create_server",
            }:
                return f"forbidden operation {node.func.attr}"
            if node.func.attr == "remove" and isinstance(node.func.value, ast.Name):
                if node.func.value.id in destructive_aliases:
                    return "forbidden operation remove"
            if node.func.attr in {"open", "write_text", "write_bytes"} and isinstance(node.func.value, ast.Call):
                constructor = node.func.value
                if (
                    isinstance(constructor.func, ast.Name)
                    and constructor.func.id == "Path"
                    and constructor.args
                    and isinstance(constructor.args[0], ast.Constant)
                    and isinstance(constructor.args[0].value, str)
                    and Path(constructor.args[0].value).is_absolute()
                ):
                    return "absolute file path"
    return None


def run_python_fence(fence: Fence, path: Path, root: Path, config: dict[str, Any]) -> list[Diagnostic]:
    rel = safe_relative(path, root)
    if fence.classification not in {"runnable", "expected-error", "compile-only"} or fence.language != "python":
        return []
    if fence.classification == "compile-only":
        try:
            compile(fence.code, rel, "exec")
            return []
        except SyntaxError as exc:
            return [
                Diagnostic(
                    "snippet.compile",
                    rel,
                    "compile-only Python block does not compile",
                    "fix the syntax or classify an intentional incomplete block as todo",
                    line=fence.line + (exc.lineno or 1),
                    construct=hashlib.sha256(fence.code.encode()).hexdigest(),
                )
            ]
    reason = unsafe_python_reason(fence.code)
    if reason:
        return [
            Diagnostic(
                "snippet.unsafe_generic",
                rel,
                "generic runner refused a dependency, process, network, or destructive operation",
                "move the example to a source-ref and domain companion test/plugin",
                line=fence.line,
                construct=reason,
            )
        ]
    try:
        timeout = int(fence.metadata.get("timeout", config["snippet_timeout_seconds"]))
    except (TypeError, ValueError):
        return [
            Diagnostic(
                "snippet.timeout_metadata",
                rel,
                "snippet timeout metadata is not an integer",
                "use a whole number of seconds within the configured bound",
                line=fence.line,
                construct=repr(fence.metadata.get("timeout")),
            )
        ]
    if not 0 < timeout <= int(config["snippet_timeout_hard_max_seconds"]):
        return [
            Diagnostic(
                "snippet.timeout_metadata",
                rel,
                "snippet timeout is outside the accepted bound",
                "use a positive timeout no greater than the configured hard maximum",
                line=fence.line,
                construct=str(timeout),
            )
        ]
    environment = {"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8", "LANG": "C.UTF-8"}
    fixture_source: Path | None = None
    fixture = fence.metadata.get("fixture")
    if fixture:
        fixture_source = (root / fixture).resolve(strict=False)
        try:
            safe_relative(fixture_source, root)
        except ConfigError:
            fixture_source = Path("/__invalid__")
        if (
            not fixture_source.is_file()
            or fixture_source.is_symlink()
            or fixture_source.stat().st_size > int(config["max_text_scan_bytes"])
        ):
            return [
                Diagnostic(
                    "snippet.fixture",
                    rel,
                    "snippet fixture is missing, escaping, linked, or oversized",
                    "use one bounded regular repository file as the fixture",
                    line=fence.line,
                    construct=fixture,
                )
            ]
    try:
        fixture_mutated = False
        with tempfile.TemporaryDirectory(prefix="bookcheck-") as temp:
            if fixture_source is not None:
                fixture_target = Path(temp) / fixture_source.name
                shutil.copyfile(fixture_source, fixture_target)
                fixture_target.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
                fixture_digest = hashlib.sha256(fixture_target.read_bytes()).digest()
            completed = run_bounded(
                [sys.executable, "-I", "-B", "-c", fence.code],
                cwd=temp,
                env=environment,
                timeout=timeout,
                output_limit=int(config["output_limit_bytes"]),
            )
            if fixture_source is not None:
                fixture_mutated = (
                    not fixture_target.is_file()
                    or hashlib.sha256(fixture_target.read_bytes()).digest() != fixture_digest
                )
    except subprocess.TimeoutExpired:
        return [
            Diagnostic(
                "snippet.timeout",
                rel,
                "Python snippet exceeded its bounded timeout",
                "make the example terminate deterministically or use a domain source-ref",
                line=fence.line,
                construct=hashlib.sha256(fence.code.encode()).hexdigest(),
            )
        ]
    except OutputLimitExceeded:
        return [
            Diagnostic(
                "snippet.output_limit",
                rel,
                "Python snippet exceeded the combined output bound",
                "reduce output or verify the example through a companion test",
                line=fence.line,
                construct=hashlib.sha256(fence.code.encode()).hexdigest(),
            )
        ]
    except SurvivingDescendantError:
        return [
            Diagnostic(
                "snippet.descendant",
                rel,
                "Python snippet left a surviving descendant process",
                "keep generic examples single-process or use a bounded domain verifier",
                line=fence.line,
                construct=hashlib.sha256(fence.code.encode()).hexdigest(),
            )
        ]
    if fixture_mutated:
        return [
            Diagnostic(
                "snippet.fixture_mutation",
                rel,
                "Python snippet modified its read-only fixture copy",
                "treat fixtures as input and write derived output to a separate temporary path",
                line=fence.line,
                construct=fixture or "",
            )
        ]
    combined = completed.stdout + completed.stderr
    if len(combined) > int(config["output_limit_bytes"]):
        return [
            Diagnostic(
                "snippet.output_limit",
                rel,
                "Python snippet exceeded the combined output bound",
                "reduce output or verify the example through a companion test",
                line=fence.line,
                construct=str(len(combined)),
            )
        ]
    output = completed.stdout.decode("utf-8", "replace").replace("\r\n", "\n").rstrip("\n")
    error = completed.stderr.decode("utf-8", "replace")
    expected = fence.metadata.get("expect")
    if fence.classification == "runnable":
        if completed.returncode != 0:
            return [
                Diagnostic(
                    "snippet.unexpected_failure",
                    rel,
                    "runnable Python snippet exited non-zero",
                    "fix the example or classify and explain an expected error",
                    line=fence.line,
                    construct=hashlib.sha256(error.encode()).hexdigest(),
                )
            ]
        if expected is not None and output != expected.replace("\\n", "\n"):
            return [
                Diagnostic(
                    "snippet.output_mismatch",
                    rel,
                    "runnable Python output does not match declared expectation",
                    "update the code or its stable expected output",
                    line=fence.line,
                    construct=hashlib.sha256(output.encode()).hexdigest(),
                )
            ]
    else:
        expected_error = fence.metadata.get("expect-error")
        if completed.returncode == 0 or not expected_error:
            return [
                Diagnostic(
                    "snippet.expected_error",
                    rel,
                    "expected-error block did not fail with a declared diagnostic",
                    "declare expect-error metadata and ensure the example fails as explained",
                    line=fence.line,
                    construct=str(completed.returncode),
                )
            ]
        if expected_error not in error:
            return [
                Diagnostic(
                    "snippet.error_mismatch",
                    rel,
                    "expected-error diagnostic substring was not observed",
                    "use a stable diagnostic substring or correct the example",
                    line=fence.line,
                    construct=hashlib.sha256(error.encode()).hexdigest(),
                )
            ]
    return []


def source_ref_diagnostics(
    fence: Fence,
    path: Path,
    root: Path,
    known_checks: set[str] | None = None,
    registered_checks: set[str] | None = None,
) -> list[Diagnostic]:
    if fence.classification != "source-ref":
        return []
    rel = safe_relative(path, root)
    source = fence.metadata.get("path")
    check = fence.metadata.get("check")
    if not source or not check:
        return [
            Diagnostic(
                "source_ref.metadata",
                rel,
                "source-ref requires path and check metadata",
                "add a repository-relative companion path and stable verifier/plugin check ID",
                line=fence.line,
                construct=f"{source}:{check}",
            )
        ]
    if not re.fullmatch(r"[a-z][a-z0-9_-]*(?::[a-z][a-z0-9_-]*)+", check):
        return [
            Diagnostic(
                "source_ref.check_id",
                rel,
                "source-ref check ID is not a stable namespaced identifier",
                "use '<plugin-or-runner>:<stable-check>' with lowercase letters, digits, '_' or '-'",
                line=fence.line,
                construct=check,
            )
        ]
    candidate = (root / source).resolve(strict=False)
    try:
        safe_relative(candidate, root)
    except ConfigError:
        candidate = Path("/__invalid__")
    if not candidate.is_file() or candidate.is_symlink():
        return [
            Diagnostic(
                "source_ref.path",
                rel,
                "source-ref companion file is missing or escapes the repository",
                "use an existing repository-relative companion source",
                line=fence.line,
                construct=source,
            )
        ]
    owner = check.split(":", 1)[0]
    if known_checks is not None and check not in known_checks:
        return [
            Diagnostic(
                "source_ref.check",
                rel,
                "source-ref names a check that is not declared by the repository",
                "add the stable check ID to known_check_ids only after its verifier contract exists",
                line=fence.line,
                construct=check,
            )
        ]
    selected_owners = {item.removeprefix("@plugin:") for item in registered_checks or set() if item.startswith("@plugin:")}
    if registered_checks is not None and owner in selected_owners and check not in registered_checks:
        return [
            Diagnostic(
                "source_ref.check",
                rel,
                "source-ref names a check that is not registered by the selected plugins",
                "select the owning plugin or use its exact stable check ID",
                line=fence.line,
                construct=check,
            )
        ]
    return []


def git_paths(root: Path) -> list[str]:
    commands = (
        ["git", "ls-files", "-c", "-o", "--exclude-standard", "-z"],
        ["git", "ls-files", "-i", "-o", "--exclude-standard", "-z"],
    )
    paths: set[str] = set()
    for command in commands:
        completed = subprocess.run(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            raise ConfigError("git path inventory failed")
        paths.update(
            part.decode("utf-8", "surrogateescape") for part in completed.stdout.split(b"\0") if part
        )
    return sorted(paths)


def repository_snapshot(root: Path) -> dict[str, tuple[int, int]]:
    snapshot: dict[str, tuple[int, int]] = {}
    for raw in git_paths(root):
        path = root / raw
        if path.is_file() or path.is_symlink():
            stat = path.lstat()
            snapshot[raw] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def hygiene_diagnostics(root: Path, config: dict[str, Any]) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    allowed_artifacts = set(config.get("allowlists", {}).get("artifact_paths", []))
    allowed_sensitive = {
        (item["path"], item["rule"])
        for item in config.get("allowlists", {}).get("sensitive_rules", [])
    }
    artifact_names = {
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage",
        ".DS_Store", "coverage.xml", "CMakeCache.txt", "cmake_install.cmake",
    }
    artifact_suffixes = {
        ".pyc", ".pyo", ".so", ".dylib", ".dll", ".o", ".obj", ".whl",
        ".pem", ".key", ".crt", ".cer", ".p12", ".pfx",
        ".a", ".lib", ".exe", ".pdb", ".profraw", ".gcda", ".gcno",
    }
    artifact_parts = {
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ".venv", "venv", "build", "dist", "target", "CMakeFiles", "htmlcov",
        ".tox", ".nox", ".hypothesis", ".idea", ".vscode",
    }
    paths = git_paths(root)
    for raw in paths:
        posix = PurePosixPath(raw)
        if raw in allowed_artifacts:
            continue
        if (
            posix.name in artifact_names
            or posix.name.startswith(".coverage.")
            or posix.name.endswith(".egg-info")
            or posix.name.endswith((".tar.gz", ".tar.bz2", ".tar.xz"))
            or posix.suffix.lower() in artifact_suffixes
            or any(part in artifact_parts for part in posix.parts)
            or any(part.endswith(".egg-info") for part in posix.parts)
        ):
            diagnostics.append(
                Diagnostic(
                    "hygiene.artifact",
                    raw,
                    "generated or local artifact is present in the repository tree",
                    "remove it safely or add an exact reviewed teaching-fixture allowlist",
                    construct=raw,
                )
            )
    secret_patterns = [
        re.compile(rb"AKIA[0-9A-Z]{16}"),
        re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),
        re.compile(rb"sk-[A-Za-z0-9]{20,}"),
        re.compile(rb"xox[baprs]-[A-Za-z0-9-]{20,}"),
        re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ]
    personal_patterns = [
        re.compile(rb"(?:student|learner)_(?:email|phone|address)\s*[:=]", re.I),
        re.compile(rb"(?:student|learner)[ -]?(?:id|number)\s*[:=]\s*[0-9]{6,}", re.I),
    ]
    max_bytes = int(config.get("max_text_scan_bytes", 1_048_576))
    for raw in paths:
        path = root / raw
        if not path.is_file() or path.stat().st_size > max_bytes:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\0" in data:
            continue
        if (raw, "hygiene.sensitive") not in allowed_sensitive:
            for pattern in secret_patterns:
                if pattern.search(data):
                    diagnostics.append(
                        Diagnostic(
                            "hygiene.sensitive",
                            raw,
                            "suspected credential or private key material is present; value redacted",
                            "remove it or add one reviewed exact path/rule teaching-fixture allowance",
                            construct=pattern.pattern.decode("ascii", "ignore"),
                        )
                    )
                    break
        if (raw, "hygiene.personal_data") not in allowed_sensitive:
            for pattern in personal_patterns:
                if pattern.search(data):
                    diagnostics.append(
                        Diagnostic(
                            "hygiene.personal_data",
                            raw,
                            "suspected learner personal-data marker is present; value redacted",
                            "replace it with an unmistakably fictional teaching record",
                            construct=pattern.pattern.decode("ascii", "ignore"),
                        )
                    )
                    break
    return diagnostics


def attribution_diagnostics(root: Path, config: dict[str, Any]) -> list[Diagnostic]:
    path = root / config["attributions"]
    if not path.exists():
        return [
            Diagnostic(
                "attribution.inventory_missing",
                config["attributions"],
                "attribution inventory is missing",
                "add the versioned neutral provenance inventory",
                construct=config["attributions"],
            )
        ]
    with path.open("rb") as stream:
        payload = tomllib.load(stream)
    diagnostics: list[Diagnostic] = []
    if payload.get("schema_version") != 1:
        raise ConfigError("unsupported attribution schema_version")
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        raise ConfigError("attribution entries must be a list")
    seen: set[str] = set()
    covered_paths: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ConfigError("attribution entry must be a table")
        unknown_fields = set(entry) - ATTRIBUTION_ENTRY_FIELDS
        if unknown_fields:
            diagnostics.append(
                Diagnostic(
                    "attribution.entry_schema",
                    config["attributions"],
                    "attribution entry contains unknown fields",
                    "use only the versioned attribution inventory schema",
                    construct=f"{entry.get('id', '')}:{','.join(sorted(unknown_fields))}",
                )
            )
        identifier = entry.get("id", "")
        if not identifier or identifier in seen:
            diagnostics.append(
                Diagnostic(
                    "attribution.entry_id",
                    config["attributions"],
                    "attribution entry has a missing or duplicate stable ID",
                    "use a unique non-empty ID",
                    construct=identifier,
                )
            )
        seen.add(identifier)
        paths = entry.get("paths", [])
        if not isinstance(paths, list) or not paths or any(not isinstance(item, str) for item in paths):
            diagnostics.append(
                Diagnostic(
                    "attribution.paths",
                    config["attributions"],
                    "attribution entry must cover at least one string path",
                    "list exact repository-relative paths",
                    construct=identifier,
                )
            )
            paths = []
        for covered in paths:
            if covered in covered_paths:
                diagnostics.append(
                    Diagnostic(
                        "attribution.path_duplicate",
                        config["attributions"],
                        "a path is covered by more than one attribution entry",
                        "merge or disambiguate the provenance decision",
                        construct=covered,
                    )
                )
            covered_paths.add(covered)
            candidate = (root / covered).resolve(strict=False)
            try:
                safe_relative(candidate, root)
            except ConfigError:
                candidate = Path("/__invalid__")
            if not candidate.exists():
                diagnostics.append(
                    Diagnostic(
                        "attribution.path",
                        config["attributions"],
                        "attribution record covers a missing or escaping path",
                        "correct the repository-relative covered path",
                        construct=covered,
                    )
                )
        status = entry.get("status")
        if status == "review-required":
            diagnostics.append(
                Diagnostic(
                    "attribution.review_required",
                    entry.get("paths", [config["attributions"]])[0],
                    "provenance review required",
                    "record a human-reviewed source/license decision or replace the material with original content",
                    severity="warning",
                    construct=identifier,
                )
            )
        elif status not in {"original-declared", "licensed-recorded", "public-domain-recorded"}:
            diagnostics.append(
                Diagnostic(
                    "attribution.status",
                    config["attributions"],
                    "attribution status is unknown",
                    "use the documented neutral status vocabulary",
                    construct=f"{identifier}:{status}",
                )
            )
        elif status == "original-declared":
            required = {"declaration", "review_date", "review_role"}
            missing = sorted(key for key in required if not entry.get(key))
            if missing:
                diagnostics.append(
                    Diagnostic(
                        "attribution.fields",
                        config["attributions"],
                        "original-content declaration lacks human review evidence",
                        "record the declaration, review role, and review date",
                        construct=f"{identifier}:{','.join(missing)}",
                    )
                )
        else:
            required = {
                "source_title", "source_url", "author_or_holder", "license", "required_notice",
                "notice_location", "adaptation", "review_date", "review_role",
            }
            missing = sorted(key for key in required if not entry.get(key))
            if missing:
                diagnostics.append(
                    Diagnostic(
                        "attribution.fields",
                        config["attributions"],
                        "reviewed attribution entry is missing required evidence",
                        "complete source, holder, license, notice, adaptation, and review fields",
                        construct=f"{identifier}:{','.join(missing)}",
                    )
                )
            source_url = str(entry.get("source_url", ""))
            parsed = urlsplit(source_url)
            if source_url and (parsed.scheme not in {"http", "https"} or not parsed.netloc):
                diagnostics.append(
                    Diagnostic(
                        "attribution.source_url",
                        config["attributions"],
                        "attribution source URL is not a complete HTTP(S) URL",
                        "record a syntactically complete source URL; the validator remains offline",
                        construct=identifier,
                    )
                )
            notice_location = entry.get("notice_location")
            if notice_location:
                notice_path = (root / str(notice_location)).resolve(strict=False)
                try:
                    safe_relative(notice_path, root)
                except ConfigError:
                    notice_path = Path("/__invalid__")
                notice = str(entry.get("required_notice", ""))
                if not notice_path.is_file() or notice not in notice_path.read_text(encoding="utf-8"):
                    diagnostics.append(
                        Diagnostic(
                            "attribution.notice",
                            config["attributions"],
                            "required visible attribution notice is missing from its recorded location",
                            "add the exact required notice to the existing visible notice file",
                            construct=f"{identifier}:{notice_location}",
                        )
                    )
    asset_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".pdf"}
    for candidate in git_paths(root):
        path_candidate = root / candidate
        explicit_marker = False
        if (
            path_candidate.suffix.lower() == ".md"
            and (
                path_candidate.parent == root
                or path_candidate.parent.name.startswith(tuple(config["unit_prefixes"]))
            )
            and path_candidate.is_file()
            and path_candidate.stat().st_size <= int(config.get("max_text_scan_bytes", 1_048_576))
        ):
            try:
                data = path_candidate.read_bytes()
                explicit_marker = b"attribution-required" in data if b"\0" not in data else False
            except OSError:
                explicit_marker = False
        if (
            (PurePosixPath(candidate).suffix.lower() in asset_suffixes or explicit_marker)
            and candidate not in covered_paths
        ):
            diagnostics.append(
                Diagnostic(
                    "attribution.candidate_unrecorded",
                    candidate,
                    "asset or explicitly marked material has no provenance inventory entry",
                    "record a neutral reviewed status or provenance-review requirement",
                    construct=candidate,
                )
            )
    return diagnostics


def changed_paths(root: Path, ref: str | None) -> set[str]:
    if not ref:
        return set()
    completed = subprocess.run(
        ["git", "diff", "--name-only", "-z", ref, "--"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise ConfigError("changed-from ref cannot be resolved")
    changed = {part.decode("utf-8", "surrogateescape") for part in completed.stdout.split(b"\0") if part}
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if untracked.returncode != 0:
        raise ConfigError("untracked path inventory failed")
    changed.update(
        part.decode("utf-8", "surrogateescape") for part in untracked.stdout.split(b"\0") if part
    )
    return changed


def stable_path_change_diagnostics(root: Path, config: dict[str, Any], changed: set[str]) -> list[Diagnostic]:
    migrations = {item["old"]: item["new"] for item in config.get("path_migrations", [])}
    prefixes = tuple(config["unit_prefixes"])
    diagnostics: list[Diagnostic] = []
    for raw in sorted(changed):
        parts = PurePosixPath(raw).parts
        first = parts[0] if parts else ""
        is_public_document = (
            len(parts) == 2
            and first.startswith(prefixes)
            and parts[1] in set(config["required_locales"])
        )
        if not is_public_document or (root / raw).exists():
            continue
        replacement = migrations.get(raw)
        if replacement and (root / replacement).exists():
            continue
        diagnostics.append(
            Diagnostic(
                "stable_path.removed",
                raw,
                "a changed public chapter/appendix path was removed or renamed without an exact migration",
                "restore the stable path or add one reviewed exact old/new path migration",
                construct=f"{raw}:{replacement}",
            )
        )
    return diagnostics


def fingerprinted(diagnostics: Sequence[Diagnostic]) -> list[tuple[str, Diagnostic]]:
    counts: defaultdict[tuple[str, str, str], int] = defaultdict(int)
    results: list[tuple[str, Diagnostic]] = []
    for diagnostic in sorted(diagnostics, key=diagnostic_key):
        normalized_path = diagnostic.path.replace("\\", "/")
        digest = hashlib.sha256(diagnostic.construct.encode("utf-8", "surrogatepass")).hexdigest()
        key = (diagnostic.rule_id, normalized_path, digest)
        ordinal = counts[key]
        counts[key] += 1
        material = f"{RULE_VERSION}\0{diagnostic.rule_id}\0{normalized_path}\0{digest}\0{ordinal}"
        results.append((hashlib.sha256(material.encode()).hexdigest(), diagnostic))
    return results


def load_baseline(root: Path, config: dict[str, Any]) -> dict[str, Any]:
    path = root / config["baseline"]
    if not path.exists():
        raise ConfigError("baseline file is missing")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("config_schema_version") != config["schema_version"]:
        raise ConfigError("baseline schema/config version mismatch")
    if payload.get("rule_version") != RULE_VERSION:
        raise ConfigError("baseline rule version mismatch")
    fingerprints = payload.get("fingerprints")
    if not isinstance(fingerprints, list):
        raise ConfigError("baseline fingerprints must be a list")
    if (
        any(not isinstance(item, str) or not re.fullmatch(r"[0-9a-f]{64}", item) for item in fingerprints)
        or fingerprints != sorted(set(fingerprints))
    ):
        raise ConfigError("baseline fingerprints must be unique sorted SHA-256 values")
    if not isinstance(payload.get("review_commit"), str) or not payload["review_commit"]:
        raise ConfigError("baseline review_commit is missing")
    unknown = set(payload) - {
        "schema_version", "config_schema_version", "rule_version", "review_commit", "fingerprints"
    }
    if unknown:
        raise ConfigError(f"unknown baseline fields: {', '.join(sorted(unknown))}")
    return payload


def write_baseline(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def plugin_diagnostics(
    root: Path,
    plugin_paths: Sequence[str],
    config: dict[str, Any],
    registered_checks: set[str] | None = None,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    registration_child = textwrap.dedent(
        """
        import importlib.util, json, sys

        class Registry:
            def __init__(self): self.plugins = []
            def add(self, *, plugin_id, api_version, checks, prerequisites=(), timeout=30):
                self.plugins.append({
                    "plugin_id": plugin_id,
                    "api_version": api_version,
                    "check_ids": list(checks) if isinstance(checks, dict) else None,
                    "prerequisites": list(prerequisites) if isinstance(prerequisites, (list, tuple)) else None,
                    "timeout": timeout,
                })
            register = add

        plugin_path = sys.argv[1]
        spec = importlib.util.spec_from_file_location("bookcheck_domain_plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        registry = Registry()
        module.register(registry)
        print(json.dumps(registry.plugins, sort_keys=True))
        """
    )
    check_child = textwrap.dedent(
        """
        import importlib.util, json, sys

        class Registry:
            def __init__(self): self.plugins = []
            def add(self, *, plugin_id, api_version, checks, prerequisites=(), timeout=30):
                self.plugins.append((plugin_id, checks))
            register = add

        plugin_path, context_path, wanted_plugin, wanted_check = sys.argv[1:5]
        spec = importlib.util.spec_from_file_location("bookcheck_domain_plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        registry = Registry()
        module.register(registry)
        context = json.load(open(context_path, encoding="utf-8"))
        for plugin_id, checks in registry.plugins:
            if plugin_id == wanted_plugin:
                result = checks[wanted_check](context)
                print(json.dumps(result or [], sort_keys=True))
                break
        else:
            raise RuntimeError("registered plugin/check disappeared")
        """
    )
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONIOENCODING": "utf-8",
        "LANG": "C.UTF-8",
    }
    before = repository_snapshot(root)
    all_ids: set[str] = set()

    def protocol_diagnostic(rule_id: str, rel: str, message: str, remediation: str, construct: str) -> None:
        diagnostics.append(Diagnostic(rule_id, rel, message, remediation, construct=construct))

    def run_child(
        command: Sequence[str], *, rel: str, timeout: int, cwd: str | os.PathLike[str]
    ) -> subprocess.CompletedProcess[bytes] | None:
        try:
            return run_bounded(
                command,
                cwd=cwd,
                timeout=timeout,
                env=environment,
                output_limit=int(config["output_limit_bytes"]),
            )
        except subprocess.TimeoutExpired:
            protocol_diagnostic(
                "plugin.timeout", rel, "domain plugin exceeded its declared timeout",
                "make plugin registration and every check bounded and deterministic", rel,
            )
        except OutputLimitExceeded:
            protocol_diagnostic(
                "plugin.output_limit", rel, "domain plugin exceeded the output bound",
                "return only bounded schema-valid diagnostics", rel,
            )
        except SurvivingDescendantError:
            protocol_diagnostic(
                "plugin.descendant", rel, "domain plugin left a surviving descendant process",
                "join or terminate every child process before the plugin exits", rel,
            )
        return None

    for raw in plugin_paths:
        candidate = (root / raw).resolve(strict=False)
        try:
            rel = safe_relative(candidate, root)
        except ConfigError:
            rel = raw
            candidate = Path("/__invalid__")
        if not candidate.is_file():
            protocol_diagnostic(
                "plugin.path", rel,
                "requested plugin path is missing or escapes the repository",
                "use an existing repository-relative bookcheck_plugin.py", raw,
            )
            continue
        with tempfile.TemporaryDirectory(prefix="bookcheck-plugin-") as temp:
            context_path = Path(temp) / "context.json"
            context_path.write_text(json.dumps({"root": str(root), "plugin": rel}), encoding="utf-8")
            completed = run_child(
                [sys.executable, "-I", "-B", "-c", registration_child, str(candidate)],
                rel=rel,
                timeout=int(config.get("plugin_timeout_seconds", 30)),
                cwd=temp,
            )
            if completed is None:
                continue
            if completed.returncode != 0:
                protocol_diagnostic(
                    "plugin.failure", rel,
                    "domain plugin registration crashed",
                    "fix plugin registration and return schema-valid metadata",
                    hashlib.sha256(completed.stderr).hexdigest(),
                )
                continue
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError:
                payload = None
            if not isinstance(payload, list):
                protocol_diagnostic(
                    "plugin.schema", rel,
                    "domain plugin registration does not match the protocol",
                    "register a list of schema-valid plugin/check contracts",
                    hashlib.sha256(completed.stdout).hexdigest(),
                )
                continue
            for plugin in payload:
                if not isinstance(plugin, dict) or set(plugin) != {
                    "plugin_id", "api_version", "check_ids", "prerequisites", "timeout"
                }:
                    protocol_diagnostic(
                        "plugin.schema", rel,
                        "domain plugin registration does not match the protocol",
                        "return only the versioned registration fields", type(plugin).__name__,
                    )
                    continue
                plugin_id = plugin.get("plugin_id")
                if (
                    not isinstance(plugin_id, str)
                    or not PLUGIN_ID_RE.fullmatch(plugin_id)
                    or plugin_id in all_ids
                    or plugin.get("api_version") != config["plugin_api_version"]
                ):
                    protocol_diagnostic(
                        "plugin.registration", rel,
                        "plugin ID is unsafe/duplicate or API version is incompatible",
                        "register one lowercase stable ID with the configured API version",
                        f"{plugin_id}:{plugin.get('api_version')}",
                    )
                    continue
                declared_timeout = plugin.get("timeout")
                if (
                    isinstance(declared_timeout, bool)
                    or not isinstance(declared_timeout, int)
                    or not 0 < declared_timeout <= int(config["plugin_timeout_seconds"])
                ):
                    protocol_diagnostic(
                        "plugin.timeout_contract", rel,
                        "plugin declared an invalid timeout",
                        "declare a positive integer no greater than the root plugin bound",
                        f"{plugin_id}:{declared_timeout}",
                    )
                    continue
                prerequisites = plugin.get("prerequisites")
                check_ids = plugin.get("check_ids")
                if (
                    not isinstance(prerequisites, list)
                    or any(not isinstance(item, str) or not item for item in prerequisites)
                    or not isinstance(check_ids, list)
                    or len(check_ids) != len(set(check_ids))
                    or any(not isinstance(item, str) or not PLUGIN_ID_RE.fullmatch(item) for item in check_ids)
                ):
                    protocol_diagnostic(
                        "plugin.schema", rel,
                        "domain plugin has malformed prerequisites or check IDs",
                        "use executable names and unique lowercase stable check IDs", str(plugin_id),
                    )
                    continue
                all_ids.add(plugin_id)
                if registered_checks is not None:
                    registered_checks.add(f"@plugin:{plugin_id}")
                    for check_id in check_ids:
                        registered_checks.add(check_id)
                        registered_checks.add(f"{plugin_id}:{check_id}")
                missing_prerequisites = [item for item in prerequisites if shutil.which(item) is None]
                if missing_prerequisites:
                    diagnostics.append(
                        Diagnostic(
                            "plugin.prerequisite",
                            rel,
                            "requested domain plugin prerequisite is unavailable",
                            "install the declared tool or do not request this plugin in the generic job",
                            construct=f"{plugin_id}:{','.join(sorted(missing_prerequisites))}",
                        )
                    )
                    continue
                for check_id in sorted(check_ids):
                    check_completed = run_child(
                        [
                            sys.executable, "-I", "-B", "-c", check_child,
                            str(candidate), str(context_path), plugin_id, check_id,
                        ],
                        rel=rel,
                        timeout=declared_timeout,
                        cwd=temp,
                    )
                    if check_completed is None:
                        continue
                    if check_completed.returncode != 0:
                        protocol_diagnostic(
                            "plugin.failure", rel,
                            "domain plugin check crashed",
                            "fix the bounded callback and return schema-valid diagnostics",
                            hashlib.sha256(check_completed.stderr).hexdigest(),
                        )
                        continue
                    try:
                        check_diagnostics = json.loads(check_completed.stdout)
                    except json.JSONDecodeError:
                        check_diagnostics = None
                    if not isinstance(check_diagnostics, list):
                        protocol_diagnostic(
                            "plugin.schema", rel,
                            "domain plugin check output does not match the protocol",
                            "return a JSON list of diagnostic objects",
                            hashlib.sha256(check_completed.stdout).hexdigest(),
                        )
                        continue
                    if not check_diagnostics:
                        diagnostics.append(
                            Diagnostic(
                                "plugin.check_passed", rel,
                                f"domain check passed: {plugin_id}:{check_id}",
                                "no action required; this is positive evidence from an explicitly selected plugin",
                                severity="info", construct=f"{plugin_id}:{check_id}",
                            )
                        )
                    for item in check_diagnostics:
                        try:
                            if not isinstance(item, dict) or not set(item) <= {
                                "rule_id", "path", "message", "remediation", "severity", "line", "construct"
                            }:
                                raise TypeError("diagnostic must contain only public protocol fields")
                            item_rule = item.get("rule_id", "failure")
                            if not isinstance(item_rule, str) or not re.fullmatch(r"[a-z][a-z0-9_.-]*", item_rule):
                                raise TypeError("invalid rule ID")
                            item_path = item.get("path", rel)
                            if not isinstance(item_path, str) or Path(item_path).is_absolute() or re.match(r"^[A-Za-z]:[\\/]", item_path):
                                raise TypeError("absolute path")
                            safe_relative(root / item_path, root)
                            severity = item.get("severity", "error")
                            if severity not in {"error", "warning", "info"}:
                                raise TypeError("invalid severity")
                            line = item.get("line")
                            if line is not None and (not isinstance(line, int) or isinstance(line, bool) or line < 1):
                                raise TypeError("invalid line")
                            message = item.get("message", "domain check failed")
                            remediation = item.get("remediation", "run the domain verifier")
                            if (
                                not isinstance(message, str)
                                or not isinstance(remediation, str)
                                or SAFE_PLUGIN_SECRET_RE.search(message + "\n" + remediation)
                                or SAFE_PLUGIN_ABSOLUTE_PATH_RE.search(message + "\n" + remediation)
                            ):
                                raise TypeError("unsafe diagnostic text")
                            diagnostics.append(
                                Diagnostic(
                                    f"plugin.{plugin_id}.{check_id}.{item_rule}", item_path,
                                    message, remediation, severity=severity, line=line,
                                    construct=str(item.get("construct", item_rule)),
                                )
                            )
                        except (TypeError, ConfigError):
                            protocol_diagnostic(
                                "plugin.diagnostic_schema", rel,
                                "plugin emitted a malformed or unsafe diagnostic; values redacted",
                                "return safe repository-relative schema-valid diagnostics", check_id,
                            )
    after = repository_snapshot(root)
    if before != after:
        diagnostics.append(
            Diagnostic(
                "plugin.source_mutation",
                ".",
                "a plugin changed the repository tree",
                "plugins must be read-only and write only to provided temporary locations",
                construct=hashlib.sha256(repr((before, after)).encode()).hexdigest(),
            )
        )
    return diagnostics


def collect_diagnostics(root: Path, config: dict[str, Any], plugins: Sequence[str]) -> list[Diagnostic]:
    units = discover_units(root, config)
    diagnostics = check_unit_shape(root, config, units)
    registered_checks: set[str] = set()
    diagnostics.extend(plugin_diagnostics(root, plugins, config, registered_checks))
    snippet_snapshot = repository_snapshot(root)
    markdown_paths: list[Path] = [root / name for name in config["root_indexes"] if (root / name).exists()]
    for unit in units:
        markdown_paths.extend(unit / name for name in config["required_locales"] if (unit / name).exists())
    scans: dict[Path, ScanResult] = {}
    referenced_checks: dict[str, str] = {}
    for path in markdown_paths:
        scan = scan_markdown(path, root, config)
        scans[path.resolve()] = scan
        diagnostics.extend(scan.diagnostics)
        if path.parent != root:
            diagnostics.extend(check_selectors(path, root))
        diagnostics.extend(check_arabic(path, root))
        diagnostics.extend(table_diagnostics(path, root, config))
        document_source_refs: set[tuple[str | None, str | None, str]] = set()
        for index, fence in enumerate(scan.fences):
            effective_fence = fence
            next_fence = scan.fences[index + 1] if index + 1 < len(scan.fences) else None
            if (
                fence.classification == "runnable"
                and fence.language == "python"
                and "expect" not in fence.metadata
                and next_fence is not None
                and next_fence.classification == "output"
            ):
                metadata = dict(fence.metadata)
                metadata["expect"] = next_fence.code.rstrip("\n")
                effective_fence = Fence(
                    fence.language, fence.classification, fence.code, fence.line, metadata, fence.end_line
                )
            diagnostics.extend(run_python_fence(effective_fence, path, root, config))
            diagnostics.extend(
                source_ref_diagnostics(
                    fence,
                    path,
                    root,
                    set(config["known_check_ids"]),
                    registered_checks if plugins else None,
                )
            )
            if fence.classification == "source-ref":
                identity = (
                    fence.metadata.get("path"),
                    fence.metadata.get("check"),
                    hashlib.sha256(fence.code.encode()).hexdigest(),
                )
                if identity in document_source_refs:
                    diagnostics.append(
                        Diagnostic(
                            "source_ref.duplicate",
                            safe_relative(path, root),
                            "document repeats the same companion path and verifier identity",
                            "keep one source-ref block per distinct evidence point",
                            line=fence.line,
                            construct=f"{identity[0]}:{identity[1]}:{identity[2]}",
                        )
                    )
                document_source_refs.add(identity)
                if identity[1]:
                    referenced_checks.setdefault(identity[1], safe_relative(path, root))
    for path in markdown_paths:
        diagnostics.extend(check_links(path, root, scans[path.resolve()], scans))
        diagnostics.extend(check_root_navigation(path, root, scans[path.resolve()]))
    for unit in units:
        sequences: dict[str, tuple[tuple[str | None, str | None, str | None], ...]] = {}
        for filename in config["required_locales"]:
            candidate = unit / filename
            if candidate.exists():
                candidate_scan = scans.get(candidate.resolve())
                if candidate_scan is None:
                    candidate_scan = scan_markdown(candidate, root, config)
                    scans[candidate.resolve()] = candidate_scan
                sequences[filename] = tuple(
                    (
                        fence.classification,
                        fence.metadata.get("path") if fence.classification == "source-ref" else None,
                        fence.metadata.get("check") if fence.classification == "source-ref" else None,
                    )
                    for fence in candidate_scan.fences
                )
        canonical = sequences.get("README.md", ())
        for filename, sequence in sequences.items():
            if filename != "README.md" and sequence != canonical:
                diagnostics.append(
                    Diagnostic(
                        "parity.fence_sequence",
                        safe_relative(unit / filename, root),
                        "localized fenced-block classifications or source identities differ from canonical English",
                        "restore equivalent classified evidence/source refs or record a reviewed locale-specific exception",
                        severity="warning",
                        construct=hashlib.sha256(repr((canonical, sequence)).encode()).hexdigest(),
                    )
                )
    diagnostics.extend(hygiene_diagnostics(root, config))
    diagnostics.extend(attribution_diagnostics(root, config))
    selected_owners = {
        item.removeprefix("@plugin:") for item in registered_checks if item.startswith("@plugin:")
    }
    for check, source_path in sorted(referenced_checks.items()):
        owner = check.split(":", 1)[0]
        if owner not in selected_owners:
            diagnostics.append(
                Diagnostic(
                    "source_ref.not_run",
                    source_path,
                    f"referenced domain check was not selected and did not run: {check}",
                    "invoke the owning plugin when domain evidence is required",
                    severity="info",
                    construct=check,
                )
            )
    after_snippets = repository_snapshot(root)
    if snippet_snapshot != after_snippets:
        diagnostics.append(
            Diagnostic(
                "snippet.source_mutation",
                ".",
                "one or more runnable snippets changed the repository tree",
                "make snippets write only inside their isolated temporary working directory",
                construct=hashlib.sha256(repr((snippet_snapshot, after_snippets)).encode()).hexdigest(),
            )
        )
    return sorted(set(diagnostics), key=diagnostic_key)


def apply_baseline(
    root: Path,
    config: dict[str, Any],
    diagnostics: Sequence[Diagnostic],
    changed: set[str],
) -> tuple[list[Diagnostic], list[str]]:
    baseline = load_baseline(root, config)
    accepted = set(baseline["fingerprints"])
    current = fingerprinted([item for item in diagnostics if item.severity != "info"])
    current_ids = {item for item, _ in current}
    failures: list[Diagnostic] = []
    for item, diagnostic in current:
        # The fingerprint already binds the rule, path, normalized construct
        # digest and duplicate ordinal. Editing another construct in the same
        # file must not turn exact untouched debt into a blanket file waiver.
        if item not in accepted:
            failures.append(diagnostic)
    stale = sorted(accepted - current_ids)
    return failures, stale


def render_text(
    diagnostics: Sequence[Diagnostic],
    stale: Sequence[str],
    accepted_legacy: Sequence[Diagnostic] = (),
    information: Sequence[Diagnostic] = (),
) -> str:
    lines: list[str] = []
    for diagnostic in diagnostics:
        location = diagnostic.path
        if diagnostic.line is not None:
            location += f":{diagnostic.line}"
            if diagnostic.column is not None:
                location += f":{diagnostic.column}"
        lines.append(f"{diagnostic.severity.upper()} {diagnostic.rule_id} {location}: {diagnostic.message}")
        lines.append(f"  fix: {diagnostic.remediation}")
    for fingerprint in stale:
        lines.append(f"ERROR baseline.stale tools/book_quality_baseline.json: resolved fingerprint must be removed: {fingerprint}")
    for diagnostic in accepted_legacy:
        lines.append(
            f"INFO baseline.accepted {diagnostic.path}: accepted exact legacy debt remains ({diagnostic.rule_id})"
        )
    for diagnostic in information:
        lines.append(f"INFO {diagnostic.rule_id} {diagnostic.path}: {diagnostic.message}")
    if not lines:
        lines.append("Book quality validation passed.")
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changed-from")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--plugin", action="append", default=[])
    parser.add_argument("--update-baseline", action="store_true", help="remove stale fingerprints only")
    parser.add_argument("--bootstrap-baseline", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = repository_root()
    try:
        config = load_config(root)
        changed = changed_paths(root, args.changed_from)
        diagnostics = collect_diagnostics(root, config, args.plugin)
        diagnostics.extend(stable_path_change_diagnostics(root, config, changed))
        diagnostics = sorted(set(diagnostics), key=diagnostic_key)
        protocol_failures = [item for item in diagnostics if item.rule_id in PLUGIN_PROTOCOL_RULES]
        if protocol_failures:
            if args.format == "json":
                print(
                    json.dumps(
                        {
                            "schema_version": SCHEMA_VERSION,
                            "diagnostics": [item.public_dict() for item in protocol_failures],
                            "stale_baseline": [],
                            "accepted_legacy": [],
                            "information": [],
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    )
                )
            else:
                print(render_text(protocol_failures, []))
            return 2
        baseline_path = root / config["baseline"]
        baseline = load_baseline(root, config)
        if args.bootstrap_baseline:
            if baseline["fingerprints"]:
                raise ConfigError("initial baseline already exists")
            fingerprints = sorted(
                item for item, _ in fingerprinted([diagnostic for diagnostic in diagnostics if diagnostic.severity != "info"])
            )
            write_baseline(
                baseline_path,
                {
                    "schema_version": 1,
                    "config_schema_version": config["schema_version"],
                    "rule_version": RULE_VERSION,
                    "review_commit": subprocess.run(
                        ["git", "rev-parse", "HEAD"], cwd=root, text=True, stdout=subprocess.PIPE, check=True
                    ).stdout.strip(),
                    "fingerprints": fingerprints,
                },
            )
            print(f"Initial reviewed baseline written with {len(fingerprints)} fingerprints.")
            return 0
        failures, stale = apply_baseline(root, config, diagnostics, changed)
        accepted_ids = set(baseline["fingerprints"])
        accepted_legacy = [
            diagnostic
            for fingerprint, diagnostic in fingerprinted([item for item in diagnostics if item.severity != "info"])
            if fingerprint in accepted_ids
        ]
        information = [item for item in diagnostics if item.severity == "info"]
        if args.update_baseline:
            if failures:
                raise ConfigError("baseline update cannot accept new or changed failures")
            if stale:
                baseline["fingerprints"] = sorted(set(baseline["fingerprints"]) - set(stale))
                write_baseline(baseline_path, baseline)
            print(f"Removed {len(stale)} resolved baseline fingerprints.")
            return 0
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "diagnostics": [item.public_dict() for item in failures],
                        "stale_baseline": list(stale),
                        "accepted_legacy": [item.public_dict() for item in accepted_legacy],
                        "information": [item.public_dict() for item in information],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        else:
            print(render_text(failures, stale, accepted_legacy, information))
        return 1 if failures or stale else 0
    except Exception as exc:  # Fail closed with a stable diagnostic; never expose a platform traceback.
        message = str(exc).replace(str(root), "<repo>")
        message = re.sub(r"(?<![\w.])/(?:[^\s:]+/)*[^\s:]+", "<path>", message)
        diagnostic = Diagnostic(
            "validator.internal",
            "tools/validate_book.py",
            message or "validator configuration or internal processing failed",
            "fix the reported configuration/protocol problem and rerun the validator",
        )
        if args.format == "json":
            print(
                json.dumps(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "diagnostics": [diagnostic.public_dict()],
                        "stale_baseline": [],
                        "accepted_legacy": [],
                        "information": [],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        else:
            print(render_text([diagnostic], []))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
