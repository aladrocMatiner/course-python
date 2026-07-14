# Chapter 25 implementation traceability

This authoring record maps the approved capability to learner-facing sections,
companion assets, and executable evidence. It is not a sixth language variant.

| Requirement | Learning evidence | Implementation evidence | Verification |
|---|---|---|---|
| Progressive curriculum | README sections 1–20 and route map in five languages | survival → first extension → capstone | root gate; editorial review |
| Reproducible toolchain | README section 2 | `tools/preflight.py`, three exact `rust-toolchain.toml` pins, `Cargo.lock`, direct Python-tool pins | preflight plus lock-aware verifier |
| Rust foundations | README sections 3–5 | `00-rust-survival`, expected move error and borrow solution | fmt, clippy, Cargo tests, direct rustc |
| Mixed package architecture | README section 7 | `src/domain.rs`, `src/lib.rs`, facade, reference, stubs | build and foreign-cwd import |
| Typed ownership boundary | README section 8 | exact-type extraction and `describe_payload` | boundary/parity tests and clippy |
| Faststats capstone | README sections 5, 9, 10 | domain, `Summary`, `OnlineStats` | domain and pytest boundary suites |
| Error and panic contract | README section 11 | `DomainError` mapping and checked extraction | Cargo/pytest plus unwrap audit |
| Attachment and parallelism | README section 13 | owned-data `py.detach`, excluded test rendezvous, dedicated timeout error | dedicated test-hooks wheel |
| Dual-language verification | README sections 12 and 16 | Cargo tests, pytest, stubs, verifier | full `verify.py` run |
| Evidence-based performance | README section 14 | `benchmarks/benchmark.py` compares every public field before timing | correctness-first benchmark smoke |
| Packaging, ABI, typing | README section 15 | sdist, default/abi3 feature, `.pyi`, `py.typed` | rebuild, inspect, clean install, mypy |
| Pedagogy and assessment | README sections 17–20 in five languages | exercises, hints, solutions, rubric | professor/book-editor review |
| Multilingual scope/hygiene | five READMEs and shared source refs | Rust plugin; temporary-only build outputs | root gate reports zero chapter/plugin diagnostics |

The six root index files (five languages) link this chapter through the integrated and hero routes.
The implementation is complete; archiving remains a separate maintainer action.
