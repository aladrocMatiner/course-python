## Phase 1: Baseline, contrato y puertas de calidad

`add-book-quality-gates` conserva ownership de las siete decisiones históricas de procedencia. El warning root de `LICENSE` bloquea la promoción automática global hasta resolverse; cada paquete humano depende solo de las entradas cuyos paths cubren esa unidad, mientras `LICENSE` y el badge son gates de publicación global. Esta change consume IDs/digests/status sin duplicar, suprimir ni fabricar aprobación.

### Task 1.1: Inventariar la matriz completa

- [x] 1.1 Registrar las 27 fuentes canónicas y 108 variantes localizadas.
- **Objective:** Convertir el estado actual en una matriz completa y trazable sin confundir tamaño con calidad.
- **Deliverables:** Inventario persistente por unidad/idioma con path, digest canónico, estado, señales de headings/fences/palabras/source refs, gaps observados y prioridad.
- **Validation:** La matriz contiene exactamente capítulos 01–25 y dos apéndices × `es/ca/sv/ar`; ningún path falta; un recuento automatizado reproduce 27 fuentes y 108 variantes.
- **Risk:** Los ratios pueden sesgar la prioridad; se etiquetan como señales de triaje, nunca aceptación.
- **Scope:** M.

### Task 1.2: Definir el paquete de revisión semántica

- [x] 1.2 Implementar el esquema de mapa de paridad y estados de review.
- **Objective:** Hacer auditable cada decisión lingüística, técnica y pedagógica.
- **Deliverables:** Esquema y plantilla con digest, 12 dimensiones del Parity Contract, roles lingüístico/técnico, excepciones, comandos, resultados y estados `inventoried` a `accepted`, más `stale`/`blocked`.
- **Validation:** Fixtures válidos e inválidos prueban campos obligatorios, transiciones, invalidación por digest y rechazo de una excepción sin justificación/aprobación.
- **Risk:** Metadatos excesivos pueden frenar revisión; mantener referencias breves y verificables.
- **Scope:** M.

### Task 1.3: Integrar las señales del gate común

- [x] 1.3 Conectar la revisión a la implementación disponible de `add-book-quality-gates`.
- **Objective:** Reusar una sola implementación para shape, links, mirror, RTL, headings, fences, alt text y source refs.
- **Deliverables:** Adaptación a `python -B tools/validate_book.py --changed-from <ref>`, taxonomía exacta `runnable|expected-error|compile-only|source-ref|todo|illustrative|output`, metadata `bookcheck` y baseline común.
- **Validation:** Un fixture roto por tipo de señal produce diagnóstico estable; cada lote elimina con `--update-baseline` los fingerprints que resuelve y el diff es reduction-only, sin añadir/ensanchar deuda; la integración no declara paridad semántica ni inventa convenciones alternativas.
- **Risk:** La implementación del gate está disponible, pero su change de origen sigue activa/no archivable hasta completar procedencia, matriz final y revisión humana; no confundir consumo técnico con aceptación de esos gates.
- **Scope:** M.

### Task 1.4: Ampliar el esquema de evidencia humana

- [ ] 1.4 Versionar y migrar los leaves de fuente/locale con reviews independientes.
- **Objective:** Representar auditoría canónica, accesibilidad renderizada y bidi sin convertir señales automáticas en aprobación.
- **Deliverables:** `SCHEMA_VERSION=2`, `LEAF_SCHEMA_VERSION=2` e índice v2 estable en `tools/parity_review.py`; source leaves con `canonical_review` y `rendered_accessibility_review`; locale leaves con `linguistic_review`, `technical_review`, `rendered_accessibility_review` y `bidi_review` obligatorio solo para árabe; `tools/parity/root-publication.json` con gates y procedencia derivada para los seis índices; estado `human-review-in-progress`; `tools/render_review_profile.json`; `tools/publication_signoff.json` schema 1 inicialmente pending y fuera del store; comandos explícitos `--migrate-review-schema` y `--export-review-bundle <path>`; migración determinista de 135 leaves v1 a 136 leaves v2, guía y tests.
- **Validation:** Mapping v1→v2 y perfil siguen design/spec; fixtures prueban campos/roles/fechas/entorno, invalidación por page/profile/render-input/provenance digest, pending por defecto, conservación compatible y downgrade de `accepted`; store v2 es no-op; mixed-version aborta sin escribir y conserva el input mixto exacto; un input íntegramente v1 se conserva/restaura byte-exacto ante falta de `RENAME_EXCHANGE`, CAS concurrente, staging/reload inválidos; un fallo de rollback conserva/reportará recovery sibling por path relativo y bloquea higiene sin inventar aprobación. Migración/export legacy conserva round trip determinista/Unicode en leaf schema 1; `--export-monolith` rechaza schema 2 antes de escribir y `--export-review-bundle` conserva determinísticamente todos los campos v2 sin mutar el store.
- **Risk:** Una migración puede destruir evidencia humana válida; snapshot, compare-and-swap, round trip y rollback deben ser lossless para campos compatibles.
- **Scope:** L.

### Task 1.5: Generar paquetes read-only por unidad

- [ ] 1.5 Implementar la proyección determinista de revisión de capítulo/apéndice.
- **Objective:** Dar a reviewers un único dossier navegable sin crear una segunda fuente de verdad editable.
- **Deliverables:** `python -B tools/parity_review.py --review-packet chapter-01-introduction` emite JSON canónico por stdout con una fuente, cuatro locales, digests, estado de todas las puertas, perfil/targets de render, comandos y entradas aplicables de `ATTRIBUTIONS.toml` por ID más `provenance_sha256`; `--root-review-packet` proyecta solo los seis índices, gates y digests del root leaf; `--verify-publication-signoff tools/publication_signoff.json` verifica el consumidor sin mutarlo y queda incluido en `handoff`; errores seguros van por stderr con exit code estable; documentación de ownership.
- **Validation:** Task 1.4 completa; tests cubren unidad/root válidos, unidad desconocida, path inseguro, orden byte-estable, stdout/stderr/exit codes, canonicalización exacta de provenance/render/sign-off inputs, procedencia multi-path/root/companion, review pendiente/aprobada, árabe bidi, `--verify-publication-signoff` current/pending/stale/malformed y stale al cambiar solo un companion cubierto, integración read-only con el perfil `handoff`, cero escrituras y prueba de que ninguna salida se puede importar ni muta el store.
- **Risk:** Una exportación puede confundirse con autoridad; salida stdout read-only, paths de origen explícitos y ninguna operación de importación.
- **Scope:** M.

### Task 1.6: Auditar las fuentes inglesas

- **Milestone:** Revisar los 24 `README.md` canónicos no avanzados antes de congelar sus oleadas.
- **Unit checkpoints (auditoría canónica y render, con rollback independiente):**
- [ ] 1.6.1 `chapter-01-introduction`.
- [ ] 1.6.2 `chapter-02-variables`.
- [ ] 1.6.3 `chapter-03-lists`.
- [ ] 1.6.4 `chapter-04-dictionaries`.
- [ ] 1.6.5 `chapter-05-sets`.
- [ ] 1.6.6 `chapter-06-tuples`.
- [ ] 1.6.7 `chapter-07-queues`.
- [ ] 1.6.8 `chapter-08-conditionals`.
- [ ] 1.6.9 `chapter-09-input`.
- [ ] 1.6.10 `chapter-10-loops`.
- [ ] 1.6.11 `chapter-11-functions`.
- [ ] 1.6.12 `chapter-12-oop`.
- [ ] 1.6.13 `chapter-13-files`.
- [ ] 1.6.14 `chapter-14-exceptions`.
- [ ] 1.6.15 `chapter-15-modulos`.
- [ ] 1.6.16 `chapter-16-entornos`.
- [ ] 1.6.17 `chapter-17-persistencia`.
- [ ] 1.6.18 `chapter-18-testing`.
- [ ] 1.6.19 `chapter-19-http`.
- [ ] 1.6.20 `chapter-20-logging`.
- [ ] 1.6.21 `chapter-21-async`.
- [ ] 1.6.22 `chapter-22-introspection`.
- [ ] 1.6.23 `appendix-cli-parser`.
- [ ] 1.6.24 `appendix-algorithms`.
- **Objective:** Evitar propagar errores, prerrequisitos ausentes o carencias pedagógicas de la fuente.
- **Deliverables:** Decisiones canónica y renderizada por unidad, más una cola de reparaciones limitada a exactitud, seguridad, accesibilidad o elementos necesarios de `BOOK_STYLE.md`; ampliaciones curriculares quedan fuera.
- **Validation:** Un checkpoint solo se marca con `canonical_review=approved` y `rendered_accessibility_review=approved`, rol/fecha/notas, digests vigentes y cero blockers; `changes-requested` mantiene el checkbox abierto. Toda reparación se ejecuta primero, se prueba y forma un bundle atómico con sus cuatro variantes antes de aceptar la unidad.
- **Risk:** Scope creep editorial; una capacidad nueva se remite a proposal separada.
- **Scope:** L.

### Task 1.7: Pilotar la suboleada sueca/árabe con capítulos 01–02

- **Milestone:** Ejecutar la primera suboleada sueca/árabe para capítulos 01–02.
- **Unit checkpoints (`sv`/`ar`, con rollback y aceptación independientes):**
- [ ] 1.7.1 `chapter-01-introduction` (`sv`/`ar`).
- [ ] 1.7.2 `chapter-02-variables` (`sv`/`ar`).
- **Objective:** Verificar que el flujo detecta omisiones reales y produce un lote revisable antes de escalar.
- **Deliverables:** Dos paquetes de unidad abiertos e independientes para capítulos 01 y 02; `README.sv.md` y `README.ar.md` restaurados; cuatro registros `sv/ar` `accepted`; registros `es/ca` explícitamente pendientes para sus fases posteriores; lecciones aprendidas incorporadas al checklist sin relajar criterios.
- **Validation:** Tasks 1.4–1.6 completas para estas unidades; cada suboleada conserva digests vigentes, auditoría y render canónicos, señales automáticas, gates humanos de `sv/ar`, bidi árabe, procedencia aplicable, código/source refs, prerrequisitos, links/selectores y `git diff --check`; ningún paquete se declara cerrado hasta aceptar también `es/ca`.
- **Risk:** Ajustes del piloto pueden invalidar la plantilla; migrar sus registros antes de continuar.
- **Scope:** L.

### Task 1.8: Auditar las fuentes avanzadas publicadas

- **Milestone:** Revisar los `README.md` canónicos de capítulos 23–25 antes de aceptar sus oleadas.
- **Unit checkpoints (auditoría canónica, render y plugin de dominio cuando aplique):**
- [ ] 1.8.1 `chapter-23-network-programming`.
- [ ] 1.8.2 `chapter-24-python-cpp-integration`.
- [ ] 1.8.3 `chapter-25-python-rust-integration`.
- **Objective:** Incorporar redes, C++ y Rust al alcance editorial sin heredar aprobación de sus gates de implementación.
- **Deliverables:** Tres auditorías canónicas y revisiones renderizadas humanas contra sus digests actuales, más reparaciones atómicas si aparecen defectos.
- **Validation:** Cada checkpoint exige `canonical_review=approved` y `rendered_accessibility_review=approved`, rol/fecha/notas, digests vigentes y cero blockers; exactitud, seguridad, pedagogía, accesibilidad y procedencia pasan. `changes-requested` deja el checkbox abierto y los plugins de dominio son evidencia adicional, no sustitutos de review.
- **Scope:** L.

## Dependencias normativas

- Task 1.4 precede a Task 1.5 y a cualquier nueva escritura de evidencia humana; la migración de los 136 leaves y el perfil de render deben estar validados antes de generar paquetes de unidad o raíz.
- El checkpoint canónico de Task 1.6 o 1.8 correspondiente precede a cualquier checkpoint localizado de esa unidad. Una reparación canónica reabre los cuatro locales por digest.
- El gate de procedencia aplicable de Task 7.1 precede al estado `accepted` de cada source/locale leaf, aunque el checkbox global 7.1 permanezca abierto hasta acabar todas las oleadas.
- Task 3.7 depende de los 27 checkpoints `sv/ar` y precede a Phase 4; los 13 checkpoints catalanes de Phase 4 preceden a Phase 5; Task 5.8 depende de los 27 checkpoints `ca` y precede a Phase 6; la banda española queda completa únicamente tras sus 27 checkpoints `es`.
- Task 7.3 depende de la navegación estructural de Task 7.2, de la procedencia global aplicable resuelta por `add-book-quality-gates` Task 4.3 y produce los digests que después consume su sign-off humano; no hereda aprobación de que 7.2 esté marcada ni depende del digest de ese consumidor.
- Task 7.4 depende de las 27 auditorías canónicas, las tres bandas localizadas, sus regresiones, Task 7.3 y los gates aplicables de procedencia; se completa atómicamente con las Tasks 4.3, 7.1 y 7.2 de `add-book-quality-gates` y su referencia narrativa al sign-off.
- Task 7.5 depende del consumidor verificado de Task 7.4 y de todos los paquetes aceptados; Task 7.6 es siempre el último paso.

## Contrato transversal de las fases 2–6

Todas las tasks localizadas usan la fuente congelada, el Parity Contract completo y todos los gates humanos aplicables: auditoría/render canónicos, revisión lingüística, revisión técnica/pedagógica, accesibilidad renderizada local y bidi para árabe. La procedencia se resuelve incrementalmente antes de aceptar el registro afectado. Cada task que agrupa unidades es solo un hito de seguimiento: sus checkboxes unitarios ejecutan paquetes y rollback boundaries independientes, normalmente en PRs/subwaves separadas; el hito no se considera completo hasta cerrar todos sus subalcances, aunque cada paquete puede permanecer abierto para otros idiomas. Gate común/equivalente, taxonomía/metadata `bookcheck`, plugins relevantes y `git diff --check` pasan sin ampliar el baseline. Un cambio canónico detiene el paquete como `stale`; una reparación de fuente se integra como bundle de una unidad antes de aceptar sus locales.

## Phase 2: Sueco y árabe, fundamentos

### Task 2.1: Capítulos 03–04

- **Milestone:** Restaurar sueco y árabe para listas y diccionarios.
- **Unit checkpoints:**
- [ ] 2.1.1 `chapter-03-lists` (`sv`/`ar`).
- [ ] 2.1.2 `chapter-04-dictionaries` (`sv`/`ar`).
- **Objective:** Recuperar operaciones, ejemplos, bordes, recuperación, ejercicios y soluciones de las dos estructuras básicas.
- **Deliverables:** Cuatro variantes localizadas y cuatro registros `accepted` para capítulos 03–04.
- **Validation:** Contratos de mutabilidad/lookup y nombres públicos coinciden con la fuente; todos los gates humanos aplicables, gate/equivalente, RTL/LTR y source refs pasan.
- **Scope:** L.

### Task 2.2: Capítulos 05–06

- **Milestone:** Restaurar sueco y árabe para sets y tuplas.
- **Unit checkpoints:**
- [ ] 2.2.1 `chapter-05-sets` (`sv`/`ar`).
- [ ] 2.2.2 `chapter-06-tuples` (`sv`/`ar`).
- **Objective:** Preservar semántica de unicidad, pertenencia, inmutabilidad y unpacking con práctica equivalente.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 05–06.
- **Validation:** Happy/edge/error, TODO/pistas/soluciones y outputs conservan conducta; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** L.

### Task 2.3: Capítulos 07–08

- **Milestone:** Restaurar sueco y árabe para colas y condicionales.
- **Unit checkpoints:**
- [ ] 2.3.1 `chapter-07-queues` (`sv`/`ar`).
- [ ] 2.3.2 `chapter-08-conditionals` (`sv`/`ar`).
- **Objective:** Recuperar orden de operaciones, decisiones y manejo de entradas límite sin introducir conceptos posteriores.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 07–08.
- **Validation:** Prerrequisitos, ramas y errores recuperables son resolubles; todos los gates humanos aplicables, gates automáticos, RTL/LTR y código pasan.
- **Scope:** L.

### Task 2.4: Capítulos 09–10

- **Milestone:** Restaurar sueco y árabe para input y bucles.
- **Unit checkpoints:**
- [ ] 2.4.1 `chapter-09-input` (`sv`/`ar`).
- [ ] 2.4.2 `chapter-10-loops` (`sv`/`ar`).
- **Objective:** Mantener validación de input, terminación y progresión de iteración de forma segura y observable.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 09–10.
- **Validation:** No hay loops/input sin límites o recuperación omitida; outputs, ejercicios, soluciones y todos los gates humanos aplicables pasan.
- **Scope:** L.

### Task 2.5: Capítulos 11–12

- **Milestone:** Restaurar sueco y árabe para funciones y OOP.
- **Unit checkpoints:**
- [ ] 2.5.1 `chapter-11-functions` (`sv`/`ar`).
- [ ] 2.5.2 `chapter-12-oop` (`sv`/`ar`).
- **Objective:** Conservar contratos de parámetros/retorno y el salto gradual hacia objetos.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 11–12.
- **Validation:** Jargon definido, identificadores estables, ejemplos ejecutables/source refs, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** L.

### Task 2.6: Capítulos 13–14

- **Milestone:** Restaurar sueco y árabe para archivos y excepciones.
- **Unit checkpoints:**
- [ ] 2.6.1 `chapter-13-files` (`sv`/`ar`).
- [ ] 2.6.2 `chapter-14-exceptions` (`sv`/`ar`).
- **Objective:** Recuperar recursos, paths seguros, errores esperados y recuperación antes de las unidades de ecosistema.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 13–14.
- **Validation:** Ejemplos usan paths temporales/seguros, documentan diagnóstico y cleanup; todos los gates humanos aplicables, gates automáticos y RTL/LTR pasan.
- **Scope:** L.

## Phase 3: Sueco y árabe, ecosistema y avanzado

### Task 3.1: Capítulos 15–16

- **Milestone:** Restaurar sueco y árabe para módulos y entornos.
- **Unit checkpoints:**
- [ ] 3.1.1 `chapter-15-modulos` (`sv`/`ar`).
- [ ] 3.1.2 `chapter-16-entornos` (`sv`/`ar`).
- **Objective:** Enseñar importación y aislamiento antes de dependencias posteriores con comandos copiables.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 15–16.
- **Validation:** Comandos, paths, plataformas declaradas y optional previews coinciden; todos los gates humanos aplicables, gates automáticos y bidi pasan.
- **Scope:** L.

### Task 3.2: Capítulos 17–18

- **Milestone:** Restaurar sueco y árabe para persistencia y testing.
- **Unit checkpoints:**
- [ ] 3.2.1 `chapter-17-persistencia` (`sv`/`ar`).
- [ ] 3.2.2 `chapter-18-testing` (`sv`/`ar`).
- **Objective:** Preservar contratos de datos y el vínculo entre comportamiento, riesgo y pruebas.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 17–18.
- **Validation:** Datos son ficticios/locales; tests conservan comportamiento y motivo; todos los gates humanos aplicables, gates automáticos y source refs pasan.
- **Scope:** L.

### Task 3.3: Capítulos 19–20

- **Milestone:** Restaurar sueco y árabe para HTTP y logging.
- **Unit checkpoints:**
- [ ] 3.3.1 `chapter-19-http` (`sv`/`ar`).
- [ ] 3.3.2 `chapter-20-logging` (`sv`/`ar`).
- **Objective:** Recuperar límites de red/configuración, errores y observabilidad sin usar secretos ni targets inseguros.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 19–20.
- **Validation:** Ejemplos mantienen alcance seguro y claims verificadas; todos los gates humanos aplicables, gates automáticos, bidi y referencias pasan.
- **Scope:** L.

### Task 3.4: Capítulos 21–22

- **Milestone:** Restaurar sueco y árabe para asyncio e introspección.
- **Unit checkpoints:**
- [ ] 3.4.1 `chapter-21-async` (`sv`/`ar`).
- [ ] 3.4.2 `chapter-22-introspection` (`sv`/`ar`).
- **Objective:** Completar las unidades avanzadas con concurrencia acotada, diagnóstico y práctica evaluable.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 21–22.
- **Validation:** No se omiten errores, soluciones ni checkpoints; ejemplos bounded/deterministic; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** L.

### Task 3.5: Capítulos 23–25

- **Milestone:** Restaurar sueco y árabe para redes e interoperabilidad nativa.
- **Unit checkpoints:**
- [ ] 3.5.1 `chapter-23-network-programming` (`sv`/`ar`).
- [ ] 3.5.2 `chapter-24-python-cpp-integration` (`sv`/`ar`).
- [ ] 3.5.3 `chapter-25-python-rust-integration` (`sv`/`ar`).
- **Objective:** Completar las rutas avanzadas publicadas sin rebajar sus contratos de seguridad, toolchain, packaging o verificación.
- **Deliverables:** Tres paquetes de unidad con rollback independiente para capítulos 23, 24 y 25, cada uno con dos variantes/registros sueco/árabe.
- **Validation:** Cada paquete obtiene todos los gates humanos, RTL/LTR, gates genéricos, su plugin explícito y contratos fuente contra digests vigentes; el hito solo se considera completo cuando sus tres checkpoints están aceptados.
- **Scope:** L.

### Task 3.6: Apéndices A–B

- **Milestone:** Restaurar sueco y árabe para CLI y algoritmos.
- **Unit checkpoints:**
- [ ] 3.6.1 `appendix-cli-parser` (`sv`/`ar`).
- [ ] 3.6.2 `appendix-algorithms` (`sv`/`ar`).
- **Objective:** Recuperar rutas, ejercicios, complejidad y soluciones completas de ambos apéndices.
- **Deliverables:** Cuatro variantes y registros `accepted` para `appendix-cli-parser` y `appendix-algorithms`.
- **Validation:** CLI permanece segura/local; contratos y complejidad algorítmica coinciden; todos los gates humanos aplicables, gates automáticos y bidi pasan.
- **Scope:** L.

### Task 3.7: Cerrar la banda sueco/árabe

- [ ] 3.7 Ejecutar regresión completa de las 54 variantes suecas/árabes.
- **Objective:** Detectar drift entre lotes antes de iniciar catalán.
- **Deliverables:** Informe de regresión 27×2, estados finales y correcciones de integración limitadas.
- **Validation:** 54 registros `accepted` con digests vigentes; ninguna omisión, link roto, wrapper RTL duplicado, source ref inválida ni revisión requerida por esos 54 registros permanece pendiente.
- **Risk:** Una reparación tardía puede invalidar múltiples digests; reabrir solo registros afectados.
- **Scope:** M.

## Phase 4: Catalán, unidades tardías primero

Cada lote catalán cumple el mismo contrato de fences/metadata `bookcheck` y actualiza el baseline únicamente para eliminar fingerprints resueltos en ese lote.

### Task 4.1: Capítulos 15–16

- **Milestone:** Restaurar catalán para módulos y entornos.
- **Unit checkpoints:**
- [ ] 4.1.1 `chapter-15-modulos` (`ca`).
- [ ] 4.1.2 `chapter-16-entornos` (`ca`).
- **Objective:** Corregir primero la pérdida observada en el inicio de la banda avanzada.
- **Deliverables:** Dos variantes catalanas y registros `accepted` para capítulos 15–16.
- **Validation:** Parity Contract, digest, review lingüística/técnica, gate/equivalente, código y enlaces localizados pasan.
- **Scope:** M.

### Task 4.2: Capítulos 17–18

- **Milestone:** Restaurar catalán para persistencia y testing.
- **Unit checkpoints:**
- [ ] 4.2.1 `chapter-17-persistencia` (`ca`).
- [ ] 4.2.2 `chapter-18-testing` (`ca`).
- **Objective:** Recuperar datos, edge/error/recovery, pruebas y soluciones equivalentes.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 17–18.
- **Validation:** Source refs/tests y propósito pedagógico coinciden; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 4.3: Capítulos 19–20

- **Milestone:** Restaurar catalán para HTTP y logging.
- **Unit checkpoints:**
- [ ] 4.3.1 `chapter-19-http` (`ca`).
- [ ] 4.3.2 `chapter-20-logging` (`ca`).
- **Objective:** Completar red, errores, seguridad y observabilidad sin reducir la ruta formativa.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 19–20.
- **Validation:** Claims, comandos, límites y recuperación coinciden; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 4.4: Capítulos 21–22

- **Milestone:** Restaurar catalán para asyncio e introspección.
- **Unit checkpoints:**
- [ ] 4.4.1 `chapter-21-async` (`ca`).
- [ ] 4.4.2 `chapter-22-introspection` (`ca`).
- **Objective:** Recuperar el detalle avanzado, TODOs, pistas, soluciones y evaluación.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 21–22.
- **Validation:** Prerrequisitos/previews, comportamiento y checkpoints equivalen; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 4.5: Capítulos 23–25

- **Milestone:** Restaurar catalán para redes e interoperabilidad nativa.
- **Unit checkpoints:**
- [ ] 4.5.1 `chapter-23-network-programming` (`ca`).
- [ ] 4.5.2 `chapter-24-python-cpp-integration` (`ca`).
- [ ] 4.5.3 `chapter-25-python-rust-integration` (`ca`).
- **Objective:** Completar la banda catalana avanzada con el mismo contrato pedagógico y técnico publicado.
- **Deliverables:** Tres paquetes de unidad con rollback independiente para capítulos 23, 24 y 25, cada uno con su variante/registro catalán.
- **Validation:** Cada paquete obtiene todos los gates humanos, gates genéricos, su plugin explícito, source refs y comandos equivalentes; el hito solo se considera completo cuando sus tres checkpoints están aceptados.
- **Scope:** L.

### Task 4.6: Apéndices A–B

- **Milestone:** Restaurar catalán para CLI y algoritmos.
- **Unit checkpoints:**
- [ ] 4.6.1 `appendix-cli-parser` (`ca`).
- [ ] 4.6.2 `appendix-algorithms` (`ca`).
- **Objective:** Eliminar los resúmenes parciales de ambos apéndices.
- **Deliverables:** Dos variantes y registros `accepted` para ambos apéndices.
- **Validation:** Ejercicios, hints, solutions, tests/complejidad y accesibilidad equivalen; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

## Phase 5: Catalán, fundamentos e intermedio

Cada lote mantiene `--changed-from` limpio y un baseline reduction-only, además de todos los gates humanos aplicables.

### Task 5.1: Capítulos 01–02

- **Milestone:** Auditar/restaurar catalán para introducción y variables.
- **Unit checkpoints:**
- [ ] 5.1.1 `chapter-01-introduction` (`ca`).
- [ ] 5.1.2 `chapter-02-variables` (`ca`).
- **Objective:** Confirmar la base antes de aceptar el resto de la progresión catalana.
- **Deliverables:** Dos registros `accepted` y correcciones catalanas confirmadas para capítulos 01–02.
- **Validation:** Parity Contract completo, todos los gates humanos aplicables y los gates automáticos pasan; similitud de tamaño no se usa como aceptación.
- **Scope:** M.

### Task 5.2: Capítulos 03–04

- **Milestone:** Restaurar catalán para listas y diccionarios.
- **Unit checkpoints:**
- [ ] 5.2.1 `chapter-03-lists` (`ca`).
- [ ] 5.2.2 `chapter-04-dictionaries` (`ca`).
- **Objective:** Preservar toda la práctica y semántica de colecciones mutables.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 03–04.
- **Validation:** Contratos de código, edge/error/recovery y assessment equivalen; todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 5.3: Capítulos 05–06

- **Milestone:** Restaurar catalán para sets y tuplas.
- **Unit checkpoints:**
- [ ] 5.3.1 `chapter-05-sets` (`ca`).
- [ ] 5.3.2 `chapter-06-tuples` (`ca`).
- **Objective:** Completar conceptos y práctica de colecciones con progresión equivalente.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 05–06.
- **Validation:** Mapas completos, código/source refs y todos los gates humanos aplicables pasan.
- **Scope:** M.

### Task 5.4: Capítulos 07–08

- **Milestone:** Restaurar catalán para colas y condicionales.
- **Unit checkpoints:**
- [ ] 5.4.1 `chapter-07-queues` (`ca`).
- [ ] 5.4.2 `chapter-08-conditionals` (`ca`).
- **Objective:** Recuperar casos, decisiones y ejercicios omitidos sin adelantar conceptos.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 07–08.
- **Validation:** Prerrequisitos, outputs, recoverable errors, soluciones y gates pasan.
- **Scope:** M.

### Task 5.5: Capítulos 09–10

- **Milestone:** Restaurar catalán para input y bucles.
- **Unit checkpoints:**
- [ ] 5.5.1 `chapter-09-input` (`ca`).
- [ ] 5.5.2 `chapter-10-loops` (`ca`).
- **Objective:** Mantener validación, límites y razonamiento iterativo completos.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 09–10.
- **Validation:** Ejemplos seguros/bounded, checkpoints, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 5.6: Capítulos 11–12

- **Milestone:** Restaurar catalán para funciones y OOP.
- **Unit checkpoints:**
- [ ] 5.6.1 `chapter-11-functions` (`ca`).
- [ ] 5.6.2 `chapter-12-oop` (`ca`).
- **Objective:** Completar el puente desde funciones hacia objetos con vocabulario introducido.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 11–12.
- **Validation:** APIs estables, glosario/conceptos, práctica y todos los gates humanos aplicables pasan.
- **Scope:** M.

### Task 5.7: Capítulos 13–14

- **Milestone:** Restaurar catalán para archivos y excepciones.
- **Unit checkpoints:**
- [ ] 5.7.1 `chapter-13-files` (`ca`).
- [ ] 5.7.2 `chapter-14-exceptions` (`ca`).
- **Objective:** Recuperar manejo seguro de recursos y recuperación de errores.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 13–14.
- **Validation:** Paths/cleanup/diagnósticos, soluciones, source refs y gates pasan.
- **Scope:** M.

### Task 5.8: Cerrar la banda catalana

- [ ] 5.8 Ejecutar regresión completa de las 27 variantes catalanas.
- **Objective:** Confirmar continuidad curricular y navegación después de las oleadas fuera de orden.
- **Deliverables:** Informe 27×1, estados finales y correcciones de integración.
- **Validation:** 27 registros `accepted`, digests vigentes, links localizados, prerequisitos/previews y gates globales pasan.
- **Scope:** M.

## Phase 6: Español, auditoría completa y gaps confirmados

La cercanía aparente del español no lo exime de revisión. Cada checkbox audita una sola unidad y modifica únicamente las diferencias confirmadas; los headings agrupan hitos temáticos de dos o tres unidades.

Cada lote español usa la taxonomía/metadata `bookcheck` común y elimina en el mismo diff cualquier fingerprint heredado que resuelva, sin añadir deuda al baseline.

### Task 6.1: Capítulos 01–02

- **Milestone:** Auditar/corregir español para capítulos 01–02.
- **Unit checkpoints:**
- [ ] 6.1.1 `chapter-01-introduction` (`es`).
- [ ] 6.1.2 `chapter-02-variables` (`es`).
- **Objective:** Verificar que introducción y variables conservan todo el aprendizaje canónico.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Mapa completo, todos los gates humanos aplicables, gate/equivalente y digests pasan.
- **Scope:** M.

### Task 6.2: Capítulos 03–04

- **Milestone:** Auditar/corregir español para capítulos 03–04.
- **Unit checkpoints:**
- [ ] 6.2.1 `chapter-03-lists` (`es`).
- [ ] 6.2.2 `chapter-04-dictionaries` (`es`).
- **Objective:** Confirmar semántica y práctica de listas/diccionarios.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Código, ejemplos, ejercicios, edge/error/recovery y gates pasan.
- **Scope:** M.

### Task 6.3: Capítulos 05–06

- **Milestone:** Auditar/corregir español para capítulos 05–06.
- **Unit checkpoints:**
- [ ] 6.3.1 `chapter-05-sets` (`es`).
- [ ] 6.3.2 `chapter-06-tuples` (`es`).
- **Objective:** Confirmar paridad completa de sets y tuplas.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Mapa, todos los gates humanos aplicables, source refs y gates automáticos pasan.
- **Scope:** M.

### Task 6.4: Capítulos 07–08

- **Milestone:** Auditar/corregir español para capítulos 07–08.
- **Unit checkpoints:**
- [ ] 6.4.1 `chapter-07-queues` (`es`).
- [ ] 6.4.2 `chapter-08-conditionals` (`es`).
- **Objective:** Confirmar colas y condicionales sin gaps pedagógicos.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Prerrequisitos, casos, soluciones, assessment y gates pasan.
- **Scope:** M.

### Task 6.5: Capítulos 09–10

- **Milestone:** Auditar/corregir español para capítulos 09–10.
- **Unit checkpoints:**
- [ ] 6.5.1 `chapter-09-input` (`es`).
- [ ] 6.5.2 `chapter-10-loops` (`es`).
- **Objective:** Confirmar input y bucles seguros, bounded y explicados.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Código/output/recovery, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.6: Capítulos 11–12

- **Milestone:** Auditar/corregir español para capítulos 11–12.
- **Unit checkpoints:**
- [ ] 6.6.1 `chapter-11-functions` (`es`).
- [ ] 6.6.2 `chapter-12-oop` (`es`).
- **Objective:** Confirmar funciones y OOP con dependencia conceptual correcta.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** APIs, jargon, ejercicios/soluciones y gates pasan.
- **Scope:** M.

### Task 6.7: Capítulos 13–14

- **Milestone:** Auditar/corregir español para capítulos 13–14.
- **Unit checkpoints:**
- [ ] 6.7.1 `chapter-13-files` (`es`).
- [ ] 6.7.2 `chapter-14-exceptions` (`es`).
- **Objective:** Confirmar archivos/excepciones, paths y recuperación segura.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Seguridad, source refs, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.8: Capítulos 15–16

- **Milestone:** Auditar/corregir español para capítulos 15–16.
- **Unit checkpoints:**
- [ ] 6.8.1 `chapter-15-modulos` (`es`).
- [ ] 6.8.2 `chapter-16-entornos` (`es`).
- **Objective:** Confirmar módulos/entornos y comandos equivalentes.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Tooling/paths/previews, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.9: Capítulos 17–18

- **Milestone:** Auditar/corregir español para capítulos 17–18.
- **Unit checkpoints:**
- [ ] 6.9.1 `chapter-17-persistencia` (`es`).
- [ ] 6.9.2 `chapter-18-testing` (`es`).
- **Objective:** Confirmar persistencia/testing y riesgos cubiertos.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Datos ficticios, tests, edge cases, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.10: Capítulos 19–20

- **Milestone:** Auditar/corregir español para capítulos 19–20.
- **Unit checkpoints:**
- [ ] 6.10.1 `chapter-19-http` (`es`).
- [ ] 6.10.2 `chapter-20-logging` (`es`).
- **Objective:** Confirmar HTTP/logging, errores, límites y seguridad.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Targets/secretos/claims, source refs, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.11: Capítulos 21–22

- **Milestone:** Auditar/corregir español para capítulos 21–22.
- **Unit checkpoints:**
- [ ] 6.11.1 `chapter-21-async` (`es`).
- [ ] 6.11.2 `chapter-22-introspection` (`es`).
- **Objective:** Cerrar gaps avanzados confirmados, incluida cualquier diferencia en introspección.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Async bounded, APIs de introspección, exercises/solutions/checkpoints, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

### Task 6.12: Capítulos 23–25

- **Milestone:** Auditar/corregir español para redes e interoperabilidad nativa.
- **Unit checkpoints:**
- [ ] 6.12.1 `chapter-23-network-programming` (`es`).
- [ ] 6.12.2 `chapter-24-python-cpp-integration` (`es`).
- [ ] 6.12.3 `chapter-25-python-rust-integration` (`es`).
- **Objective:** Confirmar que los tres capítulos avanzados conservan contratos, recuperación, seguridad y evaluación.
- **Deliverables:** Tres paquetes de unidad con rollback independiente para capítulos 23, 24 y 25, cada uno con su registro y correcciones españolas necesarias.
- **Validation:** Cada paquete obtiene todos los gates humanos, gates automáticos, su plugin, comandos y claims de plataforma contra los digests actuales; el hito solo se considera completo cuando sus tres checkpoints están aceptados.
- **Scope:** L.

### Task 6.13: Apéndices A–B

- **Milestone:** Auditar/corregir español para ambos apéndices.
- **Unit checkpoints:**
- [ ] 6.13.1 `appendix-cli-parser` (`es`).
- [ ] 6.13.2 `appendix-algorithms` (`es`).
- **Objective:** Confirmar CLI/algoritmos sin asumir equivalencia por longitud.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Comandos, complejidad, tests, soluciones, todos los gates humanos aplicables y los gates automáticos pasan.
- **Scope:** M.

## Phase 7: Integración, procedencia y aceptación global

### Task 7.1: Mantener el gate transversal de procedencia

- [ ] 7.1 Verificar incrementalmente origen/licencia de ejercicios, datasets, diagramas o prosa sustancial adaptados durante las oleadas.
- **Objective:** Evitar que la restauración introduzca material incompatible con CC BY-SA.
- **Deliverables:** En cada paquete, atribuciones requeridas cerca del material o en sección dedicada y decisión competente para cada material tocado; la task global permanece pendiente hasta terminar todas las oleadas y no duplica la auditoría histórica de `add-book-quality-gates`.
- **Validation:** Ningún registro afectado llega a `accepted` antes de resolver su procedencia aplicable; cada adaptación tocada tiene fuente, licencia y obligación registrada; material dudoso se reemplaza por ejemplo original o bloquea el paquete.
- **Scope:** M.

### Task 7.2: Reconciliar navegación, capabilities y changes activas

- [x] 7.2 Validar selectores, links localizados e índices con capítulos 23–25 publicados.
- **Objective:** Mantener navegación coherente bajo integración concurrente.
- **Deliverables:** Correcciones atómicas de índices y aliases de anchors deliberados solo si hacen falta; preservación numérica de 23–25 con sus cinco targets.
- **Validation:** English mirrors identical; links/fragments/aliases resuelven; 23→24→25 aparece en orden en los seis índices y no implica aceptación humana de sus variantes.
- **Risk:** Conflictos de rebase en índices; integrar al final y releer las specs/capabilities vigentes y las changes activas relevantes.
- **Scope:** M.

### Task 7.3: Cerrar el paquete de publicación raíz

- **Milestone:** Revisar semántica, accesibilidad renderizada y bidi de los seis índices sin duplicar el sign-off común.
- **Root checkpoints:**
- [ ] 7.3.1 `README.md`: auditoría canónica y render.
- [ ] 7.3.2 `README.en.md`: mirror byte-idéntico y render independiente.
- [ ] 7.3.3 `README.es.md`: revisión lingüística/técnica y render.
- [ ] 7.3.4 `README.ca.md`: revisión lingüística/técnica y render.
- [ ] 7.3.5 `README.sv.md`: revisión lingüística/técnica y render.
- [ ] 7.3.6 `README.ar.md`: revisión lingüística/técnica, render y bidi/copy-paste.
- **Objective:** Cubrir la superficie publicada que no pertenece a ningún paquete de capítulo/apéndice.
- **Deliverables:** `tools/parity/root-publication.json` `accepted`, paquete raíz read-only, seis decisiones de render, gates semánticos aplicables, una decisión bidi árabe, referencias/digests de procedencia global resuelta y un conjunto estable de IDs/digests listo para el sign-off consumidor.
- **Validation:** Cada checkbox exige todos sus gates `approved` con rol/fecha/notas y digests page/profile/render-input vigentes; `changes-requested` lo deja abierto. El root leaf cubre exactamente seis renders y un bidi árabe, no almacena el sign-off consumidor y puede cerrarse antes de que `add-book-quality-gates` lo referencie.
- **Risk:** Un sign-off agregado puede ocultar una página no inspeccionada; exigir path, digest y decisión separada por índice.
- **Scope:** M.

### Task 7.4: Persistir y verificar el sign-off común

- [ ] 7.4 Completar el consumidor unidireccional de la evidencia editorial y de publicación.
- **Objective:** Hacer auditable qué evidence aprobó cada rol global sin introducir un ciclo de digests ni duplicar decisiones de página.
- **Deliverables:** `tools/publication_signoff.json` `approved` con inputs actuales y tres reviews independientes; `tools/BOOK_QUALITY_REVIEW.md` y `openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md` referencian su digest; Tasks 4.3, 7.1 y 7.2 de esa change quedan marcadas solo con evidencia real.
- **Validation:** `python -B tools/parity_review.py --verify-publication-signoff tools/publication_signoff.json`; recomputación exacta de `parity_index_sha256`, `unit_evidence_sha256`, `unit_provenance_sha256`, root leaf/decision digests, `attributions_sha256`, `render_profile_sha256`, `quality_contract_sha256` y `signoff_input_sha256`; fixture que cambia solo un companion cubierto vuelve stale el sign-off; roles/fechas/notas humanos presentes; ningún leaf upstream contiene el digest consumidor; `python -B tools/run_quality.py --profile handoff --format text` incluye y pasa el verificador.
- **Risk:** Actualizar el Markdown narrativo sin el JSON, o viceversa, puede aparentar sign-off stale; el JSON es autoridad y el handoff Markdown solo referencia su digest.
- **Scope:** M.

### Task 7.5: Ejecutar aceptación global 27×5 más raíz

- [ ] 7.5 Verificar las 27 fuentes, 108 variantes y seis índices raíz como un conjunto coherente.
- **Objective:** Demostrar paridad, no solo completar lotes aislados.
- **Deliverables:** Informe final con 27 paquetes de unidad y el paquete raíz cerrados, 108 registros y root leaf `accepted`, sign-off común vigente, 27 digests canónicos vigentes, cero blockers/stale y trazabilidad a requisitos/scenarios.
- **Validation:** `python -B tools/parity_review.py --require-accepted`; `python -B tools/parity_review.py --verify-publication-signoff tools/publication_signoff.json`; paquetes read-only de cada unidad y raíz; inventario exacto de 141 renders y 28 decisiones bidi; `python -B tools/run_quality.py --profile handoff --format text`; plugins relevantes; links/selectors/mirror/RTL/headings/taxonomía y metadata `bookcheck`/alt/source refs; baseline sin entradas stale y con diffs reduction-only; código/tests; todos los gates humanos; seguridad; accesibilidad; `git diff --check`.
- **Risk:** Un cambio tardío puede reabrir registros o dejar stale el consumidor; invalidar y revisar solo el alcance afectado antes de repetir 7.4–7.5.
- **Scope:** L.

### Task 7.6: Cerrar OpenSpec y comprobar higiene

- [ ] 7.6 Confirmar que implementación, evidencia y estado del repositorio reflejan la verdad.
- **Objective:** Entregar una change archivable sin artefactos ni tareas falsas.
- **Deliverables:** Checklist completo, validaciones registradas y árbol sin caches, credenciales, datos personales ni outputs generados.
- **Validation:** `openspec validate restore-multilingual-content-parity --strict`; `openspec validate --all --strict`; `openspec doctor`; `python -B tools/run_quality.py --profile handoff --format text`; plugins; `git diff --check`; inspección de `git status --short`; todas las tareas realmente completadas antes de marcarse.
- **Scope:** S.
