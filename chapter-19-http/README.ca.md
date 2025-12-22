# Capítol 19 · HTTP i APIs bàsiques amb Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Consumirem APIs amb `requests`, enviarem JSON, gestionarem respostes i errors HTTP, i muntarem un micro servidor local amb `http.server`. Si no tens Internet, podràs practicar igual amb el servidor local.

## Objectius d’aprenentatge
- Fer peticions GET/POST i analitzar respostes.
- Enviar payloads JSON i headers.
- Gestionar errors amb missatges clars i `timeout`.
- Crear un servidor local mínim per simular endpoints.

---

## Client amb `requests`
```bash
pip install requests
```

```python
import requests

resp = requests.get("https://httpbin.org/get")
print(resp.status_code)
print(resp.json())
```

---

## POST JSON
```python
import requests

payload = {"email": "ada@example.com", "rol": "admin"}
resp = requests.post("https://httpbin.org/post", json=payload)
print(resp.status_code)
```

---

## Servidor local ràpid
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

---

## Resum
Ja saps consumir i exposar APIs bàsiques amb Python i gestionar errors i `timeouts`. Això és el pont cap a frameworks com Django REST Framework.
