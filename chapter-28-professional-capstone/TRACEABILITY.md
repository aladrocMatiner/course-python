# Chapter 28 implementation traceability

This maintainer-facing map binds each required capstone feature to prior
teaching, learner-facing instruction, implementation, and observable evidence.
It does not replace the lesson or grant publication approval.

## Foundation stage

| Feature | Prior checkpoint | Teaching anchor | Companion authority | Observable evidence | Manual assessment |
| --- | --- | --- | --- | --- | --- |
| Immutable `Order` | Chapter 12 class checkpoint and immutable data-class exercise | `stage-1--foundation-immutable-domain-and-in-memory-service` | `src/order_tracker/domain.py` | `tests.test_domain` | Foundation correctness/explanation |
| Exact ID/item/quantity/status bounds | Chapters 2, 8, 14 | `domain-boundaries` | `domain.py` | `OrderTests.test_accepts_inclusive_boundaries` and first-invalid tests | Foundation boundary |
| `pending → packed → shipped` | Chapters 8, 11, 12 | `predict-the-lifecycle` | `Order.advanced` | domain/service lifecycle tests | Foundation correctness |
| In-memory create/get/list/advance | Chapters 4, 11, 12 inheritance/composition | `minimal-theory-value-service-and-repository` | `repositories.py` and `service.py` | in-memory repository contract | Foundation separation |
| Duplicate/unknown/terminal recovery | Chapter 14 | `happy-edge-failure-and-recovery-evidence` | stable `OrderError` subclasses | service and repository preservation tests | Foundation recovery |
| Deterministic close | Chapters 12, 14 | `explained-foundation-solution` | `OrderService.close` | `test_close_is_idempotent_and_rejects_later_work` | Foundation explanation |

## Practical stage

| Feature | Prior checkpoint | Teaching anchor | Companion authority | Observable evidence | Manual assessment |
| --- | --- | --- | --- | --- | --- |
| SQLite and idempotent schema | Chapters 13, 15, 17 | `sqlite-transaction-boundary` | `SQLiteOrderRepository` | `test_schema_creation_is_idempotent` | Repository contract |
| Shared repository behavior | Chapters 11, 12, 18 | `sqlite-transaction-boundary` | `OrderRepository` | both repository contract classes | Repository contract/separation |
| Bounded busy timeout | Chapters 14, 17 | `sqlite-transaction-boundary` | `DEFAULT_BUSY_TIMEOUT_MS` | lock-timeout recovery test | Atomicity |
| Transaction rollback | Chapters 14, 17, 18 | `practical-evidence-and-explained-solution` | `SQLiteOrderRepository.add/advance` | insert/update trigger abort and lock recovery tests | Atomicity/explanation |
| CLI add/advance/list | Chapters 9, 15 and CLI appendix checkpoint | `cli-contract` | `cli.py` | real subprocess success tests | CLI correctness |
| `--database` over environment | Chapters 9, 16 | `practical-objectives-and-prediction` | `cli.main` | explicit-over-environment test | Configuration explanation |
| No implicit database | Chapters 13, 14 | `cli-contract` | `cli.main` | missing-configuration residue test | Recovery |
| Exit 0/1/2 and stream separation | Chapters 9, 14, 18 | `cli-contract` | `cli.py` | CLI success/usage/domain tests | CLI/configuration |
| Privacy-safe logging | Chapter 20 | `logging-privacy` | `cli._event` | verbose privacy test | Logging privacy |
| Clean source import/metadata | Chapters 15, 16, 18 | `companion-and-verification-working-directory` | `pyproject.toml`, `__init__.py` | `tests.test_metadata` | Testing/recovery |

## Optional systems stage

| Feature | Prior checkpoint | Teaching anchor | Companion authority | Observable evidence | Manual assessment |
| --- | --- | --- | --- | --- | --- |
| Loopback and ephemeral port | Chapter 23 essential | `systems-objective-and-exact-limits` | `LoopbackOrderServer.start` | happy loopback test | Loopback binding |
| Newline JSON and byte bounds | Chapter 23 framing | `predict-framing-and-capacity` | `loopback.py` | constructor, exact-boundary, malformed/oversize/recovery tests | Framing/limits |
| Request/list/concurrency caps | Chapters 7, 10, 23 | `systems-objective-and-exact-limits` | server constructor/handler | busy and request-limit tests | Capacity |
| Idle deadline and capacity recovery | Chapters 14, 21, 23 | `failure-recovery-cancellation-and-solution` | handler wait bounds/events | idle and busy recovery tests | Timeout/recovery |
| Owned cancellation/shutdown | Chapters 21, 23 | `failure-recovery-cancellation-and-solution` | `LoopbackOrderServer.close` | stalled-handler cancellation test | Lifecycle |
| No production claim | Chapter 23 security/lifecycle boundary | `systems-common-mistakes` | README contract | learner explanation | Scope |

## Optional hero packaging stage

| Feature | Prior checkpoint | Teaching anchor | Companion authority | Observable evidence | Manual assessment |
| --- | --- | --- | --- | --- | --- |
| Pure `src` distribution metadata | Chapters 15–16 | `packaging-objective-and-evidence-boundary` | `pyproject.toml` | metadata test and archive inspection | Metadata |
| Exact direct build pins | Chapter 16 | `build-inputs-are-direct-pins-not-a-lock` | `requirements-build.txt`, `BUILD_INPUTS.md` | preflight version plus wheel metadata/SHA-256 | Terminology/provenance boundary |
| Independent bounded source/output/install/foreign roots | Chapters 13, 16, 18 | `verification-phases` | `verify_artifact.py` | size/output/time checks plus cleanup/source fingerprint | Isolation |
| Sdist plus initial pure wheel | Chapter 16 | `verification-phases` | build phase | archive inspectors and SHA-256 report | Build/inspect |
| Rebuild wheel from exact sdist | Chapter 16 | `verification-phases` | safe extraction/rebuild | rebuilt wheel inspection | Sdist completeness |
| Clean install and `pip check` | Chapters 16, 18 | `verification-phases` | fresh venv install | installed verifier phase | Install |
| Foreign import/domain/CLI behavior | Chapters 15, 18 | `verification-phases` | `verify_installed` | metadata path, domain, CLI smoke | Installed behavior |
| No implicit acquisition/publication | Chapter 16 plus release boundary | `packaging-failure-and-recovery` | preflight/offline environment | prerequisite-missing non-pass or full local pass | Explanation/scope |

## Exact verification commands

Run the standard-library behavior suite from the repository root:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

Run source-reference validation through the registered `learning:contract`
check selected by the repository quality runner. A missing registration or
plugin is a non-pass integration state, not evidence that the references ran.

When exact build prerequisites are already provisioned, run:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

If `build==1.3.0` or the declared offline wheelhouse is absent, the verifier
exits nonzero with `prerequisite missing`. Do not install or download
implicitly to turn that result into a pass.

## Recorded local evidence

On 2026-07-15, the complete source suite passed 46/46 tests on CPython
3.13.11. After the exact prerequisites were provisioned deliberately in a
temporary environment, the artifact verifier also passed on Linux with
`build==1.3.0`, `setuptools==80.9.0`, `wheel==0.45.1`, and `pip==25.3`.
It observed:

- sdist `course_order_tracker-1.0.0.tar.gz`, SHA-256
  `803b4d28491eecb42c070f5a02d7ccaee3372129390da21a007831cad302d4a7`;
- initial wheel `course_order_tracker-1.0.0-py3-none-any.whl`, SHA-256
  `65f04e89ad76b09ccde28e2426ab75d5b0b86525e4d5c83ac43dd88d362ccfac`;
  and
- wheel rebuilt from that sdist, SHA-256
  `65f04e89ad76b09ccde28e2426ab75d5b0b86525e4d5c83ac43dd88d362ccfac`.

Matching wheel hashes are an observation for this run, not a general
reproducible-build claim. The temporary frontend, wheelhouse, artifacts,
installation, database, and foreign working directory were removed; nothing
was published.

## Evidence boundary

Passing standard-library tests proves current source behavior on the executed
interpreter. Passing artifact verification additionally proves the locally
observed sdist, wheels, clean install, foreign import, domain/CLI smoke, and
cleanup on the reported host. Neither result proves translation fluency,
rendered accessibility, unexecuted platform compatibility, provenance
acceptance, publication authorization, or production service security.
