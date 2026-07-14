## ADDED Requirements

### Requirement: Complete published-course parity inventory

The course SHALL maintain a review inventory for the 25 published chapters and two published appendices, treating each unit `README.md` as canonical English and tracking its Spanish, Catalan, Swedish, and Arabic variants independently.

#### Scenario: Inventory covers the implemented course

- **WHEN** the parity inventory is generated
- **THEN** it contains exactly 27 canonical units and 108 localized unit-language records
- **AND** every record identifies an existing stable path without renaming a directory

#### Scenario: Newly published advanced chapters enter without inherited approval

- **WHEN** chapters 23, 24, and 25 have all five published documents and domain implementation evidence
- **THEN** the parity inventory includes their canonical sources and twelve localized records
- **AND** their source audits and human reviews remain pending until explicitly completed

#### Scenario: Missing localized document blocks completion

- **WHEN** any of the four required localized siblings is absent for an in-scope unit
- **THEN** its record is blocked
- **AND** the course cannot declare the 27-unit parity restoration complete

### Requirement: One authoritative review packet per unit

The review system SHALL close each chapter or appendix through one unit packet derived read-only from its canonical source leaf, four locale leaves, applicable attribution entries, automated evidence, and rendered-review targets; the packet MUST NOT become a second editable evidence authority.

#### Scenario: Reviewer opens a unit packet

- **WHEN** a maintainer requests a packet for one published unit
- **THEN** it contains exactly the current canonical source, records for `es`, `ca`, `sv`, and `ar`, applicable `ATTRIBUTIONS.toml` entries, and deterministic validation/render targets
- **AND** every item identifies the digest and authoritative repository-relative evidence path from which it was derived

#### Scenario: Packet output is retained outside the evidence store

- **WHEN** a reviewer annotates or copies a generated packet
- **THEN** normal parity validation does not import that output or infer a decision from it
- **AND** human results become authoritative only after a maintainer records them in the owned source or locale leaf

#### Scenario: Human-review schema is upgraded

- **WHEN** `--migrate-review-schema` receives an entirely schema-v1 store and Linux `renameat2(RENAME_EXCHANGE)` is available
- **THEN** it stages and validates evidence schema 2 / leaf schema 2 for all 27 sources, 108 locales, and one new root-publication leaf, compare-and-swaps all 136 leaves, reloads them, and reports the affected repository-relative leaves
- **AND** `source.audit` maps to `canonical_review`, but a legacy approval without valid role/date becomes pending; every source rendered review and every root-page gate starts pending
- **AND** existing schema-valid linguistic and technical evidence is preserved only when both content digests remain current; locale rendered reviews and Arabic bidi reviews start pending
- **AND** `linguistic-reviewed`, `technical-reviewed`, and any incomplete legacy `accepted` map to `human-review-in-progress`
- **AND** no formerly accepted record remains accepted until the newly required reviews are genuinely approved

#### Scenario: Review-schema migration is retried

- **WHEN** `--migrate-review-schema` receives an entirely valid schema-v2 store
- **THEN** it exits successfully without rewriting any leaf
- **AND** produces the same validated inventory and no temporary repository artifact

#### Scenario: Review-schema migration cannot publish safely

- **WHEN** the live store contains any mixture of leaf schema 1, leaf schema 2, or a root leaf inconsistent with the other leaves
- **THEN** migration fails before staging or writing and preserves every mixed input path byte for byte
- **AND** identifies the version mismatch without guessing which version should win

#### Scenario: Valid-v1 review migration cannot publish safely

- **WHEN** an entirely valid v1 input changes after the snapshot, staging validation fails, or Linux `renameat2(RENAME_EXCHANGE)` is unavailable
- **THEN** migration fails before replacing the live store and preserves schema v1 byte for byte
- **AND** removes its same-filesystem sibling staging or reports a bounded repository-relative recovery action without guessing or importing human approval

#### Scenario: Reload after atomic exchange fails

- **WHEN** the complete v2 store has been exchanged into place but reload or post-publication validation fails
- **THEN** migration exchanges the retained v1 store back into place and verifies that rollback before reporting failure
- **AND** if rollback itself fails, it preserves the same-filesystem recovery store, reports its exact repository-relative path, blocks hygiene, and never reports a successful migration

#### Scenario: Schema-v2 review evidence is exported losslessly

- **WHEN** a maintainer requests `--export-review-bundle <safe-path>` from a valid 136-leaf v2 store
- **THEN** the command writes canonical JSON containing the index, 27 source objects, 108 locale objects, and root-publication object without modifying live evidence
- **AND** repeated export preserves deterministic ordering, Unicode, every object key/value, and byte-identical output

#### Scenario: Legacy monolith export cannot represent schema v2

- **WHEN** `--export-monolith <safe-path>` is requested from a leaf-schema-v2 store
- **THEN** it exits non-zero before creating or replacing output and explains that root/render/bidi evidence is not representable in schema 1
- **AND** directs the maintainer to `--export-review-bundle` without deleting or rewriting live evidence

### Requirement: One authoritative root publication packet

The review system SHALL maintain one root-publication leaf and derive one read-only packet for the six root indexes, without storing root decisions in unit leaves or duplicating the common quality sign-off.

#### Scenario: Maintainer opens the root packet

- **WHEN** a maintainer requests the root publication packet
- **THEN** it contains exactly `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md`, their current digests, render targets, applicable human gates, and derived references/digests for global provenance that covers them
- **AND** every result identifies `tools/parity/root-publication.json` as its evidence authority and the packet cannot be imported as approval

#### Scenario: Root indexes receive human review

- **WHEN** the root publication packet is prepared for acceptance
- **THEN** `README.md` has a canonical audit shared only with its byte-identical English mirror, all six paths have independent rendered-accessibility results, and the four localized indexes have linguistic and technical/pedagogical results
- **AND** `README.ar.md` additionally has a separate bidi/copy-paste result
- **AND** every decision records result, role, date, notes, page/profile/render-input digests, and no automated signal supplies those human fields

#### Scenario: Root page or review input changes

- **WHEN** a root page, declared rendering asset, or render profile changes after approval
- **THEN** only the dependent root decisions become stale and global publication acceptance fails
- **AND** no unit source or locale decision is invalidated unless its own referenced input also changed

#### Scenario: Common sign-off consumes root evidence

- **WHEN** `add-book-quality-gates` completes its accessibility/provenance sign-off
- **THEN** it references the current root leaf and decision digests rather than copying or inferring approval
- **AND** the sign-off digest is not stored in or used to invalidate the root leaf
- **AND** this parity change remains globally pending while that sign-off, its provenance audit, or its clean acceptance matrix is incomplete

#### Scenario: Root packet derives applicable provenance

- **WHEN** an attribution entry covers a root index or a local asset/license target referenced from a root index
- **THEN** the root leaf and packet contain a path-safe derived `{id, status, provenance_sha256, covered_paths}` reference ordered by ID
- **AND** an unresolved or changed reference blocks root acceptance without copying the provenance decision or depending on the later sign-off

### Requirement: Publication sign-off is a verifiable unidirectional consumer

The course SHALL persist the common publication sign-off at `tools/publication_signoff.json` outside the parity store. It SHALL reference current unit, root, attribution, and render-profile evidence, SHALL NOT be included in any upstream leaf digest, and SHALL remain a distinct human authority owned by the common book-quality handoff.

#### Scenario: Pending sign-off template is prepared

- **WHEN** schema-v2 review evidence is first implemented
- **THEN** the checked-in sign-off file records schema 1, current input references/digests, and pending book-editor, accessibility, and provenance review objects
- **AND** creating or refreshing that pending template does not approve a review, change a parity leaf, or complete a human task

#### Scenario: Sign-off inputs are derived

- **WHEN** the sign-off evidence binding is calculated
- **THEN** `inputs` contains the parity-index digest, canonical digest of the path-sorted 135 unit-leaf digests, `unit_provenance_sha256` over all `(unit, entry)` derived provenance refs including companion paths, root-leaf digest plus ID-sorted root decision digests, raw `ATTRIBUTIONS.toml` digest, render-profile digest, and `quality_contract_sha256` over the declared path-sorted validator/config contract
- **AND** `signoff_input_sha256` is the SHA-256 of canonical JSON for exactly that inputs object

#### Scenario: Root decision references are stable

- **WHEN** a root human gate is included in sign-off inputs
- **THEN** its ID is `root:<path>:<gate>` and its digest hashes canonical JSON containing that ID, repository-relative path, and complete review object
- **AND** the shared English canonical audit uses one ID bound to both byte-identical English digests rather than a duplicated decision

#### Scenario: Competent reviewers approve publication sign-off

- **WHEN** the book editor/professor, accessibility reviewer, and provenance owner supply decisions
- **THEN** their independent objects record `approved`, non-empty role, review date, notes, and the current `signoff_input_sha256`
- **AND** aggregate sign-off state is derived as `approved` only when all three pass and no input is stale

#### Scenario: Upstream evidence changes after sign-off

- **WHEN** the parity index, any referenced unit leaf, root leaf/decision, attribution inventory, render profile, or declared quality-contract file changes
- **THEN** read-only verification reports the sign-off `stale` and publication fails
- **AND** no upstream evidence is rewritten or invalidated by the consumer's own digest

#### Scenario: Companion provenance evidence changes after sign-off

- **WHEN** bytes change only in a companion path covered by a unit attribution entry while Markdown leaves and `ATTRIBUTIONS.toml` remain unchanged
- **THEN** the recomputed unit `provenance_sha256` changes, `unit_provenance_sha256` differs, and sign-off verification reports `stale`
- **AND** no page review is silently approved against the changed companion evidence

#### Scenario: Sign-off is verified for handoff

- **WHEN** `python -B tools/parity_review.py --verify-publication-signoff tools/publication_signoff.json` or the `handoff` quality profile runs
- **THEN** it recomputes every reference, validates all three human decisions, and exits non-zero for missing, pending, changes-requested, malformed, or stale evidence
- **AND** normal verification is read-only and emits only safe repository-relative diagnostics

#### Scenario: Narrative implementation review references sign-off

- **WHEN** `add-book-quality-gates` completes its Tasks 4.3, 7.1, and 7.2
- **THEN** `tools/BOOK_QUALITY_REVIEW.md` and its implementation review record the current `tools/publication_signoff.json` digest and point to that authority instead of copying root/unit decisions
- **AND** neither narrative-review digest is an input to the sign-off file

### Requirement: Frozen canonical source per review packet

Each unit-language review SHALL record a digest of the exact canonical `README.md` revision used; each source leaf SHALL record an independent canonical audit and rendered-accessibility review with result, role, review date, and notes; and a changed canonical digest SHALL invalidate those decisions and localized acceptance until reconciliation.

#### Scenario: Reviewer starts a localized wave

- **WHEN** a review packet is opened
- **THEN** it records the canonical path and digest before drafting or review
- **AND** all semantic comparisons refer to that revision

#### Scenario: Canonical source is approved

- **WHEN** a competent reviewer completes the source audit
- **THEN** factual accuracy, safety, prerequisites, pedagogy, runnable claims, accessibility semantics, and applicable provenance are recorded against the current digest
- **AND** an approved result includes a non-empty reviewer role and review date without requiring personal learner data

#### Scenario: Canonical content changes during review

- **WHEN** the canonical digest differs before acceptance or final regression
- **THEN** the affected localized records become `stale`
- **AND** cannot return to `accepted` without reconciliation and repeated relevant checks

#### Scenario: Canonical source contains a defect

- **WHEN** pre-wave review finds a factual, safety, accessibility, prerequisite, or runnable-example defect necessary to the existing lesson
- **THEN** the canonical source is corrected and verified before propagation
- **AND** the correction is reconciled across all four locales before that unit is accepted
- **AND** unrelated curriculum expansion is not folded into this change

### Requirement: Semantic learning parity contract

Every localized variant SHALL preserve the canonical learning outcomes and usable instructional substance, including purpose, objectives, prerequisites, concept order, examples, observable outputs, guided modifications, hints, normal/boundary/invalid behavior, recovery, common mistakes, explained solutions, assessment, warnings, summary, and reflection.

#### Scenario: A localized chapter is reviewed

- **WHEN** a reviewer evaluates semantic coverage
- **THEN** every required parity dimension maps to concrete localized evidence or an approved justified exception
- **AND** a summary that omits exercises, recovery, solutions, or assessment fails review

#### Scenario: Natural localization changes structure

- **WHEN** a fluent translation combines, splits, or reorders prose/headings
- **THEN** it may pass if dependency order, meaning, learner actions, and observable outcomes remain equivalent
- **AND** it is not required to reproduce English wording or word count

#### Scenario: Intentional locale-specific difference is needed

- **WHEN** language grammar, shell conventions, or learner clarity requires a local difference
- **THEN** the packet records its rationale and affected contract element
- **AND** both linguistic and technical review approve it

### Requirement: Prerequisite-aware localized progression

Localized units SHALL introduce required concepts before use, keep required exercises solvable from declared prerequisites, and label any deliberate early appearance of a later concept as an optional preview with a localized continuation path.

#### Scenario: Exercise uses a required concept

- **WHEN** a learner reaches the exercise in any language
- **THEN** its required concepts have already been explained in that variant or declared prerequisites
- **AND** the solution does not hide a new prerequisite

#### Scenario: Later concept appears early

- **WHEN** a localized lesson intentionally previews a later topic
- **THEN** it is labeled **Optional preview** or the natural localized equivalent
- **AND** explains only the minimum needed, provides a skip/copyable path, and links to the localized later unit

#### Scenario: Localized prerequisite link is available

- **WHEN** the target unit has the reader's language variant
- **THEN** navigation points to that localized file rather than silently switching to English

### Requirement: Stable technical and executable contracts

Localized content SHALL preserve executable APIs, public identifiers, control-flow semantics, commands, paths, data constraints, expected results, diagnostics, source references, and safety boundaries from the verified canonical lesson unless a deliberate correction is tested and propagated; new or modified fences SHALL use the shared `runnable|expected-error|compile-only|source-ref|todo|illustrative|output` taxonomy and versioned `bookcheck` metadata.

#### Scenario: Code is shared across languages

- **WHEN** a canonical runnable or expected-error example appears in a localized variant
- **THEN** imports, public names, arguments, meaningful behavior, output contract, and recovery remain equivalent
- **AND** comments or learner-facing strings may be localized only when verification/source references stay valid

#### Scenario: Localized inline code diverges

- **WHEN** executable code cannot be shared verbatim for a justified reason
- **THEN** that variant is executed or tested with the documented Python/toolchain and bounded timeout
- **AND** the divergence and evidence are recorded

#### Scenario: Runnable claim lacks evidence

- **WHEN** a localized block is described as runnable but is neither executed nor derived from a tested companion source
- **THEN** the technical review fails

#### Scenario: Expected failure is translated

- **WHEN** a lesson intentionally demonstrates failure
- **THEN** the localized variant labels it as expected, describes the meaningful diagnostic without promising unstable exact text, and explains recovery

#### Scenario: Localized fence is added or changed

- **WHEN** restoration adds or modifies a fenced block or its execution metadata
- **THEN** it uses the shared classification and `bookcheck` grammar
- **AND** does not create an alternate locale-specific marker convention

### Requirement: Independent human acceptance gates

No localized variant SHALL be marked accepted without manual linguistic, technical/pedagogical, and rendered-accessibility reviews recorded independently against its current canonical and localized digests; an Arabic variant SHALL additionally require a manual bidi/copy-paste review.

#### Scenario: Fluent linguistic review passes

- **WHEN** a competent reviewer evaluates a localized variant
- **THEN** terminology, grammar, tone, age-appropriate clarity, natural phrasing, and non-blaming error guidance pass
- **AND** the result is recorded by review role without requiring learner personal data

#### Scenario: Technical and pedagogical review passes

- **WHEN** a competent reviewer evaluates behavior and learning design
- **THEN** code, claims, safety, prerequisites, examples, exercises, recovery, solutions, assessment, accessibility, and source references pass

#### Scenario: Rendered accessibility review passes

- **WHEN** a competent accessibility reviewer inspects a localized page at the declared narrow, wide, and zoom/reflow targets
- **THEN** reading order, keyboard and assistive-technology access, links, tables, images/equivalents, applicable contrast, and non-visual instructions pass
- **AND** the locale record stores `approved`, a non-empty role, review date, and notes independently of structural automation

#### Scenario: Arabic bidi review passes

- **WHEN** a competent reviewer inspects the Arabic page's rendered mixed-direction content and copies representative technical text
- **THEN** RTL prose, punctuation and lists remain readable while code, commands, paths, identifiers, numbers, and URLs remain accurate LTR
- **AND** the Arabic record stores a separate approved bidi decision with role, review date, and notes

#### Scenario: One reviewer covers multiple roles

- **WHEN** one person has the competence needed for more than one linguistic, technical/pedagogical, rendered-accessibility, or bidi role
- **THEN** the packet may record that role separately for each applicable review
- **AND** every checklist, result, date, notes, and digest binding remains independently completed

#### Scenario: Human gates complete in a different order

- **WHEN** competent reviewers complete applicable gates in any order
- **THEN** the record uses `human-review-in-progress` until every required gate and automated prerequisite is current
- **AND** `accepted` is derived only after all required objects pass rather than from an intermediate state name

#### Scenario: Qualified review is unavailable

- **WHEN** no competent reviewer can assess a required language or technical domain
- **THEN** the variant remains drafted or blocked
- **AND** automation or machine translation does not promote it to accepted

### Requirement: Automated signals are triage, not semantic proof

Automated checks SHALL detect structural and technical drift, while counts and similarity ratios SHALL remain diagnostic signals that cannot independently accept or reject semantic parity.

#### Scenario: Word count differs greatly

- **WHEN** a localized variant has a large word-count difference from canonical English
- **THEN** the system flags it for priority review
- **AND** a human determines whether substance is missing

#### Scenario: Counts look similar but meaning differs

- **WHEN** words, headings, or fences are numerically similar but a warning, exercise, solution, or behavior is mistranslated
- **THEN** human review fails the record despite the automated similarity

#### Scenario: Concise translation is semantically complete

- **WHEN** a language expresses the full contract more concisely
- **THEN** the variant may pass all applicable human reviews
- **AND** no padding is added merely to satisfy a ratio

#### Scenario: Structural defect is found

- **WHEN** automation detects a missing file, broken link, malformed fence, invalid source reference, heading error, RTL imbalance, or mirror mismatch
- **THEN** the record is blocked until corrected and rechecked

### Requirement: Small, priority-ordered remediation waves

Restoration SHALL close exactly one unit per review packet and SHALL limit each editing sub-wave to one or two localized languages in that unit, prioritizing Swedish and Arabic, then later Catalan units, remaining Catalan units, and finally a complete Spanish audit.

#### Scenario: Standard wave is opened

- **WHEN** translation work begins
- **THEN** the wave belongs to one unit and contains at most two locales, normally no more than two localized files
- **AND** records its source digests, scope, reviewers, validation, and rollback boundary

#### Scenario: Advanced tracking reaches chapters 23 through 25

- **WHEN** a locale band reaches chapters 23, 24, and 25
- **THEN** each chapter executes as its own packet with network, C++, or Rust technical-review competence and an independent rollback boundary
- **AND** a higher-level tracking task remains incomplete until all three packets independently satisfy their gates

#### Scenario: Swedish and Arabic are scheduled

- **WHEN** priority order is applied
- **THEN** chapters progress in prerequisite order through 01–25 followed by both appendices
- **AND** a safety or factual defect may move earlier with documented rationale

#### Scenario: Catalan is scheduled

- **WHEN** Swedish and Arabic regression is complete
- **THEN** Catalan processes chapters 15–25 and appendices first
- **AND** then processes chapters 01–14 to close all 27 records

#### Scenario: Spanish appears close to canonical

- **WHEN** Spanish word and heading counts are similar to English
- **THEN** all 27 Spanish variants still receive semantic, linguistic, and technical review
- **AND** only confirmed gaps are changed

#### Scenario: Canonical repair affects all locales

- **WHEN** a necessary canonical correction would exceed the normal locale limit
- **THEN** it is split into linked review sub-waves for one unit
- **AND** the correction bundle is integrated atomically only after all four locales are reconciled

### Requirement: Arabic RTL and copyable LTR technical text

Every Arabic unit SHALL contain exactly one balanced outer `<div dir="rtl">` wrapper while code, commands, paths, URLs, identifiers, output, and diagnostics remain visually legible and copyable left-to-right.

#### Scenario: Arabic document is structurally checked

- **WHEN** an Arabic variant enters automated review
- **THEN** exactly one outer RTL wrapper encloses the document and closes correctly
- **AND** no nested duplicate wrapper is introduced

#### Scenario: Reviewer checks bidirectional technical content

- **WHEN** an Arabic variant contains code, commands, inline identifiers, paths, or output
- **THEN** manual review confirms visual order and copy/paste behavior
- **AND** no invisible direction mark changes executable text
- **AND** the decision remains pending unless its result, role, review date, notes, canonical digest, and localized digest are current

#### Scenario: Arabic selector and navigation are updated

- **WHEN** links are restored
- **THEN** selector order remains standard, Arabic targets resolve, and the RTL wrapper remains valid

### Requirement: Accessible parity in every language

Every canonical and localized page SHALL preserve accessible document structure and equivalent access to visual or tabular information, and SHALL retain a separate rendered human-review result that automation cannot approve.

#### Scenario: Heading structure is reviewed

- **WHEN** a localized document is validated
- **THEN** it has one H1 and hierarchical headings without skipped levels
- **AND** heading translation remains descriptive rather than mechanically copied

#### Scenario: Visual content is localized

- **WHEN** canonical content includes a meaningful image or diagram
- **THEN** the localized variant includes concise localized alt text and an equivalent prose explanation

#### Scenario: Table or visual instruction is difficult to access

- **WHEN** a table is unsuitable on a narrow screen or an instruction depends on color, icon, position, or direction
- **THEN** the localized variant provides a readable textual/list alternative

#### Scenario: Links are presented

- **WHEN** a localized lesson references another resource
- **THEN** link text describes the destination and does not rely on phrases equivalent to “click here”

#### Scenario: Page is reviewed at the rendering matrix

- **WHEN** a canonical, localized, or root-index page is prepared for unit or root closure
- **THEN** a competent reviewer inspects `320×568`, `1280×800`, and zoom/reflow at `200 %`, plus keyboard and assistive-technology reading as applicable
- **AND** records requested changes or approval against the page digest, checked-in render-profile digest, derived render-input digest, and actual renderer/browser/OS/AT versions or a justified `not-applicable`

#### Scenario: Publication rendering inventory is complete

- **WHEN** the course is prepared for global acceptance
- **THEN** rendered-accessibility evidence covers exactly 135 unit pages plus six root indexes, for 141 current paths
- **AND** bidi/copy-paste evidence covers exactly 27 Arabic unit pages plus the Arabic root index, for 28 current paths

#### Scenario: Render-input digest is derived

- **WHEN** a rendered review records its evidence binding
- **THEN** `render_input_sha256` hashes canonical JSON containing repository-relative path, page digest, profile digest, path-sorted global asset digests, and the normalized observed environment
- **AND** an absent/unsafe asset path, missing environment field, or mismatched digest prevents approval

#### Scenario: Render inputs change after approval

- **WHEN** the page bytes, versioned render profile, or a declared global rendering asset changes
- **THEN** only the dependent rendered-accessibility and bidi decisions become stale
- **AND** structural validation cannot preserve or recreate their human approval

#### Scenario: Structural accessibility checks pass

- **WHEN** headings, links, alt text, table structure, and wrapper balance pass automated checks
- **THEN** the rendered review remains pending until a competent reviewer supplies its own decision
- **AND** no command promotes or fabricates role, date, notes, accessibility approval, or bidi approval

### Requirement: Safe localized examples and claims

All touched variants SHALL retain or strengthen the canonical safety boundaries and SHALL not introduce personal data, credentials, public targets, destructive operations, unbounded work, or unverified compatibility/performance claims.

#### Scenario: Example uses data or credentials

- **WHEN** localized prose introduces sample users, tokens, paths, or configuration
- **THEN** it uses fictional data and fake secrets in temporary/local scope
- **AND** does not solicit or expose learner data

#### Scenario: Example performs I/O, networking, or concurrency

- **WHEN** localized instructions run an operation with external effects
- **THEN** it remains local/offline-capable by default, bounded by inputs/runtime/timeouts, and safe to rerun

#### Scenario: Platform or performance claim is translated

- **WHEN** a localized variant describes compatibility or speed
- **THEN** it preserves the distinction between tested behavior, design intent, and future work
- **AND** does not broaden the tested matrix

### Requirement: Stable paths and localized navigation

Parity remediation SHALL preserve all existing unit directory names, deliberate anchors, and relative URLs, keep root `README.md` and `README.en.md` byte-for-byte identical, and update shared indexes only atomically toward existing targets whose domain implementation is complete; localized parity state is tracked independently and does not control preservation of an already published entry.

#### Scenario: Legacy directory name is language-inconsistent

- **WHEN** a reviewer encounters a slug such as an existing Spanish-derived directory name
- **THEN** the directory and inbound relative URLs remain unchanged
- **AND** prose may explain the topic naturally without renaming the path

#### Scenario: Root navigation requires a correction

- **WHEN** parity review finds an index or localized-link defect
- **THEN** all affected root indexes are reconciled in one integration step
- **AND** `README.md` and `README.en.md` remain byte-identical

#### Scenario: Referenced heading is renamed

- **WHEN** a touched heading has an existing internal fragment or a recorded deliberate public anchor
- **THEN** the heading preserves that anchor or adds an inventoried explicit HTML alias at the same semantic destination
- **AND** validation proves both current navigation and the preserved fragment resolve without duplicate ambiguous anchors

#### Scenario: Target does not exist

- **WHEN** an index candidate points to an unimplemented chapter or missing localized file
- **THEN** the link is not added
- **AND** validation rejects any dangling link

### Requirement: Shared quality-gate coordination

Parity remediation SHALL consume the approved common book-quality interface when available and SHALL not duplicate ownership of global structural validation or chapter-domain plugins.

#### Scenario: Common quality gate is implemented first

- **WHEN** `tools/validate_book.py` and its baseline exist under the approved `add-book-quality-gates` change
- **THEN** each wave runs `python -B tools/validate_book.py --changed-from <ref>` as applicable
- **AND** runs relevant chapter plugins for source/domain behavior

#### Scenario: Wave resolves baselined legacy findings

- **WHEN** a remediation wave fixes content represented by existing baseline fingerprints
- **THEN** the same wave removes those resolved fingerprints through the approved `--update-baseline` flow
- **AND** the baseline diff only reduces exact debt and never adds or broadens an entry

#### Scenario: Parity work starts before the common gate

- **WHEN** the common validator is not yet implemented
- **THEN** inventory, drafting, and human review may proceed with documented equivalent checks
- **AND** final acceptance requires the common gate or equivalent evidence for unit shape, links, mirror, RTL, headings, shared fence taxonomy/metadata, alt text, and source refs

#### Scenario: Automation and semantic review disagree

- **WHEN** structural automation passes but human review finds omitted or incorrect learning substance
- **THEN** the localized record remains blocked
- **AND** common tooling is not expanded to pretend it can certify language meaning

### Requirement: Coordination with published chapters 23 through 25

This change SHALL inventory and review published chapter 23–25 documents while leaving companion implementation and domain verification owned by `teach-python-network-programming`, `teach-python-cpp-integration`, and `teach-python-rust-integration`, whether their originating changes are active or archived.

#### Scenario: Published chapter document is absent

- **WHEN** parity reconciliation finds a missing canonical or localized chapter 23–25 target
- **THEN** inventory validation fails instead of silently omitting that chapter

#### Scenario: Advanced chapter enters the review queue

- **WHEN** chapter 23, 24, or 25 has all five localized targets and its domain implementation evidence is available
- **THEN** valid entries are preserved in numeric order before appendices and added to the 27-unit inventory
- **AND** automation does not mark their variants accepted

#### Scenario: Domain implementation and parity review remain separate

- **WHEN** a chapter plugin and companion tests pass but linguistic or technical/pedagogical review is pending
- **THEN** the chapter remains published and inventoried
- **AND** its parity record remains pending rather than inheriting domain acceptance
- **AND** archiving the originating technical change does not advance the source audit or localized record

#### Scenario: Shared validator has a chapter plugin

- **WHEN** an implemented proposed chapter supplies its own domain plugin
- **THEN** the global gate discovers or invokes it according to the shared interface
- **AND** this parity change does not copy its tests or source contracts

### Requirement: Scoped provenance and license review

Any third-party exercise, dataset, diagram, or substantial prose adapted while restoring a variant SHALL have verified provenance, compatible license, and required attribution, while untouched legacy material remains outside this change's retroactive provenance audit.

#### Scenario: Reviewer adapts third-party material

- **WHEN** restoration introduces or substantially adapts external content
- **THEN** its source, license, and attribution obligations are verified and recorded near the material or in a dedicated attribution section

#### Scenario: License cannot be verified

- **WHEN** provenance or republication rights remain uncertain
- **THEN** the material is not merged
- **AND** is replaced with an original compatible example or keeps the record blocked

#### Scenario: Existing material is not touched

- **WHEN** a legacy section is outside the edited/reviewed material of a wave
- **THEN** this change does not claim to have completed a repository-wide historical provenance audit for it

#### Scenario: Unit packet references applicable provenance

- **WHEN** an `ATTRIBUTIONS.toml` entry covers the canonical page, a localized page, or companion material in one unit packet
- **THEN** the packet reports the entry ID, normalized entry/evidence digest, status, and authoritative inventory path
- **AND** unresolved applicable evidence blocks only the covered unit/page while `LICENSE` and the repository badge remain global publication gates

#### Scenario: Provenance digest is normalized

- **WHEN** a packet derives `provenance_sha256` for an applicable entry
- **THEN** canonical JSON includes the attribution inventory schema version, every field allowed and present in that entry, normalized path-sorted coverage, and path-sorted `{path, sha256}` evidence
- **AND** an unknown field, absent/unsafe path, changed schema, changed entry field, or changed covered byte invalidates the digest or fails closed

#### Scenario: Applicable provenance evidence changes

- **WHEN** an attribution entry or one of its covered paths changes after a unit review
- **THEN** a digest mismatch makes the affected provenance gate stale and prevents unit closure or publication as applicable
- **AND** an unrelated chapter entry does not invalidate another unit's human reviews

### Requirement: Auditable final acceptance and regression

The parity restoration SHALL be complete only when all 108 localized records and the root-publication leaf are accepted, all 27 canonical source leaves have approved audit/render decisions against current digests, `tools/publication_signoff.json` verifies approved against those inputs, all automated and manual gates pass, navigation is coherent, and implementation evidence matches task state.

#### Scenario: A wave finishes

- **WHEN** its source and localized digests are current, automated checks pass, canonical audit, linguistic, technical/pedagogical, rendered-accessibility, applicable bidi, and provenance gates pass, and no exception is unresolved
- **THEN** only that wave's records move to `accepted`
- **AND** its implementation task may be marked complete

#### Scenario: A unit packet closes

- **WHEN** one canonical source and all four localized records satisfy their digest-bound gates
- **THEN** that unit may be reported closed independently of every other unit
- **AND** the course remains globally pending until all 27 unit packets close

#### Scenario: Root publication packet closes

- **WHEN** all applicable root semantic, linguistic, technical/pedagogical, rendered-accessibility, Arabic bidi, and provenance gates pass against current digests
- **THEN** the root-publication leaf may move to `accepted`
- **AND** the course remains globally pending until all 27 unit packets, 108 locale records, and the root packet are accepted and the later common sign-off references their current evidence

#### Scenario: Global regression runs

- **WHEN** all language waves report completion
- **THEN** the course verifies 27 canonical and 108 localized unit files plus all six root indexes together
- **AND** finds zero `drafted`, `blocked`, `stale`, or unapproved-exception records
- **AND** confirms Tasks 4.3, 7.1, and 7.2 of `add-book-quality-gates` are completed against the referenced current evidence
- **AND** verifies `tools/publication_signoff.json` read-only and confirms its digest is referenced from the common implementation review without becoming an upstream input

#### Scenario: Generated or sensitive artifact is found

- **WHEN** final hygiene review finds caches, environments, generated builds, credentials, secrets, or learner personal data
- **THEN** completion fails until the artifact is removed safely and checks rerun

#### Scenario: OpenSpec change is handed off

- **WHEN** proposal artifacts are reviewed or completed implementation is prepared for archival
- **THEN** `openspec validate restore-multilingual-content-parity --strict` and `git diff --check` pass
- **AND** unchecked tasks remain unchecked until their work is actually verified
