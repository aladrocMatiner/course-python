# Change: Añadir un capítulo progresivo de programación de redes con Python

## Why

El curso enseña HTTP, logging, pruebas y una introducción a `asyncio`, pero no explica qué ocurre por debajo de una API ni cómo construir protocolos de red directamente con Python. Falta un puente pedagógico entre esos capítulos y la creación de clientes y servidores robustos.

Un nuevo capítulo permitirá empezar sin conocimientos previos de redes y avanzar, mediante laboratorios locales y seguros, hasta framing de mensajes, múltiples clientes, I/O asíncrono, TLS, observabilidad y pruebas de integración.

## What Changes

- Crear el capítulo 23, `chapter-23-network-programming/`, organizado en rutas esencial, intermedia y avanzada.
- Explicar desde cero el modelo cliente-servidor, hosts, DNS, direcciones IP, puertos, bytes, sockets y la relación entre las capas de transporte y HTTP.
- Incluir laboratorios ejecutables y offline sobre TCP, UDP, framing NDJSON, un contrato de telemetría versionado con schema/límites/respuestas exactos, concurrencia, `asyncio`, TLS y cierre ordenado.
- Añadir ejemplos complementarios y pruebas locales para los ejercicios que sean demasiado extensos para un único bloque de código Markdown.
- Hacer evolucionar un único proyecto de central de telemetría local: intercambio TCP básico, mensajes NDJSON validados y, finalmente, servicio multi-cliente asíncrono con pruebas.
- Aplicar una política segura por defecto: loopback, puertos no privilegiados o efímeros, límites de recursos y ninguna dependencia de Internet.
- Incluir validadores locales, escritos con la librería estándar, para enlaces, estructura multilingüe y snippets Markdown marcados como ejecutables.
- Publicar el capítulo en inglés, español, catalán, sueco y árabe, elevando explícitamente el nuevo capítulo a paridad temática/técnica completa y Markdown accesible entre idiomas.
- Actualizar los seis índices raíz (`README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`).
- Enlazar los capítulos 13, 14, 18, 19, 20 y 21 como conocimientos previos o material relacionado, sin duplicar sus explicaciones.

## Impact

- Affected specs: `teach-python-network-programming` (nueva capability).
- Affected content: nuevo directorio `chapter-23-network-programming/` y los seis índices raíz.
- Related content: capítulos 13 (streams), 14 (excepciones), 18 (pytest), 19 (HTTP), 20 (logging) y 21 (`asyncio`).
- Dependencies: Python 3.11 o posterior y su librería estándar, incluido `unittest`, para toda la ruta obligatoria. `pytest` podrá mencionarse como adaptación opcional del capítulo 18, pero no será necesario para aceptar esta change. Los fixtures TLS se versionarán con el laboratorio para no requerir `openssl` al alumnado.
- Compatibility: los ejemplos obligatorios usarán APIs portables de Python y documentarán comandos para Windows, macOS y Linux sobre IPv4 loopback; la ejecución se verificará en el entorno disponible sin afirmar una matriz multiplataforma inexistente. IPv6 se validará condicionalmente cuando esté disponible. No se renumeran ni se modifican los objetivos de los capítulos existentes.
- Security: no se incluirán escaneo de redes, sniffing, raw sockets, spoofing, explotación, criptografía casera ni despliegues públicos.
