# Plugins and CI contract

## Plugin boundary

Require explicit repository-relative plugin paths. Each plugin declares a unique safe ID, supported API version, stable check IDs, executable prerequisites, and a timeout no greater than the root cap.

Run registration and checks in bounded child processes. Validate schema, paths, messages, remediation, construct values, output size, descendants, and a before/after repository snapshot. A plugin cannot suppress or downgrade generic diagnostics.

Distinguish:

- plugin not selected;
- prerequisite missing;
- contract-defined supported skip;
- check passed;
- check failed;
- plugin protocol/internal failure.

Never convert missing, crashed, timed-out, malformed, mutating, or unselected execution into domain coverage.

## Source references

Resolve every `source-ref` to an existing repository-relative companion path and stable check ID. The generic validator may verify registration and path integrity; only an explicitly selected owning plugin/verifier supplies behavioral evidence.

Keep networking, C++, Rust, and future domains open-ended through the versioned protocol. Do not hard-code their semantics into the generic scanner.

## CI separation

Keep the generic job standard-library-first, least privilege, bounded, and independent of domain toolchains. Use pinned actions, `contents: read`, no production secrets, and a finite job timeout.

When the repository has a quality evidence runner, keep its matrix versioned and closed: named profiles and adapters, exact plugin paths, no arbitrary shell strings or autodiscovery. The runner aggregates existing owners; it does not reinterpret diagnostics. Report `pass`, `fail`, `error`, `unsupported`, and `not selected` distinctly, and keep deterministic machine-readable output free of timestamps, durations, absolute paths, secrets, and successful raw logs.

Run domain plugins only in named explicit steps/jobs with provisioned prerequisites. Keep full native/package matrices separate when they require downloads or long builds. Report exact runner/tool versions and never infer an unexecuted operating system from another host.

## Change tests

Test successful registration/checks plus duplicate/unsafe IDs, API mismatch, missing prerequisite, invalid timeout, crash, malformed output, unsafe diagnostic content, timeout, output overflow, surviving descendant, path escape, and source mutation. Assert generic diagnostics remain stable when a domain plugin fails.
