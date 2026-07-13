# Chapter 19 · HTTP and Basic APIs with Python

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll consume APIs using `requests`, send JSON data, handle HTTP responses and errors, and build a tiny local server with `http.server`. If you don’t have Internet access, you can still practice with the local server.

## Learning path
1. **HTTP recap (verbs, status codes)**.
2. **Client with `requests`**.
3. **Sending data (JSON, headers)**.
4. **Errors and simple retries**.
5. **Basic server with `http.server`**.
6. **Good practices (timeouts, logging)**.

## Learning objectives
- Make GET/POST requests and analyze responses.
- Send JSON payloads and simple authentication.
- Handle HTTP errors with friendly messages.
- Create a minimal local server to simulate endpoints.

## Why it matters
Backends communicate through HTTP. Knowing how to consume and expose APIs is essential before using advanced frameworks.

### Mini adventure
Think of HTTP as the Internet’s postal service. Each request is a letter/package with an address, sender, and stamp. Learning to send and receive letters makes you a “digital mail carrier” that connects apps like different cities.

## Prerequisites
- Exceptions, modules, environments, and JSON from Chapters 13–16.
- `requests` installed in a virtual environment and two local terminals; all required traffic stays on `localhost`.

---

## 1. `requests` client

If you don’t have `requests` installed, go back to Chapter 16 or run the following command. Start the bounded local server in section 4 before executing the client examples; the required path does not need Internet access.

```bash illustrative
pip install requests
```

```python illustrative
import requests

resp = requests.get("http://localhost:8000/health", timeout=5)
print(resp.status_code)
print(resp.json())
```

- `status_code` tells you success (200) or error (4xx, 5xx).
- `.json()` decodes the body as JSON.

### 60‑second HTTP theory
- **GET**: “give me information” (read).
- **POST**: “here is data” (create/send).
- **200**: ok.
- **400**: something in your request is wrong.
- **404**: route not found.
- **500**: server error.

You don’t need to memorize everything now. Just remember: 200 is good; 4xx/5xx means a problem.

If you don’t have Internet right now, that’s fine: jump to section 4 and try the local server.

### GET with query parameters
```python illustrative
params = {"query": "python"}
resp = requests.get("http://localhost:8000/search", params=params, timeout=5)
```

---

## 2. POST JSON

```python illustrative
payload = {"email": "noor@example.com", "rol": "admin"}
resp = requests.post("http://localhost:8000/echo", json=payload, timeout=5)
```

- `json=` serializes automatically.
- For APIs that require headers: `headers={"Authorization": "Bearer token"}`.

### Timeouts and error handling
```python illustrative
try:
    resp = requests.get("http://localhost:8000/health", timeout=5)
    resp.raise_for_status()
except requests.exceptions.Timeout:
    print("The API took too long")
except requests.exceptions.HTTPError as exc:
    print("Error HTTP", exc.response.status_code)
```

---

## 3. Simple retries

```python illustrative
url = "http://localhost:8000/health"

for intento in range(3):
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        break
    except requests.exceptions.RequestException as exc:
        print("Fallo", exc)
else:
    raise RuntimeError("Servicio no disponible")
```

- The `else` block runs if you never hit `break`.

---

## 4. Quick local server

```python illustrative
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class EchoHandler(BaseHTTPRequestHandler):
    MAX_BODY = 1_000_000

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/health") or self.path.startswith("/search"):
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid content length"})
            return
        if length > self.MAX_BODY:
            self._send_json(413, {"error": "payload too large"})
            return
        data = self.rfile.read(length)
        try:
            payload = json.loads(data)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "invalid json"})
            return
        self._send_json(200, {"ok": True, "received": payload})

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), EchoHandler)
    print("Escuchando en http://localhost:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Deteniendo servidor")
    finally:
        server.server_close()
```

- Useful to test clients without external APIs.

### Test the server with a client (in another terminal)
With the server running, execute this client:

```python illustrative
import requests

resp = requests.post("http://localhost:8000/echo", json={"mensaje": "hola"}, timeout=5)
print(resp.status_code)
print(resp.json())
```

Expected output:
```text illustrative
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## Guided exercises (with TODOs)
1. **19-1 · Consume the local API**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Hint*: run `EchoHandler` in another terminal and call `resp.raise_for_status()` before `resp.json()`.

2. **19-2 · POST with validation**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Hint*: compare `resp.json()["received"]` with your payload.

3. **19-3 · Client vs server**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Hint*: test the happy path, malformed JSON (400), and an oversized declared body (413), then stop the server with Ctrl-C.

---

## Common mistakes
- Forgetting `timeout`: the call can hang forever.
- Not using `raise_for_status()` and assuming everything was fine.
- Hardcoding API keys in code instead of environment variables.

---

## Explained solutions
1. **Local API**: call `/health` with a five-second timeout, use `raise_for_status()`, and parse `resp.json()`.
2. **POST**: compare `resp.json()["received"]` with your payload.
3. **Client/server**: run the bounded server in one terminal and the client in another. Verify 200, 400, and 413 paths, then stop it with Ctrl-C so `server_close()` releases the port.

---

## Summary
You can now consume and expose basic APIs in Python, including error handling and timeouts.

## Checkpoint and rubric
- **Correctness**: GET/POST clients use timeouts and the server returns appropriate status codes.
- **Readability**: routes, payload limits, and error responses are explicit.
- **Error handling**: verify success, malformed JSON, oversized input, and unavailable-service recovery.
- **Verification**: run client and server locally, then confirm the port is released after shutdown.
- **Explanation**: explain why required exercises avoid public services.

## Closing reflection
These skills are a bridge to frameworks like Django REST Framework. Practice by building tiny services that talk to each other.
