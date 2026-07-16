# Appendix C sources and provenance record

## Review scope

This inventory was prepared on **2026-07-16** for the canonical English draft,
its planned localized siblings, and its local companions. A date records the
research cut; it is not a promise that an unversioned source will never change.
Technical execution and human review outcomes are recorded separately in
[VERIFICATION.md](VERIFICATION.md).

The current authoring declaration is that the Appendix C lesson story,
explanations, exercises, decision records, tables, text diagrams, fake data,
tests, and companion code are being created for this repository rather than
adapted from third-party prose, exercises, diagrams, or code. Pattern names and
standard-library API names are established terminology. This declaration still
requires independent provenance and license review; it is not a legal or
publication approval.

## Claim-to-source map

| ID | Claim or terminology used | Primary source reviewed | Use and retained boundary |
|---|---|---|---|
| SRC-01 | bibliographic origin and conventional creational/structural/behavioral pattern names | Gamma, Helm, Johnson, and Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software*, Addison-Wesley, 1994; [publisher record](https://www.pearson.com/en-us/subject-catalog/p/design-patterns-elements-of-reusable-object-oriented-software/P200000009480/9780321700698) | Terminology and bibliographic influence only. No prose, catalog entry, code, or diagram is copied or adapted. Python-specific decisions and examples are original-course drafting pending review. |
| SRC-02 | `unittest.TestCase`, fixtures, assertions, discovery, and expected-exception testing are standard-library testing mechanisms | [Python 3.11 `unittest` documentation](https://docs.python.org/3.11/library/unittest.html) | Supports the short Chapter 18 concepts-to-`unittest` syntax bridge. The illustrative job test is not copied from the documentation. |
| SRC-03 | `time.monotonic()` is suitable for elapsed-time differences because its clock cannot go backwards and is unaffected by system-clock updates | [Python 3.11 `time` documentation](https://docs.python.org/3.11/library/time.html#time.monotonic) | Supports the clock choice only. The 500/100/50 ms teaching bounds are this appendix's synthetic contract, not Python performance guarantees. Tests inject time. |
| SRC-04 | cancellation is delivered as `asyncio.CancelledError`; cleanup belongs in `try/finally`; structured-concurrency components can misbehave when cancellation is swallowed | [Python 3.11 task-cancellation documentation](https://docs.python.org/3.11/library/asyncio-task.html#task-cancellation) | Supports cancellation propagation and cleanup reasoning. It does not prove the companion implementation. |
| SRC-05 | `asyncio.TaskGroup` owns created tasks, waits on exit, cancels siblings after a non-cancellation child failure, and may raise an `ExceptionGroup` | [Python 3.11 Task Group documentation](https://docs.python.org/3.11/library/asyncio-task.html#task-groups) | Supports the Chapter 21 reading. Appendix C does not rename every task group a Supervisor or invent a Chapter 21 check ID. |
| SRC-06 | Chapter 21 demonstrates task ownership, sibling cancellation, timeout, and cleanup | [local Chapter 21 lesson](../chapter-21-async/README.md#2-own-concurrent-tasks-with-taskgroup), [`structured_async.py`](../chapter-21-async/structured_async.py), and its tests | Existing repository material is linked and interpreted, not duplicated. It retains its own generic/manual evidence boundary. |
| SRC-07 | Chapter 23 owns framing, selectors, stream flow control, bounded peers, timeout, and cleanup | [local Chapter 23 lesson](../chapter-23-network-programming/README.md), [`selector_hub.py`](../chapter-23-network-programming/examples/telemetry/selector_hub.py), and `network:network-suite` | Appendix C reads Reactor-like responsibilities only. It does not add a listener, server, framing codec, socket Adapter, or Chapter 23 result. |
| SRC-08 | Chapter 19 contains an introductory broad retry example and Chapter 23 warns that automatic write retry can duplicate effects | [local Chapter 19 retry section](../chapter-19-http/README.md#3-simple-retries) and [Chapter 23 robustness section](../chapter-23-network-programming/README.md#6-robustness-logs-and-deterministic-tests) | Used as a progression contrast. Appendix C's retry-safety and deduplication contract is stricter and is verified only by its fake dependency. |
| SRC-09 | Iterator/Generator, Repository, and service-layer depth already have course owners | [Chapter 26](../chapter-26-iteration-generators/README.md), [Chapter 17](../chapter-17-persistencia/README.md#4-a-simple-repository), and [Chapter 28](../chapter-28-professional-capstone/README.md#stage-1-foundation-immutable-domain-and-in-memory-service) | Cross-links only. No companion implementation is copied into Appendix C. |

## Original-work and adaptation inventory

| Material | Current declaration | Review state |
|---|---|---|
| job-runner story, shipping transfer exercise, fake identifiers, and decision-record prompts | drafted for this course; no personal or production data | independent provenance review pending |
| family/problem indexes and route graph | original selection and organization for this curriculum; conventional pattern names retained | pedagogical and provenance review pending |
| direct/core companions and tests | present repository-authored standard-library implementation; 21 focused tests pass in the recorded runtime matrix | independent authorship/provenance/license confirmation remains pending |
| resilience/capacity/Pub/Sub companions and tests | corrected repository-authored standard-library implementation; 47 focused tests pass on CPython 3.11.14, 3.12.12, 3.13.11, and 3.14.2; independent adversarial review reports no CRITICAL/WARNING finding | machine semantics are closed for this contract; independent authorship/provenance/license confirmation remains pending |
| minimal `patterns` plugin and synthetic selection tests | present local adapter that selects core/network standard-library suites while generic tooling owns containment | seven fixtures pass; independent provenance/license confirmation and shared quality registration remain pending |
| Reactor-like and `TaskGroup` worksheets | original questions and responsibility mapping over linked local sources | review must confirm interpretation and local-source ownership |
| localized lessons | translations not part of this canonical drafting task | authorship, natural-language, semantic-parity, and license review pending |
| diagrams | text-only route/timeline/ownership diagrams drafted for the lesson | rendered accessibility and provenance review pending |

## Copyright, license, and quotation boundary

- The repository contains a CC BY-SA 4.0 license notice, but this record does
  not decide whether every planned source file is covered, whether the
  repository has authority to license it, or whether another notice is needed.
- The GoF book is cited for terminology and bibliography only. No definition,
  catalog prose, diagram, or code is reproduced.
- Python documentation and local chapters are used as technical references.
  API names and short identifiers appear for interoperability; explanatory
  prose and exercises are newly drafted.
- If a future edit adapts external prose, code, exercise structure, or a visual,
  maintainers must add the exact source, author, license/permission basis,
  changes made, attribution text, and competent review before publication.
- Automated similarity, link, or structure checks cannot infer permission,
  authorship, license compatibility, or reviewer acceptance.

## Review triggers

Revisit this file when adding a pattern, importing a sample, changing Python
version claims, altering network semantics, adding a visual, changing a linked
chapter owner, or translating the lesson. A competent provenance/license
reviewer must close the pending state against the final file digests; the
author of the draft cannot self-infer that approval.
