# Architectural · Repository

## Pattern card

| Field | Value |
|---|---|
| Family | Architectural |
| Status | Cross-link; this page demonstrates only a small client and fake |
| Route | Owned by Chapters 17 and 28 |
| Prerequisites | Dictionaries, exceptions, modules; persistence chapter for implementation |
| Time | 20–30 minutes here, then the owner chapter |

You will recognize when persistence details are leaking into application code
and follow the full implementation to its owning chapters.

## Start with the pressure

A use case wants “find job by identifier,” but its code begins to contain file
paths, SQL-shaped rows, connection handling, or dictionary layout. Tests then
need the storage mechanism even though the decision only needs a job record.

The pressure is persistence language crossing into application policy. A
**Repository** can provide a collection-like application boundary when that
separation is genuinely useful.

## The pattern in plain language

A Repository gives application code operations such as `get(job_id)` while a
concrete implementation owns storage details. The companion shows only the
client and a bounded fake. It intentionally does not teach transactions,
serialization, database connections, or a production Repository.

The simpler Python option is direct dictionary or storage access. Prefer it for
a small program when the storage choice is stable and the call remains clear.

### Use it, avoid it, count its cost

- Consider it when several use cases need the same persistence boundary and
  storage details are obscuring domain decisions.
- Avoid generic `save_anything` APIs or a Repository for every tiny data type.
- Its cost is a second model boundary, mapping, and integration tests against
  the real store.
- Remove it when direct storage code is clearer and no application policy
  depends on the abstraction.

## Predict, run, observe

Predict whether a missing record is exceptional in this particular client,
and whether an unavailable store should look like “not found.”

Run the verified, deliberately small cross-link companion:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B "zz_Appendix C Software Design Patterns/architectural - Repository/example.py"
```

Expected output:

```text illustrative
job-1:completed
job-2:not-found
boundary:job_id must be non-empty text
malformed:invalid_repository_result
recoverable:storage unavailable
recovered:job-1:completed
```

The [Repository client source](example.py) keeps “missing” distinct from
“storage unavailable.” It accepts only the small `JobStatus` domain value and
translates a malformed collaborator result to `invalid_repository_result`; no
raw dictionary layout or `KeyError` crosses the client boundary. Those
differences are part of the use-case contract, not a reason to duplicate the
persistence lessons here.

## Normal, boundary, and recoverable behavior

- **Normal:** the client asks for one record and formats a validated
  domain-relevant `JobStatus` value.
- **Boundary:** an empty identifier fails before storage; absence produces the
  deliberate `not-found` outcome; a wrong result shape, identity, or status
  becomes the stable `invalid_repository_result` error.
- **Recoverable:** storage unavailability remains an error. After the store is
  restored or replaced, a new read can succeed.

Common mistakes are turning every storage error into `None`, leaking raw rows
through the boundary, or testing only a fake and assuming the real mapping is
correct.

## Guided cross-link exercise

Read the owner lessons and identify (1) the application-facing operations, (2)
the concrete persistence mechanism, and (3) the integration evidence that a
fake alone cannot provide. Do not build a second Repository in this appendix.

**Hint:** draw caller → Repository boundary → concrete store and label where
data mapping and storage failure are translated.

**Success criterion:** your note links each responsibility to its owner, keeps
missing distinct from unavailable, and states when direct storage would be
simpler.

## Explained solution and decision record

The application owns the vocabulary it needs; a concrete Repository owns
storage access and mapping. Unit tests may use a fake for policy, while an
integration test must exercise the real store contract. The owner chapters
provide that larger context.

```text illustrative
problem → persistence details obscure use-case decisions
forces → stable application vocabulary plus honest storage failures
simplest option → direct dictionary or storage call
chosen pattern → Repository only when several use cases need the boundary
cost → mapping and real-store integration evidence
expected failure → raw layout leaks or missing/unavailable/malformed are conflated
verification → domain-value, absence, malformed, unavailable, recovery checks;
               owner chapter supplies real-store integration
when to remove it → direct storage is stable, local, and clearer
```

## Checkpoint and navigation

You pass this cross-link when you can explain what this tiny fake does **not**
prove and can find the real implementation owner.

[Return to the Appendix C family catalogue](../README.md#family-index) ·
[Study persistence in Chapter 17](../../chapter-17-persistencia/README.md) ·
[Study the professional boundary in Chapter 28](../../chapter-28-professional-capstone/README.md)
