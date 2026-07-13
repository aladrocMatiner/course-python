from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


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
    for index in range(24):
        unit_name = f"unit-{index:02d}"
        unit = root / unit_name
        unit.mkdir()
        canonical = unit / "README.md"
        canonical.write_text(f"# Canonical {index}\n", encoding="utf-8")
        canonical_sha = parity_review.digest(canonical)
        sources.append(
            {
                "unit": unit_name,
                "path": f"{unit_name}/README.md",
                "sha256": canonical_sha,
                "signals": {},
                "audit": "pending-human-review",
            }
        )
        for locale, filename in parity_review.LOCALES.items():
            localized = unit / filename
            localized.write_text(f"# Localized {index} {locale}\n", encoding="utf-8")
            records.append(
                {
                    "unit": unit_name,
                    "locale": locale,
                    "path": f"{unit_name}/{filename}",
                    "canonical_sha256": canonical_sha,
                    "localized_sha256": parity_review.digest(localized),
                    "status": "inventoried",
                    "contract": {
                        dimension: "pending" for dimension in parity_review.CONTRACT_DIMENSIONS
                    },
                    "exceptions": [],
                    "linguistic_review": parity_review.empty_review(),
                    "technical_review": parity_review.empty_review(),
                }
            )
    return {
        "schema_version": parity_review.SCHEMA_VERSION,
        "sources": sources,
        "records": records,
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

    def test_publication_mode_requires_all_historical_reviews(self) -> None:
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
            parity_review.validate_manifest(payload, root, require_accepted=True)

    def test_contract_has_twelve_semantic_dimensions(self) -> None:
        self.assertEqual(12, len(parity_review.CONTRACT_DIMENSIONS))
        self.assertEqual(len(set(parity_review.CONTRACT_DIMENSIONS)), len(parity_review.CONTRACT_DIMENSIONS))

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
            "records": [
                {"path": "ok.md", "status": "drafted", "automated_commands": []},
                {"path": "blocked.md", "status": "drafted", "automated_commands": []},
                {"path": "human.md", "status": "linguistic-reviewed", "automated_commands": []},
            ]
        }
        diagnostics = [
            parity_review.validate_book.Diagnostic("rule", "blocked.md", "bad", "fix")
        ]
        self.assertEqual(1, parity_review.record_automated_results(payload, diagnostics))
        self.assertEqual("automated-signals-pass", payload["records"][0]["status"])
        self.assertEqual("drafted", payload["records"][1]["status"])
        self.assertEqual("linguistic-reviewed", payload["records"][2]["status"])

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


if __name__ == "__main__":
    unittest.main()
