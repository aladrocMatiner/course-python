# Appendix C · Software Design Patterns in Python

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we are going to build

You will evolve one small, synthetic **job runner**. It begins as a direct
`run(job)` function with explicit `Job` and `Result` values. A new pattern is
allowed only when a second variation or an ownership problem makes the direct
version difficult to change or verify. The goal is not to collect pattern
names. It is to make a defensible design decision, test it, and know when to
remove it.

All required work is local, standard-library-only, bounded, and designed for
CPython 3.11 or newer. The examples use invented job identifiers and fake
dependencies. They require no account, credential, public target, or learner
data.

By the end, you will be able to:

- recognize a design pressure before naming a pattern;
- compare a pattern with a function, mapping, module, closure, context manager,
  direct composition, or another simpler Python option;
- separate policy, construction, translation, observation, and ownership;
- test Retry, Circuit Breaker, and Bulkhead behavior without real networks or
  wall-clock sleeps;
- trace Reactor-like and structured-concurrency responsibilities in existing
  course code without rebuilding a server; and
- write a decision that includes the cost and a removal condition, not only the
  hoped-for benefit.

## Prerequisites and entry self-assessment

Essential assumes the [Chapter 11 foundational route](../chapter-11-functions/README.md#foundational-route-calls-return-values-scope-and-safe-defaults)
and its [checkpoint](../chapter-11-functions/README.md#checkpoint-and-rubric),
the [Chapter 12 Essential practice and recovery](../chapter-12-oop/README.md#essential-practice-and-recovery),
its [checkpoint](../chapter-12-oop/README.md#checkpoint-and-rubric),
[section 4 composition](../chapter-12-oop/README.md#4-inheritance-and-composition),
[Chapter 14: exceptions](../chapter-14-exceptions/README.md#checkpoint-and-rubric),
[Chapter 15: modules](../chapter-15-modulos/README.md#checkpoint-and-rubric), and
[Chapter 18: tests](../chapter-18-testing/README.md#checkpoint-and-rubric).
You do not need `dataclass`, `typing.Protocol`, a framework, or a third-party
test library for this appendix.

Try this diagnostic before starting. A wrong answer is a route to the missing
prerequisite, not a failure.

1. **Callable:** can you pass a function without calling it? Predict the
   difference between `choose(transform)` and `choose(transform())`. If not,
   revisit [functions as arguments](../chapter-11-functions/README.md#4-passing-functions-as-arguments).
2. **Composition:** can an object delegate work to a collaborator stored on an
   attribute? If not, revisit [composition](../chapter-12-oop/README.md#composition).
3. **Exception boundary:** can you catch one low-level exception and raise a
   domain exception with `raise ... from ...`? If not, revisit
   [exception chaining](../chapter-14-exceptions/README.md#5-chaining-raise-from-).
4. **Module boundary:** can you import a module without starting its program?
   If not, revisit [entry points](../chapter-15-modulos/README.md#5-entry-point).
5. **Test:** can you express arrange, act, and assert, including one expected
   exception? If you learned with `pytest`, use the short
   [`unittest` bridge](#a-minimal-unittest-bridge) below; otherwise revisit
   [Chapter 18](../chapter-18-testing/README.md#2-first-test).

If more than two answers are uncertain, stop safely and complete the linked
sections first. If one or two are uncertain, start Essential and use its
recovery point. Do not use the network branch as a shortcut around these
foundations.

## Routes, dependency graph, and time budget

The curriculum is ordered by learning progression. The indexes later in this
page are lookup tools, not the teaching order.

```text illustrative
              ┌→ Professional → Advanced ───────────┐
Essential ────┤                                     ├→ Network crosswalk
              └→ Network resilience → Capacity ─────┘
```

Text equivalent: everyone begins with Essential. From there, the core branch
runs through Professional and Advanced, while the network branch runs through
Network resilience and Capacity. The final Network crosswalk requires both
branch exits. The two branches may be studied in either order. There is no
informal network mini-bridge: every prerequisite in the table is a real gate.

| Route | Required previous work | Sessions | Observable exit |
|---|---|---:|---|
| Essential | entry prerequisites above | 2 × 60–75 min | policy, construction, and one incompatible boundary are separated with green tests |
| Professional | Essential | 2 × 60–75 min | cross-cutting behavior and removable notifications preserve the job contract |
| Advanced | Professional | 1–2 × 60–75 min | time, IDs, output, and execution are owned without globals or frameworks |
| Network resilience | Essential; Chapters 19 and 21; [Chapter 23 Intermediate](../chapter-23-network-programming/README.md#intermediate-checkpoint) | 3 × 60–75 min | safe attempts and dependency-health transitions are proved with injected time |
| Capacity | Network resilience; [Chapter 23 sections 7–8](../chapter-23-network-programming/README.md#advanced-route-bounded-concurrency-asyncio-and-tls) and its concurrency/cleanup outcome | 1 required + 1 optional × 60–75 min | remote saturation cannot consume local capacity; admission recovers; Pub/Sub is optional |
| Network crosswalk | Advanced and Capacity | 1 × 60–75 min | existing readiness and structured-concurrency responsibilities are traced and one simpler design is defended |

List equivalent:

- **Essential:** two sessions, then either branch is available.
- **Core branch:** Professional takes two sessions; Advanced takes one or two.
- **Network branch:** Resilience takes three sessions; required Capacity takes
  one. A second Capacity session is only for optional Pub/Sub.
- **Join:** Crosswalk takes one session and starts only after Advanced and
  Capacity.
- **Complete graph:** 10–12 sessions, about 10–15 hours. If Advanced is already
  complete, Resilience → Capacity → Crosswalk adds 5–6 sessions. From Essential,
  the same destination also requires the 3–4 Professional/Advanced sessions.

Split each session into 25–35 minute microcycles: **predict → execute or read a
bounded excerpt → observe → modify → verify → explain**. At every checkpoint
you may stop, keep a passing companion, and return later.

### Returning learner checkpoint self-assessment

You may enter at the next route only when you can demonstrate the previous
route's observable exit and explain its rubric without unplanned help:

- enter Professional after showing Strategy selection, function-Factory
  validation, Adapter error chaining, and the green Essential cases;
- enter Advanced after showing Decorator result/failure preservation and the
  bounded Observer cap, stable iteration, failure policy, and removal;
- enter Resilience after Essential plus the declared Chapters 19/21/23 gates;
- enter Capacity after proving the independently complete Resilience pipeline
  and Chapter 23 sections 7–8 cleanup outcome; and
- enter Crosswalk only after both Advanced ownership and required Bulkhead
  isolation/admission pass. Optional Pub/Sub never supplies or blocks this gate.

If an item is uncertain, use that route's starter and recovery point rather
than claiming checkpoint credit. Appendix C is an optional extension: none of
its checkpoints becomes a prerequisite for an existing course route.

## A small glossary

- **Pattern:** a named, reusable arrangement of responsibilities for a
  recurring design pressure; never an automatic rule.
- **Force:** a constraint or tension that makes a choice non-obvious.
- **Policy:** a choice about behavior, such as how a job is transformed.
- **Mechanism:** how work is carried out; for example, calling a dependency.
- **Boundary:** a place where data, control, errors, or ownership cross between
  parts of a program.
- **Port:** a small application-facing execution contract. An Adapter satisfies
  that contract for a specific collaborator.
- **Composition root:** the one outer place that constructs and connects
  collaborators.
- **Idempotent:** repeating the operation has the same intended effect as doing
  it once. A request key alone does not establish this property.
- **Total deadline:** the budget for the complete logical operation, including
  attempts, waiting, and backoff.
- **Dependency-health observation:** one final positive, negative, or neutral
  signal contributed by a logical operation to its Circuit Breaker.
- **Admission:** permission to enter a bounded capacity compartment.
- **Backpressure:** a producer waits because a downstream transport or consumer
  cannot currently accept more data. Application admission control is related
  but is not the same mechanism.
- **Companion:** repository source whose behavior is checked independently of
  the prose excerpt.

## The decision record used in every required exercise

Write one line for each arrow and support it with evidence:

```text illustrative
problem → forces → simplest Python option → chosen pattern → cost
        → expected failure → verification → when to remove it
```

Choosing direct code is a valid result. For example: “one fixed policy, no
runtime selection → a direct function is clearer → no pattern → add Strategy
only when a second tested policy appears.” A pattern without an expected
failure, a verification step, and a removal threshold is an unfinished
decision.

Premature abstraction is recoverable. If you added a global Singleton, an
abstract hierarchy, a Factory, a Facade, or an event bus before a second
implementation or ownership pressure appeared, return to the last passing
direct version. Keep the behavior test, remove the indirection, and record the
future observable pressure that would justify revisiting the choice. That is a
successful design correction, not lost work.

## Family index

This index groups the intentionally small inventory by family. “Decision-card”
means recognition and comparison only; “cross-link” means another chapter owns
the implementation.

<!-- bookcheck: table-alternative -->
| pattern/technique | symptom/problem | family | route | status (executable/decision-card/cross-link) | simpler alternative | checkpoint |
|---|---|---|---|---|---|---|
| function Factory | validated construction choice | creational | Essential | executable | mapping or direct constructor | Essential |
| Factory Method | subclasses choose construction | creational | Essential | decision-card | function Factory | Essential contrast |
| Strategy callable | behavior varies independently of selection | behavioral | Essential | executable | `if`/`match` or direct function | Essential |
| bounded synchronous Observer | several removable local notifications | behavioral | Professional | executable | explicit callback call | Professional |
| Command | request needs a stored executable value | behavioral | Professional | decision-card | function plus arguments | Professional card review |
| Template Method | invariant algorithm with subclass steps | behavioral | Professional | decision-card | function composition | Professional card review |
| Iterator/Generator | bounded lazy traversal | behavioral | Cross-link | cross-link | loop or comprehension | [Chapter 26](../chapter-26-iteration-generators/README.md) |
| Circuit Breaker with State | dependency health changes allowed calls | network/behavioral | Network resilience | executable | conditional plus transition table | Resilience |
| Adapter | incompatible data, method, or error boundary | structural | Essential/Advanced | executable | explicit conversion function | Essential; Advanced |
| Decorator through composition | cross-cutting behavior wraps one contract | structural | Professional | executable | direct logging/measurement call | Professional |
| Proxy | same interface controls access to another object | structural | Professional | decision-card | direct guard | Professional card review |
| Facade | clients need one simplified entry to a subsystem | structural | Advanced | decision-card | module function | Advanced card review |
| dependency injection + composition root + execution port | collaborators and ownership must be replaceable | architectural | Advanced | executable | explicit direct composition | Advanced |
| Repository/service layer | persistence and use-case boundary | architectural | Cross-link | cross-link | direct storage call | [Chapters 17/28](../chapter-28-professional-capstone/README.md#stage-1-foundation-immutable-domain-and-in-memory-service) |
| Singleton | exactly one process-global instance is proposed | architectural | Professional | decision-card | module-owned instance or explicit owner | Professional card review |
| Retry | retry-safe transient failure may recover | network | Network resilience | executable | one call or caller retry | Resilience |
| two Bulkheads | one dependency's saturation threatens another | network | Capacity | executable | semaphore, fail-fast limit, or no pattern | Capacity |
| bounded local Pub/Sub | optional enqueue-only local fan-out | network | Capacity optional | executable | Observer or direct calls | Optional Pub/Sub |
| Reactor-like responsibility trace | readiness dispatch needs ownership analysis | network | Network crosswalk | cross-link | streams with `TaskGroup` | Crosswalk |
| `TaskGroup`/Supervisor-like ownership trace | sibling lifetime and failure propagation are unclear | concurrency | Network crosswalk | cross-link | sequential awaits | Crosswalk |

Accessible list equivalent, preserving every field:

- **Creational:** function Factory — validated construction choice — Essential —
  executable — simpler mapping/direct constructor — Essential checkpoint;
  Factory Method — subclass construction — Essential — decision-card — simpler
  function Factory — Essential contrast.
- **Behavioral:** Strategy callable — variable behavior — Essential —
  executable — simpler `if`/`match` — Essential; Observer — removable local
  notification — Professional — executable — simpler direct callback —
  Professional; Command and Template Method — stored request or subclass steps —
  Professional — decision-cards — simpler function values/composition — card
  review; Iterator/Generator — lazy traversal — cross-link — simpler loop —
  Chapter 26; Circuit Breaker/State — health transitions — Resilience —
  executable — simpler conditional/transition table — Resilience.
- **Structural:** Adapter — incompatible boundary — Essential/Advanced —
  executable — simpler conversion function — Essential and Advanced; Decorator
  composition — cross-cutting wrapper — Professional — executable — simpler
  direct call — Professional; Proxy — access control — Professional — card —
  simpler guard — card review; Facade — subsystem simplification — Advanced —
  card — simpler module function — card review.
- **Architectural:** dependency injection/composition root/port — replaceable
  owned collaborators — Advanced — executable — simpler direct composition —
  Advanced; Repository/service layer — persistence/use-case boundary —
  cross-link — simpler direct storage — Chapters 17/28; Singleton — proposed
  process-global instance — Professional — card — simpler module owner or
  explicit owner — card review.
- **Network/concurrency:** Retry — retry-safe transient recovery — Resilience —
  executable — simpler one call — Resilience; two Bulkheads — failure-domain
  isolation — Capacity — executable — simpler semaphore/fail-fast — Capacity;
  Pub/Sub — optional enqueue-only fan-out — Capacity optional — executable —
  simpler Observer/direct calls — optional checkpoint; Reactor-like and
  `TaskGroup`/Supervisor-like traces — readiness/lifetime ownership — Crosswalk —
  cross-links — simpler streams/`TaskGroup` or sequential awaits — Crosswalk.

Builder and Composite are deliberately omitted. More names would consume time
without adding a new observed seam in this job runner.

## Problem index

<!-- bookcheck: table-alternative -->
| pattern/technique | symptom/problem | family | route | status (executable/decision-card/cross-link) | simpler alternative | checkpoint |
|---|---|---|---|---|---|---|
| Strategy callable | a second policy changes behavior | behavioral | Essential | executable | `if`/`match` | Essential |
| function Factory | callers repeat selection and validation | creational | Essential | executable | mapping/direct constructor | Essential |
| Factory Method | subclasses, not configuration, own creation | creational | Essential | decision-card | function Factory | Essential contrast |
| Adapter | legacy collaborator speaks different data/method/error language | structural | Essential/Advanced | executable | conversion function | Essential; Advanced |
| Decorator through composition | measurement must wrap return and failure consistently | structural | Professional | executable | direct measurement call | Professional |
| bounded synchronous Observer | removable listeners need stable local notification | behavioral | Professional | executable | explicit callbacks | Professional |
| Command | work must be queued/stored as a value | behavioral | Professional | decision-card | function plus arguments | Professional card review |
| Singleton | hidden global instance is being proposed | architectural | Professional | decision-card | explicit owner/module | Professional card review |
| Proxy | access control must preserve the same interface | structural | Professional | decision-card | direct guard | Professional card review |
| Template Method | subclasses alter fixed algorithm steps | behavioral | Professional | decision-card | composed functions | Professional card review |
| dependency injection + composition root + execution port | tests cannot control time, IDs, output, or execution | architectural | Advanced | executable | direct explicit composition | Advanced |
| Facade | callers are coupled to many subsystem steps | structural | Advanced | decision-card | module function | Advanced card review |
| Retry | safe transient calls may recover within one deadline | network | Network resilience | executable | single call | Resilience |
| Circuit Breaker with State | repeated unhealthy calls waste budget | network/behavioral | Network resilience | executable | conditional/transition table | Resilience |
| two Bulkheads | remote saturation consumes local capacity | network | Capacity | executable | semaphore/fail-fast/no pattern | Capacity |
| bounded local Pub/Sub | optional fan-out must isolate one slow subscriber | network | Capacity optional | executable | Observer/direct calls | Optional Pub/Sub |
| Reactor-like responsibility trace | readiness registration and dispatch ownership is unclear | network | Network crosswalk | cross-link | streams + `TaskGroup` | Crosswalk |
| `TaskGroup`/Supervisor-like ownership trace | sibling cancellation and cleanup ownership is unclear | concurrency | Network crosswalk | cross-link | sequential awaits | Crosswalk |
| Iterator/Generator | traversal is lazy or potentially unbounded | behavioral | Cross-link | cross-link | loop/comprehension | Chapter 26 |
| Repository/service layer | persistence leaks into use-case decisions | architectural | Cross-link | cross-link | direct storage | Chapters 17/28 |

Accessible list equivalent by symptom:

- A second behavior calls for Strategy; repeated validated construction calls
  for a function Factory; subclass-owned creation only earns the Factory Method
  card. These are Essential, with `if`/`match`, a mapping, or a direct
  constructor as simpler options.
- An incompatible collaborator calls for Adapter; cross-cutting measurement
  calls for Decorator composition; removable local listeners call for bounded
  Observer. The first is Essential/Advanced and the other two are Professional.
- Stored work, hidden global ownership, same-interface access control, and
  subclass algorithm hooks map to the Professional Command, Singleton, Proxy,
  and Template Method cards. They remain non-executable comparisons.
- Uncontrolled time/IDs/output/execution maps to Advanced composition, injection,
  one port, and an in-memory Adapter. Many subsystem calls map only to the
  Facade card.
- Retry-safe transient failure maps to Retry; repeated dependency-health
  failure maps to Circuit Breaker/State; saturation crossing health domains
  maps to two Bulkheads; optional bounded fan-out maps to local Pub/Sub.
- Readiness dispatch and sibling lifecycle map to existing-code cross-links.
  Lazy traversal and persistence boundaries remain owned by Chapters 26 and
  17/28.

## Companion and evidence boundary

The companion modules live under
`appendix-software-design-patterns/examples/patterns/`; network modules may be
absent until that implementation stage lands. The core contract is owned by
`patterns:core-suite`; resilience and capacity are owned by
`patterns:network-suite`. Source-reference acceptance is not a claim that a
code fence ran: it confirms that the excerpt exists in the named companion and
that its owning check is configured. See [VERIFICATION.md](VERIFICATION.md) for
the current evidence state.

Run only from the repository root. These invoke `unittest` through Python's
`-m` module entrypoint and pass the hyphenated directory as a discovery path;
they do not try to import that directory name as a Python package:

```text illustrative
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/examples/tests \
  -p 'test_core_patterns.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/examples/tests \
  -p 'test_network_patterns.py' -v
```

If a companion is not yet present in your checkout, stop at the route starter
and use the decision worksheet. Do not copy a guessed implementation from the
prose.

## Essential route — earn the first three seams

### Essential objectives and context

Across two sessions you will preserve one direct job contract while separating
three different pressures:

1. Strategy separates **behavior choice** from behavior execution.
2. A function Factory validates **construction choice** at the composition
   boundary.
3. Adapter translates **data, method, and error vocabulary** at one legacy
   boundary.

Factory is not Strategy with a different name: the Factory returns a configured
executor; Strategy is the callable that determines behavior. Adapter is not a
wrapper merely because it has another object inside; it must perform an
explicit translation.

### Essential prediction and starter

Before editing, predict what should remain true when a direct executor becomes
configurable: the same valid `Job` produces an equivalent `Result`; invalid jobs
still fail before collaborators run; and an unknown policy fails at selection,
not during arbitrary execution.

Start from the direct module and tests. Record the passing command and keep it
as your recovery point.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/direct.py check=patterns:core-suite -->
```python source-ref
def run(job):
    """Execute one job directly, with no pattern object or global state."""
```

The excerpt is intentionally tiny; behavior belongs to the companion tests,
not to prose that can drift.

### A minimal `unittest` bridge

Chapter 18 teaches the testing ideas with `pytest`. Here the standard-library
spelling is different, but the reasoning is the same:

```python illustrative
import unittest

class JobTests(unittest.TestCase):
    def test_valid_job_returns_expected_result(self):
        # arrange
        job = make_valid_job()
        # act
        result = run(job)
        # assert
        self.assertEqual(result.status, "completed")

    def test_invalid_job_is_rejected(self):
        with self.assertRaises(InvalidJob):
            run(make_invalid_job())
```

`assert x == y` becomes `self.assertEqual(x, y)`; `pytest.raises(Error)` becomes
`self.assertRaises(Error)`. Fixtures become small helper functions or
`setUp()`. This block is illustrative because the exact constructors are in the
companion.

### Essential guided TODOs and hints

1. **Strategy TODO:** add two callables, one preserving payload and one
   uppercasing it. Make selection a separate function. **Hint:** pass the
   callable itself; do not call it while selecting.
2. **Factory TODO:** make one function validate a name and return a configured
   executor. **Hint:** a dictionary from names to constructors can be simpler
   than a class hierarchy.
3. **Adapter TODO:** wrap the legacy fake. Translate the `Job` into its expected
   arguments, translate its result back, and chain its low-level failure into
   the application error. **Hint:** keep the legacy object unchanged.
4. **Decision TODO:** complete the eight-field record for each change. Include
   “use direct code” among the options.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/essential.py check=patterns:core-suite -->
```python source-ref
def select_policy(name):
    """Select a policy without executing or constructing an executor."""
```

### Essential happy, boundary, and recovery cases

- **Happy:** both policies return the same result shape and the Factory builds
  the selected executor.
- **Boundary:** an unknown selection raises the stable selection error before a
  job is executed. Empty or invalid job data is rejected once.
- **Recovery:** the legacy fake fails; the Adapter raises the application
  boundary error with the legacy exception retained as `__cause__`. The next
  valid call still succeeds and no mutable residue leaks between calls.

If your test fails after the Strategy change, return to direct `run(job)`, add
one equivalence assertion, then introduce only the callable. If the Adapter
test fails, write the three translations—input, call, output/error—as separate
lines before compacting anything.

### Essential explained solution and decisions

The Strategy solution uses interchangeable callables because Python functions
already carry behavior. Selection remains outside execution so adding a policy
does not alter the job runner. A class hierarchy would add state and lifecycle
that the observed pressure does not require.

The Factory is one validating function at the outer construction boundary.
**Factory Method contrast:** Factory Method delegates creation to subclasses;
that is useful only when subtype extension owns the choice. Here configuration
owns it, so the function is smaller and clearer.

The Adapter owns visible conversion. Contrast it carefully:

- a **Proxy** preserves essentially the same interface while controlling
  access;
- a **Facade** offers a simpler entry to a larger subsystem;
- a **Decorator** preserves a contract while adding behavior; and
- this **Adapter** changes the collaborator's data, method, and error language.

Complete decisions, in compact form:

- **Factory:** callers repeat selection/validation → configuration varies while
  construction must stay valid → mapping/direct constructor → function Factory
  → one indirect construction boundary → unknown name → construction and
  no-execution tests → remove when there is only one constructor.
- **Adapter:** the legacy method/data/error vocabulary is incompatible → the
  legacy collaborator cannot change → explicit conversion function → Adapter
  → translation code may drift → malformed reply or legacy failure →
  happy/malformed/chained-cause/recovery tests → remove when both sides share
  one contract.

Example decision record: “a second policy appears → selection varies but the
job contract must not → `if` is viable → choose a Strategy callable → indirect
call and one selection boundary → unknown name → equivalence and unknown-name
tests → remove when only one policy remains.” Write your own evidence rather
than copying this sentence.

### Essential common mistakes

- building a base class before a second behavior exists;
- mixing Factory validation into every caller;
- calling a Strategy during selection;
- catching every `Exception` in the Adapter and hiding programming errors;
- changing the legacy fake instead of proving translation; and
- describing a wrapper by shape instead of responsibility.

### Essential checkpoint, rubric, reflection, and exit

Score each item 0 (not yet), 1 (with documented hint), or 2 (independent):

- direct and refactored happy behavior are equivalent;
- unknown selection and invalid input fail at the intended boundary;
- the Adapter proves input, output, and chained-error translation;
- each decision record names a simpler option, cost, test, and removal point;
- you can explain function Factory versus Factory Method and Adapter versus
  Proxy/Facade/Decorator.

Eight of ten points, with all tests green, completes Essential. Reflect: which
change would you delete first if requirements contracted, and what test makes
that deletion safe? Safe stop: keep the direct and Essential suites passing.
You may now choose Professional or Network resilience.

## Professional route — cross-cutting behavior and notifications

### Professional objectives, prediction, and starter

Across two sessions, add measurement without changing return/failure behavior,
then add bounded synchronous notifications whose subscriptions can be removed.
Predict the order when wrappers are nested and when one observer unsubscribes
during notification. Start from the passing Essential checkpoint; that commit
or clean worktree is your recovery point.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/professional.py check=patterns:core-suite -->
```python source-ref
class MeasuringExecutor:
    """Observe an executor through composition without changing its contract."""
```

### Decorator through composition

The design-pattern Decorator is an object composition: it accepts an executor,
delegates to it, and adds bounded measurement on success and failure. Python's
`@decorator` is syntax that replaces a function or class with another value.
That syntax can implement a Decorator-like wrapper, but the syntax and the
responsibility pattern are not synonyms.

**TODO:** prove the wrapper returns exactly the delegated result and propagates
the delegated exception. **Hint:** record measurement in `finally`; do not turn
an error into a success. **Boundary:** two nested wrappers report a documented
order. **Recovery:** if identity or ordering becomes confusing, unwrap to one
executor, pass its tests, then add one wrapper at a time.

### Bounded synchronous Observer

The Observer owns a small set of subscribers. Notification is synchronous,
uses a stable snapshot, has a hard subscription cap, defines its observer
failure policy, retains no event history, and makes removal idempotent.
A callback that raises is reported by an opaque observer ID plus the stable
`observer_failed` code, removed before the next publication, and does not stop
the remaining callbacks in the current snapshot.

**TODO:** subscribe, notify, remove, and notify again. **Hint:** iterate over a
snapshot so removal during notification affects the next event, not the
current iteration. **Happy:** two observers see the event once. **Boundary:**
the cap rejects one extra subscription without disturbing existing ones.
**Recovery:** one observer fails according to the documented policy; later
notification and idempotent unsubscribe remain usable.

Complete decisions, in compact form:

- **Decorator:** measurement must surround both success and failure → the job
  contract cannot change → direct measurement call → composition Decorator →
  nesting/order can become hard to see → wrapped failure or wrong order →
  return/failure/order tests → remove when one explicit call is clearer.
- **Observer:** several removable local listeners appear → publication must be
  bounded and mutation-safe → explicit callback calls → synchronous Observer →
  subscription/failure policy adds state → cap or failing callback → cap,
  snapshot, failure, no-history, and unsubscribe tests → remove when one caller
  can invoke the listener directly.

### Professional decision cards

These cards are assessed as decisions, not implemented companions.

<!-- bookcheck: table-alternative -->
| Card | Pressure | Simpler Python option | Cost and expected failure | Verification and removal threshold |
|---|---|---|---|---|
| Command | a request must be stored, queued, undone, or audited as a value | function plus explicit arguments | command types and serialization can multiply; stale command data | round-trip/dispatch tests; remove when calls are immediate and never stored |
| Singleton | exactly one process-wide instance is proposed | module-owned value or explicit owner passed from the root | hidden state, order-dependent tests, lifetime ambiguity | isolation tests expose reset/lifetime; remove in favor of explicit ownership when contexts differ |
| Proxy | access, caching, or authorization must preserve the collaborator interface | direct guard before the call | wrapper can hide I/O/cost and drift from the interface | same-contract and denied-access tests; remove when access control moves to one clear boundary |
| Template Method | an invariant algorithm has subclass-defined steps | function composition or passed callables | inheritance couples steps and makes ordering implicit | order and substitution tests; remove when only one sequence remains |

List equivalent: Command stores a request value and can often be a function
plus arguments; verify storage/dispatch and remove it for immediate calls.
Singleton proposes one process-wide owner and can often be a module value or an
explicitly passed owner; verify isolation and remove hidden state when contexts
differ. Proxy preserves an interface while controlling access and can often be
a direct guard; verify allowed and denied paths and remove it when one boundary
owns access. Template Method fixes algorithm order while subclasses fill steps
and can often be composed functions; verify order/substitution and remove it
when only one sequence remains.

For every card, still write the full eight-field decision record. “No pattern”
with a reason is a correct answer.

### Transfer exercise — choose instead of copy

The second domain is a tiny shipping-price function, deliberately about twenty
lines and unrelated to the job runner.

**Starter:** standard delivery uses a distance rule; express adds one different
policy. **Prompt:** choose direct branching or a Strategy. Do not add Factory,
Observer, or a class hierarchy unless a stated pressure needs it.

**Prediction:** which part varies, and which output contract stays fixed?
**TODO:** implement standard and express behavior, then write the decision
record. **Hint:** two named callables may be enough. **Happy:** both valid modes
produce their expected price. **Boundary:** invalid distance is rejected before
policy execution. **Recovery:** unknown mode leaves the previous input and
configuration unchanged.

**Explained solution:** direct `if`/`match` is best while there are only two
local, obvious cases and no independent selection. A Strategy becomes useful
when selection and policy changes occur independently. Both solutions pass the
observable contract; the rubric grades reasoning, not pattern count.

### Professional mistakes, checkpoint, and reflection

Common mistakes are swallowing the wrapped failure, retaining an unbounded
event history, iterating a live subscriber collection, calling a synchronous
Observer a message broker, and implementing every decision card.

Rubric, 0–2 each:

- Decorator preserves result and failure while measurement remains observable;
- Observer proves cap, stable iteration, failure policy, no history, and
  idempotent removal;
- all four cards distinguish pressure, alternative, cost, verification, and
  removal;
- transfer solution handles happy/boundary/recovery and defends direct code or
  Strategy; and
- reflection explains why `@decorator` syntax is not the pattern definition.

Eight of ten and green core tests completes Professional. Reflect: where would
an explicit call be easier to debug than a wrapper or notification mechanism?
Safe stop: keep the transfer recovery answer and passing Professional tests.

## Advanced route — make ownership explicit

### Advanced objectives, prediction, and recovery point

In one or two sessions, move construction to one composition root, inject time,
IDs, output, and execution, define one small execution port, and satisfy it with
an in-memory Adapter. Predict which tests stop needing patches when these
collaborators become explicit. Start from Professional and keep its green suite
as the recovery point.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/architecture.py check=patterns:core-suite -->
```python source-ref
def compose_application(*, execution_port, new_id, clock, write):
    """Composition root: create the application only at the outer boundary."""
```

### Ownership before abstraction

Dependency injection means a collaborator arrives from the outside; it does
not require a container. The composition root is the outer function that picks
concrete collaborators. The execution port is the smallest application-facing
contract needed by the job use case; the in-memory Adapter provides a
deterministic implementation. Domain code must not discover a clock, random ID,
console, or process-global executor by itself.

**TODO:** replace one hidden collaborator at a time. Inject fixed time and a
sequence of IDs; capture output in a list; then swap the execution Adapter.
**Hint:** start with constructor arguments and ordinary methods. Add no framework
and no database.

- **Happy:** the composed application runs a valid job and records the expected
  result/output.
- **Boundary:** a fake runs out of IDs or the execution Adapter rejects a job;
  the application reports the stable boundary without corrupting stored state.
- **Recovery:** build a fresh root after failure and prove it starts clean; no
  module-global collaborator must be reset.

The explained solution centralizes concrete choice in `compose_application`,
leaves domain decisions independent of I/O, and uses explicit fakes. A justified
direct composition is accepted when there is one stable collaborator and tests
already control it. The port becomes removable when substitution no longer
occurs or its vocabulary merely duplicates one concrete API.

### Facade decision card and owned cross-links

**Facade card:** pressure—many clients repeat a multi-step subsystem sequence;
simpler option—a module function; possible choice—a stable simplified entry;
cost—hidden capabilities and an oversized surface; expected failure—Facade and
subsystem drift; verification—contract plus delegated-error tests; remove when
there is only one caller or the module function is sufficient.

Do not add a Repository here. [Chapter 17](../chapter-17-persistencia/README.md#4-a-simple-repository)
and [Chapter 28](../chapter-28-professional-capstone/README.md#stage-1-foundation-immutable-domain-and-in-memory-service)
own Repository/service-layer implementation and persistence depth. Appendix C
uses one execution port only.

### Advanced checkpoint, rubric, and reflection

Rubric, 0–2 each:

- one root visibly owns construction and lifetime;
- time, IDs, output, and execution are deterministic without global patches;
- swapping the in-memory Adapter preserves domain behavior;
- the decision accepts and explains direct composition or the chosen port; and
- the Facade card and Repository links remain comparisons, not duplicate code.

Eight of ten and green core tests completes Advanced. Reflect: which injected
collaborator represents a real boundary, and which would be needless ceremony
in a smaller program? Safe stop: retain a root built entirely from deterministic
fakes. Crosswalk remains locked until Capacity also passes.

## Network resilience route — safe retries before state

### Resilience prerequisites, objective, and starter

This three-session route requires Essential,
[Chapter 19's introductory retry](../chapter-19-http/README.md#3-simple-retries),
[Chapter 21 cancellation and cleanup](../chapter-21-async/README.md#cancellation-and-cleanup),
and the [Chapter 23 Intermediate checkpoint](../chapter-23-network-programming/README.md#intermediate-checkpoint).
Chapter 19 motivates repetition; Chapter 23's warning against automatic write
retries is the stronger boundary. This lab makes safety, deadline, cleanup, and
health accounting explicit with a fake dependency and injected monotonic time.
It performs no socket or HTTP call.

Chapter 19's small loop is useful introductory scaffolding, but it does not
establish that a write is retry-safe, share one total deadline across every
attempt and delay, or prove cancellation cleanup. Treat it as the question that
this route answers, not as the finished resilience policy.

Start from the resilience tests. Your recovery point is one validated, bounded
dependency call with no Retry and no Circuit Breaker.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/resilience.py check=patterns:network-suite -->
```python source-ref
TOTAL_DEADLINE_SECONDS = 0.5
MAX_ATTEMPTS = 3
```

### Session 1 — classify retry safety

Retry is eligible only after validation, only for
`TransientDependencyError`, and only when the operation is retry-safe. It is
retry-safe when it is side-effect free or idempotent by contract, or when the
fake dependency proves deduplication for one stable key throughout the lab.
Merely attaching a key is not enforcement.

**Prediction:** compare four operations: read-only; stable key with enforced
deduplication; stable key without enforcement; permanent failure. Which may
make a second call? **TODO:** encode the eligibility decision before the loop.
**Hint:** unsafe and permanent operations make at most their single requested
dependency call after validation and breaker permission.

Happy case: one transient then success for a safe operation. Boundary: a key
without enforced deduplication is rejected for automatic retry. Recovery: a
permanent failure propagates after one call; a later valid operation still
works.

### Session 2 — one deadline owns attempts and backoff

The exact contract is:

- one 500 ms monotonic total deadline;
- at most three attempts;
- each attempt gets `min(100 ms, remaining budget)`;
- injected backoffs are 50 ms then 100 ms; and
- a backoff starts only if its **full** duration fits. Otherwise the operation
  exhausts without a partial sleep or another call.

```text illustrative
validate → permission → attempt ≤100 ms → backoff 50 ms
                       → attempt ≤100 ms → backoff 100 ms
                       → attempt ≤100 ms → success or exhaustion
         all arrows consume the same 500 ms total budget
```

Text equivalent: validate first, obtain breaker permission, then make no more
than three individually bounded attempts. The two scheduled waits and every
attempt subtract from the same total budget. Stop before any step that cannot
fit its complete bound.

**TODO:** inject monotonic time and delay; never patch a global clock or use a
fixed sleep as proof. **Prediction:** if only 99 ms remains before the 100 ms
backoff, how many more calls occur? Answer: zero. **Recovery:** a timed-out owned
attempt is cancelled and awaited, then becomes
`TransientDependencyError(code="attempt_timeout")`. Caller cancellation instead
propagates unchanged after cleanup. Exhaustion chains the final transient cause.

### Session 3 — Circuit Breaker as justified State

Composition is independently complete here:

```text illustrative
validation → breaker permission → retry loop → per-attempt timeout → dependency
```

There is no Bulkhead prerequisite in this route. One Circuit Breaker belongs to
one dependency-health domain. Each logical operation contributes at most one
observation:

- **negative:** a final raw transient when Retry is unavailable/bypassed, or
  `RetryExhausted` whose cause is transient;
- **positive:** dependency success or a responsive permanent failure; and
- **neutral/local:** validation failure or caller cancellation before a health
  result.

Caller cancellation always propagates as `CancelledError`, but health still
reflects the last dependency result. Cancellation before any dependency result
is neutral. If one transient has already occurred and the caller cancels during
backoff, that logical operation contributes exactly one
negative for the transient; cancellation itself adds no second observation.

Three negatives without an intervening positive open the circuit. A positive
resets the count; neutral does nothing. OPEN fails with stable `circuit_open`
and zero dependency calls. After an injected one-second cooldown, exactly one
caller gets one 100 ms HALF_OPEN attempt with no Retry. Positive closes;
transient/timeout reopens with a fresh cooldown. Cancellation releases the
probe, propagates, and leaves OPEN with the already elapsed eligibility—no
invented cooldown.

**State contrast:** use `if`, `match`, or a transition table while transitions
remain small and explicit. State earns its place here only because CLOSED,
OPEN, and exclusive HALF_OPEN permission have different behavior and cleanup.

### Resilience cases, solution, and decision

- **Happy:** safe transient then success; the breaker observes one positive.
- **Boundary:** nine failed dependency calls from three exhausted, safe logical
  operations produce three negatives and open the circuit; the next operation
  makes zero calls.
- **Recovery:** cooldown admits one probe; success closes. A cancelled probe
  releases exclusivity and a later caller can probe immediately because the
  elapsed eligibility was not reset.
- **Cancellation classification:** cancelling before a first dependency result
  is neutral; cancelling during backoff after one transient still
  propagates, records that transient once, and leaves no owned work.

The solution orders safety and validation before looping, uses one total
deadline, owns every created attempt, and reports only the logical result to the
breaker. It does not count each retry attempt as a separate health observation.
Decision record: simpler one call or caller-controlled retry; Retry costs more
calls and duplicate-effect risk; Circuit Breaker costs shared state and
transition testing. Remove Retry when transient recovery is not observed or
the operation cannot be made safe. Remove the breaker when the dependency has
no shared health domain or callers already fail cheaply.

Common mistakes: retrying every exception, treating a key as deduplication,
resetting the total deadline per attempt, beginning partial backoff, swallowing
`CancelledError`, counting every attempt, and using a breaker per request.

### Resilience checkpoint, rubric, and stop

Rubric, 0–2 each:

- retry eligibility rejects key-without-enforcement and permanent failure after
  one call;
- exact attempt/backoff/deadline and cause-chaining cases pass with fake time;
- timed-out owned work is cancelled and awaited; caller cancellation remains
  visible;
- breaker positive/negative/neutral semantics, three-negative opening, and one
  exclusive probe are proved; pre-result cancellation is neutral while
  post-transient cancellation during backoff is exactly one negative,
  with `CancelledError` propagated; and
- the decision record explains the no-pattern option, State contrast, costs,
  failures, tests, and removal.

Eight of ten and green network resilience tests completes this route without
Capacity. Reflect: which fact establishes retry safety in your design, and
where is it proved? Safe stop: one passing
`validation → breaker → retry → timeout → dependency` pipeline with zero owned
work remaining.

## Capacity route — isolate admission, optionally fan out

### Capacity objective, starter, and ownership map

Capacity requires the Resilience checkpoint and Chapter 23's
[selector concurrency](../chapter-23-network-programming/README.md#7-several-clients-with-selectors)
and [asyncio/backpressure](../chapter-23-network-programming/README.md#8-apply-asyncio-streams-and-backpressure)
sections. Session one is required; session two, Pub/Sub, is separately
skippable. Begin with passing Resilience. That exact pipeline is the recovery
point.

Capacity adds one seam per attempt:

```text illustrative
validation → breaker permission → retry loop
           → Bulkhead lease per attempt → per-attempt timeout → dependency
```

Text equivalent: validate, ask the breaker, and enter Retry. Before each actual
dependency attempt, obtain the matching local or remote compartment lease. The
lease covers only that attempt and is released before backoff.

There are exactly two Bulkheads, `local` and `remote`. Each has one execution
lease and one waiting admission slot. There is no worker task and no second
waiter queue. A third proposal to the same full compartment fails immediately
with `overloaded`; it allocates nothing. One waiter expires after
`min(50 ms, remaining total deadline)` with `admission_timeout`.

```text illustrative
remote dependency health → remote Bulkhead [1 executing] [1 waiting]
local dependency health  → local Bulkhead  [1 executing] [1 waiting]
                              independent ownership and cleanup
```

Text equivalent: the remote and local health domains each own a separate
Bulkhead. Each permits one running attempt and one waiting admission. Filling
or recovering remote changes no local lease or waiter.

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/capacity.py check=patterns:network-suite -->
```python source-ref
EXECUTION_LIMIT = 1
WAITING_LIMIT = 1
```

### Do not confuse these mechanisms

| Term | Purpose | Owner | Failure signal → recovery |
|---|---|---|---|
| timeout | bound a logical operation, one attempt, or admission wait | operation policy, attempt owner, or Bulkhead respectively | `deadline_exhausted`, `attempt_timeout`, or `admission_timeout` → cancel/await owned work, remove local admission, and return the stable result |
| Retry | repeat only retry-safe transient work inside one budget | one `RetryPolicy` for the logical operation | `RetryExhausted` chained from the final transient → stop; caller handles the final outcome |
| Circuit Breaker | gate calls for one dependency-health domain | one `CircuitBreaker` for that domain | `circuit_open` → wait for injected cooldown eligibility, then allow one exclusive bounded probe |
| Bulkhead | isolate local execution/admission capacity by failure domain | separate `local` and `remote` Bulkheads | `overloaded` or `admission_timeout` → reject locally, release/remove once, and let later independent admission recover |
| rate limiting | constrain accepted work per time window | not implemented; would belong to an explicit edge/admission policy | no signal or recovery is claimed by this appendix |
| load shedding | select work to reject under pressure | not implemented as a general policy; immediate Bulkhead rejection is only one small example | `overloaded` demonstrates one rejection → caller receives it; no priority/fairness recovery is claimed |
| Pub/Sub | enqueue one local event independently for bounded subscribers | optional `PubSub` and each owned subscriber queue | `resource_limit` or `slow_subscriber` → preserve existing subscribers or disconnect the full one; healthy queues continue and a removed slot can be reused |
| `writer.drain()` flow control | wait for stream transport output capacity | `asyncio` stream writer/transport in Chapter 23 | bounded wait/connection failure → Chapter 23 owns timeout and close; Appendix C adds no application-admission claim |

List equivalent, with purpose, owner, failure, and recovery:

- **Timeout** bounds operation/attempt/admission waiting; the corresponding
  policy or owner emits `deadline_exhausted`, `attempt_timeout`, or
  `admission_timeout`, cancels/awaits or removes its work, and returns the stable
  result.
- **Retry** belongs to one logical-operation `RetryPolicy`; final transient
  exhaustion is chained in `RetryExhausted`, then repetition stops.
- **Circuit Breaker** belongs to one dependency-health domain; `circuit_open`
  fails cheaply until cooldown eligibility allows one exclusive bounded probe.
- **Bulkhead** belongs separately to `local` and `remote`; `overloaded` or
  `admission_timeout` is cleaned once so later independent admission can recover.
- **Rate limiting** would belong to an explicit time-window admission policy;
  it is absent, so this appendix claims no signal or recovery for it.
- **Load shedding** would own a broader rejection policy; immediate
  `overloaded` is only one example and creates no priority or fairness claim.
- **Pub/Sub** owns bounded local subscriber queues; `resource_limit` preserves
  current subscribers, while `slow_subscriber` removes the full queue and lets
  healthy queues continue before a slot is reused.
- **`writer.drain()` flow control** belongs to Chapter 23's stream
  writer/transport; that chapter owns bounded waiting and close recovery, not
  Appendix C admission.

This lab implements only the explicitly bounded timeout, Retry, breaker,
Bulkhead, and optional Pub/Sub contracts.

### Required saturation lab

**Prediction:** fill remote's execution lease and waiter, then propose another
remote operation and one local operation. The third remote proposal is rejected
immediately; local still completes.

**TODO:** acquire one lease per attempt, release it before backoff, and remove a
timed-out/cancelled waiter exactly once. **Hint:** admission consumes the same
500 ms total deadline and is a local event, not dependency health.

- **Happy:** one remote and one local operation complete independently.
- **Boundary:** saturated remote rejects its third proposal with `overloaded`;
  local remains available.
- **Recovery:** release remote; its single waiter is promoted. Admission timeout
  or cancellation leaves no waiter or lease.

Before the first dependency call, admission failure makes zero calls and is
neutral to breaker health. After a previous transient attempt, admission
failure stops Retry as `RetryExhausted` chained from that transient; admission
does not create another health observation. OPEN fails before capacity. A
HALF_OPEN probe that cannot obtain capacity releases probe ownership and keeps
the already elapsed eligibility.

Caller cancellation during admission still propagates. Before any dependency
result it is neutral; after an earlier transient in the same logical operation,
that transient contributes exactly one negative and cancellation adds no second
observation. In both cases the waiter/lease is removed once.

The explained solution uses two separate bounded compartments because a single
semaphore would cap total work but would not prove local/remote isolation. A
single semaphore, immediate fail-fast counter, or no pattern is acceptable
when isolation is not an observed requirement. Bulkhead costs explicit
admission state and cancellation cleanup; remove it when one shared cap is the
actual policy.

### Optional second session — enqueue-only local Pub/Sub

This extension is process-local, in-memory, non-durable, and has no background
consumer, network, replay, acknowledgement, or history. It owns at most four
subscribers and eight queued events per subscriber. `publish()` reports opaque
`enqueued` and `disconnected` IDs—never “delivered” or “processed.”

<!-- bookcheck: path=appendix-software-design-patterns/examples/patterns/pubsub.py check=patterns:network-suite -->
```python source-ref
MAX_SUBSCRIBERS = 4
MAX_QUEUED_PER_SUBSCRIBER = 8
```

**Prediction:** after one subscriber has eight queued events, what happens on
the ninth publish while another subscriber is healthy? **TODO:** disconnect the
slow subscriber, report only its discarded count, and enqueue the ninth event
for healthy subscribers in per-subscriber FIFO order. **Hint:** never expose the
discarded contents. A fifth registration fails with `resource_limit` without
changing existing subscribers; idempotently removing one allows one new
registration.

Happy: the event enters every healthy bounded queue and the result reports each
opaque subscriber ID in `enqueued`. Boundary: the fifth subscriber is rejected.
Recovery: a full subscriber is disconnected with
`slow_subscriber`, eight pending items are discarded count-only, healthy queues
continue, and a removed slot can be reused.

Optional decision record: local fan-out appears → one slow subscriber must not
block healthy queues → bounded Observer/direct calls → enqueue-only Pub/Sub →
per-subscriber queues add capacity and removal state → ninth enqueue or fifth
registration → four/eight/FIFO/disconnect/no-history tests → remove it when
notifications can remain synchronous or only one recipient remains.

Observer calls synchronous listeners now; Pub/Sub enqueues independently for
later processing outside this boundary. Neither one proves remote delivery.

### Capacity checkpoint, rubric, and stop

Required rubric, 0–2 each:

- remote saturation cannot consume local capacity;
- one running + one waiting per compartment and immediate third rejection are
  exact;
- admission timeout/cancellation cleans once and consumes the total deadline;
- admission is local to breaker health, including prior-transient, cancellation,
  and HALF_OPEN cases; pre-result cancellation is neutral and post-transient
  cancellation contributes exactly one negative; and
- the decision defends two Bulkheads or a justified semaphore/fail-fast/direct
  alternative with cost and removal threshold.

Eight of ten completes Capacity. Pub/Sub contributes no required points. If
attempted, separately verify the four/eight limits, slow-subscriber recovery,
FIFO, no content leak, and wording that `enqueued` is not delivered. Reflect:
which resources define a real failure domain in your program? Safe stop: green
required capacity cases with no waiter, lease, or task residue.

## Network crosswalk — read ownership, do not rebuild transport

### Crosswalk objective and worksheet starter

This final session requires both Advanced and Capacity. It adds no socket,
listener, selector loop, framing codec, server, socket Adapter, or restart
Supervisor. Chapter 23 remains the transport authority; Chapter 21 remains the
structured-concurrency authority.

**Prediction:** peer A has a partial response but cannot currently progress;
peer B is ready. Which interest and dispatch let B advance? Is
`selector.select()` the whole Reactor-like design, and does a `TaskGroup`
automatically define restart policy? Write all three answers before reading.
**TODO:** copy this worksheet and fill every row before reading the answer key.
**Hint:** begin with “who creates or registers this thing?” and end with “who
waits for or closes it?”; label interpretation separately from tested behavior.

<!-- bookcheck: table-alternative -->
| Existing event/line | owner | permission/interest | success path | boundary/failure | cleanup | evidence mode |
|---|---|---|---|---|---|---|
| selector registration | TODO | TODO | TODO | TODO | TODO | TODO |
| readiness selection | TODO | TODO | TODO | TODO | TODO | TODO |
| READ/WRITE interest | TODO | TODO | TODO | TODO | TODO | TODO |
| event dispatch | TODO | TODO | TODO | TODO | TODO | TODO |
| idle expiry | TODO | TODO | TODO | TODO | TODO | TODO |
| idempotent close | TODO | TODO | TODO | TODO | TODO | TODO |
| `TaskGroup` owner | TODO | TODO | TODO | TODO | TODO | TODO |
| sibling cancellation | TODO | TODO | TODO | TODO | TODO | TODO |
| caller cancellation | TODO | TODO | TODO | TODO | TODO | TODO |
| `ExceptionGroup` | TODO | TODO | TODO | TODO | TODO | TODO |
| timeout | TODO | TODO | TODO | TODO | TODO | TODO |
| propagation | TODO | TODO | TODO | TODO | TODO | TODO |
| cleanup | TODO | TODO | TODO | TODO | TODO | TODO |

List alternative: make thirteen records—registration, readiness selection,
READ/WRITE interest, dispatch, idle expiry, idempotent close, task-group owner,
sibling cancellation, caller cancellation, `ExceptionGroup`, timeout,
propagation, and cleanup. For each record write seven labels in order: event,
owner, permission/interest, success, boundary/failure, cleanup, and evidence
mode.

### Chapter 23 Reactor-like reading

Read
[`selector_hub.py`](../chapter-23-network-programming/examples/telemetry/selector_hub.py)
with [section 7](../chapter-23-network-programming/README.md#7-several-clients-with-selectors).
Trace registration, `select()` readiness, READ/WRITE interest, dispatch, idle
expiry, and idempotent close. The selector is the readiness demultiplexer, not
the entire responsibility map. “Reactor-like” is an interpretation of these
roles; Chapter 23 does not claim to implement a named Reactor pattern.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
    def serve(self) -> None:
        self.running = True
        try:
            while self.running:
                self._expire_idle_peers()
                for key, mask in self.selector.select(self.timeout):
                    if key.fileobj is self.listener:
                        self._accept()
                    elif mask & selectors.EVENT_READ:
                        self._read(key.fileobj, key.data)
                    else:
                        self._write(key.fileobj, key.data)
        finally:
            self.close()
```

### Chapter 21 `TaskGroup` reading

Read
[`structured_async.py`](../chapter-21-async/structured_async.py) and
[Chapter 21's owned-concurrency section](../chapter-21-async/README.md#2-own-concurrent-tasks-with-taskgroup).
Trace the owner, sibling cancellation, caller cancellation, `ExceptionGroup`,
timeout, propagation, and cleanup. Chapter 21 has generic/manual companion
evidence; do not invent a patterns or Chapter 21 check ID.

```python illustrative
async with asyncio.TaskGroup() as group:
    first = group.create_task(worker("first", 0))
    second = group.create_task(worker("second", 0))
```

“Supervisor-like ownership” is only a comparison. A real Supervisor would add
explicit restart, isolation, or escalation policy, none of which is implemented
here.

### Answer key and caller-cancellation trace

<!-- bookcheck: table-alternative -->
| Existing event/line | owner | permission/interest | success path | boundary/failure | cleanup | evidence mode |
|---|---|---|---|---|---|---|
| selector registration | hub | socket plus registered event mask | registered peer can later appear as ready | invalid/over-cap peer is not retained | unregister then close the peer | Chapter 23 `network:network-suite` |
| readiness selection | event loop/OS queried by hub | `self.selector.select(self.timeout)` | returns only ready registered keys | no ready key before selector timeout | loop continues and idle policy still runs | Chapter 23 plugin evidence plus Reactor-like interpretation |
| READ/WRITE interest | hub-owned peer state | current `EVENT_READ` or `EVENT_WRITE` mask | only the eligible next operation is considered | protocol/output state cannot progress | modify interest or close the peer | Chapter 23 plugin evidence |
| event dispatch | hub's `serve()` loop | listener identity, then READ mask, otherwise WRITE | `_accept`, `_read`, or `_write` advances bounded work | handler detects capacity/protocol/I/O failure | handler or final owner closes | Chapter 23 plugin evidence plus responsibility interpretation |
| idle expiry | hub's idle policy and clock | elapsed no-progress bound | progress refreshes peer activity | idle bound expires | `_close_peer` unregisters and closes once | Chapter 23 plugin evidence |
| idempotent close | hub | explicit stop, peer failure, idle expiry, or `finally` | every owned peer/listener/selector is released | repeated unregister may raise `KeyError`/`ValueError` | expected repeat is tolerated; resources remain closed | Chapter 23 plugin evidence |
| `TaskGroup` owner | enclosing coroutine and group context | children created with `group.create_task` inside the context | context exits only after all children finish | body or child fails | group awaits every owned child before exit | Chapter 21 generic/manual companion evidence |
| sibling cancellation | `TaskGroup` | first non-cancellation child failure | no sibling is abandoned | unfinished siblings receive cancellation | their `finally` blocks run and the group waits | Chapter 21 companion evidence and standard-library contract |
| caller cancellation | caller and enclosing coroutine | cancellation reaches the owner's current await | caller resumes only after owned cleanup | `CancelledError` remains visible | children/resources finish cleanup before propagation | Chapter 21 reading/manual evidence |
| `ExceptionGroup` | `TaskGroup` exit boundary | one or more non-cancellation child failures | no grouped error on full success | failures are grouped after sibling cleanup | expected leaves may be handled with `except*`; unexpected leaves propagate | Chapter 21 generic/manual evidence and standard-library contract |
| timeout | enclosing `asyncio.timeout` context | injected/documented deadline expires | group completes before deadline | owner is cancelled internally and observes `TimeoutError` outside | task group waits for child cleanup first | Chapter 21 generic/manual companion evidence |
| propagation | enclosing coroutine/caller boundary | result, ordinary failure, or cancellation leaves the owner | result returns unchanged | swallowed error/cancellation would hide ownership outcome | handle only declared leaves, otherwise re-raise | Chapter 21 reading/manual interpretation |
| cleanup | each child `finally` plus enclosing group | child was created inside the owned scope | cleanup marker/resource release completes | success, sibling failure, timeout, or caller cancellation | owner does not return until owned cleanup finishes | Chapter 21 generic/manual companion evidence |

List alternative: Chapter 23's hub owns registration, asks for readiness,
interprets READ/WRITE interest, dispatches bounded handlers, expires idle peers,
and closes resources idempotently; those rows retain Chapter 23 plugin ownership
and label “Reactor-like” only as interpretation. Chapter 21's enclosing
coroutine and `TaskGroup` own child creation, sibling cancellation, grouped
failure, timeout, propagation, and cleanup. Caller cancellation remains visible
after cleanup. Success/failure/timeout have generic/manual companion evidence;
caller propagation and Supervisor comparison remain reading interpretations.

Caller-cancellation trace in words: the caller cancels the owning coroutine;
the current await receives cancellation; the owner asks children to cancel;
each child executes `finally`; the owner waits for cleanup; then cancellation
continues to the caller. Catching and discarding it inside a worker would break
the ownership claim.

### Synthesis decision and reading cases

Design question: a small local service has a handful of independent stream
connections. Would you add a custom readiness dispatcher and Supervisor?

The simpler accepted decision is `asyncio` streams owned by one `TaskGroup`:
the library owns readiness mechanics; the group owns task lifetime; the
application owns bounded inputs, timeout, errors, and cleanup. Cost: one task
per connection and cooperative-I/O discipline. Expected failure: a blocking
call stalls the event loop or an unowned task outlives its request. Verify
bounded concurrency, sibling/caller cancellation, and zero leftover tasks.
Remove the abstraction if sequential handling is sufficient. Choose a custom
selector design only when measured constraints and explicit responsibility
tests justify that complexity.

- **Normal reading case:** one peer becomes readable, dispatch advances it, and
  interest is updated.
- **Boundary reading case:** output is partial; WRITE interest remains until the
  bounded response completes. This is Chapter 23 flow control, not a Bulkhead.
- **Recovery reading case:** idle/error/cancellation closes exactly once while
  another peer or sibling proceeds according to its owner.

Longitudinal synthesis: Strategy decides behavior; Factory decides construction;
Adapter translates; Decorator observes one call; Observer notifies local
listeners; composition owns collaborators; Retry owns another safe attempt;
Circuit Breaker owns dependency-health permission; Bulkhead owns admission;
existing event loops and task groups own readiness and concurrent lifetime.
These responsibilities compose only when each seam is observable and tested.

### Final rubric and reflection

Rubric, 0–2 each:

- worksheet traces all six Chapter 23 readiness/cleanup responsibilities and
  all seven Chapter 21 ownership/failure responsibilities;
- evidence labels distinguish Chapter 23 plugin evidence, Chapter 21
  generic/manual evidence, and reading-only interpretation;
- caller cancellation remains visible after owned cleanup;
- streams + `TaskGroup` decision uses the complete decision record and no new
  network implementation; and
- synthesis selects the smallest pattern set for a new pressure and names what
  would be removed.

Eight of ten completes the crosswalk. Reflect: identify one boundary in your
own program where direct code is still the best design, and one measured change
that would justify a pattern. Final safe stop: all selected route tests pass,
no owned task/waiter/lease remains, and every decision has a removal condition.

## Verification, provenance, and review status

- [SOURCES.md](SOURCES.md) records terminology influences and the original-work
  boundary. No third-party prose, exercise, diagram, or code should be adapted
  without a recorded source and license decision.
- [TRACEABILITY.md](TRACEABILITY.md) maps objectives, routes, exercises, cases,
  checkpoints, source owners, and planned check IDs.
- [VERIFICATION.md](VERIFICATION.md) records what has and has not been executed.

The canonical lesson still requires a real target-profile cold read and human
pedagogical, accessibility, provenance/license, and publication review. Those
decisions cannot be inferred from automated checks and must not contain learner
names or other personal data.
