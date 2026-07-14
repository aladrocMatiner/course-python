# Chapter 24 implementation traceability

This maintainer-facing map connects every OpenSpec requirement to learner-facing teaching, implementation, and executable evidence. It is not another lesson or a replacement for the five localized READMEs.

| OpenSpec requirement | Teaching location | Companion implementation | Primary evidence |
|---|---|---|---|
| Progressive learning path | README routes and sessions 1–15 | `00-cpp-survival`, `01-first-extension`, `faststats-cpp`, `embed-python` | `tools/verify_all.py` |
| Reproducible native toolchain | Toolchain preflight and platform guidance | exact direct dev-tool input, isolated-build constraints, `tools/preflight.py` | recorded preflight plus isolated PEP 517 logs; no hermetic/cross-platform lock claim |
| Layered architecture | Professional sessions 5–6 | `core.*`, `bindings.cpp`, facade, reference, stubs | CTest, pytest, artifact smoke |
| Exact faststats contract | Session 5 | `_reference.py`, `core.cpp`, binding validators | `test_contract.py`, `core_tests.cpp` |
| Pythonic types and errors | Sessions 6–7 | bindings, enum, class, callbacks, translator | contract/online/callback pytest |
| Ownership and lifetime safety | Session 8 owner table | smart holder, `reference_internal`, `keep_alive` | `test_ownership_callbacks.py` |
| Safe buffer interoperability | Session 9 | `check_buffer`, borrowed core calls | `test_buffers.py` |
| GIL/thread/callback boundaries | Session 10 | `summarize_many`, `_faststats_test` | deterministic `test_concurrency.py` |
| Evidence-based performance | Session 11 | `benchmarks/benchmark.py` | parity-before-timing benchmark run |
| Packaging, ABI, wheel | Session 12 | PEP 517 metadata and artifact verifier | sdist→wheel, stubtest, strict positive/negative typing, parsed `ldd`/platform audit |
| Embedded Python host | Session 14 | `embed-python/src/main.cpp` and fixed strategies | good/raise/invalid/decoy cwd exit tests |
| Testing/debugging/capstone | Sessions 13 and capstone verification | CMake profiles and generated sanitizer-capability evidence | Debug/Release CTest+pytest, confirmed ASan/UBSan or explicit unsupported skip, hygiene |
| Multilingual/scope control | every localized README and final scope sections | plugin plus five language files | root bookcheck with `cpp` plugin; root indexes coordinated separately |

## Stable check IDs

- `cpp:contract` protects pinned toolchain, numeric, holder, and GIL tokens used by `source-ref` blocks.
- `cpp:boundaries` protects the Python-free core and excludes the rendezvous target from installation.
- The root validator owns generic Markdown, localization, accessibility, links, RTL, and ignored-artifact hygiene.

## Evidence boundary

The recorded Linux run proves CPython 3.13.11, GCC 13.3.0, CMake 4.1.2, pip 25.3, pybind11 3.0.4, and scikit-build-core 1.0.3 on that target. GCC/Clang/MSVC portability is designed but must not be reported as tested without another execution record. Root-index integration remains intentionally serialized with chapters 23 and 25.
