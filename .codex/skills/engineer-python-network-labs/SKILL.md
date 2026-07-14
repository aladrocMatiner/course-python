---
name: engineer-python-network-labs
description: Design, review, and verify bounded local-first Python network labs. Use for HTTP, TCP, UDP, sockets, selectors, asyncio streams, framing, TLS, retries, cancellation, backpressure, timeout, lifecycle, and network security exercises or companion tests.
---

# Purpose

Make network lessons deterministic, safe for learners, and honest about failure. Keep required verification on loopback or offline fixtures.

## Required preparation

1. Read repository instructions, the lesson contract, companion source, tests, and the declared Python/platform matrix.
2. Read [HTTP and protocol boundaries](references/http-and-protocol-boundaries.md) for HTTP, TCP/UDP, framing, retry, or resource-limit work.
3. Read [asyncio, lifecycle, and TLS](references/asyncio-lifecycle-and-tls.md) for selectors, tasks, cancellation, shutdown, backpressure, or TLS work.
4. Write down every numeric limit and ownership boundary before execution: peers, body/frame/buffer/history size, pending output, retries, idle deadline, total runtime, and diagnostic output.

## Core workflow

1. Bind only loopback addresses and request an ephemeral port. Never probe a public or production target.
2. Coordinate server readiness with an event, future, pipe, or observed bound address; do not use a fixed sleep as correctness synchronization.
3. Exercise one happy path, one boundary, one malformed input, one stalled/partial peer, disconnect, cancellation, and deterministic shutdown.
4. Include relevant protocol probes: empty UDP datagram, fragmented/coalesced frame, malformed or negative length, oversized body/frame, invalid text/JSON, output backpressure, and idle capacity recovery.
5. Bound retained application state as well as input buffers. A connection that sends valid messages indefinitely must not grow history, queues, tasks, or logs indefinitely.
6. Use monotonic deadlines and exact cleanup assertions. Close listeners, peers, transports, writers, selectors, tasks, and temporary TLS material on success, error, cancellation, and timeout.
7. Run the chapter tests and invoke its plugin explicitly through the root validator. Treat a missing tool, timeout, crash, malformed result, or source mutation as failure unless the plugin contract defines a specific supported skip.
8. Record the host, interpreter, limits, ports as non-stable observations, verified behavior, cleanup evidence, and any unsupported capability.

## Safety and TLS rules

- Use fake payloads, didactic certificates, and temporary keys. Never log credential values, learner data, or captured private material.
- Verify untrusted issuer, hostname mismatch, and expiry as expected failures before demonstrating corrected local trust.
- Keep hostname verification and certificate verification enabled. Do not teach global verification disablement as recovery.
- Bound retries and make retry safety depend on operation idempotency; do not create retry storms.
- Prefer deterministic coordination to timing assumptions and prove no live task or peer remains after each test.

## Handoff

Report learner-visible behavior and lifecycle evidence separately. If only prose or static tokens were checked, say so; do not claim that sockets, cancellation, or TLS executed.
