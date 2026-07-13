# Multilingual parity review guide

`tools/parity_manifest.json` is the review queue for chapters 01–22 and both
historical appendices. It contains 24 frozen English sources and 96 localized
records. Counts are triage signals, never acceptance evidence.

## Work in bounded batches

Review at most two units and two localized languages in one batch. Record the
current English SHA-256 before editing. If that digest changes, stop and refresh
the inventory; the record is `stale` until reconciled.

Refreshing and reconciling are deliberately separate operations. First inspect
the stale inventory produced by `--write`. When the changed source and all four
localized files are ready for a new review cycle, explicitly run:

```sh illustrative
python -B tools/parity_review.py --reconcile-drafts
```

This refreshes current digests and changes only `stale` or `inventoried`
records to `drafted`. It clears their old twelve-dimension results, exceptions,
automated command evidence, review roles, dates and notes because none of that
evidence applies to the new digest. Progressed records whose digests are still
current are left unchanged. A changed canonical source also returns its source
audit to `pending-human-review`; an unchanged source keeps its audit. Review the
manifest diff before proceeding. The flag cannot set `accepted` or either human
approval, and it requires an existing manifest.

Use this progression:

```text illustrative
inventoried → source-frozen → drafted → automated-signals-pass
→ linguistic-reviewed → technical-reviewed → accepted
```

`blocked` records have a concrete correctness, safety, accessibility, bidi or
tooling failure. An intentional difference uses `exception` only with a narrow
justification and both linguistic and technical approval. Do not put learner
data, credentials, or unnecessary reviewer identity in the manifest; record a
role such as `fluent Arabic reviewer` or `Python technical reviewer`.

## Twelve-dimension checklist

For each localized record, mark every manifest contract dimension `pass`, or
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
only `drafted` records without path-level automated errors/warnings. It cannot
set either human review or `accepted`. Run it as a separate command after
`--reconcile-drafts`; mutation actions are mutually exclusive so one invocation
cannot hide the review-reset step inside automated promotion.

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
baseline debt was added or broadened. The manifest validator rejects an
`accepted` record that lacks those fields.
