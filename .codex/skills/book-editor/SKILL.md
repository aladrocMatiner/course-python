---
name: book-editor
description: Audit and improve multilingual technical books and Markdown learning content. Use for editorial QA, executable-example review, semantic localization parity, navigation, rendered accessibility and Arabic bidi handoff, provenance evidence, maintainer onboarding, published-unit reconciliation, broken lesson repair, or publication readiness.
---

# Purpose

Review technical learning material as an exacting but pragmatic editor. Protect the learner's trust: published instructions must be understandable, runnable when claimed, safe, accessible, and equivalent across promised languages.

## Required preparation

1. Read the repository's `AGENTS.md`, project context, style guide, and canonical-language policy when present.
2. Inventory canonical units, localized variants, indexes, companion sources, validators, and active proposals.
3. Identify the declared audience, runtime/toolchain, license, and definition of “runnable”.
4. Use the `professor` skill alongside this skill when changing pedagogy; use the planning skill required by the repository for cross-cutting remediation.

## Audit workflow

### 1. Establish implemented truth

- Separate implemented chapters and verified controls from proposed work.
- Treat existing paths and public links as stable unless an approved migration says otherwise.
- Compare repository promises with actual content and automation.

### 2. Check technical correctness

- Verify APIs, outputs, version-sensitive claims, error behavior, platform scope, and security guidance against primary sources or direct execution.
- Run safe snippets in the declared environment. For destructive, expected-failure, compiled, networked, or privileged examples, use bounded isolated verification appropriate to the risk.
- Flag code that depends on missing definitions, hidden setup, execution order, live credentials, public services, or unbounded resources.

### 3. Check pedagogy

- Trace each objective to an explanation, example, exercise, and observable check.
- Detect concepts used before introduction, unexplained jargon, abrupt difficulty jumps, solutions that add hidden prerequisites, and exercises without success criteria.
- Require happy path, boundary behavior, a recoverable error, hints, explained solutions, checkpoint, and reflection as defined by the project.

### 4. Check multilingual parity

- Compare objectives, technical semantics, commands, examples, exercises, edge cases, warnings, solutions, rubrics, and links against the canonical unit.
- Use line, heading, and fence counts only to locate likely gaps; never equate similar counts with semantic parity.
- Preserve code contracts and public identifiers across languages. Verify localized comments/messages without changing behavior.
- Reject translations that reduce a complete lesson to a summary when parity is promised.

### 5. Check navigation and accessibility

- Validate relative links, language selectors, stable slugs, root-index ordering, heading hierarchy, fence balance, and right-to-left wrapper balance.
- Require descriptive links, alt text plus prose equivalents, simple readable tables, and no color-only or position-only meaning.
- Keep code, commands, paths, and identifiers readable left-to-right inside right-to-left prose.

### 6. Check safety and provenance

- Protect minors and beginners from personal-data collection, unsafe remote targets, secrets, destructive commands, misleading security shortcuts, and unsupported compatibility/performance claims.
- Verify license and attribution for adapted prose, exercises, images, datasets, and diagrams. Do not infer republication rights from public availability.

## Change boundary

- Correct narrow factual errors, broken links, malformed markup, and self-contained broken examples directly when authorized.
- Use the repository's proposal process for new capabilities, shared validators/CI, mass translation remediation, path migrations, or architecture changes.
- Preserve unrelated work and avoid turning a scoped correction into silent course-wide rewriting.

## Publication-evidence mode

When preparing a course-wide release or maintainer handoff, read [the publication and reviewer handoff workflow](references/publication-and-reviewer-handoff.md). Reconcile every published canonical/localized unit, onboarding command, provenance record, rendered accessibility target, and competent-review role against current digests.

Keep structural and executable evidence separate from linguistic fluency, technical/pedagogical approval, rendered accessibility, Arabic bidirectional review, provenance, license compatibility, and legal acceptance. Prepare reviewer-ready evidence and leave each human gate pending until the qualified reviewer actually records a decision.

## Reporting and verification

Report findings by severity with file/line evidence, learner impact, and a concrete correction. After edits, list modified files and run the relevant snippet tests, link/localization checks, OpenSpec strict validation, and whitespace checks. Run skill validators when a skill itself changes.

Prefer a small verified correction over a broad claim that the book is “clean”.
