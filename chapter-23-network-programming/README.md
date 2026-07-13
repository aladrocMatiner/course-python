# Chapter 23 · Network Programming with Python

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

In this chapter you will grow one local telemetry project from a first TCP echo into a bounded asynchronous hub. You need Python 3.11 or later, but no networking experience, Internet connection, administrator permissions, or third-party package.

All servers bind to loopback: `127.0.0.1`, or `::1` in the optional IPv6 lab. Do not change them to a public interface while learning. Scanning, sniffing, raw sockets, spoofing, exploitation, custom cryptography, and public deployment are outside this chapter.

## Outcomes, prerequisites, and routes

You will be able to explain the path from text to bytes, choose TCP or UDP, frame and validate a protocol, serve several clients without unbounded state, apply `asyncio` backpressure, verify TLS identity, and test shutdown and failure paths.

Refresh only what you need:

- [Streams and context managers in chapter 13](../chapter-13-files/README.md): deterministic resource cleanup.
- [Exceptions in chapter 14](../chapter-14-exceptions/README.md): recover from expected failures.
- [Automated testing in chapter 18](../chapter-18-testing/README.md): arrange, act, and assert.
- [HTTP in chapter 19](../chapter-19-http/README.md): HTTP is an application protocol, not the transport itself.
- [Logging in chapter 20](../chapter-20-logging/README.md): useful diagnostics without leaking payloads.
- [`asyncio` in chapter 21](../chapter-21-async/README.md): coroutines, tasks, and cancellation.

| Route | Time | Starting point | Observable result |
|---|---:|---|---|
| Essential | 2 × 45–60 min | Python functions and exceptions | Explained local TCP echo |
| Intermediate | 3 × 45–60 min | Essential checkpoint | Tested sequential telemetry protocol and UDP comparison |
| Advanced | 3–4 × 45–60 min | Intermediate checkpoint and chapter 21 | Bounded multi-client asynchronous hub |

TLS and IPv6 are optional advanced extensions. Each earlier checkpoint is useful without them.

## Essential route — from a message to a TCP stream

### 1. A small network vocabulary

A **client** starts a conversation; a **server** waits for conversations. A **host** is a machine or network environment. The Domain Name System (**DNS**) maps names to addresses. An **IP address** identifies an interface, while a **port** selects one program on that host. A **socket** is the operating-system endpoint Python uses to send and receive. A **protocol** is the shared set of message rules.

Imagine a letter: the IP address is the building, the port is the room, and the protocol is the agreed form inside the envelope. The analogy is limited—TCP carries an ordered stream of bytes, not separate envelopes.

Layers keep responsibilities separate. IP moves packets between addresses. TCP or UDP supplies transport semantics. HTTP and our telemetry format are application protocols above transport. Return to chapter 19 for consuming HTTP APIs; here we build a small application protocol to understand the layer below.

#### Predict, run, observe

Python sockets exchange **bytes**. Text needs an agreed encoding. Predict what `len(encoded)` reports before running this isolated block.

<!-- bookcheck: expect="temperature=21.5\n16" timeout=2 -->
```python runnable
text = "temperature=21.5"
encoded = text.encode("utf-8")
print(encoded.decode("utf-8"))
print(len(encoded))
```

You should observe the same text and `16`. ASCII characters use one UTF-8 byte here; that is not true for every character.

**Modify:** replace the value with `café`. Predict the character and byte counts first. **Hint:** compare `len(text)` with `len(text.encode("utf-8"))`. The explained solution is that `é` is one Python character but takes two UTF-8 bytes.

**Happy path:** both peers use UTF-8. **Edge case:** one Unicode character may span several bytes. **Recoverable error:** invalid bytes cause `UnicodeDecodeError`; catch it at the protocol boundary and reject the frame rather than guessing an encoding.

### 2. Addresses, names, and local-only experiments

`localhost` is a local name. IPv4 loopback is `127.0.0.1`; IPv6 loopback is `::1`. `socket.getaddrinfo()` returns candidates rather than assuming one family. The companion probe never contacts a public host.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/address_demo.py check=network:network-suite -->
```python source-ref
socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
```

Run from the repository root:

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/address_demo.py
```

The exact addresses and order are environment-dependent. The final line reports whether an IPv6 loopback bind worked. IPv4 remains the required fallback.

A server normally chooses a port before clients connect. Ports below 1024 may require privileges. Our two-terminal echo defaults to `65432`; automated tests bind port `0`, which asks the operating system for a free ephemeral port.

If you see `Address already in use`, choose another non-privileged port or use port `0` in coordinated code. Do not terminate an unrelated process blindly.

### 3. Your first blocking TCP exchange

TCP provides an ordered byte stream with connection setup and EOF. The lifecycle is:

1. Server: create → bind → listen → accept → receive/send → close.
2. Client: create → connect → send/receive → close.
3. Both sides use timeouts and context managers so failure also closes resources.

Predict which terminal waits first. Then run:

```text illustrative
# Terminal 1
python -B chapter-23-network-programming/examples/telemetry/echo.py server --port 65432

# Terminal 2, within thirty seconds
python -B chapter-23-network-programming/examples/telemetry/echo.py client --port 65432 --text "hello, network"
```

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/echo.py check=network:network-suite -->
```python source-ref
with socket.create_connection(("127.0.0.1", port), timeout=30.0) as connection:
    connection.sendall(text.encode("utf-8"))
```

Observe the echoed text and both processes ending. An empty `recv()` means EOF, not “try forever.” `sendall()` sends all supplied bytes or raises; it does not create message boundaries.

**Guided exercise:** add a `--text` value containing `å`. **TODO:** predict its UTF-8 byte count. **Hint:** the terminal displays text after the client has joined every received chunk. **Success:** the same text returns and both programs finish. The solution works because neither side decodes a partial chunk; the client decodes only the complete echoed byte sequence.

**Common mistake:** starting the client first yields `ConnectionRefusedError`. This is useful feedback: start the listener, verify the port, then retry. A timeout means the peer made no progress within the bound; report it and clean up rather than retrying forever.

### Essential checkpoint

You are ready to continue if you can explain why sockets use bytes, distinguish address from port, describe TCP's lifecycle, and complete the loopback echo. Your runnable product is the bounded two-terminal echo. Next, we add message boundaries and validation.

## Intermediate route — design a real message contract

### 4. TCP is not a message queue: frame it

One `sendall()` can arrive through several `recv()` calls, and several sends can arrive together. Predict what breaks if a server calls `json.loads(connection.recv(4096))`. Fragmented JSON is incomplete; coalesced JSON contains more than one document.

Our solution is newline-delimited JSON (**NDJSON**): one UTF-8 JSON object followed by `\n`. `NDJSONDecoder` keeps an incremental buffer, yields every complete line, and retains only the incomplete suffix. Content before the newline may contain at most 65,536 bytes. Byte 65,537 without a newline fails closed and clears the buffer.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/protocol.py check=network:network-suite -->
```python source-ref
messages = decoder.feed(chunk)  # zero, one, or several complete objects
```

The exact version-1 reading contract is:

| Field | Accepted value | Rejection rule |
|---|---|---|
| `version` | integer `1`, never `bool` | other versions → `unsupported_version` |
| `type` | string `reading` | wrong type → `invalid_message` |
| `sensor_id` | 1–64 ASCII chars matching `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` | missing/invalid → `invalid_message` |
| `sequence` | non-boolean integer `0..2**31-1` | duplicate/backward → `out_of_order` |
| `value` | finite non-boolean number `-1_000_000..1_000_000` | wrong type/range → `invalid_message` |

Exactly those five fields are required; unknown fields fail. An accepted reading returns:

```json illustrative
{"version":1,"type":"ack","sensor_id":"lab.temperature","sequence":7,"status":"accepted"}
```

Errors contain only `version`, `type`, stable `code`, and a bounded non-sensitive `message`. They never echo the whole input. Each connection tracks the last accepted sequence for at most 64 sensor IDs. A 65th ID returns `resource_limit` without eviction; an existing sensor can still advance. Validation happens before mutation, so every rejection is transactional.

#### Exercise: attack assumptions, not systems

Work only with the local decoder. Feed one valid frame in three fragments, then two frames in one chunk. **TODO:** assert zero/one/two returned objects. **Hint:** reuse `encode_frame()` and slice the bytes. **Success:** order is preserved and `buffered_bytes` returns to zero.

Next, change one field at a time: `sequence=True`, extra field, value `1_000_001`, duplicate sequence, then sensor 65. Predict the code. The explained solution is in `test_protocol.py`: schema and ranges use `invalid_message`, version uses `unsupported_version`, ordering uses `out_of_order`, and capacity uses `resource_limit`; state snapshots prove rejection does not mutate accepted state.

Run the focused evidence:

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p test_protocol.py -v
```

Malformed UTF-8, invalid JSON, partial EOF, and unsafe oversize framing close the connection because resynchronization is not trustworthy. A valid JSON frame with a schema error may receive an error and continue.

### 5. Compare UDP datagrams

UDP preserves each datagram boundary but does not promise delivery, uniqueness, or ordering. It has no TCP-style connection or EOF. Choose it only when the application can tolerate or repair those properties and keeps messages small.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/udp_demo.py check=network:network-suite -->
```python source-ref
sender.sendto(message, receiver_address)
data, sender_address = receiver.recvfrom(1024)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/udp_demo.py
```

The local happy path prints `received:temperature=21.5`. The edge case is a timeout when no datagram arrives. A real network may also lose, duplicate, or reorder data even when the local demo does not. Our TCP sequence/ack contract must not be promised by this UDP beacon.

**Guided decision:** choose transport for (a) a file transfer and (b) a replaceable game position update. **Hint:** ask whether every byte must arrive in order. A sound solution normally selects TCP for the file and may select UDP for replaceable updates, provided the game handles loss and size limits.

### 6. Robustness, logs, and deterministic tests

Treat peers as unreliable, not as enemies to attack. Bound time, bytes, clients, sensor state, and pending output. Log peer identity and a stable error category, never secrets or complete payloads. Retry only operations known to be safe, with a small attempt limit and backoff; this project does not auto-retry writes.

Tests use loopback, ephemeral ports, events or server readiness, short timeouts, and cleanup in `finally`. They do not use the Internet or fixed sleeps as synchronization. A timeout, disconnect mid-frame, refused connection, and invalid frame are expected recoverable paths.

**Common mistake:** catching bare `Exception` and continuing with damaged state. Catch the specific boundary error, log a bounded message, close when framing is unsafe, and keep accepted state unchanged.

### Intermediate checkpoint

You now have a tested sequential protocol core and a UDP comparison. You can explain fragmentation, coalescing, validation-before-mutation, and resource limits. The next route prevents one slow client from blocking everyone.

## Advanced route — bounded concurrency, asyncio, and TLS

### 7. Several clients with selectors

A sequential server waits inside one client's `recv()`. `selectors.DefaultSelector` asks the operating system which sockets are ready, so a slow client does not block a ready one. The companion implementation accepts at most 32 clients, keeps at most 65,536 incomplete bytes and 64 sensor entries per connection, and encodes only one pending response at a time.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
for key, mask in selector.select(timeout):
    # Accept, read, or continue a partial write only when ready.
    ...
```

A thread per connection is often easier to start with but adds thread lifecycle and shared-state synchronization. `socketserver` packages common synchronous patterns. We implement selectors here to make readiness and bounds visible; none is universally “best.”

**Prediction:** client A sends half a frame and pauses; client B sends a full frame. B should receive its ack first. The integration test proves this behavior and also exercises coalesced messages. Client 33 is closed in bounded time rather than joining an unlimited queue.

### 8. Apply asyncio streams and backpressure

Chapter 21 introduced coroutines and cancellation. Here `asyncio.start_server()` creates a task per accepted stream. `reader.read()` still returns arbitrary chunks, so it uses the same decoder. After each bounded `writer.write()`, `await writer.drain()` applies stream backpressure: if the transport buffer fills, the producer waits instead of growing output without limit.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/async_hub.py check=network:network-suite -->
```python source-ref
writer.write(encode_frame(response))
await asyncio.wait_for(writer.drain(), timeout=client_timeout)
```

Run the one-process demonstration:

```text illustrative
python -B -m chapter-23-network-programming.examples.telemetry.async_hub
```

Because a hyphenated directory is not a Python package name, the portable command is instead:

```text illustrative
cd chapter-23-network-programming/examples
python -B -m telemetry.async_hub
```

The first command is intentionally shown as a common mistake, not as runnable guidance. Use the second. It starts on an ephemeral loopback port, sends one reading, prints its ack, and closes.

Shutdown order matters: stop accepting, close client writers, await `wait_closed()`, cancel remaining handlers, and gather them. The main teaching path can use an `asyncio.Event` or `KeyboardInterrupt` on every supported platform; POSIX signal handlers are an optional platform-specific refinement.

**Guided exercise:** run two `send_readings()` calls with `asyncio.gather()`. **TODO:** give each a different sensor ID. **Hint:** keep one request pending until its response arrives. **Success:** both receive `accepted`, and `await hub.close()` leaves no handlers or writers. The solution reuses the same client helper tested in `test_network.py`.

### 9. Optional extension: verified TLS

Transport Layer Security (**TLS**) encrypts transport and lets the client verify the server certificate. It does not automatically authenticate the client or grant authorization. Tokens, mutual TLS, and access policy remain outside the base project.

The repository contains intentionally public teaching keys and certificates in `examples/certificates/`. They protect no real identity and must never be deployed. The client trusts only `lab-ca-cert.pem`; `ssl.create_default_context(cafile=...)` keeps certificate and hostname verification enabled. Never “fix” a verification failure with `CERT_NONE` or `check_hostname=False`.

Tests prove four offline cases: trusted CA plus `localhost` succeeds; wrong hostname, expired certificate, and a certificate from an untrusted CA fail closed. The valid fixture expires in July 2046, and a test warns when less than ten years remain.

**Recovery:** check the intended hostname, trust source, system/lab clock, and renewal. Encryption without identity verification does not establish who is at the other end.

### 10. Optional extension: IPv6

If the capability probe can bind `::1`, start the same async hub with `family=socket.AF_INET6`; otherwise record the explained skip and use IPv4. This tests local capability only and makes no public-network compatibility claim.

### 11. Run all evidence

From the repository root:

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
```

The first command executes 27 standard-library tests. The second runs generic book checks plus the explicitly requested `network:network-suite` domain check. The plugin is read-only and owns only localhost protocol/lifecycle behavior; the root tool owns Markdown, links, selectors, accessibility signals, localization structure, and hygiene.

## Capstone challenge

Evolve a sensor client while keeping the version-1 contract unchanged:

1. **Easy:** send three increasing readings for one sensor. TODO: assert three exact acks. Hint: start at sequence zero.
2. **Intermediate:** send a duplicate between valid readings. TODO: prove `out_of_order` does not block the later greater sequence. Hint: rejection must not mutate state.
3. **Advanced:** run two clients while a third stalls mid-frame, then shut down. TODO: prove the active clients progress and no task remains. Hint: use events and bounded `wait_for`, never a timing guess.
4. **Hero extension:** enable the trusted TLS context or conditional IPv6 path and state exactly what your machine tested.

An explained solution composes `AsyncTelemetryHub`, `send_readings()`, `ConnectionState`, and the existing tests; it does not create a second protocol. Test successful acks, one error envelope, server state, timeout cleanup, and `hub.close()`. Keep all addresses on loopback.

## Assessment rubric

Score each area from 0 (missing), 1 (partial), or 2 (demonstrated):

- Protocol: exact fields, framing, ack/error codes, and sequence semantics.
- Bounds: frame, time, 32 clients, 64 sensors, and one pending response.
- Recovery: malformed input, timeout, EOF, and rejection without partial mutation.
- Concurrency: another client progresses while one stalls.
- Security: loopback defaults, TLS trust and hostname verification, no secret logging.
- Verification: deterministic unit/integration tests and explicit local evidence.
- Cleanup and explanation: no orphaned resources, and you can explain each design choice.

Twelve or more points with no zero in protocol, bounds, or cleanup is a strong completion. A score is feedback, not a label; improve one observable behavior at a time.

## Final reflection and glossary

Can you explain why TCP needs framing, why validation precedes mutation, and why `drain()` and timeouts are resource controls? Which behavior did your machine actually test, and which deployment concern remains outside this local lab?

- **Backpressure:** slowing a producer when a consumer or buffer cannot keep up.
- **EOF:** end-of-file; on TCP, an empty read signals the peer ended its outgoing stream.
- **Ephemeral port:** a free non-privileged port selected by the operating system.
- **Framing:** rules that recover application-message boundaries from a byte stream.
- **Loopback:** a host's private path back to itself.
- **NDJSON:** one JSON value per newline-delimited frame.
- **TLS:** encrypted transport with certificate-based peer identity verification.

You have moved from “send some text” to a protocol that defines, bounds, observes, tests, and closes every conversation. That discipline transfers to HTTP services, message brokers, databases, and other networked systems.
