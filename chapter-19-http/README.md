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

---

## 1. `requests` client

If you don’t have `requests` installed, go back to Chapter 16 or run:

```bash
pip install requests
```

```python
import requests

resp = requests.get("https://httpbin.org/get")
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
```python
params = {"query": "python"}
resp = requests.get("https://httpbin.org/get", params=params)
```

---

## 2. POST JSON

```python
payload = {"email": "ada@example.com", "rol": "admin"}
resp = requests.post("https://httpbin.org/post", json=payload)
```

- `json=` serializes automatically.
- For APIs that require headers: `headers={"Authorization": "Bearer token"}`.

### Timeouts and error handling
```python
try:
    resp = requests.get("https://api.example.com", timeout=5)
    resp.raise_for_status()
except requests.exceptions.Timeout:
    print("La API tardó demasiado")
except requests.exceptions.HTTPError as exc:
    print("Error HTTP", exc.response.status_code)
```

---

## 3. Simple retries

```python
url = "https://httpbin.org/get"

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

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class EchoHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        payload = json.loads(data)
        respuesta = json.dumps({"ok": True, "received": payload}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(respuesta)

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), EchoHandler)
    print("Escuchando en http://localhost:8000")
    server.serve_forever()
```

- Useful to test clients without external APIs.

### Test the server with a client (in another terminal)
With the server running, execute this client:

```python
import requests

resp = requests.post("http://localhost:8000", json={"mensaje": "hola"})
print(resp.status_code)
print(resp.json())
```

Expected output:
```
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## Guided exercises (with TODOs)
1. **19-1 · Consume a public API**
   ```python
   # TODO 1: use requests.get to fetch random users
   # TODO 2: print name and email
   ```

2. **19-2 · POST with validation**
   ```python
   # TODO 1: send a payload to httpbin.org/post
   # TODO 2: verify the response JSON matches what you sent
   ```

3. **19-3 · Client vs server**
   ```python
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```

---

## Common mistakes
- Forgetting `timeout`: the call can hang forever.
- Not using `raise_for_status()` and assuming everything was fine.
- Hardcoding API keys in code instead of environment variables.

---

## Explained solutions
1. **Public API**: `requests.get("https://randomuser.me/api")` and parse `resp.json()`.
2. **POST**: compare `resp.json()["json"]` with your payload.
3. **Client/server**: run the server in one terminal, run the client in another, and watch the messages.

---

## Summary
You can now consume and expose basic APIs in Python, including error handling and timeouts.

## Closing reflection
These skills are a bridge to frameworks like Django REST Framework. Practice by building tiny services that talk to each other.
