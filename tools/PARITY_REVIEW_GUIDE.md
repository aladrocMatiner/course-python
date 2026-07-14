# Multilingual parity review guide

`tools/parity_manifest.json` is the compact topology index for chapters 01–25
and both appendices. Authoritative mutable evidence is isolated under
`tools/parity/sources/<unit>.json` for 27 frozen English sources and
`tools/parity/records/<unit>/<locale>.json` for 108 localized records. Counts
are triage signals, never acceptance evidence. Newly inventoried advanced
chapters start with automated evidence only; their source audit and both human
reviews remain pending.

Normal validation is read-only. A reviewer edits only the source or locale file
owned by the current batch; ordinary review does not regenerate the index or a
checked-in monolithic aggregate. Missing, extra, duplicate, stale, partial, or
escaping evidence fails closed.

## Storage migration and rollback evidence

The one-time migration is explicit and verifies a complete production reload
and byte-identical schema-v1 round trip before publishing the index:

```sh illustrative
python -B tools/parity_review.py --migrate-partitioned
python -B tools/parity_review.py
python -B tools/parity_review.py --export-monolith tools/parity_manifest.roundtrip.json
```

Compare the temporary export with the pre-migration manifest, then remove the
export; it is review evidence, not a second source of truth. Export never
replaces the live index or deletes partition files. A failed/interrupted
migration keeps the schema-v1 manifest authoritative or refuses a conflicting
partial store. Inspect the diagnostic and retry the same explicit operation;
never reconstruct human fields from counts or structural signals.

Atomic publication of the complete directory requires Linux
`renameat2(RENAME_NOREPLACE)` and fails closed on a host without that primitive.
This is a one-time repository migration boundary; ordinary read-only review and
the portable writer fallback remain available after the partition is committed.

## Work in bounded batches

Review at most two units and two localized languages in one batch. Record the
current English SHA-256 before editing. If that digest changes, stop and refresh
the inventory; the record is `stale` until reconciled.

Do not edit a parity evidence JSON file while `--write`, `--reconcile-drafts`,
`--record-automated`, migration, or export is running. Linux uses atomic
exchange/rollback to preserve an edit observed at publication. Other hosts
serialize cooperating parity CLI writers with a hardened external lock, but an
editor that ignores that lock is outside the portable fallback guarantee.

Refreshing and reconciling are deliberately separate operations. First inspect
the source/locale evidence diff produced by `--write`. When the changed source
and all four localized files are ready for a new review cycle, explicitly run:

```sh illustrative
python -B tools/parity_review.py --reconcile-drafts
```

This refreshes current digests and changes only `stale` or `inventoried`
records to `drafted`. It clears their old twelve-dimension results, exceptions,
automated command evidence, review roles, dates and notes because none of that
evidence applies to the new digest. Progressed records whose digests are still
current are left unchanged. A localized digest changes only its locale record;
a changed canonical source returns its audit to `pending-human-review` and
invalidates its four locale records. Unrelated evidence and the index remain
byte-identical. Review the granular diff before proceeding. The flag cannot set
`accepted` or either human approval, and it requires an existing index/store.

Use this progression:

```text illustrative
inventoried → source-frozen → drafted → automated-signals-pass
→ linguistic-reviewed → technical-reviewed → accepted
```

`blocked` records have a concrete correctness, safety, accessibility, bidi or
tooling failure. An intentional difference uses `exception` only with a narrow
justification and both linguistic and technical approval. Do not put learner
data, credentials, or unnecessary reviewer identity in evidence files; record
a role such as `fluent Arabic reviewer` or `Python technical reviewer`.

## Twelve-dimension checklist

For each localized record, mark every parity-contract dimension `pass`, or
attach an approved exception:

1. Purpose, buildable outcome, objectives and prerequisites.
2. Concept order and definitions before use.
3. Context, prediction, execution and observation.
4. Complete examples, output and explanation.
5. Guided modification/TODO, hint and observable success.
6. Happy path, edge case, recoverable error, diagnosis and recovery.
7. Common errors described without blame.
8. Explained solutions, not code alone.
9. Checkpoint/rubric, summary and reflection.
10. Safety, compatibility and scope warnings.
11. Navigation, selector, accessibility and textual visual equivalents.
12. Stable APIs, identifiers, commands, paths, test data and source refs.

Idiomatic reordering is welcome when dependencies and outcomes remain intact.
Matching word, heading or fence counts does not prove any item above.

## Technical and linguistic evidence

Run after every batch:

```sh illustrative
python -B tools/parity_review.py --write
python -B tools/validate_book.py --changed-from <review-base>
python -B -m unittest discover -s tools/tests -v
git diff --check
```

Once the draft and shared validator are clean, the maintainer may run
`python -B tools/parity_review.py --record-automated`. That command promotes
only eligible `drafted` records: a localized diagnostic blocks that variant, a
canonical or companion diagnostic blocks all four siblings in the unit, and a
root/config/tooling diagnostic blocks the entire promotion run. It cannot set
either human review or `accepted`. Run it as a separate command after
`--reconcile-drafts`; mutation actions are mutually exclusive so one invocation
cannot hide the review-reset step inside automated promotion. Promotion uses
the same effective baseline result as the generic CLI: exact reviewed legacy
debt remains informational, while a new failure or stale baseline fingerprint
blocks evidence recording.

The linguistic reviewer checks naturalness, age-appropriate vocabulary,
non-blaming tone and semantic coverage. The technical/pedagogical reviewer
executes or traces the examples, checks prerequisite order and confirms that
errors, recovery, safety and assessment still teach the canonical outcome.

## Arabic bidi checklist

- Exactly one outer `<div dir="rtl">` encloses the document.
- Code fences, inline code, commands, URLs, paths, APIs, filenames, outputs and
  traces remain LTR and copy without invisible directional characters.
- The selector is inside the wrapper and keeps the standard language order.
- A person inspects rendered reading order and copies representative commands;
  the parser validates only structure.

## Acceptance

A record becomes `accepted` only when the canonical/localized digests are
current, all twelve dimensions are `pass` or doubly approved exceptions, both
review roles have `approved` plus a review date, automated signals pass, and no
baseline debt was added or broadened. The aggregate validator rejects an
`accepted` record that lacks those fields; partitioning or round-trip success
never supplies a human field.
