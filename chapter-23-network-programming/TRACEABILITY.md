# Chapter 23 requirement traceability

This map records implementation evidence for
`teach-python-network-programming`. Generic Markdown, navigation, localization,
accessibility and hygiene checks are owned by `tools/validate_book.py`; the
chapter plugin owns only bounded localhost network behavior.

| Requirement | Implementation evidence | Verification evidence |
|---|---|---|
| Progressive Network Programming Curriculum | Five localized READMEs; staged address → TCP/UDP → framing → selectors → asyncio → TLS routes | Root structural/parity gate; chapter checkpoints and rubric |
| Synchronous TCP and UDP Labs | `examples/telemetry/address_demo.py`, `echo.py`, `udp_demo.py` | `DatagramAndSelectorTests` round-trip, EOF, timeout and IPv6 cases |
| Correct Application Protocol Framing | `examples/telemetry/protocol.py` with NDJSON decoder, transactional sensor state, and a 256-reading retention ring | `DecoderTests` and `ContractTests`: fragmentation/coalescing, 65,536/65,537 bytes, schema/version/sequence/value boundaries, 64/65 sensors, long-session retention |
| Concurrent and Asynchronous Networking | `selector_hub.py`, `async_hub.py` with bounded clients, buffers, 256-observation hub history, one-second selector idle expiry, and lifecycle cleanup | Two-client progress, slow input, stalled output timeout, 32/33 limit, 32 idle partial peers plus replacement capacity, long session, cleanup and shutdown tests |
| Secure Resilient and Observable Networking | Loopback defaults, bounded errors/timeouts including pre-handler TLS negotiation, `tls.py`, declared didactic PEM fixtures | Trusted localhost plus hostname, expired, untrusted, and stalled-ClientHello failure paths; error-envelope redaction tests |
| Local-First Runnable Learning Assets | Standard-library companion sources; ephemeral ports; offline certificate fixtures | 33 isolated `unittest` cases including empty UDP datagrams; public `SSLSocket.getpeercert()` expiry evidence; network plugin `network:network-suite` |
| Assessment and Integrated Capstone | Guided TODOs/hints, recovery exercises, telemetry capstone and observable rubric in every locale | Five documents share the same classified evidence sequence and tested source identities |
| Multilingual Chapter Integration | `README.md` plus ES/CA/SV/AR, one Arabic RTL wrapper, six root index entries | Root links/selectors/RTL/fence/accessibility checks; English mirror byte equality |
| Cross-Chapter Continuity and Scope | Localized prerequisites and explicit distinction from HTTP; no raw-packet/public-target exercise | Root link validation and localhost-only domain suite |

Acceptance commands:

```sh illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
openspec validate add-python-network-programming-chapter --strict
git diff --check
```
