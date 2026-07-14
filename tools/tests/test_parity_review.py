from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
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
        "schema_version": parity_review.SCHEMA_VERSION,
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

    def test_discovery_covers_twenty_five_chapters_and_two_appendices(self) -> None:
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
                parity_review.EXPECTED_CANONICAL_SOURCES,
                len(list((root / "tools/parity/sources").glob("*.json"))),
            )
            self.assertEqual(
                parity_review.EXPECTED_LOCALIZED_RECORDS,
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
            self.assertEqual(parity_review.SCHEMA_VERSION, preserved["schema_version"])
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
                parity_review.parse_args(["--export-monolith", "tools/out.json", "--write"])
        self.assertEqual(2, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
