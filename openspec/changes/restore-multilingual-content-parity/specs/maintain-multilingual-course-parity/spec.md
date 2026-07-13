## ADDED Requirements

### Requirement: Complete implemented-course parity inventory

The course SHALL maintain a review inventory for the 22 implemented chapters and two implemented appendices, treating each unit `README.md` as canonical English and tracking its Spanish, Catalan, Swedish, and Arabic variants independently.

#### Scenario: Inventory covers the implemented course

- **WHEN** the parity inventory is generated
- **THEN** it contains exactly 24 canonical units and 96 localized unit-language records
- **AND** every record identifies an existing stable path without renaming a directory

#### Scenario: Proposed chapters remain proposed truth

- **WHEN** chapters 23, 24, or 25 exist only under active OpenSpec changes
- **THEN** the parity inventory does not count or claim review completion for them
- **AND** does not create their content or navigation targets

#### Scenario: Missing localized document blocks completion

- **WHEN** any of the four required localized siblings is absent for an in-scope unit
- **THEN** its record is blocked
- **AND** the course cannot declare the 24-unit parity restoration complete

### Requirement: Frozen canonical source per review packet

Each unit-language review SHALL record a digest of the exact canonical `README.md` revision used, and a changed canonical digest SHALL invalidate acceptance until the localized variant is reconciled.

#### Scenario: Reviewer starts a localized wave

- **WHEN** a review packet is opened
- **THEN** it records the canonical path and digest before drafting or review
- **AND** all semantic comparisons refer to that revision

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

### Requirement: Human linguistic and technical acceptance

No localized variant SHALL be marked accepted without manual linguistic review and manual technical/pedagogical review recorded against the current canonical digest.

#### Scenario: Fluent linguistic review passes

- **WHEN** a competent reviewer evaluates a localized variant
- **THEN** terminology, grammar, tone, age-appropriate clarity, natural phrasing, and non-blaming error guidance pass
- **AND** the result is recorded by review role without requiring learner personal data

#### Scenario: Technical and pedagogical review passes

- **WHEN** a competent reviewer evaluates behavior and learning design
- **THEN** code, claims, safety, prerequisites, examples, exercises, recovery, solutions, assessment, accessibility, and source references pass

#### Scenario: One reviewer covers both roles

- **WHEN** one person has the needed language and technical/pedagogical competence
- **THEN** the packet may record both roles for that review
- **AND** both checklists remain independently completed

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
- **THEN** the variant may pass both human reviews
- **AND** no padding is added merely to satisfy a ratio

#### Scenario: Structural defect is found

- **WHEN** automation detects a missing file, broken link, malformed fence, invalid source reference, heading error, RTL imbalance, or mirror mismatch
- **THEN** the record is blocked until corrected and rechecked

### Requirement: Small, priority-ordered remediation waves

Restoration SHALL proceed in reviewable waves of no more than two units and two localized languages, prioritizing Swedish and Arabic, then later Catalan units, remaining Catalan units, and finally a complete Spanish audit.

#### Scenario: Standard wave is opened

- **WHEN** translation work begins
- **THEN** the wave contains at most two units and two locales, normally no more than four localized files
- **AND** records its source digests, scope, reviewers, validation, and rollback boundary

#### Scenario: Swedish and Arabic are scheduled

- **WHEN** priority order is applied
- **THEN** chapters progress in prerequisite order through 01–22 followed by both appendices
- **AND** a safety or factual defect may move earlier with documented rationale

#### Scenario: Catalan is scheduled

- **WHEN** Swedish and Arabic regression is complete
- **THEN** Catalan processes chapters 15–22 and appendices first
- **AND** then processes chapters 01–14 to close all 24 records

#### Scenario: Spanish appears close to canonical

- **WHEN** Spanish word and heading counts are similar to English
- **THEN** all 24 Spanish variants still receive semantic, linguistic, and technical review
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

#### Scenario: Arabic selector and navigation are updated

- **WHEN** links are restored
- **THEN** selector order remains standard, Arabic targets resolve, and the RTL wrapper remains valid

### Requirement: Accessible parity in every language

Every localized variant SHALL preserve accessible document structure and equivalent access to visual or tabular information.

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

Parity remediation SHALL preserve all existing unit directory names, deliberate anchors, and relative URLs, keep root `README.md` and `README.en.md` byte-for-byte identical, and update shared indexes only atomically toward accepted implemented targets.

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

### Requirement: Coordination with proposed chapters 23 through 25

This change SHALL preserve valid concurrently implemented chapter 23–25 navigation while leaving their content, translation acceptance, and domain verification owned by their respective changes.

#### Scenario: Proposed chapter is still absent

- **WHEN** parity work updates navigation and a chapter 23–25 target does not exist
- **THEN** no entry for that target is created

#### Scenario: Proposed chapter is implemented during remediation

- **WHEN** chapter 23, 24, or 25 has all five localized targets and its OpenSpec implementation is accepted/completed, or it is archived/baselined with equivalent verification evidence
- **THEN** valid entries are preserved in numeric order before appendices
- **AND** this change does not mark their variants accepted in the 24-unit inventory

#### Scenario: Proposed chapter tree is partial or pending

- **WHEN** files or all localized targets exist but the owning change still has unverified tasks/scenarios or lacks archived/baselined acceptance evidence
- **THEN** parity work does not add or preserve its root-index entry merely because paths exist
- **AND** treats the chapter as proposed truth until its own acceptance gate completes

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

### Requirement: Auditable final acceptance and regression

The parity restoration SHALL be complete only when all 96 localized records are accepted against current canonical digests, all automated and manual gates pass, navigation is coherent, and implementation evidence matches task state.

#### Scenario: A wave finishes

- **WHEN** its source digest is current, automated checks pass, both manual reviews pass, and no exception is unresolved
- **THEN** only that wave's records move to `accepted`
- **AND** its implementation task may be marked complete

#### Scenario: Global regression runs

- **WHEN** all language waves report completion
- **THEN** the course verifies 24 canonical and 96 localized files together
- **AND** finds zero `drafted`, `blocked`, `stale`, or unapproved-exception records

#### Scenario: Generated or sensitive artifact is found

- **WHEN** final hygiene review finds caches, environments, generated builds, credentials, secrets, or learner personal data
- **THEN** completion fails until the artifact is removed safely and checks rerun

#### Scenario: OpenSpec change is handed off

- **WHEN** proposal artifacts are reviewed or completed implementation is prepared for archival
- **THEN** `openspec validate restore-multilingual-content-parity --strict` and `git diff --check` pass
- **AND** unchecked tasks remain unchecked until their work is actually verified
