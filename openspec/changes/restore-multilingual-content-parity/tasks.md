## Phase 1: Baseline, contrato y puertas de calidad

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

### Task 1.4: Auditar las fuentes inglesas

- [ ] 1.4 Revisar los 24 `README.md` canónicos antes de congelar sus oleadas.
- **Objective:** Evitar propagar errores, prerrequisitos ausentes o carencias pedagógicas de la fuente.
- **Deliverables:** Resultado canónico por unidad y cola de reparaciones limitadas a exactitud, seguridad, accesibilidad o elementos necesarios de `BOOK_STYLE.md`; ampliaciones curriculares quedan fuera.
- **Validation:** Cada fuente tiene resultado explícito; toda reparación se ejecuta primero, se prueba y forma un bundle atómico con sus cuatro variantes antes de aceptar la unidad.
- **Risk:** Scope creep editorial; una capacidad nueva se remite a proposal separada.
- **Scope:** L.

### Task 1.5: Pilotar el proceso con capítulos 01–02

- [ ] 1.5 Ejecutar un piloto completo sueco/árabe para capítulos 01–02.
- **Objective:** Verificar que el flujo detecta omisiones reales y produce un lote revisable antes de escalar.
- **Deliverables:** `README.sv.md` y `README.ar.md` restaurados para capítulos 01–02, cuatro paquetes `accepted` y lecciones aprendidas incorporadas al checklist sin relajar criterios.
- **Validation:** Digests vigentes; señales automáticas; revisión lingüística y técnica; código/source refs; prerequisitos; accesibilidad; RTL/LTR; links/selectores; `git diff --check`.
- **Risk:** Ajustes del piloto pueden invalidar la plantilla; migrar sus registros antes de continuar.
- **Scope:** L.

### Task 1.6: Auditar las fuentes avanzadas publicadas

- [ ] 1.6 Revisar los `README.md` canónicos de capítulos 23–25 antes de aceptar sus oleadas.
- **Objective:** Incorporar redes, C++ y Rust al alcance editorial sin heredar aprobación de sus gates de implementación.
- **Deliverables:** Tres auditorías canónicas humanas contra sus digests actuales y reparaciones atómicas si aparecen defectos.
- **Validation:** Exactitud, seguridad, pedagogía, accesibilidad y procedencia tienen resultado explícito; los plugins de dominio son evidencia adicional, no sustitutos de review.
- **Scope:** L.

## Phase 2: Sueco y árabe, fundamentos

Todas las tareas de traducción usan la fuente congelada, el Parity Contract completo, revisión lingüística y técnica, gate común/equivalente, taxonomía/metadata `bookcheck`, plugins de ejemplo relevantes y `git diff --check`. Cada lote elimina en el mismo diff las entradas baseline que resuelve; `--update-baseline` solo puede reducir fingerprints. Un cambio canónico detiene el lote como `stale`; una reparación de fuente se integra como bundle de una unidad antes de aceptar sus locales.

### Task 2.1: Capítulos 03–04

- [ ] 2.1 Restaurar sueco y árabe para listas y diccionarios.
- **Objective:** Recuperar operaciones, ejemplos, bordes, recuperación, ejercicios y soluciones de las dos estructuras básicas.
- **Deliverables:** Cuatro variantes localizadas y cuatro registros `accepted` para capítulos 03–04.
- **Validation:** Contratos de mutabilidad/lookup y nombres públicos coinciden con la fuente; doble review, gate/equivalente, RTL/LTR y source refs pasan.
- **Scope:** L.

### Task 2.2: Capítulos 05–06

- [ ] 2.2 Restaurar sueco y árabe para sets y tuplas.
- **Objective:** Preservar semántica de unicidad, pertenencia, inmutabilidad y unpacking con práctica equivalente.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 05–06.
- **Validation:** Happy/edge/error, TODO/pistas/soluciones y outputs conservan conducta; doble review y gates pasan.
- **Scope:** L.

### Task 2.3: Capítulos 07–08

- [ ] 2.3 Restaurar sueco y árabe para colas y condicionales.
- **Objective:** Recuperar orden de operaciones, decisiones y manejo de entradas límite sin introducir conceptos posteriores.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 07–08.
- **Validation:** Prerrequisitos, ramas y errores recuperables son resolubles; doble review, gates, RTL/LTR y código pasan.
- **Scope:** L.

### Task 2.4: Capítulos 09–10

- [ ] 2.4 Restaurar sueco y árabe para input y bucles.
- **Objective:** Mantener validación de input, terminación y progresión de iteración de forma segura y observable.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 09–10.
- **Validation:** No hay loops/input sin límites o recuperación omitida; outputs, ejercicios, soluciones y doble review pasan.
- **Scope:** L.

### Task 2.5: Capítulos 11–12

- [ ] 2.5 Restaurar sueco y árabe para funciones y OOP.
- **Objective:** Conservar contratos de parámetros/retorno y el salto gradual hacia objetos.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 11–12.
- **Validation:** Jargon definido, identificadores estables, ejemplos ejecutables/source refs, doble review y gates pasan.
- **Scope:** L.

### Task 2.6: Capítulos 13–14

- [ ] 2.6 Restaurar sueco y árabe para archivos y excepciones.
- **Objective:** Recuperar recursos, paths seguros, errores esperados y recuperación antes de las unidades de ecosistema.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 13–14.
- **Validation:** Ejemplos usan paths temporales/seguros, documentan diagnóstico y cleanup; doble review, gates y RTL/LTR pasan.
- **Scope:** L.

## Phase 3: Sueco y árabe, ecosistema y avanzado

### Task 3.1: Capítulos 15–16

- [ ] 3.1 Restaurar sueco y árabe para módulos y entornos.
- **Objective:** Enseñar importación y aislamiento antes de dependencias posteriores con comandos copiables.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 15–16.
- **Validation:** Comandos, paths, plataformas declaradas y optional previews coinciden; doble review, gates y bidi pasan.
- **Scope:** L.

### Task 3.2: Capítulos 17–18

- [ ] 3.2 Restaurar sueco y árabe para persistencia y testing.
- **Objective:** Preservar contratos de datos y el vínculo entre comportamiento, riesgo y pruebas.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 17–18.
- **Validation:** Datos son ficticios/locales; tests conservan comportamiento y motivo; doble review, gates y source refs pasan.
- **Scope:** L.

### Task 3.3: Capítulos 19–20

- [ ] 3.3 Restaurar sueco y árabe para HTTP y logging.
- **Objective:** Recuperar límites de red/configuración, errores y observabilidad sin usar secretos ni targets inseguros.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 19–20.
- **Validation:** Ejemplos mantienen alcance seguro y claims verificadas; doble review, gates, bidi y referencias pasan.
- **Scope:** L.

### Task 3.4: Capítulos 21–22

- [ ] 3.4 Restaurar sueco y árabe para asyncio e introspección.
- **Objective:** Completar las unidades avanzadas con concurrencia acotada, diagnóstico y práctica evaluable.
- **Deliverables:** Cuatro variantes y registros `accepted` para capítulos 21–22.
- **Validation:** No se omiten errores, soluciones ni checkpoints; ejemplos bounded/deterministic; doble review y gates pasan.
- **Scope:** L.

### Task 3.5: Capítulos 23–25

- [ ] 3.5 Restaurar sueco y árabe para redes e interoperabilidad nativa.
- **Objective:** Completar las rutas avanzadas publicadas sin rebajar sus contratos de seguridad, toolchain, packaging o verificación.
- **Deliverables:** Dos oleadas atómicas con rollback independiente: capítulo 23 (dos variantes/registros) y capítulos 24–25 (cuatro variantes/registros).
- **Validation:** Cada oleada obtiene doble review, RTL/LTR, gates genéricos, plugins explícitos y contratos fuente contra digests vigentes; la task no se marca hasta aceptar ambas.
- **Scope:** L.

### Task 3.6: Apéndices A–B

- [ ] 3.6 Restaurar sueco y árabe para CLI y algoritmos.
- **Objective:** Recuperar rutas, ejercicios, complejidad y soluciones completas de ambos apéndices.
- **Deliverables:** Cuatro variantes y registros `accepted` para `appendix-cli-parser` y `appendix-algorithms`.
- **Validation:** CLI permanece segura/local; contratos y complejidad algorítmica coinciden; doble review, gates y bidi pasan.
- **Scope:** L.

### Task 3.7: Cerrar la banda sueco/árabe

- [ ] 3.7 Ejecutar regresión completa de las 54 variantes suecas/árabes.
- **Objective:** Detectar drift entre lotes antes de iniciar catalán.
- **Deliverables:** Informe de regresión 27×2, estados finales y correcciones de integración limitadas.
- **Validation:** 54 registros `accepted` con digests vigentes; ninguna omisión, link roto, wrapper RTL duplicado, source ref inválida o revisión pendiente.
- **Risk:** Una reparación tardía puede invalidar múltiples digests; reabrir solo registros afectados.
- **Scope:** M.

## Phase 4: Catalán, unidades tardías primero

Cada lote catalán cumple el mismo contrato de fences/metadata `bookcheck` y actualiza el baseline únicamente para eliminar fingerprints resueltos en ese lote.

### Task 4.1: Capítulos 15–16

- [ ] 4.1 Restaurar catalán para módulos y entornos.
- **Objective:** Corregir primero la pérdida observada en el inicio de la banda avanzada.
- **Deliverables:** Dos variantes catalanas y registros `accepted` para capítulos 15–16.
- **Validation:** Parity Contract, digest, review lingüística/técnica, gate/equivalente, código y enlaces localizados pasan.
- **Scope:** M.

### Task 4.2: Capítulos 17–18

- [ ] 4.2 Restaurar catalán para persistencia y testing.
- **Objective:** Recuperar datos, edge/error/recovery, pruebas y soluciones equivalentes.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 17–18.
- **Validation:** Source refs/tests y propósito pedagógico coinciden; doble review y gates pasan.
- **Scope:** M.

### Task 4.3: Capítulos 19–20

- [ ] 4.3 Restaurar catalán para HTTP y logging.
- **Objective:** Completar red, errores, seguridad y observabilidad sin reducir la ruta formativa.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 19–20.
- **Validation:** Claims, comandos, límites y recuperación coinciden; doble review y gates pasan.
- **Scope:** M.

### Task 4.4: Capítulos 21–22

- [ ] 4.4 Restaurar catalán para asyncio e introspección.
- **Objective:** Recuperar el detalle avanzado, TODOs, pistas, soluciones y evaluación.
- **Deliverables:** Dos variantes y registros `accepted` para capítulos 21–22.
- **Validation:** Prerrequisitos/previews, comportamiento y checkpoints equivalen; doble review y gates pasan.
- **Scope:** M.

### Task 4.5: Capítulos 23–25

- [ ] 4.5 Restaurar catalán para redes e interoperabilidad nativa.
- **Objective:** Completar la banda catalana avanzada con el mismo contrato pedagógico y técnico publicado.
- **Deliverables:** Dos oleadas atómicas con rollback independiente: capítulo 23 (una variante/registro) y capítulos 24–25 (dos variantes/registros).
- **Validation:** Cada oleada obtiene doble review, gates genéricos, plugins explícitos, source refs y comandos equivalentes; la task no se marca hasta aceptar ambas.
- **Scope:** L.

### Task 4.6: Apéndices A–B

- [ ] 4.6 Restaurar catalán para CLI y algoritmos.
- **Objective:** Eliminar los resúmenes parciales de ambos apéndices.
- **Deliverables:** Dos variantes y registros `accepted` para ambos apéndices.
- **Validation:** Ejercicios, hints, solutions, tests/complejidad y accesibilidad equivalen; doble review y gates pasan.
- **Scope:** M.

## Phase 5: Catalán, fundamentos e intermedio

Cada lote mantiene `--changed-from` limpio y un baseline reduction-only, además de ambas revisiones humanas.

### Task 5.1: Capítulos 01–02

- [ ] 5.1 Auditar/restaurar catalán para introducción y variables.
- **Objective:** Confirmar la base antes de aceptar el resto de la progresión catalana.
- **Deliverables:** Dos registros `accepted` y correcciones catalanas confirmadas para capítulos 01–02.
- **Validation:** Parity Contract completo, doble review y gates pasan; similitud de tamaño no se usa como aceptación.
- **Scope:** M.

### Task 5.2: Capítulos 03–04

- [ ] 5.2 Restaurar catalán para listas y diccionarios.
- **Objective:** Preservar toda la práctica y semántica de colecciones mutables.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 03–04.
- **Validation:** Contratos de código, edge/error/recovery y assessment equivalen; doble review y gates pasan.
- **Scope:** M.

### Task 5.3: Capítulos 05–06

- [ ] 5.3 Restaurar catalán para sets y tuplas.
- **Objective:** Completar conceptos y práctica de colecciones con progresión equivalente.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 05–06.
- **Validation:** Mapas completos, código/source refs y doble review pasan.
- **Scope:** M.

### Task 5.4: Capítulos 07–08

- [ ] 5.4 Restaurar catalán para colas y condicionales.
- **Objective:** Recuperar casos, decisiones y ejercicios omitidos sin adelantar conceptos.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 07–08.
- **Validation:** Prerrequisitos, outputs, recoverable errors, soluciones y gates pasan.
- **Scope:** M.

### Task 5.5: Capítulos 09–10

- [ ] 5.5 Restaurar catalán para input y bucles.
- **Objective:** Mantener validación, límites y razonamiento iterativo completos.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 09–10.
- **Validation:** Ejemplos seguros/bounded, checkpoints, doble review y gates pasan.
- **Scope:** M.

### Task 5.6: Capítulos 11–12

- [ ] 5.6 Restaurar catalán para funciones y OOP.
- **Objective:** Completar el puente desde funciones hacia objetos con vocabulario introducido.
- **Deliverables:** Dos variantes/registros `accepted` para capítulos 11–12.
- **Validation:** APIs estables, glosario/conceptos, práctica y doble review pasan.
- **Scope:** M.

### Task 5.7: Capítulos 13–14

- [ ] 5.7 Restaurar catalán para archivos y excepciones.
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

La cercanía aparente de español no lo exime de revisión. Cada tarea audita dos unidades y modifica solo las diferencias confirmadas.

Cada lote español usa la taxonomía/metadata `bookcheck` común y elimina en el mismo diff cualquier fingerprint heredado que resuelva, sin añadir deuda al baseline.

### Task 6.1: Capítulos 01–02

- [ ] 6.1 Auditar/corregir español para capítulos 01–02.
- **Objective:** Verificar que introducción y variables conservan todo el aprendizaje canónico.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Mapa completo, doble review, gate/equivalente y digests pasan.
- **Scope:** M.

### Task 6.2: Capítulos 03–04

- [ ] 6.2 Auditar/corregir español para capítulos 03–04.
- **Objective:** Confirmar semántica y práctica de listas/diccionarios.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Código, ejemplos, ejercicios, edge/error/recovery y gates pasan.
- **Scope:** M.

### Task 6.3: Capítulos 05–06

- [ ] 6.3 Auditar/corregir español para capítulos 05–06.
- **Objective:** Confirmar paridad completa de sets y tuplas.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Mapa, doble review, source refs y gates pasan.
- **Scope:** M.

### Task 6.4: Capítulos 07–08

- [ ] 6.4 Auditar/corregir español para capítulos 07–08.
- **Objective:** Confirmar colas y condicionales sin gaps pedagógicos.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Prerrequisitos, casos, soluciones, assessment y gates pasan.
- **Scope:** M.

### Task 6.5: Capítulos 09–10

- [ ] 6.5 Auditar/corregir español para capítulos 09–10.
- **Objective:** Confirmar input y bucles seguros, bounded y explicados.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Código/output/recovery, doble review y gates pasan.
- **Scope:** M.

### Task 6.6: Capítulos 11–12

- [ ] 6.6 Auditar/corregir español para capítulos 11–12.
- **Objective:** Confirmar funciones y OOP con dependencia conceptual correcta.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** APIs, jargon, ejercicios/soluciones y gates pasan.
- **Scope:** M.

### Task 6.7: Capítulos 13–14

- [ ] 6.7 Auditar/corregir español para capítulos 13–14.
- **Objective:** Confirmar archivos/excepciones, paths y recuperación segura.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Seguridad, source refs, doble review y gates pasan.
- **Scope:** M.

### Task 6.8: Capítulos 15–16

- [ ] 6.8 Auditar/corregir español para capítulos 15–16.
- **Objective:** Confirmar módulos/entornos y comandos equivalentes.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Tooling/paths/previews, doble review y gates pasan.
- **Scope:** M.

### Task 6.9: Capítulos 17–18

- [ ] 6.9 Auditar/corregir español para capítulos 17–18.
- **Objective:** Confirmar persistencia/testing y riesgos cubiertos.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Datos ficticios, tests, edge cases, doble review y gates pasan.
- **Scope:** M.

### Task 6.10: Capítulos 19–20

- [ ] 6.10 Auditar/corregir español para capítulos 19–20.
- **Objective:** Confirmar HTTP/logging, errores, límites y seguridad.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Targets/secretos/claims, source refs, doble review y gates pasan.
- **Scope:** M.

### Task 6.11: Capítulos 21–22

- [ ] 6.11 Auditar/corregir español para capítulos 21–22.
- **Objective:** Cerrar gaps avanzados confirmados, incluida cualquier diferencia en introspección.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Async bounded, APIs de introspección, exercises/solutions/checkpoints, doble review y gates pasan.
- **Scope:** M.

### Task 6.12: Capítulos 23–25

- [ ] 6.12 Auditar/corregir español para redes e interoperabilidad nativa.
- **Objective:** Confirmar que los tres capítulos avanzados conservan contratos, recuperación, seguridad y evaluación.
- **Deliverables:** Dos oleadas atómicas con rollback independiente: capítulo 23 (un registro) y capítulos 24–25 (dos registros), más las correcciones españolas necesarias.
- **Validation:** Cada oleada obtiene doble review, gates, plugins, comandos y claims de plataforma contra los digests actuales; la task no se marca hasta aceptar ambas.
- **Scope:** L.

### Task 6.13: Apéndices A–B

- [ ] 6.13 Auditar/corregir español para ambos apéndices.
- **Objective:** Confirmar CLI/algoritmos sin asumir equivalencia por longitud.
- **Deliverables:** Dos registros `accepted` y correcciones necesarias.
- **Validation:** Comandos, complejidad, tests, soluciones, doble review y gates pasan.
- **Scope:** M.

## Phase 7: Integración, procedencia y aceptación global

### Task 7.1: Revisar procedencia del material tocado

- [ ] 7.1 Verificar origen/licencia de ejercicios, datasets, diagramas o prosa sustancial adaptados durante las oleadas.
- **Objective:** Evitar que la restauración introduzca material incompatible con CC BY-SA.
- **Deliverables:** Atribuciones requeridas cerca del material o en sección dedicada; confirmación original/compatible para cada material tocado; ningún barrido retroactivo de contenido no modificado.
- **Validation:** Cada adaptación tocada tiene fuente, licencia y obligación registrada; material dudoso se reemplaza por ejemplo original o bloquea el lote.
- **Scope:** M.

### Task 7.2: Reconciliar navegación, capabilities y changes activas

- [x] 7.2 Validar selectores, links localizados e índices con capítulos 23–25 publicados.
- **Objective:** Mantener navegación coherente bajo integración concurrente.
- **Deliverables:** Correcciones atómicas de índices y aliases de anchors deliberados solo si hacen falta; preservación numérica de 23–25 con sus cinco targets.
- **Validation:** English mirrors identical; links/fragments/aliases resuelven; 23→24→25 aparece en orden en los seis índices y no implica aceptación humana de sus variantes.
- **Risk:** Conflictos de rebase en índices; integrar al final y releer las specs/capabilities vigentes y las changes activas relevantes.
- **Scope:** M.

### Task 7.3: Ejecutar aceptación global 27×5

- [ ] 7.3 Verificar las 27 fuentes y 108 variantes como un conjunto coherente.
- **Objective:** Demostrar paridad, no solo completar lotes aislados.
- **Deliverables:** Informe final con 108 registros `accepted`, 27 digests vigentes, cero blockers/stale y trazabilidad a requisitos/scenarios.
- **Validation:** Gate común `python -B tools/validate_book.py` o equivalente completo; plugins relevantes; links/selectors/mirror/RTL/headings/taxonomía y metadata `bookcheck`/alt/source refs; baseline sin entradas stale y con diffs reduction-only; código/tests; doble review; seguridad; accesibilidad; `git diff --check`.
- **Risk:** Un cambio tardío puede reabrir registros; invalidar y revisar solo el alcance afectado.
- **Scope:** L.

### Task 7.4: Cerrar OpenSpec y comprobar higiene

- [ ] 7.4 Confirmar que implementación, evidencia y estado del repositorio reflejan la verdad.
- **Objective:** Entregar una change archivable sin artefactos ni tareas falsas.
- **Deliverables:** Checklist completo, validaciones registradas y árbol sin caches, credenciales, datos personales ni outputs generados.
- **Validation:** `openspec validate restore-multilingual-content-parity --strict`; gate global/plugins; `git diff --check`; inspección de `git status --short`; todas las tareas realmente completadas antes de marcarse.
- **Scope:** S.
