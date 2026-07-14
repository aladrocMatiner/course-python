from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".codex" / "skills"

REQUIRED_NEW = frozenset(
    {
        "verify-python-learning-assets",
        "engineer-python-network-labs",
        "python-packaging-release",
        "engineer-python-native-interop",
        "maintain-book-quality-tooling",
    }
)
AFFECTED = REQUIRED_NEW | {"professor", "book-editor"}
PREEXISTING_UNRELATED = frozenset(
    {
        "backend-python-django",
        "devops-proxmox",
        "frontend-react-patternfly",
        "openspec-apply-change",
        "openspec-architect",
        "openspec-archive-change",
        "openspec-bulk-archive-change",
        "openspec-continue-change",
        "openspec-explore",
        "openspec-ff-change",
        "openspec-new-change",
        "openspec-onboard",
        "openspec-propose",
        "openspec-sync-specs",
        "openspec-update-change",
        "openspec-verify-change",
        "tester-cypress",
    }
)

EXPECTED_REFERENCES = {
    "verify-python-learning-assets": {
        "references/execution-contract.md",
        "references/evidence-and-recovery.md",
    },
    "engineer-python-network-labs": {
        "references/http-and-protocol-boundaries.md",
        "references/asyncio-lifecycle-and-tls.md",
    },
    "python-packaging-release": {
        "references/dependency-evidence.md",
        "references/artifact-verification.md",
    },
    "engineer-python-native-interop": {
        "references/cpp.md",
        "references/rust.md",
    },
    "maintain-book-quality-tooling": {
        "references/generic-validator.md",
        "references/plugins-and-ci.md",
        "references/parity-and-human-review.md",
    },
    "professor": {"references/course-level-audit.md"},
    "book-editor": {"references/publication-and-reviewer-handoff.md"},
}

EXPECTED_INTERFACE = {
    "verify-python-learning-assets": {
        "display_name": "Verify Python Learning Assets",
        "short_description": "Verify runnable Python learning examples",
        "default_prompt": "Use $verify-python-learning-assets to verify the runnable and expected-error examples in this lesson.",
    },
    "engineer-python-network-labs": {
        "display_name": "Engineer Python Network Labs",
        "short_description": "Build bounded local-first Python network labs",
        "default_prompt": "Use $engineer-python-network-labs to review and verify this bounded local Python networking lab.",
    },
    "python-packaging-release": {
        "display_name": "Python Packaging and Release",
        "short_description": "Verify Python packages and release artifacts",
        "default_prompt": "Use $python-packaging-release to verify this package from clean build through installed artifact.",
    },
    "engineer-python-native-interop": {
        "display_name": "Engineer Python Native Interop",
        "short_description": "Verify Python C++ and Rust interoperability",
        "default_prompt": "Use $engineer-python-native-interop to verify this Python and native-language boundary.",
    },
    "maintain-book-quality-tooling": {
        "display_name": "Maintain Book Quality Tooling",
        "short_description": "Maintain truthful book validators and CI",
        "default_prompt": "Use $maintain-book-quality-tooling to evolve this book quality check without overstating evidence.",
    },
    "professor": {
        "display_name": "Professor",
        "short_description": "Design lessons and course-wide learning routes",
        "default_prompt": "Use $professor to audit this curriculum and produce prerequisite-safe learning routes and assessments.",
    },
    "book-editor": {
        "display_name": "Book Editor",
        "short_description": "Audit multilingual books for publication",
        "default_prompt": "Use $book-editor to prepare truthful technical, localization, accessibility, and provenance review evidence.",
    },
}

TRIGGER_TERMS = {
    "verify-python-learning-assets": ("markdown fences", "expected-error", "companion sources", "cpython"),
    "engineer-python-network-labs": ("http", "tcp", "udp", "asyncio", "tls"),
    "python-packaging-release": ("pyproject.toml", "constraints", "sdists", "wheels", "release claims"),
    "engineer-python-native-interop": ("c++", "rust", "gil", "abi", "sanitizers"),
    "maintain-book-quality-tooling": ("validate_book.py", "parity_review.py", "domain-plugin", "ci workflows"),
    "professor": ("course-wide", "prerequisite graphs", "cognitive-load", "capstones"),
    "book-editor": ("rendered accessibility", "arabic bidi", "provenance", "published-unit"),
}

CONTRACT_TERMS = {
    "verify-python-learning-assets": ("-i -b", "no stdin", "process group", "not run", "recovery path"),
    "engineer-python-network-labs": ("loopback", "ephemeral port", "fixed sleep", "negative length", "hostname verification", "indefinitely"),
    "python-packaging-release": ("foreign working directory", "complete lock", "never upload", "source distribution", "wheel tags"),
    "engineer-python-native-interop": ("do not load the rust reference", "do not load the c++ reference", "silently omitted", "minimum supported rust version", "msvc"),
    "maintain-book-quality-tooling": ("generic validator", "explicit plugin", "least privilege", "source mutation", "human acceptance"),
    "professor": ("acyclic", "entry and exit", "longitudinal capstone", "objective → explanation"),
    "book-editor": ("rendered accessibility", "arabic", "provenance", "never mark the book accepted"),
}

PROHIBITED_FILES = {
    "readme.md",
    "changelog.md",
    "installation-guide.md",
    "installation_guide.md",
    "quick-reference.md",
    "quick_reference.md",
}
PROHIBITED_PARTS = {"__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
REFERENCE_LINK = re.compile(r"\[[^\]]+\]\((references/[a-z0-9-]+\.md)\)")
PLACEHOLDER = re.compile(r"\[(?:TODO|todo)[^\]]*\]|TODO:|Replace with|Structuring This Skill|example placeholder")


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ValueError("missing YAML frontmatter delimiters")
    raw, body = text[4:].split("\n---\n", 1)
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            raise ValueError(f"malformed frontmatter line: {line}")
        key, value = line.split(":", 1)
        if not key or key.strip() != key or not value.strip() or key in values:
            raise ValueError(f"malformed or duplicate frontmatter key: {key}")
        values[key] = value.strip()
    return values, body


def parse_interface(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[:1] != ["interface:"] or len(lines) != 4:
        raise ValueError("agents/openai.yaml must contain only the three interface fields")
    values: dict[str, str] = {}
    for line in lines[1:]:
        match = re.fullmatch(r'  ([a-z_]+): ("(?:[^"\\]|\\.)*")', line)
        if match is None:
            raise ValueError(f"invalid quoted interface line: {line}")
        values[match.group(1)] = json.loads(match.group(2))
    if set(values) != {"display_name", "short_description", "default_prompt"}:
        raise ValueError("unexpected interface fields")
    return values


def inventory_violations(actual: set[str]) -> list[str]:
    expected = set(PREEXISTING_UNRELATED | AFFECTED)
    problems = [f"missing skill directory: {name}" for name in sorted(expected - actual)]
    problems.extend(f"unexpected skill directory: {name}" for name in sorted(actual - expected))
    return problems


def skill_violations(
    path: Path,
    expected_name: str,
    expected_references: set[str],
    expected_interface: dict[str, str],
) -> list[str]:
    prefix = path.name
    problems: list[str] = []
    skill_file = path / "SKILL.md"
    if not skill_file.is_file():
        return [f"{prefix}/SKILL.md: missing"]
    try:
        frontmatter, body = parse_frontmatter(skill_file)
    except ValueError as error:
        return [f"{prefix}/SKILL.md: {error}"]
    if set(frontmatter) != {"name", "description"}:
        problems.append(f"{prefix}/SKILL.md: frontmatter must contain only name and description")
    if frontmatter.get("name") != expected_name or path.name != expected_name:
        problems.append(f"{prefix}/SKILL.md: folder/frontmatter name mismatch")
    if len(skill_file.read_text(encoding="utf-8").splitlines()) >= 500:
        problems.append(f"{prefix}/SKILL.md: core workflow must stay below 500 lines")
    if PLACEHOLDER.search(skill_file.read_text(encoding="utf-8")):
        problems.append(f"{prefix}/SKILL.md: initializer placeholder remains")

    description = frontmatter.get("description", "").casefold()
    for term in TRIGGER_TERMS.get(expected_name, ()):
        if term.casefold() not in description:
            problems.append(f"{prefix}/SKILL.md: description is missing trigger term {term!r}")

    linked = set(REFERENCE_LINK.findall(body))
    if linked != expected_references:
        missing = expected_references - linked
        extra = linked - expected_references
        for relative in sorted(missing):
            problems.append(f"{prefix}/SKILL.md: missing direct reference link {relative}")
        for relative in sorted(extra):
            problems.append(f"{prefix}/SKILL.md: unexpected direct reference link {relative}")
    reference_dir = path / "references"
    actual_references = {
        item.relative_to(path).as_posix()
        for item in reference_dir.rglob("*.md")
        if item.is_file()
    } if reference_dir.is_dir() else set()
    if actual_references != expected_references:
        for relative in sorted(expected_references - actual_references):
            problems.append(f"{prefix}/{relative}: referenced resource is missing")
        for relative in sorted(actual_references - expected_references):
            problems.append(f"{prefix}/{relative}: unlinked or unexpected reference")
    for relative in sorted(actual_references):
        reference = path / relative
        if reference.parent != reference_dir:
            problems.append(f"{prefix}/{relative}: references must be one level deep")
        if REFERENCE_LINK.search(reference.read_text(encoding="utf-8")):
            problems.append(f"{prefix}/{relative}: reference-to-reference link is not allowed")
        if PLACEHOLDER.search(reference.read_text(encoding="utf-8")):
            problems.append(f"{prefix}/{relative}: placeholder remains")

    metadata = path / "agents" / "openai.yaml"
    if not metadata.is_file():
        problems.append(f"{prefix}/agents/openai.yaml: missing")
    else:
        try:
            interface = parse_interface(metadata)
        except ValueError as error:
            problems.append(f"{prefix}/agents/openai.yaml: {error}")
        else:
            if interface != expected_interface:
                problems.append(f"{prefix}/agents/openai.yaml: stale interface metadata")
            short = interface.get("short_description", "")
            if not 25 <= len(short) <= 64:
                problems.append(f"{prefix}/agents/openai.yaml: short_description length is invalid")
            if f"${expected_name}" not in interface.get("default_prompt", ""):
                problems.append(f"{prefix}/agents/openai.yaml: default_prompt must name the skill")

    for item in path.rglob("*"):
        relative = item.relative_to(path).as_posix()
        if item.name.casefold() in PROHIBITED_FILES:
            problems.append(f"{prefix}/{relative}: prohibited auxiliary file")
        if any(part.casefold() in PROHIBITED_PARTS for part in item.parts):
            problems.append(f"{prefix}/{relative}: prohibited generated directory")
        if item.suffix.casefold() in {".pyc", ".pyo"}:
            problems.append(f"{prefix}/{relative}: prohibited generated bytecode")
    return problems


class CourseSkillContractTests(unittest.TestCase):
    def test_exact_skill_inventory(self) -> None:
        actual = {path.name for path in SKILLS.iterdir() if path.is_dir()}
        self.assertEqual([], inventory_violations(actual))
        self.assertEqual(5, len(REQUIRED_NEW))

    def test_affected_skill_contracts(self) -> None:
        problems: list[str] = []
        for name in sorted(AFFECTED):
            problems.extend(
                skill_violations(
                    SKILLS / name,
                    name,
                    EXPECTED_REFERENCES[name],
                    EXPECTED_INTERFACE[name],
                )
            )
        self.assertEqual([], problems, "\n".join(problems))

    def test_domain_and_human_boundaries_are_discoverable(self) -> None:
        problems: list[str] = []
        for name, terms in CONTRACT_TERMS.items():
            path = SKILLS / name
            corpus = "\n".join(
                file.read_text(encoding="utf-8")
                for file in [path / "SKILL.md", *(path / "references").glob("*.md")]
            ).casefold()
            for term in terms:
                if term.casefold() not in corpus:
                    problems.append(f"{name}: missing behavioral contract {term!r}")
        self.assertEqual([], problems, "\n".join(problems))

    def test_no_skill_bundles_unverified_executable_scripts(self) -> None:
        for name in AFFECTED:
            scripts = SKILLS / name / "scripts"
            self.assertFalse(scripts.exists(), f"{name}: deterministic scripts require direct success/failure tests")

    def test_negative_fixture_detects_extra_skill_and_broken_reference(self) -> None:
        inventory = set(PREEXISTING_UNRELATED | AFFECTED) | {"sixth-course-maintainer"}
        self.assertEqual(
            ["unexpected skill directory: sixth-course-maintainer"],
            inventory_violations(inventory),
        )
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "broken-skill"
            (skill / "agents").mkdir(parents=True)
            (skill / "references").mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: broken-skill\ndescription: [TODO: finish]\n---\n"
                "# Broken\n\nRead [missing evidence](references/missing.md).\n",
                encoding="utf-8",
            )
            (skill / "agents" / "openai.yaml").write_text(
                'interface:\n  display_name: "Broken"\n'
                '  short_description: "Broken fixture for contract testing"\n'
                '  default_prompt: "Use $broken-skill to test failure."\n',
                encoding="utf-8",
            )
            violations = skill_violations(
                skill,
                "broken-skill",
                {"references/missing.md"},
                {
                    "display_name": "Broken",
                    "short_description": "Broken fixture for contract testing",
                    "default_prompt": "Use $broken-skill to test failure.",
                },
            )
            self.assertIn("broken-skill/SKILL.md: initializer placeholder remains", violations)
            self.assertIn("broken-skill/references/missing.md: referenced resource is missing", violations)


if __name__ == "__main__":
    unittest.main()
