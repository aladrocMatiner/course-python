# Implementation review: provenance and publication readiness

This packet records a read-only repository inventory and routes unresolved
decisions to human reviewers. It is structural evidence, not an ownership,
permission, license-compatibility, trademark, or legal conclusion.

## Audit basis

- Inventory date: 2026-07-14 (Europe/Stockholm).
- Repository revision observed: `26b3b488502978befc736c6952b062e571493a19`.
- Scope: the current shared working tree, including tracked, untracked, and
  ignored paths where the validator's Git inventory exposes them.
- The working tree was not clean because several approved changes were being
  implemented concurrently. Consequently this packet does not satisfy the
  clean-checkout acceptance requirement in task 7.1.
- Candidate discovery was offline. It inspected file extensions, Markdown
  references, visible source/attribution headings, the literal
  `attribution-required` marker, exercise headings and identifiers, the
  checked-in attribution inventory, and repository history. History proves
  when a file entered this repository; it does not prove where the material
  originated or that it may be republished.

## Read-only inventory

| Family | Observed inventory | Provenance disposition |
|---|---:|---|
| Image/PDF assets recognized by the validator | 1 file: `icons/cc-by-sa.svg` | `review-required`; all six root indexes display it, but source, permission, license, and trademark treatment are unconfirmed. |
| Standalone raster images | 0 | No files with PNG, JPEG, GIF, WebP, or ICO suffixes were found. This is not a claim about remote or generated visuals. |
| Standalone diagrams | 0 | No Mermaid, Graphviz, PlantUML, or diagram asset file was found. Prose references to diagrams and explanatory tables are not standalone assets. |
| Dataset files in published units | 0 | No CSV, TSV, JSONL, XML, Parquet, GeoJSON, SQLite, or database file was found. Inline sample records and project TOML metadata are not dataset files. |
| Font assets | 0 | No TTF, OTF, WOFF, or WOFF2 file was found. The SVG names system font families but embeds no font file. |
| Canonical units containing exercise/challenge wording | 27 of 27 | Counts locate review targets only; they do not establish originality. Candidate discovery cannot detect unmarked adapted prose or exercises. |
| Literal `attribution-required` markers outside tests/OpenSpec | 0 | Absence of a marker is not provenance clearance. Contributor declarations and human review remain required. |
| Visible source/originality/reference sections | 10 localized files | Five Chapter 24 files contain sources/attribution plus an originality declaration; five Chapter 25 files contain an original-companion-source declaration plus verified references. Both groups remain `review-required`. |
| Exercise/prose candidate groups | Chapters 2 and 3, five locale files each | Chapter 2 names Python Crash Course in example text, uses `nostarch.com`, and carries numbered “Try it yourself” exercises. Chapter 3 carries the numbered 3-1 through 3-11 “Try it yourself” sequence and distinctive guest-list titles. Source identity, edition, adaptation, permission, and notice requirements are unresolved. |
| Repository license text | `LICENSE` | The file contains the CC BY-SA 4.0 International public-license text and all root indexes link it. Authoritative source, completeness, retention, and notice treatment await provenance-owner confirmation. |
| Public TLS teaching-fixture set | 7 PEM files plus its README | The README and five localized lessons say the fixtures are public and must not be deployed. That safety declaration and the tests do not establish generation source, ownership, or publication terms. |

The manual inventory therefore expands `ATTRIBUTIONS.toml` to seven neutral
`review-required` entries covering 30 unique existing paths. It deliberately
records no `review_date` or `review_role`: no competent provenance reviewer has
yet supplied a decision. The inventory contains no `original-declared`,
`licensed-recorded`, or `public-domain-recorded` status.

## Evidence snapshot

The following SHA-256 values bind this packet to the current observed content.
`ATTRIBUTIONS.toml` schema version 1 currently contains seven entries covering
30 unique repository-relative paths; all 30 resolve inside the repository and
exist as regular files.

The digest algorithm is exact and byte-preserving. For a multi-file group,
sort the literal repository-relative paths by their UTF-8 byte sequence. Start
one SHA-256 state and, for each path in that order, update it with the path's
UTF-8 bytes, one NUL byte (`0x00`), and the 32 raw bytes of the SHA-256 of the
file's raw contents. Add no other separator or terminator; render the final
group digest as lowercase hexadecimal. For a one-file row, report the direct
SHA-256 of that file's raw contents.

Refreshing these digests is automated content evidence only. It does not
establish source, ownership, permission, license compatibility, or legal
clearance; all seven inventory entries remain `review-required`, and the human
provenance decisions remain pending.

| Evidence group | Files | SHA-256 |
|---|---:|---|
| Chapter 2 locale files | 5 | `83a10dc44c0fc67d5a35954ffa23b395eed37ae577fcebe5f2bbf3d5a2567c08` |
| Chapter 3 locale files | 5 | `fa4a01e0466464d882225da4e517027233889a34b77a17898f29a75a292f455a` |
| Chapter 23 TLS fixture set | 8 | `369fc883aea66f133534c88042681127822e2022201ae19c5429678eb8545f9e` |
| Chapter 24 locale files | 5 | `0adc3d37faa3a315b1644ae197feea8d9d94a7bd55f91506d7f3d2368477fc1a` |
| Chapter 25 locale files | 5 | `af45ae2919a365aec2e929e0eb944bb4a1d0c1b8762d617e06560f0d6e6a352a` |
| `icons/cc-by-sa.svg` | 1 | `451ef92f502f67a83e7c1c704bdb3a09bb75635004b71ce526ca3f33ec71ffee` |
| `LICENSE` | 1 | `f9bf22071081bf077d0017909e8e3700bea1facee02eef1e80ff09158871495a` |

Any content change invalidates the corresponding digest and requires this
inventory to be rerun before a reviewer reuses the packet.

## Focused automated evidence

The repository attribution function reports exactly seven diagnostics. Every
one is the warning `attribution.review_required` with the neutral message
“provenance review required”; there is no missing candidate, path, duplicate,
schema, field, URL, or notice diagnostic for the observed tree.

The following focused commands passed on 2026-07-14:

```text
python -B -m unittest \
  tools.tests.test_validate_book.BookQualityTests.test_attribution_review_uses_neutral_language \
  tools.tests.test_validate_book.BookQualityTests.test_attribution_reviewed_license_requires_url_and_visible_notice \
  tools.tests.test_validate_book.BookQualityTests.test_attribution_required_marker_creates_candidate -v
openspec validate add-book-quality-gates --strict
openspec doctor
git diff --check -- ATTRIBUTIONS.toml tools/BOOK_QUALITY_REVIEW.md openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md
! rg -n '[[:blank:]]+$' ATTRIBUTIONS.toml tools/BOOK_QUALITY_REVIEW.md openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md
```

This is focused structural evidence only. The full tooling suite, generic book
validation, changed-scope negative probe, cross-change matrix, and clean-status
check were intentionally not claimed here; they belong to task 7.1 after the
shared working tree settles.

## Exact provenance-review blockers

The provenance owner must record a decision for every inventory entry. For a
reviewed non-original item, the schema requires source title and URL,
author/holder as supplied by the source, license or permission evidence, the
exact required notice and its visible location, adaptation details, reviewer
role, and review date. For an original-content declaration it requires the
declaration, reviewer role, and review date.

| Entry | Decision still required |
|---|---|
| `chapter-02-exercise-provenance-review` | Identify the source and edition, distinguish original additions from any adaptation, verify permission/license and visible-notice duties, or replace the unresolved material. |
| `chapter-03-exercise-provenance-review` | Identify the source and edition for the numbered/title sequence, distinguish original additions from any adaptation, verify permission/license and visible-notice duties, or replace the unresolved material. |
| `chapter-23-tls-fixture-provenance-review` | Record how the PEM fixtures were generated or sourced, who may make the publication declaration, and whether any notice is required. Keep the existing “public test fixture; never deploy” safety notice independent of that decision. |
| `chapter-24-provenance-declaration-review` | Confirm the originality declaration and whether use of the cited technical references creates any attribution or notice requirement. |
| `chapter-25-provenance-declaration-review` | Confirm the companion-source originality declaration and whether use of the cited technical references creates any attribution or notice requirement. |
| `cc-by-sa-badge-provenance-review` | Establish the SVG design source, permission/license evidence, attribution requirements, and any applicable mark-use review. |
| `cc-by-sa-license-text-provenance-review` | Confirm the authoritative license-text source, completeness, retention requirements, and the visible repository notice. |

The competent reviewer must also confirm that the validator's attribution
diagnostics remain neutral and make no accusation or legal conclusion. Tests
can constrain wording, but they cannot supply that human confirmation.

## Publication-readiness handoff

| Review role | Status | Evidence or decision needed |
|---|---|---|
| Provenance owner | Pending | Resolve all seven entries above and confirm neutral diagnostic language. |
| Book editor / professor | Pending | Confirm pedagogy, factual claims, runnable-evidence wording, and that structural signals do not imply teaching quality. |
| Accessibility reviewer | Pending | Inspect rendered wide/narrow layouts, keyboard and assistive-technology reading, visual equivalents, tables, and Arabic mixed-direction content. |
| Fluent technical linguistic reviewers | Pending | Confirm natural, semantically equivalent ES/CA/SV/AR content against current digests. |

No reviewer identity, decision, evidence date, or acceptance note was supplied
during this audit. These rows are release blockers, not failures to waive.

## OpenSpec task status

- Task 4.3: implementation evidence is prepared, but the checkbox remains open
  because its validation explicitly requires a human to confirm that no
  diagnostic makes a legal accusation. That confirmation does not exist.
- Task 7.1: remains open. This audit did not run the complete acceptance matrix
  from a clean checkout while other agents were editing the shared tree.
- Task 7.2: remains open. No book-editor/professor, accessibility, provenance,
  or linguistic sign-off has been supplied.

None of the three remaining task checkboxes can be truthfully completed from
this evidence packet alone.
