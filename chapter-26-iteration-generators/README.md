# Chapter 26 · Iteration, Iterators, and Generators

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we are going to build

Many programs receive a sequence of values and transform it: names become
labels, readings become summaries, and groups become one stream. You already
know how to do that with a `for` loop. This chapter keeps that reliable mental
model and adds three tools in a deliberate order:

1. **Comprehensions, `enumerate`, and `zip`** for small, readable collection
   transformations.
2. **Iterators** for understanding where traversal state lives and why a data
   stream can be exhausted.
3. **Generators** for producing values on demand while keeping the consumer
   explicitly bounded.

The growing project is an iteration pipeline for a small, synthetic workshop
scoreboard. Its executable authority is
[`examples/iteration_pipeline.py`](examples/iteration_pipeline.py), backed by
standard-library tests. It uses no network, credentials, personal data, files,
threads, or third-party packages.

## Learning objectives

By the end of the route you choose, you will be able to:

- **O1 — Transform clearly:** derive a list, dictionary, or set comprehension
  from an ordinary loop and choose the clearer form.
- **O2 — Enumerate and pair safely:** use `enumerate` for display positions and
  choose deliberately between truncating `zip` and `zip(..., strict=True)`.
- **O3 — Explain iterator state:** distinguish an iterable from an iterator,
  use `iter` and `next`, observe exhaustion, and recreate a traversal when the
  source permits it.
- **O4 — Protect traversal:** use an unambiguous exhaustion default and avoid
  structural mutation of the collection currently being traversed.
- **O5 — Build bounded lazy work:** explain generator expressions, `yield`,
  one-shot consumption, `yield from`, and an explicit finite limit.
- **O6 — Recover and clean up:** locate a delayed error at the consumption step,
  terminate a generator with `return`, and run deterministic cleanup after
  early closure.

The [traceability record](TRACEABILITY.md) maps every objective to teaching,
practice, recovery, solution, checkpoint, companion source, and tests.

## Prerequisites and route map

The required entry point is the foundational checkpoint in
[Chapter 11: Functions](../chapter-11-functions/README.md). You should already
be comfortable with lists, dictionaries, sets, conditionals, `for`/`while`
loops, and small functions. The chapter number does **not** mean that networking,
C++, or Rust is required.

- **Essential route · 2 sessions of 45–60 minutes.** Read E1–E3, complete the
  essential challenge, and use its rubric. Outcome: produce a numbered
  scoreboard from two small collections and reject mismatched data. Completion:
  at least 4/5 rubric points, including the strict-pairing point. Safe
  continuation: stop here and continue to
  [Chapter 12: Classes and Objects](../chapter-12-oop/README.md).
- **Professional route · 1–2 sessions of 45–60 minutes.** Complete the essential
  checkpoint first, then P1–P3 and the professional challenge. Outcome: consume,
  diagnose, and deliberately recreate a one-shot traversal. Completion: at
  least 4/5 points, including exhaustion recovery. Safe stopping point: you can
  use iterables confidently without writing generators.
- **Optional advanced route · 2 sessions of 60–75 minutes.** Complete the
  professional route and review
  [Chapter 14: Exceptions](../chapter-14-exceptions/README.md) before the cleanup
  section. Outcome: implement and explain a finite lazy pipeline, a delayed
  failure, delegation, and early cleanup. Completion: at least 5/6 points,
  including bounds and cleanup. This route remains optional for essential
  course progress.

Returning learner? Predict the result of `list(zip(["A", "B"], [1],
strict=True))`. If you can explain why the failure happens only when the zip
object is consumed, begin with the professional route. If you can also explain
why calling a generator function does not run its body, begin with the advanced
route and use the checkpoints to confirm any gaps.

## A small glossary

- **Iterable:** an object that can provide an iterator. Lists, tuples,
  dictionaries, sets, and strings are familiar examples.
- **Iterator:** a stateful object that produces one next value at a time. It
  remembers how far traversal has progressed.
- **Exhaustion:** the state after an iterator has no next value. Direct `next`
  then raises `StopIteration` unless a default was supplied.
- **Comprehension:** compact syntax for building a concrete collection from an
  iterable.
- **Generator:** an iterator created by a generator expression or a function
  containing `yield`.
- **Lazy:** producing work as values are requested. Lazy does not mean
  automatically finite, fast, or safe.
- **Consumer:** the loop, `next`, `list`, or other operation asking an iterator
  for values.

The observable sequence is always the same: obtain an iterator, request a
value, receive a value or exhaustion, and either stop or request again. This
prose sequence is the text equivalent of any iterator-state diagram you may
draw; no meaning depends on arrow direction or color.

## Essential route: readable transformations

### E1. Derive a comprehension from a loop

Objective: build a small collection without losing the ordinary loop mental
model.

Suppose a workshop records three synthetic scores. Before running the example,
predict the value of `doubled` after every loop iteration.

```python runnable
scores = [3, 5, 8]
doubled = []

for score in scores:
    doubled.append(score * 2)

print(doubled)
```

```text output
[6, 10, 16]
```

Read the loop in this order: take one `score`, compute `score * 2`, append the
result, repeat. A list comprehension states the same transformation with the
result expression first:

```python runnable
scores = [3, 5, 8]
doubled = [score * 2 for score in scores]
print(doubled)
```

```text output
[6, 10, 16]
```

The brackets mean “build a list.” Inside them:

1. `score * 2` is the value to store;
2. `score` is the current target name; and
3. `scores` is the iterable supplying values.

A single condition can filter values, but it comes after the iterable. Predict
which scores survive before running:

```python runnable
scores = [3, 5, 8]
large_doubles = [score * 2 for score in scores if score >= 5]
print(large_doubles)
```

```text output
[10, 16]
```

Dictionary and set comprehensions use the same reading order. A dictionary
stores key/value pairs; a set removes equal duplicates. We sort the set only
for stable display—set iteration order is not a correctness contract.

```python runnable
names = ["Noor", "Frej", "Taha"]
length_by_name = {name: len(name) for name in names}
unique_lengths = {len(name) for name in names}

print(length_by_name)
print(sorted(unique_lengths))
```

```text output
{'Noor': 4, 'Frej': 4, 'Taha': 4}
[4]
```

The empty-input edge is calm and useful: none of the bodies runs, so each
comprehension produces an empty collection of its own kind.

```python runnable
print([value for value in []])
print({value: len(value) for value in []})
print({value for value in []})
```

```text output
[]
{}
set()
```

**Modify — O1 TODO:** Rewrite this loop as one readable list comprehension.
Keep exactly one transformation and one condition.

```python todo
scores = [2, 4, 7, 9]
selected = []
for score in scores:
    if score >= 5:
        selected.append(score + 1)

# TODO: replace the loop with selected = [...]
print(selected)
```

**Hint:** read the original body in order: store `score + 1`, take each `score`
from `scores`, keep it when `score >= 5`.

**Explained solution:** the result expression comes first, then the same loop,
then the same condition. The normal result is `[8, 10]`; an empty `scores`
still produces `[]`.

```python runnable
scores = [2, 4, 7, 9]
selected = [score + 1 for score in scores if score >= 5]
print(selected)
```

```text output
[8, 10]
```

Common mistake: compressing nested loops, several conditions, side effects,
and assignments into one expression. A comprehension is valuable when it is
easier to read. Keep the ordinary loop when it tells the story more calmly.

### E2. Enumerate positions without a manual counter

Objective: attach human-facing positions without updating a separate variable.

`enumerate` produces `(position, value)` pairs. `start=1` is useful for labels
shown to a person; it does not change the collection's zero-based indexing.
Predict the two printed lines:

```python runnable
names = ["Noor", "Frej"]

for position, name in enumerate(names, start=1):
    print(f"{position}: {name}")
```

```text output
1: Noor
2: Frej
```

The edge case is an empty iterable: the loop body runs zero times and prints
nothing. There is no special position to invent.

**Modify — O2 TODO:** Change the starting display number to `10`, then predict
the two labels before running.

```python todo
names = ["Noor", "Frej"]
# TODO: enumerate names starting at 10 and print "position: name"
```

**Hint:** change only the `start` argument; do not add and increment a separate
counter.

**Explained solution:** `enumerate(names, start=10)` produces `(10, "Noor")`
and `(11, "Frej")`. The list itself is unchanged.

```python runnable
names = ["Noor", "Frej"]
print(list(enumerate(names, start=10)))
```

```text output
[(10, 'Noor'), (11, 'Frej')]
```

### E3. Pair data without silent loss

Objective: make the length contract visible when two data sources belong
together.

Ordinary `zip` stops when the shorter input is exhausted. That can be deliberate,
but it can also hide a missing score:

```python runnable
names = ["Noor", "Frej"]
scores = [7]
print(list(zip(names, scores)))
```

```text output
[('Noor', 7)]
```

`"Frej"` disappears because the scores iterable has no second value. When equal
lengths are part of correctness, request that contract explicitly with
`strict=True`. The companion function consumes the zip into a list, so a
mismatch cannot remain unnoticed inside an unconsumed zip object.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def strict_pairs(left, right):
    """Return pairs, rejecting unequal input lengths."""
    return list(zip(left, right, strict=True))
```

Happy path: the tests verify
`strict_pairs(["Noor", "Frej"], [7, 9]) == [("Noor", 7), ("Frej", 9)]`.
Two empty inputs correctly produce `[]`.

Predict when the next example fails: when `zip` is created, or when `list`
asks it for values?

<!-- bookcheck: expect-error="ValueError" -->
```python expected-error
names = ["Noor", "Frej"]
scores = [7]
pairs = zip(names, scores, strict=True)
print(list(pairs))
```

The stable signal is `ValueError`. Construction only creates the iterator;
consumption discovers that the right input ended first. Full traceback wording
can vary across Python maintenance versions.

**Recovery:** correct the missing score and rerun the same strict contract.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
print(list(zip(names, scores, strict=True)))
```

```text output
[('Noor', 7), ('Frej', 9)]
```

Removing `strict=True` is also a valid design only when ignored trailing values
are explicitly acceptable. Write that decision in the domain contract; do not
make silent truncation the accidental repair.

### Essential guided challenge

Build a numbered scoreboard. First predict the two output lines and the failure
for a missing score.

```python todo
names = ["Noor", "Frej"]
scores = [7, 9]

# TODO 1: pair names and scores with strict=True.
# TODO 2: enumerate the pairs starting at 1.
# TODO 3: build lines like "1. Noor: 7" with a list comprehension.
# TODO 4: print each line.
```

**Hint:** create `pairs` first. Then the comprehension can unpack
`position, (name, score)` from `enumerate(pairs, start=1)`.

**Explained solution:** strict pairing protects data alignment; enumeration
creates display positions; the comprehension formats one line per pair. Each
step has one responsibility.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
pairs = list(zip(names, scores, strict=True))
lines = [
    f"{position}. {name}: {score}"
    for position, (name, score) in enumerate(pairs, start=1)
]

for line in lines:
    print(line)
```

```text output
1. Noor: 7
2. Frej: 9
```

For `names = []` and `scores = []`, `pairs` and `lines` are empty and nothing
is printed. For unequal lengths, `ValueError` is the expected diagnostic;
repair the data rather than hiding the mismatch.

### Essential checkpoint and rubric

Complete the scoreboard for normal, empty, and unequal inputs. Explain why the
normal output is ordered, why the empty result is valid, and why the mismatch
fails during consumption.

Score one point for each:

- **Correctness:** normal input produces the two exact numbered lines.
- **Boundary:** two empty inputs produce an empty result without a fake row.
- **Recovery:** unequal inputs raise `ValueError`, and corrected input succeeds.
- **Readability:** each comprehension has one clear transformation and at most
  one simple condition.
- **Explanation:** you can distinguish display positions, collection indexes,
  and the strict pairing contract.

A score of 4/5, including **Recovery**, completes the essential route. You may
stop safely and continue to Chapter 12. Reflection: where in a program you know
would silent truncation be dangerous?

## Professional route: iterator state you can explain

### P1. Iterable and iterator are different roles

Objective: locate traversal state instead of imagining that a `for` loop
magically remembers a position.

A list is an **iterable**: it can provide an iterator. `iter(values)` asks for
one. The returned iterator stores traversal progress. `next(cursor)` asks that
specific iterator for one value.

Predict every line before running:

```python runnable
values = ["A", "B"]
cursor = iter(values)

print(iter(cursor) is cursor)
print(next(cursor))
print(next(cursor))
print(next(cursor, "done"))
```

```text output
True
A
B
done
```

The sequence in prose is:

1. `values` can create traversals.
2. `cursor` begins before the first value.
3. the first `next` advances and returns `"A"`;
4. the second advances and returns `"B"`; and
5. the third finds exhaustion and returns the supplied default.

`iter(cursor) is cursor` is `True` because an iterator is its own iterator. By
contrast, separate calls to `iter(values)` produce separate traversals with
their own state.

The companion countdown is also an iterator, but a one-shot generator rather
than a reusable collection:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def countdown(start):
    """Yield ``start`` down to 1 after validating a finite bound."""
    _require_bounded_integer(start, name="start", maximum=MAX_SQUARES)
    current = start
    while current > 0:
        yield current
        current -= 1
```

The tests verify that `list(countdown(3))` is `[3, 2, 1]` and that
`list(countdown(0))` is the empty boundary `[]`. Negative, Boolean,
non-integer, and over-limit bounds are rejected when consumption begins.

**Modify — O3 TODO:** Create two iterators from the same list. Consume two
values from the first and one from the second. Predict the three results.

```python todo
values = ["A", "B"]
first = iter(values)
second = iter(values)
# TODO: call next twice on first and once on second, then print each result.
```

**Hint:** iterator state belongs to `first` or `second`, not to `values`.

**Explained solution:** the observations are `A`, `B`, then `A`. The second
iterator starts its own traversal.

```python runnable
values = ["A", "B"]
first = iter(values)
second = iter(values)
print(next(first))
print(next(first))
print(next(second))
```

```text output
A
B
A
```

### P2. Exhaustion, defaults, and recovery

Objective: recognize exhaustion as a normal protocol event and choose an
explicit recovery.

A direct `next` with no default raises `StopIteration` after the final value:

<!-- bookcheck: expect-error="StopIteration" -->
```python expected-error
cursor = iter(["A"])
print(next(cursor))
print(next(cursor))
```

The first call prints `A`; the second reaches the intended stable signal
`StopIteration`. A `for` loop handles this signal internally and ends normally.
Do not broadly catch every exception just to keep requesting values.

There are two common recoveries:

1. If the source is reusable, ask it for a **new iterator**.
2. If exhaustion is expected in a step-by-step API, pass a deliberate default
   to `next`.

```python runnable
values = ["A"]
spent = iter(values)
print(next(spent))
print(next(spent, "done"))

fresh = iter(values)
print(next(fresh))
```

```text output
A
done
A
```

A string default is ambiguous if the stream can legitimately contain that
same string. A private sentinel object makes absence distinguishable by
identity:

```python runnable
missing = object()
value = next(iter([]), missing)
print(value is missing)
```

```text output
True
```

**Modify — O4 TODO:** Given `values = [0]`, use a private sentinel to
distinguish the real value `0` from exhaustion. Observe both requests.

```python todo
values = [0]
missing = object()
cursor = iter(values)
# TODO: request twice with missing as the default and compare each result by identity.
```

**Hint:** `0` is false-like but present. Test absence with `is missing`, not
with `if not value`.

**Explained solution:** the first result is `0` and `first is missing` is
`False`; the second result is the sentinel and `second is missing` is `True`.

```python runnable
values = [0]
missing = object()
cursor = iter(values)
first = next(cursor, missing)
second = next(cursor, missing)
print(first, first is missing)
print(second is missing)
```

```text output
0 False
True
```

### P3. Keep source mutation separate

Objective: avoid changing the structure that controls the traversal unless a
specific collection contract has been taught and tested.

Removing or inserting items in the same list being traversed can skip values
because positions shift while the iterator advances. Build a separate result
instead:

```python runnable
raw_labels = ["draft", "", "review", ""]
clean_labels = []

for label in raw_labels:
    if label:
        clean_labels.append(label)

print(raw_labels)
print(clean_labels)
```

```text output
['draft', '', 'review', '']
['draft', 'review']
```

The original remains available for diagnosis, and the result has an obvious
contract. A comprehension is also clear here:
`[label for label in raw_labels if label]`.

Common mistake: observing one successful mutation example and assuming all
collections guarantee it. They do not share one mutation-during-iteration
contract. Prefer a snapshot or a separate result unless the exact behavior is
both necessary and verified.

### Professional guided challenge

Trace a queue of synthetic stages without modifying it. Consume `"draft"`,
then `"review"`, observe exhaustion with a private sentinel, and recover by
creating a fresh traversal that again returns `"draft"`.

```python todo
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
# TODO 1: consume and print both stages.
# TODO 2: request once more with missing as the default and prove identity.
# TODO 3: create a fresh iterator and print its first value.
```

**Hint:** do not assign `fresh = cursor`; that gives the same exhausted object.
Call `iter(stages)` again.

**Explained solution:** traversal state is isolated in each iterator. The
original list is reusable; `cursor` is not reset by assigning another name.

```python runnable
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
print(next(cursor))
print(next(cursor))
print(next(cursor, missing) is missing)

fresh = iter(stages)
print(next(fresh))
```

```text output
draft
review
True
draft
```

### Professional checkpoint and rubric

Complete the guided trace and the countdown edge tests. Explain iterable,
iterator, current state, exhaustion, default, and recreation in your own words.

Score one point for each:

- **Identity:** you distinguish a reusable list from each iterator it creates.
- **State:** your prediction follows each iterator independently.
- **Boundary:** an empty iterator uses an unambiguous sentinel.
- **Recovery:** a fresh traversal is created from the reusable source.
- **Safety and explanation:** the source is not structurally mutated, and you
  can explain why assigning another name does not rewind an iterator.

A score of 4/5, including **Recovery**, completes the professional route.
Reflection: which APIs you use return reusable collections, and which might
return one-shot iterators?

## Optional advanced route: bounded lazy pipelines

Review Chapter 14 before A6 and A7: those sections use `try`, `finally`, and
exception categories. Everything below remains optional for essential course
progress.

### A1. Generator expressions defer work

Objective: distinguish a materialized collection from an on-demand iterator.

Square brackets build all list values immediately. Parentheses around the same
comprehension syntax create a generator expression:

```python runnable
numbers = [1, 2, 3]
materialized = [number * number for number in numbers]
lazy = (number * number for number in numbers)

print(materialized)
print(next(lazy))
print(list(lazy))
```

```text output
[1, 4, 9]
1
[4, 9]
```

The first `next` consumes `1`; `list(lazy)` receives only the remaining values.
The generator is one-shot. Laziness changes **when** values are requested; it
does not promise that the work is fast or that an unbounded consumer is safe.

**Modify — O5 TODO:** Predict the result of two calls to `next(lazy)` followed
by `list(lazy)` for four input numbers. Then run a finite version.

**Hint:** cross out a source value every time the consumer requests one.

### A2. Generator functions pause at `yield`

A function containing `yield` creates a generator. Calling it creates the
generator object but does not yet run its body. Each request resumes execution
until the next `yield`, normal `return`, or failure.

The tested `countdown` source appeared in P1. For `countdown(3)`, three requests
yield `3`, `2`, and `1`; the next request observes exhaustion. Its validation
also begins on consumption, so `countdown(-1)` can be constructed but fails
with `ValueError` when first consumed.

**Modify — O5 TODO:** Predict `list(countdown(0))` and
`list(countdown(2))` before consulting the test results.

**Explained solution:** zero enters the valid boundary but the loop body never
runs, so the result is `[]`. Two yields `[2, 1]` and then returns normally.

### A3. Bound an otherwise infinite source

`itertools.count()` can keep producing integers. The companion puts an
explicit, validated limit in front of it and caps that requested limit at
`MAX_SQUARES = 10_000`. This is a teaching guardrail, not a universal domain
constant.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def bounded_squares(limit):
    """Yield the first ``limit`` squares from an otherwise infinite source."""
    _require_bounded_integer(limit, name="limit", maximum=MAX_SQUARES)
    squares = (number * number for number in count())
    yield from islice(squares, limit)
```

The tests consume exactly five values and observe `[0, 1, 4, 9, 16]`. A zero
limit yields nothing. A negative, Boolean, non-integer, or over-limit value is
rejected at the first consumption step.

Do not materialize an infinite source without a limiter. Even a lazy producer
becomes unbounded if the consumer keeps requesting forever or stores every
result. Bound item count, time, input, and owned resources at the appropriate
boundary.

**Modify — O5 TODO:** Change a finite `islice` limit from 5 to 7 and predict
the final two squares. Then test `limit = 0`.

**Hint:** the source begins at zero; square indexes 5 and 6 for the new tail.

**Explained solution:** seven values are
`[0, 1, 4, 9, 16, 25, 36]`; zero values produce `[]`. The limiter, not the
generator expression alone, provides termination.

### A4. Delegate with `yield from`

Objective: forward values from a finite sub-iterable without a nested manual
yield loop.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def flatten(groups):
    """Yield every value from each finite group in order."""
    for group in groups:
        yield from group
```

For `[["A", "B"], [], ["C"]]`, the verified result is
`["A", "B", "C"]`. The empty inner group contributes no value and does not
need a special case.

**Modify — O5 TODO:** Add empty groups at the beginning and end. Predict the
same result before running.

**Hint:** `yield from []` simply completes immediately.

### A5. Delayed failure is still failure

Objective: connect a diagnostic to the consumption step that reached invalid
data.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def reciprocals(values):
    """Yield reciprocals; an invalid later value fails when it is consumed."""
    for value in values:
        yield 1 / value
```

Constructing `reciprocals([2, 0, 4])` succeeds because no division has happened.
The first `next` yields `0.5`; the second reaches zero and raises the stable
category `ZeroDivisionError`. The later `4` is never consumed from that failed
generator.

**Recovery — O6 TODO:** Correct the invalid input and create a new generator.
Do not assume the failed object can be rewound.

**Hint:** the tested recovery input is `[2, 4]`.

**Explained solution:** a new `reciprocals([2, 4])` produces `[0.5, 0.25]`.
The correction changes the invalid domain value and restarts traversal from a
known state.

### A6. Deterministic cleanup after early closure

Objective: release an owned local resource when a started generator completes,
fails, or is explicitly closed.

This companion accepts a fake `close` callback so the test can observe cleanup
without opening a real file or network connection:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def managed_values(values, close):
    """Yield values and call ``close`` once when an active generator ends."""
    if not callable(close):
        raise TypeError("close must be callable")
    try:
        yield from values
    finally:
        close()
```

The cleanup test starts the generator, consumes `"A"`, calls `cursor.close()`,
and observes `events == ["closed"]`. Calling `close` again does not append a
second event. Normal full exhaustion also runs cleanup once. A non-callable
cleanup value raises `TypeError` when consumption begins.

Important edge: closing a generator that has never started does not enter its
body, so it cannot rely on that body to acquire and then release a resource.
Acquire a resource only inside the active lifetime you control, and close a
started generator explicitly when the consumer stops early. Do not rely on
garbage-collection timing.

**Modify — O6 TODO:** Use `events = []`, start a two-value `managed_values`,
consume one value, close it, and assert the one cleanup event.

**Hint:** inspect `events` before and after `cursor.close()`.

### A7. End with `return`, not `StopIteration`

A generator ends normally when execution reaches the end or executes `return`.
Explicitly raising `StopIteration` inside its body is translated to the stable
category `RuntimeError` on the declared Python runtime. Predict the final
exception category:

<!-- bookcheck: expect-error="RuntimeError" -->
```python expected-error
def broken_generator():
    yield "ready"
    raise StopIteration("finished")

cursor = broken_generator()
print(next(cursor))
print(next(cursor))
```

The first request prints `ready`; the second reaches the incorrect explicit
raise and fails with `RuntimeError`. Full traceback prose is not the contract.

**Recovery:** replace the explicit raise with `return`.

```python runnable
def finished_generator():
    yield "ready"
    return

print(list(finished_generator()))
```

```text output
['ready']
```

### Advanced guided challenge

Build a finite report with standard-library tools only:

```python todo
from itertools import count, islice

limit = 4
# TODO 1: create a generator expression of squares from count().
# TODO 2: bound it with islice(..., limit).
# TODO 3: materialize only those four values and print them.
# TODO 4: repeat with limit = 0.
```

**Hint:** the consumer should receive `islice(squares, limit)`, never the
unbounded source directly.

**Explained solution:** create the lazy square expression, put `islice` between
it and `list`, then materialize the finite view.

```python runnable
from itertools import count, islice

limit = 4
squares = (number * number for number in count())
result = list(islice(squares, limit))
print(result)
```

```text output
[0, 1, 4, 9]
```

The zero boundary returns `[]`. A negative or huge learner-selected limit
needs validation before it reaches this construction; the companion's
`bounded_squares` owns that checked contract.

### Advanced checkpoint and rubric

Complete the bounded report, delayed-failure recovery, and cleanup TODO. Then
explain when each generator begins work and how it terminates.

Score one point for each:

- **Laziness:** you distinguish construction from the first consumption step.
- **Bounds:** every otherwise infinite source has an explicit validated finite
  consumer limit.
- **One-shot state:** a spent or failed generator is recreated deliberately.
- **Recovery:** invalid input is corrected and the repaired neighbor succeeds.
- **Delegation:** `yield from` preserves finite group order, including empty
  groups.
- **Cleanup and explanation:** a started generator closes its fake resource
  exactly once, and you explain why `return` is normal termination.

A score of 5/6, including **Bounds** and **Cleanup and explanation**, completes
the optional advanced route. Reflection: which limit belongs to the producer,
which to the consumer, and who owns cleanup in your pipeline?

## Common mistakes and calm recoveries

- **Dense comprehensions:** if you need to decode the line twice, return to a
  named loop or split intermediate values.
- **Depending on set order:** compare set membership or sort only for a stable
  display; do not promise an arbitrary rendered order.
- **Using ordinary `zip` when lengths must match:** select `strict=True`, consume
  the result, correct the source mismatch, and rerun.
- **Assuming `zip` validates at construction:** it discovers input exhaustion
  as the consumer advances.
- **Calling `next` forever:** handle exhaustion with a `for` loop, a deliberate
  default, or a new iterator from a reusable source.
- **Treating a generator as rewindable:** recreate it from the original inputs.
- **Mutating the traversed collection:** build a separate result or an explicit
  snapshot.
- **Calling a pipeline “safe because lazy”:** add an item/time/input bound and
  deterministic resource cleanup.
- **Expecting validation at generator construction:** remember that a generator
  body begins on consumption; test the first request.
- **Raising `StopIteration` inside a generator:** use `return` for normal end.

Errors in this chapter are observations, not personal failures. Reduce the
example to one producer, one consumer, and one expected next value; then repair
that smallest contract and rerun its happy neighbor.

## Verify the executable contract

From the repository root, run the declared standard-library suite:

```bash illustrative
python -B -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'
```

`-B` prevents bytecode cache creation. Discovery adds the companion `examples`
directory as the test import root and runs only `test_*.py` below its `tests`
package. The suite checks:

- normal and empty strict pairing plus unequal-length `ValueError`;
- normal, zero, invalid-bound, exhausted, and recreated countdowns;
- the first five bounded squares and invalid limits;
- finite delegation with empty groups;
- delayed `ZeroDivisionError` and corrected-input recovery; and
- partial closure, normal exhaustion, invalid cleanup, and exactly-once cleanup.

The command is expected to exit zero. A missing interpreter or a nonzero test
result is not a pass: read the first failing test, correct the smallest contract,
remove temporary state, and rerun both that case and its happy neighbor.

The Markdown `source-ref` blocks are registered under
`learning:contract`. They are evidence links, not code executed by the generic
Markdown path. The explicit learning-bridges check owns their companion
behavior; small `runnable` and `expected-error` blocks remain eligible for the
bounded generic verifier.

Verification proves the behavior exercised on the selected interpreter. It
does not by itself prove teaching quality, translation fluency, broad platform
compatibility, accessibility, or publication approval.

## Summary and closing reflection

You can now choose a traversal tool by contract:

- use an ordinary loop when its steps are clearest;
- use a simple comprehension to build a small concrete collection;
- use `enumerate` for positions and strict `zip` for equal-length pairing;
- treat iterator state and exhaustion explicitly; and
- use a generator only with a deliberate consumer bound and cleanup owner.

Before moving on, explain one pipeline aloud: where values originate, where
state lives, what stops consumption, which failure is recoverable, and who
cleans up. If each answer is concrete, the syntax is no longer magic—you are
designing the data flow.
