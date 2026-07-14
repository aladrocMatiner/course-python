# HTTP and protocol boundaries

## HTTP request handling

Validate a declared method/path/content-type contract before processing a body. Parse `Content-Length` once and accept only an integer in the closed range `0..MAX_BODY`; reject missing length when a body is required, negative values, malformed values, and values above the cap before reading. Read exactly the accepted bounded amount and handle premature end-of-file deterministically.

Keep demonstrations on `127.0.0.1`, `::1`, or `localhost` with an ephemeral port. Bound client connect/read timeouts and server lifetime. Do not turn a toy server into a production-security claim.

## Stream framing

Treat TCP as a byte stream: one send is not one receive. Test fragmented and coalesced frames, a delimiter split across reads, an oversized unterminated frame, invalid encoding, end-of-file mid-frame, and more than one frame per read.

Declare limits for:

- bytes per frame and per read;
- bytes retained before a delimiter;
- decoded frames awaiting processing;
- bytes queued for output;
- peers and per-peer logical identifiers;
- retained history or aggregation;
- idle and total operation time.

Apply limits before growing state. Prefer a bounded deque, aggregate, counter, or last-value record when full history is not a learning requirement.

## UDP behavior

Preserve datagram boundaries and treat an empty datagram as valid data, not as stream end-of-file. Test truncation policy, maximum datagram size, timeout, loss/duplication assumptions, and peer-address validation without pretending UDP is reliable or ordered.

## Backpressure and retries

Keep at most the declared pending output per peer and wait for drain/write readiness under a deadline. A slow peer must not block unrelated peers or grow memory indefinitely.

Retry only a bounded number of times with a bounded overall deadline. Explain whether the operation is idempotent and whether a retry can duplicate an effect. Use deterministic injected failures or local fixtures; never generate load against a public service.

## Protocol evidence matrix

Verify happy input, exact boundary, first rejected value, malformed type/encoding, partial input then stall, disconnect during read/write, slow consumer, capacity exhaustion, capacity recovery, and shutdown. Require stable protocol/error codes where learner-facing behavior promises them.
