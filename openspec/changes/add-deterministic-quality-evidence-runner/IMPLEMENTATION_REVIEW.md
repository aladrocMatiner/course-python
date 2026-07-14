# Implementation review

Date: 2026-07-13
Change: `add-deterministic-quality-evidence-runner`
State: implementation complete; hosted CI and human publication gates pending

## Outcome

The repository now has a schema-v1 closed quality matrix and one deterministic
runner for `core`, networking, C++, Rust, and maintainer handoff evidence. The
runner preserves the existing validator CLIs, distinguishes pass/fail/error/
unsupported/not-selected, rejects profile weakening, executes without a shell,
bounds output and time, keeps temporary state outside the checkout, and detects
source mutation.

On the observed Linux host it uses a subreaper plus continuous `/proc`
observation. Empty, unreadable, malformed, or partial maps fail closed. If
observation is lost after launch, known PIDs are stopped/killed and the result
states that cleanup of unobserved descendants cannot be proved. Other hosts are
`unsupported` for execution rather than silently receiving weaker containment.

## Corrections from adversarial review

| Finding | Implemented correction and regression |
|---|---|
| A detached `setsid()` descendant could outlive a successful parent. | Linux subreaper adoption, recursive `/proc` tracking, TERM/KILL cleanup, quiescence, and a delayed-writer regression. |
| `/proc` enumeration failure or a partial map could become a false pass. | Pre-launch and continuous observation checks now reject empty/partial/malformed maps; live direct/known PIDs cannot disappear from evidence; recovery tests prove known cleanup and no late write. |
| A regular output file could exceed a small configured cap before inspection. | Non-blocking pipe streaming retains no raw log and saturates the observed byte count exactly at the cap; a 100,000-byte writer with cap 128 reports error and records 128. |
| A caller-controlled `TMPDIR` could place temporary state in the checkout. | Only a verified writable `/tmp` or `/var/tmp` outside the repository is used; malicious environment fixtures cannot move it. |
| Matrix edits could remove the tests protecting `core` or broaden domain profiles. | The parser enforces exact required check adapters, paths, profile membership, and order before selection. |
| Public fields and diagnostics could leak ANSI controls, token assignments, or paths with spaces. | Matrix-owned public fields reject them without reflection; result messages redact POSIX, drive, and UNC paths plus `OPENAI_API_KEY`-style assignments. |
| The workflow pin test recognized only literal `uses:`. | Contract tests cover whitespace, quoted keys, and inline YAML mappings and require every detected action ref to be exactly 40 hex. |
| A failed subreaper restoration could be hidden by an early success return. | Restoration is unconditional; failure overrides pass as infrastructure error and aggregate exit 2. |

## Automated evidence

Observed host: Linux 6.17.0-35-generic x86_64, CPython 3.13.11.
Observed OpenSpec CLI: 1.6.0.
Observed revision: `26b3b488502978befc736c6952b062e571493a19`.

| Evidence | Result |
|---|---|
| `python -B -m unittest tools.tests.test_run_quality -v` | 33 tests passed. |
| Workflow contract test | 1 test passed; immutable actions, least privilege, exact jobs/profiles. |
| Full `tools/tests` discovery | 135 tests passed in 17.212 seconds. |
| Two real `core --format json` runs | Both passed and were byte-identical; SHA-256 `c0f7cc28b34dc041f5077aa8804f1107ffa12543d6fb92244a3d80c71b258339`. |
| Two real `core --format markdown` runs | Both passed and were byte-identical; SHA-256 `a1a16c1cf70858cf268a35970f15f457910d9f96a22e163f5d0c06309c3dccb2`. |
| `network-domain` | Passed only the explicitly selected Chapter 23 loopback plugin. |
| `cpp-domain` | Passed only the lightweight Chapter 24 contract/boundary plugin; no native build matrix claim. |
| `rust-domain` | Passed only the lightweight Chapter 25 contract/distribution plugin; no native build matrix claim. |
| `handoff --format markdown` | All nine checks passed; report SHA-256 `56615f92fc9f8fea23d07c79187bd03752ae138c8c0e6b568fe9163cdaeb8cba`. |
| Direct curriculum/parity/book/plugin commands | Exit 0 and agreed with their selected profiles. |
| OpenSpec strict validation, doctor, whitespace | Passed locally; final repository-wide run recorded after this review file. |

## Evidence boundary

This is local execution evidence, not a hosted GitHub Actions run. The workflow
is provisioned and contract-tested but has not run on GitHub in this change.
Windows and macOS process containment remain unsupported and unexecuted. No
fork-bomb, hostile-code sandbox, heavy C++/Rust build, wheel/ABI matrix,
performance threshold, or unexecuted platform is inferred from the lightweight
profiles.

The content snapshot covers regular, symlink, and special file entries under
the checkout, including ignored/untracked files, but excludes `.git`; its byte
cap does not separately bound directory metadata or the number of empty files.
The runner reduces trusted-project accidents and reports incomplete evidence;
it is not a security boundary for hostile repository code.

Pedagogy, linguistic quality, rendered accessibility, Arabic bidi behavior,
provenance/license decisions, compatibility, and performance remain human
gates. This change is not archived by implementation.
