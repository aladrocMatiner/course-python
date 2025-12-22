# Capítulo 19 · HTTP y APIs básicas con Python

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

---

## 1. Cliente `requests`

Si no tienes `requests` instalado, vuelve al Capítulo 16 o ejecuta:

```bash
pip install requests
```

```python
import requests

resp = requests.get("https://httpbin.org/get")
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

- `json=` serializa automáticamente.
- Para APIs que requieren headers: `headers={"Authorization": "Bearer token"}`.

### Timeouts y manejo de errores
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

## 3. Reintentos simples

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

- El bloque `else` se ejecuta si no hiciste `break`.

---

## 4. Servidor local rápido

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

- Útil para probar tus clientes sin depender de APIs externas.

### Probar el servidor con un cliente (en otra terminal)
Con el servidor corriendo, ejecuta este cliente:

```python
import requests

resp = requests.post("http://localhost:8000", json={"mensaje": "hola"})
print(resp.status_code)
print(resp.json())
```

Salida esperada:
```
200
{'ok': True, 'received': {'mensaje': 'hola'}}
```

---

## Ejercicios guiados (con TODOs)
1. **19-1 · Consumir API pública**
   ```python
   # TODO 1: usa requests.get para obtener usuarios aleatorios
   # TODO 2: imprime nombre y correo
   ```

2. **19-2 · POST con validación**
   ```python
   # TODO 1: envía payload a httpbin.org/post
   # TODO 2: verifica que el response JSON coincida con lo enviado
   ```

3. **19-3 · Cliente vs servidor**
   ```python
   # TODO 1: levanta el servidor EchoHandler
   # TODO 2: crea un cliente que le envíe datos
   ```

---

## Errores comunes
- Olvidar `timeout`: la llamada cuelga indefinidamente.
- No usar `raise_for_status()` y asumir que todo salió bien.
- Exponer API keys en el código en lugar de variables de entorno.

---

## Explicación de soluciones
1. **API pública**: `requests.get("https://randomuser.me/api")` y parsear `resp.json()`.
2. **POST**: compara `resp.json()["json"]` con tu payload.
3. **Cliente/servidor**: lanza el servidor en una terminal, ejecuta el cliente en otra y observa los mensajes.

---

## Resumen
Ya sabes consumir y exponer APIs básicas con Python, incluyendo manejo de errores y timeouts.

## Reflexión final
Estas habilidades son el puente hacia frameworks como Django REST Framework. Practica construyendo pequeños servicios que hablen entre sí.
