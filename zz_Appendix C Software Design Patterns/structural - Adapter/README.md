# Structural · Adapter

## Pattern card

| Field | Value |
|---|---|
| Family | Structural |
| Status | Executable |
| Route | Essential first use; Advanced reuse behind an execution port |
| Prerequisites | Functions, composition, exceptions and exception chaining |
| Time | 35–45 minutes |

You will make one incompatible local collaborator look like the interface the
job application already understands. The observable outcome is a normal
`Result`, a rejected malformed reply, and a translated failure whose original
cause remains available for debugging.

## Start with the pressure

The application wants `execute(job) -> Result`. A legacy runner instead exposes
`process(identifier, contents) -> dict` and raises `LegacyRunnerError`. Changing
every caller would spread legacy names, reply validation, and error handling
through the application.

That mismatch is the pressure. Name **Adapter** only after you can point to the
method, data, and error translations that need one owner.

## The pattern in plain language

An Adapter stands at a boundary. It accepts the application's language,
delegates to an incompatible collaborator, validates the reply, and translates
the result back. In Python the interface can be an ordinary documented method;
no abstract base class is required here.

The simpler alternative is one explicit conversion function. Prefer it when
there is one call site and no collaborator lifetime to own.

### Use it, avoid it, count its cost

- Use it when several callers need the same non-trivial translation or when a
  collaborator must be replaceable behind `execute(job)`.
- Do not use it merely to rename one obvious field at one call site.
- Its cost is another object, another failure boundary, and validation rules
  that must evolve with both sides.
- Remove it when the collaborator adopts the application contract or the
  boundary becomes a single transparent conversion.

## Predict, run, observe

Before running, predict which exception the caller sees when the legacy runner
fails. Should `LegacyRunnerError` escape the application boundary?

From the repository root, run the verified, import-safe companion:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/structural - Adapter/example.py"
```

Expected output:

```text illustrative
job-1:completed:PACK BOOKS
boundary:invalid_reply
recoverable:legacy_failure:cause=LegacyRunnerError
recovered:job-4:completed:PACK FOLDERS
```

Read the [Adapter companion source](example.py). `LegacyRunnerAdapter.execute`
owns three translations: argument shape, reply shape, and exception type. The
caller receives `ExecutionBoundaryError`, while `raise ... from error` preserves
the diagnostic cause.

## Normal, boundary, and recoverable behavior

- **Normal:** a matching identifier, `DONE` state, and non-empty body become a
  completed `Result`.
- **Boundary:** a reply for a different identifier is rejected before it can be
  mistaken for this job's result.
- **Recoverable:** a legacy outage becomes the stable code `legacy_failure`.
  The caller may repair or replace the collaborator and start a new operation;
  it must not guess a `Result`. The final line proves a later healthy operation
  remains available after the translated failure.

Common mistakes are accepting any dictionary, catching every possible
exception, or leaking legacy field names into callers. Translate only errors
owned by this boundary. Let programming mistakes remain visible.

## Guided exercise

Add a documented translation for a valid legacy reply with state `REJECTED`.
It must not be reported as `completed`, and an unknown state must still fail
closed.

**Hint:** decide the domain meaning first. Add the explicit branch before the
current `DONE` validation rather than weakening `_valid_reply`.

**Success criterion:** your checks distinguish `DONE`, `REJECTED`, a mismatched
identifier, and a `LegacyRunnerError`; no legacy exception escapes.

## Explained solution and decision record

A safe solution validates the identifier and body for both known states, maps
`DONE` to `completed`, and maps `REJECTED` to a deliberately chosen domain
status or domain error. It rejects every other state. This keeps the mapping
auditable instead of treating all non-success replies alike.

```text illustrative
problem → one collaborator speaks a different method/data/error language
forces → callers need one stable execution contract and fail-closed validation
simplest option → one conversion function when there is only one call site
chosen pattern → Adapter because the owned collaborator crosses three seams
cost → another boundary object and mapping tests
expected failure → malformed or mismatched replies are rejected
verification → normal, boundary, translated-error, and recovery checks
when to remove it → the collaborator implements execute(job) -> Result directly
```

## Checkpoint and navigation

You are ready to continue when you can identify every translation, explain why
the error is chained, and write one removal condition. If you cannot, return to
the direct function and make the mismatch explicit before adding the object.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Continue the Essential route](../README.md#essential-route-earn-the-first-three-seams) ·
[See the Advanced ownership route](../README.md#advanced-route-make-ownership-explicit)
