# Kapitel 19 · HTTP och API:er med Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi gör GET/POST med `requests`, skickar JSON, hanterar statuskoder och bygger en minimal lokal server med `http.server`.

---

## GET
```python
import requests

resp = requests.get("https://httpbin.org/get")
print(resp.status_code)
print(resp.json())
```

---

## POST JSON
```python
payload = {"email": "noor@example.com", "rol": "admin"}
resp = requests.post("https://httpbin.org/post", json=payload)
```

---

## Lokal server (utan Internet)
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
```

---

## Sammanfattning
HTTP är “språket” mellan tjänster. Nästa kapitel: logging och konfiguration.
