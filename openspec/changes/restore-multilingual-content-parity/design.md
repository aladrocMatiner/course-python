## Context

La verdad implementada contiene 22 capítulos y 2 apéndices. Cada unidad tiene un `README.md` inglés canónico y cuatro variantes localizadas. No existe una spec base archivada ni, todavía, un sistema de validación global implementado; los controles compartidos de `add-book-quality-gates` son propuesta, no verdad actual.

El inventario inicial revela una asimetría suficiente para definir prioridades sin usar el tamaño como aceptación: sueco y árabe suelen conservar solo una fracción de la lección inglesa, catalán pierde secciones especialmente a partir de los capítulos intermedios/tardíos y español se aproxima más al original, aunque existen diferencias que requieren auditoría. La comparación por palabras sirve para encontrar riesgo; no demuestra que una traducción enseñe lo mismo.

El público incluye principiantes jóvenes. Una omisión de recuperación de errores, advertencias, prerrequisitos o soluciones no es un defecto cosmético: cambia qué puede aprender y ejecutar con seguridad la persona lectora.

## Goals / Non-Goals

### Goals

- Restablecer equivalencia semántica y pedagógica entre cada fuente inglesa y sus cuatro variantes para las 24 unidades implementadas.
- Mantener una progresión tranquila y resoluble: prerrequisitos antes de uso, previews opcionales explícitos y el microciclo objetivo/contexto → teoría mínima → predicción → ejecución → observación → modificación → verificación → explicación.
- Preservar el contrato técnico de ejemplos, comandos, nombres públicos, outputs, referencias a companion sources y verificaciones.
- Entregar mejoras en lotes pequeños, revisables, reversibles y con evidencia reproducible.
- Integrarse con controles compartidos sin duplicar un segundo validador global.
- Mantener accesibilidad, RTL/LTR, navegación localizada, seguridad, higiene y obligaciones de licencia en todo material tocado.

### Non-Goals

- Traducir o revisar como parte de este alcance capítulos que aún son propuestas.
- Producir traducción literal o igualar conteos de palabras.
- Crear contenido curricular nuevo para rellenar diferencias de longitud.
- Sustituir criterio lingüístico/técnico humano con heurísticas.
- Renombrar paths públicos o reorganizar la numeración.

## Architecture Snapshot

- **Fuente canónica por unidad:** `README.md` inglés de cada capítulo/apéndice. Antes de abrir un lote se registra su digest y se audita si contiene el material necesario para servir de fuente correcta.
- **Variantes bajo revisión:** `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`; cada una se evalúa contra la misma revisión congelada de la fuente.
- **Paquete de paridad:** registro persistente por unidad/idioma con digest canónico, mapa de cobertura, excepciones justificadas, resultados automáticos, resultado lingüístico, resultado técnico y estado de publicación. No almacena datos personales de estudiantes.
- **Gate común:** la interfaz propuesta por `add-book-quality-gates`, `python -B tools/validate_book.py [--changed-from REF]`, aporta señales de shape, links, selector, espejo raíz, RTL, headings, fences, alt text y source refs. Los fences nuevos/modificados usan exactamente `runnable|expected-error|compile-only|source-ref|todo|illustrative|output` y la metadata versionada `bookcheck`. Los plugins de capítulo siguen siendo dueños de sus pruebas de dominio.
- **Revisión humana:** una puerta lingüística verifica naturalidad, nivel y equivalencia; una puerta técnica/pedagógica verifica conducta, seguridad, prerequisitos y aprendizaje. Una persona puede cubrir ambos roles solo si tiene competencia demostrable en ambos; el registro identifica roles, no datos de alumnos.
- **Navegación:** enlaces internos y selectores apuntan a la variante del mismo idioma cuando existe. Los índices se editan atómicamente solo hacia targets existentes cuya implementación esté aceptada/completada o archivada/baselined con evidencia; un directorio parcial no basta.
- **Changes concurrentes:** capítulos 23, 24 y 25 son propuestas separadas con validadores y localización propios. Este esfuerzo no reclama su cumplimiento y no pisa sus contenidos.

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

### Decision: Lotes máximos de dos unidades y dos idiomas

Un lote modifica como máximo dos unidades canónicas y dos locales, con un máximo normal de cuatro archivos localizados, además de correcciones canónicas/evidencia estrictamente necesarias. El trabajo sueco y árabe puede compartir lote cuando hay revisores adecuados; si no, se separa por idioma.

**Rationale:** limita el coste de review, reduce conflictos y permite revertir una oleada sin perder progreso anterior.

### Decision: Prioridad por riesgo y dependencia curricular

El orden es:

1. Sueco y árabe, capítulos 01–22 y apéndices, en orden de prerrequisitos.
2. Catalán, primero capítulos 15–22 y apéndices; después capítulos 01–14.
3. Español, auditoría completa en orden y corrección solo de gaps confirmados.

Dentro de cada banda se procesan pares consecutivos (`01–02`, `03–04`, …, `21–22`) y finalmente los dos apéndices. Un defecto de seguridad o exactitud puede adelantarse y queda documentado.

**Rationale:** atiende primero las mayores pérdidas observadas sin dejar que las unidades posteriores dependan de fundamentos aún incompletos.

### Decision: Automatización como señal, revisión humana como aceptación

Los checks automatizados detectan archivos ausentes, links, wrappers, headings, fences, clasificaciones/metadata `bookcheck`, referencias, divergencias estructurales y cambios de digest. Conteos y ratios generan avisos de triaje, no PASS/FAIL semántico por sí solos. La aceptación requiere ambos resultados humanos, lingüístico y técnico/pedagógico.

**Rationale:** una traducción larga puede ser incorrecta y una formulación más breve puede ser completamente equivalente.

### Decision: Reusar el gate común y conservar una ruta provisional

Si `add-book-quality-gates` se aprueba y aplica primero, esta change consume `python -B tools/validate_book.py --changed-from <ref>` y su baseline, sin duplicar parsers globales. Cuando un lote resuelve un fingerprint heredado, ejecuta el flujo aprobado `--update-baseline` y entrega en el mismo diff una reducción exacta; nunca añade fingerprints, ensancha una supresión ni conserva una entrada stale. Si aún no está implementado, los lotes pueden producir inventario y review mediante comandos/documentación equivalentes que usan la misma taxonomía de fences y metadata `bookcheck`. La aceptación final exige el gate común o un paquete equivalente que cubra los mismos controles y pueda migrarse sin cambiar los contratos de paridad.

**Rationale:** permite avanzar trabajo editorial y evita dos fuentes de verdad para validación estructural.

### Decision: Código y source refs son contratos compartidos

Los bloques localizados conservan imports, APIs, identificadores, control flow relevante, argumentos, resultados y comandos del canónico. Todo fence nuevo/modificado conserva la clasificación canónica o usa exactamente `runnable`, `expected-error`, `compile-only`, `source-ref`, `todo`, `illustrative` u `output`, con metadata `bookcheck` cuando corresponda; no se crea una convención localizada paralela. Comentarios y strings destinados al lector pueden localizarse si los tests y source refs siguen siendo válidos. Un bloque runnable se ejecuta una vez desde su companion source probado, no cinco copias divergentes; cualquier ejemplo inline divergente se verifica explícitamente.

**Rationale:** reduce drift técnico sin prohibir traducción natural.

### Decision: Evidencia de revisión sin datos personales innecesarios

El registro de lote conserva unidad, idioma, digest, fecha, roles de revisión, checklist, comandos/resultados y excepciones. No contiene datos de estudiantes, credenciales ni secretos; los nombres de revisores no son requisito de la spec.

## Review Packet and State Model

Cada unidad/idioma transita por:

`inventoried → source-frozen → drafted → automated-signals-pass → linguistic-reviewed → technical-reviewed → accepted`

- Un cambio de digest canónico mueve el registro a `stale` hasta reconciliación.
- Un fallo de link, código, RTL, seguridad o accesibilidad mueve el registro a `blocked`.
- Una diferencia intencional usa `exception` con justificación, alcance y aprobación lingüística/técnica; no sirve para omitir contenido por comodidad.
- Solo `accepted` permite marcar completada la tarea correspondiente.

El paquete señala cada elemento del Parity Contract con referencia a sección/línea o una explicación breve. Los números de palabras, headings y fences se guardan como observaciones, no como veredicto.

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
- Los índices se corrigen atómicamente, conservan `README.md == README.en.md` byte a byte y nunca enlazan capítulos 23–25 hasta que existan sus cinco targets y su implementación esté aceptada/completada o archivada/baselined con evidencia.

## Active Change Coordination

- **`add-book-quality-gates`:** esta change consume su interfaz y baseline si están implementados. El gate común detecta estructura; el paquete de paridad aporta aceptación semántica humana.
- **Capítulo 23:** reservado por `add-python-network-programming-chapter`; queda fuera del inventario. Su navegación se preserva solo con cinco targets y change aceptada/completada o archivada/baselined con evidencia.
- **Capítulo 24:** reservado por `add-python-cpp-integration-chapter`; mismo tratamiento.
- **Capítulo 25:** reservado por `add-python-rust-integration-chapter`; mismo tratamiento.
- Ningún lote de esta change modifica los directorios 23–25 ni declara que sus traducciones fueron revisadas.
- Antes de editar un índice o herramienta compartida se releen las changes activas y se rebasa sobre su estado implementado real.

## Risks / Trade-offs

- **Volumen de 96 variantes:** los lotes pequeños aumentan coordinación → manifest único, estados explícitos y pares consecutivos.
- **Fluidez vs literalidad:** un traductor puede omitir detalle para sonar natural → mapa semántico por resultado, no correspondencia de frases.
- **Canonical drift:** cambios ingleses invalidan reviews → digest y estado `stale`.
- **Falsa confianza por métricas:** conteos similares ocultan errores → señales solo de triaje y doble puerta humana.
- **Competencia de revisión escasa:** puede bloquear un idioma → no autoaprobar; mantener lote en `drafted` o `blocked` hasta review competente.
- **Conflicto con tooling concurrente:** duplicación o baseline divergente → consumir la interfaz común y limitar esta change a evidencia de paridad.
- **Conflicto con índices 23–25:** rebase puede borrar o publicar trabajo parcial → integración tardía, cinco targets más estado OpenSpec/evidencia aceptada y validación de links.
- **Propagar errores del inglés:** traducción fiel de un defecto → auditoría canónica previa y corrección sincronizada.
- **Attribution drift:** adaptar material durante traducción puede introducir obligaciones → preferir redacción original y revisar procedencia solo del material tocado.

## Migration Plan

1. Inventariar 24 fuentes y 96 variantes; registrar gaps y prioridad sin editar contenido.
2. Definir el paquete de revisión y conectarlo al gate común, o documentar controles equivalentes provisionales.
3. Ejecutar un piloto sueco/árabe con capítulos 01–02; ajustar el checklist sin relajar aceptación.
4. Completar sueco/árabe por pares consecutivos y después apéndices.
5. Completar catalán empezando por 15–22/apéndices y luego 01–14.
6. Auditar y corregir español por pares, sin asumir paridad por similitud de tamaño.
7. Reconciliar navegación, changes concurrentes y digests; ejecutar regresión global y reviews finales.
8. Publicar/archivar solo cuando los 96 registros estén `accepted` y todos los gates pasen.

Cada lote es revertible por archivos de unidad y su evidencia. Revertir un lote no altera paths ni estados de otros lotes; su registro vuelve a la fase anterior.

## Open Questions

- Ninguna bloqueante. La ubicación física definitiva del paquete de review puede alinearse durante implementación con la estructura aprobada por `add-book-quality-gates`, manteniendo el esquema y estados definidos aquí.

## Definition of Done

- Las 24 fuentes y 96 variantes localizadas aparecen en el inventario, sin documentos ausentes ni estados `drafted`, `blocked`, `stale` o excepciones sin aprobar.
- Cada variante tiene revisión lingüística y técnica/pedagógica registrada contra el digest canónico vigente.
- Los 96 mapas cubren todos los elementos del Parity Contract; conteos se usan solo como señales.
- Código, comandos, outputs, identificadores, source refs y tests mantienen el contrato canónico o una corrección explícita verificada en los cinco idiomas.
- Prerrequisitos, optional previews, seguridad, recuperación, soluciones, checkpoints y accesibilidad son equivalentes.
- Árabe conserva wrapper RTL único y código/comandos/paths legibles y copiables LTR.
- Root English mirrors son byte-identical; links/selectores/anchors resuelven; índices preservan 23–25 solo con cinco targets y estado aceptado/completado o archivado/baselined verificable.
- Pasa `python -B tools/validate_book.py --changed-from <ref>` cuando el gate común esté implementado, más plugins relevantes; cada baseline diff es reduction-only y elimina en el mismo lote los fingerprints resueltos. De lo contrario pasa evidencia equivalente documentada para shape, links, mirror, RTL, headings, la taxonomía/metadata `bookcheck`, alt text y source refs.
- Pasa `openspec validate restore-multilingual-content-parity --strict` durante la fase de proposal y `git diff --check` antes de entrega.
