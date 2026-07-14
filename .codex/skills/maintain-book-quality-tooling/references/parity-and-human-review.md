# Parity and human-review contract

## Published inventory

Discover the same published units and required locales as the root quality configuration; do not freeze a chapter-number regex that silently excludes later units. Reconcile by stable unit path and locale.

Keep topology separate from mutable review evidence. A compact index may declare the exact publication scope, while one canonical-source file and one unit/locale record file isolate concurrent review. Do not keep a generated monolithic aggregate as a second authority. Migration and rollback must be explicit, deterministic, repository-relative, and whole-object lossless before the old representation is replaced.

When a canonical digest changes, invalidate review evidence tied to the old source. When a localized digest changes, return that localized record to the appropriate pending/drafted state. Preserve prior evidence only when its source, localized digest, schema, and reviewer contract remain valid.

Automation may record inventory and automated-signal success. It may not write linguistic, technical/pedagogical, rendered-accessibility, bidirectional, provenance, license, or legal approval.

Normal validation is read-only. A localized digest refresh writes only its record; a canonical refresh invalidates only its audit and four dependent locale records. Reject missing, extra, duplicate, escaping, stale, or partially written evidence rather than silently rebuilding or approving it.

## Semantic dimensions

Use structure and counts only to prioritize review. Human comparison must cover purpose/objectives/prerequisites, concept order, examples/outputs, guided work, happy/edge/error/recovery behavior, common mistakes, explained solutions, assessment/reflection, safety/compatibility, navigation/accessibility, and technical/source-reference contracts.

Preserve code identifiers, commands, paths, public APIs, numerical limits, and stable diagnostics across languages unless localization is deliberate and equivalently verified.

## Accessibility and bidirectional handoff

Automated checks may verify heading order, descriptive-link patterns, alt-text presence, table structure, and wrapper balance. A competent reviewer still inspects rendered narrow/wide layouts, keyboard and assistive-technology reading, prose equivalents, contrast where applicable, and Arabic right-to-left text with left-to-right code/paths/commands.

Do not label structural success as accessible approval.

## Provenance boundary

Automation checks that attribution records exist, paths resolve, fields are present, and required notices are visible. A human reviewer determines source identity, permission/license terms, attribution sufficiency, compatibility, ownership, and legal release status. Use neutral `review required` language and never assert infringement or clearance automatically.

## Evidence packet

Provide canonical/localized digests, changed paths, automated commands/results, unresolved semantic dimensions, rendered-review targets, provenance records, exact reviewer roles, and pending decisions. Keep reviewer identity/date/notes only when genuinely supplied by the competent person.
