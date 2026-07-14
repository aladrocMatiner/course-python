## 1. Freeze partition storage contracts

- [x] 1.1 Add schema-v2 index and granular loader fixtures.
  - **Objective:** Resolve exactly 27 source files and 108 unit/locale files into the existing aggregate contract.
  - **Deliverables:** Partition constants/models/loaders in `tools/parity_review.py` and temporary-repository fixtures.
  - **Validation:** Complete, missing, extra, duplicate, misnamed, malformed, stale, Unicode, traversal, symlink, and shuffled-enumeration cases produce stable results.
  - **Risk:** Filesystem discovery can silently omit evidence; derive exact paths from validated topology and reject extras.
  - **Scope:** L.

- [x] 1.2 Add deterministic localized writers.
  - **Objective:** Serialize canonical/locale objects atomically while leaving byte-identical evidence untouched.
  - **Deliverables:** Canonical JSON serializers, same-directory temporary replacement, changed-file planner, and cleanup.
  - **Validation:** One-locale, one-source/four-locale, multi-promotion, no-op, stale-writer/concurrent-edit CAS, write-failure, partial-state, and deterministic retry tests inspect exact changed paths/bytes.
  - **Scope:** L.

## 2. Implement lossless migration and rollback export

- [x] 2.1 Implement explicit staged `--migrate-partitioned`.
  - **Objective:** Publish the partition only after production reload, validation, and whole-object equality with schema v1.
  - **Deliverables:** Staging/publish/retry logic and fail-closed CLI diagnostics.
  - **Validation:** Successful migration, malformed/stale/already-v2 input, serialization failure, comparison mismatch, concurrent source edit, interrupted pre/post-store publication, conflicting retry, path escape, and cleanup cases pass.
  - **Risk:** Cross-file atomicity is limited; keep the monolith authoritative until the final atomic index replacement and expose partial state.
  - **Scope:** L.

- [x] 2.2 Implement explicit `--export-monolith` rollback evidence.
  - **Objective:** Reconstruct canonical schema-v1 bytes without replacing live storage or deleting evidence.
  - **Deliverables:** Safe explicit output, atomic validation, and round-trip comparator.
  - **Validation:** Exact byte round trip, existing/conflicting output policy, unsafe path, write failure, Unicode/Arabic, and live-index non-mutation tests pass.
  - **Scope:** M.

## 3. Preserve review workflow and human invariants

- [x] 3.1 Route every existing parity action through the aggregate loader/writer.
  - **Objective:** Keep default, `--write`, `--reconcile-drafts`, `--record-automated`, `--manifest`, and `--require-accepted` behavior stable.
  - **Deliverables:** Partition-aware CLI and compatibility tests for direct schema-v1 fixtures.
  - **Validation:** Read-only snapshot, effective-baseline blockers, current transition tests, custom manifest, exact 27/108 counters, and stable exit messages pass.
  - **Scope:** M.

- [x] 3.2 Prove digest invalidation and writes stay local.
  - **Objective:** Make independent locale review safe while invalidating all evidence actually tied to a changed canonical digest.
  - **Deliverables:** Regression tests for localized change, canonical change, no-op refresh, and automated promotion.
  - **Validation:** Localized change touches one record; canonical change touches one source plus four records; unrelated bytes/index stay identical; retry recovers visibly from partial files.
  - **Scope:** M.

- [x] 3.3 Prove no storage operation can fabricate human evidence.
  - **Objective:** Preserve audit/status/dimensions/exceptions/commands/review roles/dates/notes exactly except existing explicit transition semantics.
  - **Deliverables:** Whole-object invariants and negative accepted-record fixtures.
  - **Validation:** Migration/export/default/write never promote; accepted fixtures still require every source/human/automated field; `--require-accepted` retains pending counts.
  - **Scope:** M.

## 4. Migrate current evidence and reconcile documentation

- [x] 4.1 Migrate the real 27/108 manifest and prove its round trip.
  - **Objective:** Replace the hotspot without losing or approving current evidence.
  - **Deliverables:** Compact `tools/parity_manifest.json`, 27 source files, 108 locale files, and temporary exported comparison removed after review.
  - **Validation:** Export matches the pre-migration SHA-256/bytes; counters remain 27 pending audits and 108 `automated-signals-pass`; default validation passes; publication gate fails as expected.
  - **Risk:** The source manifest already contains concurrent work; migrate the current bytes once and never regenerate review values from counts.
  - **Scope:** M.

- [x] 4.2 Update reviewer guidance and active change storage wording.
  - **Objective:** Teach locale-local diffs, safe migration/export/recovery, and unchanged human gates.
  - **Deliverables:** `tools/PARITY_REVIEW_GUIDE.md`, relevant quality/skill guidance, and coordinated active OpenSpec artifact references.
  - **Validation:** Commands use the stable CLI/index; docs identify authoritative files; no content wave, source audit, accessibility/bidi, provenance, or human sign-off checkbox is completed.
  - **Scope:** S.

## 5. Integrated verification

- [x] 5.1 Run partition and full tooling regressions.
  - **Objective:** Demonstrate storage, transitions, automation, publication boundary, and read-only guarantees together.
  - **Deliverables:** Passing parity-specific and all `tools/tests` evidence.
  - **Validation:** `python -B tools/parity_review.py`; expected non-zero `--require-accepted` with 27/108 pending; curriculum/generic validators; no source mutation or generated caches.
  - **Scope:** M.

- [x] 5.2 Record implementation evidence and run strict coordination/hygiene checks.
  - **Objective:** Leave an apply-complete change whose artifacts and real storage agree.
  - **Deliverables:** `IMPLEMENTATION_REVIEW.md` with exact migration hash/counters/failure boundary and completed checklist.
  - **Validation:** Strict validation for this change, `restore-multilingual-content-parity`, `add-book-quality-gates`, and the runner change; `openspec doctor`; `git diff --check`; no stage/export/temp files.
  - **Scope:** S.
