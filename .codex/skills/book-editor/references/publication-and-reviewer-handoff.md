# Publication and reviewer handoff

## Reconcile the published inventory

1. Discover canonical units from the same configured publication scope as the repository validator.
2. Confirm every canonical unit has every promised locale and that root indexes target existing matching-language files.
3. Compare current source and localized digests with the review inventory.
4. Preserve a prior decision only when its exact source/localized evidence and review contract remain valid.
5. Return changed or newly published records to pending/drafted states; never carry approval across changed evidence automatically.

Report exact counts and missing/stale paths, but treat heading, word, and fence counts only as triage signals.

## Prepare maintainer onboarding

Give a new maintainer a short evidence packet containing:

- canonical-language and stable-path policy;
- required locale and Arabic wrapper/bidirectional conventions;
- runnable/source-reference contract;
- local generic, parity, plugin, companion, OpenSpec, and whitespace commands;
- generated-artifact and secret hygiene boundaries;
- active changes and files with shared ownership;
- human gates that automation cannot complete.

Run each documented command or mark it unavailable with the exact prerequisite. Do not present a stale onboarding command as publication evidence.

## Prepare provenance evidence

Inventory adapted prose, exercises, diagrams, datasets, code, fonts, certificates, and other third-party assets. Record repository-relative coverage, source/author or holder as supplied, source location, declared license/permission, required notice, adaptation, and review date/evidence.

Do not infer ownership, permission, license compatibility, public-domain status, or legal clearance from public availability or metadata alone. Route unresolved decisions to the competent provenance/legal reviewer using neutral language.

## Prepare rendered accessibility and bidi review

Supply the exact pages and viewports to inspect. Ask competent reviewers to check heading navigation, descriptive links, images plus prose equivalents, narrow tables/list alternatives, keyboard and assistive-technology reading, zoom/reflow, and instructions that do not depend on color or position.

For Arabic, inspect one outer right-to-left wrapper, punctuation and list flow, inline mixed-direction text, and left-to-right readability of code, commands, paths, identifiers, numbers, and URLs. Static wrapper balance is not rendered bidirectional approval.

## Preserve release boundaries

Track automated, linguistic, technical/pedagogical, rendered-accessibility, Arabic bidi, provenance/license, and legal review independently. Record reviewer role, decision, evidence/date, and requested changes only when actually supplied.

Conclude with a reviewer-ready list of passed automated evidence, pending human owners, stale evidence, blockers, and the exact rerun needed after correction. Never mark the book accepted because structure or tests alone pass.
