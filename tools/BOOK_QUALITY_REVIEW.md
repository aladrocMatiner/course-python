# Book quality implementation review

This record documents what the automated gate establishes, what it deliberately
does not establish, and which evidence must still be supplied by a person.

## Acceptance commands

```sh illustrative
python -B -m unittest discover -s tools/tests -v
python -B tools/parity_review.py
python -B tools/validate_book.py
git diff --check
openspec validate add-book-quality-gates --strict
openspec validate restore-multilingual-content-parity --strict
```

Chapter-specific plugins are selected explicitly; the generic CI job does not
claim they ran:

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

The unit suite uses temporary Git repositories and leaves the source tree
unchanged. Runnable snippets execute with isolated Python (`-I -B`), no stdin, a
temporary working directory, a minimal environment, a hard timeout, monitored
temporary stdout/stderr files, and a combined output limit. The static preflight
rejects obvious network, process, dynamic-code, absolute-path and destructive
operations. This reduces accidents for trusted book content; it is not a
security boundary for hostile code.

## Parser limitations and human boundary

The Markdown scanner is a conservative state machine, not a complete CommonMark
renderer. It shields fenced code and understands ATX headings, ordinary inline
links/images, explicit HTML anchors, adjacent `bookcheck` metadata, simple pipe
tables and the outer Arabic RTL wrapper. It does not prove rendered layout,
screen-reader quality, natural language, factual accuracy, semantic translation
equivalence or license compatibility. Those remain review responsibilities.

`parity.fence_sequence`, word counts and heading counts are triage signals only.
`tools/parity_manifest.json` refuses `accepted` unless all twelve semantic
dimensions and both linguistic and technical human reviews are recorded against
the current English digest.

## Initial provenance and asset audit

The repository-wide candidate scan found one image asset,
`icons/cc-by-sa.svg`, and marked its source history as **provenance review
required**. Chapter 2 prose/exercises were also already identified for the same
neutral review. `ATTRIBUTIONS.toml` makes no ownership, infringement or license
compatibility judgment. Public didactic TLS key fixtures are exact-path
allowlisted only for secret scanning; an adjacent unlisted private key still
fails with redacted output.

## Human sign-off

| Review role | Status | Required confirmation |
|---|---|---|
| Book editor / professor | Pending | Pedagogy, factual claims and automation boundary |
| Accessibility reviewer | Pending | Rendered navigation, tables, bidi and assistive semantics |
| Provenance owner | Pending | Source/license decisions and required visible notices |
| Fluent linguistic reviewers | Pending | Natural and semantically equivalent ES/CA/SV/AR variants |

Pending rows are release gates, not automated failures to waive.
