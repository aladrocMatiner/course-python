# Change: Restaurar la paridad multilingüe del libro implementado

## Why

El libro declara inglés canónico y variantes completas en español, catalán, sueco y árabe para 22 capítulos y 2 apéndices, pero el inventario actual muestra que muchas variantes —sobre todo sueco y árabe, y después catalán en las unidades avanzadas— son resúmenes que omiten objetivos, explicaciones, ejercicios, casos límite, recuperación, soluciones y evaluación. Esta diferencia rompe la progresión pedagógica y hace que el resultado de aprendizaje dependa del idioma elegido.

La restauración es un esfuerzo editorial transversal: necesita una fuente canónica congelada por lote, criterios de equivalencia semántica, revisión lingüística y técnica, validación estructural automatizada y una secuencia que permita publicar mejoras pequeñas sin perder navegación, contratos de código, accesibilidad ni trazabilidad.

## What Changes

- Inventariar los 24 bloques implementados —capítulos 01–22 y los dos apéndices— y sus 96 variantes localizadas frente al `README.md` inglés canónico de cada unidad.
- Definir un contrato de paridad semántica que cubra objetivos, prerrequisitos, conceptos, ejemplos, resultados observables, ejercicios, pistas, casos límite, errores recuperables, advertencias, soluciones, evaluación, reflexión y navegación.
- Restaurar primero sueco y árabe; después catalán empezando por capítulos 15–22 y apéndices; finalmente auditar español y completar cualquier diferencia confirmada.
- Ejecutar el trabajo en lotes revisables de como máximo dos unidades y dos idiomas localizados, con una fuente inglesa congelada y evidencia de revisión por lote.
- Preservar APIs, identificadores, comandos, comportamiento, resultados esperados y referencias a fuentes verificadas; localizar únicamente donde no cambie el contrato técnico.
- Exigir revisión humana lingüística y técnica. Las métricas de palabras, headings, fences o bloques actúan como señales de triaje, nunca como prueba suficiente de paridad.
- Preservar el único wrapper RTL exterior de árabe y la legibilidad LTR de código, comandos, rutas e identificadores.
- Restaurar prerrequisitos y enlaces localizados; marcar los conceptos adelantados como **Optional preview** con el mínimo necesario, una ruta para omitirlos y enlace a la unidad localizada posterior.
- Aplicar accesibilidad, seguridad editorial y revisión de procedencia/licencia a todo material tocado, sin convertir esta change en una auditoría de procedencia de contenido no modificado.
- Coordinar con `add-book-quality-gates`: cuando esté disponible, consumir `python -B tools/validate_book.py`, la taxonomía de fences/metadata `bookcheck` y su baseline común; cada lote elimina fingerprints resueltos sin añadir ni ampliar deuda. Mientras tanto, el inventario y la revisión pueden avanzar con evidencia equivalente, pero la Definition of Done exige el gate común aprobado o comprobaciones equivalentes documentadas.
- Coordinar con los capítulos propuestos 23–25 sin implementarlos, traducirlos ni crear enlaces colgantes; preservar sus entradas solo cuando existen los cinco targets y su change está aceptada/completada o archivada/baselined con evidencia, nunca por un árbol parcial.
- Mantener todos los nombres de directorio y URLs relativas actuales. No se renombra ninguna unidad.

## Impact

- Affected specs: nueva capability `maintain-multilingual-course-parity`.
- Affected content: `chapter-01-*` a `chapter-22-*`, `appendix-cli-parser/`, `appendix-algorithms/` y sus `README.{es,ca,sv,ar}.md`; el `README.md` canónico de una unidad solo se corrige cuando una carencia o error de la fuente impida una traducción correcta.
- Affected navigation: los seis índices raíz únicamente para corregir paridad, enlaces localizados o preservar una integración concurrente válida; `README.md` y `README.en.md` permanecen byte-for-byte idénticos.
- Affected quality evidence: inventario y registros de revisión por lote; señales del gate común propuesto por `add-book-quality-gates` o evidencia equivalente hasta que esté disponible.
- Active-change coordination: `add-book-quality-gates`, `add-python-network-programming-chapter`, `add-python-cpp-integration-chapter` y `add-python-rust-integration-chapter`.
- Breaking changes: ninguna. Los paths, anchors deliberados, ejemplos públicos y contratos de código existentes se conservan salvo corrección técnica explícita, probada y propagada a los cinco idiomas.

## Out of Scope

- Implementar contenido o traducciones de los capítulos 23–25.
- Añadir temas curriculares nuevos que no existan en el inglés canónico; una ampliación sustancial requiere su propia proposal.
- Renombrar directorios para traducir slugs heredados o normalizar nombres.
- Declarar equivalencia mediante traducción automática sin revisión humana competente.
- Reescribir material no tocado únicamente para uniformar estilo o realizar una auditoría retroactiva completa de procedencia.
