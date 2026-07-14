# Book quality implementation review

This record documents what the automated gate establishes, what it deliberately
does not establish, and which evidence must still be supplied by a person.

## Acceptance commands

The versioned quality matrix is the maintainer/CI entry point. It aggregates
the existing owners and emits deterministic text, JSON, or Markdown; it does
not replace their CLIs or reinterpret their diagnostics.

```sh illustrative
python -B tools/run_quality.py --profile core --format text
python -B tools/run_quality.py --profile network-domain --format text
python -B tools/run_quality.py --profile cpp-domain --format text
python -B tools/run_quality.py --profile rust-domain --format text
python -B tools/run_quality.py --profile handoff --format markdown
```

The direct-command fallback remains useful for diagnosis and verifies the same
owners independently:

```sh illustrative
python -B -m unittest discover -s tools/tests -v
python -B tools/validate_curriculum.py
python -B tools/parity_review.py
python -B tools/validate_book.py
git diff --check
openspec validate --all --strict --no-interactive
openspec doctor
```

Chapter-specific plugins are selected explicitly. The generic CI job selects
`core`; three separately named bounded jobs select exactly one domain profile.
The profile matrix maps those checks to these stable direct commands:

```sh illustrative
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
python -B tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

## Scenario-to-test map

| Contract | Automated evidence |
|---|---|
| Versioned config and exact allowlists | `test_config_rejects_*` |
| Unit shape, mirrors, selectors and navigation | `test_unit_shape_*`, `test_selector_*` |
| Markdown hierarchy, links, fragments and fence metadata | `test_markdown_*`, `test_links_*` |
| Bounded trusted Python | `test_python_snippet_*` |
| Source-reference contract | `test_source_reference_*` |
| Plugin isolation and protocol | `test_plugin_*` |
| Git inventory, artifacts and redacted secret findings | `test_changed_paths_*`, `test_hygiene_*` |
| Stable non-growing baseline | `test_fingerprint_*`, `test_baseline_*` |
| Neutral attribution wording | `test_attribution_*` |
| Semantic-review state guard | `test_parity_review.py` |
| Quality matrix, bounded runner and stable reports | `test_run_quality.py` |

The unit suite uses temporary Git repositories and leaves the source tree
unchanged. Runnable snippets execute with isolated Python (`-I -B`), no stdin, a
temporary working directory, a minimal environment, a hard timeout, monitored
temporary stdout/stderr files, and a combined output limit. The static preflight
rejects obvious network, process, dynamic-code, absolute-path and destructive
operations. This reduces accidents for trusted book content; it is not a
security boundary for hostile code.

The aggregate runner has the same trusted-code boundary. It uses no shell,
closes stdin, bounds child time/output, controls descendants where the host has
a tested primitive, and compares a content snapshot after each check. A missing
prerequisite or unsupported process-tree capability is `unsupported`, never a
pass. Loss of Linux `/proc` observability before launch prevents execution;
loss after launch is an infrastructure error, kills every observed PID, and
explicitly says that unobserved-descendant cleanup cannot be proved. Reports
reject or redact terminal controls, tokens, and absolute/temporary paths
(including paths with spaces), omit environment secrets and successful raw
logs, and do not inherit `OPENAI_API_KEY`.

The source snapshot includes regular, symlink, and special file entries under
the checkout, including untracked and ignored files, but excludes `.git`. Its
byte cap does not separately bound directory metadata or the number of empty
files. Together with the process-observability caveat, these are trusted-code
limits, not a hostile-code sandbox. Host/tool versions are observed execution
evidence only, not a compatibility matrix.

## Parser limitations and human boundary

The Markdown scanner is a conservative state machine, not a complete CommonMark
renderer. It shields fenced code and understands ATX headings, ordinary inline
links/images, explicit HTML anchors, adjacent `bookcheck` metadata, simple pipe
tables and the outer Arabic RTL wrapper. It does not prove rendered layout,
screen-reader quality, natural language, factual accuracy, semantic translation
equivalence or license compatibility. Those remain review responsibilities.

`parity.fence_sequence`, word counts and heading counts are triage signals only.
The `tools/parity_manifest.json` index plus granular `tools/parity/` evidence
store refuse `accepted` unless all twelve semantic dimensions and both
linguistic and technical human reviews are recorded against the current English
digest. The inventory covers 27 canonical units and 108 localized variants;
storage migration and automated reconciliation do not approve any source or
translation.

## Initial provenance and asset audit

The extension/marker-based candidate scan finds one image asset,
`icons/cc-by-sa.svg`, and no literal `attribution-required` marker outside the
validator fixtures and OpenSpec artifacts. The 2026-07-14 manual read-only
inventory also records neutral review work for the Chapter 2 and Chapter 3
exercise/prose candidates, Chapter 24 and Chapter 25 declarations/reference
sections, the repository license text, and the Chapter 23 TLS fixture set.
`ATTRIBUTIONS.toml` now contains seven `review-required` entries covering 30
unique existing paths; it records no human reviewer role/date and makes no
ownership, infringement, permission, trademark, or license-compatibility
judgment.

The exact paths, evidence digests, discovery limits, and provenance-owner
questions are in the
[change-local provenance and publication-readiness packet](../openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md).
It also records that all 27 canonical units contain exercise/challenge wording,
while automated discovery cannot identify unmarked adapted prose. Public
didactic TLS key fixtures remain exact-path allowlisted only for secret
scanning; an adjacent unlisted private key still fails with redacted output.
Task 4.3 remains pending until a competent provenance reviewer confirms the
decisions and the neutrality of attribution diagnostics.

## Human sign-off

| Review role | Status | Required confirmation |
|---|---|---|
| Book editor / professor | Pending | Pedagogy, factual claims and automation boundary |
| Accessibility reviewer | Pending | Rendered navigation, tables, bidi and assistive semantics |
| Provenance owner | Pending | Source/license decisions and required visible notices |
| Fluent linguistic reviewers | Pending | Natural and semantically equivalent ES/CA/SV/AR variants |

Pending rows are release gates, not automated failures to waive.
