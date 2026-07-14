## Context

`tools/parity_manifest.json` is both the validation input and the edit queue for 27 canonical sources and 108 localized variants. It is currently a deterministic 5,563-line schema-v1 document. Every canonical audit, locale contract, exception, command, role, date, note, digest, signal, priority, and gap shares that file. This makes unrelated review batches conflict even though `restore-multilingual-content-parity` deliberately limits work to at most two units/two locales.

All canonical audits remain `pending-human-review`; all 108 locale records are `automated-signals-pass` with human fields pending. The migration must preserve this exact evidence. `parity_review.py` is the stable CLI and in-memory validation logic, `validate_book.py` owns automated diagnostics, and human reviewers alone may approve semantic/accessibility/bidi/provenance gates.

## Goals / Non-Goals

**Goals:**

- Give each canonical source and each unit/locale record an independent authoritative file.
- Preserve every schema-v1 field and state through a deterministic reversible migration.
- Keep aggregate validation, CLI behavior, review transitions, and publication failure semantics stable.
- Write only evidence whose payload changed and fail closed on incomplete, duplicate, stale, escaping, or extra storage.
- Make interrupted migration/update recoverable without guessing or promoting evidence.

**Non-Goals:**

- Translate or edit lesson Markdown, decide source quality, or approve any human gate.
- Change the twelve semantic dimensions, transition graph, plugin evidence, or accepted-state requirements.
- Treat structural signals, counts, or successful migration as semantic parity.
- Introduce a database, service, external dependency, reviewer identity system, or generated approval.

## Decisions

### Keep a compact index and granular authoritative files

`tools/parity_manifest.json` becomes schema version 2 and contains the existing notice, a fixed relative store root (`tools/parity`), the exact ordered unit IDs, and the exact ordered locale IDs. It contains no mutable per-review digest: otherwise every locale edit would still touch the hotspot.

`tools/parity/sources/<unit>.json` contains schema version 1 and exactly one canonical source object. `tools/parity/records/<unit>/<locale>.json` contains schema version 1 and exactly one localized record object. Unit/locale names must match discovered publication scope and safe slug vocabularies; paths are derived rather than supplied by each record. Symlink, traversal, missing, duplicate, and extra JSON files fail validation.

One file per unit was rejected because four language reviewers would still conflict. One file per semantic dimension was rejected because it would fragment an auditable review decision and make acceptance harder to inspect.

### Preserve schema-v1 aggregate semantics in memory

The loader resolves schema v1 (legacy monolith) or schema v2 (partition index) into the same schema-v1 aggregate object consumed by `build_manifest`, `validate_manifest`, transition checks, and automated promotion. This keeps review semantics in one implementation. The partition writer performs the inverse projection and canonical JSON serialization (`indent=2`, Unicode preserved, keys sorted, final newline).

Aggregate order is the index's validated unit order followed by the stable locale order `es`, `ca`, `sv`, `ar`. A deterministic `--export-monolith <path>` writes the exact legacy representation for audit/rollback. Normal validation remains read-only.

Keeping a generated aggregate checked in was rejected because it would recreate the conflict and introduce two authorities. The compatibility aggregate is emitted only on explicit request.

### Make migration explicit, lossless, and fail-closed

`--migrate-partitioned` accepts only a valid schema-v1 default/current manifest. It builds all 135 files under a temporary sibling store, constructs a temporary index, reloads it through the production loader, validates it, and compares the canonical aggregate bytes with the original. Only then is the absent destination store published with Linux `renameat2(RENAME_NOREPLACE)` and the index updated with exchange/rollback semantics. A host without the tested no-replace directory primitive fails closed before publication. The original schema-v1 bytes are compared again before publication; a concurrent note/review edit observed by the exchange is restored and remains authoritative.

If execution stops before index replacement, the schema-v1 monolith remains authoritative. A retry may adopt an already-published store only after exact reload/comparison; conflicting data causes a diagnostic and no overwrite. Temporary paths are bounded to the manifest parent and cleaned when safe. The command never removes the legacy information before equivalence is proved.

The rollback path is explicit export rather than automatic destructive replacement: export, verify byte identity/diff, then a maintainer may replace the index in the same reviewed change. No field is synthesized in either direction.

### Localize normal writes and expose partial failure

Partition-aware `--write`, `--reconcile-drafts`, and `--record-automated` build and validate the full next aggregate before writing. Each changed source/record is serialized to a same-directory temporary file and re-read. On Linux, `renameat2(RENAME_EXCHANGE)` captures the exact replaced bytes and rolls back when they differ from the loaded baseline; failed rollback retains recovery evidence instead of deleting it. Other hosts serialize cooperating CLI writers with a hardened external lock, recheck under that lock, and use no-clobber creation/replace. That portable fallback does not claim protection from an editor that ignores the lock, so manual evidence edits must not overlap a mutating parity command. Byte-identical files are untouched. Index bytes are unchanged unless publication scope/schema changes.

A localized digest change resets only its record. A canonical digest change resets its source audit and the four records tied to that canonical digest. Automated promotion may update every eligible drafted record, but it still writes only those record files. If a multi-file operation is interrupted after some atomic replacements, the next read detects stale/inconsistent evidence and exits non-zero; rerunning the explicit operation deterministically completes the same transition. The tool does not conceal partial state or fabricate a transaction result.

A complex generation-pointer store was rejected: it would make every small review publish an entire generation and require garbage collection. File-level atomicity plus fail-closed recovery is adequate for a Git-reviewed repository.

### Keep human authority and active-change ownership unchanged

Migration copies `audit`, `status`, all 12 dimension results, exceptions, automated commands, and both review objects verbatim. No storage operation may promote state, approve an audit/review, add a role/date/note, or turn a provenance warning into approval. `--require-accepted` runs after aggregate validation and must continue to report 27/108 pending until people record complete current evidence.

The active multilingual change remains the owner of content repair and semantic review. The book-quality change remains the owner of generic diagnostics/baseline/provenance. Their documents are updated only to explain that `parity_manifest.json` is an index and `tools/parity/` stores authoritative records; no human task checkbox changes.

## Risks / Trade-offs

- [Migration loses a rarely used review field] → Whole-object canonical byte comparison and round-trip tests, not a selected-field mapping.
- [Many files make discovery ambiguous] → Fixed derived layout, exact 27/108 cardinality, rejection of extra/missing/duplicate files.
- [An interrupted or concurrent multi-file update is partially visible] → Linux exchange/rollback, cooperative fallback locking, atomic individual writes, source-byte revalidation, full-load fail-closed validation, deterministic retry, and no silent acceptance. Out-of-band editors are explicitly serialized with CLI mutation on fallback hosts.
- [Index remains a conflict point] → It contains publication topology only; ordinary reviews never rewrite it.
- [Automation accidentally advances human state] → Copy invariants and negative tests assert every human field/state before and after migration/actions.
- [Symlinks or custom manifests escape the repository] → Resolve every index/store/temp/output path against the repository root and reject escapes before I/O.
- [135 files feel noisier] → Review diffs become one source or locale object, while the CLI retains one aggregate view and stable commands.

## Migration Plan

1. Add partition loader/writer/migration tests using temporary repositories and the exact schema-v1 fixture.
2. Add `--migrate-partitioned` and `--export-monolith`; prove failed migrations leave the monolith authoritative.
3. Migrate the current 27/108 manifest and compare exported bytes and all human-state counters with the pre-migration file.
4. Run normal validation, expected publication failure, generic validator, tooling tests, and strict coordinated OpenSpec validation.
5. Update reviewer guidance and active artifact storage wording without completing human tasks.
6. Roll back by exporting the schema-v1 aggregate, verifying it, replacing the index in a reviewed diff, and removing the partition directory only after validation.

## Open Questions

None for storage schema v2. Reviewer packets and rendered-review assignment are later additive capabilities built on this store.
