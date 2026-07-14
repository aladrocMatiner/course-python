# Change: Add course-wide book quality gates

## Why

The book has a clear editorial contract in `BOOK_STYLE.md`, but it has no repository-wide validator, test suite, or continuous-integration workflow. The three proposed advanced chapters therefore duplicate link, Markdown, localization, and hygiene validators, while the 22 implemented chapters contain legacy inconsistencies that cannot safely be fixed or waived ad hoc.

A single standard-library quality layer can make new regressions visible without pretending that structural automation proves teaching quality or translation accuracy. A reviewed baseline ratchet lets the project adopt that layer incrementally, and chapter plugins keep network, C++, and Rust verification close to their toolchains.

## What Changes

- Add a root, CPython 3.11+ standard-library validator at `tools/validate_book.py` with stable text and JSON diagnostics.
- Add `unittest` coverage for course discovery, the five-file unit model, root README mirroring, localized selectors and navigation, relative links and anchors, Markdown headings and fences, Arabic RTL balance, and machine-checkable accessibility rules.
- Define an explicit classification contract for every fenced block: `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative`, or `output`.
- Execute only opted-in, trusted Python snippets through bounded temporary-directory hooks; the runner is a safety guard, not a security sandbox. Delegate dependency-heavy, network, native, and multi-process examples to registered chapter plugins.
- Add source-reference and plugin contracts so root checks can verify documentation-to-source traceability while chapter tools retain domain-specific builds, tests, artifact checks, and compatibility matrices.
- Add repository hygiene checks for generated caches, virtual environments, build outputs, native artifacts, accidental credentials, and learner data, including ignored paths without printing secret values.
- Check in a reviewed issue baseline whose stable fingerprints can only stay equal or decrease. New and changed content must pass current rules, while legacy debt remains visible and cannot silently grow or be reintroduced.
- Add an attribution inventory and audit for adapted prose, exercises, datasets, diagrams, and other assets. Diagnostics report missing or unresolved provenance records and never assert copyright infringement or provide a legal conclusion.
- Add a least-privilege CI workflow that runs unit tests and book validation on pull requests and pushes with bounded execution and no example network access.
- Reconcile the originating network, C++, and Rust chapter changes with capabilities `teach-python-network-programming`, `teach-python-cpp-integration`, and `teach-python-rust-integration`: the root validator owns generic documentation, localization, accessibility, and hygiene rules; those capabilities retain domain-specific validators and plugin adapters regardless of whether their originating changes are active or archived.

## Impact

- **Affected specs:** new capability `verify-course-content-quality`.
- **Affected code:** `tools/validate_book.py`, `tools/book_quality.toml`, `tools/book_quality_baseline.json`, `tools/tests/`, `ATTRIBUTIONS.toml`, and `.github/workflows/book-quality.yml`.
- **Affected content:** all root indexes and all implemented or future chapter/appendix Markdown are inspected; legacy content is not rewritten by this proposal.
- **Coordinated capabilities:** `teach-python-network-programming`, `teach-python-cpp-integration`, and `teach-python-rust-integration`; their originating changes required reconciliation before implementation to avoid duplicate generic validators, and may later be archived independently.
- **Runtime/tooling:** CPython 3.11+ and Git. Production validation uses only the Python standard library; domain plugins may declare additional tools but are not run by the generic CI job unless its workflow explicitly provisions them.
- **Compatibility:** stable directory names and relative URLs remain unchanged. The initial baseline makes adoption non-breaking for untouched legacy content, while new or modified content receives stricter acceptance checks.
