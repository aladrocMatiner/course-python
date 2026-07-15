## MODIFIED Requirements

### Requirement: Parity evidence is partitioned by canonical source and locale

The repository SHALL use schema-v2 `tools/parity_manifest.json` as a compact topology index, exactly 30 canonical files at `tools/parity/sources/<unit>.json`, and exactly 120 locale files at `tools/parity/records/<unit>/<locale>.json` for `es`, `ca`, `sv`, and `ar`. Unit and locale paths MUST be derived, repository-relative, safe, and equal to the discovered publication scope of Chapters 01–28 plus two appendices.

#### Scenario: Complete partition loads

- **WHEN** the index, 30 source files, and 120 locale files match their schemas and current Markdown digests
- **THEN** the loader produces one deterministic aggregate with 30 sources and 120 records

#### Scenario: Additive topology expansion preserves evidence

- **WHEN** a valid 27-source/108-locale schema-v2 store is explicitly reconciled after all five siblings of Chapters 26–28 are published
- **THEN** exactly three source leaves and twelve locale leaves are added with pending human gates
- **AND** compatible human fields for unrelated existing leaves remain byte-identical while changed Chapters 1, 2, and 7 invalidate only their bound evidence

#### Scenario: Missing, extra, or duplicate evidence fails

- **WHEN** a source/record is omitted, duplicated, misnamed, placed under an undeclared unit/locale, or an extra JSON file exists in the store
- **THEN** read-only validation fails with a stable relative diagnostic and never silently drops or adopts evidence
- **AND** restoring the exact topology makes the next validation succeed

#### Scenario: Store path is unsafe

- **WHEN** an index/store/output path is absolute, traverses the repository, resolves through an escaping symlink, or uses an unsafe unit/locale identifier
- **THEN** validation exits non-zero before reading or writing the external target

#### Scenario: Index remains stable during ordinary review

- **WHEN** a reviewer changes evidence for one existing locale without changing publication topology
- **THEN** the index and every unrelated source/locale file remain byte-identical

### Requirement: Existing review commands operate on one aggregate contract

`tools/parity_review.py` SHALL preserve its default validation, `--write`, `--reconcile-drafts`, `--record-automated`, `--manifest`, and `--require-accepted` semantics while loading schema-v2 partitions into the existing aggregate validation/transition model. A normal invocation MUST remain read-only.

#### Scenario: Read-only validation changes nothing

- **WHEN** the default command validates a current partitioned store
- **THEN** it exits `0`, reports the 30/120 inventory, and every repository file remains byte-identical

#### Scenario: One localized digest changes

- **WHEN** exactly one localized Markdown digest changes and reconciliation is explicitly requested
- **THEN** only that locale record is reset to `drafted` with old contract/exceptions/commands/reviews cleared
- **AND** its source, three sibling locales, index, and all other evidence files remain byte-identical

#### Scenario: One canonical digest changes

- **WHEN** exactly one canonical Markdown digest changes and reconciliation is explicitly requested
- **THEN** only that source audit returns to `pending-human-review` and its four locale records reset against the new canonical digest
- **AND** evidence for every other unit remains byte-identical

#### Scenario: Automated promotion remains scoped

- **WHEN** `--record-automated` runs on eligible drafted records
- **THEN** only records with passing effective generic evidence advance to `automated-signals-pass`
- **AND** canonical/unit/global blockers retain the existing fail-closed scope and no human field is changed

#### Scenario: Atomic record write is interrupted

- **WHEN** a same-directory temporary write or replace fails
- **THEN** the prior target file remains valid or the full store fails validation visibly
- **AND** rerunning the same explicit operation completes deterministically without treating partial state as accepted

#### Scenario: Stale writer meets concurrent reviewer edit

- **WHEN** a planned partition update on Linux exchanges a target whose bytes no longer match the aggregate it loaded
- **THEN** exchange validation restores the reviewer bytes, rejects the stale write, and retains recovery evidence if rollback itself cannot be proved
- **AND** reloading and deliberately reconciling the current evidence provides the recovery path

#### Scenario: Portable writers cooperate through a lock

- **WHEN** a host lacks Linux atomic exchange and two parity CLI mutators target the same evidence
- **THEN** a hardened per-user/per-target lock serializes them and the stale operation rejects the bytes written by the first
- **AND** guidance states that an out-of-band editor which ignores that lock must not overlap a mutating parity command

### Requirement: Human acceptance authority is unchanged

Partition storage and migration SHALL NOT approve a canonical audit, semantic dimension, exception, linguistic review, technical review, rendered-accessibility/bidi review, or provenance decision. An `accepted` record MUST continue to require current digests, an approved canonical audit, all twelve dimensions passed/dually approved, both human review roles/dates, and the required automated commands.

#### Scenario: Migration cannot create approval

- **WHEN** pending or `automated-signals-pass` evidence is migrated, exported, reconciled, or validated
- **THEN** its audit/status/contract/review values remain pending or unchanged and no role/date/note is synthesized

#### Scenario: Publication gate still fails honestly

- **WHEN** `--require-accepted` runs against the migrated current repository
- **THEN** it reports 30 pending canonical source reviews, 120 pending localized reviews, and the pending root publication packet and exits non-zero

#### Scenario: Structurally complete files are not semantic proof

- **WHEN** all partition files and automated signals validate
- **THEN** output describes storage/automated evidence only and never calls translations, accessibility, bidi, pedagogy, source, ownership, or license decisions approved

#### Scenario: Existing accepted fixture stays strict

- **WHEN** an accepted test fixture loses a source audit, dimension, dual exception approval, human role/date, current digest, or required automated command
- **THEN** aggregate validation rejects it identically before and after partitioning
