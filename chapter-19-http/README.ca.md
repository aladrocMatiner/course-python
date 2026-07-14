# Capítol 19 · HTTP i APIs bàsiques amb Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Consumirem APIs amb `requests`, enviarem dades JSON, gestionarem respostes i errors HTTP i construirem un servidor local petit amb `http.server`. Si no tens accés a Internet, podràs practicar igualment amb el servidor local.

## Itinerari d'aprenentatge
1. **Repàs d'HTTP: verbs i codis d'estat**.
2. **Client amb `requests`**.
3. **Enviar dades: JSON i headers**.
4. **Errors i reintents senzills**.
5. **Servidor bàsic amb `http.server`**.
6. **Bones pràctiques: timeouts i logging**.

## Objectius d'aprenentatge
- Fer peticions GET i POST i analitzar-ne les respostes.
- Enviar payloads JSON i autenticació senzilla.
- Gestionar errors HTTP amb missatges entenedors.
- Crear un servidor local mínim per simular endpoints.

## Per què és important
Els backends es comuniquen mitjançant HTTP. Saber consumir i exposar APIs és essencial abans de treballar amb frameworks avançats.

### Miniaventura
Imagina HTTP com el servei postal d'Internet. Cada petició és una carta o paquet amb adreça, remitent i segell. Aprendre a enviar i rebre aquestes cartes et converteix en un «carter digital» que connecta aplicacions com si fossin ciutats diferents.

## Prerequisits
- Excepcions, mòduls, entorns i JSON dels capítols 13–16.
- `requests` instal·lat en un entorn virtual i dos terminals locals; tot el trànsit obligatori es manté a `localhost`.

## Prediu abans d'executar
Abans d'iniciar el client local, prediu el codi d'estat de la ruta de salut i l'excepció que hauries de veure si no hi ha cap servidor escoltant. Prova només la configuració acotada a localhost i compara després tots dos resultats amb la predicció.

---

## 1. Client amb `requests`

Si no tens `requests`, torna al capítol 16 o executa l'ordre següent. Inicia el servidor local acotat de la secció 4 abans d'executar els exemples del client; el recorregut obligatori no necessita Internet.

```bash illustrative
pip install requests
```

```python illustrative
import requests

resp = requests.get("http://localhost:8000/health", timeout=5)
print(resp.status_code)
print(resp.json())
```

- `status_code` indica èxit (200) o error (4xx, 5xx).
- `.json()` descodifica el cos com a JSON.

### Teoria HTTP en 60 segons
- **GET**: «dona'm informació», és a dir, lectura.
- **POST**: «aquí tens dades», és a dir, crear o enviar.
- **200**: correcte.
- **400**: alguna cosa de la petició és incorrecta.
- **404**: la ruta no existeix.
- **500**: error del servidor.

No cal memoritzar-ho tot ara. Recorda només que 200 sol indicar èxit i que 4xx/5xx indica un problema.

Si ara no tens Internet, no passa res: ves a la secció 4 i prova el servidor local.

### GET amb paràmetres de consulta
```python illustrative
params = {"query": "python"}
resp = requests.get("http://localhost:8000/search", params=params, timeout=5)
```

---

## 2. POST amb JSON

```python illustrative
payload = {"email": "noor@example.com", "rol": "admin"}
resp = requests.post("http://localhost:8000/echo", json=payload, timeout=5)
```

- `json=` serialitza les dades automàticament.
- Si una API demana headers, pots usar `headers={"Authorization": "Bearer token"}`.

### Timeouts i gestió d'errors
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

## 3. Reintents senzills

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

- El bloc `else` s'executa si mai no s'ha arribat al `break`.

---

## 4. Servidor local ràpid

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

- És útil per provar clients sense APIs externes. El contracte només accepta les rutes GET exactes `/health` i `/search`, la ruta POST exacta `/echo` i el tipus de mitjà `application/json` (s'hi permeten paràmetres com el charset). Abans de llegir, POST exigeix un `Content-Length` decimal dins `0..1_000_000`. Els cossos sense longitud, amb longitud negativa, mal formada o excessiva, esgotats per temps o incomplets segueixen camins `4xx` acotats.

### Provar el servidor amb un client en un altre terminal
Amb el servidor actiu, executa aquest client:

```python illustrative
import requests

resp = requests.post("http://localhost:8000/echo", json={"mensaje": "hola"}, timeout=5)
print(resp.status_code)
print(resp.json())
```

Sortida esperada:
```text illustrative
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

### Verificar el límit de la petició
El [handler HTTP acotat i les seves proves de regressió](bounded_http.py) inicia un servidor efímer de loopback i comprova l'èxit, longituds negatives, mal formades i excessives, una ruta desconeguda i un tipus de mitjà incorrecte:

```bash illustrative
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Executa l'ordre des de `chapter-19-http/`. La prova de longitud negativa ha de retornar `400` immediatament; mai no ha d'arribar a `read(-1)` ni esperar que el client tanqui la connexió.

---

## Exercicis guiats (amb TODO)
1. **19-1 · Consumir l’API local**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Pista*: executa `EchoHandler` en un altre terminal i crida `resp.raise_for_status()` abans de `resp.json()`.

2. **19-2 · POST amb validació**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Pista*: compara `resp.json()["received"]` amb el payload enviat.

3. **19-3 · Client i servidor**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Pista*: prova el camí feliç, longitud absent (411), negativa o mal formada (400), excessiva (413), tipus de mitjà incorrecte (415), ruta incorrecta (404) i JSON mal format (400); després atura el servidor amb Ctrl-C.

---

## Errors habituals
- Oblidar `timeout`, cosa que pot deixar la petició bloquejada indefinidament.
- No utilitzar `raise_for_status()` i suposar que tot ha anat bé.
- Escriure claus d'API directament al codi en lloc d'usar variables d'entorn.
- Cridar `read()` abans de validar una longitud no negativa i acotada: un valor negatiu pot convertir-se en una lectura sense límit.
- Acceptar qualsevol ruta o tipus de mitjà i exposar accidentalment una API més àmplia que la documentada.

---

## Solucions explicades
1. **API local**: crida `/health` amb timeout, usa `raise_for_status()` i interpreta `resp.json()`.
2. **POST**: compara `resp.json()["received"]` amb el payload.
3. **Client/servidor**: executa el servidor acotat en un terminal i el client en un altre. Verifica els camins 200, 400, 404, 411, 413 i 415. Valida la ruta, el tipus de mitjà i l'interval decimal abans de llegir exactament els bytes declarats amb un timeout de socket. Després atura'l amb Ctrl-C perquè `server_close()` alliberi el port.

---

## Resum
Ara pots consumir i exposar APIs bàsiques amb Python, amb gestió d'errors i timeouts.

## Punt de control i rúbrica
- **Correcció**: els clients GET/POST utilitzen timeouts i el servidor retorna codis d'estat adequats.
- **Llegibilitat**: les rutes, els límits del payload i les respostes d'error són explícits.
- **Errors**: verifica l'èxit, longituds absents, negatives, mal formades o excessives, ruta o tipus de mitjà incorrectes, JSON mal format i recuperació si el servei no està disponible.
- **Verificació**: executa client i servidor localment i confirma que el port queda lliure després d'aturar-lo.
- **Explicació**: explica per què els exercicis obligatoris eviten serveis públics.

## Reflexió final
Aquestes habilitats són el pont cap a frameworks com Django REST Framework. Practica construint serveis petits que es comuniquin entre ells.
