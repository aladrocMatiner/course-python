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
- Excepciones, módulos, entornos y JSON de los capítulos 13–16.
- `requests` instalado en un entorno virtual y dos terminales locales; todo el tráfico requerido permanece en `localhost`.

## Predice antes de ejecutar
Antes de iniciar el cliente local, predice el código de estado de la ruta de salud y la excepción que deberías ver si ningún servidor está escuchando. Prueba solo la configuración acotada en localhost y compara después ambos resultados con tu predicción.

---

## 1. Cliente `requests`

Si no tienes `requests` instalado, vuelve al capítulo 16 o ejecuta el siguiente comando. Inicia el servidor local acotado de la sección 4 antes de ejecutar los ejemplos del cliente; el recorrido obligatorio no necesita Internet.

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

- Resulta útil para probar clientes sin APIs externas. El contrato solo acepta las rutas GET exactas `/health` y `/search`, la ruta POST exacta `/echo` y el tipo de medio `application/json` (se permiten parámetros como el charset). Antes de leer, POST exige un `Content-Length` decimal en `0..1_000_000`. Los cuerpos sin longitud, con longitud negativa, mal formada o excesiva, agotados por tiempo o incompletos siguen rutas `4xx` acotadas.

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

### Verificar la frontera de la petición
El [handler HTTP acotado y sus pruebas de regresión](bounded_http.py) inicia un servidor efímero en loopback y comprueba el éxito, longitudes negativas, mal formadas y excesivas, una ruta desconocida y un tipo de medio incorrecto:

```bash illustrative
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Ejecuta el comando desde `chapter-19-http/`. La prueba de longitud negativa debe devolver `400` enseguida; nunca debe alcanzar `read(-1)` ni esperar a que el cliente cierre la conexión.

---

## Ejercicios guiados (con TODOs)
1. **19-1 · Consumir la API local**
   ```python todo
   # TODO 1: use requests.get to fetch http://localhost:8000/health with timeout=5
   # TODO 2: verify status 200 and print the JSON
   ```
   *Pista*: ejecuta `EchoHandler` en otra terminal y llama a `resp.raise_for_status()` antes de `resp.json()`.

2. **19-2 · POST con validación**
   ```python todo
   # TODO 1: send a payload to http://localhost:8000/echo
   # TODO 2: verify the response JSON matches what you sent
   ```
   *Pista*: compara `resp.json()["received"]` con el payload enviado.

3. **19-3 · Cliente vs servidor**
   ```python todo
   # TODO 1: run the EchoHandler server
   # TODO 2: create a client that sends it data
   ```
   *Pista*: prueba el camino feliz, longitud ausente (411), negativa o mal formada (400), excesiva (413), tipo de medio incorrecto (415), ruta incorrecta (404) y JSON mal formado (400); después detén el servidor con Ctrl-C.

---

## Errores comunes
- Olvidar `timeout`: la llamada cuelga indefinidamente.
- No usar `raise_for_status()` y asumir que todo salió bien.
- Exponer API keys en el código en lugar de variables de entorno.
- Llamar a `read()` antes de validar una longitud no negativa y acotada: un valor negativo puede convertirse en una lectura sin límite.
- Aceptar cualquier ruta o tipo de medio y exponer por accidente una API más amplia que la documentada.

---

## Explicación de soluciones
1. **API local**: llama a `/health` con timeout, usa `raise_for_status()` y analiza `resp.json()`.
2. **POST**: compara `resp.json()["received"]` con tu payload.
3. **Cliente/servidor**: ejecuta el servidor acotado en una terminal y el cliente en otra. Verifica los caminos 200, 400, 404, 411, 413 y 415. Valida ruta, tipo de medio y rango decimal antes de leer exactamente los bytes declarados con un timeout de socket. Después detenlo con Ctrl-C para que `server_close()` libere el puerto.

---

## Resumen
Ya sabes consumir y exponer APIs básicas con Python, incluyendo manejo de errores y timeouts.

## Punto de control y rúbrica
- **Corrección**: los clientes GET/POST usan timeouts y el servidor devuelve códigos de estado apropiados.
- **Legibilidad**: rutas, límites de payload y respuestas de error son explícitos.
- **Errores**: verifica éxito, longitudes ausentes, negativas, mal formadas o excesivas, ruta o tipo de medio incorrectos, JSON mal formado y recuperación si el servicio no está disponible.
- **Verificación**: ejecuta cliente y servidor localmente y confirma que el puerto queda libre tras detenerlo.
- **Explicación**: explica por qué los ejercicios obligatorios evitan servicios públicos.

## Reflexión final
Estas habilidades son el puente hacia frameworks como Django REST Framework. Practica construyendo pequeños servicios que hablen entre sí.
