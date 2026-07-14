---
name: maintain-book-quality-tooling
description: Maintain truthful, deterministic quality tooling for the multilingual Python book. Use when changing validate_book.py, parity_review.py, parity manifests, validator configuration or baseline, domain-plugin protocols, quality tests/guides, or least-privilege CI workflows.
---

# Purpose

Evolve automated evidence without broadening its trust boundary or claiming judgments that require a competent human reviewer.

## Required preparation

1. Read repository instructions, OpenSpec artifacts, `BOOK_STYLE.md`, current validator/quality-matrix configuration, tests, review guides, and the files affected by the proposed rule.
2. Read [the generic validator contract](references/generic-validator.md) for Markdown, diagnostics, execution, configuration, baseline, or hygiene changes.
3. Read [the plugin and CI contract](references/plugins-and-ci.md) for domain checks, source references, process isolation, prerequisites, or workflow changes.
4. Read [the parity and human-review contract](references/parity-and-human-review.md) for inventories, digests, transitions, translations, accessibility, provenance, or publication evidence.

## Core workflow

1. State the exact invariant, its owner, and what passing cannot prove.
2. Add a positive fixture, a focused failure fixture, and a recovery assertion before or with implementation. Keep diagnostics stable, repository-relative, safe, and actionable.
3. Preserve read-only behavior, bounded input/output/runtime, versioned configuration/schema, deterministic ordering, and fail-closed protocol errors.
4. Keep the generic validator standard-library-first and domain-neutral. Invoke networking, C++, Rust, or future toolchain checks only through explicit plugin paths or provisioned verifier jobs.
5. Make every plugin declare stable IDs, prerequisites, timeout, and check IDs. Reject crashes, malformed output, source mutation, unsafe paths/content, or unsupported API versions.
6. Preserve manifest records only while their source/localized digests and review evidence remain valid. Automated structure or execution may advance an automated signal but never human acceptance.
7. Keep CI least privilege, pinned, bounded, secret-free, and explicit about which domain evidence ran. Never auto-execute arbitrary discovered plugins.
8. Run focused tests, the full tooling suite, parity reconciliation/validation as applicable, the named core/domain quality profiles (or their direct-command fallback), OpenSpec validation, and whitespace/hygiene checks.

## Human boundary

Leave linguistic fluency, technical/pedagogical adequacy, rendered accessibility, Arabic bidirectional quality, provenance, ownership, license compatibility, and legal acceptance pending until a competent named reviewer records evidence. Do not infer these decisions from counts, matching structure, test success, or model output.

## Handoff

Report the changed invariant, positive/negative/recovery evidence, generic versus domain coverage, preserved pending human gates, migration or baseline effect, and exact commands. Say `not selected`, `unsupported`, or `unverified` instead of implying coverage.
