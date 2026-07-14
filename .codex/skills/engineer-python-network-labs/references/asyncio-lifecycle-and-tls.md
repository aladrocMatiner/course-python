# Asyncio, lifecycle, and TLS

## Ownership and structured concurrency

Give every task an owner and a bounded await point. On Python 3.11+, prefer `TaskGroup` for related work and `asyncio.timeout` or `wait_for` for an explicit deadline. Preserve the original exception or exception group; do not erase cancellation during cleanup.

Test success, child failure, timeout, caller cancellation, peer disconnect, and server shutdown. After each case, assert no owned task, writer, transport, selector registration, or listening socket remains.

Use events, futures, barriers, or injected clocks for synchronization. A short fixed sleep may help a demonstration breathe, but it cannot prove readiness, concurrency, expiry, or cleanup.

## Selector lifecycle

Track monotonic last-activity/deadline state for each peer. Expire idle or partial peers on a bounded selector tick, unregister before closing, and make repeated close safe. Confirm capacity returns after stalled peers expire.

Keep read and write interest precise. Do not leave a socket permanently writable when there is no pending output, and do not read unbounded new work while its output is backpressured.

## TLS fixtures and recovery

Use only public `ssl` APIs and local didactic material. Keep private keys fake, scoped, inventoried when checked in, or generated under temporary storage. Avoid dates or hosts that make a fixture accidentally valid outside the lesson.

Verify:

1. trusted issuer and matching hostname succeed;
2. untrusted issuer fails;
3. hostname mismatch fails;
4. expired/not-yet-valid certificate fails using a portable public strategy;
5. corrected local trust succeeds without disabling verification;
6. client/server contexts use their intended purpose and hostname checking remains enabled.

Do not use global monkeypatches or private CPython certificate helpers as publication evidence.

## Diagnostics

Log bounded error codes and peer metadata only when safe. Do not print certificates' private components, tokens, payload bodies, learner identifiers, full absolute paths, or arbitrary peer-controlled text. Treat connection resets during cleanup as expected bounded outcomes only where the contract says so.
