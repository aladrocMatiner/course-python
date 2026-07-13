# Kapitel 19 · HTTP och grundläggande API:er med Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi konsumerar API:er med `requests`, skickar JSON, hanterar HTTP-svar och fel och bygger en liten lokal server med `http.server`. Utan Internet kan du fortfarande genomföra den lokala delen.

## Lärväg

1. **HTTP-repetition**: verb och statuskoder.
2. **Klient med `requests`**.
3. **JSON och headers**.
4. **Fel och begränsade retries**.
5. **Lokal server med `http.server`**.
6. **Timeouts och logging**.

## Lärandemål

- Göra GET/POST och analysera svar.
- Skicka JSON-payloads och enkel autentisering.
- Hantera HTTP-fel med vänliga meddelanden.
- Skapa en minimal lokal endpoint-simulator.

## Varför det spelar roll

Backends kommunicerar via HTTP. Du behöver förstå konsumtion och exponering före avancerade frameworks.

### Miniäventyr

HTTP är Internets posttjänst. Varje request är ett brev med adress och innehåll; som digital brevbärare kopplar du samman applikationer.

## Förkunskaper
Rekommenderade tidigare kapitel: 13, 14, 16.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Klient med `requests`

Installera vid behov via kapitel 16 eller:

```bash illustrative
pip install requests
```

```python illustrative
import requests

resp = requests.get("http://localhost:8000/health", timeout=5)
print(resp.status_code)
print(resp.json())
```

- `status_code` visar framgång 200 eller fel 4xx/5xx.
- `.json()` avkodar bodyn som JSON.

### HTTP-teori på 60 sekunder

- **GET** läser information.
- **POST** skickar eller skapar data.
- **200** betyder ok, **400** felaktig request, **404** okänd route och **500** serverfel.

Du behöver inte memorera allt. Kom ihåg 200 kontra problemserierna 4xx/5xx. Utan Internet går du direkt till den lokala servern i avsnitt 4.

### GET med query-parametrar

```python illustrative
params = {"query": "python"}
resp = requests.get("http://localhost:8000/search", params=params, timeout=5)
```

---

## 2. POST med JSON

```python illustrative
payload = {"email": "noor@example.com", "rol": "admin"}
resp = requests.post("http://localhost:8000/echo", json=payload, timeout=5)
```

- `json=` serialiserar automatiskt.
- API-headers kan exempelvis vara `headers={"Authorization": "Bearer token"}`; riktiga tokens ska komma från säker konfiguration.

### Timeouts och felhantering

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

## 3. Enkla retries

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

Loopens `else` körs om `break` aldrig nås.

---

## 4. Snabb lokal server

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

Servern testar klienter utan externt API.

### Testa i en annan terminal

Med servern igång:

```python illustrative
import requests

resp = requests.post("http://localhost:8000/echo", json={"mensaje": "hola"}, timeout=5)
print(resp.status_code)
print(resp.json())
```

Förväntad utdata:

```text illustrative
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## Vägledda övningar (med TODO)

1. **19-1 · Använd det lokala API:t**

   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **19-2 · POST med validering**

   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **19-3 · Klient och server**

   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

---

## Vanliga misstag

- Glömma `timeout` och kunna fastna obegränsat.
- Inte anropa `raise_for_status()` och anta framgång.
- Hårdkoda API-nycklar i stället för environment variables.

---

## Förklarade lösningar

1. **Lokalt API**: anropa `/health` med timeout, använd `raise_for_status()` och tolka `resp.json()`.
2. **POST**: jämför `resp.json()["received"]` med din payload.
3. **Klient/server**: verifiera 200, 400 och 413 lokalt och stoppa servern med Ctrl-C.

---

## Sammanfattning

Du kan konsumera och exponera grundläggande API:er med felhantering och timeout.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Färdigheterna leder vidare till Django REST Framework. Öva med små lokala tjänster som pratar med varandra.
