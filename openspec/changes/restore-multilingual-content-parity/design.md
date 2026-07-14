## Context

La verdad publicada contiene 25 capítulos y 2 apéndices. Cada unidad tiene un `README.md` inglés canónico y cuatro variantes localizadas. La interfaz ejecutable y el baseline de `add-book-quality-gates` están disponibles y se consumen; su change de origen permanece activa y no archivable hasta completar procedencia, la matriz final y la revisión humana.

El inventario inicial revela una asimetría suficiente para definir prioridades sin usar el tamaño como aceptación: sueco y árabe suelen conservar solo una fracción de la lección inglesa, catalán pierde secciones especialmente a partir de los capítulos intermedios/tardíos y español se aproxima más al original, aunque existen diferencias que requieren auditoría. La comparación por palabras sirve para encontrar riesgo; no demuestra que una traducción enseñe lo mismo.

El público incluye principiantes jóvenes. Una omisión de recuperación de errores, advertencias, prerrequisitos o soluciones no es un defecto cosmético: cambia qué puede aprender y ejecutar con seguridad la persona lectora.

## Goals / Non-Goals

### Goals

- Restablecer equivalencia semántica y pedagógica entre cada fuente inglesa y sus cuatro variantes para las 27 unidades publicadas.
- Mantener una progresión tranquila y resoluble: prerrequisitos antes de uso, previews opcionales explícitos y el microciclo objetivo/contexto → teoría mínima → predicción → ejecución → observación → modificación → verificación → explicación.
- Preservar el contrato técnico de ejemplos, comandos, nombres públicos, outputs, referencias a companion sources y verificaciones.
- Entregar mejoras en lotes pequeños, revisables, reversibles y con evidencia reproducible.
- Integrarse con controles compartidos sin duplicar un segundo validador global.
- Mantener accesibilidad, RTL/LTR, navegación localizada, seguridad, higiene y obligaciones de licencia en todo material tocado.

### Non-Goals

- Implementar o alterar los contratos de dominio de capítulos que pertenecen a otras changes.
- Producir traducción literal o igualar conteos de palabras.
- Crear contenido curricular nuevo para rellenar diferencias de longitud.
- Sustituir criterio lingüístico/técnico humano con heurísticas.
- Renombrar paths públicos o reorganizar la numeración.

## Architecture Snapshot

- **Fuente canónica por unidad:** `README.md` inglés de cada capítulo/apéndice. Antes de abrir un lote se registra su digest y se audita si contiene el material necesario para servir de fuente correcta.
- **Variantes bajo revisión:** `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`; cada una se evalúa contra la misma revisión congelada de la fuente.
- **Paquete de paridad:** `tools/parity_manifest.json` conserva únicamente el índice de topología; `tools/parity/sources/<unit>.json` y `tools/parity/records/<unit>/<locale>.json` son los registros persistentes granulares con digests, mapa de cobertura, excepciones, resultados automáticos, decisiones humanas independientes y bindings derivados de procedencia. Los companions/canonical se ligan al source leaf y una entrada que cubre una página localizada se liga solo a su locale leaf; `ATTRIBUTIONS.toml` sigue siendo la autoridad de la decisión. El paquete de capítulo se genera como una proyección read-only de una fuente, sus cuatro registros y las entradas aplicables, referenciadas por ID y digest normalizado de entrada/evidencia; no se guarda como segunda autoridad ni almacena datos personales.
- **Paquete raíz:** `tools/parity/root-publication.json` es el único leaf autoritativo para los seis índices raíz. Registra auditoría canónica de `README.md`, render separado para los seis paths, revisión lingüística/técnica de `README.{es,ca,sv,ar}.md`, bidi de `README.ar.md` y referencias/digests a la procedencia global aplicable sin copiar su decisión. `--root-review-packet` solo proyecta ese leaf, digests y targets; `README.en.md` comparte la auditoría canónica porque debe ser byte-idéntico, pero conserva su propia decisión de render.
- **Consumidor de sign-off:** `tools/publication_signoff.json` está fuera de `tools/parity/` y es la autoridad únicamente para el sign-off común. Referencia evidence previa mediante digests; nunca es input de un source/locale/root leaf. `add-book-quality-gates` posee sus decisiones humanas y `--verify-publication-signoff` más el perfil `handoff` verifican frescura sin escribirlas.
- **Gate común:** la interfaz implementada por `add-book-quality-gates`, `python -B tools/validate_book.py [--changed-from REF]`, aporta señales de shape, links, selector, espejo raíz, RTL, headings, fences, alt text y source refs. Los fences nuevos/modificados usan exactamente `runnable|expected-error|compile-only|source-ref|todo|illustrative|output` y la metadata versionada `bookcheck`. Los plugins de capítulo siguen siendo dueños de sus pruebas de dominio.
- **Revisión humana:** la fuente registra auditoría canónica y accesibilidad renderizada; cada locale registra puertas lingüística, técnica/pedagógica y de accesibilidad renderizada, y árabe registra además bidi/copy-paste. Cada decisión conserva resultado, rol, fecha, notas, digests de contenido y, para render/bidi, digest de perfil y entorno observado. Una persona puede cubrir varios roles solo con competencia demostrable y cada checklist permanece independiente.
- **Perfil de render:** `tools/render_review_profile.json` versiona viewports, zoom/reflow, tareas de teclado/AT, checklist bidi y assets globales que participan en el render. La evidencia registra su SHA-256 más renderer, browser, OS y tecnología asistiva/versiones realmente usados; un cambio de página, perfil o asset declarado invalida solo las decisiones dependientes.
- **Navegación:** enlaces internos y selectores apuntan a la variante del mismo idioma cuando existe. Los índices se editan atómicamente solo hacia targets existentes cuya implementación de dominio esté completada, archivada o baselined con evidencia; el estado humano `accepted` de paridad se registra aparte y no controla la conservación de una entrada ya publicada. Un directorio parcial no basta.
- **Changes coordinadas:** capítulos 23, 24 y 25 conservan validadores y contratos de dominio propios. Este esfuerzo inventaría sus documentos publicados, pero no reclama ni modifica su implementación de dominio.

## Parity Contract

Cada mapa unidad/idioma SHALL comprobar como mínimo:

1. Título, propósito, resultado construible, objetivos y prerrequisitos.
2. Orden conceptual y definiciones necesarias antes del uso.
3. Contexto real y pregunta/predicción antes de ejecutar.
4. Ejemplos completos, etiqueta de bloque, output significativo y explicación.
5. Modificación guiada/TODO, pista útil y condición observable de éxito.
6. Happy path, caso límite, fallo recuperable, diagnóstico y recuperación.
7. Errores comunes sin lenguaje culpabilizador.
8. Soluciones explicadas y no solo código final.
9. Checkpoint/rúbrica, resumen y reflexión final.
10. Advertencias de seguridad, compatibilidad y alcance.
11. Enlaces, selector, navegación, alt text y equivalentes textuales.
12. Identificadores públicos, comandos, paths, datos de prueba y referencias a fuente.

Una sección puede reordenarse o expresarse de forma idiomática si conserva la dependencia pedagógica y el resultado observable. No se requiere correspondencia de headings uno-a-uno cuando la estructura localizada sea más natural, pero cada elemento del mapa debe tener evidencia concreta.

## Decisions

### Decision: Congelar la fuente inglesa por lote

Cada lote registra el digest del `README.md` canónico antes de traducir. Si la fuente cambia antes de aceptar el lote, su revisión queda stale y debe reconciliarse o repetirse.

**Rationale:** evita aprobar una traducción contra una versión que ya no existe.

**Alternative considered:** comparar siempre contra `HEAD`; se descarta porque un cambio concurrente puede invalidar silenciosamente trabajo ya revisado.

### Decision: Auditar la fuente antes de propagarla

La fuente inglesa no se asume perfecta. Si presenta un error factual, un ejemplo roto, un prerrequisito ausente o una carencia respecto a `BOOK_STYLE.md` necesaria para completar el mismo aprendizaje, se corrige primero dentro del mismo lote y después se propaga a todas las variantes afectadas. No se añade currículo nuevo.

**Rationale:** paridad con una fuente incorrecta multiplicaría el defecto.

### Decision: Una unidad por paquete y hasta dos idiomas por sublote

Un paquete de cierre pertenece exactamente a un capítulo o apéndice. Dentro de él, un sublote modifica uno o dos locales de esa unidad, además de la corrección canónica y evidencia estrictamente necesarias. Sueco y árabe pueden compartir sublote cuando existen revisores competentes; si no, se separan. Los dos apéndices pueden coordinarse en el mismo hito, pero conservan paquetes, digests, aceptación y rollback independientes.

**Rationale:** evita 27 proposals duplicadas, limita conflictos y permite cerrar o revertir una unidad sin mezclar su evidencia humana con otra.

**Alternative considered:** una change por capítulo; se descarta porque duplicaría requisitos, complicaría el sync/archivo de una misma capability y no resolvería la aceptación global 27×5.

### Decision: Un paquete raíz separado cierra la superficie publicada

Los seis índices raíz no pertenecen a ninguna unidad y no se fuerzan dentro de los 27 paquetes. Un único paquete raíz read-only consume `tools/parity/root-publication.json`: `README.md` aporta la auditoría canónica compartida con su mirror byte-idéntico; los cuatro índices localizados reciben revisión lingüística y técnica/pedagógica; los seis reciben accesibilidad renderizada; y `README.ar.md` añade bidi/copy-paste. El leaf conserva roles, fechas, notas, digests y estado independiente por path. Después de cerrar el leaf, el sign-off de `add-book-quality-gates` referencia esos IDs/digests en vez de copiar la decisión; su digest no se almacena en el leaf ni participa en su invalidación.

**Rationale:** el handoff real cubre 141 páginas y 28 páginas árabes; cerrar solo 135 páginas de unidad dejaría navegación, rutas curriculares y bidi raíz sin evidencia humana.

**Alternative considered:** asumir que la Task 7.2 de `add-book-quality-gates` cubre implícitamente los índices; se descarta porque un sign-off agregado sin paths/digests no permite invalidación ni demuestra qué página se revisó.

El root leaf usa esta forma canónica:

- `schema_version=2`, `leaf_kind="root-publication"` y estado derivado;
- auditoría canónica ligada a los digests byte-idénticos de `README.md`/`README.en.md`;
- seis page objects en orden fijo, cada uno con path/digest y sus gates aplicables; `README.en.md` solo añade render al audit compartido, los cuatro locales añaden lingüístico/técnico/render y árabe añade bidi;
- `provenance` ordenada por ID con `{id, status, provenance_sha256, covered_paths}` para entradas que cubren un root path o un asset/licencia local referenciado por él.

Cada gate humano root tiene un `decision_id` estable `root:<path>:<gate>` (`canonical`, `linguistic`, `technical`, `rendered-accessibility` o `bidi`) y `decision_sha256 = SHA-256(canonical_json_bytes({decision_id, path, review}))`. La auditoría canónica compartida usa `root:README.md:canonical` y liga ambos English digests; no se duplica para `README.en.md`.

Una entrada root de procedencia cambia solo ese gate derivado; el badge también participa como asset de render y por tanto invalida los renders dependientes. El root leaf no contiene datos del sign-off consumidor.

### Decision: Sign-off común como consumidor unidireccional verificable

`tools/publication_signoff.json` usa schema 1 y contiene `state` (`pending|changes-requested|stale|approved`), `inputs`, `signoff_input_sha256` y objetos humanos separados `book_editor_review`, `accessibility_review` y `provenance_review`. `inputs` contiene:

- `parity_index_sha256` y `unit_evidence_sha256`, este último calculado sobre la lista canónica path-ordenada de los 135 leaf digests;
- `unit_provenance_sha256`, calculado sobre `canonical_json_bytes` de todas las referencias derivadas `{unit, id, status, provenance_sha256, covered_paths}` de los 27 paquetes, ordenadas por `(unit, id)`; esto liga también companion paths que no son leaves;
- `root_leaf_sha256` y la lista `{decision_id, decision_sha256}` de sus decisiones, ordenada por ID; el `path` forma parte del payload hasheado de cada decisión y permanece visible en el paquete raíz, sin duplicarse en la referencia compacta del sign-off;
- `attributions_sha256` y `render_profile_sha256`;
- `quality_contract_sha256`, calculado sobre la lista path-ordenada de digests de `BOOK_STYLE.md`, `tools/parity_review.py`, `tools/validate_book.py`, `tools/run_quality.py`, `tools/book_quality.toml` y `tools/quality_matrix.toml`. Los handoffs narrativos quedan fuera para poder referenciar el sign-off después sin crear un ciclo.

`signoff_input_sha256` es el SHA-256 de `canonical_json_bytes(inputs)` y cada review se liga a él con result, role, review date y notes. El estado `approved` es derivado y exige los tres reviews aprobados contra inputs actuales. `--verify-publication-signoff tools/publication_signoff.json` recomputa referencias/digests, rechaza pending/stale y no muta ningún archivo; `tools/run_quality.py --profile handoff` lo invoca. `tools/BOOK_QUALITY_REVIEW.md` y `openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md` referencian el digest del sign-off para el handoff narrativo, pero sus propios digests no vuelven al JSON ni a los leaves.

**Rationale:** materializa qué evidencia consumió el sign-off y permite invalidación automática sin un ciclo root → sign-off → root.

**Alternative considered:** guardar el sign-off dentro del root leaf; se descarta porque cualquier referencia recíproca produciría un ciclo o haría que una decisión agregada reescribiese evidence de página ya aprobada.

### Decision: Prioridad por riesgo y dependencia curricular

El orden es:

1. Sueco y árabe, capítulos 01–25 y apéndices, en orden de prerrequisitos.
2. Catalán, primero capítulos 15–25 y apéndices; después capítulos 01–14.
3. Español, auditoría completa en orden y corrección solo de gaps confirmados.

Dentro de cada banda los hitos pueden coordinar pares consecutivos (`01–02`, `03–04`, …), pero cada unidad conserva su paquete y cierre independiente. Los capítulos 23, 24 y 25 se revisan individualmente con competencia técnica de redes, C++ o Rust; los apéndices se coordinan al final sin fusionar su evidencia. Un defecto de seguridad o exactitud puede adelantarse y queda documentado.

**Rationale:** atiende primero las mayores pérdidas observadas sin dejar que las unidades posteriores dependan de fundamentos aún incompletos.

### Decision: Automatización como señal, revisión humana como aceptación

Los checks automatizados detectan archivos ausentes, links, wrappers, headings, fences, clasificaciones/metadata `bookcheck`, referencias, divergencias estructurales y cambios de digest. Conteos y ratios generan avisos de triaje, no PASS/FAIL semántico por sí solos. La paridad semántica requiere aprobación lingüística y técnica/pedagógica; el estado final `accepted` exige además auditoría/render canónicos, render localizado, procedencia aplicable y bidi árabe como gates humanos independientes.

**Rationale:** una traducción larga puede ser incorrecta y una formulación más breve puede ser completamente equivalente.

### Decision: Reusar la implementación disponible del gate común

La interfaz ejecutable de `add-book-quality-gates` ya está disponible: esta change consume `python -B tools/validate_book.py --changed-from <ref>` y su baseline sin duplicar parsers globales. Cuando un lote resuelve un fingerprint heredado, ejecuta el flujo aprobado `--update-baseline` y entrega en el mismo diff una reducción exacta; nunca añade fingerprints, ensancha una supresión ni conserva una entrada stale. La change de origen sigue activa por sus gates de procedencia, verificación limpia y revisión humana; ese estado no convierte su implementación disponible en un fallback ni permite atribuirle aceptación humana.

**Rationale:** permite avanzar trabajo editorial y evita dos fuentes de verdad para validación estructural.

### Decision: Código y source refs son contratos compartidos

Los bloques localizados conservan imports, APIs, identificadores, control flow relevante, argumentos, resultados y comandos del canónico. Todo fence nuevo/modificado conserva la clasificación canónica o usa exactamente `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative` u `output`, con metadata `bookcheck` cuando corresponda; no se crea una convención localizada paralela. Comentarios y strings destinados al lector pueden localizarse si los tests y source refs siguen siendo válidos. Un bloque runnable se ejecuta una vez desde su companion source probado, no cinco copias divergentes; cualquier ejemplo inline divergente se verifica explícitamente.

**Rationale:** reduce drift técnico sin prohibir traducción natural.

### Decision: Evidencia de revisión sin datos personales innecesarios

El registro granular conserva unidad, idioma, digest, fecha, roles de revisión, checklist, comandos/resultados y excepciones. La auditoría canónica, revisión lingüística, revisión técnica/pedagógica, accesibilidad renderizada y bidi tienen objetos separados. No contiene datos de estudiantes, credenciales ni secretos; los nombres de revisores no son requisito de la spec. Una edición localizada modifica solo su archivo unidad/locale; el índice de topología no se regenera durante review ordinario.

### Decision: Migración atómica a evidence schema v2

`SCHEMA_VERSION` y `LEAF_SCHEMA_VERSION` avanzan de 1 a 2; `INDEX_SCHEMA_VERSION` permanece en 2 porque la topología de unidades no cambia. `--migrate-review-schema` acepta únicamente un store íntegramente v1 sin root leaf o íntegramente v2 con root leaf. Para v1 crea un sibling staging completo, impredecible y same-filesystem junto a `tools/parity/`, valida 27 fuentes/108 records más `root-publication.json` —136 leaves—, compara el snapshot original y publica el directorio entero mediante Linux `renameat2(RENAME_EXCHANGE)`, el primitive ya exigido para migraciones de store. Un store mixto falla antes de staging/escritura y conserva su input mixto byte por byte; una edición concurrente o un host v1 sin ese primitive conserva el input v1 byte por byte; v2 válido es un no-op idempotente.

Mapping v1→v2:

- `source.audit` se sustituye por `canonical_review`; `pending-human-review` queda pending y un legacy `approved` sin rol/fecha también vuelve a pending porque no aporta evidencia suficiente. Se añade `rendered_accessibility_review` pending y un binding `provenance` derivado para la página canónica y companions de unidad.
- Se conservan `linguistic_review` y `technical_review` solo cuando su schema, campos humanos exigibles y ambos digests siguen válidos; un review legacy incompleto vuelve a pending. Se añaden `rendered_accessibility_review` pending, `provenance` derivada para la página localizada y, solo para `ar`, `bidi_review` pending.
- Se crea `root-publication.json` con los seis paths/digests actuales y todos sus gates humanos en pending; ninguna señal estructural ni sign-off agregado preexistente se transforma en aprobación de página.
- `linguistic-reviewed` y `technical-reviewed` se mapean a `human-review-in-progress`. Cualquier legacy `accepted` se rebaja a `human-review-in-progress` hasta aprobar los gates nuevos; otros estados válidos se preservan.
- Tras el exchange, el sibling de staging conserva temporalmente el store v1. El snapshot compara todo el árbol —archivos esperados, directorios, symlinks y entradas extra— para no perder una edición concurrente de topología. Solo se elimina después de volver a cargar y validar v2; si el reload falla, otro `RENAME_EXCHANGE` restaura v1 antes de limpiar el sibling. Si también falla ese rollback, se conserva ese recovery same-filesystem dentro del repositorio, se informa su path relativo sin afirmar éxito y cualquier reintento permanece bloqueado hasta recuperación manual. No se deja backup ni staging tras una migración correcta.
- `--export-monolith` mantiene round trip byte-exacto solo para leaf schema 1 y rechaza schema 2 antes de crear output. `--export-review-bundle <path>` exporta desde schema 2 un objeto JSON canónico con index, 27 sources, 108 records y root publication, sin cambiar el store; importarlo no es una operación soportada ni una vía de aprobación.

**Alternative considered:** ampliar leaves v1 opcionalmente; se descarta porque mixed-version y campos ausentes permitirían interpretar evidencia incompleta de forma distinta entre writers.

### Decision: Procedencia referenciada, no duplicada

`ATTRIBUTIONS.toml` sigue siendo la única autoridad de procedencia. Para cada entrada aplicable, el paquete calcula `provenance_sha256` sobre `canonical_json_bytes({inventory_schema_version, entry, evidence: [{path, sha256}, ...]})`: `entry` incluye todos los campos permitidos por el schema vigente, con keys canónicas y `paths` normalizados/ordenados; evidence se ordena por path. Un campo desconocido, path ausente o inseguro falla cerrado. Los source/locale/root leaves guardan solo `{id, status, provenance_sha256, covered_paths}` como binding derivado contra el cual se revisó; nunca copian ni deciden fuente/licencia. Una entrada de companion/canonical bloquea su unidad, una entrada de página localizada bloquea solo ese locale y `LICENSE`, `icons/cc-by-sa.svg` u otro asset local no-Markdown enlazado desde un índice son gates globales. Un cambio en schema, entrada o path vuelve stale únicamente esos bindings y exige confirmación explícita antes de restaurar `accepted`, mientras un diagnóstico root global puede seguir bloqueando la promoción automática completa sin convertir una entrada ajena de capítulo en gate semántico de otra unidad.

## Review Packet and State Model

Cada unidad/idioma usa el estado derivado:

`inventoried → source-frozen → drafted → automated-signals-pass → human-review-in-progress → accepted`

- Un cambio de digest canónico mueve el registro a `stale` hasta reconciliación.
- Un fallo de link, código, RTL, seguridad o accesibilidad mueve el registro a `blocked`.
- Una diferencia intencional usa `exception` con justificación, alcance y aprobación lingüística/técnica; no sirve para omitir contenido por comodidad.
- `human-review-in-progress` no impone un orden entre gates y puede representar cualquier subconjunto genuinamente completado.
- Solo `accepted` permite marcar completada la subtask de locale correspondiente.
- El estado es un resumen derivado; nunca reemplaza los objetos independientes de review. `accepted` exige auditoría/render canónicos, procedencia aplicable, accesibilidad renderizada local y, para árabe, bidi, además de los gates lingüístico y técnico/pedagógico.
- El root leaf usa el mismo principio fail-closed: solo llega a `accepted` cuando sus seis paths y todos los gates humanos de página aplicables pasan; no depende del sign-off consumidor y no modifica ni hereda el estado de ningún paquete de unidad.

El paquete señala cada elemento del Parity Contract con referencia a sección/línea o una explicación breve. Incluye una fuente y sus cuatro locales, decisiones de procedencia aplicables y los targets de render; se deriva de las particiones autoritativas mediante una salida determinista y read-only. Los números de palabras, headings y fences se guardan como observaciones, no como veredicto.

## Rendered Accessibility and Bidi Evidence

- Cada una de las 135 páginas de unidad y los seis índices raíz se inspeccionan a `320×568`, `1280×800` y zoom/reflow al `200 %`.
- La revisión registra headings/orden de lectura, teclado, tecnología asistiva, links, tablas, imágenes/equivalentes, contraste aplicable y ausencia de significado dependiente solo de color o posición.
- Cada una de las 28 páginas árabes añade puntuación/listas RTL, texto mixto, números/URLs y copy/paste LTR de comandos, rutas e identificadores.
- `tools/render_review_profile.json` declara la matriz mínima y los assets globales. Cada decisión conserva `profile_sha256`, el entorno real normalizado (`renderer`, `browser`, `os`, `assistive_technology` y versiones o `not-applicable` justificado) y `render_input_sha256 = SHA-256(canonical_json_bytes({path, page_sha256, profile_sha256, assets: [{path, sha256}, ...], environment}))`, con assets ordenados por path.
- Los checks de estructura pueden preparar targets y detectar defectos conservadores, pero no escriben `approved`, rol, fecha ni notas humanas.
- Un cambio de page digest, profile digest o asset global declarado invalida únicamente las decisiones de render/bidi dependientes; no promueve ni borra evidencia no relacionada.

## Arabic and Bidirectional Text

- Cada `README.ar.md` mantiene exactamente un `<div dir="rtl">` exterior balanceado.
- Code fences, código inline, comandos, rutas, URLs, APIs, nombres de archivos, outputs y trazas se conservan legibles LTR mediante estructura Markdown/HTML adecuada; no se insertan marcas invisibles que alteren copy/paste.
- El selector de idiomas queda dentro de una posición consistente sin duplicar wrappers.
- La revisión manual comprueba lectura visual y copia de comandos, además del parser automatizado.

## Accessibility and Navigation

- Un H1 por documento y jerarquía de headings sin saltos.
- Links descriptivos, selector estándar y navegación hacia la variante localizada disponible.
- Headings ya enlazados conservan su anchor deliberado o añaden un alias HTML explícito inventariado y probado cuando una traducción/revisión necesita renombrarlos.
- Toda imagen significativa conserva alt text localizado y explicación textual equivalente; tablas complejas reciben alternativa legible.
- Ninguna instrucción depende solo de color, posición, icono o dirección visual.
- Los índices se corrigen atómicamente, conservan `README.md == README.en.md` byte a byte y mantienen los capítulos 23–25 publicados en orden numérico con sus cinco targets existentes.

## Technical Capability Coordination

- **`add-book-quality-gates`:** esta change consume su interfaz y baseline disponibles, aunque la change de origen siga activa y no archivable. El gate común detecta estructura y conserva la frontera de publicación/procedencia; esta change posee la evidencia humana por página y el paquete de unidad que el sign-off global consume, sin duplicar la decisión final.
- **Capítulo 23:** su companion y plugin de redes siguen perteneciendo a `teach-python-network-programming`; sus cinco documentos entran en el inventario de paridad.
- **Capítulo 24:** su companion y plugin C++ siguen perteneciendo a `teach-python-cpp-integration`; sus cinco documentos entran en el inventario de paridad.
- **Capítulo 25:** su companion y plugin Rust siguen perteneciendo a `teach-python-rust-integration`; sus cinco documentos entran en el inventario de paridad.
- Las changes técnicas de origen pueden cerrarse o archivarse de forma independiente. Ese estado no satisface la auditoría canónica ni la aceptación humana localizada.
- Inventariar estos documentos no declara que sus fuentes o traducciones hayan recibido revisión humana.
- Antes de editar un índice o herramienta compartida se releen las specs/capabilities vigentes y las changes activas relevantes, y se rebasa sobre su estado implementado real.

## Risks / Trade-offs

- **Volumen de 108 variantes:** los lotes pequeños aumentan coordinación → índice estable, registros por fuente y unidad/locale, estados explícitos y pares consecutivos.
- **Fluidez vs literalidad:** un traductor puede omitir detalle para sonar natural → mapa semántico por resultado, no correspondencia de frases.
- **Canonical drift:** cambios ingleses invalidan reviews → digest y estado `stale`.
- **Falsa confianza por métricas:** conteos similares ocultan errores → señales solo de triaje y gates humanos independientes.
- **Competencia de revisión escasa:** puede bloquear un idioma → no autoaprobar; mantener lote en `drafted` o `blocked` hasta review competente.
- **Paquete agregado se convierte en segunda autoridad:** reviewers editan una exportación → generar el paquete read-only desde source/locale leaves y rechazar cualquier intento de importarlo como aprobación.
- **Aprobación estructural se confunde con accesibilidad:** wrappers/headings pasan pero el render falla → objetos humanos separados, targets exactos y `accepted` fail-closed.
- **Entorno de render deriva:** una página no cambia pero sí renderer/CSS/AT → perfil versionado, entorno registrado e invalidación por `render_input_sha256`.
- **Procedencia ajena bloquea una unidad:** una entrada de capítulo no relacionada se trata como global → intersección exacta de paths; solo LICENSE/badge permanecen gates de publicación global.
- **Conflicto con tooling concurrente:** duplicación o baseline divergente → consumir la interfaz común y limitar esta change a evidencia de paridad.
- **Drift en índices 23–25:** un rebase puede borrar enlaces publicados → mirrors byte-idénticos, targets localizados existentes y validación de links.
- **Propagar errores del inglés:** traducción fiel de un defecto → auditoría canónica previa y corrección sincronizada.
- **Attribution drift:** adaptar material durante traducción puede introducir obligaciones → preferir redacción original y revisar procedencia solo del material tocado.

## Migration Plan

1. Inventariar 27 fuentes y 108 variantes en el índice y almacén granular; registrar gaps y prioridad sin editar contenido.
2. Añadir el perfil de render v1, crear el root leaf pending y migrar atómicamente los 135 leaves v1 a los 136 leaves v2 con `--migrate-review-schema`; verificar staging, CAS, reload, idempotencia y rollback, sin conservar o inventar una aprobación incompatible.
3. Generar los paquetes read-only por unidad y raíz, añadir `tools/publication_signoff.json` pending y el verificador consumidor, y conectarlos a la implementación disponible del gate común y a `ATTRIBUTIONS.toml`.
4. Ejecutar un piloto sueco/árabe con capítulos 01–02, un paquete por unidad; ajustar el checklist sin relajar aceptación.
5. Completar sueco/árabe por hitos consecutivos y paquetes independientes, y después apéndices.
6. Completar catalán empezando por 15–25/apéndices y luego 01–14.
7. Auditar y corregir español por hitos, sin asumir paridad por similitud de tamaño.
8. Reconciliar navegación, changes concurrentes y digests; completar el paquete raíz.
9. Registrar los tres sign-offs comunes contra `signoff_input_sha256`, actualizar el handoff narrativo por referencia y verificar el consumidor sin copiar decisiones.
10. Ejecutar regresión global y publicar/archivar solo cuando los 27 paquetes, el paquete raíz, los 108 registros y el sign-off consumidor estén aceptados y todos los gates pasen.

Cada lote es revertible por archivos de unidad y su evidencia. Revertir un lote no altera paths ni estados de otros lotes; su registro vuelve a la fase anterior.

## Open Questions

- Ninguna bloqueante. La capability `partitioned-parity-evidence` conserva el índice/topología de unidades, aislamiento y escrituras atómicas, amplía de forma explícita los leaves humanos y mantiene el sign-off consumidor fuera de sus digests para evitar autoridad circular.

## Definition of Done

- Las 27 fuentes y 108 variantes localizadas aparecen en el inventario, sin documentos ausentes ni estados `drafted`, `blocked`, `stale` o excepciones sin aprobar.
- Cada fuente tiene auditoría canónica y accesibilidad renderizada aprobadas contra su digest; cada variante tiene revisión lingüística, técnica/pedagógica y accesibilidad renderizada registradas contra ambos digests vigentes, y árabe tiene revisión bidi/copy-paste aprobada.
- Los 27 paquetes read-only agregan exactamente una fuente, cuatro locales y la procedencia aplicable sin convertirse en una segunda autoridad editable.
- El paquete raíz agrega exactamente los seis índices: auditoría canónica del mirror inglés, gates lingüístico/técnico de los cuatro índices localizados, seis renders y bidi árabe; el sign-off común referencia la evidencia sin duplicarla.
- `tools/publication_signoff.json` tiene inputs actuales y tres reviews aprobadas; su verificador y el perfil `handoff` pasan, mientras los 136 leaves permanecen independientes del digest consumidor.
- Los 108 mapas cubren todos los elementos del Parity Contract; conteos se usan solo como señales.
- Código, comandos, outputs, identificadores, source refs y tests mantienen el contrato canónico o una corrección explícita verificada en los cinco idiomas.
- Prerrequisitos, optional previews, seguridad, recuperación, soluciones, checkpoints y accesibilidad son equivalentes.
- Árabe conserva wrapper RTL único y código/comandos/paths legibles y copiables LTR.
- Las 141 páginas tienen render aprobado y las 28 páginas árabes tienen bidi aprobado; root English mirrors son byte-identical, links/selectores/anchors resuelven y los índices preservan 23–25 en orden con sus cinco targets.
- Pasa `python -B tools/validate_book.py --changed-from <ref>` y los plugins relevantes; cada baseline diff es reduction-only y elimina en el mismo lote los fingerprints resueltos.
- Las Tasks 4.3, 7.1 y 7.2 de `add-book-quality-gates` están realmente completas y sus sign-offs referencian los digests autoritativos vigentes.
- El export monolítico legacy conserva round trip byte-exacto/Unicode en leaf schema 1; schema 2 se exporta lossless y determinísticamente mediante `--export-review-bundle`.
- Pasa `openspec validate restore-multilingual-content-parity --strict` durante la fase de proposal y `git diff --check` antes de entrega.
