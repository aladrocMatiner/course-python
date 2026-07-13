# Book Style and Quality Guide

This guide is the shared editorial contract for the Python course. It applies to new content and to any existing unit touched by a change. Course-wide legacy gaps are tracked through OpenSpec rather than silently expanding an unrelated edit.

## Audience and voice

- Write for motivated beginners, including readers around 14 years old, without speaking down to them.
- Be calm, direct, encouraging, and technically exact. Normalize mistakes and explain why a correction works.
- Define necessary jargon in plain language before using it repeatedly. Add a small glossary when a unit introduces several domain terms.
- Prefer short sentences, concrete examples, and visible progress over dense reference-style exposition.

## Required learning loop

Every chapter or substantial subsection must provide:

1. Concrete learning objectives and prerequisites.
2. Real-world context explaining why the topic matters.
3. Minimal theory in prerequisite order.
4. A prediction or question before execution.
5. A small runnable example and the meaningful output to observe.
6. A guided modification or TODO with a useful hint.
7. At least one happy path, one edge case, and one recoverable error.
8. Common mistakes explained without blame.
9. An explained solution, not only final code.
10. A checkpoint or self-assessment and a closing reflection.

Long chapters should expose essential, intermediate, and advanced routes with estimated session length and an observable outcome for each route. Advanced material must not be required to complete an earlier checkpoint.

## Prerequisites and previews

- Teach a concept before relying on it in required work.
- An intentional early appearance of a later concept must be marked **Optional preview**.
- A preview explains only the minimum needed, provides a copyable path for learners who skip it, and links to the localized chapter that teaches it fully.
- Keep a chapter's required exercises solvable using its declared prerequisites.

## Examples and code

- Target CPython 3.11 or later unless a chapter explicitly declares a narrower verified matrix.
- Prefer the standard library for the beginner path. Mark third-party dependencies and separate installation from use.
- Keep examples small, readable, deterministic, and safe to rerun. Use temporary directories and local loopback services where relevant.
- State whether a block is runnable, illustrative, expected to fail, compile-only, output, or an incomplete TODO. Never make a learner guess.
- Runnable examples must be executed directly or derived from a tested companion source. Expected failures must document the diagnostic and recovery.
- Verify version-sensitive claims against primary official documentation, record the verified version/date in advanced assets, and avoid “latest” claims that the repository cannot keep true.
- Avoid real secrets, personal data, destructive commands, public targets, unbounded input, fixed sleeps, and platform claims that were not tested.
- Keep public identifiers and code semantics stable across translations. Comments, prose, and user-facing sample text may be localized when tests/source references remain valid.
- Show commands for the active environment and distinguish shell input from program output.

## Exercises and assessment

- Increase difficulty gradually and make the success condition observable.
- Give TODOs and hints before the solution. Do not hide prerequisites inside a solution.
- Explain what risk or concept each test covers; prefer deterministic behavior checks over coverage targets.
- End routes with a small rubric covering correctness, readability, error handling, verification, and explanation.
- A capstone should reuse earlier work instead of introducing several unrelated concepts at once.

## Languages and navigation

- `README.md` is the canonical English unit. The required localized siblings are `README.es.md`, `README.ca.md`, `README.sv.md`, and `README.ar.md`.
- Root `README.md` and `README.en.md` are mirrors and must remain byte-for-byte identical. The other root indexes are Spanish, Catalan, Swedish, and Arabic.
- Translation quality means semantic parity: preserve objectives, technical behavior, commands, examples, exercises, edge cases, warnings, solutions, checkpoints, and links.
- Translate explanations naturally; do not reduce a localized chapter to a summary.
- Link prerequisites and navigation to the reader's language when that translation exists.
- Keep the selector order `English → Español → Català → Svenska → العربية`. The current language is plain text; every other language links to its exact sibling README. Arabic units use one outer `<div dir="rtl">`; code, commands, file paths, and identifiers remain legible left-to-right.
- Existing folder names are stable links even where their language is inconsistent. New chapter slugs use `chapter-NN-english-kebab-case`.
- Preserve deliberate or already referenced heading anchors. When a heading must change, keep an explicit documented alias and verify the old fragment before removing it.
- Do not publish an index entry for a proposed chapter merely because files exist; require all language targets and the owning change's accepted implementation evidence.

## Accessibility

- Use one H1 followed by hierarchical headings without skipped levels.
- Use descriptive link text rather than “click here”.
- Give every meaningful image or diagram concise alt text and an equivalent prose explanation.
- Use simple tables with header cells; provide a list alternative when a table becomes difficult on a narrow screen.
- Do not encode meaning only through color, position, emoji, or visual styling.
- Explain abbreviations on first use and keep warnings understandable without relying on icons.

## Attribution and licensing

- Write original examples where practical.
- Before adapting an exercise, dataset, diagram, or substantial prose, verify its license and record the source and required attribution near the material or in a dedicated attribution section.
- Do not assume that educational availability permits republication under this repository's CC BY-SA license.

## Review checklist

- Objectives map to examples, exercises, and an observable check.
- Prerequisites and optional previews are explicit.
- Runnable and expected-error examples were verified with the declared environment.
- Happy path, edge case, recovery, common mistake, hint, and explained solution are present.
- Language variants preserve the same learning outcomes and safety constraints.
- Links, language selectors, RTL structure, headings, code fences, and alt text are valid.
- Generated caches, environments, build artifacts, credentials, and learner data are absent.
- Claims distinguish tested behavior, deliberate design, and future work.
