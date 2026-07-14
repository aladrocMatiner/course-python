# partitioned-parity-evidence Specification

## Purpose
TBD - created by archiving change partition-parity-evidence-by-unit. Update Purpose after archive.
## Requirements
### Requirement: Parity evidence is partitioned by canonical source and locale
The repository SHALL use schema-v2 `tools/parity_manifest.json` as a compact topology index, exactly 27 canonical files at `tools/parity/sources/<unit>.json`, and exactly 108 locale files at `tools/parity/records/<unit>/<locale>.json` for `es`, `ca`, `sv`, and `ar`. Unit and locale paths MUST be derived, repository-relative, safe, and equal to the discovered publication scope.

#### Scenario: Complete partition loads
- **WHEN** the index, 27 source files, and 108 locale files match their schemas and current Markdown digests
- **THEN** the loader produces one deterministic aggregate with 27 sources and 108 records

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

### Requirement: Migration and rollback preserve complete evidence
The CLI SHALL provide an explicit migration from a valid schema-v1 monolith to the partitioned store and an explicit export back to the canonical schema-v1 representation. Both directions MUST preserve every object key and value, ordering contract, Unicode value, digest, state, signal, gap, priority, command, exception, and human-review field without inference.

#### Scenario: Current monolith round-trips exactly
- **WHEN** the valid 27-source/108-record schema-v1 manifest is migrated, loaded, and exported
- **THEN** its canonical schema-v1 bytes are identical to the pre-migration bytes
- **AND** all 27 audits and 108 localized statuses/review objects are unchanged

#### Scenario: Migration validates before publication
- **WHEN** migration is requested
- **THEN** the tool stages the complete store inside the repository, reloads/validates it through the production path, compares it to the source aggregate, and only then publishes the store and index

#### Scenario: Atomic directory publication is unavailable
- **WHEN** the host lacks the tested Linux no-replace directory rename primitive
- **THEN** migration exits non-zero before publishing the store or index and leaves the schema-v1 monolith authoritative

#### Scenario: Migration failure is recoverable
- **WHEN** staging, serialization, comparison, or index publication fails
- **THEN** the schema-v1 manifest remains authoritative or a previously published exact store is detected safely
- **AND** a retry either completes the same lossless migration or refuses conflicting files without overwriting them

#### Scenario: Legacy evidence changes during migration
- **WHEN** a reviewer changes the schema-v1 manifest after staging began but before store/index publication
- **THEN** migration detects the source-byte mismatch, preserves the edited monolith as authoritative, and does not publish a stale index

#### Scenario: Invalid legacy input is not migrated
- **WHEN** the schema-v1 monolith is stale, incomplete, malformed, already partitioned, or contains an invalid accepted record
- **THEN** migration exits non-zero before publishing the schema-v2 index

#### Scenario: Rollback is explicit
- **WHEN** a maintainer requests monolithic export to a safe repository path
- **THEN** the tool writes an atomically validated schema-v1 file without replacing the live index or deleting partition files
- **AND** the maintainer can review byte equality before a separate rollback edit

### Requirement: Existing review commands operate on one aggregate contract
`tools/parity_review.py` SHALL preserve its default validation, `--write`, `--reconcile-drafts`, `--record-automated`, `--manifest`, and `--require-accepted` semantics while loading schema-v2 partitions into the existing aggregate validation/transition model. A normal invocation MUST remain read-only.

#### Scenario: Read-only validation changes nothing
- **WHEN** the default command validates a current partitioned store
- **THEN** it exits `0`, reports the 27/108 inventory, and every repository file remains byte-identical

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
- **THEN** it reports 27 pending canonical audits and 108 pending localized reviews and exits non-zero

#### Scenario: Structurally complete files are not semantic proof
- **WHEN** all partition files and automated signals validate
- **THEN** output describes storage/automated evidence only and never calls translations, accessibility, bidi, pedagogy, source, ownership, or license decisions approved

#### Scenario: Existing accepted fixture stays strict
- **WHEN** an accepted test fixture loses a source audit, dimension, dual exception approval, human role/date, current digest, or required automated command
- **THEN** aggregate validation rejects it identically before and after partitioning

### Requirement: Aggregate ordering and diagnostics are deterministic
The loader and exporter SHALL order units by the validated index and locales as `es`, `ca`, `sv`, `ar`, use canonical JSON encoding, and emit only repository-relative, non-secret diagnostics. Filesystem enumeration order MUST NOT affect aggregate bytes or messages.

#### Scenario: Enumeration order changes
- **WHEN** the same valid partition files are returned in different filesystem orders
- **THEN** aggregate JSON, exported monolith, counters, and diagnostics remain byte-identical

#### Scenario: Unicode and Arabic evidence round-trip
- **WHEN** notes or gaps contain valid non-ASCII or Arabic text
- **THEN** migration/export preserves the exact Unicode content and does not insert directional controls or escaped replacement text

#### Scenario: Failure contains sensitive-looking data
- **WHEN** malformed evidence contains an absolute path or token-like value
- **THEN** the diagnostic identifies the stable file/rule with unsafe values redacted and does not echo the secret-looking content

### Requirement: Active change coordination remains truthful
The reviewer guide and active parity/quality change artifacts SHALL describe `tools/parity_manifest.json` as the index and `tools/parity/` as authoritative granular evidence while retaining their existing review ownership and unchecked human tasks.

#### Scenario: Documentation is reconciled
- **WHEN** maintainers follow the active multilingual workflow after migration
- **THEN** the same CLI commands operate on the partition store and the guide explains locale-local diffs, migration/export, and recovery

#### Scenario: Storage migration does not complete editorial tasks
- **WHEN** strict OpenSpec validation runs after documentation reconciliation
- **THEN** no canonical audit, localized review wave, accessibility/bidi review, provenance review, or human sign-off checkbox is marked complete because of storage work
