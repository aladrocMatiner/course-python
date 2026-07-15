# Multilingual parity review guide

`tools/parity_manifest.json` is the compact topology index for chapters 01–28
and both appendices. Authoritative mutable evidence is isolated under
`tools/parity/sources/<unit>.json` for 30 frozen English sources and
`tools/parity/records/<unit>/<locale>.json` for 120 localized records. Counts
are triage signals, never acceptance evidence. Evidence schema 2 also owns
`tools/parity/root-publication.json` for the six root indexes. The external
`tools/publication_signoff.json` consumes current unit/root/provenance evidence
later; it is deliberately outside the parity store and never participates in
an upstream leaf digest.

Source and locale leaves retain path-scoped, derived provenance bindings as
`{id, status, provenance_sha256, covered_paths}`. Canonical pages and companions
bind the source leaf; an entry covering a localized page binds only that locale
leaf. `ATTRIBUTIONS.toml` remains the sole authority for the human provenance
decision. A covered-byte or entry change therefore makes the affected binding
stale without copying or fabricating a legal conclusion.

Normal validation is read-only. A reviewer edits only the source or locale file
owned by the current batch; ordinary review does not regenerate the index or a
checked-in monolithic aggregate. Missing, extra, duplicate, stale, partial, or
escaping evidence fails closed.

## Storage migration, export and rollback evidence

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

The independent human-review schema migration upgrades the complete 135-leaf
schema-1 store to 136 schema-2 leaves, including the root publication leaf:

```sh illustrative
python -B tools/parity_review.py --migrate-review-schema
python -B tools/parity_review.py
python -B tools/parity_review.py --export-review-bundle tools/parity-review-bundle.json
```

This second migration uses an unpredictable same-filesystem staging directory
and Linux `renameat2(RENAME_EXCHANGE)`. It validates the staged v2 store,
compares the original v1 snapshot immediately before exchange, reloads v2 and
retains v1 until post-publication validation succeeds. The comparison includes
the complete directory tree, so a concurrent extra file, directory or symlink
cannot be silently discarded. A failed reload restores v1 byte-for-byte. If
rollback itself cannot be proved, the diagnostic reports a repository-relative
recovery directory; final hygiene and migration retries remain blocked until a
maintainer resolves it.
A valid v2 store is an idempotent no-op; a mixed store fails before staging or
writing. `--export-monolith` remains lossless only for leaf schema 1 and rejects
v2 because the legacy format cannot represent root/render/bidi evidence.
`--export-review-bundle` is the lossless v2 export. Neither export is importable
or an approval authority.

The later publication-topology expansion is a separate explicit operation:

```sh illustrative
python -B tools/parity_review.py --reconcile-topology
python -B tools/parity_review.py
```

It permits only the additive 27-to-30 transition, preserves existing unit
leaves when their inputs are unchanged, and creates the three new canonical
reviews and twelve localized records with pending/inventoried—not approved—
evidence. It stages and validates all 151 schema-v2 leaves, exchanges the
complete store, updates the index with compare-and-swap, reloads production,
and rolls the index and store back byte-for-byte on a detected failure. A
second run is an idempotent no-op. Ordinary `--write` cannot change topology.

## Work in bounded batches

One review packet owns exactly one chapter or appendix. Edit only one or two
localized languages from that unit in a sub-wave. Record the current English
SHA-256 before editing. If that digest changes, stop and refresh the inventory;
the record is `stale` until reconciled.

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
automated command evidence and all digest-bound locale reviews because none of
that evidence applies to the new bytes. Progressed records whose inputs remain
current are left unchanged. A localized digest changes only its locale record;
a changed canonical source resets its canonical/render reviews and invalidates
its four locale records. A profile or declared asset change resets only the
dependent rendered-accessibility/bidi decisions. A changed canonical/companion
provenance binding marks progressed records in that unit stale; a localized-page
binding affects only that locale. Content reviews remain independent and
acceptance must be recorded explicitly again after provenance is resolved.
Unrelated evidence and the index remain byte-identical. The flag cannot set `accepted` or any human
approval, and it requires an existing index/store.

Use this progression:

```text illustrative
inventoried → source-frozen → drafted → automated-signals-pass
→ human-review-in-progress → accepted
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

## Review packets and evidence ownership

Generate a deterministic dossier without writing or creating a second
authority:

```sh illustrative
python -B tools/parity_review.py --review-packet chapter-01-introduction
python -B tools/parity_review.py --root-review-packet
```

A unit packet projects one source leaf, its four locale leaves in
`es/ca/sv/ar` order, the checked-in render profile and applicable references to
`ATTRIBUTIONS.toml`, including companion paths. The root packet projects the
six root pages, sixteen independent decision IDs, applicable global provenance
references, render assets and targets. Packet JSON uses `packet_schema_version`
and has no import command; annotations or copied output are disposable.

Authorities are unambiguous: source/locale/root decisions live in their owned
leaf, provenance decisions live only in `ATTRIBUTIONS.toml`, and the three
common publication decisions live only in `tools/publication_signoff.json`.
Verify the latter read-only with:

```sh illustrative
python -B tools/parity_review.py --verify-publication-signoff tools/publication_signoff.json
```

The verifier recomputes all 150 unit-leaf digests, unit companion provenance,
the root leaf and its sixteen decision digests, attribution/profile inputs and
the declared quality contract. It also requires all upstream page evidence to
be accepted. Pending, changes-requested or stale evidence exits non-zero; it
never rewrites either authority.

## Technical, linguistic and rendered evidence

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
any human review or `accepted`. Run it as a separate command after
`--reconcile-drafts`; mutation actions are mutually exclusive so one invocation
cannot hide the review-reset step inside automated promotion. Promotion uses
the same effective baseline result as the generic CLI: exact reviewed legacy
debt remains informational, while a new failure or stale baseline fingerprint
blocks evidence recording.

The linguistic reviewer checks naturalness, age-appropriate vocabulary,
non-blaming tone and semantic coverage. The technical/pedagogical reviewer
executes or traces the examples, checks prerequisite order and confirms that
errors, recovery, safety and assessment still teach the canonical outcome.
Separately, a competent accessibility reviewer inspects every page at
`320×568`, `1280×800` and 200% zoom/reflow with keyboard and applicable
assistive technology, recording the actual renderer/browser/OS/AT environment.
Arabic additionally receives a distinct rendered bidi/copy-paste decision.

## Arabic bidi checklist

- Exactly one outer `<div dir="rtl">` encloses the document.
- Code fences, inline code, commands, URLs, paths, APIs, filenames, outputs and
  traces remain LTR and copy without invisible directional characters.
- The selector is inside the wrapper and keeps the standard language order.
- A person inspects rendered reading order and copies representative commands;
  the parser validates only structure.

## Acceptance

A record becomes `accepted` only when canonical audit/render, all twelve
dimensions, linguistic, technical/pedagogical, localized render, applicable
Arabic bidi, provenance and automated evidence are current and approved. Every
human object records a role, date and notes. The root packet needs one shared
English audit, six renders, four linguistic reviews, four technical reviews and
one Arabic bidi review. The aggregate validator rejects incomplete acceptance;
partitioning, packet generation, structural success and round-trip evidence
never supply a human field. The `handoff` quality profile is expected to fail
at `publication-signoff` until those page decisions, all provenance entries and
the three common sign-offs are genuinely complete.
