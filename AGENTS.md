
# Course Authoring Instructions

<!-- OPENSPEC:START -->
# OpenSpec Instructions

Always open `openspec/AGENTS.md` when a request mentions a proposal, spec,
change, plan, new capability, architecture shift, or another cross-cutting
change. Use it to learn the current OpenSpec workflow, artifact conventions,
and repository-specific human review boundaries.

Keep this managed block so `openspec update` can refresh the instructions.
<!-- OPENSPEC:END -->

These rules apply to every change to the book.

## Required context

- Read `BOOK_STYLE.md` and `openspec/config.yaml` before changing chapters, appendices, indexes, examples, or translations.
- Use the local `professor` and `book-editor` skills when creating or reviewing educational content.
- For proposals or cross-cutting changes, use the official OpenSpec skill matching the action (`openspec-propose`, `openspec-apply-change`, `openspec-verify-change`, or `openspec-archive-change`) plus `openspec-architect` for decomposition and risk sequencing.

## Stable content model

- Treat each existing directory name and relative URL as a stable public link. Renaming requires an approved proposal and migration plan.
- Use `README.md` as the canonical English source for every chapter or appendix. Each unit has Spanish, Catalan, Swedish, and Arabic variants.
- Keep root `README.md` and `README.en.md` identical. Update all six root indexes atomically only after their target paths exist.
- Preserve the Arabic outer `<div dir="rtl">` wrapper and keep code, commands, paths, and identifiers readable left-to-right.

## Quality gates

- Do not call an example runnable unless it has been executed with the documented Python/toolchain or is linked to a tested companion source.
- Preserve semantic parity across languages: objectives, concepts, examples, exercises, edge cases, warnings, solutions, and assessment—not merely headings or word counts.
- Introduce prerequisites before use. Label intentional previews as optional, explain the minimum needed, and link to the later chapter.
- Include accessible headings, descriptive links, alt text and text equivalents for visuals, readable tables, and instructions that do not depend only on color.
- Keep commands safe and scoped. Use temporary paths, bounded timeouts, local services, fake secrets, and offline-capable examples by default.
- Never include personal data about learners, live credentials, unsafe remote targets, or unverified compatibility/performance claims.
- Verify provenance and attribution before adapting third-party exercises or prose; preserve license obligations.
- Run the relevant validators, `openspec validate <change-id> --strict`, `openspec doctor`, and `git diff --check` before handing off work.
