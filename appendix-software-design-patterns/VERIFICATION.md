# Appendix C verification record

## Current state

Evidence cut: **2026-07-16**.

The canonical lesson and this evidence scaffold are a pre-freeze draft. Core
companions, 21 core tests, corrected 47 network tests, the minimal plugin, and
seven plugin fixtures are present. Core and network each pass on CPython
3.11.14, 3.12.12, 3.13.11, and 3.14.2; the complete appendix suite is 68/68.
Independent adversarial review passes 25/25 Resilience-only tests while
Capacity/Pub/Sub imports are blocked and reports no CRITICAL/WARNING finding.
The earlier 36-test semantic failure and in-progress correction failure remain
in the outcome log rather than being erased. Localized pages, shared
source-reference registration, and the `patterns-domain` profile have not yet
been verified as present together. Therefore no configured source-reference
acceptance, translation, cold-read, provenance, accessibility, or publication
result is recorded as a pass here. Machine network correctness does not infer
configured Markdown acceptance or any human decision.

Status words have strict meanings:

- **planned:** the path/check/command is part of the approved contract but its
  prerequisites are not all present;
- **not run:** prerequisites may exist, but this record has no captured run;
- **pass/fail:** command, runtime, bounded outcome, and final files are recorded;
- **human pending:** automation cannot supply the required judgment.

## Execution contract

| Item | Contract |
|---|---|
| supported runtime | CPython 3.11+; actual tested patch versions must be recorded, never inferred |
| dependencies | Python standard library only for required and optional companions |
| network | no socket or public/private remote target; fake dependency only |
| data | synthetic jobs and opaque IDs; no credentials or personal data |
| deterministic time | injected monotonic clock and delay; no wall-clock sleep as correctness evidence |
| Retry bounds | 500 ms total, max 3 attempts, max 100 ms each, full-fit 50/100 ms backoffs |
| breaker bounds | 3 negatives to OPEN, 1 s injected cooldown, one exclusive 100 ms HALF_OPEN attempt without Retry |
| capacity bounds | exactly two compartments; each 1 execution + 1 waiting slot; admission ≤ min(50 ms, remaining total) |
| optional Pub/Sub bounds | max 4 subscribers and 8 queued event IDs each; no worker, broker, replay, acknowledgement, or delivery claim |
| generic runner containment | 30 s and 64 KiB captured output per check |
| outer profile containment | 120 s and 512 KiB for the planned `patterns-domain` selection |
| cleanup | no owned task, attempt, waiter, lease, subscriber-history buffer, temp artifact, or bytecode residue after a case |

Observed host time is never reported as a benchmark or portability guarantee.
A containment timeout is a failure, not evidence that a shorter semantic
deadline worked.

## Planned machine commands

Run from the repository root. The core, network, and plugin commands have
captured local outcomes below.

```text illustrative
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/examples/tests \
  -p 'test_core_patterns.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/examples/tests \
  -p 'test_network_patterns.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/examples/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover \
  -s appendix-software-design-patterns/tools \
  -p 'test_bookcheck_plugin.py' -v
python3 -B tools/validate_book.py \
  --plugin appendix-software-design-patterns/tools/bookcheck_plugin.py
openspec validate add-software-design-patterns-appendix --strict
openspec doctor
git diff --check
```

The final repository-wide wave must also run the then-current named quality and
parity profiles from repository documentation. This appendix does not freeze a
stale list while other active changes own those shared surfaces.

## Route evidence matrix

| Route/check | Required evidence | Status at this cut | Closure condition |
|---|---|---|---|
| Essential | direct equivalence; Strategy selection; Factory validation; Adapter data/method/error translation; recovery/no residue | machine pass; human/source-reference acceptance pending | 21-test core suite passes; configured owner must accept excerpts and pedagogy remains reviewable |
| Professional | Decorator result/failure/order; Observer cap/stable iteration/failure/removal/no history; transfer fixture | machine pass; human review pending | core suite passes; cards/solution still require pedagogical review |
| Advanced | explicit root; fixed clock/IDs/output; one port/in-memory Adapter; fresh-root recovery | machine pass; human review pending | core suite passes without global patch/framework/database/Repository duplicate; rubric review remains pending |
| Network resilience | safety/dedup enforcement; exact calls/delays/deadline; timeout cancel/await; cause; breaker observations/open/probe/cancellation; no Capacity import | machine pass across four CPython lines; independent review pass | 25/25 Resilience-only tests pass with Capacity/Pub/Sub imports blocked; shared source/human review remains pending |
| Capacity | local/remote isolation; exact admission cap; overload/timeout/promotion/cancel; prior transient; OPEN and HALF_OPEN ordering | machine pass across four CPython lines; independent review pass | corrected combined network suite proves hard maxima, ordering, 20 ms integration, probes, cancellation, and no residue; shared source/human review remains pending |
| optional Pub/Sub | four/eight bounds; opaque enqueue/disconnect IDs; slow isolation; count-only discard; FIFO; slot recovery; no background work | optional machine pass across four CPython lines; independent review pass | optional cases prove hard maxima and enqueue-only recovery; skipping remains allowed and human/source review remains pending |
| Network crosswalk | exact Chapter 23 source trace and Chapter 21 ownership trace; normal/boundary/recovery worksheet; simpler design record | not run | anchors resolve; evidence modes are accurate; competent manual review confirms no duplicate transport/Supervisor claim |

## Source-reference acceptance matrix

| Owner | Paths | Check/evidence | Status |
|---|---|---|---|
| Appendix C core | `direct.py`, `essential.py`, `professional.py`, `architecture.py` | `patterns:core-suite` | files/plugin/suite pass; shared known-check ownership and excerpt acceptance remain pending |
| Appendix C network | `resilience.py`, `capacity.py`, `pubsub.py` | `patterns:network-suite` | corrected files/plugin/47-test suite pass on four CPython lines and independent adversarial review; shared known-check ownership and excerpt acceptance remain pending |
| Chapter 23 | `examples/telemetry/selector_hub.py` | existing `network:network-suite` | source exists; Appendix C-specific reference and current selected result not yet recorded here |
| Chapter 21 | `structured_async.py` and its tests | generic/manual companion evidence | source exists; no named Appendix C or Chapter 21 plugin check is claimed |

If a `source-ref` excerpt and its companion disagree, fix the lesson or source
according to the approved behavior; never weaken validation or relabel an
illustrative fragment as executed.

## Required failure and recovery evidence

The final captured test report must make these failure paths visible, not only
count tests:

- invalid job and unknown selection make no collaborator call;
- legacy failure is explicitly translated and chained, then a later call works;
- wrapped failure propagates while measurement remains observable;
- Observer cap, mutation during stable notification, observer failure policy,
  idempotent removal, and zero history;
- key without enforced deduplication and permanent/unsafe calls do not retry;
- insufficient full backoff makes no partial delay or late call;
- attempt timeout cancels and awaits owned work; caller cancellation propagates;
- cancellation before any dependency result is neutral, while cancellation
  during backoff/admission after a transient propagates and contributes exactly
  one negative from that transient;
- raw and exhausted transient health observations open after exactly three
  negatives; positive resets; neutral is ignored;
- only one HALF_OPEN probe runs; cancellation releases it without a new cooldown;
- remote saturation leaves local capacity available; admission timeout,
  overload, and cancellation leave no waiter/lease;
- admission after a prior transient preserves the transient cause without a
  second health observation;
- validation runs before breaker permission even when OPEN, while a Bulkhead
  lease/admission runs before the per-attempt timeout task; the integrated
  20 ms remaining-budget case makes zero dependency calls, stays neutral, and
  leaves no residue; and
- optional slow subscriber disconnects count-only while healthy queues continue.

The first four core bullets above are covered by the green 21-test core suite.
The corrected 47-test network suite covers the remaining bullets on all four
recorded CPython lines; independent adversarial and Resilience-isolation runs
confirm the exact semantics. Neither machine result closes shared or human
gates.

## Baseline and overlapping ownership

The implementation baseline captured for OpenSpec task 1.2 is:

| Surface | Observed state on 2026-07-16 | Ownership boundary |
|---|---|---|
| host runtime | CPython 3.13.11 | an observed host fact, not the entire support matrix |
| Appendix C discovery | unit 33 is visible; canonical, core, network, and plugin files exist; four locale siblings were not yet complete at the cut | Appendix C may change local files; publication waits for all required siblings |
| core evidence | 21/21 passes on CPython 3.11.14, 3.12.12, 3.13.11, and 3.14.2; real `patterns:core-suite` callback passes on 3.13.11; plugin fixtures 7/7 pass | Appendix C core/plugin implementation |
| network evidence | initial 36/36 pass was rejected by semantic review; corrected 47/47 plus real `patterns:network-suite` pass on CPython 3.11.14, 3.12.12, 3.13.11, and 3.14.2; independent 25/25 isolated Resilience and adversarial review have no CRITICAL/WARNING | Appendix C network machine contract closed; shared/human gates remain |
| current parity topology | manifest expects 32 canonical units while discovery finds 33 (`expected 32 canonical units, found 33`) | do not baseline or waive the pending additive 32/128→33/132 publication transition |
| current named profiles | `core`, `learning-bridges`, `environment-domain`, `network-domain`, `cpp-domain`, `rust-domain`, `all-automated`, and `handoff`; `patterns-domain` is absent/planned | preserve every existing binding/order; add `patterns-domain` only after the shared ownership gate |
| current quality run | core/network behavior is green; book/parity remains non-pass because discovery sees unit 33 before its four locale leaves and manifests are published | do not treat the topology failure as an Appendix C behavior failure or waive it |
| active changes | `add-software-design-patterns-appendix`, `add-python-environment-toolchains`, `add-core-python-bridges-and-capstone`, `restore-multilingual-content-parity`, and `add-book-quality-gates` | refresh status before any shared edit |
| shared root/curriculum, parity, quality, attribution/sign-off | overlapping active owners; no shared edit is part of this canonical-local wave | ownership/reconciliation gate remains mandatory before shared tasks |

List equivalent: the host is 3.13.11; core is green on four supported CPython
lines and its real callback is green on the host; plugin fixtures are green.
Network is green on all four recorded CPython lines and its independent
semantic review is clean; this still infers no source-reference or human
approval. Parity says
`expected 32 canonical units, found 33`: the manifest still has 32 while
discovery sees Appendix C as unit 33. The eight current profiles are `core`,
`learning-bridges`, `environment-domain`, `network-domain`, `cpp-domain`,
`rust-domain`, `all-automated`, and `handoff`; `patterns-domain` remains absent
and planned. Five active changes overlap shared publication surfaces, so this
local evidence must not authorize a shared edit, 33/132 transition, profile
addition, or baseline waiver.

## Manual and human review gates

| Gate | Required record | Current state |
|---|---|---|
| canonical cold read | role-only target-profile participants collectively cover Essential, Professional, Advanced, Resilience, Capacity, and Crosswalk within upper estimates using documented help; findings are corrected and retested | human pending; deliberately not performed or inferred by this draft |
| pedagogical/technical review | objective progression, cognitive load, decisions, network semantics, solutions, rubrics, and recovery points against final digest | human pending |
| accessibility | rendered headings, tables plus text/list alternatives, link descriptions, non-color instructions, keyboard/screen-reader checks | human pending |
| localization | natural Spanish/Catalan/Swedish/Arabic and semantic parity for all objectives, cases, hints, solutions, rubrics, bounds, and non-claims | human pending |
| Arabic bidi | one balanced outer RTL wrapper and readable LTR code/commands/paths/identifiers in rendered output | human pending |
| provenance/license | original-work declaration, external source use, permission/license obligations, notices, and final digests | human pending |
| publication | all prior current decisions plus root/navigation/parity/profile inputs | human pending |

Cold-read notes must record roles, prerequisites, environment, route coverage,
documented versus unplanned help, time, finding, correction, and retest. Do not
record participant names, contact details, account identifiers, or other
personal data. Any route that exceeds its upper estimate or requires unplanned
help must be corrected and re-piloted; it cannot be waived by automation.

### Blank cold-read record template

Copy one blank record per observed session. Do not populate it with names,
contact details, account IDs, free-form biographical details, or any other
personal data. A role such as “target-profile learner” or “independent
facilitator” is sufficient.

- Record ID:
- Role only (no name/PII):
- Proven prerequisite checkpoint(s):
- Environment and exact runtime/tool version:
- Route and checkpoint(s) observed:
- Documented help used (lesson section/hint/recovery link):
- Unplanned external help required (yes/no; describe only the blocked step):
- Elapsed minutes:
- Finding (including jargon, blocked step, or recovery failure):
- Correction made to the lesson/companion:
- Retest date, scope, minutes, help used, and outcome:

The collected records, not one individual, must cover all six required
checkpoints: Essential, Professional, Advanced, Network resilience, Capacity,
and Network crosswalk. This canonical cold read is the human gate that blocks
translation; the later specialist gates still block final publication. Every
row remains pending until a real session exists.
Any “yes” for unplanned help or duration above the route's published upper
estimate is a critical finding: correct the material and retest that checkpoint
before translation. Automation must never fill this template, change pending
coverage, or infer acceptance.

## Outcome log

| Date/runtime | Command or review | Outcome | Evidence/notes |
|---|---|---|---|
| 2026-07-16 / CPython 3.11.14, 3.12.12, 3.13.11, 3.14.2 | focused `test_core_patterns.py` matrix | pass: 21/21 on every runtime | standard-library core behavior only; no configured source-reference or human acceptance inferred |
| 2026-07-16 / CPython 3.13.11 | real `patterns:core-suite` callback | pass | minimal plugin selected and completed the core suite; generic containment remains the runner's owner |
| 2026-07-16 / CPython 3.13.11 | `test_bookcheck_plugin.py` | pass: 7/7 | registration, independent selection, one bounded failure, missing suite, symlink rejection, and sanitized OS-error fixtures |
| 2026-07-16 / CPython 3.13.11 | local focused rerun of core + plugin fixtures | pass: 21/21 + 7/7 | `PYTHONDONTWRITEBYTECODE=1`, `-B`; no network suite claimed |
| 2026-07-16 / CPython 3.13.11 | focused `test_network_patterns.py` | pass: 36/36 | fake-time Retry/breaker/Bulkhead/Pub/Sub, published bounds, cleanup/recovery edges, and source boundaries; no other-runtime result inferred |
| 2026-07-16 / CPython 3.13.11 | real `patterns:network-suite` callback | pass | minimal plugin selected and completed the network suite; configured Markdown source-reference acceptance remains separate |
| 2026-07-16 / independent technical review | network contract trace | fail | hard maxima remained configurable; attempt-timeout semantics, validation→breaker and admission→attempt-timeout order, and required probe cases were incomplete; correction and retest required |
| 2026-07-16 / CPython 3.13.11 | focused network suite during semantic correction | fail: 2 of 37 | full-fit and exact-fit backoff cases expected the prior transient cause but observed `attempt_timeout`; this was an in-progress tree and requires a stable recovery retest |
| 2026-07-16 / CPython 3.11.14, 3.12.12, 3.13.11, 3.14.2 | corrected `test_network_patterns.py` matrix | pass: 47/47 on every runtime | proves hard maxima, overtime attempt mapping, validation-before-permission including OPEN, lease-before-attempt-timeout, exact 20 ms admission, pre/post-transient cancellation health, all probe outcomes, cleanup, and optional Pub/Sub boundaries |
| 2026-07-16 / independent technical review | frozen network adversarial and isolated Resilience rerun | pass: 47/47 combined; 25/25 isolated; no CRITICAL/WARNING | Capacity/Pub/Sub imports were blocked for the isolated route; correction closes every earlier semantic finding without erasing it |
| 2026-07-16 / CPython 3.13.11 | complete appendix companions and real plugin checks | pass: 68/68; core + network callbacks pass | 21 core plus 47 network tests; generic plugin selects each known suite independently; configured Markdown acceptance remains separate |
| 2026-07-16 / CPython 3.13.11 | targeted canonical Markdown/source scan | local draft pass; publication incomplete | one H1, heading/fence/table accessibility, existing local anchors, and all eight `source-ref` excerpts are structurally/literally valid; four locale sibling targets remain intentionally missing for the translation task |
| 2026-07-16 / OpenSpec CLI | strict change validation, doctor, and appendix-scoped `git diff --check` | pass | planning artifacts are valid and repository root is healthy; this does not close implementation or human gates |
| 2026-07-16 / not applicable | evidence scaffold creation and update | partial machine pass; human gates pending | canonical draft, source inventory, traceability, and verification contract updated without inferring cold-read/provenance/accessibility/publication acceptance |

Add rows only after running against the exact files being handed off. Include
the runtime/tool version, bounded exit status, and concise failure diagnostics.
Do not replace a prior failure row; append the correction and retest so the
recovery trail remains visible.
