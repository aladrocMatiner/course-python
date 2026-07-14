# Change: Restaurar la paridad multilingüe del libro implementado

## Why

El libro declara inglés canónico y variantes completas en español, catalán, sueco y árabe para 25 capítulos y 2 apéndices, pero el inventario actual muestra que muchas variantes —sobre todo sueco y árabe, y después catalán en las unidades avanzadas— son resúmenes que omiten objetivos, explicaciones, ejercicios, casos límite, recuperación, soluciones y evaluación. Esta diferencia rompe la progresión pedagógica y hace que el resultado de aprendizaje dependa del idioma elegido.

La restauración es un esfuerzo editorial transversal: necesita una fuente canónica congelada por lote, criterios de equivalencia semántica, revisiones humanas lingüística, técnica/pedagógica, de accesibilidad renderizada y bidi, validación estructural automatizada y una secuencia que permita publicar mejoras pequeñas sin perder navegación, contratos de código, accesibilidad ni trazabilidad.

## What Changes

- Inventariar los 27 bloques publicados —capítulos 01–25 y los dos apéndices— y sus 108 variantes localizadas frente al `README.md` inglés canónico de cada unidad.
- Definir un contrato de paridad semántica que cubra objetivos, prerrequisitos, conceptos, ejemplos, resultados observables, ejercicios, pistas, casos límite, errores recuperables, advertencias, soluciones, evaluación, reflexión y navegación.
- Restaurar primero sueco y árabe; después catalán empezando por capítulos 15–25 y apéndices; finalmente auditar español y completar cualquier diferencia confirmada.
- Mantener esta change como contrato general único y ejecutar la revisión mediante 27 paquetes de capítulo/apéndice y un paquete final de índices raíz, sin duplicar la misma capability en proposals por capítulo. Cada paquete de unidad cierra un solo capítulo/apéndice y divide el trabajo localizado en sublotes de uno o dos idiomas contra una fuente inglesa congelada.
- Cerrar un paquete de unidad solo cuando su auditoría canónica, cuatro revisiones localizadas, accesibilidad renderizada de las cinco páginas, revisión bidi árabe y procedencia aplicable estén registradas contra los digests vigentes; cada puerta conserva rol, decisión, fecha y notas independientes.
- Cerrar el paquete raíz únicamente cuando los seis índices tengan revisión semántica/renderizada aplicable y el índice árabe tenga revisión bidi/copy-paste. Después, el sign-off común de `add-book-quality-gates` referencia esos digests sin entrar en la identidad ni invalidación del root leaf; la aceptación global espera ambos pasos.
- Persistir ese consumo unidireccional en `tools/publication_signoff.json`: referencias/digests actuales del índice, los 135 leaves de unidad, la procedencia derivada de los 27 paquetes —incluidos companions—, root leaf/decisiones, perfil de render y `ATTRIBUTIONS.toml`, más decisiones separadas de book editor, accesibilidad y procedencia. Un verificador read-only y el perfil `handoff` rechazan referencias stale sin escribir aprobación.
- Preservar APIs, identificadores, comandos, comportamiento, resultados esperados y referencias a fuentes verificadas; localizar únicamente donde no cambie el contrato técnico.
- Exigir gates humanos independientes para revisión lingüística, técnica/pedagógica, accesibilidad renderizada y bidi cuando aplique. Las métricas de palabras, headings, fences o bloques actúan como señales de triaje, nunca como prueba suficiente de paridad.
- Preservar el único wrapper RTL exterior de árabe y la legibilidad LTR de código, comandos, rutas e identificadores.
- Restaurar prerrequisitos y enlaces localizados; marcar los conceptos adelantados como **Optional preview** con el mínimo necesario, una ruta para omitirlos y enlace a la unidad localizada posterior.
- Aplicar accesibilidad, seguridad editorial y revisión de procedencia/licencia a todo material tocado, sin convertir esta change en una auditoría de procedencia de contenido no modificado.
- Consumir la interfaz ejecutable y el baseline ya disponibles de `add-book-quality-gates` mediante `python -B tools/validate_book.py` y la taxonomía de fences/metadata `bookcheck`; cada lote elimina fingerprints resueltos sin añadir ni ampliar deuda. La change de origen permanece activa y no archivable hasta cerrar procedencia, matriz final y revisión humana, sin impedir el uso de su implementación.
- Incorporar los capítulos ya implementados 23–25 al inventario sin heredar aprobación: sus señales automatizadas pueden registrarse, pero sus auditorías canónicas y revisiones humanas comienzan pendientes.
- Mantener todos los nombres de directorio y URLs relativas actuales. No se renombra ninguna unidad.

## Capabilities

### New Capabilities

- `maintain-multilingual-course-parity`: inventario 27×5, 27 paquetes read-only por unidad más un paquete raíz, paridad semántica, revisiones humanas independientes, accesibilidad/bidi, procedencia aplicable y aceptación global.

### Modified Capabilities

- `partitioned-parity-evidence`: versiona source/locale leaves a schema 2, añade el root-publication leaf, define migración/rollback atómicos, conserva export legacy en schema 1, añade export lossless de schema 2, valida el consumidor externo y amplía `--require-accepted` sin fabricar aprobación.

## Impact

- Affected specs: nueva capability `maintain-multilingual-course-parity`; capability modificada `partitioned-parity-evidence`.
- Affected content: `chapter-01-*` a `chapter-25-*`, `appendix-cli-parser/`, `appendix-algorithms/` y sus `README.{es,ca,sv,ar}.md`; el `README.md` canónico de una unidad solo se corrige cuando una carencia o error de la fuente impida una traducción correcta.
- Affected navigation: los seis índices raíz únicamente para corregir paridad, enlaces localizados o preservar una integración concurrente válida; `README.md` y `README.en.md` permanecen byte-for-byte idénticos.
- Affected quality evidence: inventario y registros de revisión por unidad/idioma, paquete de cierre por capítulo, paquete de publicación para los seis índices raíz, decisiones separadas de accesibilidad renderizada y bidi, y `tools/publication_signoff.json` como consumidor unidireccional; señales y sign-off del gate común implementado por `add-book-quality-gates` y plugins explícitos de capítulo.
- Capability coordination: `add-book-quality-gates`, `teach-python-network-programming`, `teach-python-cpp-integration` y `teach-python-rust-integration`. Sus changes de origen pueden estar activas o archivadas; el cierre técnico nunca avanza un registro de paridad.
- Breaking changes: solo el formato interno de evidencia tras la migración explícita a leaf schema 2; `--export-monolith` rechaza ese store porque schema 1 no representa root/render/bidi y el reemplazo lossless es `--export-review-bundle`. No hay breaking changes para lectores: paths, anchors deliberados, ejemplos públicos y contratos de código se conservan salvo corrección técnica explícita, probada y propagada a los cinco idiomas.

## Out of Scope

- Reimplementar los companions o contratos de dominio de los capítulos 23–25; esta change solo posee su revisión editorial y de paridad.
- Añadir temas curriculares nuevos que no existan en el inglés canónico; una ampliación sustancial requiere su propia proposal.
- Crear una proposal por capítulo para ejecutar el mismo contrato de review; una unidad solo abre una change separada cuando descubre una capacidad nueva, una migración pública o una reestructuración curricular fuera de este alcance.
- Renombrar directorios para traducir slugs heredados o normalizar nombres.
- Declarar equivalencia mediante traducción automática sin revisión humana competente.
- Reescribir material no tocado únicamente para uniformar estilo o realizar una auditoría retroactiva completa de procedencia.

## Risks

- Una migración parcial podría perder o sobreinterpretar evidencia humana; el store se migra completo mediante staging validada, compare-and-swap, publicación atómica, retry idempotente y rollback byte-exacto.
- Un dossier editable podría convertirse en segunda autoridad; el paquete por unidad es una proyección JSON read-only y toda decisión se registra únicamente en su source/locale leaf o en `ATTRIBUTIONS.toml`.
- Un PASS estructural podría confundirse con accesibilidad; el render y bidi conservan objetos humanos, perfil versionado, entorno observado e invalidación por inputs.
- Los 27 paquetes de unidad más el paquete raíz pueden producir conflictos o scope creep; cada suboleada posee una unidad y hasta dos locales, paths públicos estables y rollback independiente.
- Un sign-off que se referencie a sí mismo produciría un ciclo de digests; el evidence de unidad/root nunca almacena el digest consumidor, y solo `publication_signoff.json` apunta hacia evidence previa.

## Migration and Rollback

La implementación avanzará el evidence/leaf schema de 1 a 2 sin cambiar el índice de topología v2. `--migrate-review-schema` stagedará y validará los 135 leaves existentes, creará un leaf raíz nuevo —136 leaves en v2—, mantendrá campos lingüísticos/técnicos compatibles, iniciará los gates nuevos como pending y rebajará cualquier aceptación legacy incompleta. Un store v2 válido será un no-op; un store mixto abortará sin escribir y conservará exactamente sus bytes mixtos; un input íntegramente v1 restaurará v1 byte a byte ante conflicto concurrente, falta de `renameat2(RENAME_EXCHANGE)` o fallo posterior. `--export-review-bundle` entregará el agregado v2 lossless, mientras el export monolítico legacy seguirá limitado a leaf schema 1. La implementación añade `tools/publication_signoff.json` en un diff separado y estado pending; la migración no lo incluye en el exchange del store ni en digests upstream. Cada suboleada editorial se revierte por unidad/locale y nunca modifica evidencia humana ajena.

## Definition of Done

- Los 27 paquetes de unidad y el paquete raíz se generan determinísticamente desde sus leaves autoritativos, procedencia aplicable y un perfil de render versionado, sin segunda autoridad editable.
- Las 27 fuentes tienen auditoría canónica y render aprobados; las 108 variantes tienen gates lingüístico, técnico/pedagógico y render aprobados, y las 27 árabes añaden bidi/copy-paste.
- Las 141 páginas publicadas tienen revisión renderizada vigente, las 28 páginas árabes tienen bidi/copy-paste aprobado y el paquete raíz conserva las revisiones lingüísticas/técnicas aplicables de los índices localizados.
- Toda procedencia aplicable y los gates globales de publicación están resueltos contra evidencia vigente; las Tasks 4.3, 7.1 y 7.2 de `add-book-quality-gates` están realmente completas y ningún estado `accepted` depende de un digest o perfil stale.
- `python -B tools/parity_review.py --verify-publication-signoff tools/publication_signoff.json` y el perfil `handoff` confirman que los sign-offs humanos apuntan a evidence actual; ningún leaf upstream contiene el digest del consumidor.
- `python -B tools/parity_review.py --require-accepted`, el perfil `handoff`, plugins aplicables, tests, OpenSpec strict/doctor, whitespace e higiene pasan desde un checkout limpio.
