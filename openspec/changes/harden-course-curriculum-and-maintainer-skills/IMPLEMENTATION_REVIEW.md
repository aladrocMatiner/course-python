# Implementation review

Date: 2026-07-13
Change: `harden-course-curriculum-and-maintainer-skills`
State: implementation complete; publication/human acceptance deliberately pending

## Outcome

The change is implemented across the five new maintainer skills, the extended `professor` and `book-editor` skills, the curriculum contract and routes, the audited beginner and systems lessons, Chapters 23–25 companions, parity tooling, and explicit CI domain jobs. Public chapter paths and native APIs remain stable. `README.md` remains byte-identical to `README.en.md`.

Automation now inventories all 27 canonical units and 108 localized variants.
At this change's implementation snapshot, all 108 records had current automated
signals. Later canonical and localized editorial work correctly opened a new
review cycle: the coordinated current state is 33 `automated-signals-pass` and
75 `drafted`. All 27 canonical source audits and all 108 linguistic/technical
reviews remain pending. This is an apply-complete OpenSpec change, not an
assertion that the separate multilingual restoration change is accepted or
ready to archive.

## Corrections found during forward review

Independent fresh-context skill runs were treated as adversarial forward tests, not as approval:

| Finding exposed by the forward run | Correction and regression evidence |
|---|---|
| A TLS peer that connected but never completed its handshake existed before the async handler tracked a writer/task. | The server now applies bounded public `ssl_handshake_timeout` and `ssl_shutdown_timeout`; a regression proves the pre-handler peer is released. |
| Network evidence did not exercise output stall, capacity recovery after selector expiry, empty UDP data, or portable TLS scheduling/error assertions. | Added all four cases, removed English exception-message dependence/fixed-sleep correctness, and brought the bounded loopback suite to 33 passing tests. |
| The Chapter 15 lesson omitted the PEP 517 backend acquisition boundary and cleanup path. | All five lessons now distinguish an online/cache-backed isolated build, a reviewed offline wheelhouse, and a checked non-isolated fallback. A committed artifact verifier builds only a temporary source copy, inspects the wheel, installs that exact wheel in a second venv, and tests it from a foreign cwd. |
| The first artifact-runner iteration could leave a descendant after a successful parent, or after a timeout when the descendant ignored `SIGTERM`. | Cleanup now targets the complete process group on every exit, escalates to `SIGKILL` on POSIX, and uses a kill-on-close Windows Job Object before allowing the real command to start. Linux regressions prove both reported leak cases; Windows remains designed but locally unexecuted. |
| The first `RECORD` check accepted any `sha256=` prefix and numeric size. | Inspection now decodes and compares every URL-safe SHA-256 and exact byte size, correlates all archive members, and rejects a fixture with a false digest and `999999` size. |
| An `accepted` parity record could omit automated evidence and retain a pending canonical audit. | Acceptance now requires an approved current source audit, both human reviews, and the exact generic/parity commands. A negative unit fixture protects this boundary. |
| The C++ negative typing probe accepted any three `error:` strings. | It now requires exactly one diagnostic at each native-only constructor line (11, 15, and 19); the full mypy run proved those exact locations. |
| The workflow test checked only that plugin command strings existed. | It now parses named job blocks, forbids plugins in the generic job, requires one explicit plugin in each domain job, and rejects `continue-on-error`, `|| true`, `set +e`, and automatic plugin discovery. |
| The Rust benchmark encoded but did not report warm-up/repetition counts. | The evidence record now prints warm-up count, timed repetitions, statistic, and input sizes before reporting medians. |

## Automated evidence matrix at the implementation snapshot

| Area | Command/evidence | Result |
|---|---|---|
| Skill packages | `quick_validate.py` against the five new skills plus `professor` and `book-editor` | 7/7 valid |
| Skill/tool contracts | `python -B -m unittest discover -s tools/tests -p 'test_*.py' -v` | 82 tests passed; includes 5 skill-contract and 10 curriculum tests |
| Curriculum declaration | `python -B tools/validate_curriculum.py` | 0 issues; contractual ordering evidence only, not pedagogical approval |
| Standard-library companions | Chapter 15/19/20/21/22 and both appendix unittest suites | 36 tests passed: 17 + 4 + 3 + 3 + 3 + 2 + 4 |
| Chapter 15 artifact | `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py`, online/cache-backed and provisioned `--wheelhouse` runs | Both isolated PEP 517 builds, structured wheel inspection, exact install, `pip check`, installed test/entry point, foreign-cwd import, source snapshot, and cleanup passed |
| Network companions | `python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p 'test_*.py' -v` | 33 tests passed on loopback with bounded time/state |
| Generic book gate | `python -B tools/validate_book.py` | Exit 0; only two exact accepted legacy attribution notices and intentionally unselected domain references were informational |
| Parity inventory | `python -B tools/parity_review.py` | 27 sources and 108 variants valid; 108 `automated-signals-pass` records |
| Publication boundary | `python -B tools/parity_review.py --require-accepted` | Expected exit 1: 27 canonical audits and 108 localized reviews pending |
| Network domain | `python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py` | Exit 0; `network:network-suite` passed |
| C++ domain | `python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py` | Exit 0; `cpp:contract` and `cpp:boundaries` passed |
| Rust domain | `python -B tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py` | Exit 0; `rust:contract` and `rust:distribution-boundary` passed |
| OpenSpec | Strict validation for this change, `add-book-quality-gates`, and `restore-multilingual-content-parity`; `openspec doctor` | All valid; doctor reports the OpenSpec root is healthy |

## Coordinated-state recheck on 2026-07-14

Subsequent work in `add-book-quality-gates` and
`restore-multilingual-content-parity` changed content and expanded the neutral
provenance inventory. The current recheck therefore distinguishes this
change's automated contracts from those active changes' human publication
gates:

- the complete tools suite passes 136/136 tests, the curriculum validator
  reports zero issues, and normal parity validation reports 27 sources and 108
  variants;
- parity correctly retains 33 records at `automated-signals-pass` and 75 at
  `drafted`; publication mode still reports 27 canonical audits and 108
  localized reviews pending;
- the generic and all three explicit plugin invocations preserve five new
  unbaselined `attribution.review_required` warnings for `LICENSE`, Chapter 3,
  the Chapter 23 TLS fixtures, Chapter 24, and Chapter 25, so their aggregate
  exit is 1 while those human provenance decisions remain unresolved;
- the owning network, C++, and Rust plugin checks themselves report positive
  domain evidence; none suppresses, converts, or misattributes the generic
  provenance warnings;
- strict validation passes for all eight active OpenSpec changes, OpenSpec
  doctor finds a healthy root, and `git diff --check` passes.

This non-zero aggregate is the intended fail-closed publication behavior of
the coordinated active quality change, not a failed skill, curriculum, domain,
or companion contract in this implementation. Archiving this implementation
must not archive or approve the still-active provenance and multilingual
changes.

## Package and native host evidence

### Chapter 15 pure-Python package

- Host: Linux x86_64, CPython 3.13.11.
- Produced temporary online/cache-backed `course_mi_app-0.1.0-py3-none-any.whl`, SHA-256 `2cf9b33330eaa912ef3df6a6dc0a5293839e6e088edc77abc11dbd91cf85209b`.
- The verifier parses and correlates `METADATA`, `WHEEL`, `entry_points.txt`, and `RECORD`; compares the three packaged modules byte-for-byte with reviewed source; rejects extra/unsafe/oversized members; installs with `--no-index` from the exact local artifact; runs `pip check`, the installed `mi-app` entry point, the installed test, and a foreign-cwd import; bounds subprocess time/output/process trees; removes temporary state; and proves the checkout snapshot is unchanged.
- An adversarial offline run with only `setuptools` correctly exposed the backend's dynamic `wheel` requirement. The verifier and five lessons now require both inputs and fail before building if either is missing.
- A final provisioned no-index run passed using `setuptools-83.0.0` (SHA-256 `29b23c360f22f414dc7336bb39178cc7bcbf6021ed2733cde173f09dba19abb3`) and `wheel-0.47.0` (SHA-256 `212281cab4dff978f6cedd499cd893e1f620791ca6ff7107cf270781e587eced`). It produced an offline temporary project wheel with SHA-256 `66e1d941cadea3d795359545a482041e5db3e53c545159d511623fc6d9124a91`; all wheelhouse, build, and install temporaries were removed. These automated downloads/hashes prove the offline mechanism, not human review of those third-party inputs.

### Chapter 24 C++/Python

Full command: `COURSE_CPP_VERIFY_PYTHON=/tmp/course-cpp-dev/bin/python python -B chapter-24-python-cpp-integration/tools/verify_all.py`.

- Host: Linux 6.17.0-35 x86_64, glibc 2.39; CPython 3.13.11 (`cpython-313-x86_64-linux-gnu`).
- Toolchain: GCC/G++ 13.3.0, GNU ld 2.42, C++17, CMake 4.1.2, Ninja 1.13, pip 25.3, build 1.3.0, pybind11 3.0.4, scikit-build-core 1.0.3, pytest 8.4.2, mypy 1.18.2.
- Passed survival CTest/binary, first-extension wheel with 2 pytest cases, faststats Debug and Release CTest plus 36 pytest cases each, clean sdist-to-`cp313` wheel rebuild/install, `pip check`, foreign-cwd smoke, stubtest, strict positive typing, the three exact negative typing diagnostics, resolved ELF dependencies, and all embedded-host success/error/path cases. The 2026-07-14 coordinated recheck repeated the complete verifier after adding a misaligned-buffer regression and passed 37 pytest cases in both Debug and Release, plus sanitizers, artifacts, typing, dependencies, and embedding.
- GNU ASan/UBSan executed and passed with recorded status `enabled:GNU`; it was not counted as a skip.
- The first artifact attempt correctly failed because a local compile probe had produced a source `__pycache__` that entered the sdist. That cache was removed and the complete verifier was rerun from fresh temporary builds to exit 0. No partial result was promoted.

### Chapter 25 Rust/Python

Full command from `chapter-25-python-rust-integration/`: `python -B examples/faststats-rs/tools/verify.py`.

- Host: Linux 6.17.0-35 x86_64, glibc 2.39; CPython 3.13.11 (`cpython-313-x86_64-linux-gnu`).
- Toolchain: pinned rustc/Cargo 1.97.0 via rustup, GCC 13.3.0, GNU ld 2.42, PyO3 0.29.0, maturin 1.14.1, pip 25.3, pytest 9.1.1, mypy 2.2.0. The shell default rustc 1.96.1 was not mistaken for the pinned compiler.
- Passed locked fmt/clippy/Cargo tests, expected ownership compile failure and recovery, first-extension editable/wheel tests, a dedicated test-hooks wheel with 4/4 concurrency cases, clean sdist reconstruction, strict typing/stubtest, and clean foreign-cwd installs.
- Release wheel: `cp313-cp313-manylinux_2_34_x86_64`, with 40 pytest cases passed and 2 intentional hook-only skips. Those two paths passed in the dedicated hook wheel.
- Stable ABI wheel: `cp311-abi3-manylinux_2_34_x86_64`; tag/content inspection and clean CPython 3.13 install/smoke passed.
- Benchmark smoke reported `warmup-runs=1; timed-repetitions=3; statistic=median; sizes=10,10000`, verified all six result fields and representative `TypeError`/`ValueError` behavior before timing, and made no minimum-speedup claim.

## Deliberately unresolved human and platform gates

- All 27 canonical source audits remain `pending-human-review`.
- All 108 localized records retain pending linguistic and technical/pedagogical review; 33 currently retain automated signals and 75 are drafts in the new review cycle. Automated word/fence/heading signals are triage only.
- Rendered accessibility, Arabic visual bidi/copy-paste behavior, and provenance/license decisions for reviewed material still require competent humans.
- The generic validator reports two accepted legacy attribution-review notices (`chapter-02-variables/README.md` and `icons/cc-by-sa.svg`) as informational debt plus the five unbaselined provenance-review warnings listed in the coordinated-state recheck. This change does not claim to resolve or waive any of them.
- Native verification is execution evidence only for this Linux x86_64/CPython 3.13 host. Windows/MSVC and macOS/Clang remain unverified. The Rust `abi3` tag/install on 3.13 is not execution evidence for CPython 3.11, 3.12, free-threaded Python, or other operating systems.
- Full native builds remain outside the lightweight static CI domain jobs. CI runs explicit bounded plugins with read-only permissions; it does not imply the wider local native matrix.

No change is archived by this implementation. The separate multilingual restoration and provenance/accessibility work must remain active until their human gates are genuinely complete.
