## MODIFIED Requirements

### Requirement: Review inventory covers every published unit
The parity inventory SHALL discover every published chapter and appendix with
canonical English and four localized siblings, including Chapters 23–30 and
Appendices A–C, while preserving compatible review results and never inferring
human approval.

#### Scenario: Current published tree is reconciled
- **WHEN** parity reconciliation runs against 30 chapters and three appendices after Appendix C is complete and authorized
- **THEN** it reports 33 canonical sources and 132 localized records with deterministic digests and no omitted published unit

#### Scenario: Appendix C first enters the inventory
- **WHEN** the five Appendix C pages, companions, source references, and owned checks exist
- **THEN** one source and four locale leaves are created with current digests while canonical, linguistic, technical/pedagogical, rendered-accessibility, Arabic-bidi, provenance, and publication fields remain pending

#### Scenario: Newly inventoried bridge variants retain their first-entry gate
- **WHEN** Chapters 26–28 first enter the inventory during the preserved prior expansion
- **THEN** their automated signals are recorded and their canonical, linguistic, technical/pedagogical, rendered-accessibility, Arabic-bidi, provenance, and publication fields remain pending until competent human reviewers approve them

#### Scenario: Previously inventoried bridge variants remain review-bound
- **WHEN** Chapters 26–28 remain in the expanded inventory
- **THEN** their existing compatible automated signals are retained and their canonical, linguistic, technical, rendered-accessibility, Arabic-bidi, provenance, and publication fields keep their actual pending/approved state without being inherited by Appendix C

#### Scenario: Previously inventoried advanced variants remain independent
- **WHEN** Chapters 23–25 remain in the expanded inventory
- **THEN** their compatible network/native evidence stays owned by those chapters and is not copied into Chapters 26–30 or Appendix C

#### Scenario: Newly inventoried advanced variants retain their first-entry gate
- **WHEN** Chapters 23–25 first enter the inventory during the preserved prior expansion
- **THEN** their automated signals are recorded while canonical, linguistic, technical/pedagogical, rendered-accessibility, Arabic-bidi, provenance, and publication fields remain pending until competent reviewers approve them

#### Scenario: Newly inventoried environment variants retain their first-entry gate
- **WHEN** Chapters 29–30 first enter the inventory during the preserved prior expansion
- **THEN** their compatible automated environment signals are recorded while canonical, linguistic, technical/pedagogical, rendered-accessibility, Arabic-bidi, provenance, and publication fields remain pending until competent human reviewers approve them

#### Scenario: Previously inventoried environment variants remain independent
- **WHEN** Chapters 29–30 remain in the expanded inventory
- **THEN** their compatible environment evidence and pending human gates stay unchanged and are not inherited by Appendix C

#### Scenario: Canonical correction invalidates review
- **WHEN** a canonical digest changes after a learner-facing correction
- **THEN** affected localized records become stale or pending and cannot retain an accepted result against the old digest

## ADDED Requirements

### Requirement: Appendix C publication evidence remains separated by owner
Publication evidence SHALL inventory the canonical and four localized Appendix
C pages, their companion/source/provenance inputs, the `patterns:core-suite`
and `patterns:network-suite` checks, root decisions, and final sign-offs without
changing the ownership or result of generic, `learning`, `environment`,
`network`, C++, or Rust evidence.

#### Scenario: Generic validation does not infer pattern behavior
- **WHEN** generic book validation runs without the patterns plugin
- **THEN** Markdown, links, runnable trusted snippets, source-reference structure, accessibility signals, attribution schema, and hygiene are checked
- **AND** both `patterns:*` checks remain not selected rather than passed

#### Scenario: Core patterns evidence is selected
- **WHEN** the isolated patterns plugin executes `patterns:core-suite`
- **THEN** it reports only the bounded pure-Python construction/behavior/architecture contract observed on that host
- **AND** it does not imply network policy, Chapter 21/23 mechanics, linguistic, pedagogical, accessibility, provenance, or production approval

#### Scenario: Network patterns evidence is selected
- **WHEN** the isolated patterns plugin executes `patterns:network-suite`
- **THEN** it reports only Appendix C's bounded Retry/deduplication, Circuit Breaker, Bulkhead, optional Pub/Sub, cancellation, and cleanup observations
- **AND** it performs no socket work and Chapter 21/23 framing/Reactor/TaskGroup/TLS behavior remains owned by its existing evidence rather than being relabeled as re-executed

#### Scenario: Source reference names the wrong automated owner
- **WHEN** an Appendix C source reference uses a path/check-ID combination outside its registered `patterns:*` ownership or labels a Chapter 23 source as Appendix C evidence
- **THEN** source-contract validation fails that structural mismatch
- **AND** recovery links the existing Chapter 23 explanation/evidence or registers the original Appendix C companion under the correct check

#### Scenario: Semantic duplication is a human evidence boundary
- **WHEN** automated path/check contracts pass
- **THEN** technical/provenance reviewers still compare Appendix C with Chapter 23 for copied mechanics, unsupported adaptation, or misleading nominal-pattern claims
- **AND** any unresolved duplication or provenance finding blocks publication rather than being declared machine-verified

#### Scenario: Human publication gate stays pending
- **WHEN** automated structure, core/network pattern checks, parity packets, root links, and hygiene pass
- **THEN** canonical, linguistic, technical/pedagogical, rendered-accessibility, Arabic-bidi, provenance/license, and final publication decisions remain pending
- **AND** no quality baseline or CI success manufactures a reviewer identity, date, note, or approval

#### Scenario: Provenance input changes
- **WHEN** a companion, exercise, diagram, source note, attribution entry, or page digest changes
- **THEN** affected unit/root/publication evidence becomes current-pending or stale according to its existing contract
- **AND** final sign-off cannot remain approved against the prior input digest
