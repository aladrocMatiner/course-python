## Why

The published course passes its structural gate but still teaches several concepts before their declared prerequisites, omits chapters 23–25 from the human-review inventory, and contains concrete HTTP, logging, networking, packaging, C++, and Rust claims that the current generic checks do not protect. The repository also lacks reusable maintainer skills for verifying those domains, so the same gaps can recur even after narrow corrections.

## What Changes

- Add five repository-local maintainer skills for Python learning assets, network laboratories, packaging/release, native interoperability, and book-quality tooling; extend `professor` and `book-editor` with executable curriculum-route and provenance/onboarding workflows.
- Publish a course-level route map and prerequisite contract without renaming chapters or breaking public links. Make every essential checkpoint solvable from declared prerequisites, split foundational functions from optional higher-order material, and add recoverable executable solutions where the audit found summary-only answers.
- Correct the audited safety and accuracy defects in chapters 15, 16, 19–25 and the appendices: bounded HTTP bodies, trusted-only logging configuration, structured concurrency guidance, bounded network state and idle peers, accurate packaging/toolchain claims, explicit sanitizer skips, stronger native typing/artifact checks, and accurate benchmarks/errors.
- Extend parity inventory and quality evidence from 24 canonical sources/96 localized variants to all 27 published units/108 localized variants while retaining human linguistic, technical, accessibility, and provenance approval as pending release gates.
- Run domain plugins in an explicit bounded CI job, repair stale traceability, add the missing OpenSpec assistant guide referenced by `AGENTS.md`, and keep generic validation separate from network/native verification.
- Preserve all five language variants and Arabic bidi structure for learner-facing edits. Canonical corrections are propagated semantically; automation never marks a translation or provenance record human-approved.

### Goals

- Make the beginner route calm, dependency-correct, and independently completable.
- Turn audited systems claims into bounded, executable contracts with regression tests.
- Give future maintainers concise, validated skills that reproduce the required review workflows.
- Make quality dashboards and OpenSpec task state describe every published unit truthfully.

### Non-goals

- No chapter directory, public URL, or public native module API is renamed.
- No human linguistic, accessibility, pedagogical, provenance, legal, or cross-platform approval is fabricated.
- No public-network targets, production deployment, framework track, or unverified performance promise is added.
- The incomplete historical translation-review change is coordinated and expanded, not falsely completed.

## Capabilities

### New Capabilities

- `maintain-course-learning-progression`: Course-level routes, prerequisite ordering, assessment recovery, cognitive-load limits, and multilingual learner navigation.
- `provide-course-maintainer-skills`: Validated repository-local skills and conditional domain references for repeatable authoring, verification, packaging, networking, native interop, and quality-tool maintenance.
- `harden-python-systems-lessons`: Safe and technically accurate HTTP, logging, asyncio, networking, packaging, C++, Rust, CLI, and algorithm learning contracts with bounded executable evidence.
- `complete-published-quality-evidence`: Full-unit parity inventory, explicit domain-plugin CI, truthful traceability, OpenSpec guidance, and preserved human release boundaries.

### Modified Capabilities

None. No archived base specs exist; the change coordinates with the active `add-book-quality-gates` and `restore-multilingual-content-parity` deltas without claiming they are accepted base specifications.

## Impact

- **Affected content:** root `README*`, audited chapters 01–25, both appendices, and their five-language variants where learner-facing semantics change.
- **Affected source/tests:** chapter 23 network companions; chapter 24 CMake, stubs, artifact verification; chapter 25 Rust preflight, benchmark, error contracts; `tools/` tests, parity manifest, and CI workflow.
- **Affected skills:** five new directories under `.codex/skills/`; focused additions to `professor` and `book-editor`. Unrelated Django, PatternFly, Proxmox, and browser-testing skills are not activated by this course change.
- **Active-change coordination:** update quality/parity evidence only where published truth changed; do not complete their human-review tasks. Preserve the completed ownership of chapters 23–25 and reconcile their traceability.
- **Migration:** existing paths and APIs remain stable. Review inventory expands additively; old pending records retain their status and new records begin pending human review.
- **Risks:** broad multilingual drift, overloading the beginner path, platform-dependent native checks, and CI duration. Mitigations are atomic per-unit edits, explicit essential/advanced boundaries, conditional toolchain checks, and bounded domain jobs.
- **Rollback:** each phase is independently revertible; prior inventory can be restored from version control, and domain CI can be disabled without weakening the generic validator contract.
- **Definition of done:** all change tasks are checked with their stated evidence; all seven affected skill validators pass; 62+ quality tests plus new regressions pass; every change-owned generic and domain check passes or reports an explicit supported skip; generic/plugin invocations preserve any unresolved human provenance or publication diagnostics owned by coordinated active changes instead of waiving them; parity reports 27 sources/108 variants without human acceptance claims; strict OpenSpec validation and `git diff --check` pass.
