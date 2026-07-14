# Rust interoperability workflow

## Toolchain terminology and preflight

Treat Cargo `rust-version` as the minimum supported Rust version (MSRV) contract and `rust-toolchain.toml` as an exact development/verification toolchain selection. Test the pinned toolchain and, when claimed, the MSRV separately; neither label substitutes for execution.

Record rustup/rustc/cargo versions, host triple, linker family, Python ABI/architecture, PyO3, maturin, and enabled features. Detect the active target rather than requiring Unix `cc` everywhere: GNU-like targets need their configured C compiler/linker, while `*-pc-windows-msvc` requires an available MSVC linker/developer environment. Report a missing prerequisite precisely.

## Domain and Python boundary

Keep domain behavior independent of PyO3. Test Rust success and error variants before mapping them to stable Python exceptions. Avoid `unwrap`, `expect`, panic, and unchecked indexing on Python-controlled paths unless a proven invariant makes them unreachable and the reason is documented.

Audit extraction and conversion for exact/coercible Python types, booleans-as-integers, integer overflow, non-finite floats, size caps, strings/bytes, and owned versus borrowed data.

## Ownership, attachment, and concurrency

Move only owned, `Send`-safe data into detached work. Access no `Bound`, `Python`, borrowed buffer, Python callback, or interpreter-owned value while detached. Reattach before constructing Python results or exceptions.

Use a bounded rendezvous to prove parallel native entry. Preserve synchronization poisoning or worker failure as an actionable test failure; do not swallow it into an empty/default result. Ensure test-only features and rendezvous source are disabled and excluded from release artifacts.

## Cargo, maturin, typing, and ABI

Run format, clippy with warnings denied where declared, Cargo tests with the checked-in lock, and expected compiler-error/recovery examples. Build wheels through maturin in temporary storage, test version-specific and `abi3` variants only when configured, and inspect their tags/content/runtime imports.

Keep the Python facade, extension module name, `.pyi`, and `py.typed` aligned. Run pytest, a type checker, and stub/runtime surface checks. Build a wheel from the sdist, install it cleanly, and import from a foreign directory.

Compare the complete public result before any benchmark, including counts and every summary field. Record release profile, sizes, warmup, repeats, host, copy/conversion cost, and medians; never promise Rust is universally faster.

## Repository commands

Use the Chapter 25 plugin for bounded contract evidence and its full verifier only where Rust, the linker, Python build inputs, and maturin are provisioned. Keep `target`, Cargo home/cache overrides, environments, wheels, sdists, libraries, logs, and panic/core artifacts in temporary storage. Do not broaden Linux evidence to Windows or macOS.
