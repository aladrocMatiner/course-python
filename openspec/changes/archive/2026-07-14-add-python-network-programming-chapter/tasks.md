## TASK BREAKDOWN

## Phase 1: Estructura y contratos didácticos

### Task 1.1: Congelar el temario y las fronteras con capítulos existentes

- **Objective:** Definir las rutas esencial, intermedia y avanzada, sus prerrequisitos, duración orientativa, producto observable y orden exacto antes de redactar contenido extenso.
- **Deliverables:** Esqueleto de headings en `chapter-23-network-programming/README.md`, mapa de evolución de la central de telemetría, microciclo didáctico común y enlaces a los capítulos 13, 14, 18, 19, 20 y 21.
- **Validation:** Cada requisito se asocia al menos a una subsección; cada ruta termina en un resultado ejecutable; cada subsección introduce un concepto principal mediante predecir → ejecutar → observar → modificar → comprobar; HTTP/`asyncio` se referencian sin repetir sus introducciones.
- **Risk:** Un temario excesivo puede ocultar la progresión; cada checkpoint debe terminar en un resultado ejecutable.
- **Scope:** S
- [x] 1.1 Congelar temario, prerrequisitos, checkpoints y trazabilidad con requisitos.

### Task 1.2: Diseñar los assets ejecutables

- **Objective:** Separar snippets pequeños de los laboratorios multiarchivo y definir una validación reproducible del Markdown.
- **Deliverables:** Assets/tests de TCP/NDJSON/UDP/async/TLS; si existe el gate raíz, `chapter-23-network-programming/tools/bookcheck_plugin.py` con `register(registry)` y solo checks de red; si no, `validate_docs.py`/`check_hygiene.py` standalone temporales con migración explícita.
- **Validation:** Cada asset tiene Python 3.11+, puerto/timeout/cierre/source ref; con root gate no se crean parsers/hygiene genéricos locales; si el capítulo llega primero, equivalence tests deben pasar antes de reemplazar los standalones por plugin y root CLI.
- **Risk:** Demasiados archivos aumentarían la carga cognitiva; solo los ejemplos multiarchivo deben salir del README.
- **Scope:** S
- [x] 1.2 Definir nombres, responsabilidades y comandos de los ejemplos complementarios.

## Phase 2: Ruta esencial y fundamentos síncronos

### Task 2.1: Escribir el modelo mental de red

- **Objective:** Enseñar desde cero cliente/servidor, host, DNS, IP, puerto, socket, protocolo, capas y texto frente a bytes.
- **Deliverables:** Secciones iniciales de `chapter-23-network-programming/README.md` con analogía, glosario mínimo, `encode`/`decode`, `localhost`, `getaddrinfo`, IPv4/IPv6 y puertos efímeros.
- **Validation:** Un lector puede explicar dónde encaja HTTP y resolver direcciones locales sin Internet con Python 3.11+; se ejecutan los paths IPv4 y, condicionalmente, IPv6 con skip explicado cuando no esté disponible; la subsección incluye su microciclo, happy path y edge case.
- **Scope:** M
- [x] 2.1 Redactar modelo mental, bytes, direcciones, resolución y laboratorio seguro.

### Task 2.2: Crear el primer cliente y servidor TCP

- **Objective:** Mostrar el ciclo de vida completo de sockets TCP bloqueantes con un intercambio local observable.
- **Deliverables:** Explicación y ejemplo cliente-servidor sobre `socket`, `bind`, `listen`, `accept`, `connect`, `sendall`, bucle `recv`, EOF, context managers y cierre limpio.
- **Validation:** El eco funciona en dos terminales sobre loopback, soporta un puerto configurable, maneja `ConnectionRefusedError`/timeout y ambos procesos terminan sin sockets huérfanos; la subsección incluye predicción, modificación guiada, error común y solución explicada.
- **Scope:** M
- [x] 2.2 Implementar y explicar el laboratorio de eco TCP síncrono.

### Task 2.3: Enseñar framing y un protocolo de aplicación

- **Objective:** Corregir la idea de que cada `recv()` corresponde a un mensaje y construir un protocolo sencillo pero seguro.
- **Deliverables:** Codec NDJSON UTF-8, buffer incremental y contrato exacto version/type/sensor_id/sequence/value, required/unknown-field policy, ack/error envelope, límite de 65,536 bytes y transiciones transaccionales; prefijo de longitud y orden de bytes quedan como comparación avanzada.
- **Validation:** Tests unitarios cubren fragmentación/coalescing, campos/tipos/rangos, unknown/missing, version, secuencia, 64/65 sensores, ack/error/resource_limit, UTF-8/JSON, EOF y 65,536/65,537 bytes; rechazos no mutan estado y el eco ingenuo sirve como predicción.
- **Risk:** Es el salto conceptual principal del capítulo; debe partir de un fallo reproducible del eco ingenuo.
- **Scope:** L
- [x] 2.3 Implementar framing, codec JSON, validación y casos límite.

### Task 2.4: Comparar UDP con TCP

- **Objective:** Enseñar datagramas y sus trade-offs sin presentarlos como una variante menor de TCP.
- **Deliverables:** Laboratorio local con `sendto`/`recvfrom`, explicación de límites, pérdida, duplicación, orden y criterios de elección.
- **Validation:** El intercambio conserva fronteras de datagrama, maneja timeout y el ejercicio exige predecir el resultado y justificar cuándo elegir TCP o UDP mediante un happy path y un edge case.
- **Scope:** M
- [x] 2.4 Crear la subsección y el laboratorio UDP.

## Phase 3: Ruta intermedia y avanzada

### Task 3.1: Añadir robustez y observabilidad

- **Objective:** Convertir los ejemplos básicos en servicios que reaccionen de forma predecible a fallos y peers no confiables.
- **Deliverables:** Secciones sobre timeouts, reintentos acotados, desconexión, tamaño máximo, límites de conexiones, cleanup y logging sin secretos ni payloads sensibles.
- **Validation:** Casos guiados de peer lento, conexión rechazada, mensaje inválido y desconexión liberan recursos, producen diagnósticos comprensibles y cierran con una solución explicada.
- **Scope:** M
- [x] 3.1 Documentar e implementar timeouts, límites, manejo de errores y logging.

### Task 3.2: Evolucionar hacia varios clientes

- **Objective:** Hacer visible el bloqueo del servidor secuencial y comparar soluciones concurrentes con sus costes.
- **Deliverables:** Central multi-cliente con `selectors.DefaultSelector` y límite de conexiones, más una comparación conceptual con thread-per-connection y `socketserver`.
- **Validation:** Al menos dos clientes progresan; límites 32/33 clientes y 64/65 sensores/conexión se aceptan/rechazan de forma acotada; cada cliente conserva <=65,536 bytes, <=64 sequence entries y una respuesta pendiente; el cierre no deja estado activo.
- **Risk:** Presentar todas las estrategias con igual profundidad diluiría el aprendizaje; solo `selectors` se implementa y las demás se comparan.
- **Scope:** L
- [x] 3.2 Implementar un servidor concurrente acotado y comparar alternativas.

### Task 3.3: Aplicar `asyncio` a sockets de alto nivel

- **Objective:** Reutilizar los fundamentos del capítulo 21 para crear cliente y servidor con streams asíncronos.
- **Deliverables:** Ejemplos con `asyncio.start_server`, `open_connection`, tareas por cliente, `reader`, `writer`, `drain`, timeouts, cancelación y `wait_closed`.
- **Validation:** Varios clientes concurrentes completan intercambios NDJSON; un `asyncio.Event` y `KeyboardInterrupt` proporcionan shutdown principal multiplataforma y cierran listener, tareas y writers sin warnings; señales POSIX quedan como nota opcional.
- **Scope:** L
- [x] 3.3 Crear y explicar el servicio asíncrono con backpressure y shutdown.

### Task 3.4: Añadir TLS verificado

- **Objective:** Mostrar cómo proteger el transporte sin enseñar atajos inseguros.
- **Deliverables:** Sección avanzada con `ssl` y fixtures PEM versionados para CA didáctica, `localhost`, certificado expirado y CA no confiable; claves marcadas como públicas/no reutilizables; trust store, hostname, distinción entre identidad de servidor y autenticación de cliente, y comandos de generación solo opcionales.
- **Validation:** El cliente correcto completa handshake e intercambio; CA no confiable, certificado expirado y hostname incorrecto fallan cerrados; los fixtures son PEM portables, no requieren herramientas específicas del sistema y se prueban en el entorno disponible; ningún ejemplo usa o recomienda `CERT_NONE`.
- **Risk:** El certificado válido caducará → emitirlo con al menos diez años de margen, documentar renovación y añadir un test que avise con antelación; la clave versionada debe estar inequívocamente marcada como fixture didáctico público.
- **Scope:** L
- [x] 3.4 Implementar el laboratorio TLS con verificación de identidad.

### Task 3.5: Construir el proyecto final y su suite de pruebas

- **Objective:** Integrar los conceptos del capítulo en un servicio local multi-cliente verificable.
- **Deliverables:** Central de telemetría asíncrona con contrato exacto NDJSON, framing, validación/estado transaccional, límites de frame/clientes/output, timeouts, logging, shutdown y pruebas bajo `chapter-23-network-programming/examples/`; modos TLS e IPv6 como extensiones.
- **Validation:** `python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v` cubre schema/rangos/secuencia/ack/error/resource_limit, 64/65 sensores, 32/33 clientes, framing, input inválido, timeout y cleanup sin Internet ni sleeps frágiles; TLS/IPv6 se ejecutan o registran skip justificado.
- **Scope:** L
- [x] 3.5 Implementar el capstone, criterios de evaluación y tests locales.

## Phase 4: Cierre pedagógico y localización

> **Frontera de ownership:** las tareas localizadas marcadas en esta change certifican autoría completa y verificación estructural/de dominio a nivel de implementación. No certifican aceptación humana lingüística, técnica/pedagógica localizada, accesibilidad renderizada, bidi ni procedencia. Esas tareas y transiciones de estado permanecen abiertas en `restore-multilingual-content-parity`.

### Task 4.1: Auditar ejercicios y apoyos de aprendizaje

- **Objective:** Confirmar y refinar el andamiaje incorporado durante cada tarea técnica, sin posponer la pedagogía hasta el final.
- **Deliverables:** Auditoría de implementación de objetivos/prerrequisitos, contexto, teoría mínima, mini aventura, microciclos, ejercicios fácil/medio/avanzado con TODOs/pistas, errores comunes, soluciones, checkpoints, rúbrica, reflexión y handoff de accesibilidad.
- **Validation:** Cada bloque principal contiene objetivo/contexto/teoría mínima/predicción/ejecución/observación/modificación/verificación, ejercicio, happy/edge/recovery, error normalizado y solución explicada; rutas respetan duración/producto y headings/links/tables/visuals son accesibles.
- **Scope:** L
- [x] 4.1 Auditar y refinar ejercicios, microciclos, soluciones y reflexión.

### Task 4.2: Crear la versión española

- **Objective:** Producir una traducción española completa, clara y técnicamente equivalente a la versión de referencia.
- **Deliverables:** `chapter-23-network-programming/README.es.md`.
- **Validation:** Paridad de autoría de objetivos, checkpoints, ejemplos, comandos, advertencias y ejercicios; enlaces de prerrequisitos apuntan a `README.es.md`; los bloques `runnable` conservan equivalencia verificable. La aceptación humana permanece pendiente en `maintain-multilingual-course-parity`.
- **Scope:** L
- [x] 4.2 Completar la autoría y revisión de implementación de la versión española.

### Task 4.3: Crear las versiones catalana, sueca y árabe

- **Objective:** Mantener la cobertura lingüística habitual del curso sin divergencia técnica.
- **Deliverables:** `README.ca.md`, `README.sv.md` y `README.ar.md`, incluyendo RTL en la versión árabe.
- **Validation:** Paridad de autoría de objetivos, headings, code fences, comandos, advertencias, ejercicios, edge cases, soluciones y rúbrica; enlaces localizados, estructura de accesibilidad, RTL y validación automatizada pasan. La doble revisión humana y la accesibilidad/bidi renderizados permanecen pendientes en `maintain-multilingual-course-parity`.
- **Risk:** Las traducciones son paralelizables, pero solo después de congelar los ejemplos.
- **Scope:** L por idioma
- [x] 4.3a Completar la autoría y revisión de implementación de la versión catalana.
- [x] 4.3b Completar la autoría y revisión de implementación de la versión sueca.
- [x] 4.3c Completar la autoría y revisión de implementación de la versión árabe con dirección RTL.

### Task 4.4: Integrar navegación e índices sin perder capítulos posteriores

- **Objective:** Insertar capítulo 23 y preservar cualquier capítulo posterior que ya haya sido implementado.
- **Deliverables:** Selectores de idioma del capítulo y enlaces del capítulo 23 en `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`.
- **Validation:** Cada índice abre el idioma correcto; selectors funcionan; no links rotos; English duplicates aligned; capítulos 24/25 se preservan si existen y el orden implementado es 23→24→25 antes de apéndices.
- **Scope:** S
- [x] 4.4 Actualizar los seis índices y verificar los cinco selectores del capítulo.

## Phase 5: Verificación final

### Task 5.1: Validar contenido y ejemplos

- **Objective:** Demostrar que los materiales funcionan en condiciones reproducibles y seguras.
- **Deliverables:** Suite `unittest`, contenido corregido y, según orden de changes, plugin `register(registry)` + root CLI o standalone temporal documentado.
- **Validation:** Root CLI/plugin cuando existe; nunca generic parser/hygiene duplicado. En transición, standalone con equivalence migration. En ambos: links/a11y/parity/RTL, TCP/UDP/32-client/async/TLS, IPv6 condicional, schema/transiciones, portability, diff/status limpio.
- **Risk:** IPv6 puede no estar disponible; registrar un skip justificado. TLS no puede omitirse porque los fixtures versionados eliminan la dependencia del sistema.
- **Scope:** M
- [x] 5.1 Ejecutar validaciones Markdown, Python, red local, seguridad y localización.

### Task 5.2: Trazar la implementación contra la spec

- **Objective:** Confirmar que ningún requisito o escenario de implementación quedó sin evidencia y que los gates humanos externos siguen expresamente pendientes.
- **Deliverables:** Revisión final de la checklist y de los escenarios de `teach-python-network-programming`.
- **Validation:** `openspec validate add-python-network-programming-chapter --strict`, trazabilidad requisito por requisito y estado pendiente verificable de las decisiones humanas en `restore-multilingual-content-parity`; completar esta checklist no significa aceptar esas revisiones.
- **Scope:** S
- [x] 5.2 Validar OpenSpec, cerrar trazabilidad y completar la checklist.
