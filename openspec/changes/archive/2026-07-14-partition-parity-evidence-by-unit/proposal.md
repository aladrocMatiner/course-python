## Why

All 27 canonical audits and 108 localized review records currently share one 5,500-line JSON file, so independent reviewers edit the same hotspot and routine unit work creates avoidable merge conflicts. Human review is still pending, making this the safest point to partition storage without migrating accepted decisions or inventing approval evidence.

## What Changes

- Replace the monolithic record store with a small versioned index, one deterministic canonical-source file per published unit, and one deterministic record file per unit/locale.
- Keep `tools/parity_review.py` as the stable entry point and preserve its validation, reconciliation, automated-signal, and publication-gate semantics across the partitioned store.
- Add an explicit, fail-closed migration that round-trips every digest, state, contract dimension, exception, command, role, date, note, priority, gap, and signal before removing monolithic records from the index.
- Make read-only validation reject missing, extra, duplicated, escaping, malformed, stale, or misnamed unit files and guarantee deterministic aggregate ordering.
- Ensure a canonical digest change resets only its source audit and four localized records, while a localized digest change resets only that locale record; unrelated evidence files remain byte-identical.
- Add unit and repository tests for migration/rollback, Linux atomic exchange/rollback, portable cooperating-writer locking, partial failure recovery, concurrent-review isolation, source revalidation before publication, no fabricated approvals, and unchanged publication gates.
- Update reviewer guidance and the active multilingual change's storage references without marking any human task complete.

Goals are locale-local review evidence, lossless migration, deterministic aggregation, and unchanged human acceptance rules. Non-goals are translating content, approving audits/reviews, changing the twelve-dimension contract, or relaxing gates.

Migration first writes and validates all unit files in a temporary sibling directory, verifies semantic equality with the monolith, then uses a tested Linux no-replace rename to publish the complete directory and atomically exchange the index. A host without that publication primitive fails closed with the schema-v1 monolith still authoritative. Rollback deterministically exports the partitioned data back to the schema-v1 monolith; both directions reject stale or incomplete input and never infer evidence.

Done means all 27 source files and 108 locale files validate, a round trip is semantically identical, localized reconciliation changes only one locale file, canonical reconciliation changes only its source plus four locales, publication mode still reports all pending human gates, unrelated files remain byte-identical, and all coordinated OpenSpec changes validate strictly.

## Capabilities

### New Capabilities

- `partitioned-parity-evidence`: Lossless per-unit storage, deterministic aggregation, safe migration/rollback, and unit-local review updates while preserving human acceptance semantics.

### Modified Capabilities

None. The active `restore-multilingual-content-parity` delta remains the owner of semantic review requirements; this change only introduces a safer persistence capability.

## Impact

- `tools/parity_manifest.json` becomes the compact index and a new `tools/parity/` directory owns 27 `sources/<unit>.json` files plus 108 `records/<unit>/<locale>.json` files.
- `tools/parity_review.py`, `tools/tests/test_parity_review.py`, and `tools/PARITY_REVIEW_GUIDE.md` gain partition-aware behavior and migration evidence.
- Active OpenSpec artifacts that name the old monolith are reconciled to the stable index-plus-unit-store contract without claiming editorial completion.
- No chapter Markdown, localized text, digest, human role, status, or approval is intentionally changed.
- Main risks are evidence loss, partial writes, path escape, nondeterministic ordering, and accidental review promotion. Atomic staging, exact-key comparison, safe relative paths, status invariants, and before/after byte checks mitigate them.
