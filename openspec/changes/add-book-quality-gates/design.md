## Context

The implemented repository has 22 chapters, two appendices, five language files per unit, and six root indexes. It currently has no shared build, CI, snippet runner, or companion-source test suite. `BOOK_STYLE.md` defines requirements that range from exactly machine-checkable invariants, such as a byte-identical English root mirror, to judgments that require a fluent technical reviewer, such as natural translation and pedagogical sufficiency.

At design time, the three chapter proposals reserved chapters 23, 24, and 25 and each proposed a local `validate_docs.py` or equivalent. Their resulting capabilities have intentionally different domain verification: bounded localhost protocol tests for networking, compiled artifact and ABI checks for C++, and Cargo/maturin/package checks for Rust. Their generic Markdown, localization, accessibility, and hygiene logic must not diverge whether the originating changes are active or archived.

This change introduces the missing shared layer. It is proposed truth only: none of the files or controls below is implemented until the change is approved and its tasks are completed.

## Goals / Non-Goals

### Goals

- Provide one deterministic, standard-library entry point for repository-wide structural quality.
- Reject regressions in links, navigation, Markdown structure, snippet claims, RTL wrapping, accessible image/table structure, and repository hygiene.
- Make runnable claims traceable to bounded execution or tested companion sources.
- Let domain chapters register focused verification without copying the root parser and diagnostics.
- Adopt gates without requiring an unsafe all-at-once rewrite of legacy chapters.
- Record provenance decisions consistently and expose unresolved inventory items without making legal assertions.
- Give contributors equivalent local and CI commands with actionable, stable diagnostics.

### Non-Goals

- Prove that a lesson is motivating, age-appropriate, factually correct, or understandable.
- Prove semantic translation parity from heading, token, or word counts.
- Act as a hostile-code sandbox or execute untrusted pull-request snippets safely.
- Check external URL availability, licenses, or ownership over the network.
- Replace fluent technical/linguistic review, chapter-specific tests, compilers, package builds, or artifact verification.
- Rename existing directories, rewrite legacy content, or implement the three proposed advanced chapters.
- Introduce a Markdown framework, third-party parser, test dependency, or generated documentation site.

## Architecture Snapshot

### Component map

- `tools/validate_book.py`: single standard-library production entry point, Markdown scanner, rule registry, snippet runner, baseline comparator, plugin dispatcher, and diagnostic renderer.
- `tools/book_quality.toml`: versioned configuration for content roots, permitted exclusions, time/output limits, artifact rules, attribution path, and plugin API version. It is parsed with `tomllib`.
- `tools/book_quality_baseline.json`: reviewed legacy issue fingerprints plus rule/config schema versions; it contains no broad path or rule suppressions.
- `tools/tests/test_validate_book.py`: `unittest` behavior suite. Small repositories are created in `tempfile.TemporaryDirectory`; focused static fixtures are used only when byte layout matters.
- `ATTRIBUTIONS.toml`: machine-readable inventory of provenance decisions and required notices for adapted or third-party material.
- `.github/workflows/book-quality.yml`: least-privilege CI that runs unit tests, changed-scope/full validation, and diff hygiene.
- `<unit>/tools/bookcheck_plugin.py`: optional chapter-owned adapter for domain checks. Generic Markdown rules remain at the root.

### Key boundaries

- The root validator reads repository content and reports diagnostics; it does not rewrite Markdown, delete artifacts, update the baseline, or alter attribution records during a normal run.
- Generic checks own repository structure, Markdown, navigation, snippet metadata, bounded Python execution, attribution-record consistency, and hygiene.
- Plugins own only behavior that needs domain knowledge or external toolchains. A plugin cannot waive or downgrade a root diagnostic.
- Structural comparison produces review signals, not a claim of semantic multilingual equivalence. Fluent human review remains an acceptance gate.
- Provenance status is supplied by a human reviewer. Automation checks presence and consistency and says “review required”; it never says that material infringes copyright.

### Data and control flow

1. Resolve the repository root from the script location, load versioned TOML configuration, and discover root indexes plus unit `README.md` files without following symlinks outside the repository.
2. Parse all required Markdown for global invariants; when `--changed-from` is present, use `git diff --name-only -z` to identify the stricter changed scope.
3. Run deterministic generic rules and collect structured diagnostics rather than failing on the first issue.
4. For opted-in Python snippets, create an isolated temporary working directory and run a bounded subprocess. For `source-ref`, validate the path and named verifier or plugin hook.
5. When explicitly requested, execute each plugin in a bounded child process and merge its diagnostics under a namespaced rule ID.
6. Compare current legacy fingerprints with the checked-in baseline, reject new/stale inconsistencies according to ratchet rules, sort diagnostics, and render text or JSON.

## Decisions

### Decision: Stable CLI and diagnostic protocol

The accepted local commands are:

```text
python -B -m unittest discover -s tools/tests -v
python -B tools/validate_book.py
python -B tools/validate_book.py --changed-from <git-ref>
python -B tools/validate_book.py --format json
python -B tools/validate_book.py --plugin <relative-plugin-path>
```

The default validates the full repository against the baseline. `--changed-from` still runs global invariants, then requires every changed or added in-scope file to satisfy current rules without new baseline debt. Deleted/renamed stable content produces a diagnostic unless an approved migration config exists.

Each diagnostic contains `schema_version`, `rule_id`, severity, repository-relative path, line/column when known, a safe message, and an actionable remediation. JSON output is sorted and contains no absolute paths, timestamps, secret values, or platform-dependent tracebacks. Exit code `0` means no unbaselined error, `1` means quality failure, and `2` means configuration, plugin-protocol, or internal failure.

Alternative considered: multiple purpose-specific scripts. Rejected because parsing and suppression semantics would drift, although internal functions remain independently testable.

### Decision: Explicit discovery and navigation contracts

A unit is a non-root directory containing canonical `README.md` and not excluded by exact configuration. It must also contain `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md`. Root must contain its six current indexes, and `README.md` must be byte-for-byte identical to `README.en.md`.

Selectors use the standard order English, Spanish, Catalan, Swedish, Arabic; each target remains in the same unit and the current language is not a self-link. Root index entries must target their matching localized file, and links are accepted only after the target path exists. External URLs are syntax-checked but never fetched.

Relative Markdown and HTML links/images are resolved without escaping the repository. Percent-encoding and fragments are normalized; local fragments must match a deterministic GitHub-compatible heading slug or explicit HTML anchor. Links inside fenced code are ignored.

### Decision: Conservative Markdown and accessibility checks

The scanner is a small, documented state machine rather than a complete CommonMark implementation. It checks one H1, no skipped heading levels, unique linkable heading anchors, balanced fences with matching delimiter length/type, selector position, and a single balanced outer RTL wrapper in Arabic files. Fences and inline code shield their contents from link/HTML rules.

Machine-checkable accessibility rules require descriptive non-empty link text, non-empty image alt text, and a nearby prose text equivalent for meaningful visuals. Explicitly decorative images use a documented marker and empty alt. Markdown tables require a valid header separator; tables above the configured complexity threshold require a nearby list/text alternative marker. Heuristic warnings about color/position/icon-only wording are review prompts, not proof of inaccessibility. A human reviewer remains responsible for whether alt text and prose are actually equivalent and useful.

Alternative considered: a third-party CommonMark/HTML/accessibility stack. Rejected for the first iteration to preserve offline CPython 3.11 operation; parser limitations are documented and covered by fixtures.

### Decision: One explicit fenced-block taxonomy

Every fenced block in new or changed content has a language token and exactly one classification token in its info string:

```text
runnable | expected-error | compile-only | source-ref | todo | illustrative | output
```

- `runnable`: complete trusted Python expected to exit successfully; it may be followed by one `output` fence for exact normalized output.
- `expected-error`: complete trusted Python expected to fail with a declared diagnostic substring and bounded non-zero exit.
- `compile-only`: syntax-checkable Python that is never executed; other languages require a source reference/plugin.
- `source-ref`: explanatory excerpt backed by a repository-relative companion path and a stable verifier or plugin check ID.
- `todo`: intentionally incomplete learner work and never executed.
- `illustrative`: non-runnable pseudocode, commands, config, or partial code; prose must not call it runnable.
- `output`: inert expected output immediately associated with a preceding runnable or expected-error block.

Optional metadata is supplied by one immediately preceding comment using the versioned `bookcheck` grammar, for example `<!-- bookcheck: timeout=5 expect-error="ValueError" -->` or `<!-- bookcheck: path="chapter-x/examples/a.py" check="chapter-x:unit" -->`. `shlex` parses the key/value payload; duplicate/unknown keys fail. Classification sequence and source-reference identity become structural parity signals across language siblings, while semantic parity still requires human review.

### Decision: Bounded execution is a guard, not a sandbox

Only `python runnable` and `python expected-error` blocks execute in the generic runner. Shell, network, multi-process, native, package-install, and dependency-bearing examples must be `illustrative` or `source-ref` and use a domain plugin/companion test.

The runner uses the current CPython with `-I -B`, an empty temporary working directory, no stdin, a minimal allowlisted environment, a five-second default and ten-second hard maximum, a 64 KiB combined-output limit, and process-group termination on timeout. Declared fixture copies must stay within the repository and are copied read-only into the temporary tree. Obvious network, subprocess, privilege, destructive filesystem, credential, and unbounded-loop operations are rejected before execution.

These controls reduce accidents in trusted educational snippets; Python introspection can bypass static checks, so they are not a security boundary. CI must not execute untrusted changed snippets from forked code with elevated tokens or secrets. The workflow has read-only permissions and no credentials beyond the checkout token.

### Decision: Versioned, explicit plugin hooks

A plugin exposes `register(registry)` and declares a unique ID, API version, check IDs, prerequisites, and bounded timeout. The root invokes an explicitly selected plugin in a child process, provides repository-relative immutable context as JSON, and accepts only schema-valid diagnostics. Plugin IDs namespace every result; crashes, malformed output, path escape attempts, or timeouts fail closed. Plugins cannot suppress generic rules or write into the source tree.

Chapter verifiers may call the root CLI with their plugin or expose the plugin through their existing orchestrator. Network plugins own localhost protocol/lifecycle tests; C++ owns compiler/CMake/build/wheel/ABI tests; Rust owns rustup/Cargo/maturin/wheel tests. The generic CI job does not silently skip a requested plugin with unmet prerequisites: it fails with an actionable preflight diagnostic. Plugins not requested are listed as not run, not reported as passing.

### Decision: Artifact and sensitive-data hygiene

Hygiene enumerates tracked, untracked, and ignored paths using NUL-delimited Git output. It rejects unexpected `__pycache__`, bytecode, virtual environments, test caches, coverage, build/dist trees, wheels/sdists, Cargo/CMake/native outputs, temporary certificates/keys, editor files, and platform trash. Exact allowlists live in TOML and cannot use repository-wide wildcards.

Bounded content rules detect likely live credentials or personal learner data in text files. Reports contain only path, location, and rule ID; matched material is redacted. Clearly fake teaching values require an explicit narrow fixture allowlist. The validator is read-only and never deletes a suspected secret or artifact.

### Decision: Exact baseline ratchet for legacy debt

The initial implementation runs a read-only full audit, reviews false positives, and checks in exact issue fingerprints. A fingerprint contains rule version, rule ID, repository-relative path, normalized offending construct digest, and duplicate ordinal—not an unstable line number. Baseline metadata records its schema/config version and the review commit.

Current issues must be a subset of the baseline, and new/changed files may not introduce a new issue. When an old issue disappears, validation reports the baseline entry as stale until it is removed in the same change; this makes debt reduction permanent. `--update-baseline` may only remove resolved fingerprints and cannot accept new or changed failures. Any exceptional increase requires an explicit OpenSpec-approved migration, not a command-line flag or wildcard suppression.

Alternative considered: fail the entire existing book immediately. Rejected because it would encourage broad suppressions and make unrelated improvements impractical.

### Decision: Attribution inventory checks evidence, not legality

`ATTRIBUTIONS.toml` uses a versioned schema. Entries include a stable ID, repository-relative covered paths, material kind, review status, source title/URL when applicable, author/holder as recorded by the source, license identifier or exact license text location, required notice, adaptation note, and review date. Status distinguishes `original-declared`, `licensed-recorded`, `public-domain-recorded`, and `review-required`.

The audit checks schema, path existence, duplicate coverage, required fields/notices, URL syntax, and coverage for assets or `attribution-required` markers. It does not fetch sources, infer copied prose, decide whether a license is compatible, or declare infringement. New/changed `review-required` items fail publication until a human records a decision; legacy unknowns may enter the reviewed baseline with the neutral diagnostic “provenance review required.” Required attribution prose remains near the material or in a dedicated visible section; the TOML inventory is not a substitute for license notices.

### Decision: CI is deterministic, least-privilege, and baseline-aware

`.github/workflows/book-quality.yml` runs on pull requests and protected-branch pushes. Actions are pinned to full commit SHAs with a nearby release comment, permissions are `contents: read`, job time is bounded, and commands run on CPython 3.11 or later without installing third-party packages. Pull requests fetch the base commit and run `--changed-from`; pushes run the full audit. Both run `unittest`, generic validation, and `git diff --check` for the relevant range.

The workflow emits the stable text report and may attach JSON as a non-secret artifact, but no gate is marked successful if tests, config, baseline comparison, or a requested plugin fails. Domain-toolchain workflows remain owned by the corresponding chapter changes.

## Pedagogical Quality Boundary

The validator can prove that a promised runnable block was executed under its declared contract, that each language exposes corresponding structural learning checkpoints, and that required files and navigation exist. It cannot decide whether prerequisites are explained well, hints are useful, solutions teach rather than reveal, a translation is natural, or an assessment measures the objective. Pull-request review therefore continues to use the `professor` skill and `BOOK_STYLE.md`, tracing objectives to explanation, prediction, execution, modification, edge/error recovery, solution, checkpoint, and reflection.

Counts and classification sequences are signals for review, never evidence that translations are semantically equal.

## Technical Capability Coordination

If this proposal is approved before chapter implementation:

- `teach-python-network-programming` uses the root validator plus a network plugin for bounded TCP/UDP/TLS/selector/async lifecycle checks. The root config exact-allowlists only its declared public didactic PEM fixtures under `chapter-23-network-programming/examples/certificates/`; neighboring, generated, or undeclared keys still fail hygiene.
- `teach-python-cpp-integration` keeps `verify_all.py`, `verify_native.py`, `verify_artifacts.py`, CMake/compiler/package/ABI checks, and exposes source-reference results through a C++ plugin; no duplicate generic parser remains.
- `teach-python-rust-integration` keeps Cargo/fmt/clippy/maturin/wheel/package checks and exposes source-reference results through a Rust plugin; generic documentation and hygiene remain at the root.
- All three capabilities use the shared fenced-block taxonomy and root diagnostic IDs. Their originating specs/tasks were reconciled before implementation and revalidated strictly; later archive status does not alter ownership.

If a chapter proposal is implemented first, this change initially treats its local validator as a domain tool and migrates duplicate generic checks only after equivalent root tests pass. No approved acceptance scenario is deleted; ownership changes while behavior is preserved or strengthened.

The proposed `restore-multilingual-content-parity` change may consume structural-parity diagnostics from this capability, but fluent linguistic and technical review remains its responsibility rather than being duplicated here.

## Risks / Trade-offs

- A small Markdown scanner may misread unusual CommonMark → document supported syntax, maintain focused fixtures, and fail with an actionable parser diagnostic instead of guessing.
- A large initial baseline may hide debt → exact fingerprints, no wildcard suppressions, changed-scope enforcement, stale-entry failure, and ratchet-only updates.
- Snippet execution may be mistaken for secure sandboxing → trusted-input wording, explicit unsafe classifications, no shell execution, least-privilege CI, and plugin isolation.
- Plugin code may hang, mutate, or emit malformed data → child process, temporary context, time/output bounds, schema validation, and fail-closed behavior.
- Structural parity can produce false confidence → label it a signal and require fluent technical review under the professor workflow.
- Hygiene secret scans may expose or falsely flag data → redact values, bound reads, use narrow fake-fixture allowlists, and test diagnostics.
- Attribution automation may be interpreted as a legal judgment → use neutral statuses/messages and require human provenance/license review without asserting infringement.
- Active proposals may drift during parallel work → reconcile their spec/task ownership before approval or implementation and validate every affected change strictly.
- Full scans may slow contributions → parse each file once, deterministic caches only in memory, changed-scope PR enforcement, and a bounded CI budget.

## Migration Plan

1. Freeze rule, marker, diagnostic, plugin, baseline, and attribution schemas in tests.
2. Implement the read-only validator and its positive/negative/timeout tests without changing book content.
3. Run a full audit, classify false positives, and commit a human-reviewed exact baseline plus attribution inventory; do not auto-fix or auto-waive findings.
4. Enable local full and changed-scope commands, then reconcile the three active chapter proposals to the root ownership boundary.
5. Add CI in enforcing mode only after the reviewed baseline makes the current default branch pass.
6. Reduce legacy debt in small, independently reviewed changes; remove stale baseline entries with each fix.

Rollback removes the workflow first, then the root tooling and inventory in one revert. It does not rename or rewrite course content. Chapter domain validators remain independently callable throughout migration.

## Open Questions

None blocking. Exact initial baseline findings and attribution statuses are implementation-time audit outputs and must be reviewed rather than predicted in this proposal.

## Definition of Done

- `python -B -m unittest discover -s tools/tests -v` passes and covers every rule family, both diagnostic formats, time/output bounds, baseline behavior, plugin failures, and redaction.
- `python -B tools/validate_book.py` passes against the reviewed baseline and changes no tracked or untracked repository content.
- A temporary bad fixture for each normative scenario fails with its stable rule ID; positive fixtures pass.
- `python -B tools/validate_book.py --changed-from <ref>` rejects new debt while allowing unchanged reviewed legacy debt.
- Attribution diagnostics use neutral review language and never claim infringement or license compatibility.
- Generic CI passes with pinned actions, read-only permissions, and bounded jobs.
- The three advanced chapter changes contain no duplicated generic validator implementation after reconciliation and retain their domain verification coverage.
- Fluent reviewers confirm that automated parity remains a signal rather than a replacement for semantic, pedagogical, and accessibility review.
- `openspec validate add-book-quality-gates --strict` and `git diff --check` pass.
