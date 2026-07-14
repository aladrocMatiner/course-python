## ADDED Requirements

### Requirement: Review inventory covers every published unit
The parity inventory SHALL discover every published chapter and appendix with canonical English and four localized siblings, including chapters 23, 24, and 25, while preserving existing review results and never inferring human approval.

#### Scenario: Current published tree is reconciled
- **WHEN** parity reconciliation runs against 25 chapters and two appendices
- **THEN** it reports 27 canonical sources and 108 localized records, with deterministic digests and no omitted published unit

#### Scenario: Newly inventoried advanced variants
- **WHEN** chapters 23–25 first enter the inventory
- **THEN** their automated signals are recorded and their linguistic, technical, and source audit fields remain pending until competent human reviewers approve them in the recorded linguistic and technical/pedagogical roles

#### Scenario: Canonical correction invalidates review
- **WHEN** a canonical digest changes after a learner-facing correction
- **THEN** affected localized records become stale or pending and cannot retain an accepted result against the old digest

### Requirement: Generic and domain validation have separate truthful ownership
The generic gate SHALL validate shared book structure and bounded trusted snippets, while network, C++, and Rust plugins SHALL own their toolchain/domain behavior and report passed, failed, or explicitly skipped evidence without suppressing generic diagnostics.

#### Scenario: Generic validation only
- **WHEN** a contributor runs `python -B tools/validate_book.py` without plugins
- **THEN** shared checks run and each referenced domain check is reported as not selected rather than passed

#### Scenario: Explicit domain validation
- **WHEN** CI or a maintainer selects a chapter plugin with its provisioned prerequisites
- **THEN** the bounded plugin protocol runs the domain checks, preserves generic findings, and records positive check evidence or a precise failure/skip

#### Scenario: Unsupported native host
- **WHEN** a native domain job cannot provision a claimed toolchain
- **THEN** the job does not claim cross-platform success and its documented matrix identifies the missing host evidence

### Requirement: CI exercises published domain evidence with least privilege
The repository SHALL run generic quality checks on supported changes and SHALL provide explicit bounded domain jobs for network, C++, and Rust evidence using least privilege, pinned actions, no production secrets, and no public targets.

#### Scenario: Generic CI
- **WHEN** a pull request or push runs book quality CI
- **THEN** unit tests, parity inventory, generic validation, and whitespace checks run with `contents: read` and a bounded timeout

#### Scenario: Domain CI
- **WHEN** files relevant to chapters 23–25 or their shared validation contracts change
- **THEN** the corresponding plugin jobs run on provisioned hosts or report the documented conditional skip; the network job remains loopback-only

#### Scenario: Generated artifacts
- **WHEN** a domain build or test completes or fails
- **THEN** build outputs remain in temporary/ignored job storage and the committed workspace contains no generated binary, wheel, sdist, cache, credential, or learner data

### Requirement: Traceability and task state reflect implemented truth
Every completed implementation claim SHALL match navigation, source evidence, OpenSpec task checkboxes, and verification results; stale handoff text SHALL be corrected rather than retained as historical truth.

#### Scenario: Index task is complete
- **WHEN** all six root indexes link chapter 25 in matching languages and its owning task is checked
- **THEN** traceability states that index integration is implemented and does not call the task pending

#### Scenario: Human gate remains unfinished
- **WHEN** automation is complete but linguistic, accessibility, pedagogical, or provenance sign-off is absent
- **THEN** the corresponding task and review row remain pending and no completion summary implies otherwise

### Requirement: OpenSpec authoring instructions resolve locally
The assistant guidance referenced by the root `AGENTS.md` SHALL exist at `openspec/AGENTS.md` and SHALL direct contributors to the repository config, stable content rules, matching OpenSpec action skill, and strict validation without duplicating generated CLI schemas.

#### Scenario: Proposal request
- **WHEN** an assistant handles a proposal or cross-cutting change
- **THEN** it can open both instruction files, reads `openspec/config.yaml`, uses the matching OpenSpec workflow, and preserves public paths and human review boundaries

#### Scenario: CLI workflow evolves
- **WHEN** OpenSpec changes artifact locations or instructions
- **THEN** the guide tells contributors to use `status` and `instructions` resolved paths instead of hard-coded assumptions

### Requirement: Automated evidence never substitutes for specialist review
Quality reports SHALL state the exact structural, executable, and domain evidence established and SHALL retain separate human gates for natural language, semantic teaching parity, rendered accessibility, and provenance/license decisions.

#### Scenario: All automated checks pass
- **WHEN** validators, plugins, skill checks, links, RTL structure, and tests pass
- **THEN** the report may claim those checks passed but cannot mark a pending human review approved

#### Scenario: Reviewer requests changes
- **WHEN** a competent reviewer finds a semantic, accessibility, or provenance issue after automation passes
- **THEN** the relevant record remains blocked or changes-requested and the automation is not weakened to waive the finding
