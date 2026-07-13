# Canonical source audit · chapters 01–22 and historical appendices

Audit date: 2026-07-13

This report records the required English-source review before multilingual
acceptance. It covers the 24 historical canonical units: chapters 01–22 plus
the CLI and algorithms appendices. Chapters 23–25 belong to their own active
OpenSpec changes and are verified by their traceability reports and plugins.

`corrected` means the canonical lesson was reviewed, narrow factual,
pedagogical, safety, or accessibility defects were repaired, and the same
contract was propagated to all four localized siblings. It does **not** mean a
translation has human linguistic or technical acceptance. Those roles remain
pending in `tools/parity_manifest.json`.

## Unit outcomes

| Unit | Canonical review and repair outcome | Result |
|---|---|---|
| Chapter 01 · Introduction | Made setup portable and current, documented rollback, added prerequisite/prediction/checkpoint flow, and kept commands platform-aware. | corrected |
| Chapter 02 · Variables | Corrected the interpreter model and `bool`/numeric validation, added learning routes and assessment. The inherited provenance item remains an explicit human review gate. | corrected; provenance review required |
| Chapter 03 · Lists | Stabilized the `top3` return schema and its test; added prerequisite, prediction, routes, and rubric. | corrected |
| Chapter 04 · Dictionaries | Qualified the hashable-key contract and added prerequisite, prediction, and assessment. | corrected |
| Chapter 05 · Sets | Qualified membership as O(1) on average and made every displayed set deterministic without implying iteration order. | corrected |
| Chapter 06 · Tuples | Distinguished fixed outer structure from deep immutability and required every tuple element to be hashable when used as a key. | corrected |
| Chapter 07 · Queues | Reworked rate limiting around a validated, injected `monotonic()` clock with deterministic boundary tests. | corrected |
| Chapter 08 · Conditionals | Restored the missing `time` import and added explicit branch prediction and assessment. | corrected |
| Chapter 09 · Input | Replaced title-derived paths with a safe path contract and replaced naïve CSV splitting with the `csv` module. | corrected |
| Chapter 10 · Loops | Added explicit prerequisites/previews, bounded reasoning, prediction, and a checkpoint rubric. | corrected |
| Chapter 11 · Functions | Corrected the pipeline test import and output claims; kept the local-module test illustrative so the generic runner does not pretend to execute a missing file. | corrected |
| Chapter 12 · OOP | Closed invariant bypasses, qualified `dataclass` ordering and shallow `frozen` behavior, imported `replace`, and added beginner/professional/advanced routes. | corrected |
| Chapter 13 · Files | Moved runnable file work to temporary directories and documented safe cleanup. | corrected |
| Chapter 14 · Exceptions | Corrected `Exception` versus bare-`except` semantics and made recovery hints explicit. | corrected |
| Chapter 15 · Modules | Made the `src` layout and imports coherent, added an import test, and reclassified a non-standalone fence. | corrected |
| Chapter 16 · Environments | Added prerequisites, recovery hints, assessment, and explicit missing-secret failure. | corrected |
| Chapter 17 · Persistence | Ensured SQLite resources close transactionally and made CSV type conversion and failure behavior explicit. | corrected |
| Chapter 18 · Testing | Added prerequisites, missing hints, and an outcome-based rubric. | corrected |
| Chapter 19 · HTTP | Constrained examples to localhost with timeouts, a 1 MiB request cap, 400/413 paths, and deterministic shutdown. | corrected |
| Chapter 20 · Logging | Added safe JSON configuration recovery and bounded rotating file output. | corrected |
| Chapter 21 · Async | Made coroutine execution explicit with `asyncio.run`, completed dependencies, and demonstrated cancellation cleanup. | corrected |
| Chapter 22 · Introspection | Made object description defensive and demonstrated `Signature.bind` with positional-only validation. | corrected |
| Appendix · CLI parser | Added missing-file recovery, deterministic `argv` tests, temporary paths, and captured-log assertions. | corrected |
| Appendix · Algorithms | Corrected BFS validation/claims and the first-duplicate contract, hints, and tests. | corrected |

## Acceptance boundary

Automated validation may establish current digests, structure, runnable
behavior, safe paths, navigation, RTL shape, and plugin results. It cannot
establish fluent translation, rendered bidi quality, pedagogical suitability,
or provenance. The parity inventory therefore stops at
`automated-signals-pass` until competent linguistic and technical reviewers
record approval. The Chapter 02 provenance item and any attribution marked
`review-required` remain visible rather than being baselined away.

## Reproduction

Use the commands in `tools/BOOK_QUALITY_REVIEW.md`. A release candidate must at
minimum pass the tool unit tests, the generic validator under Python 3.11+, all
declared domain plugins, parity inventory validation, strict OpenSpec
validation, `openspec doctor`, and `git diff --check` from a frozen checkout.
