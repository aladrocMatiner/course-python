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
Capítols previs recomanats: 13, 14, 16.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1. Client amb `requests`

Si no tens `requests`, torna al capítol 16 o executa:

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

- És útil per provar clients sense dependre d'APIs externes.

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

---

## Exercicis guiats (amb TODO)
1. **19-1 · Consumir l’API local**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

2. **19-2 · POST amb validació**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **19-3 · Client i servidor**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

---

## Errors habituals
- Oblidar `timeout`, cosa que pot deixar la petició bloquejada indefinidament.
- No utilitzar `raise_for_status()` i suposar que tot ha anat bé.
- Escriure claus d'API directament al codi en lloc d'usar variables d'entorn.

---

## Solucions explicades
1. **API local**: crida `/health` amb timeout, usa `raise_for_status()` i interpreta `resp.json()`.
2. **POST**: compara `resp.json()["received"]` amb el payload.
3. **Client/servidor**: verifica localment 200, 400 i 413 i atura el servidor amb Ctrl-C.

---

## Resum
Ara pots consumir i exposar APIs bàsiques amb Python, amb gestió d'errors i timeouts.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Aquestes habilitats són el pont cap a frameworks com Django REST Framework. Practica construint serveis petits que es comuniquin entre ells.
