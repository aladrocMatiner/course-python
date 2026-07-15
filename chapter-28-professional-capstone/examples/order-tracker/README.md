# `course-order-tracker` companion project

This is the executable authority for Chapter 28. It is one pure-Python,
standard-library-only project with a `src` layout. It uses synthetic orders;
it does not collect names, addresses, payments, credentials, or production
data.

## Stable public contract

- Distribution: `course-order-tracker`
- Import package: `order_tracker`
- Installed command: `order-tracker`
- Python: CPython 3.11 or newer
- Runtime dependencies: none outside the standard library
- Statuses: `pending`, `packed`, `shipped`
- SQLite busy timeout: 250 ms by default, configurable only from 1 through
  5,000 ms

The `Order` value is immutable. Identifiers contain 1–32 non-whitespace
characters after surrounding whitespace is removed; item labels contain 1–80;
quantity is an exact built-in `int` from 1 through 1,000 and never `bool`.

## Project layout

- `src/order_tracker/domain.py` owns values, transitions, and stable failures.
- `src/order_tracker/repositories.py` provides interchangeable in-memory and
  SQLite repositories.
- `src/order_tracker/service.py` is the application boundary shared by every
  adapter.
- `src/order_tracker/cli.py` owns argument parsing, configuration precedence,
  stable JSON output, exit status, and privacy-safe logging.
- `src/order_tracker/loopback.py` is an optional bounded newline-JSON loopback
  lab. Importing the package never starts it.
- `tests/` holds domain, repository-contract, service, CLI subprocess,
  loopback-lifecycle, metadata, artifact-preflight, and archive-inspection
  tests.
- `BUILD_INPUTS.md` records direct build-input identity and review boundaries.
- `tools/verify_artifact.py` verifies built artifacts only when its exact build
  prerequisites were provisioned explicitly.

## Run source tests

From the repository root:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

The command needs no third-party dependency and writes all databases under
temporary directories.

## Installed CLI contract

After installing a locally verified wheel into a disposable environment, use
an explicitly selected disposable database:

```bash illustrative
order-tracker --database path/to/disposable/orders.sqlite3 add ORD-001 widget 2
order-tracker --database path/to/disposable/orders.sqlite3 advance ORD-001
order-tracker --database path/to/disposable/orders.sqlite3 list
```

`--database` overrides `ORDER_TRACKER_DB`. With neither value, the command
exits 2 before creating a database. Success exits 0; domain or repository
failure exits 1. Expected learner-facing errors contain no traceback.

## Artifact verification prerequisites

`requirements-build.txt` is a list of exact direct build-tool pins for the
declared workflow. It is not a resolver-generated, hash-complete,
cross-platform lock. Initial acquisition may require network access and is a
separate maintainer action.

[`BUILD_INPUTS.md`](BUILD_INPUTS.md) records the selected release artifacts,
their observed PyPI SHA-256 values, reported project-license metadata, and the
human review boundary. This narrows wheelhouse provenance without turning the
three direct pins into a transitive lock.

The verifier itself never acquires tools. It requires:

- a POSIX host for bounded process-group termination evidence (other hosts
  report a non-pass prerequisite rather than claiming child cleanup);
- an already installed `build==1.3.0` frontend; and
- `ORDER_TRACKER_WHEELHOUSE` pointing to a dedicated offline directory
  containing only the exact recorded `setuptools==80.9.0` and `wheel==0.45.1`
  wheels and hashes.

Then, from the repository root:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

Without those inputs it exits nonzero with `prerequisite missing`. With them,
it builds in isolation with `PIP_NO_INDEX=1`, inspects sdist and wheel,
rebuilds from the exact sdist, installs the rebuilt wheel into a fresh
environment, runs `pip check`, imports and runs the CLI from a foreign
directory, reports SHA-256 observations, and removes every temporary root.
It never uploads, publishes, signs, attests, or requests an index token.
It rejects a source member over 2 MiB, a project snapshot over 8 MiB, an
archive over 12 MiB compressed or expanded, child output over 16 KiB, a build
over 180 seconds, or another verifier child over 30 seconds.

## License

This original educational companion is licensed under CC BY-SA 4.0. See
`LICENSE` and the repository root license.
