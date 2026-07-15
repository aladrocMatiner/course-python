# Chapter 26 canonical implementation traceability

This maintainer record maps the canonical English objectives to learner-facing
teaching and executable evidence. It is not a language variant and it does not
approve future translations, rendered accessibility, provenance, or
publication.

## Evidence boundary

- Canonical lesson: `chapter-26-iteration-generators/README.md`.
- Companion authority:
  `chapter-26-iteration-generators/examples/iteration_pipeline.py`.
- Behavioral tests:
  `chapter-26-iteration-generators/examples/tests/test_iteration_pipeline.py`.
- Companion `source-ref` check ID: `learning:contract`.
- Declared command from the repository root:
  `python -B -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'`.
- Generic `runnable` and `expected-error` fences remain direct lesson evidence;
  they are not represented as executed merely because a companion check passes.

The command uses only the standard library and finite fake data. `-B` prevents
bytecode caches. A nonzero result, unavailable interpreter, timeout, output
bound, source mutation, or residue is a non-pass.

## O1 — Transform clearly

- **Prerequisite:** Chapter 10 loops and the Chapter 11 foundational checkpoint.
- **Teaching and prediction:**
  [`E1. Derive a comprehension from a loop`](README.md#e1-derive-a-comprehension-from-a-loop)
  asks for state prediction before comparing the loop with list, dictionary,
  and set comprehensions.
- **TODO and hint:** the O1 TODO derives one expression and one condition from
  the visible loop; its hint restates the original body in execution order.
- **Happy and edge behavior:** `[6, 10, 16]`, deterministic dictionary insertion
  order, set membership without set-order claims, and empty list/dict/set
  outcomes are direct `runnable`/`output` fence contracts.
- **Failure and recovery:** the section rejects dense, nested, side-effecting
  essential comprehensions and recovers to a named ordinary loop or split
  intermediate values.
- **Explained solution:** the `selected = [score + 1 ...]` example explains why
  expression, loop, and condition retain the original meaning.
- **Checkpoint/rubric:**
  [`Essential checkpoint and rubric`](README.md#essential-checkpoint-and-rubric),
  especially readability and boundary categories.
- **Source/evidence:** the canonical direct fences are the source rather than a
  `source-ref` indirection; the companion's bounded generator expression is
  shown under the registered `learning:contract` reference in A3.
- **Test:**
  `EssentialSyntaxTests.test_comprehensions_preserve_documented_collection_semantics`.

## O2 — Enumerate and pair safely

- **Prerequisite:** O1 and familiar tuple unpacking from earlier collection
  chapters.
- **Teaching and prediction:**
  [`E2. Enumerate positions without a manual counter`](README.md#e2-enumerate-positions-without-a-manual-counter)
  and
  [`E3. Pair data without silent loss`](README.md#e3-pair-data-without-silent-loss)
  ask learners to predict position pairs and the strict mismatch phase.
- **TODO and hint:** the E2 TODO changes only `start`; the
  [`essential guided challenge`](README.md#essential-guided-challenge) combines
  strict pairing, enumeration, and one readable formatting comprehension.
- **Happy and edge behavior:** display positions begin at one; two empty strict
  inputs return `[]`; ordinary `zip` truncation remains observable and
  deliberate.
- **Failure and recovery:** unequal strict inputs raise `ValueError` during
  consumption; recovery corrects the input lengths instead of silently
  weakening the contract.
- **Explained solution:** the numbered scoreboard separates pairing, positioning,
  formatting, and printing.
- **Checkpoint/rubric:** the essential checkpoint requires strict mismatch
  recovery and an explanation of display position versus collection index.
- **Source-ref:** `strict_pairs` in `examples/iteration_pipeline.py`, referenced
  from E3 with `check="learning:contract"`.
- **Tests:**
  `EssentialSyntaxTests.test_enumerate_uses_the_declared_display_start`,
  `EssentialSyntaxTests.test_non_strict_zip_truncation_is_deliberate_and_observable`,
  and all three `StrictPairsTests`.

## O3 — Explain iterator state

- **Prerequisite:** essential checkpoint and foundational function calls.
- **Teaching and prediction:**
  [`P1. Iterable and iterator are different roles`](README.md#p1-iterable-and-iterator-are-different-roles)
  traces two independent cursors and asks for three predicted values.
- **TODO and hint:** learners consume two values from one iterator and one from
  another; the hint locates state in each iterator rather than the list.
- **Happy and edge behavior:** `iter(cursor) is cursor`, normal `A`/`B`
  consumption, `countdown(3) == [3, 2, 1]`, and the zero countdown boundary.
- **Failure and recovery:** exhausted direct `next` raises `StopIteration`; a
  reusable source creates a fresh iterator, while an arbitrary generator is
  never described as rewindable.
- **Explained solution:** the two-iterator example produces `A`, `B`, then `A`
  and explains independent traversal state.
- **Checkpoint/rubric:**
  [`Professional checkpoint and rubric`](README.md#professional-checkpoint-and-rubric),
  especially identity, state, and recovery.
- **Source-ref:** `countdown` in `examples/iteration_pipeline.py`, referenced
  from P1 with `check="learning:contract"`.
- **Tests:** all `CountdownTests`, including explicit one-shot exhaustion and
  recreation.

## O4 — Protect traversal

- **Prerequisite:** O3 plus Chapter 2 identity and false-like-value semantics.
- **Teaching and prediction:**
  [`P2. Exhaustion, defaults, and recovery`](README.md#p2-exhaustion-defaults-and-recovery)
  predicts an intended `StopIteration`; P3 compares the unchanged source with a
  separate cleaned result.
- **TODO and hint:** the sentinel TODO distinguishes real `0` from exhaustion;
  the professional challenge warns that `fresh = cursor` does not rewind state.
- **Happy and edge behavior:** a private sentinel handles empty input without
  confusing absence with `0`; a separate result preserves the original list.
- **Failure and recovery:** the lesson rejects broad exception swallowing and
  mutation of the list controlling traversal; recovery uses a deliberate
  default, a fresh iterator, a snapshot, or a separate result.
- **Explained solution:** the sentinel identity output is `0 False` and then
  `True`; the professional trace ends and recreates traversal explicitly.
- **Checkpoint/rubric:** professional boundary, recovery, safety, and explanation
  categories.
- **Source/evidence:** direct `runnable` and `expected-error` fences are the
  canonical source; iterator exhaustion is also exercised through the
  `countdown` `learning:contract` source reference.
- **Tests:**
  `CountdownTests.test_exhaustion_is_one_shot_and_recovery_recreates_generator`
  plus the bounded direct-fence evidence for the private sentinel and unchanged
  source/result values.

## O5 — Build bounded lazy work

- **Prerequisite:** professional checkpoint; Chapter 14 is required only when
  entering the later cleanup/error sections.
- **Teaching and prediction:** A1 predicts partial generator-expression
  consumption; A2 traces pause/resume; A3 predicts a seven-value finite view;
  A4 predicts delegation across empty groups.
- **TODO and hint:** each section asks for one bounded modification, and the
  [`advanced guided challenge`](README.md#advanced-guided-challenge) places
  `islice` between `count()` and `list`.
- **Happy and edge behavior:** partial one-shot consumption, zero countdown,
  first five squares `[0, 1, 4, 9, 16]`, zero limit, and empty delegated groups.
- **Failure and recovery:** invalid square/countdown bounds fail when consumed;
  the lesson never asks a learner to materialize an infinite source and recovers
  by validating a finite limit.
- **Explained solution:** the four-value advanced challenge yields
  `[0, 1, 4, 9]` and identifies the limiter—not laziness alone—as the termination
  contract.
- **Checkpoint/rubric:**
  [`Advanced checkpoint and rubric`](README.md#advanced-checkpoint-and-rubric),
  especially laziness, bounds, one-shot state, and delegation.
- **Source-refs:** `countdown`, `bounded_squares`, and `flatten` in
  `examples/iteration_pipeline.py`, each referenced with
  `check="learning:contract"`.
- **Tests:** all `BoundedSquaresTests`, all `DelegationTests`, and the normal and
  zero-bound `CountdownTests`.

## O6 — Recover and clean up

- **Prerequisite:** O5 and Chapter 14 exception/finally semantics.
- **Teaching and prediction:** A5 locates failure at the second consumption
  request; A6 predicts the cleanup-event sequence; A7 predicts `RuntimeError`
  from an explicit `StopIteration` inside a generator.
- **TODO and hint:** corrected reciprocal input creates a new generator; cleanup
  starts then explicitly closes a two-value generator; the A7 recovery replaces
  explicit `StopIteration` with `return`.
- **Happy and edge behavior:** corrected reciprocals are `[0.5, 0.25]`; normal
  exhaustion and partial explicit closure each clean up once; repeated close
  does not duplicate cleanup.
- **Failure and recovery:** delayed zero raises `ZeroDivisionError`, a
  non-callable cleanup raises `TypeError`, and explicit generator
  `StopIteration` becomes `RuntimeError`; every case has a successful bounded
  neighbor.
- **Explained solution:** A5 explains recreation, A6 explains active lifetime
  ownership, and A7 shows normal termination with `return`.
- **Checkpoint/rubric:** advanced recovery and cleanup categories are mandatory
  for route completion.
- **Source-refs:** `reciprocals` and `managed_values` in
  `examples/iteration_pipeline.py`, referenced with
  `check="learning:contract"`.
- **Tests:** all `DelayedFailureTests` and all `CleanupTests`; the A7
  `expected-error`/recovery fence pair supplies the explicit
  `RuntimeError`/successful-return evidence.

## Contract-case inventory

- **Normal:** equal pairing, countdown 3, five squares, finite flatten,
  corrected reciprocals, and normal cleanup.
- **Empty/boundary:** empty pairs, countdown 0, square limit 0, empty outer and
  inner groups, and exhausted iterators.
- **Invalid:** unequal pairs; negative, over-limit, Boolean, and non-integer
  bounds; zero reciprocal; non-callable cleanup; explicit generator
  `StopIteration`.
- **Recovery:** equalized inputs, recreated iterators/generators, corrected
  reciprocal data, finite validated limits, explicit close, and `return`.
- **Hygiene:** import performs no work; tests use no external input or resource;
  the declared command uses `-B`; no cache, environment, report, credential,
  learner data, or generated artifact is an accepted result.

## Handoff boundary

Passing the suite and direct Markdown evidence supports the canonical technical
contract only. Spanish, Catalan, Swedish, and Arabic semantic parity, rendered
accessibility, Arabic bidirectional behavior, provenance/license acceptance,
learner comprehension, and publication sign-off remain separate human review
gates.
