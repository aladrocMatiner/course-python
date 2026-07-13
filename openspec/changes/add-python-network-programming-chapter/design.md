## Context

El repositorio es un curso Markdown para estudiantes jóvenes y principiantes, con 22 capítulos y cinco variantes lingüísticas por capítulo. Los ejemplos son pequeños y ejecutables; cada lección incluye objetivos, contexto, teoría mínima, ejercicios con TODOs, errores comunes, soluciones explicadas y reflexión final.

Los capítulos 19 y 21 introducen HTTP y `asyncio`, respectivamente, pero el curso no contiene material sobre sockets, TCP, UDP, DNS, framing o TLS. El capítulo 1 recomienda Python 3.11 o posterior. La nueva capability debe cubrir ese vacío como una miniunidad de varias sesiones, no como una lectura única, y sin depender de infraestructura externa.

## ASSUMPTIONS

- Assumption: “OpenStack” en la petición se refiere a una proposal de OpenSpec.
- Assumption: “desde cero” significa desde cero en redes; el alumnado ya ha recorrido los fundamentos de Python del curso.
- Assumption: el contenido se añadirá como capítulo 23 para no renumerar ni romper los capítulos existentes.
- Assumption: `README.md` seguirá siendo la versión inglesa por defecto y se mantendrán las variantes española, catalana, sueca y árabe.
- Assumption: `README.en.md`, aunque duplica el índice inglés, debe actualizarse junto con `README.md` para evitar deriva.
- Assumption: Python 3.11 o posterior será la baseline, coherente con la recomendación del capítulo 1; la ruta IPv4 se diseñará con APIs portables y comandos documentados para Windows, macOS y Linux.
- Assumption: la implementación comenzará solo después de aprobar esta proposal.

## Goals / Non-Goals

### Goals

- Crear una progresión comprensible desde el primer socket hasta servicios concurrentes y asíncronos robustos.
- Mantener todos los laboratorios esenciales reproducibles en `localhost`, sin Internet ni privilegios administrativos.
- Enseñar corrección de protocolos: bytes, lecturas parciales, framing, validación, límites y cierre ordenado.
- Integrar seguridad, observabilidad y testing como parte del diseño, no como apéndices opcionales.
- Conservar la estructura pedagógica y la cobertura multilingüe del curso.

### Non-Goals

- Repetir el consumo de APIs HTTP con `requests` o la teoría básica de `async`/`await`.
- Enseñar frameworks web/RPC, WebSockets, QUIC o sistemas distribuidos.
- Enseñar escaneo de puertos o redes, captura o manipulación de paquetes, raw sockets, ARP, spoofing o técnicas de explotación.
- Profundizar en NAT, routing, firewalls, administración de sistemas o despliegue de servicios en redes públicas.
- Diseñar criptografía o desactivar la validación TLS para hacer funcionar un ejemplo.

## ARCHITECTURE SNAPSHOT

- Component map:
  - `chapter-23-network-programming/README.md`: contenido técnico inglés de referencia.
  - `chapter-23-network-programming/README.{es,ca,sv,ar}.md`: traducciones con los mismos objetivos, ejemplos y criterios de evaluación.
  - `chapter-23-network-programming/examples/`: laboratorios multiarchivo y evolución de la central de telemetría que no resulten legibles como snippets aislados.
  - `chapter-23-network-programming/examples/tests/`: pruebas `unittest` del codec/framing y pruebas de integración en loopback.
  - `chapter-23-network-programming/examples/certificates/`: CA, certificados y claves exclusivamente didácticos para casos TLS válido, no confiable, expirado y hostname incorrecto.
  - `chapter-23-network-programming/tools/bookcheck_plugin.py`: checks de red mediante `register(registry)` cuando existe el gate raíz; si el capítulo llega primero, `validate_docs.py`/`check_hygiene.py` son fallbacks temporales retirados tras equivalence tests.
  - `README*.md`: descubrimiento del capítulo desde los seis índices raíz.
  - `openspec/changes/add-python-network-programming-chapter/specs/teach-python-network-programming/spec.md`: requisitos y escenarios de aceptación.
- Key boundaries:
  - El capítulo 19 conserva HTTP y APIs; el capítulo 23 explica transporte y protocolos propios, y remite a HTTP como ejemplo de protocolo de aplicación.
  - El capítulo 21 conserva los fundamentos de `asyncio`; el capítulo 23 los aplica mediante streams, timeouts, cancelación, backpressure y shutdown.
  - Toda la ruta aceptada usa la librería estándar, incluido `unittest`; `pytest` puede aparecer solo como adaptación opcional enlazada al capítulo 18.
  - Los servidores se enlazan a loopback por defecto y nunca requieren exposición pública.
- Learning flow:
  - Ruta esencial (2 sesiones de 45–60 min): modelo mental y bytes → direcciones y resolución → TCP síncrono; resultado: eco local explicado.
  - Ruta intermedia (3 sesiones de 45–60 min): NDJSON y validación → UDP → robustez y `unittest`; resultado: central de telemetría secuencial probada.
  - Ruta avanzada (3–4 sesiones de 45–60 min): varios clientes → streams `asyncio` → backpressure y shutdown → TLS; resultado: central de telemetría asíncrona, con TLS/IPv6 como extensiones verificables.
  - Cada subsección introduce un solo concepto principal mediante el ciclo predecir → ejecutar → observar → modificar → comprobar.
- Runtime flow:
  - Sensor local → socket de loopback → decoder NDJSON con límite de 64 KiB por línea → validación de mensaje versionado → central de telemetría → respuesta NDJSON; logs y tests observan el ciclo sin registrar secretos ni dejar recursos abiertos.

## Capstone Protocol Contract

- Cada frame es un único objeto JSON UTF-8 terminado por `\n`; el límite de 65,536 bytes incluye el contenido anterior al delimitador. El decoder conserva como máximo ese buffer por cliente y rechaza EOF parcial, UTF-8/JSON inválido o un byte adicional sin delimitador.
- Una lectura válida contiene exactamente `{"version": 1, "type": "reading", "sensor_id": ..., "sequence": ..., "value": ...}`. No faltan ni sobran campos.
- `version` es el entero JSON 1 y `type` es el string `"reading"`. `sensor_id` es ASCII, tiene 1–64 caracteres y cumple `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`. `sequence` es un entero no booleano en `[0, 2**31-1]`. `value` es un número JSON no booleano, finito y situado en `[-1_000_000, 1_000_000]`.
- En cada conexión, `sequence` debe crecer estrictamente para un mismo `sensor_id`; duplicados o retrocesos producen error y no mutan la última lectura aceptada. Se conservan como máximo 64 IDs de sensor distintos por conexión; un 65.º ID produce `resource_limit` sin crear estado. La sección UDP explica que un datagrama no ofrece esta sesión/ack fiable y no promete corregir pérdida o reordenación.
- Una aceptación responde `{"version":1,"type":"ack","sensor_id":...,"sequence":...,"status":"accepted"}`. Un rechazo responde `{"version":1,"type":"error","code":...,"message":...}` con code estable (`invalid_message`, `unsupported_version`, `out_of_order` o `resource_limit`) y mensaje no sensible, sin reflejar el payload completo.
- Un error de schema sobre un frame válido permite continuar; framing, UTF-8/JSON o tamaño inválido envía error solo cuando sea seguro y cierra la conexión. Ningún rechazo muta estado.
- El capstone acepta como máximo 32 clientes simultáneos y 64 sensores distintos por conexión, procesa una lectura/respuesta por cliente antes de leer la siguiente y espera `drain()`; no mantiene colas o diccionarios ilimitados. El cliente 33 o sensor 65 recibe un cierre/rechazo acotado y explicado.

## Decisions

### Decision: un capítulo con tres rutas progresivas

El capítulo tendrá subsecciones numeradas agrupadas como esencial, intermedia y avanzada, con la duración y el producto observable definidos en el mapa anterior. Completar una ruta produce un resultado útil, pero completar el capítulo entero incluye las tres; solo TLS e IPv6 son extensiones avanzadas opcionales del proyecto. El contenido está pensado para varias sesiones y no para una sola lectura.

Alternatives considered:

- Dos capítulos separados: reduciría la longitud individual, pero añadiría navegación, traducciones y una frontera artificial entre framing, concurrencia y seguridad.
- Un apéndice avanzado: haría que robustez, seguridad y testing pareciesen secundarios cuando forman parte del comportamiento correcto de red.

### Decision: ejemplos local-first y seguros por defecto

Los ejemplos esenciales usarán `127.0.0.1` o `::1` cuando el sistema lo permita, puertos configurables o asignados con `bind(..., 0)`, timeouts y limpieza determinista. IPv6 tendrá fallback documentado si no está disponible.

Alternatives considered:

- APIs o servidores públicos: son fáciles de mostrar, pero introducen conectividad, disponibilidad, privacidad y resultados no reproducibles.
- Bind a `0.0.0.0`: facilita conexiones remotas, pero expone accidentalmente los ejercicios en redes compartidas.

### Decision: enseñar TCP como stream antes del protocolo de aplicación

El primer eco TCP servirá como motivación, no como patrón final. Inmediatamente después se demostrará que un `recv()` no equivale a un mensaje y se implementará NDJSON: un objeto JSON UTF-8 por línea, buffer incremental y límite de 64 KiB antes del delimitador. Un prefijo de longitud y el orden de bytes de red se explicarán únicamente como ampliación avanzada comparativa.

Alternatives considered:

- Usar solo mensajes cortos de eco: oculta lecturas parciales y produce una comprensión incorrecta que falla al avanzar.
- Prefijo de longitud como primera estrategia: es robusto, pero introducir `struct` y orden de bytes al mismo tiempo aumenta la carga cognitiva.

### Decision: una central de telemetría como hilo conductor

El proyecto no aparecerá de golpe al final. El eco de la ruta esencial evolucionará en la ruta intermedia hacia una central secuencial que recibe lecturas NDJSON validadas; la ruta avanzada la convertirá en servicio multi-cliente asíncrono. UDP servirá para comparar una baliza de telemetría sin garantías, y TLS/IPv6 serán extensiones del mismo dominio.

Alternatives considered:

- Chat multiusuario: es motivador, pero añade broadcast, estado compartido y sincronización que distraen de los contratos de red.
- Proyectos independientes por sección: permiten ejemplos pequeños, pero obligan a reconstruir contexto y ocultan la evolución arquitectónica.

### Decision: microciclo pedagógico dentro de cada subsección

Cada tarea de contenido deberá incluir objetivo y contexto, teoría mínima, una predicción antes de ejecutar, ejemplo observable, modificación guiada, happy path, edge case, error común y solución explicada. La fase pedagógica final será una auditoría de coherencia, no el momento de añadir por primera vez el andamiaje.

### Decision: ejemplos externos solo para laboratorios multiarchivo

Los ejemplos pequeños permanecerán en Markdown, siguiendo la convención del curso. Los pares cliente-servidor completos, el codec reutilizable, la central de telemetría y sus tests vivirán en `examples/` para poder ejecutarlos y verificarlos sin copiar grandes bloques manualmente.

Los fences autocontenidos y seguros llevarán la marca `runnable`; el gate raíz o fallback temporal los ejecutará en un directorio temporal con timeout y salida esperada. Los bloques que necesitan otra terminal o infraestructura se marcarán `compile-only`, se compilarán en memoria y enlazarán a un companion example cubierto por `unittest`. Los TODOs incompletos tendrán su propia marca y no se presentarán como ejecutables. El owner genérico también comprobará Python 3.11+, enlaces locales, selectores y paridad sin crear caches.

Si `add-book-quality-gates` se aprueba e implementa antes que este capítulo, `chapter-23-network-programming/tools/bookcheck_plugin.py` expondrá el API versionado `register(registry)` y registrará solo checks de red; el validador raíz poseerá Markdown, links, paridad, accesibilidad e higiene. Si aún no existe, `validate_docs.py`/`check_hygiene.py` serán standalone temporales; al aparecer el gate raíz, tests de equivalencia precederán su eliminación y migración al plugin, sin conservar parsers genéricos duplicados.

Alternatives considered:

- Todo inline: mantiene la estructura histórica, pero dificulta probar y mantener ejemplos concurrentes de varios archivos.
- Todo en archivos externos: mejora la automatización, pero separa demasiado pronto la explicación del código para principiantes.

### Decision: TLS verificado como ruta avanzada

La sección TLS usará `ssl` con fixtures PEM versionados bajo `examples/certificates/`: una CA didáctica, certificado/clave para `localhost` con SAN correcto y validez de al menos diez años desde su creación, un certificado expirado y material firmado por una CA no confiable. Las claves estarán marcadas como públicas, locales, exclusivamente didácticas y prohibidas para cualquier despliegue. Así, los casos válido, expirado, hostname incorrecto y CA no confiable serán reproducibles offline y multiplataforma sin exigir `openssl`; los comandos de generación quedarán como nota opcional para quien quiera explorar.

TLS autenticará al servidor ante el cliente. El capítulo explicará que eso no autentica al cliente y dejará tokens, mTLS y autorización fuera del proyecto base. La desactivación de validación no se presentará como solución.

Alternatives considered:

- Omitir TLS: dejaría incompleta una ruta que pretende llegar a un nivel avanzado.
- Mostrar `CERT_NONE`: simplifica el laboratorio, pero enseña un antipatrón inseguro.

## Risks / Trade-offs

- El capítulo puede superar ampliamente la longitud media del curso → dividirlo en checkpoints esencial/intermedio/avanzado, usar ejemplos externos para el código largo y mantener teoría mínima.
- La paridad completa es un estándar más estricto que varias traducciones resumidas existentes → congelar primero ejemplos y comandos, no traducir identificadores, automatizar la comparación de headings/code fences/enlaces y presupuestar revisión completa por idioma.
- Los tests de red pueden ser frágiles → usar puertos efímeros, coordinación determinista, timeouts cortos y cleanup en `finally`/fixtures; evitar esperas arbitrarias como mecanismo de sincronización.
- TLS y IPv6 varían entre sistemas → documentar prerrequisitos, mantener IPv4 como ruta obligatoria y tratar IPv6/TLS local como rutas avanzadas con fallos explicados.
- Concurrencia puede sobrecargar a principiantes → empezar con servidor secuencial y mostrar el problema observable antes de introducir threads/selectors y `asyncio`.
- La ausencia de CI y configuración Python impide demostrar una matriz Windows/macOS/Linux → usar solo APIs portables, documentar diferencias de comandos, ejecutar en el entorno disponible y expresar portabilidad como decisión de diseño, no como garantía probada en tres sistemas.
- Un schema ambiguo produciría clientes incompatibles → congelar el contrato anterior antes de implementar y probar cada límite, respuesta y transición sin mutación parcial.

## EXECUTION ORDER

1. Aprobar esta proposal y congelar el mapa de requisitos y el temario.
2. Escribir el contenido técnico inglés y los ejemplos síncronos básicos, que son dependencia del resto.
3. Añadir framing, protocolo, UDP y robustez; validar sus pruebas antes de introducir concurrencia.
4. Evolucionar la central de telemetría con servidor multi-cliente, streams `asyncio`, TLS y observabilidad.
5. Auditar los microciclos pedagógicos, ejercicios graduados, edge cases, soluciones y referencias cruzadas ya incluidos en cada incremento.
6. Traducir primero al español y, en paralelo, al catalán, sueco y árabe usando ejemplos ya congelados.
7. Actualizar los seis índices y verificar selectores, enlaces y paridad temática.
8. Ejecutar validaciones de Markdown, snippets, laboratorios, tests y OpenSpec.

Las traducciones son paralelizables después de estabilizar el contenido y los bloques de código. Las secciones avanzadas dependen del codec/framing y no deben desarrollarse antes de que sus casos de fragmentación estén probados.

## DEFINITION OF DONE

- `openspec validate add-python-network-programming-chapter --strict` finaliza sin errores.
- `openspec show add-python-network-programming-chapter --json --deltas-only` reconoce todos los requisitos y escenarios.
- Existen las cinco variantes del capítulo, sus selectores funcionan y los seis índices raíz enlazan a la versión correcta.
- La ruta esencial, intermedia y avanzada funciona offline sobre IPv4 loopback con Python 3.11+ en el entorno de validación; usa APIs portables y documenta comandos/diferencias para Windows, macOS y Linux sin afirmar una matriz no ejecutada. IPv6 se ejecuta condicionalmente y registra un skip explicado.
- Con root-first, `python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py` posee docs/hygiene y red; con chapter-first, los standalones equivalentes pasan y quedan retirados tras migración probada al mismo comando.
- `python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v` valida los laboratorios TCP, UDP, NDJSON, múltiples clientes y `asyncio` sin bloquearse ni dejar sockets abiertos o caches en el repositorio.
- Las pruebas cubren happy path y límites exactos de schema, secuencia, 64/65 sensores, 32/33 clientes, fragmentación/coalescing, payload inválido o grande, timeout, desconexión, respuesta/error y cleanup transaccional.
- El cliente TLS valida confianza y hostname; las pruebas negativas cubren CA no confiable, certificado expirado y hostname incorrecto; ningún ejemplo recomienda desactivar la verificación.
- La central de telemetría funciona de forma secuencial en la ruta intermedia y multi-cliente asíncrona en la ruta avanzada; TLS se verifica con fixtures versionados e IPv6 se ejecuta condicionalmente o registra un skip explicado.
- Una revisión pedagógica y accesible confirma objetivos, contexto, teoría mínima, ejemplos, ejercicios con TODOs y pistas, errores comunes, soluciones explicadas, checkpoints, rúbrica, reflexión, headings jerárquicos, links descriptivos y alternativas textuales.
- Una revisión de alcance confirma que no se introducen técnicas ofensivas, privilegios, dependencia de Internet ni exposición pública por defecto.

## Open Questions

None.
