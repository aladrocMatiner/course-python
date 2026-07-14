# teach-python-network-programming Specification

## Purpose
Define Chapter 23 as a progressive, local-first path from network fundamentals
and synchronous TCP and UDP to framing, concurrency, asyncio, TLS, resilience,
observability, testing, and an assessed telemetry capstone, with five-language
technical integration and separate human localization acceptance.

## Requirements
### Requirement: Progressive Network Programming Curriculum

The course SHALL provide a chapter 23 that teaches network programming from a zero-networking baseline through clearly labeled essential, intermediate, and advanced routes, while assuming the Python knowledge covered by earlier chapters and using Python 3.11 or later.

#### Scenario: Learner starts without networking knowledge

- **WHEN** a learner begins the chapter without prior networking experience
- **THEN** the chapter introduces client, server, host, DNS, IP address, port, socket, protocol, bytes, and transport layers before requiring socket code
- **AND** it provides a local first success before introducing framing or concurrency

#### Scenario: Learner advances without conceptual gaps

- **WHEN** a learner follows the chapter in order
- **THEN** each route states its prerequisites, estimated multi-session duration, and observable outcome and builds on previously executed work
- **AND** the learner evolves one telemetry project from a TCP echo to a framed protocol, multi-client service, asynchronous service, and integrated capstone

#### Scenario: Learner stops at a checkpoint

- **WHEN** a learner completes only the essential or intermediate checkpoint
- **THEN** the route ends with a runnable, useful result and a summary of what has been learned
- **AND** later material is clearly marked as the next level needed to complete the full chapter, while TLS and IPv6 are identified as optional project extensions

### Requirement: Synchronous TCP and UDP Labs

The chapter SHALL provide standard-library labs for address resolution, blocking TCP, and UDP that explain socket lifecycle and the distinct semantics of streams and datagrams.

#### Scenario: TCP echo round trip

- **WHEN** the learner starts the documented TCP server and client in separate terminals
- **THEN** they exchange bytes over loopback using a non-privileged configurable or ephemeral port
- **AND** both sides handle timeout, EOF, and deterministic cleanup

#### Scenario: UDP datagram exchange

- **WHEN** the learner runs the documented UDP exercise
- **THEN** the peers exchange local datagrams with `sendto` and `recvfrom`
- **AND** the lesson explains message boundaries, possible loss, duplication, reordering, size constraints, and when UDP is appropriate

#### Scenario: Address family varies by environment

- **WHEN** the operating system supports IPv6 loopback
- **THEN** the chapter demonstrates portable resolution with `getaddrinfo` and an IPv6 local path
- **AND** it provides an IPv4 loopback fallback when IPv6 is unavailable

### Requirement: Correct Application Protocol Framing

The chapter SHALL demonstrate that TCP is a byte stream and SHALL implement NDJSON framing with one UTF-8 JSON object per line, an incremental buffer, a 65,536-byte content limit before the newline, and an exact validated version-1 telemetry contract.

#### Scenario: Valid telemetry reading is received

- **WHEN** a frame contains exactly `version`, `type`, `sensor_id`, `sequence`, and `value`
- **THEN** `version` is integer 1, `type` is `reading`, `sensor_id` matches `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`, and sequence is a non-boolean integer within `[0,2**31-1]`
- **AND** value is a non-boolean finite JSON number within `[-1_000_000,1_000_000]`, with missing or unknown fields rejected

#### Scenario: Telemetry reading is accepted

- **WHEN** a valid reading has a sequence strictly greater than the last accepted sequence for that sensor on the connection
- **THEN** the hub records it and returns a version-1 `ack` containing the same sensor ID and sequence plus status `accepted`
- **AND** only the accepted message updates connection state

#### Scenario: Telemetry reading is rejected

- **WHEN** schema, type, range, version, duplicate, or out-of-order validation fails
- **THEN** the hub returns a bounded version-1 `error` with stable code `invalid_message`, `unsupported_version`, `out_of_order`, or `resource_limit` and a non-sensitive message
- **AND** does not echo the complete payload or mutate the last accepted state; a schema error may continue while unsafe framing/encoding errors close the connection

#### Scenario: Per-connection sensor state reaches its limit

- **WHEN** one connection has accepted readings for 64 distinct sensor IDs and supplies a valid reading for a 65th ID
- **THEN** the hub returns `resource_limit` without adding the ID or evicting accepted state
- **AND** a later valid reading for one of the existing 64 IDs can still be processed according to its sequence

#### Scenario: TCP message is fragmented

- **WHEN** one logical message arrives across multiple `recv` or stream reads
- **THEN** the decoder buffers input until exactly one complete frame can be reconstructed
- **AND** it does not assume that one send equals one receive

#### Scenario: Multiple messages are coalesced

- **WHEN** several frames arrive in a single read
- **THEN** the decoder yields each complete message separately and retains only the incomplete remainder

#### Scenario: NDJSON line is malformed or oversized

- **WHEN** a peer sends invalid UTF-8, invalid JSON, an incomplete line at EOF, or a 65,537th content byte without a newline
- **THEN** the service rejects it in a controlled and memory-bounded way
- **AND** returns or logs a non-sensitive diagnostic before safely closing or continuing according to the protocol

### Requirement: Concurrent and Asynchronous Networking

The chapter SHALL evolve the sequential server into a bounded multi-client design and an `asyncio` streams design, explaining their trade-offs and lifecycle.

#### Scenario: Multiple clients make progress

- **WHEN** at least two local clients connect and exchange valid framed messages
- **THEN** a slow client does not prevent the other client from receiving its response
- **AND** the server accepts at most 32 clients, tracks at most 64 sensor IDs per connection, bounds each incomplete input buffer to 65,536 bytes, permits one pending response per client, and rejects excess in bounded time

#### Scenario: Asynchronous writer experiences pressure

- **WHEN** the asynchronous server writes responses to a client
- **THEN** the implementation uses the streams backpressure mechanism and a bounded message size
- **AND** explains why unbounded buffering is unsafe

#### Scenario: Service is cancelled or interrupted

- **WHEN** the asynchronous service is cancelled or receives the documented shutdown action
- **THEN** it closes the listener, client tasks, readers/writers, and sockets in a deterministic order
- **AND** exits without orphaned tasks or unhandled cleanup warnings

### Requirement: Secure Resilient and Observable Networking

The chapter SHALL teach safe defaults, bounded failure handling, verified TLS, and useful diagnostics as part of the network design.

#### Scenario: Exercise runs with safe exposure

- **WHEN** a learner follows a server example without changing its configuration
- **THEN** the server binds only to loopback and uses a non-privileged port
- **AND** no essential exercise requires Internet access, administrative privileges, raw sockets, or a public listener

#### Scenario: Untrusted peer stalls or disconnects

- **WHEN** a peer stops sending, disconnects mid-frame, or exceeds a timeout or size limit
- **THEN** the service releases the associated resources within a bounded time
- **AND** logs a useful diagnostic without secrets or full sensitive payloads

#### Scenario: TLS peer is trusted

- **WHEN** the advanced TLS client connects with the documented laboratory trust material and expected hostname
- **THEN** certificate trust and hostname validation succeed before application data is exchanged
- **AND** the required CA, certificate, and intentionally public laboratory key fixtures are available offline in the repository

#### Scenario: TLS identity is invalid

- **WHEN** the certificate is untrusted, expired, or does not match the expected hostname
- **THEN** the client fails closed with an explained verification error
- **AND** the chapter does not recommend disabling certificate verification as a fix

#### Scenario: TLS authentication boundary is explained

- **WHEN** the learner completes the TLS section
- **THEN** the chapter explains that ordinary server TLS authenticates the server but not the client
- **AND** keeps client tokens, mTLS, and authorization outside the base project instead of implying that encryption provides them

### Requirement: Local-First Runnable Learning Assets

The chapter SHALL provide Python 3.11+ inline snippets and companion multi-file examples with exact commands, expected outcomes, bounded waits, cleanup instructions, and a standard-library validator for marked runnable Markdown blocks.

#### Scenario: Offline learner completes the core path

- **WHEN** a learner has Python and the repository but no Internet connection
- **THEN** they can complete the essential, intermediate, and advanced TCP, UDP, framing, concurrency, and asynchronous routes on loopback
- **AND** the TLS extension uses versioned fixtures while only IPv6 may be skipped with an explained platform capability check

#### Scenario: Requested port is unavailable

- **WHEN** an example encounters `Address already in use`
- **THEN** the chapter explains the error and provides a configurable or operating-system-assigned port strategy
- **AND** does not instruct the learner to terminate unrelated processes blindly

#### Scenario: Runnable example is copied or executed

- **WHEN** a Markdown block marked `runnable` or a companion example is run with Python 3.11 or later
- **THEN** it compiles and exhibits the documented output or behavior
- **AND** terminates within a documented timeout or shutdown procedure

#### Scenario: Documentation validation runs

- **WHEN** the root validator with the network plugin is executed, or the documented standalone fallback runs before the root gate is available
- **THEN** it rejects Python versions below 3.11, checks relative links, language selectors, and structural parity
- **AND** it executes `runnable` blocks with a bounded timeout and expected output, compiles `compile-only` blocks in memory, distinguishes TODO snippets, leaves no cache artifacts, and removes the fallback after equivalence-tested migration

### Requirement: Assessment and Integrated Capstone

The chapter SHALL include guided exercises and an evolving local telemetry project that assess both successful operation and important edge cases.

#### Scenario: Learner studies a networking concept

- **WHEN** a substantial subsection introduces a new concept
- **THEN** it provides objective/prerequisite, context, minimal theory, prediction, execution, observation, guided modification, and verification
- **AND** includes a happy path, edge case, recoverable error, normalized common mistake, explained solution, and reflection

#### Scenario: Learner practices incrementally

- **WHEN** the learner reaches a major topic
- **THEN** they receive a guided exercise with TODOs, hints, expected success criteria, and an explained solution
- **AND** the exercises progress from easy to intermediate and advanced

#### Scenario: Learner tests a network service

- **WHEN** the learner runs the documented test suite
- **THEN** unit and integration tests use loopback, ephemeral ports, deterministic coordination, timeouts, and cleanup
- **AND** cover happy paths plus fragmentation, coalescing, malformed or oversized input, timeout, and disconnect edge cases

#### Scenario: Learner completes the capstone

- **WHEN** the learner completes the final project
- **THEN** the telemetry hub serves up to 32 clients with the exact version-1 NDJSON schema, validation, sequence rules, at most 64 sensor states per connection, bounded buffers/output, timeouts, logging, and graceful shutdown
- **AND** trusted TLS mode is tested with repository fixtures while IPv6 mode is tested conditionally or skipped with an explained platform capability check

#### Scenario: Final project is assessed

- **WHEN** the learner reviews the completed telemetry hub
- **THEN** a rubric covers protocol correctness, framing, bounds, error recovery, concurrency, security, tests, observability, cleanup, and explanation
- **AND** the learner identifies what was tested locally and what remains an optional or unverified deployment concern

### Requirement: Multilingual Chapter Integration

The course SHALL publish the chapter in the five existing content languages and integrate it into all root indexes without changing existing chapter numbers.

#### Scenario: Reader discovers the chapter

- **WHEN** a reader opens any of `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md`, or `README.ar.md`
- **THEN** the index includes chapter 23 before later implemented chapters and the appendices and links to the matching language version
- **AND** preserves already implemented chapter 24 or 25 entries rather than replacing them

#### Scenario: Reader switches language

- **WHEN** a reader selects any other language from a chapter 23 variant
- **THEN** the link opens the same chapter in English, Spanish, Catalan, Swedish, or Arabic
- **AND** the Arabic document preserves the repository's right-to-left convention

#### Scenario: Technical content remains equivalent

- **WHEN** the five variants are compared
- **THEN** they preserve the same learning objectives, checkpoints, commands, code semantics, safety warnings, exercises, and assessment criteria

#### Scenario: Reader uses accessible Markdown

- **WHEN** a chapter variant is rendered
- **THEN** headings are hierarchical, links are descriptive, tables have simple headers, and meaningful visuals have alt text plus equivalent prose
- **AND** meaning does not depend only on color, position, or icons, while Arabic code and commands remain readable left-to-right inside the RTL wrapper

#### Scenario: Technical completion precedes human localization acceptance

- **WHEN** all five chapter documents, indexes, companion/domain checks, and automated structural checks pass
- **THEN** this technical capability may be implementation-complete while every content-equivalence and accessibility requirement remains normative
- **AND** no localized record becomes `accepted` until `maintain-multilingual-course-parity` records a current canonical audit, competent linguistic review, localized technical/pedagogical review, rendered-accessibility and applicable Arabic bidi review, plus required provenance evidence for material touched during localization

### Requirement: Cross-Chapter Continuity and Scope

The chapter SHALL reuse earlier course knowledge through explicit cross-links and SHALL keep transport programming distinct from subjects already covered elsewhere.

#### Scenario: Learner needs a prerequisite refresher

- **WHEN** the chapter uses streams, exceptions, automated testing, HTTP layering, logging, or `asyncio`
- **THEN** it links to chapters 13, 14, 18, 19, 20, or 21 in the reader's current language as appropriate
- **AND** briefly states what knowledge is expected before continuing

#### Scenario: HTTP boundary remains clear

- **WHEN** the chapter explains where HTTP fits in the network stack
- **THEN** it identifies HTTP as an application protocol over transport
- **AND** refers API consumption and `requests` practice to chapter 19 instead of reteaching them

#### Scenario: Unsafe or out-of-scope topic is considered

- **WHEN** the material mentions scanning, sniffing, raw sockets, spoofing, exploitation, custom cryptography, or public deployment
- **THEN** it marks the topic out of scope and does not provide operational offensive instructions
