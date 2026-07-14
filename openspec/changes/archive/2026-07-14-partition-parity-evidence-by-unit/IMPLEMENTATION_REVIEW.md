# Implementation review

Date: 2026-07-13
Change: `partition-parity-evidence-by-unit`
State: implementation complete; all semantic and publication reviews pending

## Outcome

`tools/parity_manifest.json` is now a compact schema-v2 topology index. The
authoritative store contains exactly 27 canonical source leaves and 108
unit/locale leaves. The loader reconstructs the same schema-v1 aggregate used
by validation and review transitions, while ordinary locale work changes only
the affected leaf and never rewrites the index.

The real migration preserved all source audits, digests, statuses, twelve-
dimension contracts, exceptions, commands, signals, gaps, priorities, roles,
dates, and notes. It did not promote any human state.

## Corrections from adversarial review

| Finding | Implemented correction and regression |
|---|---|
| A stale aggregate writer could overwrite another reviewer's disjoint locale. | Old-to-new leaf planning writes only payloads changed from the loaded baseline; disjoint leaves merge and same-leaf conflicts fail. |
| The final check-then-replace window could lose an edit to a leaf or the legacy monolith. | Linux uses `renameat2(RENAME_EXCHANGE)` and validates the exact swapped bytes, rolling back a mismatch and retaining recovery evidence if rollback cannot be proved. |
| Portable filesystems lack byte-conditional rename. | Ordinary non-Linux writers/export use a hardened per-user/per-target cooperative lock, recheck under lock, and no-clobber creation; guidance forbids overlapping an out-of-band editor. |
| Migration validated staging but then rewrote 135 live leaves, leaving an unrecoverable partial store on interruption. | The complete validated staging directory is published once with Linux `RENAME_NOREPLACE`; a tenth-leaf injected failure leaves no live partial store and retry succeeds. |
| Staging acquisition and destination publication had destructive races. | Atomic ownership and no-replace tests preserve foreign staging/store content and clean only owned paths. |
| A store-root symlink, malformed legacy `null`, or corrupted temporary could escape stable failure behavior. | Lexical symlink rejection, stable object validation, and temporary byte re-read now fail closed. |
| Accepted exceptions treated non-empty strings such as `"false"` as approval. | Exact exception keys/dimensions and boolean `is True` are required; parametrized negatives cover dimensions, dual approval, role/date, digests, and required commands. |
| Custom manifest errors could echo an absolute or token-like path. | CLI labels custom manifests generically and JSON readers no longer echo unsafe filenames. |
| A caller-controlled/fixed fallback lock could follow a symlink or collide across repositories. | Lock names hash target plus user ID; safe open flags, owner/inode/type/link/mode/size checks, and a symlink-victim regression prevent writes. |

## Automated evidence

Observed host: Linux 6.17.0-35-generic x86_64, CPython 3.13.11.

| Evidence | Result |
|---|---|
| `python -B -m unittest tools.tests.test_parity_review -v` | 33 tests passed. |
| Full `tools/tests` discovery | 135 tests passed in 17.212 seconds. |
| Real partition topology | 27 `sources/*.json` plus 108 `records/<unit>/<locale>.json`; no symlinks. |
| `python -B tools/parity_review.py` | Exit 0: 27 sources and 108 variants valid. |
| `python -B tools/parity_review.py --require-accepted` | Expected exit 1: 27 canonical audits and 108 localized reviews pending. |
| Real statuses | 27/27 sources remain `pending-human-review`; 108/108 records remain `automated-signals-pass`. |
| Explicit schema-v1 export | Byte-identical to the pre-migration manifest; SHA-256 `295884365c2603d689aad703e3d60933ee815b957a1154de3aadc8c17e65011f`. |
| No-op real `--write` | Partition bytes remained unchanged. |
| Generic/curriculum validators | Exit 0; generic output retains only reviewed informational debt and unselected-domain notices. |
| OpenSpec strict validation, doctor, whitespace | Passed locally; final coordinated run recorded after this review file. |

## Portability and human boundary

The one-time complete-directory migration requires Linux
`renameat2(RENAME_NOREPLACE)` and fails closed elsewhere with schema v1 still
authoritative. On Linux, normal updates use exchange/rollback. On other hosts,
ordinary writers and export protect cooperating CLI operations through the
hardened lock; they do not claim to serialize an editor which ignores it.
Neither Windows nor macOS was executed in this review.

All 27 canonical audits and all 108 linguistic/technical localized reviews
remain pending. Automated structure, byte equality, migration success, and
`automated-signals-pass` are not evidence of semantic equivalence, pedagogy,
rendered accessibility, Arabic bidi quality, provenance, ownership, or license
acceptance. This change is not archived by implementation.
