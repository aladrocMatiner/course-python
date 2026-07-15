# Chapter 28 · Professional Capstone: One Order Tracker, Four Stages

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we are going to build

You will grow one local order tracker instead of starting four unrelated final
projects. The foundation stage combines immutable values, classes, and
functions in memory. The practical stage keeps the same domain while adding
SQLite, a command-line interface (CLI), configuration, logging, and tests. An
optional systems stage exposes the same service through a bounded loopback
adapter. A final optional hero stage verifies a source distribution and wheel
without publishing either.

All examples use fictional identifiers such as `ORD-001` and item labels such
as `widget`. Do not substitute real customer, address, payment, credential, or
production information.

## Learning objectives

By the end of the stages you select, you can:

- model a bounded immutable `Order` and explain every accepted transition;
- separate domain, service, repository, CLI, and optional network
  responsibilities;
- preserve prior state after validation, duplicate, transition, locking, or
  database failures;
- operate a SQLite-backed CLI with explicit configuration, stable output,
  meaningful exit codes, and privacy-safe logs;
- verify normal, boundary, invalid, and recovery behavior at the boundary that
  owns it;
- run an optional loopback lab with explicit byte, request, concurrency, and
  time limits and deterministic shutdown; and
- distinguish source-tree evidence from a built, inspected, clean-installed
  artifact, without uploading it.

## Prerequisites and independently stoppable routes

The catalogue number does not make Chapters 23–27 automatic prerequisites.
Enter only the stage for which you meet the named checkpoint.

### Foundation route

- **Entry:** the [Chapter 12 class checkpoint](../chapter-12-oop/README.md#checkpoint-and-rubric)
  and its [immutable data-class exercise](../chapter-12-oop/README.md#guided-exercises-with-todos),
  plus functions, conditionals, loops, and collections from Chapters 3–11.
- **Time:** 2–3 sessions of 50–75 minutes.
- **Outcome:** a tested in-memory service that creates, lists, and advances
  immutable synthetic orders.
- **Exit:** all five foundation rubric items pass.
- **Safe stop:** keep the in-memory artifact; persistence, networking, and
  packaging are not required.

### Practical route

- **Entry:** the foundation exit plus Chapters
  [13](../chapter-13-files/README.md#checkpoint-and-rubric) through
  [18](../chapter-18-testing/README.md#checkpoint-and-rubric). Complete the
  [CLI appendix checkpoint](../appendix-cli-parser/README.md#checkpoint-and-rubric)
  before implementing the command adapter, and complete the
  [Chapter 20 logging checkpoint](../chapter-20-logging/README.md#checkpoint-and-rubric)
  before the logging-privacy sub-checkpoint; this prevents logging from being
  a hidden first-time concept.
- **Time:** 4–6 sessions of 50–80 minutes.
- **Outcome:** a transactional SQLite CLI with explicit configuration,
  privacy-safe events, subprocess evidence, and recovery.
- **Exit:** the standard-library suite passes and the learner can explain one
  rollback and the CLI precedence rule.
- **Safe stop:** this is a complete practical capstone. The server and package
  build are optional.

### Optional systems route

- **Entry:** the practical exit, the
  [Chapter 21 asyncio checkpoint](../chapter-21-async/README.md#checkpoint-and-rubric),
  and the [Chapter 23 network assessment](../chapter-23-network-programming/README.md#assessment-rubric).
- **Time:** 2–3 sessions of 50–75 minutes.
- **Outcome:** a tested newline-JSON service on `127.0.0.1` and an
  operating-system-assigned port, with capacity recovery and clean shutdown.
- **Exit:** the eight loopback tests pass and every declared limit can be
  explained.
- **Safe stop:** no public exposure, TLS, authentication, or deployment is
  claimed.

### Optional hero packaging route

- **Entry:** the practical exit plus the package/environment lessons in
  [Chapter 15](../chapter-15-modulos/README.md#checkpoint-and-rubric) and
  [Chapter 16](../chapter-16-entornos/README.md#checkpoint-and-rubric).
- **Time:** 2–3 sessions of 50–80 minutes after exact build inputs have been
  deliberately provisioned.
- **Outcome:** local sdist-to-wheel-to-clean-install evidence from a foreign
  working directory.
- **Exit:** every verifier phase passes and the learner can state which host
  was actually tested.
- **Safe stop:** no upload, signing, attestation, token, or package-index
  mutation belongs to this chapter.

## Architecture in words

The CLI and optional loopback adapter translate external input. Both call
`OrderService`. The service creates `Order` values and asks an
`OrderRepository` to store or advance them. `InMemoryOrderRepository` and
`SQLiteOrderRepository` implement the same operations. SQLite is therefore a
replaceable persistence detail, not a second set of business rules.

The control sequence is:

1. an adapter parses and bounds input;
2. the service constructs or requests a domain operation;
3. the immutable order validates the exact domain;
4. the selected repository commits the complete change or preserves the prior
   state;
5. the adapter emits bounded output or a stable error category.

This numbered description is the complete text equivalent of an architecture
diagram; no meaning depends on color, arrows, or screen position.

## Companion and verification working directory

The executable authority is
`chapter-28-professional-capstone/examples/order-tracker/`. Run the complete
standard-library suite from the repository root:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

This command exercises domain, both repositories, service, CLI subprocesses,
logging privacy, loopback lifecycle, metadata, artifact preflight, and archive
inspection fixtures. It uses temporary
directories, fake data, ephemeral ports, bounded child output, and bounded
timeouts.

---

## Stage 1 · Foundation: immutable domain and in-memory service

### Foundation objectives and context

An order tracker sounds simple until a duplicate overwrites an earlier order
or a shipped order moves backward. The foundation stage makes those rules
observable before any database or adapter adds cognitive load.

You will:

- create an immutable order in `pending`;
- advance only `pending → packed → shipped`;
- accept exact inclusive text and quantity boundaries;
- list by `order_id` rather than insertion accident; and
- prove every rejected operation leaves prior state unchanged.

### Predict the lifecycle

Before reading the implementation, predict these observations:

1. What statuses result from two calls to `advance("ORD-001")`?
2. What should a third call do?
3. If a second create uses `ORD-001` with a different item, which order should
   remain?
4. Should `True` be accepted as quantity `1`?

Write the predicted status or exception category, not a full traceback.

### Minimal theory: value, service, and repository

`Order` is a frozen data class, following Chapter 12's immutable data-class
exercise. A transition returns a new snapshot; it does not edit the earlier
value. `OrderService` coordinates the use case. A small inheritance contract
names the five repository operations, and `InMemoryOrderRepository` implements
them with a dictionary returned in sorted identifier order. No structural
typing concept from Chapter 27 is required for this stage.

The stable domain failures are:

- `OrderValidationError` for invalid bounded values;
- `DuplicateOrderError` for an existing identifier;
- `UnknownOrderError` for a missing identifier;
- `InvalidTransitionError` for advancing `shipped`; and
- `RepositoryError` for persistence/lifecycle failures.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/domain.py check=learning:contract -->
```python source-ref
pending = Order("ORD-001", "widget", 2)
packed = pending.advanced()
assert pending.status == "pending"
assert packed.status == "packed"
```

### Domain boundaries

After surrounding whitespace is removed:

- `order_id` length is 1–32 characters;
- `item` length is 1–80 characters;
- `quantity` is an exact built-in `int` from 1 through 1,000;
- `bool` and `int` subclasses are rejected; and
- `status` is exactly `pending`, `packed`, or `shipped`.

The values at 32, 80, 1, and 1,000 are accepted. Empty text, lengths 33/81,
quantities 0/1,001, and either Boolean are rejected before repository state
changes.

### Guided foundation TODO

Work in a disposable copy or a scratch file that imports the companion:

```python todo
repository = InMemoryOrderRepository()
service = OrderService(repository)

# TODO 1: create ORD-001 for two widgets and record its status.
# TODO 2: advance it twice and record both new statuses.
# TODO 3: try one more advance and record the exception category.
# TODO 4: list again and prove ORD-001 is still shipped.
```

**Hint:** compare an immutable snapshot captured before the rejected operation
with `service.get("ORD-001")` afterward. Do not catch `Exception`; name the
domain failure you expect.

### Happy, edge, failure, and recovery evidence

- **Happy:** `pending`, `packed`, and `shipped` appear in that order.
- **Edge:** identifier length 32, item length 80, and quantities 1/1,000 pass.
- **Recoverable failure:** a duplicate raises `DuplicateOrderError` and keeps
  the original item and quantity.
- **Recovery:** retry with a unique identifier; it succeeds without repairing
  repository internals.
- **Terminal failure:** advancing `shipped` raises
  `InvalidTransitionError`; reloading still returns `shipped`.

Run the focused evidence:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_domain tests.test_service -v
```

### Explained foundation solution

The solution constructs `Order` before calling `repository.add`, so invalid
data never reaches storage. `advanced()` uses one explicit next-status map and
returns a new frozen value. The repository assigns that value only after
transition validation succeeds. Duplicate detection happens before dictionary
assignment. These orders make unchanged-state recovery a property of the
design, not a cleanup trick.

### Foundation common mistakes

- Mutating `order.status` directly defeats immutable snapshots and fails.
- Treating `bool` as a quantity accepts a technically integer-like value with
  the wrong domain meaning.
- Catching every exception hides whether validation, lookup, transition, or
  persistence failed.
- Returning dictionary insertion order would make an accidental ordering
  contract; the service requires sorted identifiers.

### Foundation checkpoint and rubric

Score one point for each item:

- **Correctness:** one order reaches all three statuses in order.
- **Boundary:** inclusive text/quantity limits pass and first invalid values
  fail.
- **Recovery:** duplicate and terminal-transition failures preserve snapshots.
- **Separation:** the learner can distinguish value, service, and repository.
- **Explanation:** the learner explains why a new immutable snapshot makes
  rollback reasoning simpler.

Five points complete the foundation stage. At four, repeat only the missing
case; below four, revisit the boundary and state-preservation tests. You may
stop here with a complete tested in-memory artifact.

### Foundation reflection

Which ordering decision—validate, compute, then assign—does the most work to
protect state, and what would break if assignment happened first?

---

## Stage 2 · Practical: SQLite, CLI, configuration, logging, and tests

### Practical objectives and prediction

The practical stage retains the same service and replaces only its repository.
Before running it, predict:

- which database wins when both `ORDER_TRACKER_DB` and `--database` exist;
- whether a missing database setting should create `orders.db` implicitly;
- what remains after a SQLite update aborts before commit; and
- which stream carries stable results versus diagnostics/events.

The answers are: the explicit argument wins; no default file is created; the
previous committed status remains; stdout carries results while stderr carries
diagnostics and optional events.

### SQLite transaction boundary

`SQLiteOrderRepository` creates its schema idempotently and opens short-lived
connections with a default 250 ms busy timeout. Writes begin explicitly,
validate/read, apply one complete mutation, then commit. A database exception
rolls back and maps to `RepositoryError` without exposing SQL, bound item text,
or a full path.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/repositories.py check=learning:contract -->
```python source-ref
repository = SQLiteOrderRepository(database, busy_timeout_ms=250)
service = OrderService(repository)
service.create("ORD-001", "widget", 2)
```

The shared repository tests run the same add/get/list/advance contract against
memory and SQLite. A controlled trigger aborts an update; the test observes
`pending` afterward, removes only its own trigger, and then advances
successfully. Another test holds an explicit temporary lock beyond 50 ms,
observes a bounded failure, releases it, and retries.

### CLI contract

The installed command supports:

```bash illustrative
order-tracker --database path/to/disposable/orders.sqlite3 add ORD-001 widget 2
order-tracker --database path/to/disposable/orders.sqlite3 advance ORD-001
order-tracker --database path/to/disposable/orders.sqlite3 list
```

Stable success output is compact JSON:

```text illustrative
{"order_id":"ORD-001","status":"pending"}
```

Listing one pending order produces:

```text illustrative
{"item":"widget","order_id":"ORD-001","quantity":2,"status":"pending"}
```

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/cli.py check=learning:contract -->
```python source-ref
configured = args.database if args.database is not None else environment.get("ORDER_TRACKER_DB")
```

Exit status is part of the interface:

- `0`: command completed;
- `1`: domain or repository rejected the operation;
- `2`: arguments or database configuration are unusable.

With no configuration, stderr says how to recover and no database is created.
A non-integer CLI quantity is a usage error (2); an integer outside the domain
is a domain error (1). A later valid invocation against the same selected
database succeeds.

### Logging privacy

`--verbose` adds one bounded stderr event. A successful create looks like:

```text illustrative
event=add order_id=ORD-LOG outcome=success
```

Events may contain phase, stable order identifier, count, outcome, and stable
category. They never contain item text, a complete database path, environment
values, SQL with data, secrets, or expected-error traceback details. Stdout
remains unchanged so scripts can parse it.

### Guided practical TODO

Add one subprocess test, not a call to a private CLI helper:

```python todo
# TODO 1: invoke the CLI to create ORD-RECOVER in a temporary database.
# TODO 2: invoke the same add again and assert exit 1 plus duplicate-order.
# TODO 3: invoke list and prove the original item/quantity remain.
# TODO 4: retry with ORD-RECOVER-2 and assert exit 0.
```

**Hint:** assert return code, stdout, stderr, and database state. Bound the
subprocess timeout and captured output. Use only a `TemporaryDirectory` and
synthetic values.

### Practical evidence and explained solution

Run:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest \
  tests.test_repository_contract tests.test_cli tests.test_metadata -v
```

The explained solution invokes `python -m order_tracker` from a foreign
temporary working directory with only the companion `src` directory on the
source-test import path. It does not bypass `argparse`. Duplicate insertion is
rejected by the same domain/repository category the service exposes. A final
`list` proves the original row survived; a new identifier proves recovery.

### Practical common mistakes

- Choosing a hidden default database makes an innocent command mutate the
  working tree.
- Printing a complete database path or item in logs turns diagnostics into a
  data leak.
- Testing `cli.main` alone can miss entry parsing, streams, exit status, and
  foreign-working-directory problems.
- Catching `sqlite3.Error` in the CLI leaks persistence details and duplicates
  repository responsibility.
- Deleting a locked/corrupt database as “recovery” can destroy unrelated data;
  correct the disposable path or release only the lock your test owns.

### Practical checkpoint and rubric

Score one point for each item:

- **Repository contract:** memory and SQLite produce the same observable
  lifecycle/errors.
- **Atomicity:** a controlled failed update preserves the previous row and a
  later clean transaction succeeds.
- **CLI/configuration:** precedence, JSON, stream separation, and 0/1/2 exits
  match the contract.
- **Logging privacy:** events contain the phase/outcome but none of the
  forbidden values.
- **Testing/recovery:** subprocess tests cover normal, boundary, invalid, and
  retry behavior without residue.
- **Explanation:** the learner can explain where commit occurs and why
  `--database` wins.

The practical stage is complete with all six. Optional systems or packaging
work cannot compensate for a zero here. This is a safe professional stopping
point.

### Practical reflection

Why is “same service, different repository” stronger evidence than writing a
second SQLite-specific application from scratch?

---

## Stage 3 · Optional systems extension: bounded loopback adapter

### Systems objective and exact limits

This optional adapter teaches lifecycle, not Internet deployment. It uses
newline-delimited UTF-8 JSON, one request per connection, `127.0.0.1`, and an
operating-system-assigned port.

Default limits are:

- request bytes: 1,024 including the newline;
- response bytes: 4,096 including the newline;
- total accepted requests: 8;
- simultaneous active handlers: 4;
- orders returned by one list response: 20; and
- idle read/write deadline: 0.5 seconds.

Constructor validation allows request sizes from 1 through 65,536 bytes,
response sizes from 38 through 65,536 bytes, request/list counts from 1 through
100, concurrency from 1 through 32, and deadlines from 0.05 through 10
seconds. The 38-byte minimum is the complete `response-limit` error frame, so
even that recovery message respects the selected bound. The adapter retains no
request history or unbounded output queue. A connection admitted past the
concurrency gate consumes one total-request slot even when its frame is later
malformed or times out; a peer rejected as `busy` does not.

### Predict framing and capacity

Predict what happens when a peer:

1. sends valid JSON below 1,024 bytes;
2. sends 1,025 bytes before a newline;
3. opens the only allowed handler and stalls;
4. sends malformed UTF-8/JSON; or
5. asks for a ninth request.

The stable errors are respectively success, `request-too-large`, `busy` for a
concurrent peer followed by capacity recovery, `malformed-request`, and
`request-limit` followed by clean shutdown.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/loopback.py check=learning:contract -->
```python source-ref
async with LoopbackOrderServer(service) as server:
    response = await send_request(server.address, {"action": "list"})
```

One valid request is:

```json illustrative
{"action":"add","order_id":"NET-1","item":"widget","quantity":2}
```

The bounded response is:

```json illustrative
{"ok":true,"order":{"item":"widget","order_id":"NET-1","quantity":2,"status":"pending"}}
```

### Guided systems TODO

Extend the temporary test, not a public service:

```python todo
# TODO 1: start with max_concurrency=1 and an ephemeral port.
# TODO 2: open one client and wait on connection_started without sleeping.
# TODO 3: prove a second client receives busy.
# TODO 4: finish/close the first client, await capacity_available, and retry.
# TODO 5: close the server and assert zero active connections/tasks.
```

**Hint:** readiness and recovery are events. A fixed sleep cannot prove either.
Always close the client writer in `finally`.

### Failure, recovery, cancellation, and solution

The suite covers constructor limits, a request at the exact byte boundary,
valid add/list, malformed input, oversize input, list/response caps, a busy
handler, idle timeout, total-request exhaustion, cancellation of a stalled
handler, capacity return, and listener shutdown. The server closes the
listener, cancels and awaits every owned handler, then completes
`wait_closed()`. `CancelledError` is re-raised after each writer is closed.

Run only the optional evidence:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_loopback -v
```

The explained solution never binds `0.0.0.0`, never chooses a fixed port,
never contacts a public target, never disables a security check, and never
claims TLS, authentication, or production hardening. It applies byte/state
limits before retaining data and proves a later request or a clean shutdown
after rejection.

### Systems common mistakes

- One TCP write is not guaranteed to be one read; the newline is the declared
  frame boundary.
- A fixed sleep is not server-readiness or cleanup evidence.
- Loopback removes public routing, not all application-security concerns.
- Cancelling without awaiting tasks can leave sockets and warnings behind.
- An optional adapter must not become an import-time or packaging prerequisite.

### Systems checkpoint and rubric

Score one point for **loopback/ephemeral binding**, **framing and byte limits**,
**request/concurrency limits**, **timeout/capacity recovery**,
**cancellation/shutdown**, and **explaining why this is not production**.
All six complete the optional systems stage. Otherwise keep the practical
stage result and report systems evidence as incomplete.

### Systems reflection

Which resource is bounded by each number, and which assertion proves that the
capacity returns?

---

## Stage 4 · Optional hero packaging: verify the artifact, not the checkout

### Packaging objective and evidence boundary

Passing source tests proves the checkout. It does not prove that an sdist
contains every source, that a wheel has correct metadata, that installation
works, or that import resolves outside the repository. The hero stage tests
those claims separately.

The distribution is `course-order-tracker`, import package `order_tracker`,
command `order-tracker`, version `1.0.0`, `Requires-Python >=3.11`, and
runtime dependencies none. Its wheel declares `py3-none-any`. That tag is a
compatibility declaration, not proof for hosts that were not executed.

### Build inputs are direct pins, not a lock

`requirements-build.txt` records `build==1.3.0`,
`setuptools==80.9.0`, and `wheel==0.45.1` as exact direct pins for this
workflow. It has no hashes, resolver provenance, cross-platform matrix, or
transitive index snapshot, so it is not called a complete lock.

The companion [build-input record](examples/order-tracker/BUILD_INPUTS.md)
separately records the selected release filenames, observed PyPI SHA-256
values, reported license metadata, and primary format references. The verifier
checks the two offline backend-wheel hashes. This provenance observation is
still not a resolved dependency graph or a human license/publication approval.

Initial tool acquisition is a separate, deliberate maintainer step that may
need an approved network/index. The verifier never performs it. Before running
the accepted command, the host must provide POSIX process groups for bounded
child-tree cleanup, `build==1.3.0` must already be importable, and
`ORDER_TRACKER_WHEELHOUSE` must name a dedicated offline directory containing
only the exact recorded setuptools and wheel artifacts. Missing, additional,
or mismatched input is a non-pass prerequisite state.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py check=learning:contract -->
```python source-ref
wheelhouse = require_prerequisites()
verify(wheelhouse)
```

From the repository root, the accepted command is:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

On this checkout, if tools are not provisioned, the truthful result is
nonzero and begins:

```text illustrative
prerequisite missing:
```

That is not an artifact pass and does not invalidate the already completed
practical source stage.

### Verification phases

The verifier:

1. fingerprints and scans the source tree;
2. copies it to an independent temporary source root;
3. runs isolated PEP 517 builds offline from the declared wheelhouse;
4. inspects the exact sdist and initial pure wheel;
5. safely unpacks the sdist into a second source root;
6. rebuilds a wheel from that distributed source;
7. checks metadata, required members, `RECORD`, license, no runtime
   dependencies, and `py3-none-any`;
8. installs the exact rebuilt wheel with `--no-index --no-deps` into a fresh
   environment;
9. runs `pip check`, metadata/import/domain/CLI smoke from a foreign directory;
10. reports filenames and SHA-256 observations plus executed versions; and
11. removes all temporary source, output, install, cache, database, and foreign
    roots on success or failure.

It rejects an individual source/archive member over 2 MiB, a project snapshot
over 8 MiB, an archive over 12 MiB compressed or expanded, combined child
output over 16 KiB, an initial/rebuild/install phase over 180 seconds, or any
other child phase over 30 seconds. A non-POSIX host reports a prerequisite
state; this course does not substitute a weaker process-cleanup claim.

SHA-256 proves which bytes were observed in that run. It is not a
byte-for-byte reproducible-build claim.

### Guided packaging TODO

Before execution, fill this evidence plan:

```text todo
TODO 1: name the source input and the two independently built wheels.
TODO 2: predict where order_tracker.__file__ must resolve after clean install.
TODO 3: name the phase that should reject a database or .env inside an archive.
TODO 4: record the exact interpreter/host actually executed.
TODO 5: state why no command in the plan uploads an artifact.
```

**Hint:** “the tests passed” is not enough. Record build, inspect, rebuild,
install, import, behavior, CLI, and cleanup separately. A missing prerequisite
remains missing.

### Packaging failure and recovery

- Missing frontend/wheelhouse: provision the exact inputs explicitly; do not
  disable isolation or allow an implicit index fallback.
- Missing sdist member: correct `MANIFEST.in`/metadata, discard every temporary
  artifact, and rebuild from the beginning.
- Source-tree import leak: change to the fresh interpreter/foreign working
  directory; do not add the checkout to `PYTHONPATH`.
- Forbidden database/cache/credential: remove the source cause and repeat
  inspection before installation.
- CLI smoke failure: correct the package/entry point and rerun all downstream
  phases, not only the final command.

Verification stops locally. Publication requires separate authorization,
credentials, review, signing/attestation policy, and index controls that this
chapter neither requests nor exercises.

### Packaging common mistakes

- Calling direct pins a universal lock overstates their evidence.
- Treating a wheel filename as execution proof overstates compatibility.
- Installing from the checkout lets a missing package file hide.
- Reusing an old build/cache invalidates clean-build evidence.
- Reporting a missing build tool as “skipped/pass” fabricates success.
- Adding an upload command expands authority beyond this capstone.

### Packaging checkpoint and rubric

If selected, score one point for **isolated build**, **sdist inspection**,
**wheel rebuilt from sdist**, **clean install and `pip check`**,
**foreign-directory metadata/import/domain/CLI evidence**, **digest/toolchain
record**, **cleanup**, and **explaining no publication**. All eight complete
the hero stage. If any is unavailable, report the exact non-pass phase and
retain the independently completed practical stage.

### Packaging reflection

Which defect can source tests hide but a wheel rebuilt from the sdist expose?

---

## Final selected-stage assessment

For every selected stage, no required category may score zero:

- **Domain correctness:** values and transitions match the exact contract.
- **Separation of concerns:** adapters do not own domain/SQLite rules.
- **Persistence atomicity:** rejection preserves committed state.
- **CLI/configuration:** precedence, JSON, streams, and exit codes are stable.
- **Logging privacy:** diagnostics disclose no item, path, environment, SQL
  data, credential, or expected-error traceback.
- **Testing and recovery:** normal, boundary, invalid, and repaired behavior
  are observable.
- **Systems lifecycle, if selected:** bounds, cancellation, and cleanup pass.
- **Artifact evidence, if selected:** source-to-installed phases pass locally.
- **Explanation:** the learner can justify one design decision and one
  recovery boundary.

Optional points cannot hide a foundation or practical failure. A passing tool
without an explanation leaves that rubric category incomplete.

## Complete traceability and verification

[Chapter 28 traceability](TRACEABILITY.md) maps every feature to prior teaching,
the learner-facing section, companion source, exact test, and rubric item. The
companion [verification guide](examples/order-tracker/README.md) records the
commands and artifact prerequisite boundary.

## Repository hygiene check

After verification, inspect even ignored paths under the chapter. There must
be no virtual environment, `build/`, `dist/`, wheel, sdist, SQLite database,
`*.egg-info`, cache, bytecode, coverage, credential, learner data, live socket,
or child process. All generated state belongs in temporary roots.

## Sources, originality, and human review boundary

The chapter prose, fictional order scenarios, TODOs, tests, and companion code
were written as original course material. Technical behavior was checked
against the official Python documentation for
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html),
[`argparse`](https://docs.python.org/3/library/argparse.html), and
[`asyncio` streams](https://docs.python.org/3/library/asyncio-stream.html), plus
the primary packaging references listed in the companion build-input record.
No prose or exercise is presented as copied from those references.

That declaration and automated structure/tests do not approve provenance,
license obligations, translation quality, rendered accessibility, Arabic bidi,
or publication. Those remain explicit competent-human gates.

## Closing reflection

The capstone is complete at the stage you selected when behavior, recovery,
cleanup, and your explanation agree. Which boundary—immutable domain,
transaction, adapter, or artifact—gave you the strongest new evidence, and
what would you verify next before a real release?
