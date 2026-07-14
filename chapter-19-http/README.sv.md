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
- Undantag, moduler, miljöer och JSON från kapitel 13–16.
- `requests` installerat i en virtuell miljö och två lokala terminaler; all obligatorisk trafik stannar på `localhost`.

## Förutsäg innan du kör
Innan du startar den lokala klienten: förutsäg statuskoden för health-routen och vilket undantag du bör se om ingen server lyssnar. Testa bara den avgränsade konfigurationen på `localhost` och jämför sedan båda resultaten med din förutsägelse.

---

## 1. Klient med `requests`

Installera vid behov via kapitel 16 eller med kommandot nedan. Starta den begränsade lokala servern i avsnitt 4 innan du kör klientexemplen; den obligatoriska vägen behöver inte Internet.

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
import socket
from urllib.parse import urlsplit

class EchoHandler(BaseHTTPRequestHandler):
    MAX_BODY = 1_000_000
    READ_TIMEOUT = 5

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in {"/health", "/search"}:
            self._send_json(200, {"ok": True})
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if urlsplit(self.path).path != "/echo":
            self._send_json(404, {"error": "not found"})
            return
        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "application/json required"})
            return

        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._send_json(411, {"error": "content length required"})
            return
        if not raw_length.isascii() or not raw_length.isdecimal():
            self._send_json(400, {"error": "invalid content length"})
            return
        normalized_length = raw_length.lstrip("0") or "0"
        maximum = str(self.MAX_BODY)
        if len(normalized_length) > len(maximum) or (
            len(normalized_length) == len(maximum) and normalized_length > maximum
        ):
            self._send_json(413, {"error": "payload too large"})
            return
        length = int(normalized_length)

        self.connection.settimeout(self.READ_TIMEOUT)
        try:
            data = self.rfile.read(length)
        except (TimeoutError, socket.timeout):
            self._send_json(408, {"error": "request body timeout"})
            return
        if len(data) != length:
            self._send_json(400, {"error": "incomplete request body"})
            return
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

Servern testar klienter utan externa API:er. Kontraktet accepterar bara de exakta GET-routes `/health` och `/search`, den exakta POST-routen `/echo` och mediatypen `application/json` (parametrar som charset är tillåtna). Före läsning kräver POST ett decimalt `Content-Length` inom `0..1_000_000`. Saknade, negativa, felaktiga eller för stora längder samt tidsbegränsade eller ofullständiga bodies får begränsade `4xx`-vägar.

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

### Verifiera request-gränsen

Den [begränsade HTTP-handlern och regressionstesterna](bounded_http.py) startar en tillfällig loopback-server och provar framgång, negativa, felaktiga och för stora längder, en okänd route och fel mediatyp:

```bash illustrative
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Kör kommandot från `chapter-19-http/`. Testet med negativ längd ska snabbt returnera `400`; det får aldrig nå `read(-1)` eller vänta på att klienten stänger anslutningen.

---

## Vägledda övningar (med TODO)

1. **19-1 · Använd det lokala API:t**

   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Ledtråd*: kör `EchoHandler` i en annan terminal och anropa `resp.raise_for_status()` före `resp.json()`.

2. **19-2 · POST med validering**

   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Ledtråd*: jämför `resp.json()["received"]` med din payload.

3. **19-3 · Klient och server**

   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Ledtråd*: testa normalfallet, saknad längd (411), negativ eller felaktig längd (400), för stor längd (413), fel mediatyp (415), fel route (404) och felaktig JSON (400); stoppa sedan servern med Ctrl-C.

---

## Vanliga misstag

- Glömma `timeout` och kunna fastna obegränsat.
- Inte anropa `raise_for_status()` och anta framgång.
- Hårdkoda API-nycklar i stället för environment variables.
- Anropa `read()` innan en icke-negativ övre gräns har validerats: ett negativt värde kan bli en obegränsad läsning.
- Acceptera alla routes eller mediatyper och därmed råka exponera ett bredare API än lektionen dokumenterar.

---

## Förklarade lösningar

1. **Lokalt API**: anropa `/health` med timeout, använd `raise_for_status()` och tolka `resp.json()`.
2. **POST**: jämför `resp.json()["received"]` med din payload.
3. **Klient/server**: kör den begränsade servern i en terminal och klienten i en annan. Verifiera vägarna 200, 400, 404, 411, 413 och 415. Validera route, mediatyp och decimalintervall innan exakt det deklarerade antalet byte läses med socket-timeout. Stoppa sedan med Ctrl-C så att `server_close()` frigör porten.

---

## Sammanfattning

Du kan konsumera och exponera grundläggande API:er med felhantering och timeout.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: GET/POST-klienter använder timeouts och servern returnerar lämpliga statuskoder.
- **Läsbarhet**: routes, payloadgränser och felsvar är tydliga.
- **Felhantering**: verifiera framgång, saknade, negativa, felaktiga eller för stora längder, fel route/mediatyp, felaktig JSON och återhämtning när tjänsten inte är tillgänglig.
- **Verifiering**: kör klient och server lokalt och bekräfta att porten frigörs efter avstängning.
- **Förklaring**: förklara varför obligatoriska övningar undviker publika tjänster.

## Avslutande reflektion

Färdigheterna leder vidare till Django REST Framework. Öva med små lokala tjänster som pratar med varandra.
