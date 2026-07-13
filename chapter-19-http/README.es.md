# Capítulo 19 · HTTP y APIs básicas con Python

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Consumiremos APIs usando `requests`, enviaremos datos en JSON, manejaremos respuestas y errores HTTP, y construiremos un micro servidor local con `http.server`. Si no tienes Internet, podrás practicar igual con el servidor local.

## Orden pedagógico
1. **Repaso HTTP (verbos, códigos)**.
2. **Cliente con `requests`**.
3. **Enviar datos (JSON, headers)**.
4. **Manejo de errores y reintentos**.
5. **Servidor básico con `http.server`**.
6. **Buenas prácticas (timeouts, logging)**.

## Objetivos de aprendizaje
- Realizar peticiones GET/POST y analizar respuestas.
- Enviar payloads JSON y autenticación simple.
- Manejar errores HTTP con mensajes amigables.
- Crear un servidor local mínimo para simular endpoints.

## Por qué importa
Los backends se comunican mediante HTTP. Saber consumir y exponer APIs es esencial antes de usar frameworks más avanzados.

### Mini aventura
Piensa en HTTP como el servicio postal de Internet. Cada petición es una carta o paquete con dirección, remitente y sello. Aprender a enviar y recibir cartas te convierte en cartero digital capaz de conectar aplicaciones como si fueran ciudades diferentes.

## Prerrequisitos
Capítulos previos recomendados: 13, 14, 16.
Usa CPython 3.11+ en un entorno local desechable y mantén los datos, secretos y servicios fuera de sistemas reales.

---

## 1. Cliente `requests`

Si no tienes `requests` instalado, vuelve al Capítulo 16 o ejecuta:

```bash illustrative
pip install requests
```

```python illustrative
import requests

resp = requests.get("http://localhost:8000/health", timeout=5)
print(resp.status_code)
print(resp.json())
```

- `status_code` indica éxito (200) o error (4xx, 5xx).
- `.json()` decodifica el cuerpo como JSON.

### Mini teoría de HTTP en 60 segundos
- **GET**: “dame información” (leer).
- **POST**: “aquí tienes datos” (crear/enviar).
- **200**: ok.
- **400**: algo en tu petición está mal.
- **404**: no existe esa ruta.
- **500**: el servidor falló.

No hace falta memorizarlo todo hoy: basta con reconocer “200 es bueno” y “4xx/5xx es un problema”.

Si no tienes Internet ahora mismo, no pasa nada: ve directo a la sección 4 y prueba el servidor local.

### GET con parámetros
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

- `json=` serializa automáticamente.
- Para APIs que requieren headers: `headers={"Authorization": "Bearer token"}`.

### Timeouts y manejo de errores
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

## 3. Reintentos simples

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

- El bloque `else` se ejecuta si no hiciste `break`.

---

## 4. Servidor local rápido

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

- Útil para probar tus clientes sin depender de APIs externas.

### Probar el servidor con un cliente (en otra terminal)
Con el servidor corriendo, ejecuta este cliente:

```python illustrative
import requests

resp = requests.post("http://localhost:8000/echo", json={"mensaje": "hola"}, timeout=5)
print(resp.status_code)
print(resp.json())
```

Salida esperada:
```text illustrative
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## Ejercicios guiados (con TODOs)
1. **19-1 · Consumir la API local**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

2. **19-2 · POST con validación**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

3. **19-3 · Cliente vs servidor**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

---

## Errores comunes
- Olvidar `timeout`: la llamada cuelga indefinidamente.
- No usar `raise_for_status()` y asumir que todo salió bien.
- Exponer API keys en el código en lugar de variables de entorno.

---

## Explicación de soluciones
1. **API local**: llama a `/health` con timeout, usa `raise_for_status()` y analiza `resp.json()`.
2. **POST**: compara `resp.json()["received"]` con tu payload.
3. **Cliente/servidor**: verifica localmente 200, 400 y 413 y detén el servidor con Ctrl-C.

---

## Resumen
Ya sabes consumir y exponer APIs básicas con Python, incluyendo manejo de errores y timeouts.

## Punto de control y rúbrica
- **Corrección**: el resultado cumple el contrato de la unidad.
- **Legibilidad**: nombres y responsabilidades se entienden a la primera.
- **Errores**: se prueban un caso válido, un límite y una recuperación.
- **Verificación**: los ejemplos y ejercicios se ejecutan en un entorno limpio.
- **Explicación**: puedes justificar las decisiones y sus riesgos.

## Reflexión final
Estas habilidades son el puente hacia frameworks como Django REST Framework. Practica construyendo pequeños servicios que hablen entre sí.
