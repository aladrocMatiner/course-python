## Context

The repository publishes 25 numbered chapters and two appendices in five unit languages, plus six root indexes. The declared graph is acyclic and the generic quality tooling is already read-only and prefix-based, but the content audit found three prerequisite leaks and three missing bridges:

- Chapter 1 asks a first-time learner to create a file without teaching the editor/directory/run/traceback loop.
- Chapter 7 requires `from collections import deque` before any required import lesson, while Chapter 2 does not fully introduce `bool`, `None`, comparison results, or the promised safe float comparison.
- Comprehensions/iterables/generators and annotations appear as previews; Chapters 24–25 later require much stronger iterator, typing, package, and verification concepts.
- Route checkpoints are independent; only domain-specific Chapters 23–25 have capstones, so the practical route has no single artifact that proves integration.

The active `restore-multilingual-content-parity` change has completed its schema-v2 and packet implementation for 27 canonical/108 locale leaves, while all human reviews remain pending. The active `add-book-quality-gates` change still owns historical provenance decisions. This change must add content without stealing either human-review or provenance authority.

Learners are motivated beginners, including readers around age 14. Essential work remains CPython 3.11+, local/offline, bounded, and standard-library-first. Existing paths and anchors are public editorial API.

## Goals / Non-Goals

**Goals:**

- Close the three prerequisite leaks in Chapters 1, 2, and 7 without renaming existing headings or paths.
- Publish three complete new units with exact five-language topology and independently stoppable routes.
- Add executable, deterministic companion evidence for iteration, typing runtime contracts, capstone behavior, and the capstone distribution artifact.
- Extend the declared graph and route prose so numerical catalogue order remains stable while pedagogical order is explicit.
- Reconcile parity evidence additively to 30 sources/120 locales and leave every new human gate pending.

**Non-Goals:**

- General threads/processes, security curriculum, profiling, frameworks, deployment, package-index publication, or a native build matrix.
- Renumbering Chapters 01–25, changing their public URLs, or making Chapters 24/25 prerequisites of one another.
- Treating a type checker, structural match, model translation, or passing test as human approval.

## Decisions

### 1. Use three new stable paths but a non-numerical learning route

Create:

- `chapter-26-iteration-generators`
- `chapter-27-python-typing`
- `chapter-28-professional-capstone`

The table of contents keeps numerical order after Chapter 25. Route prose and `tools/curriculum_map.toml` place Chapter 26 after the Chapter 11 foundational checkpoint, Chapter 27 after Chapters 15/18/22/26 and before either native hero route, and Chapter 28 in stages after Chapters 12, 18, and optionally 23. Chapter 28's practical work may begin after Chapter 18, but its logging-privacy sub-checkpoint and complete practical rubric require the Chapter 20 logging checkpoint. This follows the stable-path rule and avoids renaming earlier directories.

Alternative rejected: insert and renumber chapters before 23. That would break public URLs and every localized/navigation/evidence reference.

### 2. Keep early corrections as additive subsections

Do not rename existing headings. Add the same semantic subsection at the corresponding dependency point in all five siblings:

- Chapter 1: working directory, editor versus REPL, save/run, deliberate `NameError`, read the final traceback line, repair, rerun.
- Chapter 2: `bool`, comparison expressions, `None` as an absence sentinel, `==` versus `is None`, truth values as a preview of Chapter 8, `math.isclose`, and optional `Decimal` only as a named later tool rather than required work.
- Chapter 7: `import module`, `from module import name`, standard-library documentation, accidental shadowing, and `python -m`, using `collections.deque` as the concrete outcome.

Alternative rejected: create a separate imports chapter. The essential concept is small and belongs immediately before its first required use; package design remains owned by Chapter 15.

### 3. Give each new unit an explicit route boundary

Chapter 26:

- Essential: readable list/dict/set comprehensions plus `enumerate` and `zip` on small materialized inputs.
- Professional: iterable versus iterator, `iter`, `next`, exhaustion, one-shot behavior, and recovery by obtaining a new iterator.
- Advanced optional: generator expressions, `yield`, bounded lazy pipelines, cleanup, and why laziness does not make an infinite input safe by itself.

Chapter 27:

- Essential: annotations for parameters/returns/collections, unions, `None`, narrowing, and the fact that annotations do not enforce runtime values.
- Professional: `Callable`, `TypedDict`, `Protocol`, `Self`, and basic generics against a small inventory domain.
- Advanced optional: one pinned development-tool snapshot for an explicitly scoped checker run, negative fixtures with stable error categories rather than full version-specific text, and a clean recovery run.

Chapter 28:

- Foundation stage after Chapter 12: in-memory order domain and service.
- Practical stage after Chapter 18: SQLite repository, CLI, configuration, logging, and normal/boundary/invalid/recovery tests.
- Systems extension after Chapter 23: bounded localhost adapter that reuses the domain contract; it is optional and must not become a packaging prerequisite.
- Hero packaging stage: pure-Python `pyproject.toml`, sdist/wheel build, archive inspection, wheel rebuilt from sdist, clean install, foreign-working-directory import, CLI smoke, and cleanup. No upload.

Every stage maps features to already taught checkpoints. Assessment introduces no new framework or programming model.

### 4. Use companion sources as the executable authority

Canonical paths:

- `chapter-26-iteration-generators/examples/iteration_pipeline.py` and `tests/test_iteration_pipeline.py`
- `chapter-27-python-typing/examples/typed_inventory.py`, runtime tests, checker-positive and checker-negative consumers, plus a bounded verifier
- `chapter-28-professional-capstone/examples/order-tracker/` with `src/`, `tests/`, `pyproject.toml`, and `tools/verify_artifact.py`

Markdown excerpts use exact `source-ref` metadata when behavior belongs to a companion. Small standard-library snippets may be `runnable` or `expected-error`. TODO, output, shell, TOML, and partial typing examples retain their truthful classifications.

The generic validator owns Markdown, navigation, localization shape, eligible snippets, and source-reference registration. A single explicit `learning-bridges` plugin owns the disposable beginner contracts, bounded Chapter 26–28 source suites, checker preflight, and the Chapter 28 artifact-prerequisite preflight. Its exact bytes join the publication sign-off quality-contract digest so a later plugin change invalidates the downstream consumer instead of leaving apparently current sign-off inputs. Full artifact verification remains an explicit packaging command because it requires provisioned build inputs. Missing checker/build prerequisites are reported as prerequisite missing, never pass.

Alternative rejected: execute all snippets or builds from generic validation. That would widen the generic trust boundary and make basic checks depend on third-party tools.

### 5. Treat the capstone package as an artifact, not a source checkout

The capstone uses a `src` layout, standard-library runtime dependencies, explicit console entry point, package data only when declared, and no learner identity. Verification creates independent temporary roots for the source snapshot, build output, unpacked sdist, clean install, foreign working directory, and isolated home/cache. It inspects metadata and archives, rebuilds a wheel from the sdist, installs the exact wheel, runs `pip check`, imports outside the checkout, exercises the CLI and domain cases, and removes every temporary artifact.

Build-system requirements are separate from runtime requirements. Any development pin is described as a host-specific snapshot, not a universal lock. Wheel tags remain declarations, not proof of untested hosts.

### 6. Publish localization and navigation atomically

Canonical English and companion behavior stabilize first. Spanish, Catalan, Swedish, and Arabic siblings preserve headings, objectives, code contracts, TODOs, cases, diagnostics, solutions, rubrics, and links; code identifiers remain unchanged. Arabic uses exactly one outer `<div dir="rtl">` and LTR containers for code/commands where needed.

Only after all 15 new Markdown files and companion targets exist do all six root indexes receive route and table-of-contents links. `README.md` is copied byte-for-byte to `README.en.md`. Automated parity is evidence of shape and current digests only; fluent review remains pending.

### 7. Expand topology additively and invalidate only affected evidence

The book configuration already discovers `chapter-*`; add the three units to `tools/curriculum_map.toml`, then run the explicit parity write/reconciliation path. The resulting store has 30 source leaves, 120 locale leaves, and one root publication leaf. Existing leaf human fields are preserved only when their bound digests/profile/provenance remain current. Changed Chapters 1, 2, and 7 become stale/pending through normal digest rules; three new units start pending. Root navigation changes invalidate the root packet and stored sign-off input.

The sign-off template is regenerated as canonical `pending` for current inputs. No reviewer role, date, note, or approval is invented.

Alternative rejected: maintain a second three-unit manifest. Publication topology and final sign-off must have one authority.

### 8. Active-change ownership

This change depends on `restore-multilingual-content-parity` Tasks 1.4 and 1.5. It owns only the additive 30/120 migration and reviews for the three new units. The restoration change continues to track the original 27 units and must consume the new current topology at final publication; any exact-count planning text that would otherwise contradict implemented truth is reconciled before handoff. `add-book-quality-gates` remains the sole owner of its seven historical provenance decisions.

## Risks / Trade-offs

- **[Risk] Fifteen new lessons plus changes to fifteen existing siblings increase review load.** → Keep code contracts identical, generate deterministic packets, separate language work, and leave all human gates pending.
- **[Risk] Numerical order differs from pedagogical order.** → Preserve catalogue order but publish exact route sequences and prerequisite links in every language.
- **[Risk] The capstone becomes a hidden bundle of new concepts.** → Stage it at Chapters 12/18/23, map each feature to a prior checkpoint, and keep each stage independently complete.
- **[Risk] Checker diagnostics vary.** → Assert stable categories/exit behavior, pin the tested snapshot for professional evidence, and avoid full diagnostic golden text.
- **[Risk] Packaging downloads or caches contaminate evidence.** → Use provisioned inputs, isolated temporary directories, explicit prerequisite states, repository snapshots, and cleanup assertions.
- **[Risk] New topology makes the existing pending sign-off stale.** → Regenerate only the pending consumer after all content/config changes stabilize; never rewrite approved evidence because none exists.
- **[Risk] Scope grows into the deferred second wave.** → Specs exclude general concurrency, security, profiling, frameworks, deployment, and index publication.

## Migration Plan

1. Add and validate OpenSpec artifacts; verify overlap and exact ownership.
2. Implement canonical Chapter 1/2/7 subsections and companion sources/tests for Chapters 26–28.
3. Run narrow executable and artifact checks; correct canonical behavior before translation.
4. Create four localized siblings for every touched/new unit and run structural/selector/RTL checks.
5. Update all six indexes and the curriculum graph atomically; validate the graph.
6. Reconcile the partitioned parity store to 30/120, verify locality/invalidation, emit review packets, and regenerate pending sign-off inputs.
7. Run full tests, generic/domain profiles, strict OpenSpec, hygiene, and whitespace checks.
8. Commit planning, content, and integration in logical units; push accessible remotes.

Rollback removes the three unit trees, their route/index/checkpoint entries, and their 15 evidence leaves in one revert, then reconciles Chapters 1/2/7 and root digests. Existing 27-unit content and evidence remain addressable throughout.

## Open Questions

None. Visibility/publication approval and human review decisions intentionally remain external gates; package-index upload is outside this change.
