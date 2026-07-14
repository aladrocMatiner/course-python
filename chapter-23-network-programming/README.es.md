# Capítulo 23 · Programación de redes con Python

[English](README.md) · Español (actual) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

En este capítulo harás crecer un único proyecto de telemetría local: desde un primer eco TCP hasta una central asíncrona con recursos acotados. Necesitas Python 3.11 o posterior, pero no conocimientos previos de redes, Internet, permisos de administración ni paquetes externos.

Todos los servidores escuchan únicamente en loopback: `127.0.0.1` o, en la extensión IPv6, `::1`. No los cambies a una interfaz pública mientras aprendes. Escaneo, sniffing, raw sockets, spoofing, explotación, criptografía propia y despliegue público quedan fuera del capítulo.

## Resultados, prerrequisitos y rutas

Aprenderás a recorrer el camino de texto a bytes, elegir TCP o UDP, delimitar y validar un protocolo, atender varios clientes sin estado ilimitado, aplicar backpressure con `asyncio`, verificar identidad TLS y probar fallos y cierre.

Repasa solo lo necesario:

- [Streams y context managers del capítulo 13](../chapter-13-files/README.es.md): cierre determinista.
- [Excepciones del capítulo 14](../chapter-14-exceptions/README.es.md): recuperación de fallos esperados.
- [Pruebas automatizadas del capítulo 18](../chapter-18-testing/README.es.md): preparar, actuar y comprobar.
- [HTTP del capítulo 19](../chapter-19-http/README.es.md): HTTP es un protocolo de aplicación, no el transporte.
- [Logging del capítulo 20](../chapter-20-logging/README.es.md): diagnósticos útiles sin filtrar payloads.
- [`asyncio` del capítulo 21](../chapter-21-async/README.es.md): coroutines, tareas y cancelación.

| Ruta | Tiempo | Punto de partida | Resultado observable |
|---|---:|---|---|
| Esencial | 2 × 45–60 min | Funciones y excepciones | Eco TCP local explicado |
| Intermedia | 3 × 45–60 min | Checkpoint esencial | Protocolo secuencial probado y comparación UDP |
| Avanzada | 3–4 × 45–60 min | Checkpoint intermedio y capítulo 21 | Central asíncrona multicliente acotada |

TLS e IPv6 son extensiones avanzadas opcionales. Los checkpoints anteriores son útiles sin ellas.

## Ruta esencial — de un mensaje a un stream TCP

### 1. Vocabulario mínimo de red

Un **cliente** inicia una conversación; un **servidor** la espera. Un **host** es una máquina o entorno de red. El sistema de nombres de dominio (**DNS**) relaciona nombres y direcciones. Una **dirección IP** identifica una interfaz y un **puerto** selecciona un programa del host. Un **socket** es el extremo que ofrece el sistema operativo. Un **protocolo** reúne las reglas compartidas.

Piensa en una carta: la IP es el edificio, el puerto la habitación y el protocolo el formulario acordado. La analogía termina ahí: TCP transporta un stream ordenado de bytes, no sobres separados.

Las capas separan responsabilidades: IP mueve paquetes, TCP o UDP aporta semántica de transporte y HTTP o nuestra telemetría vive en la aplicación. Para consumir APIs vuelve al capítulo 19; aquí construiremos un protocolo pequeño para comprender el nivel inferior.

#### Predice, ejecuta y observa

Los sockets intercambian **bytes**. El texto requiere una codificación acordada. Predice `len(encoded)` antes de ejecutar:

<!-- bookcheck: expect="temperature=21.5\n16" timeout=2 -->
```python runnable
text = "temperature=21.5"
encoded = text.encode("utf-8")
print(encoded.decode("utf-8"))
print(len(encoded))
```

Verás el mismo texto y `16`. Aquí cada carácter ASCII ocupa un byte; no todos los caracteres cumplen eso.

**Modifica:** usa `café` y predice caracteres y bytes. **Pista:** compara `len(text)` y `len(text.encode("utf-8"))`. La solución se explica así: `é` es un carácter de Python, pero ocupa dos bytes UTF-8.

**Happy path:** ambos peers usan UTF-8. **Edge case:** un carácter puede ocupar varios bytes. **Error recuperable:** bytes inválidos producen `UnicodeDecodeError`; rechaza el frame en el límite del protocolo, no adivines la codificación.

### 2. Direcciones, nombres y pruebas locales

`localhost` es un nombre local. El loopback IPv4 es `127.0.0.1` y el IPv6 es `::1`. `socket.getaddrinfo()` devuelve candidatos y evita asumir una familia. El probe complementario nunca consulta un host público.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/address_demo.py check=network:network-suite -->
```python source-ref
socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
```

Desde la raíz del repositorio:

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/address_demo.py
```

Las direcciones y su orden dependen del entorno. La última línea indica si se pudo hacer bind a loopback IPv6; IPv4 es el fallback obligatorio.

Los puertos menores de 1024 pueden necesitar privilegios. El eco en dos terminales usa `65432`; los tests usan puerto `0` para que el sistema operativo elija un puerto efímero libre.

Si aparece `Address already in use`, escoge otro puerto no privilegiado o usa `0` en código coordinado. No finalices a ciegas un proceso ajeno.

### 3. Primer intercambio TCP bloqueante

TCP ofrece un stream ordenado de bytes, establecimiento de conexión y EOF. Su ciclo de vida es:

1. Servidor: crear → bind → listen → accept → recibir/enviar → cerrar.
2. Cliente: crear → connect → enviar/recibir → cerrar.
3. Ambos lados usan timeouts y context managers para que los recursos también se cierren al fallar.

Predice qué terminal espera primero y ejecuta:

```text illustrative
# Terminal 1
python -B chapter-23-network-programming/examples/telemetry/echo.py server --port 65432

# Terminal 2, antes de treinta segundos
python -B chapter-23-network-programming/examples/telemetry/echo.py client --port 65432 --text "hello, network"
```

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/echo.py check=network:network-suite -->
```python source-ref
with socket.create_connection(("127.0.0.1", port), timeout=30.0) as connection:
    connection.sendall(text.encode("utf-8"))
```

Observa el texto devuelto y el final de ambos procesos. Un `recv()` vacío significa EOF. `sendall()` envía todos los bytes o lanza una excepción, pero no crea fronteras entre mensajes.

**Ejercicio guiado:** envía un `--text` con `å`. **TODO:** predice sus bytes UTF-8. **Pista:** el cliente une todos los chunks antes de decodificar. **Éxito:** vuelve el mismo texto y ambos procesos terminan. La solución funciona porque no se decodifica un chunk parcial.

**Error común:** iniciar antes el cliente produce `ConnectionRefusedError`. Arranca el listener, verifica el puerto y reintenta. Un timeout indica falta de progreso: informa y limpia, sin reintentos infinitos.

### Checkpoint esencial

Debes poder explicar bytes, dirección frente a puerto, ciclo TCP y completar el eco loopback. Tu producto es el eco acotado en dos terminales. Ahora añadiremos fronteras y validación.

## Ruta intermedia — diseñar un contrato real

### 4. TCP no es una cola de mensajes: framing

Un `sendall()` puede llegar en varios `recv()` y varios envíos pueden llegar juntos. Predice el fallo de `json.loads(connection.recv(4096))`: JSON fragmentado está incompleto y JSON coalescido contiene varios documentos.

Usamos JSON delimitado por líneas (**NDJSON**): un objeto UTF-8 y `\n`. `NDJSONDecoder` conserva un buffer incremental, entrega cada línea completa y retiene solo el sufijo incompleto. Antes del salto se admiten 65.536 bytes; el byte 65.537 sin delimitador falla de forma cerrada.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/protocol.py check=network:network-suite -->
```python source-ref
messages = decoder.feed(chunk)  # cero, uno o varios objetos completos
```

Contrato exacto de lectura versión 1:

| Campo | Valor aceptado | Rechazo |
|---|---|---|
| `version` | entero `1`, nunca `bool` | otra versión → `unsupported_version` |
| `type` | string `reading` | otro tipo → `invalid_message` |
| `sensor_id` | 1–64 ASCII con `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` | ausente/inválido → `invalid_message` |
| `sequence` | entero no booleano `0..2**31-1` | duplicado/retroceso → `out_of_order` |
| `value` | número finito no booleano `-1_000_000..1_000_000` | tipo/rango → `invalid_message` |

Se exigen exactamente esos campos. Una aceptación responde:

```json illustrative
{"version":1,"type":"ack","sensor_id":"lab.temperature","sequence":7,"status":"accepted"}
```

Los errores contienen solo `version`, `type`, un `code` estable y un `message` acotado; nunca reflejan la entrada completa. Cada conexión conserva secuencia para un máximo de 64 sensores y solo sus 256 lecturas aceptadas más recientes. El sensor 65 devuelve `resource_limit` sin expulsar estado. Al alcanzar el límite del historial se descarta la observación más antigua, pero la secuencia sigue siendo correcta. Se valida antes de mutar: todo rechazo es transaccional.

#### Ejercicio: cuestiona supuestos, no sistemas

Trabaja solo con el decoder local. Divide un frame válido en tres partes y une dos frames en un chunk. **TODO:** comprueba cero/uno/dos objetos. **Pista:** usa `encode_frame()` y slices. **Éxito:** orden conservado y buffer final a cero.

Cambia después un campo: `sequence=True`, campo extra, valor `1_000_001`, secuencia duplicada y sensor 65. Predice el código. `test_protocol.py` explica la solución y usa snapshots para demostrar que un rechazo no muta el estado.

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p test_protocol.py -v
```

UTF-8/JSON inválido, EOF parcial y framing inseguro cierran la conexión porque no es fiable resincronizar. Un objeto JSON bien delimitado con schema inválido puede recibir error y continuar.

### 5. Comparar datagramas UDP

UDP conserva la frontera de cada datagrama, pero no promete entrega, unicidad ni orden. No tiene conexión ni EOF como TCP. Elígelo solo si la aplicación tolera o repara esas propiedades y mantiene mensajes pequeños.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/udp_demo.py check=network:network-suite -->
```python source-ref
sender.sendto(message, receiver_address)
data, sender_address = receiver.recvfrom(1024)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/udp_demo.py
```

El happy path local imprime `received:temperature=21.5`; el edge case es timeout sin datagrama. Una red real también puede perder, duplicar o reordenar. La baliza UDP no promete el contrato fiable de secuencia/ack de TCP.

**Decisión guiada:** elige transporte para un archivo y para una posición de juego reemplazable. **Pista:** pregunta si cada byte debe llegar en orden. Solución razonada: TCP para el archivo; UDP puede servir para updates reemplazables si el juego maneja pérdida y límites.

### 6. Robustez, logs y tests deterministas

Acota tiempo, bytes, clientes, sensores, historial retenido y salida pendiente. El selector cierra un peer tras un segundo sin progreso de lectura o escritura; ambos hubs conservan como máximo 256 observaciones aceptadas para inspección didáctica. Registra peer y categoría estable, nunca secretos ni payloads completos. Reintenta solo operaciones seguras con pocos intentos y backoff; este proyecto no reintenta escrituras automáticamente.

Los tests usan loopback, puertos efímeros, eventos/readiness, timeouts cortos y `finally`, no Internet ni sleeps fijos. Timeout, desconexión a medio frame, rechazo e input inválido son rutas recuperables esperadas.

**Error común:** capturar `Exception` y seguir con estado dañado. Captura el error de frontera concreto, registra un mensaje acotado, cierra si el framing es inseguro y no alteres estado aceptado.

### Checkpoint intermedio

Ya tienes un núcleo secuencial probado y una comparación UDP. Puedes explicar fragmentación, coalescing, validación antes de mutación y límites. Ahora impediremos que un cliente lento bloquee al resto.

## Ruta avanzada — concurrencia acotada, asyncio y TLS

### 7. Varios clientes con selectors

El servidor secuencial espera dentro de un `recv()`. `selectors.DefaultSelector` informa qué sockets están listos. La implementación acepta 32 clientes como máximo, 65.536 bytes incompletos, 64 sensores y 256 lecturas recientes por conexión; codifica una única respuesta pendiente y cierra el peer tras un segundo sin progreso.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
for key, mask in selector.select(timeout):
    # Acepta, lee o continúa una escritura parcial solo cuando está listo.
    ...
```

Un thread por conexión puede ser sencillo, pero añade ciclo de vida y sincronización. `socketserver` empaqueta patrones síncronos. Implementamos selectors para hacer visible readiness y límites; ninguna opción es siempre la mejor.

**Predicción:** A envía medio frame y pausa; B envía uno completo. B debe recibir antes el ack. El test de integración lo prueba, también con mensajes coalescidos. El cliente 33 se cierra en tiempo acotado.

### 8. Streams asyncio y backpressure

`asyncio.start_server()` crea una tarea por stream aceptado. `reader.read()` sigue devolviendo chunks arbitrarios y reutiliza el decoder. Después de cada `writer.write()` acotado, `await writer.drain()` aplica backpressure para no acumular salida ilimitada.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/async_hub.py check=network:network-suite -->
```python source-ref
writer.write(encode_frame(response))
await asyncio.wait_for(writer.drain(), timeout=client_timeout)
```

Error común por el guion del directorio:

```text illustrative
python -B -m chapter-23-network-programming.examples.telemetry.async_hub
```

Comando portable correcto:

```text illustrative
cd chapter-23-network-programming/examples
python -B -m telemetry.async_hub
```

El primero se muestra como error, no como instrucción ejecutable. El segundo crea puerto efímero, envía una lectura, muestra el ack y cierra.

Orden de cierre: dejar de aceptar, cerrar writers, esperar `wait_closed()`, cancelar handlers restantes y reunirlos. Un `asyncio.Event` o `KeyboardInterrupt` es el camino multiplataforma; señales POSIX son una ampliación opcional.

**Ejercicio:** ejecuta dos `send_readings()` con `asyncio.gather()`. **TODO:** sensor distinto por cliente. **Pista:** una petición queda pendiente hasta su respuesta. **Éxito:** ambos reciben `accepted` y `hub.close()` no deja handlers ni writers. La solución reutiliza el helper probado.

### 9. Extensión opcional: TLS verificado

Transport Layer Security (**TLS**) cifra y permite verificar el certificado del servidor. No autentica automáticamente al cliente ni concede autorización. Tokens, mTLS y políticas quedan fuera.

El servidor aplica también a la negociación y al cierre TLS su límite de cliente de un segundo. Así, un peer TCP que nunca envía ClientHello expira antes de que exista el handler de aplicación y no puede bloquear el cierre indefinidamente.

Las claves de `examples/certificates/` son fixtures públicos y nunca deben desplegarse. El cliente confía solo en `lab-ca-cert.pem`; `ssl.create_default_context(cafile=...)` conserva certificado y hostname. Nunca arregles un fallo con `CERT_NONE` o `check_hostname=False`.

Los tests offline cubren éxito para CA confiable + `localhost`, y fallo cerrado por hostname erróneo, expiración y CA no confiable. El certificado válido expira en julio de 2046; un test avisa con diez años de margen.

**Recuperación:** comprueba hostname, fuente de confianza, reloj y renovación. Cifrar sin verificar identidad no prueba quién está al otro lado.

### 10. Extensión opcional: IPv6

Si el probe puede enlazar `::1`, inicia la central con `family=socket.AF_INET6`; si no, registra el skip explicado y usa IPv4. Solo se comprueba capacidad local, no compatibilidad en redes públicas.

### 11. Ejecutar toda la evidencia

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
```

El primer comando ejecuta 33 tests de librería estándar. El segundo suma checks genéricos y `network:network-suite`. El plugin solo posee protocolo y lifecycle local; la herramienta raíz posee Markdown, links, selectores, señales de accesibilidad, estructura lingüística e higiene.

## Reto final

1. **Fácil:** tres lecturas crecientes de un sensor; TODO: tres acks exactos; pista: empieza en cero.
2. **Intermedio:** un duplicado entre lecturas válidas; prueba que `out_of_order` no impide la secuencia mayor posterior.
3. **Avanzado:** dos clientes activos y otro parado a medio frame; prueba progreso y cierre sin tareas, con eventos y `wait_for`, nunca una espera adivinada.
4. **Hero:** activa TLS confiable o IPv6 condicional y escribe exactamente qué probó tu máquina.

La solución combina `AsyncTelemetryHub`, `send_readings()`, `ConnectionState` y los tests existentes; no inventa otro protocolo. Comprueba acks, un error, estado, timeout y cierre siempre en loopback.

## Rúbrica de evaluación

Puntúa cada área con 0 (ausente), 1 (parcial) o 2 (demostrado):

- **Protocolo:** campos exactos, framing, códigos de ack/error y semántica de secuencia.
- **Límites:** frame, un segundo de inactividad del selector, 32 clientes, 64 sensores, 256 observaciones retenidas y una respuesta pendiente.
- **Recuperación:** entrada mal formada, timeout, EOF y rechazo sin mutación parcial.
- **Concurrencia:** otro cliente progresa mientras uno permanece bloqueado.
- **Seguridad:** valores predeterminados de loopback, confianza TLS y verificación del hostname, sin secretos en los logs.
- **Verificación:** pruebas unitarias y de integración deterministas y evidencia local explícita.
- **Limpieza y explicación:** no quedan recursos huérfanos y puedes explicar cada decisión de diseño.

Doce puntos o más, sin cero en protocolo, límites ni limpieza, es una finalización sólida. La puntuación orienta, no etiqueta: mejora un comportamiento observable cada vez.

## Reflexión final y glosario

¿Por qué TCP necesita framing? ¿Por qué validamos antes de mutar? ¿Por qué `drain()` y timeouts controlan recursos? Separa siempre lo probado localmente de los problemas de despliegue que aquí no verificamos.

- **Backpressure:** frenar al productor cuando consumidor o buffer no siguen el ritmo.
- **EOF:** fin del stream saliente del peer, indicado por lectura TCP vacía.
- **Puerto efímero:** puerto libre seleccionado por el sistema operativo.
- **Framing:** reglas para recuperar mensajes desde un stream de bytes.
- **Loopback:** camino privado de un host hacia sí mismo.
- **NDJSON:** un valor JSON por frame delimitado por salto de línea.
- **TLS:** transporte cifrado con verificación de identidad por certificado.

Has pasado de enviar texto a definir, acotar, observar, probar y cerrar cada conversación. Esa disciplina se transfiere a HTTP, brokers, bases de datos y otros sistemas conectados.
