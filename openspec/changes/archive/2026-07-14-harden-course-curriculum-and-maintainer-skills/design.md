## Context

The repository publishes 25 numbered chapters and two appendices in five languages. The root validator, 62 unit tests, and the current 24-source/96-variant parity inventory pass, but those controls are intentionally structural and exclude the three newly published systems chapters from human-review inventory. The audit also found prerequisite use before teaching in Chapters 02–12 and concrete resource, trust, packaging, typing, and toolchain defects in Chapters 15–25.

There are no archived base specs. Implemented files are therefore the runtime truth, while `add-book-quality-gates` and `restore-multilingual-content-parity` remain active coordination artifacts. Existing unit directories, relative links, native public APIs, English mirror equality, and Arabic wrapper conventions are stable contracts. Human linguistic, accessibility, pedagogical, and provenance decisions cannot be automated.

## Goals / Non-Goals

**Goals:**

- Make the numbered beginner path genuinely completable by separating essential work from optional previews and recording an acyclic checkpoint/concept map.
- Correct the audited systems defects with executable regression evidence and explicit resource/trust/platform bounds.
- Add five concise maintainer skills that route to reusable domain references and validation commands.
- Cover every published unit in parity evidence and run each domain plugin explicitly without overstating its coverage.
- Preserve semantic parity, stable public paths/APIs, bidi readability, repository hygiene, and human release boundaries.

**Non-Goals:**

- Renumbering chapters, renaming directories, or migrating public module names.
- Completing the historical 108 human translation reviews, accessibility review, or provenance ownership decision.
- Claiming a platform, compiler, dependency graph, performance result, or license status that was not actually verified.
- Adding framework tracks, production networking, publishing packages, or replacing domain plugins with the generic Markdown runner.

## Decisions

### Decision: Keep numerical navigation and add explicit route contracts

The six root indexes retain the existing numerical table of contents and gain localized route descriptions with prerequisites, estimated sessions, outcomes, checkpoints, and stopping points. Chapters 02–12 are corrected in place so their essential route requires only already taught concepts; advanced demonstrations stay under clearly skippable previews. Chapter 11 gains a foundational functions route before higher-order functions.

An auditable standard-library curriculum contract lives in `tools/curriculum_map.toml`. A focused validator checks schema, stable paths/anchors, route order, prerequisite existence, and DAG cycles. It is evidence for maintainers, not a claim that AST detection proves learning quality.

Alternatives rejected:

- Renumbering Chapters 03–11 would make the dependency order visually cleaner but would break public URLs and every localized/inbound link.
- A route-map-only correction would leave essential checkpoints that still require hidden later concepts.
- Treating every early use as a preview would overload beginners and would not make the required work independently solvable.

### Decision: Change learner-facing content as five-language unit bundles

Canonical English defines the technical contract. Any changed objective, bound, route, exercise, solution, warning, command, or tested claim is propagated semantically to Spanish, Catalan, Swedish, and Arabic in the same implementation phase. Code identifiers remain stable unless the existing locale deliberately localizes learner-only examples. Arabic keeps one outer RTL wrapper and LTR code/paths. Root changes update six indexes atomically and keep `README.md == README.en.md` byte-for-byte.

Automated reconciliation refreshes digests and returns affected review records to pending/stale. It never writes linguistic or technical approval.

Alternative rejected: English-only repairs followed by an unspecified translation pass would knowingly publish different safety and prerequisite contracts.

### Decision: Use five skills with progressive disclosure, not micro-skills

The new skill set is exactly:

1. `verify-python-learning-assets`;
2. `engineer-python-network-labs`;
3. `python-packaging-release`;
4. `engineer-python-native-interop`; and
5. `maintain-book-quality-tooling`.

Each is initialized by the installed skill-creator, has generated UI metadata, a short core workflow, and direct one-level references only where domain detail is material. Native interop uses conditional `cpp.md` and `rust.md` references so common oracle/binding/package discipline is shared without loading or conflating both toolchains. Existing `professor` and `book-editor` gain narrowly scoped course-level references/workflow; unrelated framework and infrastructure skills are untouched.

Alternatives rejected:

- Separate TLS, CMake, pybind11, maturin, testing, accessibility, and translation skills would duplicate ownership and increase trigger ambiguity.
- One generic “course expert” skill would hide incompatible network/native safety and toolchain requirements.
- Skills alone cannot enforce deterministic invariants, so curriculum/parity/plugin rules remain repository tools and tests.

### Decision: Correct executable systems contracts code-first

For each audited systems defect, tests or deterministic verification are changed before learner prose:

- HTTP accepts only the documented path/media type and `0 <= Content-Length <= MAX_BODY` before an exact bounded read.
- Logging explicitly limits `dictConfig` to trusted application-owned configuration or an allowlisted schema.
- Asyncio teaches task ownership, `TaskGroup`, `asyncio.timeout`, and cancellation cleanup for Python 3.11+.
- Network state uses bounded retention, per-peer idle deadlines, bounded output, and cleanup on every exit; TLS tests avoid private CPython APIs.
- Packaging calls direct pins/`pip freeze` snapshots accurately, teaches a real `src/<package>` layout, and scopes reproducibility to clean artifact evidence.
- C++ verification observes whether sanitizer flags were actually applied, parses missing dynamic dependencies, and narrows stubtest suppressions.
- Rust preflight distinguishes MSRV from `rust-toolchain.toml`, detects MSVC or Unix compilers, preserves synchronization errors, and compares the full benchmark result.
- Introspection and appendices use real/self-contained modules, warn about executable hooks, catch expected errors narrowly, and state algorithm assumptions.

All network execution is loopback-only with ephemeral ports, deterministic coordination, and hard resource/time limits. Native builds use temporary directories and report an unsupported capability as an explicit skip only where the contract permits it.

Alternative rejected: prose-only warnings would leave runnable companion code and verifier false positives unchanged.

### Decision: Expand inventory by discovery and keep domain CI explicit

`tools/parity_review.py` discovers the same published units as the root validator rather than hard-coding Chapters 01–22. Reconciliation preserves old records, adds Chapters 23–25 as pending, and produces 27 sources/108 localized variants. Publication mode describes all published units; human review remains required.

The existing generic CI job remains standard-library-only. Separate least-privilege jobs invoke the network, C++, and Rust plugins explicitly. The plugin jobs validate the repository domain contracts; full compiler/package matrices remain separate verifier commands and may only be claimed for hosts where they ran. Source references say `not selected`, `passed`, `failed`, or explicit supported `skip` truthfully.

Alternative rejected: auto-discovering and executing arbitrary plugins inside the generic job would expand the trust/toolchain boundary and make fork CI less predictable.

### Decision: Reconcile active OpenSpec evidence without fabricating completion

The missing `openspec/AGENTS.md` is restored as a short repository guide that points to root instructions, config, and CLI-resolved artifact paths. Chapter 25 traceability is updated to match completed index integration. Active parity/quality artifacts are updated only where counts or ownership changed; human tasks remain unchecked. The new change's task list records implemented automation separately from required external sign-off.

## Risks / Trade-offs

- **[Large multilingual diff]** → Work in per-unit bundles, preserve selectors/anchors, refresh digests only after canonical and four siblings agree, and run changed/full validators after each phase.
- **[A dependency map gives false confidence]** → Treat it as a gate for declared concepts and cycles; retain professor/book-editor review for cognitive load and actual solvability.
- **[Beginner chapters remain dense]** → Bound essential routes by time/outcome and move professional material behind explicit checkpoints without deleting useful depth.
- **[Network timeout tests become flaky]** → Use readiness events, ephemeral ports, monotonic deadlines, short bounded polling, and no fixed sleeps as correctness synchronization.
- **[Native verification is host-dependent]** → Separate capability detection from pass, record exact host/tool versions, and never infer Windows/macOS from Linux.
- **[CI duration grows]** → Keep static C++/Rust plugin jobs lightweight and bounded; reserve full native builds for their existing verifier or a future provisioned matrix.
- **[Parity count update collides with active restoration]** → Preserve all prior records/statuses by path and invalidate only changed digests; update active task language from 24/96 to 27/108 without checking human work.
- **[Provenance cannot be resolved automatically]** → Keep current review-required entries and human owner task pending; new original material is recorded without making a legal conclusion.

## Migration Plan

1. Land proposal/spec/design/tasks and validate them strictly.
2. Initialize, implement, and validate the five skills; extend `professor` and `book-editor` with direct references.
3. Add the curriculum contract and tests, then correct root routes and Chapters 02–12 as five-language bundles.
4. Add regression tests and correct standard-library systems lessons, network companions, packaging text, and native companions/docs.
5. Expand parity discovery/manifest, add explicit domain-plugin CI, restore OpenSpec guidance, and reconcile traceability/active counts.
6. Run skill, curriculum, generic, parity, three plugin, chapter companion, strict OpenSpec, hygiene, and whitespace checks from a clean tree. Require every check owned by this change to pass or report its explicit supported skip, while preserving any non-zero human provenance/publication blocker owned by a coordinated active change.

Rollback is phase-based: revert the affected unit bundle and its digest refresh together; revert a skill directory and its contract entry together; revert parity code and manifest together; disable only the failing explicit domain job without weakening the generic gate. Stable paths and public APIs mean no data or consumer migration is required.

## Open Questions

- Human linguistic, rendered-accessibility, pedagogical, and provenance reviewers still need to be assigned outside this automated implementation.
- Full Windows and macOS native build runners are not available in the current local environment; their status must remain unverified until CI infrastructure explicitly provides them.
