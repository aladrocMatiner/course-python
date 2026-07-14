from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_book.py"
SPEC = importlib.util.spec_from_file_location("validate_book", MODULE_PATH)
assert SPEC and SPEC.loader
validate_book = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validate_book
SPEC.loader.exec_module(validate_book)


CONFIG = """
schema_version = 1
plugin_api_version = 1
python_min = "3.11"
snippet_timeout_seconds = 1
snippet_timeout_hard_max_seconds = 2
plugin_timeout_seconds = 3
output_limit_bytes = 65536
max_text_scan_bytes = 1048576
max_table_columns = 4
attributions = "ATTRIBUTIONS.toml"
baseline = "tools/book_quality_baseline.json"
unit_prefixes = ["chapter-", "appendix-"]
required_locales = ["README.md", "README.es.md", "README.ca.md", "README.sv.md", "README.ar.md"]
root_indexes = ["README.md", "README.en.md", "README.es.md", "README.ca.md", "README.sv.md", "README.ar.md"]
known_check_ids = ["unit:test", "domain:contract"]
[allowlists]
artifact_paths = []
sensitive_rules = []
""".lstrip()


SELECTORS = {
    "README.md": "English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)",
    "README.es.md": "[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)",
    "README.ca.md": "[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)",
    "README.sv.md": "[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)",
    "README.ar.md": "[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · العربية",
}


class TemporaryBook:
    def __init__(self) -> None:
        self._temporary = tempfile.TemporaryDirectory(prefix="book-quality-test-")
        self.root = Path(self._temporary.name)
        (self.root / "tools").mkdir()
        (self.root / "tools" / "book_quality.toml").write_text(CONFIG, encoding="utf-8")
        (self.root / "tools" / "book_quality_baseline.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "config_schema_version": 1,
                    "rule_version": 1,
                    "review_commit": "fixture",
                    "fingerprints": [],
                }
            ),
            encoding="utf-8",
        )
        (self.root / "ATTRIBUTIONS.toml").write_text("schema_version = 1\n", encoding="utf-8")
        root_index = "# Course\n\n- [Unit](chapter-01-test/README.md)\n"
        for filename in ("README.md", "README.en.md"):
            (self.root / filename).write_text(root_index, encoding="utf-8")
        localized_targets = {
            "README.es.md": "chapter-01-test/README.es.md",
            "README.ca.md": "chapter-01-test/README.ca.md",
            "README.sv.md": "chapter-01-test/README.sv.md",
            "README.ar.md": "chapter-01-test/README.ar.md",
        }
        for filename, target in localized_targets.items():
            body = f"# Index {filename}\n\n- [Unit]({target})\n"
            if filename == "README.ar.md":
                body = f"<div dir=\"rtl\">\n\n{body}\n</div>\n"
            (self.root / filename).write_text(body, encoding="utf-8")
        unit = self.root / "chapter-01-test"
        unit.mkdir()
        for filename, selector in SELECTORS.items():
            body = f"# Unit\n\n{selector}\n\n## Goal\n\nA small lesson.\n"
            if filename == "README.ar.md":
                body = f"<div dir=\"rtl\">\n\n{body}\n</div>\n"
            (unit / filename).write_text(body, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Book Test"], cwd=self.root, check=True)
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "fixture"], cwd=self.root, check=True)

    def close(self) -> None:
        self._temporary.cleanup()


class BookQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.book = TemporaryBook()
        self.root = self.book.root
        self.config = validate_book.load_config(self.root)

    def tearDown(self) -> None:
        self.book.close()

    def test_conforming_fixture_has_no_generic_errors(self) -> None:
        diagnostics = validate_book.collect_diagnostics(self.root, self.config, [])
        self.assertEqual([], [item for item in diagnostics if item.severity == "error"])

    def test_repository_workflow_is_pinned_bounded_and_least_privilege(self) -> None:
        workflow = MODULE_PATH.parents[1] / ".github" / "workflows" / "book-quality.yml"
        text = workflow.read_text(encoding="utf-8")

        def job_block(job_name: str) -> str:
            match = re.search(
                rf"(?ms)^  {re.escape(job_name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
                text,
            )
            self.assertIsNotNone(match, f"missing workflow job: {job_name}")
            assert match is not None
            return match.group("body")

        uses_pattern = re.compile(
            r'''(?mx)
            (?:
                ^\s*(?:-\s*)?
                |
                [,{]\s*
            )
            (?:uses|'uses'|"uses")\s*:\s*
            ([^,\s}\]#]+)
            '''
        )
        uses = uses_pattern.findall(text)
        self.assertTrue(uses)
        self.assertTrue(
            all(re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", value) for value in uses)
        )
        tag_probes = (
            "        uses : actions/example@v4\n",
            "        'uses': actions/example@v4\n",
            '        "uses" : actions/example@v4\n',
            "steps: [{ uses: actions/example@v4 }]\n",
            "steps: [{ 'uses': actions/example@v4 }]\n",
        )
        for probe in tag_probes:
            with self.subTest(probe=probe):
                detected = uses_pattern.findall(probe)
                self.assertEqual(["actions/example@v4"], detected)
                self.assertFalse(
                    all(
                        re.fullmatch(r"[^@\s]+@[0-9a-f]{40}", value)
                        for value in detected
                    )
                )
        self.assertIn("permissions:\n  contents: read", text)
        self.assertIn("timeout-minutes:", text)
        self.assertEqual(1, text.count("--changed-from"))
        self.assertIn("fetch-depth: 0", text)
        self.assertIn(
            'git diff --check "${{ github.event.pull_request.base.sha }}...HEAD"', text
        )
        self.assertIn("git diff-tree --check --no-commit-id -r HEAD", text)
        self.assertNotIn("pip install", text)
        self.assertNotIn("continue-on-error", text)
        self.assertNotIn("actions/upload-artifact", text)
        self.assertNotIn("${{ matrix.", text)
        self.assertNotRegex(text, r"(?m)^\s*run:\s*(?:find\b|for\b|.*(?:glob|rglob).*)")
        self.assertNotIn("|| true", text)
        self.assertNotIn("set +e", text)

        validate_job = job_block("validate")
        self.assertNotIn("--plugin", validate_job)
        pr_core = (
            'python -B tools/run_quality.py --profile core '
            '--changed-from "${{ github.event.pull_request.base.sha }}" --format text'
        )
        push_core = "python -B tools/run_quality.py --profile core --format text"
        self.assertEqual(1, validate_job.count(pr_core))
        self.assertEqual(1, validate_job.count(push_core))
        self.assertIn("fetch-depth: 0", validate_job)
        for direct_command in (
            "python -B -m unittest discover",
            "python -B tools/validate_curriculum.py",
            "python -B tools/parity_review.py",
            "python -B tools/validate_book.py",
        ):
            self.assertNotIn(direct_command, text)

        profiles_by_job = {
            "network-domain": "network-domain",
            "cpp-domain": "cpp-domain",
            "rust-domain": "rust-domain",
        }
        for job_name, profile in profiles_by_job.items():
            command = f"python -B tools/run_quality.py --profile {profile} --format text"
            block = job_block(job_name)
            self.assertEqual(1, block.count(command))
            self.assertEqual(1, block.count("--profile"))
            self.assertNotIn("--check", block)
            self.assertNotIn("--changed-from", block)
            self.assertEqual(1, text.count(command))
        self.assertEqual(5, text.count("python -B tools/run_quality.py"))
        self.assertEqual(5, text.count("--profile"))
        self.assertEqual(5, text.count("--format text"))
        self.assertGreaterEqual(text.count("timeout-minutes: 5"), 3)
        self.assertEqual(1, text.count("permissions:"))

    def test_cli_exit_codes_are_distinct_safe_and_read_only_from_foreign_cwd(self) -> None:
        script = self.root / "tools" / "validate_book.py"
        shutil.copyfile(MODULE_PATH, script)

        def source_snapshot() -> dict[str, bytes]:
            return {
                path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*")
                if path.is_file() and ".git" not in path.parts
            }

        before = source_snapshot()
        clean = subprocess.run(
            [sys.executable, "-B", str(script), "--format", "json"],
            cwd=self.root.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, clean.returncode, clean.stdout)
        self.assertEqual(before, source_snapshot())
        self.assertNotIn(str(self.root), clean.stdout)
        self.assertNotIn("Traceback", clean.stdout + clean.stderr)

        (self.root / "chapter-01-test" / "README.sv.md").unlink()
        violation = subprocess.run(
            [sys.executable, "-B", str(script), "--format", "json"],
            cwd=self.root.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(1, violation.returncode)
        self.assertIn("unit.locale_missing", violation.stdout)
        repeated = subprocess.run(
            [sys.executable, "-B", str(script), "--format", "json"],
            cwd=self.root.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(violation.stdout, repeated.stdout)
        public = json.loads(violation.stdout)["diagnostics"][0]
        self.assertTrue(
            {"schema_version", "rule_id", "severity", "path", "message", "remediation"} <= set(public)
        )

        config_path = self.root / "tools" / "book_quality.toml"
        config_path.write_text(CONFIG + "unknown = 1\n", encoding="utf-8")
        internal = subprocess.run(
            [sys.executable, "-B", str(script), "--format", "json"],
            cwd=self.root.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(2, internal.returncode)
        internal_payload = json.loads(internal.stdout)
        self.assertEqual("validator.internal", internal_payload["diagnostics"][0]["rule_id"])
        self.assertIn("remediation", internal_payload["diagnostics"][0])
        self.assertNotIn(str(self.root), internal.stdout)
        self.assertNotIn("Traceback", internal.stdout + internal.stderr)

    def test_config_rejects_unknown_and_wildcard_suppression(self) -> None:
        path = self.root / "tools" / "book_quality.toml"
        path.write_text(CONFIG + "unknown = 1\n", encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "unknown"):
            validate_book.load_config(self.root)
        path.write_text(CONFIG.replace("artifact_paths = []", 'artifact_paths = ["**"]'), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "wildcard"):
            validate_book.load_config(self.root)

    def test_config_rejects_missing_keys_bad_limits_and_escaping_paths(self) -> None:
        path = self.root / "tools" / "book_quality.toml"
        path.write_text(CONFIG.replace('python_min = "3.11"\n', ""), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "missing"):
            validate_book.load_config(self.root)
        path.write_text(CONFIG.replace("plugin_timeout_seconds = 3", "plugin_timeout_seconds = 99"), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "plugin_timeout"):
            validate_book.load_config(self.root)
        path.write_text(CONFIG.replace('baseline = "tools/book_quality_baseline.json"', 'baseline = "../outside.json"'), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "escapes"):
            validate_book.load_config(self.root)

    def test_unit_shape_and_root_mirror_fail_precisely(self) -> None:
        (self.root / "chapter-01-test" / "README.sv.md").unlink()
        (self.root / "chapter-01-test" / "README.fr.md").write_text("# French\n", encoding="utf-8")
        (self.root / "README.en.md").write_text("# Drift\n", encoding="utf-8")
        diagnostics = validate_book.check_unit_shape(
            self.root, self.config, validate_book.discover_units(self.root, self.config)
        )
        self.assertEqual(
            {"unit.locale_missing", "unit.locale_unexpected", "root.english_mirror"},
            {item.rule_id for item in diagnostics},
        )

    @unittest.skipUnless(hasattr(os, "symlink"), "requires symlink support")
    def test_discovery_rejects_symlinked_content_unit(self) -> None:
        outside = Path(self.book._temporary.name).parent / "outside-book-unit"
        outside.mkdir(exist_ok=True)
        link = self.root / "chapter-99-escape"
        try:
            link.symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(validate_book.ConfigError, "symlink"):
                validate_book.discover_units(self.root, self.config)
        finally:
            link.unlink(missing_ok=True)
            outside.rmdir()

    def test_selector_rejects_self_link(self) -> None:
        path = self.root / "chapter-01-test" / "README.es.md"
        path.write_text(
            "# Unit\n\n[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · "
            "[Svenska](README.sv.md) · [العربية](README.ar.md)\n",
            encoding="utf-8",
        )
        rules = {item.rule_id for item in validate_book.check_selectors(path, self.root)}
        self.assertIn("navigation.selector_self_link", rules)

    def test_root_navigation_requires_one_localized_target_in_order(self) -> None:
        path = self.root / "README.es.md"
        path.write_text(
            "# Index\n\n"
            "- [Later](chapter-02-later/README.es.md)\n"
            "- [First](chapter-01-test/README.md)\n"
            "- [First again](chapter-01-test/README.md)\n",
            encoding="utf-8",
        )
        later = self.root / "chapter-02-later"
        later.mkdir()
        (later / "README.es.md").write_text("# Later\n", encoding="utf-8")
        scan = validate_book.scan_markdown(path, self.root, self.config)
        rules = {item.rule_id for item in validate_book.check_root_navigation(path, self.root, scan)}
        self.assertTrue(
            {"navigation.root_language", "navigation.unit_missing", "navigation.unit_duplicate", "navigation.chapter_order"}
            <= rules
        )

    def test_markdown_parser_checks_hierarchy_fence_and_metadata(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n### Skipped\n\n<!-- bookcheck: timeout=1 timeout=2 -->\n```python\nprint('x')\n",
            encoding="utf-8",
        )
        scan = validate_book.scan_markdown(path, self.root, self.config)
        self.assertTrue(
            {"markdown.heading_skip", "markdown.fence_unclosed", "fence.classification", "fence.metadata"}
            <= {item.rule_id for item in scan.diagnostics}
        )

    def test_explicit_anchor_collision_and_all_fence_classes_are_deterministic(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        blocks = "\n".join(
            f"```text {classification}\nexample\n```"
            for classification in ("runnable", "output", "expected-error", "compile-only", "source-ref", "todo", "illustrative")
        )
        path.write_text(f"# Unit\n\n<a id=\"unit\"></a>\n\n{blocks}\n", encoding="utf-8")
        scan = validate_book.scan_markdown(path, self.root, self.config)
        self.assertIn("markdown.anchor_collision", {item.rule_id for item in scan.diagnostics})
        self.assertEqual(
            ["runnable", "output", "expected-error", "compile-only", "source-ref", "todo", "illustrative"],
            [fence.classification for fence in scan.fences],
        )

    def test_arabic_wrapper_ignores_html_like_text_inside_fence(self) -> None:
        path = self.root / "chapter-01-test" / "README.ar.md"
        path.write_text(
            '<div dir="rtl">\n\n# درس\n\n```html illustrative\n</div>\n```\n\n</div>\n',
            encoding="utf-8",
        )
        self.assertEqual([], validate_book.check_arabic(path, self.root))
        path.write_text('<div dir="rtl">\n\n# درس\u200f\n\n</div>\n', encoding="utf-8")
        self.assertEqual("rtl.invisible_control", validate_book.check_arabic(path, self.root)[0].rule_id)

    def test_links_resolve_fragments_and_reject_escape(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n[Good](README.es.md#index-es)\n[Bad](README.es.md#missing)\n[Escape](../../outside.md)\n",
            encoding="utf-8",
        )
        target = self.root / "chapter-01-test" / "README.es.md"
        target.write_text("# Index ES\n", encoding="utf-8")
        scan = validate_book.scan_markdown(path, self.root, self.config)
        target_scan = validate_book.scan_markdown(target, self.root, self.config)
        diagnostics = validate_book.check_links(path, self.root, scan, {target.resolve(): target_scan})
        self.assertEqual({"link.fragment_missing", "link.path_escape"}, {item.rule_id for item in diagnostics})

    def test_percent_encoded_unicode_query_and_explicit_fragment_resolve(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        target = self.root / "chapter-01-test" / "Lição.md"
        target.write_text('# Lição\n\n<a id="passo-final"></a>\n', encoding="utf-8")
        path.write_text(
            "# Unit\n\n[Localized](Li%C3%A7%C3%A3o.md?mode=read#passo-final)\n",
            encoding="utf-8",
        )
        scan = validate_book.scan_markdown(path, self.root, self.config)
        target_scan = validate_book.scan_markdown(target, self.root, self.config)
        self.assertEqual(
            [], validate_book.check_links(path, self.root, scan, {target.resolve(): target_scan})
        )

    def test_link_scanner_handles_html_and_shields_inline_and_fenced_code(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n"
            "`[not a link](missing-inline.md)`\n\n"
            "```text illustrative\n[not a link](missing-fence.md)\n```\n\n"
            "<!-- bookcheck: visual-text-equivalent -->\n"
            "A license badge is explained here. <img src=\"badge.svg\" alt=\"License badge\">\n"
            "<a href=\"README.es.md\">Spanish lesson</a>\n",
            encoding="utf-8",
        )
        (path.parent / "badge.svg").write_text("<svg/>", encoding="utf-8")
        scan = validate_book.scan_markdown(path, self.root, self.config)
        self.assertEqual([], scan.diagnostics)
        targets = {target for _image, _label, target, _line in scan.links}
        self.assertEqual({"badge.svg", "README.es.md"}, targets)
        scans = {path.resolve(): scan}
        self.assertEqual([], validate_book.check_links(path, self.root, scan, scans))

    def test_table_structure_requires_header_and_wide_alternative(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n| A | B |\n| one | two |\n\n"
            "| A | B | C | D | E |\n| --- | --- | --- | --- | --- |\n| 1 | 2 | 3 | 4 | 5 |\n",
            encoding="utf-8",
        )
        rules = {item.rule_id for item in validate_book.table_diagnostics(path, self.root, self.config)}
        self.assertEqual({"a11y.table_header", "a11y.table_alternative"}, rules)

    def test_python_snippet_success_error_compile_and_safety(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        runnable = validate_book.Fence("python", "runnable", "print('ok')", 4, {"expect": "ok"})
        expected = validate_book.Fence(
            "python", "expected-error", "raise ValueError('bad')", 8, {"expect-error": "ValueError"}
        )
        compile_only = validate_book.Fence("python", "compile-only", "value = 1", 12, {})
        unsafe = validate_book.Fence("python", "runnable", "import socket", 16, {})
        self.assertEqual([], validate_book.run_python_fence(runnable, path, self.root, self.config))
        self.assertEqual([], validate_book.run_python_fence(expected, path, self.root, self.config))
        self.assertEqual([], validate_book.run_python_fence(compile_only, path, self.root, self.config))
        self.assertEqual("snippet.unsafe_generic", validate_book.run_python_fence(unsafe, path, self.root, self.config)[0].rule_id)

    def test_python_snippet_allows_in_memory_list_remove(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        fence = validate_book.Fence(
            "python",
            "runnable",
            "items = ['keep', 'drop']\nitems.remove('drop')\nprint(items)",
            4,
            {},
        )
        self.assertEqual([], validate_book.run_python_fence(fence, path, self.root, self.config))

    def test_python_snippet_enforces_timeout_output_and_path_safety(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        timeout = validate_book.Fence("python", "runnable", "while True: pass", 4, {"timeout": "1"})
        overflow = validate_book.Fence("python", "runnable", "print('x' * 70000)", 8, {})
        destructive = validate_book.Fence("python", "runnable", "import os\nos.remove('lesson.txt')", 12, {})
        absolute = validate_book.Fence(
            "python", "runnable", "from pathlib import Path\nPath('/tmp/bookcheck').write_text('x')", 16, {}
        )
        process = validate_book.Fence("python", "runnable", "import os\nos.fork()", 20, {})
        self.assertEqual("snippet.timeout", validate_book.run_python_fence(timeout, path, self.root, self.config)[0].rule_id)
        self.assertEqual("snippet.output_limit", validate_book.run_python_fence(overflow, path, self.root, self.config)[0].rule_id)
        self.assertEqual("snippet.unsafe_generic", validate_book.run_python_fence(destructive, path, self.root, self.config)[0].rule_id)
        self.assertEqual("snippet.unsafe_generic", validate_book.run_python_fence(absolute, path, self.root, self.config)[0].rule_id)
        self.assertEqual("snippet.unsafe_generic", validate_book.run_python_fence(process, path, self.root, self.config)[0].rule_id)

    @unittest.skipUnless(hasattr(os, "fork"), "requires POSIX process groups")
    def test_bounded_runner_kills_surviving_descendant(self) -> None:
        code = "import os, time\npid = os.fork()\nif pid == 0:\n    time.sleep(30)\n    os._exit(0)\n"
        with self.assertRaises(validate_book.SurvivingDescendantError):
            validate_book.run_bounded(
                [sys.executable, "-I", "-B", "-c", code],
                cwd=self.root,
                timeout=2,
                output_limit=4096,
            )

    def test_python_snippet_copies_only_bounded_regular_fixture(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        fixture_path = self.root / "chapter-01-test" / "sample.txt"
        fixture_path.write_text("safe fixture", encoding="utf-8")
        valid = validate_book.Fence(
            "python", "runnable", "print(open('sample.txt', encoding='utf-8').read())", 4,
            {"fixture": "chapter-01-test/sample.txt", "expect": "safe fixture"},
        )
        escaping = validate_book.Fence(
            "python", "runnable", "print('never')", 8, {"fixture": "../outside.txt"}
        )
        self.assertEqual([], validate_book.run_python_fence(valid, path, self.root, self.config))
        self.assertEqual("snippet.fixture", validate_book.run_python_fence(escaping, path, self.root, self.config)[0].rule_id)

    def test_runnable_uses_the_following_output_fence_as_expectation(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n```python runnable\nprint('actual')\n```\n```text output\nexpected\n```\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.collect_diagnostics(self.root, self.config, [])
        self.assertIn("snippet.output_mismatch", {item.rule_id for item in diagnostics})

    def test_source_reference_requires_metadata_and_safe_existing_path(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        missing = validate_book.Fence("python", "source-ref", "", 3, {})
        self.assertEqual("source_ref.metadata", validate_book.source_ref_diagnostics(missing, path, self.root)[0].rule_id)
        valid = validate_book.Fence(
            "python", "source-ref", "", 3, {"path": "chapter-01-test/README.md", "check": "unit:test"}
        )
        self.assertEqual(
            [], validate_book.source_ref_diagnostics(valid, path, self.root, {"unit:test"})
        )
        invalid_id = validate_book.Fence(
            "python", "source-ref", "", 3, {"path": "chapter-01-test/README.md", "check": "Not stable"}
        )
        self.assertEqual(
            "source_ref.check_id", validate_book.source_ref_diagnostics(invalid_id, path, self.root)[0].rule_id
        )
        self.assertEqual(
            "source_ref.check",
            validate_book.source_ref_diagnostics(
                valid, path, self.root, {"unit:test"}, {"@plugin:unit"}
            )[0].rule_id,
        )

    def test_unselected_source_reference_is_reported_as_non_failing_information(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n<!-- bookcheck: path=chapter-01-test/README.md check=domain:contract -->\n"
            "```python source-ref\nprint('documented elsewhere')\n```\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.collect_diagnostics(self.root, self.config, [])
        evidence = [item for item in diagnostics if item.rule_id == "source_ref.not_run"]
        self.assertEqual(1, len(evidence))
        self.assertEqual("info", evidence[0].severity)
        failures, stale = validate_book.apply_baseline(self.root, self.config, diagnostics, set())
        self.assertNotIn(evidence[0], failures)
        self.assertEqual([], stale)

    def test_fingerprint_ignores_line_movement_but_not_construct(self) -> None:
        first = validate_book.Diagnostic("rule", "chapter/readme.md", "message", "fix", line=2, construct="x")
        moved = validate_book.Diagnostic("rule", "chapter/readme.md", "message", "fix", line=200, construct="x")
        changed = validate_book.Diagnostic("rule", "chapter/readme.md", "message", "fix", line=2, construct="y")
        self.assertEqual(validate_book.fingerprinted([first])[0][0], validate_book.fingerprinted([moved])[0][0])
        self.assertNotEqual(validate_book.fingerprinted([first])[0][0], validate_book.fingerprinted([changed])[0][0])

    def test_baseline_allows_exact_debt_rejects_changed_and_reports_stale(self) -> None:
        diagnostic = validate_book.Diagnostic("legacy", "chapter-01-test/README.md", "old", "fix", construct="x")
        fingerprint = validate_book.fingerprinted([diagnostic])[0][0]
        baseline_path = self.root / "tools" / "book_quality_baseline.json"
        payload = json.loads(baseline_path.read_text(encoding="utf-8"))
        payload["fingerprints"] = [fingerprint]
        baseline_path.write_text(json.dumps(payload), encoding="utf-8")
        failures, stale = validate_book.apply_baseline(self.root, self.config, [diagnostic], set())
        self.assertEqual(([], []), (failures, stale))
        failures, stale = validate_book.apply_baseline(
            self.root, self.config, [diagnostic], {"chapter-01-test/README.md"}
        )
        self.assertEqual([], failures)
        changed_construct = validate_book.Diagnostic(
            "legacy", "chapter-01-test/README.md", "old", "fix", construct="changed"
        )
        failures, _ = validate_book.apply_baseline(
            self.root, self.config, [changed_construct], {"chapter-01-test/README.md"}
        )
        self.assertEqual([changed_construct], failures)
        rendered = validate_book.render_text([], [], [diagnostic])
        self.assertIn("baseline.accepted", rendered)
        _, stale = validate_book.apply_baseline(self.root, self.config, [], set())
        self.assertEqual([fingerprint], stale)

    def test_baseline_rejects_duplicates_unsorted_values_and_unknown_fields(self) -> None:
        path = self.root / "tools" / "book_quality_baseline.json"
        fingerprint = "a" * 64
        payload = {
            "schema_version": 1,
            "config_schema_version": 1,
            "rule_version": 1,
            "review_commit": "fixture",
            "fingerprints": [fingerprint, fingerprint],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "unique sorted"):
            validate_book.load_baseline(self.root, self.config)
        payload["fingerprints"] = []
        payload["unexpected"] = True
        path.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(validate_book.ConfigError, "unknown baseline"):
            validate_book.load_baseline(self.root, self.config)

    def test_changed_paths_include_staged_deleted_and_untracked_names(self) -> None:
        tracked = self.root / "chapter-01-test" / "README.ca.md"
        tracked.write_text(tracked.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        deleted = self.root / "chapter-01-test" / "README.sv.md"
        deleted.unlink()
        untracked = self.root / "chapter-01-test" / "new lesson.txt"
        untracked.write_text("new", encoding="utf-8")
        subprocess.run(["git", "add", str(tracked.relative_to(self.root))], cwd=self.root, check=True)
        changed = validate_book.changed_paths(self.root, "HEAD")
        self.assertTrue(
            {
                "chapter-01-test/README.ca.md",
                "chapter-01-test/README.sv.md",
                "chapter-01-test/new lesson.txt",
            }
            <= changed
        )
        diagnostics = validate_book.stable_path_change_diagnostics(self.root, self.config, changed)
        self.assertIn("chapter-01-test/README.sv.md", {item.path for item in diagnostics})

    def test_exact_path_migration_accepts_only_an_existing_replacement(self) -> None:
        removed = "chapter-01-test/old-name.md"
        replacement = "chapter-01-test/new-name.md"
        (self.root / replacement).write_text("replacement", encoding="utf-8")
        self.config["path_migrations"] = [{"old": removed, "new": replacement}]
        self.assertEqual(
            [], validate_book.stable_path_change_diagnostics(self.root, self.config, {removed, replacement})
        )

    def test_hygiene_finds_ignored_artifact_and_redacts_secret(self) -> None:
        (self.root / ".gitignore").write_text("build/\n", encoding="utf-8")
        (self.root / "build").mkdir()
        (self.root / "build" / "output.whl").write_text("artifact", encoding="utf-8")
        (self.root / "token.txt").write_text("ghp_abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")
        (self.root / "student.txt").write_text("student_email = private@example.invalid", encoding="utf-8")
        (self.root / "undeclared.pem").write_text("public-looking but undeclared", encoding="utf-8")
        diagnostics = validate_book.hygiene_diagnostics(self.root, self.config)
        rules = {item.rule_id for item in diagnostics}
        self.assertIn("hygiene.artifact", rules)
        self.assertIn("hygiene.sensitive", rules)
        self.assertIn("hygiene.personal_data", rules)
        self.assertNotIn("ghp_", "\n".join(item.message for item in diagnostics))

    def test_hygiene_detects_cache_directory_components_and_recovers(self) -> None:
        cache_files = {
            ".mypy_cache/3.13/state.json",
            ".pytest_cache/v/cache/nodeids",
            ".ruff_cache/state.json",
        }
        for raw in cache_files:
            candidate = self.root / raw
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text("generated", encoding="utf-8")
        (self.root / ".mypy_cache" / ".gitignore").write_text("*\n", encoding="utf-8")
        ordinary = self.root / "notes" / "cache" / "state.json"
        ordinary.parent.mkdir(parents=True)
        ordinary.write_text("lesson data", encoding="utf-8")

        detected = {
            item.path
            for item in validate_book.hygiene_diagnostics(self.root, self.config)
            if item.rule_id == "hygiene.artifact"
        }
        self.assertTrue(cache_files <= detected)
        self.assertNotIn("notes/cache/state.json", detected)

        shutil.rmtree(self.root / ".mypy_cache")
        shutil.rmtree(self.root / ".pytest_cache")
        shutil.rmtree(self.root / ".ruff_cache")
        recovered = {
            item.path
            for item in validate_book.hygiene_diagnostics(self.root, self.config)
            if item.rule_id == "hygiene.artifact"
        }
        self.assertFalse(cache_files & recovered)

    def test_attribution_review_uses_neutral_language(self) -> None:
        (self.root / "ATTRIBUTIONS.toml").write_text(
            textwrap.dedent(
                """
                schema_version = 1
                [[entries]]
                id = "review"
                paths = ["chapter-01-test/README.md"]
                status = "review-required"
                """
            ),
            encoding="utf-8",
        )
        diagnostics = validate_book.attribution_diagnostics(self.root, self.config)
        self.assertEqual("attribution.review_required", diagnostics[0].rule_id)
        self.assertNotRegex(diagnostics[0].message, r"illegal|infring|copied")

    def test_attribution_reviewed_license_requires_url_and_visible_notice(self) -> None:
        (self.root / "NOTICE.md").write_text("Different notice\n", encoding="utf-8")
        (self.root / "ATTRIBUTIONS.toml").write_text(
            textwrap.dedent(
                """
                schema_version = 1
                [[entries]]
                id = "licensed"
                paths = ["chapter-01-test/README.md"]
                kind = "prose"
                status = "licensed-recorded"
                source_title = "Source"
                source_url = "not-a-url"
                author_or_holder = "Holder"
                license = "Example"
                required_notice = "Required exact notice"
                notice_location = "NOTICE.md"
                adaptation = "Translated and shortened"
                review_date = "2026-07-13"
                review_role = "provenance owner"
                """
            ),
            encoding="utf-8",
        )
        rules = {item.rule_id for item in validate_book.attribution_diagnostics(self.root, self.config)}
        self.assertEqual({"attribution.source_url", "attribution.notice"}, rules)

    def test_plugin_protocol_accepts_namespaced_diagnostics(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            textwrap.dedent(
                """
                def check(context):
                    return [{
                        "rule_id": "smoke",
                        "path": "chapter-01-test/README.md",
                        "message": "domain failure",
                        "remediation": "fix domain",
                    }]

                def register(registry):
                    registry.add(plugin_id="fixture", api_version=1, checks={"unit": check}, timeout=2)
                """
            ),
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertEqual(["plugin.fixture.unit.smoke"], [item.rule_id for item in diagnostics])

    def test_explicit_plugin_reports_positive_check_evidence(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "def check(context): return []\n"
            "def register(registry):\n"
            "    registry.add(plugin_id='fixture', api_version=1, checks={'unit': check}, timeout=2)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertEqual(["plugin.check_passed"], [item.rule_id for item in diagnostics])
        self.assertEqual("info", diagnostics[0].severity)

    def test_plugin_fails_closed_on_missing_prerequisite(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "def register(registry):\n"
            "    registry.add(plugin_id='fixture', api_version=1, checks={}, prerequisites=['definitely-not-a-tool'], timeout=2)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertEqual("plugin.prerequisite", diagnostics[0].rule_id)

    def test_plugin_output_is_bounded(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "print('x' * 70000)\n"
            "def register(registry):\n"
            "    registry.add(plugin_id='fixture', api_version=1, checks={}, timeout=2)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertEqual("plugin.output_limit", diagnostics[0].rule_id)

    def test_plugin_rejects_malformed_diagnostic_and_source_mutation(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            textwrap.dedent(
                """
                from pathlib import Path

                def check(context):
                    target = Path(context["root"]) / "chapter-01-test" / "README.md"
                    target.write_text(target.read_text(encoding="utf-8") + "mutated", encoding="utf-8")
                    return ["not-an-object"]

                def register(registry):
                    registry.add(plugin_id="fixture", api_version=1, checks={"unit": check}, timeout=2)
                """
            ),
            encoding="utf-8",
        )
        rules = {item.rule_id for item in validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)}
        self.assertEqual({"plugin.diagnostic_schema", "plugin.source_mutation"}, rules)

    def test_plugin_registration_crash_timeout_and_escape_fail_closed(self) -> None:
        plugin = self.root / "plugin.py"
        cases = {
            "api": (
                "def register(registry):\n"
                "    registry.add(plugin_id='fixture', api_version=99, checks={}, timeout=1)\n",
                "plugin.registration",
            ),
            "duplicate": (
                "def register(registry):\n"
                "    registry.add(plugin_id='fixture', api_version=1, checks={}, timeout=1)\n"
                "    registry.add(plugin_id='fixture', api_version=1, checks={}, timeout=1)\n",
                "plugin.registration",
            ),
            "crash": (
                "def check(context): raise RuntimeError('boom')\n"
                "def register(registry):\n"
                "    registry.add(plugin_id='fixture', api_version=1, checks={'unit': check}, timeout=1)\n",
                "plugin.failure",
            ),
            "escape": (
                "def check(context):\n"
                "    return [{'rule_id': 'x', 'path': '../escape', 'message': 'x', 'remediation': 'x'}]\n"
                "def register(registry):\n"
                "    registry.add(plugin_id='fixture', api_version=1, checks={'unit': check}, timeout=1)\n",
                "plugin.diagnostic_schema",
            ),
            "timeout": (
                "def check(context):\n"
                "    while True: pass\n"
                "def register(registry):\n"
                "    registry.add(plugin_id='fixture', api_version=1, checks={'unit': check}, timeout=1)\n",
                "plugin.timeout",
            ),
        }
        self.config["plugin_timeout_seconds"] = 1
        for name, (source, expected) in cases.items():
            with self.subTest(name=name):
                plugin.write_text(source, encoding="utf-8")
                rules = {item.rule_id for item in validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)}
                self.assertIn(expected, rules)

    def test_fence_language_metadata_and_physical_output_contracts(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n"
            "<!-- bookcheck: timeout=1 -->\n\n"
            "```bash runnable\necho unsafe\n```\n\n"
            "<!-- bookcheck: expect-error=ValueError -->\n"
            "```python runnable\nprint('ok')\n```\n\n"
            "```cpp compile-only\nnot C++\n```\n\n"
            "```python runnable\nprint('x')\n```\n\n## Intervening heading\n\n"
            "```text output\nx\n```\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.scan_markdown(path, self.root, self.config).diagnostics
        by_rule = {item.rule_id: item for item in diagnostics}
        self.assertTrue(
            {
                "fence.metadata_orphan",
                "fence.metadata_incompatible",
                "fence.execution_language",
                "fence.compile_language",
                "fence.output_orphan",
            }
            <= set(by_rule)
        )
        self.assertTrue(all(item.remediation for item in by_rule.values()))

    def test_snippet_rejects_obvious_source_write_and_external_import(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        original = (self.root / "README.md").read_bytes()
        write_code = (
            "from pathlib import Path\n"
            f"Path({str(self.root)!r}).joinpath('README.md').write_text('mutated')"
        )
        write_fence = validate_book.Fence("python", "runnable", write_code, 4, {})
        dependency_fence = validate_book.Fence(
            "python", "runnable", "import definitely_external_package", 8, {}
        )
        write_diagnostic = validate_book.run_python_fence(
            write_fence, path, self.root, self.config
        )[0]
        dependency_diagnostic = validate_book.run_python_fence(
            dependency_fence, path, self.root, self.config
        )[0]
        self.assertEqual("snippet.unsafe_generic", write_diagnostic.rule_id)
        self.assertEqual("snippet.unsafe_generic", dependency_diagnostic.rule_id)
        self.assertTrue(write_diagnostic.remediation)
        self.assertEqual(original, (self.root / "README.md").read_bytes())

    def test_dormant_local_import_is_not_executed_by_generic_runner(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        fence = validate_book.Fence(
            "python",
            "runnable",
            "def later():\n    from local_package import helper\n    return helper()",
            4,
            {},
        )
        self.assertEqual([], validate_book.run_python_fence(fence, path, self.root, self.config))

    def test_timeout_metadata_is_a_quality_diagnostic_and_fixture_is_read_only(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        invalid = validate_book.Fence("python", "runnable", "print('x')", 4, {"timeout": "abc"})
        diagnostic = validate_book.run_python_fence(invalid, path, self.root, self.config)[0]
        self.assertEqual("snippet.timeout_metadata", diagnostic.rule_id)
        self.assertTrue(diagnostic.remediation)

        fixture = self.root / "chapter-01-test" / "sample.txt"
        fixture.write_text("original", encoding="utf-8")
        writer = validate_book.Fence(
            "python",
            "runnable",
            "open('sample.txt', 'w', encoding='utf-8').write('changed')",
            8,
            {"fixture": "chapter-01-test/sample.txt"},
        )
        rules = {
            item.rule_id
            for item in validate_book.run_python_fence(writer, path, self.root, self.config)
        }
        self.assertTrue(rules & {"snippet.unexpected_failure", "snippet.fixture_mutation"})
        self.assertEqual("original", fixture.read_text(encoding="utf-8"))

    def test_ghost_source_reference_is_rejected_declaratively(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        fence = validate_book.Fence(
            "python",
            "source-ref",
            "",
            3,
            {"path": "chapter-01-test/README.md", "check": "ghost:anything"},
        )
        diagnostic = validate_book.source_ref_diagnostics(
            fence, path, self.root, set(self.config["known_check_ids"])
        )[0]
        self.assertEqual("source_ref.check", diagnostic.rule_id)
        self.assertIn("known_check_ids", diagnostic.remediation)

    def test_selector_targets_exact_sibling_and_normalizes_self_link(self) -> None:
        other = self.root / "chapter-02-other"
        other.mkdir()
        (other / "README.ca.md").write_text("# Other\n", encoding="utf-8")
        path = self.root / "chapter-01-test" / "README.es.md"
        path.write_text(
            "# Unit\n\n[English](README.md) · [Español](./README.es.md) · "
            "[Català](../chapter-02-other/README.ca.md) · [Svenska](README.sv.md) · "
            "[العربية](README.ar.md)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.check_selectors(path, self.root)
        rules = {item.rule_id for item in diagnostics}
        self.assertIn("navigation.selector_self_link", rules)
        self.assertIn("navigation.selector_target", rules)
        self.assertTrue(all(item.remediation for item in diagnostics))

    def test_empty_link_generic_alt_and_marker_without_prose_fail(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        (path.parent / "badge.svg").write_text("<svg/>", encoding="utf-8")
        path.write_text(
            "# Unit\n\n\n\n\n[](README.es.md)\n\n"
            "<!-- bookcheck: visual-text-equivalent -->\n![image](badge.svg)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.scan_markdown(path, self.root, self.config).diagnostics
        rules = {item.rule_id for item in diagnostics}
        self.assertIn("a11y.link_text", rules)
        self.assertIn("a11y.image_alt", rules)
        self.assertIn("a11y.visual_equivalent", rules)
        self.assertTrue(all(item.remediation for item in diagnostics))

    def test_sensitive_allowlist_is_exact_by_path_and_rule(self) -> None:
        fixture = self.root / "fixture.txt"
        fixture.write_text(
            "ghp_abcdefghijklmnopqrstuvwxyz123456\nstudent_email = private@example.invalid\n",
            encoding="utf-8",
        )
        self.config["allowlists"]["sensitive_rules"] = [
            {"path": "fixture.txt", "rule": "hygiene.sensitive"}
        ]
        diagnostics = [
            item
            for item in validate_book.hygiene_diagnostics(self.root, self.config)
            if item.path == "fixture.txt"
        ]
        self.assertEqual(["hygiene.personal_data"], [item.rule_id for item in diagnostics])
        self.assertNotIn("private@example.invalid", diagnostics[0].message)

    def test_attribution_required_marker_creates_candidate(self) -> None:
        path = self.root / "chapter-01-test" / "README.md"
        path.write_text(
            "# Unit\n\n<!-- attribution-required -->\nAdapted exercise.\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.attribution_diagnostics(self.root, self.config)
        candidates = [
            item for item in diagnostics
            if item.rule_id == "attribution.candidate_unrecorded" and item.path == "chapter-01-test/README.md"
        ]
        self.assertEqual(1, len(candidates))
        self.assertTrue(candidates[0].remediation)

    def test_stable_paths_ignore_deleted_companions_but_protect_public_readmes(self) -> None:
        companion = "chapter-01-test/examples/obsolete.py"
        public = "chapter-01-test/README.sv.md"
        (self.root / public).unlink()
        diagnostics = validate_book.stable_path_change_diagnostics(
            self.root, self.config, {companion, public}
        )
        self.assertEqual([public], [item.path for item in diagnostics])

    def test_appendices_must_follow_all_chapters(self) -> None:
        path = self.root / "README.md"
        path.write_text(
            "# Course\n\n- [Appendix](appendix-a/README.md)\n"
            "- [Chapter](chapter-01-test/README.md)\n",
            encoding="utf-8",
        )
        appendix = self.root / "appendix-a"
        appendix.mkdir()
        (appendix / "README.md").write_text("# Appendix\n", encoding="utf-8")
        scan = validate_book.scan_markdown(path, self.root, self.config)
        diagnostics = validate_book.check_root_navigation(path, self.root, scan)
        self.assertIn("navigation.appendix_order", {item.rule_id for item in diagnostics})

    def test_extended_artifact_families_are_detected(self) -> None:
        paths = [
            ".tox/state.txt",
            ".idea/workspace.xml",
            "coverage.xml",
            "package.egg-info/PKG-INFO",
            "release.tar.gz",
            "CMakeCache.txt",
        ]
        for raw in paths:
            candidate = self.root / raw
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text("generated", encoding="utf-8")
        detected = {
            item.path
            for item in validate_book.hygiene_diagnostics(self.root, self.config)
            if item.rule_id == "hygiene.artifact"
        }
        self.assertTrue(set(paths) <= detected)

    def test_fingerprint_normalizes_platform_path_separators(self) -> None:
        posix = validate_book.Diagnostic("rule", "a/b.md", "m", "fix", construct="x")
        windows = validate_book.Diagnostic("rule", r"a\b.md", "m", "fix", construct="x")
        self.assertEqual(
            validate_book.fingerprinted([posix])[0][0],
            validate_book.fingerprinted([windows])[0][0],
        )

    def test_plugin_declared_timeout_is_enforced_per_check(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "import time\n"
            "def check(context): time.sleep(2); return []\n"
            "def register(registry):\n"
            "    registry.add(plugin_id='slow', api_version=1, checks={'unit': check}, timeout=1)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertIn("plugin.timeout", {item.rule_id for item in diagnostics})

    def test_plugin_rejects_unsafe_ids_and_redacts_unsafe_diagnostic_text(self) -> None:
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "def check(context):\n"
            "    return [{'rule_id':'leak','path':'chapter-01-test/README.md',"
            "'message':'ghp_abcdefghijklmnopqrstuvwxyz123456 at /tmp/private/file',"
            "'remediation':'use /home/private/file'}]\n"
            "def register(registry):\n"
            "    registry.add(plugin_id='safe', api_version=1, checks={'unit': check}, timeout=1)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertIn("plugin.diagnostic_schema", {item.rule_id for item in diagnostics})
        rendered = validate_book.render_text(diagnostics, [])
        self.assertNotIn("ghp_", rendered)
        self.assertNotIn("/tmp/private", rendered)

        plugin.write_text(
            "def register(registry):\n"
            "    registry.add(plugin_id='bad id', api_version=1, checks={'bad/check': lambda c: []}, timeout=1)\n",
            encoding="utf-8",
        )
        diagnostics = validate_book.plugin_diagnostics(self.root, ["plugin.py"], self.config)
        self.assertIn("plugin.registration", {item.rule_id for item in diagnostics})

    def test_plugin_protocol_failure_uses_exit_two_and_public_json(self) -> None:
        script = self.root / "tools" / "validate_book.py"
        shutil.copyfile(MODULE_PATH, script)
        plugin = self.root / "plugin.py"
        plugin.write_text(
            "def register(registry): registry.add(plugin_id='x', api_version=99, checks={}, timeout=1)\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [sys.executable, "-B", str(script), "--format", "json", "--plugin", "plugin.py"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(2, completed.returncode)
        payload = json.loads(completed.stdout)
        diagnostic = payload["diagnostics"][0]
        self.assertEqual("plugin.registration", diagnostic["rule_id"])
        self.assertTrue(diagnostic["remediation"])


if __name__ == "__main__":
    unittest.main()
