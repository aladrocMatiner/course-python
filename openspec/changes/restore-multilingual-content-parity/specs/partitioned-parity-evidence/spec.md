# partitioned-parity-evidence Specification

## MODIFIED Requirements

### Requirement: Parity evidence is partitioned by canonical source and locale

The repository SHALL use schema-v2 `tools/parity_manifest.json` as a compact unit-topology index, exactly 27 leaf-schema-v2 canonical files at `tools/parity/sources/<unit>.json`, exactly 108 leaf-schema-v2 locale files at `tools/parity/records/<unit>/<locale>.json` for `es`, `ca`, `sv`, and `ar`, and exactly one leaf-schema-v2 file at `tools/parity/root-publication.json` for the six root indexes and their derived applicable-provenance references. Unit, locale, root, and provenance paths MUST be derived, repository-relative, safe, and equal to the discovered publication scope.

#### Scenario: Complete partition loads

- **WHEN** the index, 27 source files, 108 locale files, and root-publication leaf match their schemas and current Markdown digests
- **THEN** the loader produces one deterministic aggregate with 27 sources, 108 records, and one root-publication object covering six paths

#### Scenario: Missing, extra, or duplicate evidence fails

- **WHEN** a source/record/root leaf is omitted, duplicated, misnamed, placed under an undeclared unit/locale, or any other JSON file exists in the store
- **THEN** read-only validation fails with a stable relative diagnostic and never silently drops or adopts evidence
- **AND** restoring the exact 136-leaf topology makes the next validation succeed

#### Scenario: Store path is unsafe

- **WHEN** an index/store/output/root path is absolute, traverses the repository, resolves through an escaping symlink, or uses an unsafe unit/locale identifier
- **THEN** validation exits non-zero before reading or writing the external target

#### Scenario: Index remains stable during ordinary review

- **WHEN** a reviewer changes evidence for one existing source, locale, or root page without changing unit publication topology
- **THEN** the index and every unrelated leaf remain byte-identical

### Requirement: Migration and rollback preserve complete evidence

The CLI SHALL preserve its explicit lossless migration from a valid schema-v1 monolith to the 135-file leaf-schema-v1 partition and explicit export back to canonical schema-v1 while that legacy leaf schema remains active. It SHALL additionally provide `--migrate-review-schema` to migrate the complete partition from leaf schema 1 to leaf schema 2 plus the root-publication leaf and `--export-review-bundle <path>` to export every schema-v2 object losslessly. No command MAY squeeze schema-v2-only human evidence into the legacy monolith, discard fields, or infer approval.

#### Scenario: Current monolith round-trips exactly

- **WHEN** the valid 27-source/108-record schema-v1 manifest is migrated to leaf schema 1, loaded, and exported before review-schema migration
- **THEN** its canonical schema-v1 bytes are identical to the pre-migration bytes
- **AND** all 27 audits and 108 localized statuses/review objects are unchanged

#### Scenario: Legacy partition migration validates before publication

- **WHEN** monolith-to-partition migration is requested
- **THEN** the tool stages the complete legacy store, reloads/validates it through the production path, compares it to the source aggregate, and only then publishes the store and index

#### Scenario: Atomic legacy directory publication is unavailable

- **WHEN** the host lacks the tested Linux no-replace directory rename primitive
- **THEN** legacy migration exits non-zero before publishing the store or index and leaves the schema-v1 monolith authoritative

#### Scenario: Legacy migration failure is recoverable

- **WHEN** legacy staging, serialization, comparison, or index publication fails
- **THEN** the schema-v1 monolith remains authoritative or a previously published exact store is detected safely
- **AND** a retry either completes the same lossless migration or refuses conflicting files without overwriting them

#### Scenario: Legacy evidence changes during migration

- **WHEN** a reviewer changes the schema-v1 manifest after staging began but before store/index publication
- **THEN** migration detects the source-byte mismatch, preserves the edited monolith as authoritative, and does not publish a stale index

#### Scenario: Invalid legacy input is not migrated

- **WHEN** the schema-v1 monolith is stale, incomplete, malformed, already partitioned, or contains an invalid accepted record
- **THEN** migration exits non-zero before publishing the schema-v2 topology index

#### Scenario: Legacy rollback export remains explicit

- **WHEN** a maintainer requests monolithic export from a leaf-schema-v1 store to a safe repository path
- **THEN** the tool writes an atomically validated schema-v1 file without replacing the live index or deleting partition files
- **AND** the maintainer can review byte equality before a separate rollback edit

#### Scenario: Legacy export cannot represent review schema 2

- **WHEN** monolithic schema-v1 export is requested after `--migrate-review-schema` succeeds
- **THEN** the command exits non-zero before writing output and identifies that root/render/bidi evidence is not representable
- **AND** leaves all 136 schema-v2 leaves byte-identical

#### Scenario: Review bundle export preserves schema 2

- **WHEN** `--export-review-bundle <safe-path>` is requested from a valid 136-leaf schema-v2 store
- **THEN** it atomically writes canonical JSON containing the index, 27 source objects, 108 locale objects, and root-publication object without changing the live store
- **AND** repeated exports preserve every field, deterministic ordering, Unicode, and byte-identical output

#### Scenario: Human-review schema migration succeeds atomically

- **WHEN** all 135 leaves are valid schema 1, the root leaf is absent, and Linux `renameat2(RENAME_EXCHANGE)` is available
- **THEN** `--migrate-review-schema` stages and validates all 136 schema-v2 leaves, compare-and-swaps the complete store, reloads it, and only then removes the retained schema-v1 store
- **AND** preserves compatible fields, creates every new gate pending, downgrades incomplete legacy acceptance, and never fabricates role/date/notes

#### Scenario: Mixed-version review store fails without writes

- **WHEN** the live store mixes leaf versions or root topology inconsistent with those versions
- **THEN** migration aborts before staging/writing and preserves the mixed input byte for byte
- **AND** reports the conflicting repository-relative leaves without choosing a winner

#### Scenario: Human-review migration from valid v1 fails safely

- **WHEN** an entirely valid v1 source snapshot changes, staging/reload fails, or atomic exchange is unavailable
- **THEN** migration preserves or restores schema v1 byte for byte and reports failure
- **AND** a failed rollback preserves same-filesystem recovery evidence with its exact repository-relative path, blocks hygiene, and does not report success

#### Scenario: Human-review migration is retried

- **WHEN** `--migrate-review-schema` receives an entirely valid 136-leaf schema-v2 store
- **THEN** it succeeds as a no-op without rewriting a leaf or leaving a temporary repository artifact

### Requirement: Existing review commands operate on one aggregate contract

`tools/parity_review.py` SHALL preserve default validation, `--write`, `--reconcile-drafts`, `--record-automated`, `--manifest`, `--migrate-partitioned`, and `--require-accepted` semantics while loading the compatible partition version into one aggregate validation/transition model. It SHALL preserve `--export-monolith` for leaf schema 1, reject that legacy format for leaf schema 2, and add explicit `--migrate-review-schema`, `--export-review-bundle <path>`, `--review-packet <unit>`, `--root-review-packet`, and `--verify-publication-signoff <path>` operations; every normal validation, packet, or sign-off verification invocation MUST remain read-only.

#### Scenario: Read-only validation changes nothing

- **WHEN** the default command validates a current 136-leaf store
- **THEN** it exits `0`, reports the 27/108/root inventory, and every repository file remains byte-identical

#### Scenario: One localized digest changes

- **WHEN** exactly one localized Markdown digest changes and reconciliation is explicitly requested
- **THEN** only that locale record resets to `drafted`, with stale contract/exceptions/commands/human gates cleared or retained only where the versioned invalidation contract permits
- **AND** its source, three sibling locales, root leaf, index, and all other evidence files remain byte-identical

#### Scenario: One canonical digest changes

- **WHEN** exactly one canonical Markdown digest changes and reconciliation is explicitly requested
- **THEN** only that source's canonical/render reviews return to pending and its four locale records reset against the new canonical digest
- **AND** evidence for every other unit, the root leaf, and the index remain byte-identical

#### Scenario: One root digest changes

- **WHEN** exactly one root index digest changes and reconciliation is explicitly requested
- **THEN** only the dependent root-page decisions and aggregate root state become pending or stale according to the review-input contract
- **AND** all 135 unit leaves and the index remain byte-identical

#### Scenario: Automated promotion remains scoped

- **WHEN** `--record-automated` runs on eligible drafted records
- **THEN** only records with passing effective generic evidence advance to `automated-signals-pass`
- **AND** canonical/unit/root/global blockers retain their fail-closed scope and no human field is changed

#### Scenario: Review packets are deterministic and read-only

- **WHEN** a maintainer requests a valid unit or root packet
- **THEN** canonical JSON is emitted on stdout in stable order and no source, locale, root, index, attribution, or Markdown file changes
- **AND** unknown/unsafe input fails with a stable non-zero exit and repository-relative stderr diagnostic

#### Scenario: Publication sign-off verification is external and read-only

- **WHEN** `--verify-publication-signoff` receives a safe schema-valid consumer file
- **THEN** it recomputes index/unit-leaf/unit-companion-provenance/root/provenance/profile/quality-contract references and validates independent book-editor, accessibility, and provenance decisions against `signoff_input_sha256`
- **AND** missing/pending/stale evidence exits non-zero without writing the consumer, parity store, attribution inventory, profile, or narrative implementation review

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

Partition storage, migration, reconciliation, packet generation, sign-off verification, and automation SHALL NOT approve a canonical audit, semantic dimension, exception, linguistic review, technical/pedagogical review, rendered-accessibility review, bidi review, root review, provenance decision, or common sign-off. A localized `accepted` record MUST require current digests, approved canonical audit/render, all twelve semantic dimensions, linguistic/technical/render gates, applicable Arabic bidi, provenance, and required automated commands. The root leaf MUST require every applicable page/provenance gate before `accepted`; `tools/publication_signoff.json` consumes its decision digests later and is not part of any upstream leaf identity.

#### Scenario: Migration cannot create approval

- **WHEN** pending or `automated-signals-pass` evidence is migrated, exported, reconciled, validated, or projected
- **THEN** compatible existing values remain pending or unchanged and no result/role/date/note is synthesized

#### Scenario: Publication gate still fails honestly

- **WHEN** `--require-accepted` runs after schema migration but before competent review
- **THEN** it reports pending canonical/render, 108 localized human-gate, root-page, bidi, and applicable provenance evidence and exits non-zero
- **AND** it does not claim to validate the later external common sign-off

#### Scenario: Structurally complete files are not semantic proof

- **WHEN** all 136 leaves and automated signals validate
- **THEN** output describes storage/automated evidence only and never calls translations, accessibility, bidi, pedagogy, source, ownership, license, root review, or publication sign-off approved

#### Scenario: Accepted locale fixture stays strict

- **WHEN** an accepted locale fixture loses a canonical audit/render, semantic dimension, dual exception approval, applicable human result/role/date, current digest, provenance gate, or required automated command
- **THEN** aggregate validation rejects it

#### Scenario: Accepted root fixture stays strict

- **WHEN** an accepted root fixture loses mirror equality, a localized semantic gate, any of six rendered decisions, Arabic bidi, current digest, or provenance gate
- **THEN** aggregate validation rejects it

### Requirement: Aggregate ordering and diagnostics are deterministic

The loader and exporter SHALL order units by the validated index and locales as `es`, `ca`, `sv`, `ar`, order root paths as `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, `README.ar.md`, use canonical JSON encoding, and emit only repository-relative, non-secret diagnostics. Filesystem enumeration order MUST NOT affect aggregate or packet bytes or messages.

#### Scenario: Enumeration order changes

- **WHEN** the same valid partition files or attribution entries are returned in different filesystem orders
- **THEN** aggregate JSON, packet JSON, compatible legacy export, schema-v2 review-bundle export, counters, and diagnostics remain byte-identical

#### Scenario: Unicode and Arabic evidence round-trip

- **WHEN** notes or gaps contain valid non-ASCII or Arabic text
- **THEN** migration, compatible legacy export, schema-v2 review-bundle export, and packet projection preserve the exact Unicode content and do not insert directional controls or escaped replacement text

#### Scenario: Failure contains sensitive-looking data

- **WHEN** malformed evidence contains an absolute path or token-like value
- **THEN** the diagnostic identifies the stable file/rule with unsafe values redacted and does not echo the secret-looking content

### Requirement: Active change coordination remains truthful

The reviewer guide and active parity/quality change artifacts SHALL describe `tools/parity_manifest.json` as the unit index, `tools/parity/` as authoritative granular page evidence including `root-publication.json`, and `tools/publication_signoff.json` as the separate unidirectional common-sign-off authority, while retaining independent review ownership and unchecked human tasks.

#### Scenario: Documentation is reconciled

- **WHEN** maintainers follow the active multilingual workflow after review-schema migration
- **THEN** the same CLI commands operate on the partition store and the guide explains locale/root-local diffs, both migrations, both compatible exports, packet projection, sign-off verification, and recovery

#### Scenario: Storage migration does not complete editorial tasks

- **WHEN** strict OpenSpec validation runs after documentation reconciliation
- **THEN** no canonical audit, localized review wave, root review, accessibility/bidi review, provenance review, or human sign-off checkbox is marked complete because of storage work
