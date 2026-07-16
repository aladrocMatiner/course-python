## MODIFIED Requirements

### Requirement: Parity evidence is partitioned by canonical source and locale
The repository SHALL use schema-v2 `tools/parity_manifest.json` as a compact
unit-topology index, exactly 33 leaf-schema-v2 canonical files at
`tools/parity/sources/<unit>.json`, exactly 132 leaf-schema-v2 locale files at
`tools/parity/records/<unit>/<locale>.json` for `es`, `ca`, `sv`, and `ar`, and
exactly one leaf-schema-v2 `tools/parity/root-publication.json` for the six root
indexes and their derived applicable-provenance references. Unit, locale, root,
and provenance paths MUST be derived, repository-relative, safe, and equal to
the discovered publication scope. Physical publication paths MAY differ from a
safe logical unit ID only through a closed validated mapping. Appendix C's root
page and all nested pages declared by its closed catalogue SHALL contribute to
one deterministic aggregate digest per language under logical ID
`appendix-software-design-patterns`; nested pages SHALL NOT create additional
unit leaves.

#### Scenario: Mapped Appendix C digest covers nested pages
- **WHEN** the physical `zz_Appendix C Software Design Patterns` tree is reconciled under logical ID `appendix-software-design-patterns`
- **THEN** its source and locale digests include the root page plus every catalogue-declared nested page in deterministic relative-path order
- **AND** changing, adding, removing, or renaming a nested page invalidates only Appendix C evidence and cannot silently preserve the former digest

#### Scenario: Complete partition loads
- **WHEN** the index, 33 source files, 132 locale files, and root-publication leaf match their schemas and current Markdown digests
- **THEN** the loader produces one deterministic aggregate with 33 sources, 132 records, and one root-publication object covering six paths

#### Scenario: Core 27/108 to 30/120 expansion remains lossless
- **WHEN** a valid 27-source/108-locale/root schema-v2 store is explicitly reconciled after all five siblings of Chapters 26–28 are published
- **THEN** exactly three source leaves and twelve locale leaves are added with pending human gates
- **AND** compatible human fields for unrelated existing leaves remain byte-identical, changed Chapters 1, 2, and 7 invalidate only their bound unit/locale evidence, and changed root indexes invalidate only their dependent root decisions

#### Scenario: Environment 30/120 to 32/128 expansion remains lossless
- **WHEN** a valid reviewed 30-source/120-locale/root store is explicitly reconciled after all five siblings and owned checks for Chapters 29–30 are published
- **THEN** exactly two source leaves and eight locale leaves are added with pending human gates
- **AND** only evidence bound to the changed Chapters 1, 15, 16, and 19 plus changed root inputs is invalidated while every compatible unrelated leaf remains byte-identical

#### Scenario: Appendix C starts from both reviewed expansions
- **WHEN** Appendix C topology reconciliation is requested
- **THEN** its only supported source state is the valid implemented 32/128/root result produced after both prior additive expansions
- **AND** it never bypasses, relabels, or reconstructs either transition from counts alone

#### Scenario: Missing, extra, or duplicate evidence fails
- **WHEN** a source/record/root leaf is omitted, duplicated, misnamed, placed under an undeclared unit/locale, or any other JSON file exists in the store
- **THEN** read-only validation fails with a stable relative diagnostic and never silently drops or adopts evidence
- **AND** restoring the exact 166-leaf topology makes the next validation succeed

#### Scenario: Store path is unsafe
- **WHEN** an index/store/output/root path is absolute, traverses the repository, resolves through an escaping symlink, or uses an unsafe unit/locale identifier
- **THEN** validation exits non-zero before reading or writing the external target

#### Scenario: Index remains stable during ordinary review
- **WHEN** a reviewer changes evidence for one existing source, locale, or root page without changing unit publication topology
- **THEN** the index and every unrelated leaf remain byte-identical

### Requirement: Existing review commands operate on one aggregate contract
`tools/parity_review.py` SHALL preserve default validation, `--write`,
`--reconcile-drafts`, `--record-automated`, `--manifest`,
`--migrate-partitioned`, and `--require-accepted` semantics while loading the
compatible partition version into one aggregate validation/transition model. It
SHALL preserve `--export-monolith` for leaf schema 1, reject that legacy format
for leaf schema 2, and preserve explicit `--migrate-review-schema`,
`--export-review-bundle <path>`, `--review-packet <unit>`,
`--root-review-packet`, and `--verify-publication-signoff <path>` operations;
every normal validation, packet, or sign-off verification invocation MUST remain
read-only.

#### Scenario: Read-only validation changes nothing
- **WHEN** the default command validates a current 166-leaf store
- **THEN** it exits `0`, reports the 33/132/root inventory, and every repository file remains byte-identical

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
- **AND** all 165 unit leaves and the index remain byte-identical

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
Partition storage, migration, reconciliation, packet generation, sign-off
verification, and automation SHALL NOT approve a canonical audit, semantic
dimension, exception, linguistic review, technical/pedagogical review,
rendered-accessibility review, bidi review, root review, provenance decision, or
common sign-off. A localized `accepted` record MUST require current digests,
approved canonical audit/render, all twelve semantic dimensions,
linguistic/technical/render gates, applicable Arabic bidi, provenance, and
required automated commands. The root leaf MUST require every applicable
page/provenance gate before `accepted`; `tools/publication_signoff.json` consumes
its decision digests later and is not part of any upstream leaf identity.

#### Scenario: Migration cannot create approval
- **WHEN** pending or `automated-signals-pass` evidence is migrated, exported, reconciled, validated, or projected
- **THEN** compatible existing values remain pending or unchanged and no result/role/date/note is synthesized

#### Scenario: Publication gate still fails honestly
- **WHEN** `--require-accepted` runs against the 33/132/root store before competent review
- **THEN** it reports pending canonical/render, 132 localized human-gate, root-page, bidi, and applicable provenance evidence and exits non-zero
- **AND** it does not claim to validate the later external common sign-off

#### Scenario: Structurally complete files are not semantic proof
- **WHEN** all 166 leaves and automated signals validate
- **THEN** output describes storage/automated evidence only and never calls translations, accessibility, bidi, pedagogy, source, ownership, license, root review, or publication sign-off approved

#### Scenario: Accepted locale fixture stays strict
- **WHEN** an accepted locale fixture loses a canonical audit/render, semantic dimension, dual exception approval, applicable human result/role/date, current digest, provenance gate, or required automated command
- **THEN** aggregate validation rejects it

#### Scenario: Accepted root fixture stays strict
- **WHEN** an accepted root fixture loses mirror equality, a localized semantic gate, any of six rendered decisions, Arabic bidi, current digest, or provenance gate
- **THEN** aggregate validation rejects it

## ADDED Requirements

### Requirement: Appendix C topology reconciliation is explicit and additive
The parity CLI SHALL support one explicit authorized transition from the
currently implemented 32 canonical/128 localized/root topology to 33/132/root
after all five Appendix C pages and owned checks exist. It MUST preserve
unrelated source/locale evidence byte-for-byte, create only the Appendix C
source plus four locale leaves as pending, preserve the root leaf while its six
Markdown digests are unchanged, invalidate the external publication-signoff
consumer bound to the changed topology, and never infer a review result. Root
leaf decisions SHALL be reconciled only after the six root indexes change.

#### Scenario: Authorized 32/128 to 33/132 transition succeeds
- **WHEN** the current 32/128/root store is valid, all five Appendix C pages/checks exist, no mutating parity command overlaps, and the maintainer explicitly authorized the shown transition
- **THEN** reconciliation stages, validates, and publishes exactly one new source plus four locale leaves and an updated deterministic index
- **AND** every unrelated evidence leaf including the unchanged root leaf remains byte-identical, new human fields are pending/empty, and the external publication-signoff consumer becomes stale or pending rather than approved

#### Scenario: Scaffold or owned check is incomplete
- **WHEN** Appendix C lacks canonical English, any localized sibling, or either registered `patterns:*` check
- **THEN** reconciliation fails before changing the 32/128/root store and names only the missing repository-relative target/check
- **AND** completing every required input permits a later explicit transition

#### Scenario: Reconciliation is repeated
- **WHEN** the valid 33/132/root store already covers Appendix C and the same explicit topology command is run again
- **THEN** it reports an idempotent no-op and every parity/publication input remains byte-identical

#### Scenario: Unsupported topology jump is proposed
- **WHEN** the discovered tree or index would jump from any count other than the exact supported 32/128 source state to 33/132, omit a locale, or adopt more than Appendix C
- **THEN** reconciliation fails closed before publication
- **AND** no partial leaf, reviewer evidence, root state, or rewritten index is retained
