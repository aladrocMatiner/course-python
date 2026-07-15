## MODIFIED Requirements

### Requirement: Review inventory covers every published unit

The parity inventory SHALL discover every published chapter and appendix with canonical English and four localized siblings, including Chapters 23–28, while preserving compatible review results and never inferring human approval.

#### Scenario: Current published tree is reconciled

- **WHEN** parity reconciliation runs against 28 chapters and two appendices
- **THEN** it reports 30 canonical sources and 120 localized records, with deterministic digests and no omitted published unit

#### Scenario: Newly inventoried bridge variants

- **WHEN** Chapters 26–28 first enter the inventory
- **THEN** their automated signals are recorded and their canonical, linguistic, technical, rendered-accessibility, Arabic bidi, provenance, and publication fields remain pending until competent human reviewers approve them

#### Scenario: Previously inventoried advanced variants

- **WHEN** Chapters 23–25 remain in the expanded inventory
- **THEN** their existing compatible evidence is retained without being inherited by or copied into Chapters 26–28

#### Scenario: Canonical correction invalidates review

- **WHEN** a canonical digest changes after a learner-facing correction
- **THEN** affected localized records become stale or pending and cannot retain an accepted result against the old digest
