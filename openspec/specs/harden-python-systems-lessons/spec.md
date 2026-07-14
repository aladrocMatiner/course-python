# harden-python-systems-lessons Specification

## Purpose
TBD - created by archiving change harden-course-curriculum-and-maintainer-skills. Update Purpose after archive.
## Requirements
### Requirement: HTTP examples reject ambiguous or unbounded requests
The course SHALL teach and test an HTTP handler that accepts only the documented route and media type, parses `Content-Length` as an integer in the inclusive range `0..MAX_BODY`, applies a bounded read, and returns stable client errors without waiting for EOF.

#### Scenario: Valid bounded JSON request
- **WHEN** a loopback client sends the documented path, JSON media type, and a body whose declared length is within the limit
- **THEN** the handler reads exactly that many bytes and returns the documented success response

#### Scenario: Negative, malformed, or oversized length
- **WHEN** `Content-Length` is absent where required, non-numeric, negative, or greater than `MAX_BODY`
- **THEN** the handler returns a bounded `4xx` response without calling an unbounded read or blocking the single-server loop

#### Scenario: Wrong route or media type
- **WHEN** a request uses an undocumented route or non-JSON media type
- **THEN** the handler rejects it explicitly and the lesson explains the boundary rather than silently accepting arbitrary input

### Requirement: Logging configuration has an explicit trust boundary
The course SHALL describe `logging.config.dictConfig` input as executable application configuration that is safe only from a trusted local source, and SHALL not present arbitrary user-supplied JSON as safe configuration.

#### Scenario: Trusted local configuration
- **WHEN** the lesson loads a bundled or application-owned JSON file
- **THEN** it validates an allowlisted schema or clearly states why the source is trusted before passing the dictionary to `dictConfig`

#### Scenario: Untrusted configuration
- **WHEN** configuration could be supplied by a learner, request, download, or another untrusted party
- **THEN** the lesson refuses to pass it directly to `dictConfig` and explains that factories/importable callables can create code-execution behavior

### Requirement: Async lessons teach bounded structured concurrency
The asyncio route SHALL distinguish cooperative tasks from threads, teach timeout and cancellation propagation for CPython 3.11+, and prefer structured task ownership for required concurrent work.

#### Scenario: Successful task group
- **WHEN** several bounded local operations complete successfully
- **THEN** the example waits for the owned tasks, reports deterministic results, and leaves no background task running

#### Scenario: Timeout or child failure
- **WHEN** a child exceeds its deadline or raises an expected failure
- **THEN** sibling cancellation and cleanup are observable, `CancelledError` is not swallowed, and the learner receives a recoverable explanation

### Requirement: Network servers bound state, occupancy, and shutdown
The networking chapter SHALL enforce explicit limits for incomplete frames, retained readings, pending output, sensors, connected peers, and peer idle time; every server path SHALL release state on EOF, timeout, protocol rejection, cancellation, or normal shutdown.

#### Scenario: Long-lived valid client
- **WHEN** one client sends more valid readings than the retention limit
- **THEN** retained history stays bounded through aggregation or a fixed-capacity buffer while sequence validation remains correct

#### Scenario: Idle or partial clients occupy capacity
- **WHEN** clients connect and stop before completing a frame
- **THEN** an explicit idle deadline closes them and frees capacity in bounded time

#### Scenario: Fragmentation and coalescing
- **WHEN** frames arrive fragmented or multiple frames arrive together
- **THEN** the decoder preserves message boundaries and never exceeds the documented buffer limit

#### Scenario: Local TLS failure and recovery
- **WHEN** hostname, trust anchor, expiry, or protocol validation fails against the bundled loopback fixtures
- **THEN** tests observe the documented failure without private CPython APIs, live targets, or learner secrets

### Requirement: Packaging lessons distinguish snapshots, constraints, and reproducible builds
The course SHALL use accurate terminology for dependency snapshots, constraints, lock files, build isolation, sdists, wheels, and native wheel tags, and SHALL scope reproducibility claims to evidence actually executed.

#### Scenario: Beginner dependency snapshot
- **WHEN** `pip freeze` is shown
- **THEN** the lesson calls it an environment snapshot rather than a resolver or hermetic lock and explains its platform/interpreter scope

#### Scenario: Installable src layout
- **WHEN** a professional `src` layout is taught
- **THEN** the importable package lives beneath `src/<package>/`, metadata builds an installable distribution, and a clean foreign-working-directory import is verified

#### Scenario: Native package verification
- **WHEN** C++ or Rust packaging claims a reproducible wheel or sdist
- **THEN** the verifier builds from a clean source distribution, installs into a clean environment, checks tags/dependencies/typing, records the tested host matrix, and labels untested platforms explicitly

### Requirement: C++ verification reports capabilities truthfully
The C++ companion SHALL separate autonomous core tests from CPython binding tests, verify public typing and artifact dependencies, and distinguish sanitizer success from an unsupported-toolchain skip.

#### Scenario: Supported sanitizer toolchain
- **WHEN** ASan/UBSan are enabled on a supported compiler
- **THEN** configuration evidence proves the flags reached the intended autonomous targets and those tests pass before success is reported

#### Scenario: Unsupported sanitizer toolchain
- **WHEN** the compiler cannot support the configured sanitizer contract
- **THEN** the verifier emits an explicit structured skip and never prints a sanitizer-passed claim

#### Scenario: Stub and native API agree
- **WHEN** `stubtest` or a typing consumer checks constructors, methods, callbacks, and return types
- **THEN** unsupported construction is rejected and an allowlist cannot hide an entire public class surface

#### Scenario: Broken runtime dependency
- **WHEN** the built extension inspection reports a missing dynamic dependency
- **THEN** artifact verification fails instead of merely printing the platform tool output

### Requirement: Rust verification distinguishes compiler policy and runtime failures
The Rust companion SHALL distinguish Cargo MSRV from an exact rustup toolchain, support the documented compiler family on each claimed platform, preserve the real cause of concurrency failures, and benchmark the full public result contract.

#### Scenario: Toolchain preflight on Unix and Windows
- **WHEN** preflight runs on a documented Unix compiler environment or an MSVC developer shell
- **THEN** it detects the platform-appropriate C compiler, verifies the pinned rustup toolchain separately from `rust-version`, and reports unsupported setups without a false build failure

#### Scenario: Benchmark parity
- **WHEN** the Rust benchmark runs before timing
- **THEN** it compares every public summary field and error contract against the Python oracle before reporting samples

#### Scenario: Test rendezvous fails
- **WHEN** a test hook times out or its synchronization state is poisoned
- **THEN** the Python exception identifies that concurrency/test-hook failure rather than mapping it to an unrelated domain validation error

### Requirement: Supporting advanced lessons preserve safe executable contracts
The introspection and appendix examples SHALL be complete, importable, narrowly exception-safe, and explicit about algorithm preconditions and complexity assumptions.

#### Scenario: Introspection hooks can execute code
- **WHEN** the lesson uses `getattr`, `hasattr`, `vars`, `dir`, descriptors, or properties
- **THEN** it explains which operations can invoke user code and provides a bounded example with a real companion module or self-contained test

#### Scenario: CLI error recovery
- **WHEN** the CLI receives an expected invalid path or argument
- **THEN** `main(argv)` returns a stable exit code, catches only expected exceptions, and does not expose an arbitrary raw exception as user-facing output

#### Scenario: Graph search contract
- **WHEN** breadth-first search is described as `O(V + E)`
- **THEN** the lesson states the node hashability and average dictionary/set operation assumptions and does not attribute the bound to a misleading “shared references” optimization

### Requirement: Systems corrections remain equivalent and accessible in five languages
Every learner-facing systems correction SHALL preserve the same limits, warnings, commands, exercises, recovery behavior, and tested-platform scope in English, Spanish, Catalan, Swedish, and Arabic.

#### Scenario: Localized safety boundary
- **WHEN** a canonical body limit, timeout, trust boundary, supported platform, or explicit skip changes
- **THEN** all four localized siblings express the same numerical and behavioral contract without broadening it

#### Scenario: Arabic and narrow-screen reading
- **WHEN** an Arabic lesson or a wide capability table is updated
- **THEN** one outer RTL wrapper remains balanced, code and paths stay readable LTR, and a prose/list equivalent makes the relationship understandable without visual position alone

#### Scenario: Repository hygiene
- **WHEN** systems examples and verification finish
- **THEN** no build directory, cache, environment, wheel, sdist, credential, learner data, or transient certificate is left in the source tree
