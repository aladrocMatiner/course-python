# Public Chapter 23 TLS fixtures

These certificates and private keys are intentionally public teaching fixtures.
They protect no real identity and **must never be reused for deployment**.

- `lab-ca-cert.pem` trusts the valid localhost and deliberately expired leaves.
- `localhost-cert.pem` has SAN entries for `localhost`, `127.0.0.1`, and `::1`.
- `expired-cert.pem` expired in 2021 and exists only for a fail-closed test.
- `untrusted-cert.pem` is signed by a different CA, which is intentionally absent.

The valid fixture expires in July 2046. Regenerate it well before that date and
rerun the TLS tests. The companion tests load only these local files and never
contact the Internet.
