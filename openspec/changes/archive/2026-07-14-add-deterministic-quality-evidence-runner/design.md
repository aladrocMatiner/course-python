## Context

Quality evidence is currently invoked from four places: `.github/workflows/book-quality.yml`, `tools/BOOK_QUALITY_REVIEW.md`, individual change reviews, and ad-hoc maintainer commands. The sets already differ: the documented handoff runs `tools/validate_curriculum.py`, while CI does not. The validators also expose different output shapes, and copied pass counts or host versions become stale without a failing contract.

The repository is standard-library-first, receives untrusted pull-request code, has a dirty in-progress worktree during local review, and owns domain plugins for networking, C++, and Rust. Existing validator CLIs and plugin ownership are stable. Human linguistic, technical/pedagogical, rendered-accessibility, bidi, and provenance decisions must remain outside automation.

## Goals / Non-Goals

**Goals:**

- Put check identity, selection, prerequisites, time/output bounds, and evidence scope in one versioned reviewable matrix.
- Run named profiles with bounded child processes and fail-detect repository writes.
- Produce deterministic text, JSON, and Markdown summaries with honest result states and stable exit codes.
- Make CI and the maintainer handoff consume the same profile contract, including curriculum validation.
- Preserve generic/domain ownership and report observed host evidence without turning it into a compatibility claim.

**Non-Goals:**

- Treat repository code as hostile safely; the runner is not an OS sandbox.
- Discover or execute plugins, compilers, package builds, benchmarks, or network targets implicitly.
- Replace any validator CLI, domain verifier, OpenSpec, or human release gate.
- Claim Windows/macOS, native ABI, free-threaded Python, performance, translation, accessibility, or provenance evidence that was not executed and reviewed.

## Decisions

### Use a versioned TOML matrix with a closed adapter vocabulary

`tools/quality_matrix.toml` uses schema version 1. It declares global hard limits, stable check IDs, explicit profiles, adapter names, prerequisite executable names, and only adapter-specific safe fields. Adapters map to known argv templates in `tools/run_quality.py`; the matrix cannot contain shell fragments or arbitrary command strings. Paths are repository-relative, cannot traverse or follow a symlink outside the root, and plugin paths must be explicit.

The initial profiles are `core`, `network-domain`, `cpp-domain`, `rust-domain`, and `handoff`. The parser itself enforces their mandatory membership and adapter/path bindings before selecting a profile, so `core` cannot remove the tests that protect the matrix. `core` selects tool tests, curriculum, parity, and generic book validation. Each domain profile selects exactly one named plugin invocation. `handoff` selects the core/domain evidence plus strict validation of all OpenSpec changes and a whitespace check. New domains require a reviewed schema/contract extension; networking/C++/Rust are not a permanently closed domain list.

An arbitrary argv list was rejected because it would turn a data file into a general CI command launcher. Autodiscovery was rejected because adding a file could silently broaden execution and evidence claims.

### Make selection and result state explicit

The CLI accepts a named `--profile` or repeated explicit `--check` IDs, with `core` as the documented default. It lists every declared check in stable matrix order. Selected checks become `pass`, `fail`, `error`, or `unsupported`; unselected checks remain `not-selected`. A missing prerequisite is `unsupported`, never `pass`. A requested but unknown profile/check is a usage/configuration error.

Exit `0` means every selected check passed. Exit `1` means at least one selected quality check executed and failed. Exit `2` means configuration, prerequisite, timeout, output, process-tree, mutation, or other execution evidence is incomplete or unsafe. Infrastructure errors dominate quality failures for the aggregate exit while every completed check remains visible.

`--changed-from <revision>` is forwarded only to adapters that declare changed-scope support. It never narrows tool tests, curriculum, or parity inventory. The workflow keeps its explicit pull-request and push conditions so a push performs full generic validation.

### Reuse bounded process primitives, but require truthful platform capability

Every command is an argv sequence executed without `shell=True`, with stdin closed, a minimal non-secret environment, a repository root working directory, a hard timeout, and a combined output cap. Output flows through a bounded pipe/reader that retains no successful raw log and detects the first byte beyond the cap; it never persists an arbitrarily oversized regular file. Temporary HOME/output state is created only in a resolved directory outside the repository, independent of a caller-controlled `TMPDIR`.

An ordinary POSIX process group is insufficient because a descendant can call `setsid()`. A host is supported only when the executor has a tested subtree primitive that observes/reaps descendants after session detachment (Linux subreaper plus `/proc` tracking in schema v1). Observability is checked before child launch and continuously while it runs: an empty, malformed, unreadable, or partial map that omits a live direct/known PID is an infrastructure error. Cleanup freezes and kills every PID already observed; if observability was lost, the result says that cleanup of an unobserved descendant cannot be proved and never reports a pass. Other hosts report `unsupported` before repository code runs. A single-process or group-only fallback must not be reported as equivalent containment.

A content-hash snapshot of regular, symlink, and special file entries under the checkout (tracked, untracked, and ignored, excluding `.git`) is compared before and after each selected check. It bounds total file bytes, not directory metadata or the count of empty files; those are documented trusted-code limits rather than a hostile-input sandbox. A detected change is `error`, remaining execution stops, and the runner never attempts to restore user files. Temporary output lives outside the repository and is removed on success and failure.

This is fail-detection for trusted project code, not containment for malicious code. CI retains `contents: read`, no secrets, pinned actions, and job timeouts.

### Normalize evidence instead of copying raw logs

Schema-v1 JSON contains the selected profile/check IDs, overall status, revision when available, observed Python/platform identity, and a stable ordered result for every check. It contains no timestamps, durations, temporary/absolute paths, environment values, or successful raw logs. Matrix-owned public scope/boundary fields reject tokens, terminal controls, and absolute POSIX/drive/UNC paths before execution. Result details are bounded, single-line, normalized, and redact those values even when paths contain spaces; raw output is never evidence of a secret-safe channel.

Text and Markdown are projections of the same result model. Markdown uses status words and a textual table rather than color alone, and includes the automation/human boundary. Identical repository, revision, matrix, selection, environment identity, and fixture output therefore produce byte-identical JSON/Markdown.

Storing generated reports in the repository by default was rejected because results would become stale and create source mutation. The CLI writes stdout; a caller may explicitly capture it as an external CI artifact.

### Keep validator ownership and CI jobs visible

The runner aggregates exit evidence; it does not reinterpret validator diagnostics. `validate_book.py` still owns generic rules and the plugin protocol, `parity_review.py` owns review-state invariants, and `validate_curriculum.py` owns declared prerequisite evidence. Domain jobs remain separately named and select one domain profile, so a generic pass cannot imply a plugin ran.

The CI workflow replaces duplicated direct quality commands with the `core` profile and three explicit domain profiles. Workflow contract tests pin those selections, require the curriculum entry in `core`, reject `continue-on-error`, and preserve least privilege. Action-key parsing covers ordinary whitespace, quoted YAML keys, and inline mappings so a tag cannot evade the immutable-ref check through formatting. Heavy native/package verification remains outside these lightweight jobs until separately provisioned and evidenced.

## Risks / Trade-offs

- [A green aggregate could be mistaken for publication approval] → Every format states its evidence scope and pending human gates; no report mutates review/provenance state.
- [The runner becomes a second validator] → Adapters preserve child exit semantics and do not duplicate rule logic.
- [Configuration becomes executable suppression] → Closed schema, exact IDs/paths, no wildcards or arbitrary argv, and fail-closed unknown fields.
- [Large or sensitive child output leaks] → Hard cap, redaction, no pass logs, bounded failure excerpts, and minimal environment.
- [A child leaves work or descendants behind] → Per-check content snapshot, tested detached-session subtree cleanup, explicit unsupported platforms, and adversarial negative regressions.
- [Hand-maintained reports still drift] → The guide points to the runner output; contract tests compare workflow selections to the matrix.
- [The full handoff takes longer] → Profiles keep the default core small and domains explicit; checks continue after ordinary failures to return one useful summary.

## Migration Plan

1. Add matrix/parser/model tests and validate the current direct commands as adapter fixtures.
2. Add the runner and prove positive, failure, infrastructure, mutation, cleanup, and deterministic-output cases.
3. Route the workflow through `core` and the three domain profiles; keep permissions/actions/job bounds unchanged.
4. Update the maintainer guide and run both direct commands and profiles once to prove equivalent ownership and exit behavior.
5. Roll back by restoring the direct workflow/guide commands and removing the additive runner/matrix. Existing CLIs and content require no migration.

## Open Questions

None for schema v1. Cross-platform/native matrices and persisted CI artifacts require separate proposals and actual runner evidence.
