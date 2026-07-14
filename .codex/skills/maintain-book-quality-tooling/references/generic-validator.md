# Generic validator contract

## Ownership

Keep the root validator responsible for repository structure, Markdown/navigation, language selectors and right-to-left wrappers, local links/anchors, fence metadata, eligible trusted Python snippets, source-reference registration, accessibility structure, attribution-record consistency, baseline/config integrity, and artifact/credential hygiene.

Do not add network protocols, compilers, package builds, native ABI inspection, or toolchain-specific behavior to the generic layer.

## Rule design

For every rule, define:

- stable namespaced rule ID and severity;
- exact scope and exclusions;
- positive, boundary, malformed, and recovery fixtures;
- repository-relative path/line behavior;
- message and actionable remediation;
- construct fingerprint and baseline migration effect;
- time, input-size, and output-size bounds;
- what passing cannot prove.

Return exit `1` for quality failures and exit `2` for configuration/protocol/internal failure according to the existing CLI contract. Sort diagnostics deterministically and keep JSON free of timestamps, absolute paths, tracebacks, secrets, learner data, unsafe payloads, and legal conclusions.

## Execution and mutation boundary

Use isolated temporary working directories, minimal environments, no stdin, bounded child process groups, and snapshot-based source mutation detection for trusted snippets. State clearly that static screening and subprocess isolation are not a hostile-code sandbox.

Normal validation must not rewrite Markdown, update the baseline/manifest, delete artifacts, or change review status. Provide explicit reconciliation/update commands for intended generated evidence.

## Versioned configuration and baseline

Validate known keys and schema/API versions before scanning. Keep allowlists exact and narrow. Reject wildcard suppression that can hide new paths or rules.

Use exact baseline fingerprints only for reviewed legacy debt. New or changed content cannot add debt; removed debt makes its baseline entry stale until removed. Never add new failures through an automatic baseline-update switch.
