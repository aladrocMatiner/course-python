# Iterator and Generator

| Field | Value |
|---|---|
| Family | Behavioural |
| Status | Cross-link with a small verified client |
| Route | Chapter 26 owner route |
| Prerequisites | Loops, functions, `yield`; complete lesson is in Chapter 26 |
| Estimated time | 15–25 minutes here |

## Start with the pressure

Records may arrive gradually or may be too numerous to copy into another list.
The caller wants one item at a time and must establish a bound for this local
operation. That traversal pressure points toward the iterator protocol and a
generator; Appendix C should not duplicate their full owner chapter.

## The basic idea

An iterator supplies the next value on demand. A generator function uses
`yield` to implement that protocol while preserving its suspended position.
The companion is only a client-level cross-link: it strips names, skips blanks,
and applies two positive integer bounds. `limit` caps yielded names;
`max_scanned` caps source records examined. The second bound prevents an endless
stream of blanks from keeping this client inside the loop forever. Standard
library `islice(records, max_scanned)` exposes at most that many source items
without first copying them into a list.

The complete explanation, exercises, testing, and pipeline work remain in
[Chapter 26: Iteration, Iterators, and Generators](../../chapter-26-iteration-generators/README.md).

## Simpler option, fit, and cost

- **Simpler option:** a direct loop or list comprehension for small, already
  bounded data.
- **Use it when:** traversal is lazy, streaming, large, or potentially
  unbounded and the caller controls consumption.
- **Do not use it when:** a small complete collection is clearer and needed
  repeatedly.
- **Cost:** one-pass behavior, suspended state, deferred errors, and resource
  cleanup that the consumer must understand.

## Predict, run, observe

Predict why a valid name in source position four is not observed when
`max_scanned=3`, and why an invalid bound fails only when iteration begins.

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  'zz_Appendix C Software Design Patterns/behavioural - Iterator and Generator/example.py'
```

```text illustrative
normal=['build', 'test']
scan-boundary=[]
failure=max_scanned must be a positive integer
recovery=['build', 'test', 'publish']
```

Because a generator body begins on first iteration, `list(...)` is what exposes
the invalid-limit exception in this small client.

## Normal, boundary, and recoverable behavior

- Normal: blank records are skipped and two valid names are yielded lazily.
- Boundary: scanning stops after three blank records, so a later valid value is
  deliberately not consumed.
- Recoverable error: Boolean, non-integer, and non-positive bounds are rejected;
  positive `limit` and `max_scanned` values restore iteration.

Do not infer that laziness makes work free or automatically bounded. Both output
and source scanning need a bound; open files or sockets also need explicit
cleanup ownership.

## Guided exercise

Pass a source generator that records each item it produces. Request one valid
name with `max_scanned=3` and observe which source items were consumed.

**Hint:** use a local list named `seen`; append immediately before each source
`yield`.

**Success criterion:** consumption stops as soon as one nonblank name is yielded
or three records are scanned, whichever comes first. Your explanation
distinguishes both bounds from result-list construction in this demonstration.

## Explained solution and decision record

`islice` enforces the source-scan bound, while `return` enforces the result
bound. This client is enough to recognize the pressure, but Chapter 26 owns
iterator classes, generator lifecycles, pipelines, errors, and assessments.

```text illustrative
lazy bounded traversal → one-pass values and caller-owned consumption
→ direct loop/list → generator client
→ cost: deferred execution and cleanup semantics
→ verify early stop, invalid bound, and recovery
→ follow Chapter 26 rather than duplicating the owner lesson
```

## Checkpoint and navigation

Can you explain when the generator body starts, who advances it, what bounds
consumption, and why one pass may not be reusable? Continue in the owner chapter
for the full checkpoint.

[Return to the Appendix C catalogue](../README.md#family-index) ·
[Open the canonical Chapter 26 lesson](../../chapter-26-iteration-generators/README.md)
