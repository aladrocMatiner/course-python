from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "parity_review.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("parity_review", MODULE_PATH)
assert SPEC and SPEC.loader
parity_review = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = parity_review
SPEC.loader.exec_module(parity_review)


def manifest_fixture(root: Path) -> dict:
    sources = []
    records = []
    for index, unit_name in enumerate(published_unit_names()):
        unit = root / unit_name
        unit.mkdir()
        canonical = unit / "README.md"
        canonical.write_text(f"# Canonical {index}\n", encoding="utf-8")
        canonical_sha = parity_review.digest(canonical)
        canonical_signals = synthetic_signals(canonical, root, {})
        sources.append(
            {
                "unit": unit_name,
                "path": f"{unit_name}/README.md",
                "sha256": canonical_sha,
                "signals": canonical_signals,
                "audit": "pending-human-review",
            }
        )
        for locale, filename in parity_review.LOCALES.items():
            localized = unit / filename
            localized.write_text(f"# Localized {index} {locale}\n", encoding="utf-8")
            localized_signals = synthetic_signals(localized, root, {})
            records.append(
                {
                    "unit": unit_name,
                    "locale": locale,
                    "path": f"{unit_name}/{filename}",
                    "canonical_sha256": canonical_sha,
                    "localized_sha256": parity_review.digest(localized),
                    "status": "inventoried",
                    "priority": parity_review.initial_priority(
                        locale, canonical_signals, localized_signals, unit_name
                    ),
                    "signals": localized_signals,
                    "observed_gaps": parity_review.gap_signals(
                        canonical_signals, localized_signals
                    ),
                    "contract": {
                        dimension: "pending" for dimension in parity_review.CONTRACT_DIMENSIONS
                    },
                    "exceptions": [],
                    "automated_commands": [],
                    "linguistic_review": parity_review.empty_review(),
                    "technical_review": parity_review.empty_review(),
                }
            )
    return {
        "schema_version": parity_review.LEGACY_SCHEMA_VERSION,
        "notice": "Structural metrics are triage signals, never proof of semantic or linguistic parity.",
        "sources": sources,
        "records": records,
    }


def published_unit_names() -> list[str]:
    return sorted(
        [f"chapter-{number:02d}-lesson" for number in range(1, 26)]
        + ["appendix-cli-parser", "appendix-algorithms"]
    )


@contextlib.contextmanager
def expected_units_fixture():
    units = published_unit_names()
    with patch.object(parity_review, "expected_unit_ids", return_value=units):
        yield units


def add_topology_units(root: Path) -> list[str]:
    """Add the three publication units used by the 27-to-30 migration fixture."""

    new_units = [
        f"chapter-{number:02d}-new-lesson" for number in range(26, 29)
    ]
    for number in range(26, 29):
        unit_name = f"chapter-{number:02d}-new-lesson"
        unit = root / unit_name
        unit.mkdir()
        (unit / "README.md").write_text(
            f"# Canonical new lesson {number}\n", encoding="utf-8"
        )
        for locale, filename in parity_review.LOCALES.items():
            (unit / filename).write_text(
                f"# Localized new lesson {number} {locale}\n", encoding="utf-8"
            )
    return sorted([*published_unit_names(), *new_units])


def write_legacy_manifest(root: Path, payload: dict) -> Path:
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
    path = tools / "parity_manifest.json"
    path.write_bytes(parity_review.canonical_json_bytes(payload))
    return path


def migrate_fixture(root: Path, payload: dict) -> tuple[Path, bytes]:
    path = write_legacy_manifest(root, payload)
    original = path.read_bytes()
    with expected_units_fixture():
        parity_review.migrate_partitioned(path, root)
    return path, original


def file_snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def independent_canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def independent_sha256(payload: object) -> str:
    return hashlib.sha256(independent_canonical_json_bytes(payload)).hexdigest()


def synthetic_signals(path: Path, root: Path, config: dict) -> dict:
    del root, config
    content = path.read_text(encoding="utf-8")
    return {
        "words": len(content.split()),
        "headings": content.count("# "),
        "fences": content.count("```") // 2,
        "source_refs": 0,
        "fence_sequence_sha256": parity_review.digest(path),
    }


def write_v2_support_files(root: Path) -> None:
    english = "# Course fixture\n\nNo external links.\n"
    localized = {
        "README.md": english,
        "README.en.md": english,
        "README.es.md": "# Curso de prueba\n",
        "README.ca.md": "# Curs de prova\n",
        "README.sv.md": "# Testkurs\n",
        "README.ar.md": "<div dir=\"rtl\">\n\n# دورة اختبار\n\n</div>\n",
    }
    for name, content in localized.items():
        (root / name).write_text(content, encoding="utf-8")
    icons = root / "icons"
    icons.mkdir()
    (icons / "cc-by-sa.svg").write_text("<svg></svg>\n", encoding="utf-8")
    tools = root / "tools"
    tools.mkdir(exist_ok=True)
    repository_root = MODULE_PATH.parents[1]
    (root / "BOOK_STYLE.md").write_bytes(
        (repository_root / "BOOK_STYLE.md").read_bytes()
    )
    for name in (
        "parity_review.py",
        "validate_book.py",
        "run_quality.py",
        "book_quality.toml",
        "learning_bridges_plugin.py",
        "quality_matrix.toml",
    ):
        (tools / name).write_bytes((MODULE_PATH.parent / name).read_bytes())
    profile_source = MODULE_PATH.parent / "render_review_profile.json"
    (tools / "render_review_profile.json").write_bytes(profile_source.read_bytes())
    (root / "ATTRIBUTIONS.toml").write_text(
        "schema_version = 1\nentries = []\n", encoding="utf-8"
    )


def topology_config(root: Path) -> dict:
    """Return the fixture config without repository-specific file allowlists."""

    config = tomllib.loads((root / "tools/book_quality.toml").read_text("utf-8"))
    config["allowlists"] = {"artifact_paths": [], "sensitive_rules": []}
    return config


def refresh_review_fixture(root: Path, path: Path) -> None:
    """Refresh migrated synthetic metrics before asserting byte preservation."""

    units = published_unit_names()
    with patch.object(
        parity_review, "expected_unit_ids", return_value=units
    ), patch.object(
        parity_review.validate_book,
        "load_config",
        return_value=topology_config(root),
    ):
        previous, baseline = parity_review.snapshot_manifest(path, root, units)
        refreshed = parity_review.build_v2_manifest(root, previous)
        parity_review.write_partitioned_manifest(path, refreshed, root, baseline)


def migrate_review_fixture(root: Path, payload: dict) -> Path:
    path, _ = migrate_fixture(root, payload)
    write_v2_support_files(root)
    with expected_units_fixture():
        parity_review.migrate_review_schema(path, root)
    return path


def approve_review(review: dict) -> None:
    review.update(
        {
            "result": "approved",
            "role": "competent fixture reviewer",
            "review_date": "2026-07-15",
            "notes": "fixture evidence bound to current inputs",
        }
    )


def approve_render_review(
    review: dict, relative: str, root: Path, profile: dict
) -> None:
    approve_review(review)
    environment = {
        "assistive_technology": "fixture-at",
        "assistive_technology_version": "1",
        "browser": "fixture-browser",
        "browser_version": "1",
        "os": "fixture-os",
        "os_version": "1",
        "renderer": "fixture-renderer",
        "renderer_version": "1",
    }
    review["environment"] = environment
    review["render_input_sha256"] = parity_review.render_input_sha256(
        relative,
        review["page_sha256"],
        review["profile_sha256"],
        parity_review.render_assets(root, profile),
        environment,
    )


def approve_v2_payload(root: Path, payload: dict) -> None:
    profile, _profile_sha256 = parity_review.load_render_profile(root)
    for source in payload["sources"]:
        approve_review(source["canonical_review"])
        approve_render_review(
            source["rendered_accessibility_review"], source["path"], root, profile
        )
    for record in payload["records"]:
        record["contract"] = {
            dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
        }
        record["automated_commands"] = [
            "python -B tools/validate_book.py",
            "python -B tools/parity_review.py",
        ]
        approve_review(record["linguistic_review"])
        approve_review(record["technical_review"])
        approve_render_review(
            record["rendered_accessibility_review"], record["path"], root, profile
        )
        if record["locale"] == "ar":
            approve_render_review(record["bidi_review"], record["path"], root, profile)
        record["status"] = "accepted"
    root_publication = payload["root_publication"]
    approve_review(root_publication["canonical_review"])
    for page in root_publication["pages"]:
        approve_render_review(
            page["rendered_accessibility_review"], page["path"], root, profile
        )
        for field in ("linguistic_review", "technical_review"):
            if field in page:
                approve_review(page[field])
        if "bidi_review" in page:
            approve_render_review(page["bidi_review"], page["path"], root, profile)
    root_publication["state"] = "accepted"


class ParityReviewTests(unittest.TestCase):
    def test_transition_rejects_regression_and_allows_blocking(self) -> None:
        parity_review.validate_transition("drafted", "automated-signals-pass")
        parity_review.validate_transition("drafted", "blocked")
        with self.assertRaisesRegex(parity_review.ParityError, "regression"):
            parity_review.validate_transition("technical-reviewed", "drafted")

    def test_accepted_record_requires_both_human_reviews(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            record = payload["records"][0]
            record["status"] = "accepted"
            record["contract"] = {
                dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
            }
            with self.assertRaisesRegex(parity_review.ParityError, "human approvals"):
                parity_review.validate_manifest(payload, root)

    def test_publication_mode_requires_all_published_reviews(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            with self.assertRaisesRegex(parity_review.ParityError, "publication review incomplete"):
                parity_review.validate_manifest(payload, root, require_accepted=True)
            for source in payload["sources"]:
                source["audit"] = "approved"
            approved_review = {
                "result": "approved",
                "role": "reviewer",
                "review_date": "2026-07-13",
                "notes": "reviewed",
            }
            for record in payload["records"]:
                record["status"] = "accepted"
                record["contract"] = {
                    dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
                }
                record["linguistic_review"] = dict(approved_review)
                record["technical_review"] = dict(approved_review)
                record["automated_commands"] = [
                    "python -B tools/validate_book.py",
                    "python -B tools/parity_review.py",
                ]
            parity_review.validate_manifest(payload, root, require_accepted=True)

    def test_accepted_record_requires_source_audit_and_automated_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            record = payload["records"][0]
            record["status"] = "accepted"
            record["contract"] = {
                dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
            }
            approved_review = {
                "result": "approved",
                "role": "reviewer",
                "review_date": "2026-07-13",
                "notes": "reviewed",
            }
            record["linguistic_review"] = dict(approved_review)
            record["technical_review"] = dict(approved_review)
            record["automated_commands"] = [
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            ]

            with self.assertRaisesRegex(
                parity_review.ParityError, "canonical source audit"
            ):
                parity_review.validate_manifest(payload, root)

            payload["sources"][0]["audit"] = "approved"
            record["automated_commands"] = []
            with self.assertRaisesRegex(
                parity_review.ParityError, "automated evidence"
            ):
                parity_review.validate_manifest(payload, root)

            record["automated_commands"] = [
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            ]
            parity_review.validate_manifest(payload, root)

    def test_accepted_record_rejects_each_incomplete_or_false_evidence_field(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            baseline = manifest_fixture(root)
            record = baseline["records"][0]
            baseline["sources"][0]["audit"] = "approved"
            record["status"] = "accepted"
            record["contract"] = {
                dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
            }
            approved_review = {
                "result": "approved",
                "role": "reviewer",
                "review_date": "2026-07-13",
                "notes": "current human evidence",
            }
            record["linguistic_review"] = dict(approved_review)
            record["technical_review"] = dict(approved_review)
            record["automated_commands"] = [
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            ]
            exception_dimension = parity_review.CONTRACT_DIMENSIONS[0]
            record["contract"][exception_dimension] = "exception"
            record["exceptions"] = [
                {
                    "dimension": exception_dimension,
                    "justification": "reviewed equivalent",
                    "linguistic_approved": True,
                    "technical_approved": True,
                }
            ]
            parity_review.validate_manifest(baseline, root)

            def missing_dimension(payload: dict) -> None:
                payload["records"][0]["contract"].pop(exception_dimension)

            def false_string_approval(payload: dict) -> None:
                payload["records"][0]["exceptions"][0]["linguistic_approved"] = "false"

            def missing_dual_approval(payload: dict) -> None:
                payload["records"][0]["exceptions"][0]["technical_approved"] = False

            def invalid_exception_dimension(payload: dict) -> None:
                payload["records"][0]["exceptions"][0]["dimension"] = "not-a-dimension"

            def extra_exception_key(payload: dict) -> None:
                payload["records"][0]["exceptions"][0]["approved_by"] = "nobody"

            def missing_role(payload: dict) -> None:
                payload["records"][0]["linguistic_review"]["role"] = ""

            def missing_date(payload: dict) -> None:
                payload["records"][0]["technical_review"]["review_date"] = ""

            def stale_localized_digest(payload: dict) -> None:
                payload["records"][0]["localized_sha256"] = "0" * 64

            def stale_canonical_digest(payload: dict) -> None:
                payload["records"][0]["canonical_sha256"] = "0" * 64

            def missing_required_command(payload: dict) -> None:
                payload["records"][0]["automated_commands"].pop()

            cases = {
                "dimension": (missing_dimension, "incomplete parity contract"),
                "false-string-approval": (false_string_approval, "unapproved parity exception"),
                "dual-approval": (missing_dual_approval, "unapproved parity exception"),
                "exception-dimension": (invalid_exception_dimension, "malformed parity exception"),
                "exception-keys": (extra_exception_key, "malformed parity exception"),
                "role": (missing_role, "human approvals"),
                "date": (missing_date, "human approvals"),
                "localized-digest": (stale_localized_digest, "localized record is stale"),
                "canonical-digest": (stale_canonical_digest, "canonical digest mismatch"),
                "automated-command": (missing_required_command, "automated evidence"),
            }
            for label, (mutate, message) in cases.items():
                with self.subTest(label=label):
                    payload = copy.deepcopy(baseline)
                    mutate(payload)
                    with self.assertRaisesRegex(parity_review.ParityError, message):
                        parity_review.validate_manifest(payload, root)

    def test_manifest_rejects_a_silently_omitted_published_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            payload["sources"].pop()
            with self.assertRaisesRegex(parity_review.ParityError, "exactly 27"):
                parity_review.validate_manifest(payload, root)

    def test_contract_has_twelve_semantic_dimensions(self) -> None:
        self.assertEqual(12, len(parity_review.CONTRACT_DIMENSIONS))
        self.assertEqual(len(set(parity_review.CONTRACT_DIMENSIONS)), len(parity_review.CONTRACT_DIMENSIONS))

    def test_legacy_discovery_fixture_covers_twenty_five_chapters_and_two_appendices(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-test-") as temp:
            root = Path(temp)
            for number in range(1, 26):
                (root / f"chapter-{number:02d}-lesson").mkdir()
            (root / "appendix-cli-parser").mkdir()
            (root / "appendix-algorithms").mkdir()
            (root / "draft-chapter").mkdir()
            (root / "notes").mkdir()

            units = parity_review.scoped_units(
                root, {"unit_prefixes": ["chapter-", "appendix-"]}
            )

            self.assertEqual(27, len(units))
            self.assertIn("chapter-23-lesson", {path.name for path in units})
            self.assertIn("chapter-25-lesson", {path.name for path in units})

    def test_partition_loader_round_trips_and_rejects_topology_drift(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            payload["records"][0]["linguistic_review"]["notes"] = "مراجعة معلّقة"
            path, _ = migrate_fixture(root, payload)

            with expected_units_fixture() as units:
                self.assertEqual(payload, parity_review.load_manifest(path, root, units))
            real_rglob = Path.rglob

            def reversed_rglob(candidate: Path, pattern: str):
                return iter(reversed(list(real_rglob(candidate, pattern))))

            with expected_units_fixture(), patch.object(
                Path, "rglob", new=reversed_rglob
            ):
                shuffled = parity_review.load_manifest(path, root)
            self.assertEqual(
                parity_review.canonical_json_bytes(payload),
                parity_review.canonical_json_bytes(shuffled),
            )
            self.assertEqual(
                parity_review.LEGACY_TOPOLOGY_CANONICAL_SOURCES,
                len(list((root / "tools/parity/sources").glob("*.json"))),
            )
            self.assertEqual(
                parity_review.LEGACY_TOPOLOGY_CANONICAL_SOURCES
                * len(parity_review.LOCALES),
                len(list((root / "tools/parity/records").glob("*/*.json"))),
            )

            secret_name = "github_pat_DO_NOT_ECHO.json"
            extra = root / "tools/parity" / secret_name
            extra.write_text("{}\n", encoding="utf-8")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "extra evidence"
            ) as raised:
                parity_review.load_manifest(path, root)
            self.assertNotIn(secret_name, str(raised.exception))
            extra.unlink()

            missing = root / "tools/parity/records" / published_unit_names()[0] / "es.json"
            saved = missing.read_bytes()
            missing.unlink()
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "missing evidence"
            ):
                parity_review.load_manifest(path, root)
            missing.write_bytes(saved)
            with expected_units_fixture():
                self.assertEqual(payload, parity_review.load_manifest(path, root))

            missing.write_text("{malformed\n", encoding="utf-8")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "malformed localized record leaf"
            ):
                parity_review.load_manifest(path, root)
            missing.write_bytes(saved)

    def test_partition_loader_rejects_unsafe_index_and_leaf_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path, _ = migrate_fixture(root, payload)
            index_bytes = path.read_bytes()
            index = json.loads(index_bytes)
            index["store_root"] = "../outside"
            path.write_bytes(parity_review.canonical_json_bytes(index))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "store_root"
            ):
                parity_review.load_manifest(path, root)
            path.write_bytes(index_bytes)

            leaf = (
                root
                / "tools/parity/records"
                / published_unit_names()[0]
                / "es.json"
            )
            leaf_bytes = leaf.read_bytes()
            malformed = json.loads(leaf_bytes)
            malformed["record"]["locale"] = "ca"
            leaf.write_bytes(parity_review.canonical_json_bytes(malformed))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "identity mismatch"
            ):
                parity_review.load_manifest(path, root)
            leaf.write_bytes(leaf_bytes)

            index = json.loads(index_bytes)
            index["units"][1] = index["units"][0]
            path.write_bytes(parity_review.canonical_json_bytes(index))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "unique"
            ):
                parity_review.load_manifest(path, root)
            path.write_bytes(index_bytes)

            localized = root / payload["records"][0]["path"]
            localized_bytes = localized.read_bytes()
            localized.write_text("# Changed after evidence\n", encoding="utf-8")
            with expected_units_fixture():
                stale = parity_review.load_manifest(path, root)
            with self.assertRaisesRegex(parity_review.ParityError, "localized record is stale"):
                parity_review.validate_manifest(stale, root)
            localized.write_bytes(localized_bytes)

            outside = root.parent / f"{root.name}-outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            leaf.unlink()
            try:
                leaf.symlink_to(outside)
            except OSError:
                outside.unlink(missing_ok=True)
                self.skipTest("symlinks are unavailable on this platform")
            try:
                with expected_units_fixture(), self.assertRaisesRegex(
                    parity_review.ParityError, "contains symlink"
                ):
                    parity_review.load_manifest(path, root)
            finally:
                leaf.unlink(missing_ok=True)
                leaf.write_bytes(leaf_bytes)
                outside.unlink(missing_ok=True)

    def test_partition_writer_is_local_deterministic_and_recovers(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path, _ = migrate_fixture(root, payload)
            with expected_units_fixture():
                aggregate, baseline = parity_review.snapshot_manifest(path, root)
            record = aggregate["records"][0]
            record["observed_gaps"].append("review this localized edge")
            target = (
                root
                / "tools/parity/records"
                / record["unit"]
                / f"{record['locale']}.json"
            )
            target_before = target.read_bytes()

            with expected_units_fixture(), patch.object(
                parity_review,
                "atomic_compare_exchange",
                side_effect=OSError("exchange failed"),
            ), self.assertRaises(OSError):
                parity_review.write_manifest(path, aggregate, root, baseline)
            self.assertEqual(target_before, target.read_bytes())
            self.assertEqual([], list(target.parent.glob(f".{target.name}.*.tmp")))

            with expected_units_fixture():
                changed = parity_review.write_manifest(path, aggregate, root, baseline)
                _, unchanged_baseline = parity_review.snapshot_manifest(path, root)
                unchanged = parity_review.write_manifest(
                    path, aggregate, root, unchanged_baseline
                )
            self.assertEqual([target.relative_to(root).as_posix()], changed)
            self.assertEqual([], unchanged)

            with expected_units_fixture():
                aggregate, promotion_baseline = parity_review.snapshot_manifest(path, root)
            for promoted in aggregate["records"][:2]:
                promoted["status"] = "drafted"
                promoted["automated_commands"] = []
            self.assertEqual(2, parity_review.record_automated_results(aggregate, []))
            with expected_units_fixture():
                promoted_changed = parity_review.write_manifest(
                    path, aggregate, root, promotion_baseline
                )
            self.assertEqual(
                sorted(
                    f"tools/parity/records/{record['unit']}/{record['locale']}.json"
                    for record in aggregate["records"][:2]
                ),
                promoted_changed,
            )

    def test_atomic_write_portable_fallback_is_cooperative_and_no_clobber(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-atomic-test-") as temp:
            root = Path(temp)
            existing = root / "existing.json"
            existing.write_bytes(b"old\n")
            created = root / "created.json"
            self.assertEqual(
                parity_review.cooperative_lock_path(existing),
                parity_review.cooperative_lock_path(existing),
            )
            self.assertNotEqual(
                parity_review.cooperative_lock_path(existing),
                parity_review.cooperative_lock_path(created),
            )

            with patch.object(parity_review.sys, "platform", "darwin"):
                self.assertTrue(
                    parity_review.atomic_write(
                        existing, b"new\n", expected=b"old\n"
                    )
                )
                self.assertTrue(
                    parity_review.atomic_write(created, b"created\n", expected=None)
                )
                existing.write_bytes(b"external\n")
                with self.assertRaisesRegex(
                    parity_review.ParityError, "concurrent evidence change"
                ):
                    parity_review.atomic_write(
                        existing, b"other\n", expected=b"new\n"
                    )
            self.assertEqual(b"external\n", existing.read_bytes())
            self.assertEqual(b"created\n", created.read_bytes())
            self.assertEqual([], list(root.glob(".*.tmp")))

            symlinked_target = root / "symlink-lock-target.json"
            symlinked_target.write_bytes(b"old\n")
            victim = root / "victim.txt"
            victim.write_bytes(b"do not write\n")
            lock_path = parity_review.cooperative_lock_path(symlinked_target)
            lock_path.unlink(missing_ok=True)
            lock_path.symlink_to(victim)
            try:
                with patch.object(parity_review.sys, "platform", "darwin"), self.assertRaisesRegex(
                    parity_review.ParityError, "unsafe or unavailable cooperative parity lock"
                ):
                    parity_review.atomic_write(
                        symlinked_target, b"new\n", expected=b"old\n"
                    )
            finally:
                lock_path.unlink(missing_ok=True)
            self.assertEqual(b"old\n", symlinked_target.read_bytes())
            self.assertEqual(b"do not write\n", victim.read_bytes())

    def test_partition_writer_merges_disjoint_leaves_and_rejects_same_leaf_races(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            with expected_units_fixture():
                aggregate_a, baseline_a = parity_review.snapshot_manifest(path, root)
                aggregate_b, baseline_b = parity_review.snapshot_manifest(path, root)
            aggregate_a = copy.deepcopy(aggregate_a)
            aggregate_b = copy.deepcopy(aggregate_b)
            aggregate_a["records"][0]["linguistic_review"]["notes"] = "reviewer A: es"
            aggregate_b["records"][1]["linguistic_review"]["notes"] = "reviewer B: ca"

            with expected_units_fixture():
                changed_b = parity_review.write_manifest(
                    path, aggregate_b, root, baseline_b
                )
                changed_a = parity_review.write_manifest(
                    path, aggregate_a, root, baseline_a
                )
                merged, _ = parity_review.snapshot_manifest(path, root)
            self.assertEqual(1, len(changed_a))
            self.assertEqual(1, len(changed_b))
            self.assertEqual(
                ["reviewer A: es", "reviewer B: ca"],
                [
                    merged["records"][0]["linguistic_review"]["notes"],
                    merged["records"][1]["linguistic_review"]["notes"],
                ],
            )

            with expected_units_fixture():
                aggregate_c, baseline_c = parity_review.snapshot_manifest(path, root)
                aggregate_d, baseline_d = parity_review.snapshot_manifest(path, root)
            aggregate_c = copy.deepcopy(aggregate_c)
            aggregate_d = copy.deepcopy(aggregate_d)
            aggregate_c["records"][0]["technical_review"]["notes"] = "reviewer C"
            aggregate_d["records"][0]["technical_review"]["notes"] = "reviewer D"
            with expected_units_fixture():
                parity_review.write_manifest(path, aggregate_c, root, baseline_c)
                with self.assertRaisesRegex(
                    parity_review.ParityError, "concurrent evidence change"
                ):
                    parity_review.write_manifest(path, aggregate_d, root, baseline_d)
                preserved = parity_review.load_manifest(path, root)
            self.assertEqual(
                "reviewer C",
                preserved["records"][0]["technical_review"]["notes"],
            )

            with expected_units_fixture():
                aggregate_e, baseline_e = parity_review.snapshot_manifest(path, root)
            aggregate_e = copy.deepcopy(aggregate_e)
            aggregate_e["records"][2]["technical_review"]["notes"] = "reviewer E"
            record_e = aggregate_e["records"][2]
            leaf_e = (
                root
                / "tools/parity/records"
                / record_e["unit"]
                / f"{record_e['locale']}.json"
            )
            real_renameat2 = parity_review.linux_renameat2
            injected = False

            def edit_leaf_during_exchange(source: Path, target: Path, flags: int):
                nonlocal injected
                if (
                    target == leaf_e
                    and flags == parity_review.RENAME_EXCHANGE
                    and not injected
                ):
                    injected = True
                    concurrent = json.loads(leaf_e.read_bytes())
                    concurrent["record"]["technical_review"]["notes"] = "reviewer F"
                    leaf_e.write_bytes(parity_review.canonical_json_bytes(concurrent))
                return real_renameat2(source, target, flags)

            with expected_units_fixture(), patch.object(
                parity_review,
                "linux_renameat2",
                side_effect=edit_leaf_during_exchange,
            ), self.assertRaisesRegex(
                parity_review.ParityError, "concurrent evidence change"
            ):
                parity_review.write_manifest(path, aggregate_e, root, baseline_e)
            self.assertTrue(injected)
            with expected_units_fixture():
                preserved_external = parity_review.load_manifest(path, root)
            self.assertEqual(
                "reviewer F",
                preserved_external["records"][2]["technical_review"]["notes"],
            )

    def test_migration_interruption_keeps_legacy_authoritative_and_retries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            real_atomic_write = parity_review.atomic_write

            def fail_index(target: Path, data: bytes, **kwargs):
                if target == path:
                    raise OSError("index publication failed")
                return real_atomic_write(target, data, **kwargs)

            with expected_units_fixture(), patch.object(
                parity_review, "atomic_write", side_effect=fail_index
            ), self.assertRaises(OSError):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertTrue((root / "tools/parity").is_dir())

            with expected_units_fixture():
                parity_review.migrate_partitioned(path, root)
                self.assertEqual(payload, parity_review.load_manifest(path, root))

    def test_migration_cas_preserves_a_concurrent_monolith_edit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            real_renameat2 = parity_review.linux_renameat2
            concurrent_note = "human evidence added during migration"
            injected = False

            def edit_during_exchange(source: Path, target: Path, flags: int):
                nonlocal injected
                if (
                    target == path
                    and flags == parity_review.RENAME_EXCHANGE
                    and not injected
                ):
                    injected = True
                    concurrent = json.loads(path.read_bytes())
                    concurrent["records"][0]["linguistic_review"]["notes"] = concurrent_note
                    path.write_bytes(parity_review.canonical_json_bytes(concurrent))
                return real_renameat2(source, target, flags)

            with expected_units_fixture(), patch.object(
                parity_review, "linux_renameat2", side_effect=edit_during_exchange
            ), self.assertRaisesRegex(
                parity_review.ParityError, "concurrent evidence change"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertTrue(injected)
            preserved = json.loads(path.read_bytes())
            self.assertEqual(
                parity_review.LEGACY_SCHEMA_VERSION,
                preserved["schema_version"],
            )
            self.assertEqual(
                concurrent_note,
                preserved["records"][0]["linguistic_review"]["notes"],
            )
            self.assertTrue((root / "tools/parity").is_dir())
            self.assertFalse((root / "tools/.parity.staging").exists())

    def test_migration_rejects_invalid_or_conflicting_input_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path, _ = migrate_fixture(root, payload)
            before = file_snapshot(root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "requires a schema-v1 manifest"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(before, file_snapshot(root))

        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            localized = root / payload["records"][0]["path"]
            localized.write_text("# stale localized input\n", encoding="utf-8")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "localized record is stale"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertFalse((root / "tools/parity").exists())

        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            store = root / "tools/parity"
            with expected_units_fixture() as units:
                parity_review.write_partition_store(store, payload, units)
            leaf = store / "records" / published_unit_names()[0] / "es.json"
            conflicting = json.loads(leaf.read_bytes())
            conflicting["record"]["observed_gaps"].append("conflicting retry evidence")
            leaf.write_bytes(parity_review.canonical_json_bytes(conflicting))
            conflicting_bytes = leaf.read_bytes()
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "existing partition store conflicts"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertEqual(conflicting_bytes, leaf.read_bytes())

    def test_migration_serialization_failure_cleans_only_its_staging(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            real_atomic_write = parity_review.atomic_write

            def fail_staging(target: Path, data: bytes, **kwargs):
                if ".parity.staging" in target.parts:
                    raise OSError("serialization failed")
                return real_atomic_write(target, data, **kwargs)

            with expected_units_fixture(), patch.object(
                parity_review, "atomic_write", side_effect=fail_staging
            ), self.assertRaisesRegex(OSError, "serialization failed"):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertFalse((root / "tools/.parity.staging").exists())
            self.assertFalse((root / "tools/parity").exists())

    def test_migration_late_staging_failure_leaves_no_partial_store_and_retries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            real_atomic_write = parity_review.atomic_write
            staging_writes = 0

            def fail_tenth_staging_write(target: Path, data: bytes, **kwargs):
                nonlocal staging_writes
                if ".parity.staging" in target.parts:
                    staging_writes += 1
                    if staging_writes == 10:
                        raise OSError("late staging write failed")
                return real_atomic_write(target, data, **kwargs)

            with expected_units_fixture(), patch.object(
                parity_review,
                "atomic_write",
                side_effect=fail_tenth_staging_write,
            ), self.assertRaisesRegex(OSError, "late staging write failed"):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(10, staging_writes)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertFalse((root / "tools/.parity.staging").exists())
            self.assertFalse((root / "tools/parity").exists())

            with expected_units_fixture():
                parity_review.migrate_partitioned(path, root)
                self.assertEqual(payload, parity_review.load_manifest(path, root))

    def test_migration_publish_race_preserves_the_competing_store(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            real_publish = parity_review.publish_directory_noreplace

            def race_publish(source: Path, target: Path):
                target.mkdir()
                (target / "user-evidence.txt").write_text(
                    "do not replace\n", encoding="utf-8"
                )
                return real_publish(source, target)

            with expected_units_fixture(), patch.object(
                parity_review,
                "publish_directory_noreplace",
                side_effect=race_publish,
            ), self.assertRaisesRegex(
                parity_review.ParityError, "store appeared during migration"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertEqual(
                "do not replace\n",
                (root / "tools/parity/user-evidence.txt").read_text(encoding="utf-8"),
            )
            self.assertFalse((root / "tools/.parity.staging").exists())

    def test_migration_refuses_preexisting_staging_without_deleting_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            staging = root / "tools/.parity.staging"
            staging.mkdir()
            user_file = staging / "user-evidence.txt"
            user_file.write_text("do not delete\n", encoding="utf-8")

            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "staging path already exists"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertEqual("do not delete\n", user_file.read_text(encoding="utf-8"))

    def test_migration_staging_acquisition_race_is_non_destructive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            staging = root / "tools/.parity.staging"
            real_mkdir = Path.mkdir
            raced = False

            def racing_mkdir(candidate: Path, *args, **kwargs):
                nonlocal raced
                if candidate == staging and not raced:
                    raced = True
                    real_mkdir(candidate, *args, **kwargs)
                    (candidate / "user-evidence.txt").write_text(
                        "do not delete\n", encoding="utf-8"
                    )
                    raise FileExistsError(str(candidate))
                return real_mkdir(candidate, *args, **kwargs)

            with expected_units_fixture(), patch.object(
                Path, "mkdir", new=racing_mkdir
            ), self.assertRaisesRegex(
                parity_review.ParityError, "staging path already exists"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertEqual(
                "do not delete\n",
                (staging / "user-evidence.txt").read_text(encoding="utf-8"),
            )

    def test_migration_refuses_broken_store_symlink_without_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = write_legacy_manifest(root, payload)
            legacy_bytes = path.read_bytes()
            store = root / "tools/parity"
            store.symlink_to(
                root.parent / f"{root.name}-missing-external-target",
                target_is_directory=True,
            )

            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "store is missing or unsafe"
            ):
                parity_review.migrate_partitioned(path, root)
            self.assertEqual(legacy_bytes, path.read_bytes())
            self.assertTrue(store.is_symlink())

    def test_partition_loader_rejects_store_symlink_even_when_target_is_internal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            store = root / "tools/parity"
            real_store = root / "tools/parity-real"
            store.rename(real_store)
            store.symlink_to(real_store, target_is_directory=True)

            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "store is missing or unsafe"
            ):
                parity_review.load_manifest(path, root)

    def test_malformed_legacy_object_has_stable_cli_failure(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            payload["sources"][0] = None
            write_legacy_manifest(root, payload)
            output = io.StringIO()
            fake_module = root / "tools/parity_review.py"

            with expected_units_fixture(), patch.object(
                parity_review, "__file__", str(fake_module)
            ), contextlib.redirect_stdout(output):
                result = parity_review.main(["--migrate-partitioned"])
            self.assertEqual(1, result)
            self.assertIn("canonical sources must be JSON objects", output.getvalue())
            self.assertFalse((root / "tools/parity").exists())

            secret_name = "github_pat_DO_NOT_ECHO.json"
            secret_path = root / "tools" / secret_name
            secret_path.write_text("{malformed\n", encoding="utf-8")
            secret_output = io.StringIO()
            with patch.object(
                parity_review, "__file__", str(fake_module)
            ), contextlib.redirect_stdout(secret_output):
                secret_result = parity_review.main(
                    ["--manifest", f"tools/{secret_name}"]
                )
            self.assertEqual(1, secret_result)
            self.assertIn("<custom-manifest>", secret_output.getvalue())
            self.assertNotIn(secret_name, secret_output.getvalue())

    def test_export_monolith_is_byte_exact_safe_and_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            payload["records"][0]["linguistic_review"]["notes"] = "مراجعة معلّقة"
            path, original = migrate_fixture(root, payload)
            before = file_snapshot(root)
            output = root / "tools/parity-export.json"
            with expected_units_fixture(), patch.object(
                parity_review,
                "atomic_compare_exchange",
                side_effect=OSError("exchange failed"),
            ), self.assertRaisesRegex(OSError, "exchange failed"):
                parity_review.export_monolith(path, output, root)
            self.assertFalse(output.exists())
            self.assertEqual([], list(output.parent.glob(f".{output.name}.*.tmp")))
            self.assertEqual(before, file_snapshot(root))

            with expected_units_fixture():
                parity_review.export_monolith(path, output, root)
            self.assertEqual(original, output.read_bytes())
            after = file_snapshot(root)
            self.assertEqual(
                {key: value for key, value in before.items()},
                {key: value for key, value in after.items() if key != "tools/parity-export.json"},
            )

            with expected_units_fixture():
                parity_review.export_monolith(path, output, root)
            output.write_text("{}\n", encoding="utf-8")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "conflicting output"
            ):
                parity_review.export_monolith(path, output, root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "escapes repository"
            ):
                parity_review.export_monolith(path, root.parent / "outside.json", root)

    def test_digest_refresh_writes_only_bound_partition_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            for record in payload["records"]:
                record["status"] = "automated-signals-pass"
                record["automated_commands"] = [
                    "python -B tools/validate_book.py",
                    "python -B tools/parity_review.py",
                ]
            target_unit = published_unit_names()[0]
            payload["sources"][0]["audit"] = "approved"
            path, _ = migrate_fixture(root, payload)
            units = [root / unit for unit in published_unit_names()]
            localized = root / target_unit / parity_review.LOCALES["es"]
            localized.write_text("# Unit\n\nlocalized change\n", encoding="utf-8")

            with (
                expected_units_fixture(),
                patch.object(parity_review.validate_book, "load_config", return_value={}),
                patch.object(parity_review, "scoped_units", return_value=units),
                patch.object(parity_review, "signals", side_effect=synthetic_signals),
            ):
                previous, baseline = parity_review.snapshot_manifest(path, root)
                refreshed = parity_review.build_manifest(
                    root, previous_payload=previous
                )
                localized_changed = parity_review.write_manifest(
                    path, refreshed, root, baseline
                )
            self.assertEqual(
                [f"tools/parity/records/{target_unit}/es.json"], localized_changed
            )
            self.assertEqual("drafted", refreshed["records"][0]["status"])

            canonical = root / target_unit / "README.md"
            canonical.write_text("# Unit\n\ncanonical change\n", encoding="utf-8")
            with (
                expected_units_fixture(),
                patch.object(parity_review.validate_book, "load_config", return_value={}),
                patch.object(parity_review, "scoped_units", return_value=units),
                patch.object(parity_review, "signals", side_effect=synthetic_signals),
            ):
                previous, baseline = parity_review.snapshot_manifest(path, root)
                refreshed = parity_review.build_manifest(
                    root, previous_payload=previous
                )
                self.assertEqual(4, parity_review.reconcile_draft_records(refreshed))
                canonical_changed = parity_review.write_manifest(
                    path, refreshed, root, baseline
                )
            self.assertEqual(
                sorted(
                    [f"tools/parity/sources/{target_unit}.json"]
                    + [
                        f"tools/parity/records/{target_unit}/{locale}.json"
                        for locale in parity_review.LOCALES
                    ]
                ),
                canonical_changed,
            )
            self.assertEqual("pending-human-review", refreshed["sources"][0]["audit"])

    def test_storage_round_trip_preserves_human_evidence_without_promotion(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-partition-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            record = payload["records"][0]
            record["status"] = "technical-reviewed"
            record["contract"] = {
                dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
            }
            record["linguistic_review"] = {
                "result": "approved",
                "role": "fluent reviewer",
                "review_date": "2026-07-13",
                "notes": "genuine supplied evidence",
            }
            record["technical_review"] = {
                "result": "approved",
                "role": "technical reviewer",
                "review_date": "2026-07-13",
                "notes": "genuine supplied evidence",
            }
            path, original = migrate_fixture(root, payload)
            output = root / "tools/human-evidence-export.json"
            with expected_units_fixture():
                loaded = parity_review.load_manifest(path, root)
                parity_review.export_monolith(path, output, root)
            self.assertEqual(payload, loaded)
            self.assertEqual(original, output.read_bytes())
            with self.assertRaisesRegex(parity_review.ParityError, "publication review incomplete"):
                parity_review.validate_manifest(loaded, root, require_accepted=True)

    def test_gap_signals_are_triage_not_acceptance(self) -> None:
        canonical = {
            "words": 100,
            "headings": 10,
            "source_refs": 2,
            "fence_sequence_sha256": "canonical",
        }
        localized = {
            "words": 20,
            "headings": 3,
            "source_refs": 0,
            "fence_sequence_sha256": "localized",
        }
        gaps = parity_review.gap_signals(canonical, localized)
        self.assertEqual(4, len(gaps))
        self.assertTrue(all("accepted" not in gap for gap in gaps))

    def test_automated_promotion_never_claims_human_acceptance(self) -> None:
        payload = {
            "sources": [
                {"unit": "ok"},
                {"unit": "blocked"},
                {"unit": "human"},
            ],
            "records": [
                {"unit": "ok", "path": "ok/README.es.md", "status": "drafted", "automated_commands": []},
                {"unit": "blocked", "path": "blocked/README.es.md", "status": "drafted", "automated_commands": []},
                {"unit": "human", "path": "human/README.es.md", "status": "linguistic-reviewed", "automated_commands": []},
            ]
        }
        diagnostics = [
            parity_review.validate_book.Diagnostic("rule", "blocked/README.es.md", "bad", "fix")
        ]
        self.assertEqual(1, parity_review.record_automated_results(payload, diagnostics))
        self.assertEqual("automated-signals-pass", payload["records"][0]["status"])
        self.assertEqual("drafted", payload["records"][1]["status"])
        self.assertEqual("linguistic-reviewed", payload["records"][2]["status"])

    def test_automated_promotion_fails_closed_for_canonical_and_global_errors(self) -> None:
        def payload() -> dict:
            return {
                "sources": [{"unit": "a"}, {"unit": "b"}],
                "records": [
                    {"unit": "a", "path": "a/README.es.md", "status": "drafted", "automated_commands": []},
                    {"unit": "a", "path": "a/README.ca.md", "status": "drafted", "automated_commands": []},
                    {"unit": "b", "path": "b/README.es.md", "status": "drafted", "automated_commands": []},
                ],
            }

        canonical = payload()
        canonical_diagnostics = [
            parity_review.validate_book.Diagnostic("rule", "a/README.md", "bad", "fix")
        ]
        self.assertEqual(
            1,
            parity_review.record_automated_results(canonical, canonical_diagnostics),
        )
        self.assertEqual(
            ["drafted", "drafted", "automated-signals-pass"],
            [record["status"] for record in canonical["records"]],
        )

        global_failure = payload()
        global_diagnostics = [
            parity_review.validate_book.Diagnostic("rule", ".", "shared gate failed", "fix")
        ]
        self.assertEqual(
            0,
            parity_review.record_automated_results(global_failure, global_diagnostics),
        )
        self.assertEqual(
            ["drafted", "drafted", "drafted"],
            [record["status"] for record in global_failure["records"]],
        )

    def test_automated_gate_uses_effective_baseline_failures(self) -> None:
        legacy = parity_review.validate_book.Diagnostic(
            "legacy", "chapter/README.md", "reviewed", "keep reviewed"
        )
        config = {"baseline": "tools/book_quality_baseline.json"}
        with (
            patch.object(
                parity_review.validate_book,
                "collect_diagnostics",
                return_value=[legacy],
            ),
            patch.object(
                parity_review.validate_book,
                "apply_baseline",
                return_value=([], []),
            ),
        ):
            self.assertEqual(
                [], parity_review.automated_gate_diagnostics(Path("."), config)
            )

        with (
            patch.object(
                parity_review.validate_book,
                "collect_diagnostics",
                return_value=[legacy],
            ),
            patch.object(
                parity_review.validate_book,
                "apply_baseline",
                return_value=([], ["stale-fingerprint"]),
            ),
        ):
            diagnostics = parity_review.automated_gate_diagnostics(
                Path("."), config
            )
        self.assertEqual(["baseline.stale"], [item.rule_id for item in diagnostics])

    def test_reconcile_drafts_is_explicit_destructive_and_never_accepts(self) -> None:
        approved_review = {
            "result": "approved",
            "role": "reviewer",
            "review_date": "2026-07-13",
            "notes": "evidence for an obsolete digest",
        }
        payload = {
            "records": [
                {
                    "status": "stale",
                    "contract": {
                        dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
                    },
                    "exceptions": [{"obsolete": True}],
                    "automated_commands": ["old command"],
                    "linguistic_review": dict(approved_review),
                    "technical_review": dict(approved_review),
                },
                {
                    "status": "inventoried",
                    "contract": {
                        dimension: "pending" for dimension in parity_review.CONTRACT_DIMENSIONS
                    },
                    "exceptions": [],
                    "automated_commands": [],
                    "linguistic_review": parity_review.empty_review(),
                    "technical_review": parity_review.empty_review(),
                },
                {
                    "status": "accepted",
                    "contract": {
                        dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
                    },
                    "exceptions": [],
                    "automated_commands": ["current command"],
                    "linguistic_review": dict(approved_review),
                    "technical_review": dict(approved_review),
                },
            ]
        }
        accepted_before = dict(payload["records"][2])

        self.assertEqual(2, parity_review.reconcile_draft_records(payload))
        for record in payload["records"][:2]:
            self.assertEqual("drafted", record["status"])
            self.assertEqual({"pending"}, set(record["contract"].values()))
            self.assertEqual([], record["exceptions"])
            self.assertEqual([], record["automated_commands"])
            self.assertEqual(parity_review.empty_review(), record["linguistic_review"])
            self.assertEqual(parity_review.empty_review(), record["technical_review"])
        self.assertEqual(accepted_before, payload["records"][2])

    def test_reconcile_rejects_malformed_records_and_conflicting_actions(self) -> None:
        with self.assertRaisesRegex(parity_review.ParityError, "records must be a list"):
            parity_review.reconcile_draft_records({"records": {}})
        with self.assertRaisesRegex(parity_review.ParityError, "unknown review state"):
            parity_review.reconcile_draft_records({"records": [{"status": "mystery"}]})
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                parity_review.parse_args(["--reconcile-drafts", "--record-automated"])
        self.assertEqual(2, raised.exception.code)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                parity_review.parse_args(["--migrate-partitioned", "--write"])
        self.assertEqual(2, raised.exception.code)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                parity_review.parse_args(["--reconcile-topology", "--write"])
        self.assertEqual(2, raised.exception.code)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                parity_review.parse_args(["--export-monolith", "tools/out.json", "--write"])
        self.assertEqual(2, raised.exception.code)

    def test_review_schema_migration_maps_pending_gates_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            path = migrate_review_fixture(root, payload)
            with expected_units_fixture() as units:
                migrated = parity_review.load_manifest(path, root, units)
                parity_review.validate_manifest(migrated, root)
            self.assertEqual(parity_review.SCHEMA_VERSION, migrated["schema_version"])
            self.assertEqual(27, len(migrated["sources"]))
            self.assertEqual(108, len(migrated["records"]))
            self.assertEqual("pending", migrated["root_publication"]["state"])
            self.assertEqual(
                {"pending"},
                {
                    source["canonical_review"]["result"]
                    for source in migrated["sources"]
                },
            )
            for record in migrated["records"]:
                self.assertEqual("pending", record["rendered_accessibility_review"]["result"])
                self.assertEqual(record["locale"] == "ar", "bidi_review" in record)
            self.assertEqual(
                136,
                len(
                    [
                        candidate
                        for candidate in (root / "tools/parity").rglob("*.json")
                        if candidate.is_file()
                    ]
                ),
            )
            before = file_snapshot(root)
            with expected_units_fixture():
                self.assertEqual([], parity_review.migrate_review_schema(path, root))
            self.assertEqual(before, file_snapshot(root))

            bundle = root / "tools/review-bundle.json"
            with expected_units_fixture():
                parity_review.export_review_bundle(path, bundle, root)
                first = bundle.read_bytes()
                parity_review.export_review_bundle(path, bundle, root)
            self.assertEqual(first, bundle.read_bytes())
            exported = json.loads(first)
            self.assertEqual(27, len(exported["sources"]))
            self.assertEqual(108, len(exported["records"]))
            self.assertIn("root_publication", exported)
            bundle.write_bytes(b"conflicting output\n")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "refusing to replace conflicting output"
            ):
                parity_review.export_review_bundle(path, bundle, root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "must not replace live partition"
            ):
                parity_review.export_review_bundle(
                    path, root / "tools/parity/export.json", root
                )

            legacy_output = root / "tools/legacy.json"
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "cannot represent leaf schema 2"
            ):
                parity_review.export_monolith(path, legacy_output, root)
            self.assertFalse(legacy_output.exists())

    def test_topology_reconciliation_adds_pending_units_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-topology-v2-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            refresh_review_fixture(root, path)
            old_source = root / "tools/parity/sources/chapter-01-lesson.json"
            old_record = root / "tools/parity/records/chapter-01-lesson/es.json"
            old_source_bytes = old_source.read_bytes()
            old_record_bytes = old_record.read_bytes()
            current_units = add_topology_units(root)

            with patch.object(
                parity_review, "expected_unit_ids", return_value=current_units
            ), patch.object(
                parity_review.validate_book,
                "load_config",
                return_value=topology_config(root),
            ):
                changed = parity_review.reconcile_partition_topology(path, root)
                expanded = parity_review.load_manifest(
                    path, root, expected_units=current_units
                )
                self.assertEqual([], parity_review.reconcile_partition_topology(path, root))

            self.assertIn("tools/parity_manifest.json", changed)
            self.assertEqual(30, len(expanded["sources"]))
            self.assertEqual(120, len(expanded["records"]))
            self.assertEqual(old_source_bytes, old_source.read_bytes())
            self.assertEqual(old_record_bytes, old_record.read_bytes())
            new_units = set(current_units) - set(published_unit_names())
            new_sources = [
                source for source in expanded["sources"] if source["unit"] in new_units
            ]
            new_records = [
                record for record in expanded["records"] if record["unit"] in new_units
            ]
            self.assertEqual(3, len(new_sources))
            self.assertEqual(12, len(new_records))
            self.assertEqual(
                {"pending"},
                {
                    source["canonical_review"]["result"]
                    for source in new_sources
                },
            )
            self.assertEqual(
                {"inventoried"}, {record["status"] for record in new_records}
            )
            self.assertEqual(
                {"pending"},
                {
                    record[review]["result"]
                    for record in new_records
                    for review in (
                        "linguistic_review",
                        "technical_review",
                        "rendered_accessibility_review",
                    )
                },
            )

    def test_topology_reconciliation_reload_failure_rolls_back_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-topology-v2-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            refresh_review_fixture(root, path)
            current_units = add_topology_units(root)
            before = file_snapshot(root)

            with patch.object(
                parity_review, "expected_unit_ids", return_value=current_units
            ), patch.object(
                parity_review.validate_book,
                "load_config",
                return_value=topology_config(root),
            ), patch.object(
                parity_review,
                "load_manifest",
                side_effect=parity_review.ParityError(
                    "injected topology reload failure"
                ),
            ), self.assertRaisesRegex(
                parity_review.ParityError, "topology reload failure"
            ):
                parity_review.reconcile_partition_topology(path, root)

            self.assertEqual(before, file_snapshot(root))
            self.assertEqual(
                [], list((root / "tools").glob(".parity-topology-v2.*"))
            )

    def test_review_schema_migration_downgrades_legacy_acceptance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            record = payload["records"][0]
            source = next(
                item for item in payload["sources"] if item["unit"] == record["unit"]
            )
            source["audit"] = "approved"
            record["status"] = "accepted"
            record["contract"] = {
                dimension: "pass" for dimension in parity_review.CONTRACT_DIMENSIONS
            }
            approved = {
                "result": "approved",
                "role": "fixture reviewer",
                "review_date": "2026-07-15",
                "notes": "legacy fixture decision",
            }
            record["linguistic_review"] = dict(approved)
            record["technical_review"] = dict(approved)
            record["automated_commands"] = [
                "python -B tools/validate_book.py",
                "python -B tools/parity_review.py",
            ]
            incomplete = payload["records"][1]
            incomplete["status"] = "linguistic-reviewed"
            incomplete["linguistic_review"] = {
                "result": "approved",
                "role": "",
                "review_date": "",
                "notes": "",
            }
            path = migrate_review_fixture(root, payload)
            with expected_units_fixture():
                migrated = parity_review.load_manifest(path, root)
            mapped = next(
                item
                for item in migrated["records"]
                if item["unit"] == record["unit"] and item["locale"] == record["locale"]
            )
            mapped_source = next(
                item for item in migrated["sources"] if item["unit"] == record["unit"]
            )
            self.assertEqual("human-review-in-progress", mapped["status"])
            self.assertEqual("approved", mapped["linguistic_review"]["result"])
            self.assertEqual("approved", mapped["technical_review"]["result"])
            self.assertEqual("pending", mapped["rendered_accessibility_review"]["result"])
            self.assertEqual("pending", mapped_source["canonical_review"]["result"])
            mapped_incomplete = next(
                item
                for item in migrated["records"]
                if item["unit"] == incomplete["unit"]
                and item["locale"] == incomplete["locale"]
            )
            self.assertEqual("pending", mapped_incomplete["linguistic_review"]["result"])
            self.assertEqual("drafted", mapped_incomplete["status"])

    def test_review_schema_mixed_store_aborts_before_staging_without_writes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            leaf = sorted((root / "tools/parity/sources").glob("*.json"))[-1]
            mixed = json.loads(leaf.read_bytes())
            mixed["schema_version"] = parity_review.LEAF_SCHEMA_VERSION
            leaf.write_bytes(parity_review.canonical_json_bytes(mixed))
            before = file_snapshot(root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "mixes"
            ) as caught:
                parity_review.migrate_review_schema(path, root)
            self.assertIn(leaf.relative_to(root).as_posix(), str(caught.exception))
            self.assertEqual(before, file_snapshot(root))
            self.assertEqual([], list((root / "tools").glob(".parity-review-v2.*")))

            mixed["schema_version"] = parity_review.LEGACY_LEAF_SCHEMA_VERSION
            leaf.write_bytes(parity_review.canonical_json_bytes(mixed))
            root_leaf = root / "tools/parity/root-publication.json"
            root_leaf.write_bytes(parity_review.canonical_json_bytes({}))
            before_root_mismatch = file_snapshot(root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "root-publication.json is present"
            ):
                parity_review.migrate_review_schema(path, root)
            self.assertEqual(before_root_mismatch, file_snapshot(root))

    def test_review_schema_unavailable_exchange_preserves_v1_and_cleans_staging(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            before = file_snapshot(root)
            real_rename = parity_review.linux_renameat2

            def exchange_unavailable(source: Path, target: Path, flags: int):
                if flags == parity_review.RENAME_EXCHANGE:
                    raise OSError("RENAME_EXCHANGE unavailable")
                return real_rename(source, target, flags)

            with expected_units_fixture(), patch.object(
                parity_review,
                "linux_renameat2",
                side_effect=exchange_unavailable,
            ), self.assertRaisesRegex(OSError, "unavailable"):
                parity_review.migrate_review_schema(path, root)
            self.assertEqual(before, file_snapshot(root))
            self.assertEqual([], list((root / "tools").glob(".parity-review-v2.*")))

    def test_review_schema_exchange_race_restores_concurrent_human_edit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            target = next((root / "tools/parity/records").rglob("es.json"))
            real_rename = parity_review.linux_renameat2
            injected = False

            def edit_before_exchange(source: Path, destination: Path, flags: int):
                nonlocal injected
                if (
                    destination == root / "tools/parity"
                    and flags == parity_review.RENAME_EXCHANGE
                    and not injected
                ):
                    injected = True
                    leaf = json.loads(target.read_bytes())
                    leaf["record"]["linguistic_review"]["notes"] = (
                        "concurrent human evidence"
                    )
                    target.write_bytes(parity_review.canonical_json_bytes(leaf))
                    (destination / "concurrent-extra.txt").write_text(
                        "external edit\n", encoding="utf-8"
                    )
                    (destination / "concurrent-link").symlink_to(
                        root / "README.md"
                    )
                return real_rename(source, destination, flags)

            with expected_units_fixture(), patch.object(
                parity_review, "linux_renameat2", side_effect=edit_before_exchange
            ), self.assertRaisesRegex(
                parity_review.ParityError, "changed during atomic"
            ):
                parity_review.migrate_review_schema(path, root)
            self.assertTrue(injected)
            preserved = json.loads(target.read_bytes())
            self.assertEqual(
                "concurrent human evidence",
                preserved["record"]["linguistic_review"]["notes"],
            )
            self.assertEqual(
                parity_review.LEGACY_LEAF_SCHEMA_VERSION,
                preserved["schema_version"],
            )
            self.assertEqual(
                "external edit\n",
                (root / "tools/parity/concurrent-extra.txt").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertTrue((root / "tools/parity/concurrent-link").is_symlink())
            self.assertEqual([], list((root / "tools").glob(".parity-review-v2.*")))

    def test_review_schema_invalid_staging_never_replaces_live_store(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            before = file_snapshot(root)
            real_writer = parity_review.write_partition_store

            def corrupt_staging(store: Path, payload: dict, units: list[str], **kwargs):
                real_writer(store, payload, units, **kwargs)
                leaf = next((store / "sources").glob("*.json"))
                leaf.write_bytes(b"not-json\n")

            with expected_units_fixture(), patch.object(
                parity_review, "write_partition_store", side_effect=corrupt_staging
            ), self.assertRaisesRegex(parity_review.ParityError, "malformed"):
                parity_review.migrate_review_schema(path, root)
            self.assertEqual(before, file_snapshot(root))
            self.assertEqual([], list((root / "tools").glob(".parity-review-v2.*")))

    def test_review_schema_reload_failure_rolls_back_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            before = file_snapshot(root)
            real_loader = parity_review.load_partition_store

            def fail_published(*args, **kwargs):
                result = real_loader(*args, **kwargs)
                if (
                    kwargs.get("required_leaf_version")
                    == parity_review.LEAF_SCHEMA_VERSION
                    and kwargs.get("store_override") is None
                ):
                    raise parity_review.ParityError("injected post-exchange reload failure")
                return result

            with expected_units_fixture(), patch.object(
                parity_review, "load_partition_store", side_effect=fail_published
            ), self.assertRaisesRegex(
                parity_review.ParityError, "post-exchange reload failure"
            ):
                parity_review.migrate_review_schema(path, root)
            self.assertEqual(before, file_snapshot(root))
            self.assertEqual([], list((root / "tools").glob(".parity-review-v2.*")))

    def test_review_schema_failed_rollback_retains_relative_recovery_store(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path, _ = migrate_fixture(root, manifest_fixture(root))
            write_v2_support_files(root)
            real_loader = parity_review.load_partition_store
            real_rename = parity_review.linux_renameat2
            exchanges = 0

            def fail_published(*args, **kwargs):
                result = real_loader(*args, **kwargs)
                if (
                    kwargs.get("required_leaf_version")
                    == parity_review.LEAF_SCHEMA_VERSION
                    and kwargs.get("store_override") is None
                ):
                    raise parity_review.ParityError("injected reload failure")
                return result

            def fail_rollback(source: Path, target: Path, flags: int):
                nonlocal exchanges
                if flags == parity_review.RENAME_EXCHANGE:
                    exchanges += 1
                    if exchanges == 2:
                        raise OSError("injected rollback failure")
                return real_rename(source, target, flags)

            with expected_units_fixture(), patch.object(
                parity_review, "load_partition_store", side_effect=fail_published
            ), patch.object(
                parity_review, "linux_renameat2", side_effect=fail_rollback
            ), self.assertRaisesRegex(
                parity_review.AtomicRecoveryError,
                r"tools/\.parity-review-v2\.",
            ):
                parity_review.migrate_review_schema(path, root)
            recovery = list((root / "tools").glob(".parity-review-v2.*"))
            self.assertEqual(1, len(recovery))
            self.assertEqual(
                parity_review.LEGACY_LEAF_SCHEMA_VERSION,
                json.loads(next((recovery[0] / "sources").glob("*.json")).read_bytes())[
                    "schema_version"
                ],
            )
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.AtomicRecoveryError, "manual resolution"
            ):
                parity_review.migrate_review_schema(path, root)

    def test_review_schema_profile_change_invalidates_render_bindings(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            profile_path = root / parity_review.RENDER_PROFILE
            profile = json.loads(profile_path.read_bytes())
            profile["accessibility_checks"].append("new checked input")
            profile_path.write_bytes(parity_review.canonical_json_bytes(profile))
            with expected_units_fixture():
                payload = parity_review.load_manifest(path, root)
            with self.assertRaisesRegex(
                parity_review.ParityError, "stale canonical source rendered review"
            ):
                parity_review.validate_manifest(payload, root)

    def test_v2_intermediate_states_are_derived_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            with expected_units_fixture():
                payload = parity_review.load_manifest(path, root)

            record = payload["records"][0]
            record["status"] = "human-review-in-progress"
            with self.assertRaisesRegex(
                parity_review.ParityError, "claims absent human evidence"
            ):
                parity_review.validate_manifest(payload, root)

            record["status"] = "automated-signals-pass"
            record["linguistic_review"].update(
                {
                    "result": "changes-requested",
                    "role": "fixture reviewer",
                    "review_date": "2026-07-15",
                    "notes": "changes required",
                }
            )
            with self.assertRaisesRegex(
                parity_review.ParityError, "does not reflect requested changes"
            ):
                parity_review.validate_manifest(payload, root)

            record["linguistic_review"] = parity_review.pending_review(
                canonical_sha256=record["canonical_sha256"],
                localized_sha256=record["localized_sha256"],
            )
            record["status"] = "automated-signals-pass"
            payload["root_publication"]["state"] = "human-review-in-progress"
            with self.assertRaisesRegex(
                parity_review.ParityError, "root state claims absent human evidence"
            ):
                parity_review.validate_manifest(payload, root)

    def test_global_render_asset_change_resets_only_dependent_render_gates(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-render-refresh-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            with expected_units_fixture():
                aggregate, _baseline = parity_review.snapshot_manifest(path, root)
            approve_v2_payload(root, aggregate)
            parity_review.validate_manifest(aggregate, root, require_accepted=True)
            source = aggregate["sources"][0]
            rendered = source["rendered_accessibility_review"]
            profile = json.loads((root / parity_review.RENDER_PROFILE).read_bytes())
            expected_assets = [
                {
                    "path": relative,
                    "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(),
                }
                for relative in profile["global_assets"]
            ]
            self.assertEqual(
                independent_sha256(
                    {
                        "path": source["path"],
                        "page_sha256": source["sha256"],
                        "profile_sha256": rendered["profile_sha256"],
                        "assets": expected_assets,
                        "environment": rendered["environment"],
                    }
                ),
                rendered["render_input_sha256"],
            )
            (root / "icons/cc-by-sa.svg").write_text(
                "<svg><title>updated</title></svg>\n", encoding="utf-8"
            )
            units = [root / name for name in published_unit_names()]
            with (
                expected_units_fixture(),
                patch.object(parity_review.validate_book, "load_config", return_value={}),
                patch.object(parity_review, "scoped_units", return_value=units),
                patch.object(parity_review, "signals", side_effect=synthetic_signals),
            ):
                refreshed = parity_review.build_v2_manifest(root, aggregate)

            self.assertEqual(
                {"approved"},
                {
                    source["canonical_review"]["result"]
                    for source in refreshed["sources"]
                },
            )
            self.assertEqual(
                {"pending"},
                {
                    source["rendered_accessibility_review"]["result"]
                    for source in refreshed["sources"]
                },
            )
            for record in refreshed["records"]:
                self.assertEqual("approved", record["linguistic_review"]["result"])
                self.assertEqual("approved", record["technical_review"]["result"])
                self.assertEqual(
                    "pending", record["rendered_accessibility_review"]["result"]
                )
                if record["locale"] == "ar":
                    self.assertEqual("pending", record["bidi_review"]["result"])
                self.assertEqual("human-review-in-progress", record["status"])
            root_publication = refreshed["root_publication"]
            self.assertEqual("stale", root_publication["state"])
            self.assertEqual(
                {"pending"},
                {
                    page["rendered_accessibility_review"]["result"]
                    for page in root_publication["pages"]
                },
            )
            parity_review.validate_manifest(refreshed, root)

    def test_review_schema_require_accepted_fails_honestly_after_migration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-review-v2-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            with expected_units_fixture():
                payload = parity_review.load_manifest(path, root)
            with self.assertRaisesRegex(
                parity_review.ParityError, "publication review incomplete"
            ):
                parity_review.validate_manifest(payload, root, require_accepted=True)

    def test_unit_and_root_review_packets_are_canonical_read_only_projections(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-packet-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            unit = published_unit_names()[0]
            before = file_snapshot(root)
            with expected_units_fixture():
                packet = parity_review.build_unit_review_packet(root, unit)
                repeated = parity_review.build_unit_review_packet(root, unit)
                root_packet = parity_review.build_root_review_packet(root)
            self.assertEqual(before, file_snapshot(root))
            self.assertEqual(
                parity_review.canonical_json_bytes(packet),
                parity_review.canonical_json_bytes(repeated),
            )
            self.assertEqual("unit-review", packet["packet_kind"])
            self.assertNotIn("schema_version", packet)
            self.assertEqual(
                list(parity_review.LOCALES),
                [item["value"]["locale"] for item in packet["localized_records"]],
            )
            self.assertEqual(16, len(root_packet["decisions"]))
            self.assertEqual(
                16,
                len({item["decision_id"] for item in root_packet["decisions"]}),
            )
            self.assertEqual(
                list(parity_review.ROOT_PATHS),
                [
                    item["path"]
                    for item in root_packet["root_publication"]["value"]["pages"]
                ],
            )
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "unknown review packet unit"
            ):
                parity_review.build_unit_review_packet(root, "chapter-99-missing")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "unsafe review packet unit"
            ):
                parity_review.build_unit_review_packet(root, "../escape")
            packet_path = root / "tools/packet.json"
            packet_path.write_bytes(parity_review.canonical_json_bytes(packet))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "unsupported parity manifest"
            ):
                parity_review.load_manifest(packet_path, root)
            self.assertTrue(path.is_file())

    def test_publication_signoff_verifies_approved_and_detects_companion_staleness(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-signoff-test-") as temp:
            root = Path(temp)
            payload = manifest_fixture(root)
            unit = published_unit_names()[0]
            companion = root / unit / "fixture.txt"
            companion.write_text("fixture v1\n", encoding="utf-8")
            second_companion = root / unit / "fixture-2.txt"
            second_companion.write_text("fixture 2\n", encoding="utf-8")
            path = migrate_review_fixture(root, payload)
            (root / "ATTRIBUTIONS.toml").write_text(
                "\n".join(
                    [
                        "schema_version = 1",
                        "",
                        "[[entries]]",
                        'id = "fixture-original"',
                        (
                            f'paths = ["{unit}/fixture.txt", '
                            f'"{unit}/fixture-2.txt"]'
                        ),
                        'kind = "fixture"',
                        'status = "original-declared"',
                        'declaration = "original test fixture"',
                        'review_date = "2026-07-15"',
                        'review_role = "fixture provenance owner"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            with expected_units_fixture():
                aggregate, baseline = parity_review.snapshot_manifest(path, root)
            units = [root / name for name in published_unit_names()]
            with (
                expected_units_fixture(),
                patch.object(parity_review.validate_book, "load_config", return_value={}),
                patch.object(parity_review, "scoped_units", return_value=units),
                patch.object(parity_review, "signals", side_effect=synthetic_signals),
            ):
                aggregate = parity_review.build_v2_manifest(root, aggregate)
            approve_v2_payload(root, aggregate)
            parity_review.validate_manifest(aggregate, root, require_accepted=True)
            with expected_units_fixture():
                parity_review.write_manifest(path, aggregate, root, baseline)
                packet = parity_review.build_unit_review_packet(root, unit)
            self.assertEqual(
                [f"{unit}/fixture-2.txt", f"{unit}/fixture.txt"],
                packet["provenance"]["references"][0]["covered_paths"],
            )
            normalized_entry = {
                "adaptation": None,
                "declaration": "original test fixture",
                "id": "fixture-original",
                "kind": "fixture",
                "paths": [f"{unit}/fixture-2.txt", f"{unit}/fixture.txt"],
                "review_date": "2026-07-15",
                "review_role": "fixture provenance owner",
                "status": "original-declared",
            }
            normalized_entry = {
                key: value
                for key, value in normalized_entry.items()
                if value is not None
            }
            expected_provenance_sha256 = independent_sha256(
                {
                    "inventory_schema_version": 1,
                    "entry": normalized_entry,
                    "evidence": [
                        {
                            "path": f"{unit}/fixture-2.txt",
                            "sha256": hashlib.sha256(
                                second_companion.read_bytes()
                            ).hexdigest(),
                        },
                        {
                            "path": f"{unit}/fixture.txt",
                            "sha256": hashlib.sha256(
                                companion.read_bytes()
                            ).hexdigest(),
                        },
                    ],
                }
            )
            self.assertEqual(
                expected_provenance_sha256,
                packet["provenance"]["references"][0]["provenance_sha256"],
            )

            signoff_path = root / parity_review.PUBLICATION_SIGNOFF
            with expected_units_fixture():
                signoff = parity_review.pending_publication_signoff(root)
                root_packet = parity_review.build_root_review_packet(root)
            unit_leaf_paths = sorted(
                list((root / "tools/parity/sources").glob("*.json"))
                + list((root / "tools/parity/records").rglob("*.json"))
            )
            expected_unit_leaf_refs = [
                {
                    "path": leaf.relative_to(root).as_posix(),
                    "sha256": hashlib.sha256(leaf.read_bytes()).hexdigest(),
                }
                for leaf in unit_leaf_paths
            ]
            self.assertEqual(135, len(expected_unit_leaf_refs))
            quality_paths = sorted(
                [
                    "BOOK_STYLE.md",
                    "tools/parity_review.py",
                    "tools/validate_book.py",
                    "tools/run_quality.py",
                    "tools/book_quality.toml",
                    "tools/learning_bridges_plugin.py",
                    "tools/quality_matrix.toml",
                ]
            )
            expected_quality_refs = [
                {
                    "path": relative,
                    "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(),
                }
                for relative in quality_paths
            ]
            for reference in root_packet["decisions"]:
                self.assertRegex(reference["decision_id"], r"^root:")
                root_value = root_packet["root_publication"]["value"]
                if reference["decision_id"] == "root:README.md:canonical":
                    review = root_value["canonical_review"]
                else:
                    page = next(
                        item
                        for item in root_value["pages"]
                        if item["path"] == reference["path"]
                    )
                    gate = reference["decision_id"].rsplit(":", 1)[1]
                    field = {
                        "rendered-accessibility": "rendered_accessibility_review",
                        "linguistic": "linguistic_review",
                        "technical": "technical_review",
                        "bidi": "bidi_review",
                    }[gate]
                    review = page[field]
                self.assertEqual(
                    independent_sha256(
                        {
                            "decision_id": reference["decision_id"],
                            "path": reference["path"],
                            "review": review,
                        }
                    ),
                    reference["decision_sha256"],
                )
            expected_inputs = {
                "attributions_sha256": hashlib.sha256(
                    (root / "ATTRIBUTIONS.toml").read_bytes()
                ).hexdigest(),
                "parity_index_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "quality_contract_sha256": independent_sha256(expected_quality_refs),
                "render_profile_sha256": hashlib.sha256(
                    (root / parity_review.RENDER_PROFILE).read_bytes()
                ).hexdigest(),
                "root_decisions": [
                    {
                        "decision_id": item["decision_id"],
                        "decision_sha256": item["decision_sha256"],
                    }
                    for item in root_packet["decisions"]
                ],
                "root_leaf_sha256": hashlib.sha256(
                    (root / "tools/parity/root-publication.json").read_bytes()
                ).hexdigest(),
                "unit_evidence_sha256": independent_sha256(
                    expected_unit_leaf_refs
                ),
                "unit_provenance_sha256": independent_sha256(
                    [
                        {
                            "unit": unit,
                            **packet["provenance"]["references"][0],
                        }
                    ]
                ),
            }
            self.assertEqual(expected_inputs, signoff["inputs"])
            self.assertEqual(
                independent_sha256(expected_inputs), signoff["signoff_input_sha256"]
            )
            signoff_path.write_bytes(parity_review.canonical_json_bytes(signoff))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "reviews are pending"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            for field in (
                "book_editor_review",
                "accessibility_review",
                "provenance_review",
            ):
                approve_review(signoff[field])
            signoff_path.write_bytes(parity_review.canonical_json_bytes(signoff))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "state is not approved"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            signoff["state"] = "approved"
            signoff_path.write_bytes(parity_review.canonical_json_bytes(signoff))
            before = file_snapshot(root)
            with expected_units_fixture():
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            self.assertEqual(before, file_snapshot(root))

            changes_requested = copy.deepcopy(signoff)
            changes_requested["state"] = "changes-requested"
            changes_requested["book_editor_review"]["result"] = (
                "changes-requested"
            )
            signoff_path.write_bytes(
                parity_review.canonical_json_bytes(changes_requested)
            )
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "reviews are pending"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            stored_stale = copy.deepcopy(signoff)
            stored_stale["state"] = "stale"
            signoff_path.write_bytes(parity_review.canonical_json_bytes(stored_stale))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "state is not approved"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            malformed = copy.deepcopy(signoff)
            del malformed["book_editor_review"]["role"]
            signoff_path.write_bytes(parity_review.canonical_json_bytes(malformed))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "malformed publication book-editor"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            signoff_path.write_bytes(parity_review.canonical_json_bytes(signoff))

            badge_path = root / "icons/cc-by-sa.svg"
            badge_bytes = badge_path.read_bytes()
            badge_path.write_bytes(badge_bytes + b"<!-- changed -->\n")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "upstream evidence is stale"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            badge_path.write_bytes(badge_bytes)

            canonical_path = root / unit / "README.md"
            canonical_bytes = canonical_path.read_bytes()
            canonical_path.write_bytes(canonical_bytes + b"\nchanged\n")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "upstream evidence is stale"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            canonical_path.write_bytes(canonical_bytes)

            root_page = root / "README.es.md"
            root_page_bytes = root_page.read_bytes()
            root_page.write_bytes(root_page_bytes + b"\nchanged\n")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "upstream evidence is stale"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            root_page.write_bytes(root_page_bytes)

            profile_path = root / parity_review.RENDER_PROFILE
            profile_bytes = profile_path.read_bytes()
            changed_profile = json.loads(profile_bytes)
            changed_profile["accessibility_checks"].append("fixture changed check")
            profile_path.write_bytes(independent_canonical_json_bytes(changed_profile))
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "upstream evidence is stale"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            profile_path.write_bytes(profile_bytes)

            quality_path = root / "BOOK_STYLE.md"
            quality_bytes = quality_path.read_bytes()
            quality_path.write_bytes(quality_bytes + b"\n")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError, "inputs are stale"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            quality_path.write_bytes(quality_bytes)
            with expected_units_fixture():
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )

            approved_signoff = copy.deepcopy(signoff)
            resolved_attributions = (root / "ATTRIBUTIONS.toml").read_bytes()
            misc = root / "misc.txt"
            misc.write_text("unresolved fixture\n", encoding="utf-8")
            with (root / "ATTRIBUTIONS.toml").open("a", encoding="utf-8") as stream:
                stream.write(
                    "\n".join(
                        [
                            "[[entries]]",
                            'id = "unresolved-misc"',
                            'paths = ["misc.txt"]',
                            'kind = "fixture"',
                            'status = "review-required"',
                            'note = "human provenance review required"',
                            "",
                        ]
                    )
                )
            with expected_units_fixture():
                unresolved_signoff = parity_review.pending_publication_signoff(root)
            for field in (
                "book_editor_review",
                "accessibility_review",
                "provenance_review",
            ):
                approve_review(unresolved_signoff[field])
            unresolved_signoff["state"] = "approved"
            signoff_path.write_bytes(
                parity_review.canonical_json_bytes(unresolved_signoff)
            )
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError,
                "provenance review is incomplete",
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            (root / "ATTRIBUTIONS.toml").write_bytes(resolved_attributions)
            signoff_path.write_bytes(
                parity_review.canonical_json_bytes(approved_signoff)
            )

            leaf_before = {
                relative: data
                for relative, data in before.items()
                if relative.startswith("tools/parity/")
            }
            attribution_before = (root / "ATTRIBUTIONS.toml").read_bytes()
            companion.write_text("fixture v2\n", encoding="utf-8")
            self.assertEqual(attribution_before, (root / "ATTRIBUTIONS.toml").read_bytes())
            self.assertEqual(
                leaf_before,
                {
                    relative: data
                    for relative, data in file_snapshot(root).items()
                    if relative.startswith("tools/parity/")
                },
            )
            with expected_units_fixture():
                stale_aggregate = parity_review.load_manifest(path, root)
            with self.assertRaisesRegex(
                parity_review.ParityError,
                "stale canonical source provenance",
            ):
                parity_review.validate_manifest(stale_aggregate, root)
            with (
                expected_units_fixture(),
                patch.object(parity_review.validate_book, "load_config", return_value={}),
                patch.object(parity_review, "scoped_units", return_value=units),
                patch.object(parity_review, "signals", side_effect=synthetic_signals),
            ):
                refreshed = parity_review.build_v2_manifest(root, stale_aggregate)
            self.assertEqual(
                {"stale"},
                {
                    record["status"]
                    for record in refreshed["records"]
                    if record["unit"] == unit
                },
            )
            self.assertEqual(
                {"accepted"},
                {
                    record["status"]
                    for record in refreshed["records"]
                    if record["unit"] != unit
                },
            )
            parity_review.validate_manifest(refreshed, root)
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.PublicationIncompleteError,
                "upstream evidence is stale",
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )

    def test_publication_signoff_rejects_noncanonical_or_unsafe_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-signoff-test-") as temp:
            root = Path(temp)
            migrate_review_fixture(root, manifest_fixture(root))
            signoff_path = root / parity_review.PUBLICATION_SIGNOFF
            with expected_units_fixture():
                signoff = parity_review.pending_publication_signoff(root)
            signoff_path.write_text(json.dumps(signoff), encoding="utf-8")
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "canonical JSON"
            ):
                parity_review.verify_publication_signoff(
                    root, parity_review.PUBLICATION_SIGNOFF
                )
            with self.assertRaisesRegex(parity_review.ParityError, "non-canonical"):
                parity_review.verify_publication_signoff(
                    root, "tools/../tools/publication_signoff.json"
                )

    def test_resolved_provenance_requires_complete_human_evidence(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-provenance-test-") as temp:
            root = Path(temp)
            migrate_review_fixture(root, manifest_fixture(root))
            unit = published_unit_names()[0]
            evidence = root / unit / "fixture.txt"
            evidence.write_text("original fixture\n", encoding="utf-8")
            (root / "ATTRIBUTIONS.toml").write_text(
                "\n".join(
                    [
                        "schema_version = 1",
                        "",
                        "[[entries]]",
                        'id = "incomplete-original"',
                        f'paths = ["{unit}/fixture.txt"]',
                        'kind = "fixture"',
                        'status = "original-declared"',
                        'declaration = "original fixture"',
                        'review_date = "2026-07-15"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            with expected_units_fixture(), self.assertRaisesRegex(
                parity_review.ParityError, "lacks human-reviewed evidence"
            ):
                parity_review.build_unit_review_packet(root, unit)

    def test_root_provenance_change_remains_stale_until_explicit_review(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-root-stale-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            (root / "ATTRIBUTIONS.toml").write_text(
                "\n".join(
                    [
                        "schema_version = 1",
                        "",
                        "[[entries]]",
                        'id = "root-icon-original"',
                        'paths = ["icons/cc-by-sa.svg"]',
                        'kind = "fixture"',
                        'status = "original-declared"',
                        'declaration = "original fixture icon"',
                        'review_date = "2026-07-15"',
                        'review_role = "fixture provenance owner"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            with expected_units_fixture():
                aggregate, _baseline = parity_review.snapshot_manifest(path, root)
            aggregate["root_publication"] = parity_review.refresh_root_publication(
                root, aggregate["root_publication"]
            )
            approve_v2_payload(root, aggregate)
            parity_review.validate_manifest(aggregate, root, require_accepted=True)

            (root / "icons/cc-by-sa.svg").write_text(
                "<svg><title>changed</title></svg>\n", encoding="utf-8"
            )
            refreshed = parity_review.refresh_root_publication(
                root, aggregate["root_publication"]
            )
            self.assertEqual("stale", refreshed["state"])
            self.assertNotEqual(
                aggregate["root_publication"]["provenance"], refreshed["provenance"]
            )
            repeated = parity_review.refresh_root_publication(root, refreshed)
            self.assertEqual("stale", repeated["state"])
            profile, profile_sha256 = parity_review.load_render_profile(root)
            parity_review.validate_root_publication(
                repeated,
                root,
                profile,
                profile_sha256,
            )

    def test_root_provenance_includes_normally_linked_non_markdown_assets(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-root-asset-test-") as temp:
            root = Path(temp)
            migrate_review_fixture(root, manifest_fixture(root))
            english = "# Course fixture\n\n[Dataset](assets/data.pdf)\n"
            (root / "README.md").write_text(english, encoding="utf-8")
            (root / "README.en.md").write_text(english, encoding="utf-8")
            asset = root / "assets/data.pdf"
            asset.parent.mkdir()
            asset.write_bytes(b"fixture pdf bytes\n")
            (root / "ATTRIBUTIONS.toml").write_text(
                "\n".join(
                    [
                        "schema_version = 1",
                        "",
                        "[[entries]]",
                        'id = "root-linked-asset"',
                        'paths = ["assets/data.pdf"]',
                        'kind = "fixture"',
                        'status = "original-declared"',
                        'declaration = "original fixture asset"',
                        'review_date = "2026-07-15"',
                        'review_role = "fixture provenance owner"',
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            profile, _profile_sha256 = parity_review.load_render_profile(root)
            references = parity_review.root_provenance_references(root, profile)
            self.assertEqual(["root-linked-asset"], [item["id"] for item in references])

    def test_root_changes_requested_remains_blocked_when_render_input_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-root-blocked-test-") as temp:
            root = Path(temp)
            path = migrate_review_fixture(root, manifest_fixture(root))
            with expected_units_fixture():
                aggregate = parity_review.load_manifest(path, root)
            approve_v2_payload(root, aggregate)
            localized_page = next(
                page
                for page in aggregate["root_publication"]["pages"]
                if page["path"] == "README.es.md"
            )
            localized_page["linguistic_review"]["result"] = "changes-requested"
            aggregate["root_publication"]["state"] = "blocked"
            (root / "icons/cc-by-sa.svg").write_text(
                "<svg><title>changed</title></svg>\n", encoding="utf-8"
            )
            refreshed = parity_review.refresh_root_publication(
                root, aggregate["root_publication"]
            )
            self.assertEqual("blocked", refreshed["state"])
            profile, profile_sha256 = parity_review.load_render_profile(root)
            parity_review.validate_root_publication(
                refreshed, root, profile, profile_sha256
            )

    def test_packet_cli_stdout_stderr_and_exit_codes_are_stable(self) -> None:
        with tempfile.TemporaryDirectory(prefix="parity-packet-cli-test-") as temp:
            root = Path(temp)
            migrate_review_fixture(root, manifest_fixture(root))
            unit = published_unit_names()[0]
            module_file = root / "tools/parity_review.py"
            with expected_units_fixture(), patch.object(
                parity_review, "__file__", str(module_file)
            ):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = parity_review.main(["--review-packet", unit])
                self.assertEqual(0, result)
                self.assertEqual("", stderr.getvalue())
                self.assertEqual("unit-review", json.loads(stdout.getvalue())["packet_kind"])

                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = parity_review.main(
                        ["--review-packet", "../escape"]
                    )
                self.assertEqual(2, result)
                self.assertEqual("", stdout.getvalue())
                self.assertIn("ERROR parity.inventory", stderr.getvalue())
                self.assertNotIn(str(root), stderr.getvalue())

                signoff_path = root / parity_review.PUBLICATION_SIGNOFF
                signoff = parity_review.pending_publication_signoff(root)
                signoff_path.write_bytes(parity_review.canonical_json_bytes(signoff))
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = parity_review.main(
                        [
                            "--verify-publication-signoff",
                            parity_review.PUBLICATION_SIGNOFF,
                        ]
                    )
                self.assertEqual(1, result)
                self.assertEqual("", stdout.getvalue())
                self.assertIn("publication review incomplete", stderr.getvalue())

                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = parity_review.main(
                        [
                            "--review-packet",
                            unit,
                            "--manifest",
                            "tools/custom.json",
                        ]
                    )
                self.assertEqual(2, result)
                self.assertEqual("", stdout.getvalue())
                self.assertIn("default parity index", stderr.getvalue())

                for arguments in (
                    ["--review-packet", ""],
                    ["--verify-publication-signoff", ""],
                    ["--review-packet", unit, "--require-accepted"],
                ):
                    with self.subTest(arguments=arguments):
                        stdout = io.StringIO()
                        stderr = io.StringIO()
                        with contextlib.redirect_stdout(
                            stdout
                        ), contextlib.redirect_stderr(stderr):
                            result = parity_review.main(arguments)
                        self.assertEqual(2, result)
                        self.assertEqual("", stdout.getvalue())
                        self.assertTrue(stderr.getvalue().startswith("ERROR "))

                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    result = parity_review.main(
                        ["--migrate-review-schema", "--require-accepted"]
                    )
                self.assertEqual(1, result)
                self.assertIn("cannot be combined", stdout.getvalue())
                self.assertEqual("", stderr.getvalue())

    def test_packet_stdout_writer_preserves_exact_canonical_bytes(self) -> None:
        class BinaryCapture:
            def __init__(self) -> None:
                self.buffer = io.BytesIO()

            def write(self, value: str) -> int:
                raise AssertionError(f"text stdout used unexpectedly: {value!r}")

        capture = BinaryCapture()
        payload = {"arabic": "مرحبا", "value": [1, 2, 3]}
        expected = independent_canonical_json_bytes(payload)
        with patch.object(parity_review.sys, "stdout", capture):
            parity_review.write_stdout_bytes(expected)
        self.assertEqual(expected, capture.buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
