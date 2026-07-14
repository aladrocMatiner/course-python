## Why

The repository's acceptance matrix is duplicated across CI, maintainer guides, and implementation reviews, so required checks can drift: CI currently omits the curriculum validator even though local handoff requires it. Maintainers also have no single deterministic, machine-readable record that distinguishes executed, failed, unsupported, and unselected evidence without manually copying command output.

## What Changes

- Add a versioned, standard-library quality matrix with stable check IDs, explicit profiles, bounded commands, prerequisites, and evidence scope; no plugin or native toolchain is auto-discovered or auto-executed.
- Add a read-only orchestration CLI that runs explicitly selected checks without a shell, closes stdin, uses a hard streaming output cap, contains descendants that detach into another session on explicitly supported hosts, detects source-tree mutation, and emits deterministic text, JSON, or Markdown evidence.
- Distinguish `pass`, `fail`, `error`, `unsupported`, and `not-selected`; use stable exit codes and never translate missing native prerequisites into a pass.
- Include the curriculum contract in the core CI profile and make CI consume named profiles while retaining explicit, least-privilege domain jobs.
- Add behavior tests for schema failures, selection, ordering, time/output limits, runtime process-observability loss, cleanup, public-field redaction/rejection, source mutation, prerequisite handling, workflow-key drift, and byte-stable reports.
- Document the runner as evidence aggregation only: it does not approve pedagogy, translation, accessibility, provenance, compatibility, or performance.

Goals are one reviewable command contract, reproducible evidence, and local/CI alignment. Non-goals are a hostile-code sandbox, a package manager, automatic plugin discovery, full native builds in the lightweight gate, or replacement of existing validator CLIs and human release gates.

Migration keeps the current commands callable and first routes their exact behavior through named matrix entries. Rollback consists of returning the workflow and guide to those direct commands and deleting the new additive runner/matrix; no content or review state is transformed.

Done means the core and three explicit domain profiles are enforced before selection, curriculum validation runs in CI, identical fixtures produce byte-identical normalized reports, detached-descendant/output-flood/TMPDIR/profile-tampering probes fail closed, the source snapshot is unchanged, and all affected OpenSpec changes validate strictly.

## Capabilities

### New Capabilities

- `deterministic-quality-evidence`: Versioned selection, bounded execution, truthful result states, deterministic reports, and CI/maintainer alignment for repository quality evidence.

### Modified Capabilities

None. There are no archived base specs; active `add-book-quality-gates` remains the owner of individual validator rules and least-privilege policy.

## Impact

- New files under `tools/` for the matrix, runner, tests, and maintainer documentation.
- `.github/workflows/book-quality.yml` consumes explicit profiles and gains the missing curriculum check without broadening permissions.
- `tools/BOOK_QUALITY_REVIEW.md` references generated evidence instead of a hand-maintained command matrix.
- Coordinates with `add-book-quality-gates` for validator ownership, with `harden-course-curriculum-and-maintainer-skills` for domain checks, and with `restore-multilingual-content-parity` by preserving every human review boundary.
- Main risks are false confidence, unsafe command extensibility, hidden source mutation, and oversized/sensitive logs. The design must use a closed command vocabulary, relative/redacted summaries, hard bounds, explicit selection, and regression tests.
