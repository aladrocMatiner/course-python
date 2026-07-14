# OpenSpec contributor guide

Use this guide together with the repository root `AGENTS.md`. It is a local
pointer to the installed OpenSpec workflow, not a copy of the CLI schema.

## Before changing anything

1. Read `openspec/config.yaml` and the repository's stable-path and book-style
   rules.
2. Inspect live work with `openspec list --json` and avoid overlapping an
   active change without reconciling its artifacts first.
3. Select the repository-local OpenSpec skill that matches the requested
   action: propose, update, apply, verify, sync, or archive.
4. Ask OpenSpec for current artifact paths and instructions with
   `openspec status --change <change> --json` and
   `openspec instructions <artifact-or-apply> --change <change> --json`.

Do not assume artifact names or ordering from an older OpenSpec release. Keep
public chapter paths, anchors, code contracts, localized siblings, and human
review boundaries stable unless the approved change explicitly alters them.

## Proposal and planning rules

- Give each change a unique kebab-case verb-led identifier.
- Keep `proposal.md`, `design.md`, delta specs, and `tasks.md` mutually
  consistent. Each spec requirement needs at least one `#### Scenario:`.
- Separate automated evidence from linguistic, accessibility, pedagogical, and
  provenance approval. Automation must never manufacture a human sign-off.
- Record dependencies on other active changes and resolve conflicting ownership
  before implementation.

## Apply and verification rules

- Read every context file returned by `openspec instructions apply` before
  editing implementation files.
- Implement tasks in dependency order and check a task only after its stated
  validation has passed.
- Run the narrow tests while iterating, then the repository quality matrix and
  `openspec validate <change> --strict` before handoff.
- Use `openspec doctor` to detect repository-level OpenSpec problems.
- Do not archive a change until implementation verification is complete and a
  maintainer has requested archival.

If the CLI and this guide disagree, use the current CLI-resolved instructions,
then update this pointer in a separate reviewed change.
