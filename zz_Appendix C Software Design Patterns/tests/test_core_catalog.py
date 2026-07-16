"""Closed-catalogue and runnable-example checks for Appendix C."""

from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import re
import subprocess
import sys
import tomllib
import unittest
from urllib.parse import unquote, urlsplit

from load_example import load_example


APPENDIX_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = APPENDIX_ROOT / "catalog.toml"
EXPECTED_FAMILIES = (
    "creational",
    "structural",
    "behavioural",
    "architectural",
    "concurrency",
    "network",
)
EXPECTED_STATUSES = {"executable", "decision-card", "cross-link"}
EXPECTED_ROUTE_IDS = {
    "essential",
    "professional",
    "advanced",
    "network-resilience",
    "network-capacity",
    "network-crosswalk",
}
ROLE_BY_STATUS = {
    "executable": "pattern",
    "decision-card": "contrast",
    "cross-link": "cross-link",
}
FORBIDDEN_IMPORTS = {
    "http",
    "multiprocessing",
    "requests",
    "socket",
    "threading",
    "urllib",
}
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\((?:<([^>]+)>|([^\s)]+))\)")
PENDING_ROOT_LOCALES = {
    "README.ar.md",
    "README.ca.md",
    "README.es.md",
    "README.sv.md",
}


def load_catalog() -> dict[str, object]:
    with CATALOG_PATH.open("rb") as stream:
        return tomllib.load(stream)


def heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        text = re.sub(r"<[^>]+>|[`*_~]", "", match.group(1)).strip().lower()
        base = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
        base = re.sub(r"\s+", "-", base)
        count = counts.get(base, 0)
        counts[base] = count + 1
        slugs.add(base if count == 0 else f"{base}-{count}")
    return slugs


class CatalogContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load_catalog()
        cls.patterns = cls.catalog["patterns"]

    def test_catalog_identity_and_family_order_are_exact(self) -> None:
        self.assertEqual(1, self.catalog["schema_version"])
        self.assertEqual(
            "appendix-software-design-patterns",
            self.catalog["logical_unit_id"],
        )
        self.assertEqual(APPENDIX_ROOT.name, self.catalog["physical_path"])
        self.assertNotIn(":", APPENDIX_ROOT.name)
        self.assertEqual(list(EXPECTED_FAMILIES), self.catalog["family_order"])

    def test_catalog_has_25_unique_complete_entries(self) -> None:
        self.assertEqual(25, len(self.patterns))
        family_rank = {family: index for index, family in enumerate(EXPECTED_FAMILIES)}
        catalog_families = [entry["family"] for entry in self.patterns]
        self.assertEqual(
            sorted(catalog_families, key=family_rank.__getitem__),
            catalog_families,
        )
        required = {
            "id",
            "name",
            "directory",
            "family",
            "route",
            "route_ids",
            "role",
            "status",
            "summary",
            "simple_alternative",
            "checkpoint",
            "checkpoint_href",
            "example_check",
        }
        for key in ("id", "name", "directory"):
            values = [entry[key] for entry in self.patterns]
            self.assertEqual(len(values), len(set(values)), key)
        for entry in self.patterns:
            self.assertFalse(required - set(entry), entry["id"])
            self.assertIn(entry["family"], EXPECTED_FAMILIES)
            self.assertIn(entry["status"], EXPECTED_STATUSES)
            self.assertEqual(ROLE_BY_STATUS[entry["status"]], entry["role"])
            self.assertEqual(len(entry["route_ids"]), len(set(entry["route_ids"])))
            self.assertFalse(set(entry["route_ids"]) - EXPECTED_ROUTE_IDS)
            self.assertEqual("patterns:core-suite", entry["example_check"])
            if entry["status"] == "executable":
                self.assertTrue(entry["route_ids"], entry["id"])
            self.assertEqual(Path(entry["directory"]).name, entry["directory"])
            self.assertNotIn(":", entry["directory"])
            self.assertTrue(
                entry["directory"].startswith(f"{entry['family']} - "),
                entry["directory"],
            )
            if entry["status"] == "cross-link":
                self.assertIn("owner", entry, entry["id"])
                owner = entry["owner"]
                owner_path = (
                    APPENDIX_ROOT / owner
                    if owner.startswith(tuple(f"{family} - " for family in EXPECTED_FAMILIES))
                    else APPENDIX_ROOT.parent / owner
                )
                self.assertTrue(owner_path.is_dir(), owner)

    def test_manifest_table_and_directories_are_bijective(self) -> None:
        declared = {entry["directory"] for entry in self.patterns}
        physical = {
            child.name
            for child in APPENDIX_ROOT.iterdir()
            if child.is_dir()
            and any(child.name.startswith(f"{family} - ") for family in EXPECTED_FAMILIES)
        }
        self.assertEqual(declared, physical)

        root_text = (APPENDIX_ROOT / "README.md").read_text(encoding="utf-8")
        table_positions: list[int] = []
        for entry in self.patterns:
            directory = APPENDIX_ROOT / entry["directory"]
            self.assertFalse(directory.is_symlink(), entry["directory"])
            page = directory / "README.md"
            example = directory / "example.py"
            self.assertTrue(page.is_file() and not page.is_symlink(), entry["id"])
            self.assertTrue(
                example.is_file() and not example.is_symlink(), entry["id"]
            )
            link = f"[{entry['name']}](<{entry['directory']}/README.md>)"
            self.assertEqual(1, root_text.count(link), entry["id"])
            table_positions.append(root_text.index(link))
            row = next(line for line in root_text.splitlines() if link in line)
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            self.assertEqual(8, len(cells), entry["id"])
            self.assertTrue(all(cells), entry["id"])
            self.assertEqual(entry["family"], cells[3])
            self.assertEqual(entry["route"], cells[4])
            self.assertEqual(entry["status"], cells[5])
            self.assertEqual(entry["simple_alternative"], cells[6].replace("`", ""))
            self.assertIn(f"]({entry['checkpoint_href']})", cells[7])
        self.assertEqual(sorted(table_positions), table_positions)

    def test_pattern_pages_expose_the_declared_learning_identity(self) -> None:
        for entry in self.patterns:
            page = (APPENDIX_ROOT / entry["directory"] / "README.md").read_text(
                encoding="utf-8"
            )
            with self.subTest(pattern=entry["id"]):
                self.assertGreaterEqual(len(page), 900)
                self.assertTrue(page.startswith("# "))
                self.assertIn(entry["name"].lower(), page.lower())
                self.assertIn(entry["family"].lower(), page.lower())
                normalized_page = page.lower().replace("-", " ")
                normalized_status = entry["status"].lower().replace("-", " ")
                self.assertIn(normalized_status, normalized_page)
                self.assertIn("example.py", page)
                self.assertIn("checkpoint", page.lower())
                self.assertIn("simpl", page.lower())

    def test_catalogue_markdown_links_resolve_locally(self) -> None:
        pages = [APPENDIX_ROOT / "README.md"]
        pages.extend(
            APPENDIX_ROOT / entry["directory"] / "README.md"
            for entry in self.patterns
        )
        for page in pages:
            text = page.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK_RE.finditer(text):
                raw_target = match.group(1) or match.group(2)
                parsed = urlsplit(raw_target)
                if parsed.scheme or parsed.netloc:
                    continue
                raw_path = unquote(parsed.path)
                target = page if not raw_path else (page.parent / raw_path)
                if page == APPENDIX_ROOT / "README.md" and raw_path in PENDING_ROOT_LOCALES:
                    continue
                with self.subTest(page=page.parent.name, target=raw_target):
                    self.assertTrue(target.is_file(), raw_target)
                    if parsed.fragment and target.suffix.lower() == ".md":
                        self.assertIn(unquote(parsed.fragment), heading_slugs(target))

    def test_examples_are_import_safe_and_bounded(self) -> None:
        for entry in self.patterns:
            path = APPENDIX_ROOT / entry["directory"] / "example.py"
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            imports = {
                node.names[0].name.split(".", 1)[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import) and node.names
            }
            imports.update(
                node.module.split(".", 1)[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            )
            infinite_loops = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.While)
                and isinstance(node.test, ast.Constant)
                and node.test.value is True
            ]
            with self.subTest(pattern=entry["id"]):
                self.assertFalse(imports & FORBIDDEN_IMPORTS)
                self.assertFalse(infinite_loops)
                stdout, stderr = StringIO(), StringIO()
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    load_example(path, APPENDIX_ROOT)
                self.assertEqual("", stdout.getvalue())
                self.assertEqual("", stderr.getvalue())

        observer = load_example(
            APPENDIX_ROOT
            / "behavioural - Bounded Synchronous Observer"
            / "example.py",
            APPENDIX_ROOT,
        )
        with self.assertRaises(ValueError):
            observer.JobEventSubject(True)
        subject = observer.JobEventSubject(2)
        received: list[str] = []
        remove_first = subject.subscribe(received.append)
        subject.subscribe(received.append)
        remove_first()
        remove_first()
        self.assertEqual((1, ()), subject.notify("one-event"))
        self.assertEqual(["one-event"], received)
        with self.assertRaises(TypeError):
            subject.subscribe(None)

        iterator = load_example(
            APPENDIX_ROOT / "behavioural - Iterator and Generator" / "example.py",
            APPENDIX_ROOT,
        )
        scanned: list[int] = []

        def infinite_blanks():
            while True:
                scanned.append(1)
                yield ""

        self.assertEqual(
            [],
            list(iterator.first_job_names(infinite_blanks(), 1, 3)),
        )
        self.assertEqual(3, len(scanned))
        with self.assertRaises(ValueError):
            list(iterator.first_job_names(["job"], 1.5, 3))

        repository = load_example(
            APPENDIX_ROOT / "architectural - Repository" / "example.py",
            APPENDIX_ROOT,
        )
        with self.assertRaises(repository.RepositoryContractError):
            repository.job_summary(repository.MalformedRepository(), "job-1")

        service = load_example(
            APPENDIX_ROOT / "architectural - Service Layer" / "example.py",
            APPENDIX_ROOT,
        )
        with self.assertRaises(service.ServiceContractError):
            service.complete_job(service.MalformedService(), "job-1")

        decorator = load_example(
            APPENDIX_ROOT
            / "structural - Decorator through Composition"
            / "example.py",
            APPENDIX_ROOT,
        )
        original = RuntimeError("original")
        measured = decorator.MeasuringExecutor(
            decorator.FailOnceExecutor(original),
            decorator.StepClock([1.0, 2.0]),
            decorator.BrokenMeasurements(),
        )
        try:
            measured.execute("job")
        except RuntimeError as error:
            self.assertIs(original, error)
        else:
            self.fail("the wrapped failure did not propagate")
        self.assertEqual("completed:job", measured.execute("job"))

        state_source = (
            APPENDIX_ROOT / "behavioural - State" / "example.py"
        ).read_text(encoding="utf-8")
        state_tree = ast.parse(state_source)
        self.assertNotIn(
            "CircuitBreaker",
            {node.name for node in ast.walk(state_tree) if isinstance(node, ast.ClassDef)},
        )

    def test_every_example_runs_from_its_own_directory(self) -> None:
        for entry in self.patterns:
            path = APPENDIX_ROOT / entry["directory"] / "example.py"
            with self.subTest(pattern=entry["id"]):
                completed = subprocess.run(
                    [sys.executable, "-B", path.name],
                    cwd=path.parent,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertLessEqual(len(completed.stdout.encode()), 16_384)
                self.assertEqual("", completed.stderr)


if __name__ == "__main__":
    unittest.main()
