# Borrador de revisión de implementación y handoff

Fecha: 2026-07-14
Change: `restore-multilingual-content-parity`
Estado: implementación editorial en curso; ninguna aprobación de publicación

## Propósito y límite de este documento

Este documento reúne el estado observable y prepara el trabajo que todavía
requiere revisión competente. No aprueba ninguna fuente canónica, traducción,
decisión de accesibilidad, comportamiento bidireccional, procedencia, licencia
o publicación. Tampoco declara completa o archivable la change.

OpenSpec muestra 4 de 50 tareas marcadas y 46 pendientes. Este handoff no
modifica `tasks.md`, los registros de paridad ni ninguna decisión humana. Las
ediciones recientes cambiaron contenido después de parte de la evidencia
registrada. Sus digests ya se reconciliaron y la validación normal de
`parity_review.py` pasa sobre el árbol actual; el gate de publicación sigue
bloqueado de forma explícita por las auditorías y revisiones humanas pendientes.

## Inventario publicado

El alcance sigue siendo:

| Familia | Inventario |
|---|---:|
| Fuentes inglesas canónicas | 27: capítulos 01–25 y dos apéndices |
| Variantes localizadas | 108: 27 × `es`, `ca`, `sv`, `ar` |
| Páginas de unidad | 135: 27 × cinco idiomas |
| Índices raíz | 6 |
| Conjunto renderizado completo | 141 páginas |

La topología 27/108 está inventariada, pero la existencia y la estructura no
demuestran paridad semántica. Las 27 auditorías canónicas y las 108 revisiones
localizadas permanecen dentro de la frontera humana descrita más abajo.

## Correcciones canónicas realizadas

Se añadió una pregunta de predicción antes de ejecutar a estas doce fuentes
canónicas, cubriendo los capítulos 13–22 y los dos apéndices:

- `chapter-13-files/README.md`
- `chapter-14-exceptions/README.md`
- `chapter-15-modulos/README.md`
- `chapter-16-entornos/README.md`
- `chapter-17-persistencia/README.md`
- `chapter-18-testing/README.md`
- `chapter-19-http/README.md`
- `chapter-20-logging/README.md`
- `chapter-21-async/README.md`
- `chapter-22-introspection/README.md`
- `appendix-cli-parser/README.md`
- `appendix-algorithms/README.md`

Los doce prompts completan el paso «predecir antes de ejecutar» requerido por
`BOOK_STYLE.md`; no constituyen las 27 auditorías canónicas humanas. Todo
registro localizado dependiente de estos digests debe considerarse pendiente
de reconciliación antes de una revisión o aceptación posterior.

## Auditoría editorial sueca y árabe

Se realizó una revisión editorial asistida de las 54 páginas suecas/árabes
contra sus 27 fuentes. Esto permitió corregir defectos claros, pero no sustituye
la revisión lingüística o técnica/pedagógica de una persona competente y no
promovió ningún registro.

Se editaron las variantes `README.sv.md` y `README.ar.md` de estas quince
unidades, 30 archivos en total:

- `appendix-algorithms`
- `appendix-cli-parser`
- `chapter-13-files`
- `chapter-14-exceptions`
- `chapter-15-modulos`
- `chapter-16-entornos`
- `chapter-17-persistencia`
- `chapter-18-testing`
- `chapter-19-http`
- `chapter-20-logging`
- `chapter-21-async`
- `chapter-22-introspection`
- `chapter-23-network-programming`
- `chapter-24-python-cpp-integration`
- `chapter-25-python-rust-integration`

Las correcciones incluyeron:

- equivalentes suecos y árabes de los doce prompts canónicos y sincronización
  de sus prerrequisitos;
- restauración del enlace localizado opcional de capítulo 13 a capítulo 14;
- eliminación de prosa árabe introducida accidentalmente en la página sueca
  del capítulo 22;
- detalle completo del capstone y la rúbrica del capítulo 23;
- contexto de ejecución temporal/red del verificador C++ y corrección de la
  traducción árabe de «it compiled» en capítulo 24;
- encabezado de errores recuperables y detalle omitido sobre preflight,
  contrato numérico, distribución, ejercicios, checkpoints y glosario en
  capítulo 25.

La comprobación acotada de las 27 parejas confirmó secuencias equivalentes de
niveles de heading y fences, enlaces locales resolubles con el mismo recuento,
un único wrapper RTL árabe cerrado al final, ausencia de controles bidi
invisibles y ausencia de prosa árabe accidental en sueco salvo el selector de
idioma. Estas son señales estructurales y editoriales, no aprobación renderizada
ni de fluidez.

## Español y catalán

La auditoría editorial y estructural cubrió las 27 unidades en español y
catalán: 54 archivos en total. Se corrigieron 45 archivos y nueve no necesitaron
cambios. La regresión estructural de los 54 archivos terminó con `errors=0`;
además, 98 fences `runnable` y nueve casos `expected-error` terminaron con
`diagnostics=0`.

Estos resultados prueban el alcance y los checks ejecutados, pero no aportan
fluidez lingüística, equivalencia técnica/pedagógica ni accesibilidad
renderizada. Las revisiones humanas ES/CA y la reconciliación de sus digests
siguen pendientes. No se ha promovido ningún registro ni marcado ninguna tarea
por esta auditoría.

## Estado actual de reconciliación automática

Después de ejecutar `parity_review.py --write` y
`parity_review.py --reconcile-drafts`, el inventario real contiene 33 registros
`automated-signals-pass` y 75 registros `drafted`. La ejecución posterior de
`parity_review.py --record-automated` promovió cero registros.

La promoción se cerró de forma conservadora porque existe un warning global no
incluido en el baseline, `attribution.review_required`, asociado a `LICENSE`.
Al ser global, el contrato fail-closed impide promover cualquier variante en
esa ejecución. Además hay bloqueos acotados por unidad en
`chapter-03-lists`, `chapter-23-network-programming`,
`chapter-24-python-cpp-integration` y
`chapter-25-python-rust-integration`.

Este resultado es el comportamiento protector esperado: evita registrar
evidencia automática parcial mientras una deuda global nueva o un diagnóstico
de la unidad sigue abierto. No se debe forzar la transición, ampliar o inventar
un baseline, suprimir el warning ni editar estados manualmente para obtener un
PASS. Resolver y revisar las causas permite repetir el flujo; aun entonces,
`automated-signals-pass` solo sería evidencia automática y nunca aceptación
lingüística, técnica/pedagógica o de publicación.

## Evidencia técnica ya ejecutada

La evidencia siguiente prueba controles concretos en el host observado; no
aprueba traducciones ni amplía la matriz de plataformas. La evidencia del
review consolidado se ejecutó en Linux x86_64 con CPython 3.13.11, salvo que se
indique otra cosa.

| Área | Evidencia observada | Resultado y límite |
|---|---|---|
| Suite de herramientas actual | `python -B -m unittest discover -s tools/tests -p 'test_*.py' -v` | 136 tests pasaron el 2026-07-14 en 16.633 s. |
| Currículo declarado | `python -B tools/validate_curriculum.py` | 0 issues en el review consolidado; prueba orden contractual, no aprobación pedagógica. |
| Skills mantenedoras | `quick_validate.py` sobre cinco skills nuevas más `professor` y `book-editor` | 7/7 válidas en el review consolidado. |
| Companions estándar | suites de capítulos 15, 19, 20, 21 y 22 y ambos apéndices | 36 tests pasaron: 17 + 4 + 3 + 3 + 3 + 2 + 4. |
| Artefacto de capítulo 15 | `verify_artifact.py`, ruta aislada y ruta `--wheelhouse` | Build PEP 517, inspección de wheel, instalación exacta, `pip check`, entry point, import desde cwd externo y cleanup pasaron. |
| Redes | suite de capítulo 23 y plugin explícito | 33 tests loopback acotados; `network:network-suite` pasó. |
| C++ ligero | plugin explícito de capítulo 24 | `cpp:contract` y `cpp:boundaries` pasaron; no equivale al build nativo. |
| Rust ligero | plugin explícito de capítulo 25 | `rust:contract` y `rust:distribution-boundary` pasaron; no equivale al build nativo. |

### Evidencia nativa C++

El review consolidado registró un `verify_all.py` completo sobre Linux x86_64,
CPython 3.13.11, GCC/G++ 13.3.0, GNU ld 2.42, C++17, CMake 4.1.2,
Ninja 1.13, pybind11 3.0.4 y scikit-build-core 1.0.3. Pasaron survival,
primera extensión, CTest Debug/Release, pytest, sdist→wheel, clean install,
`pip check`, foreign-cwd smoke, stubtest, typing positivo y negativo,
dependencias ELF, sanitizers GNU y embedding.

Después se añadió una regresión explícita para buffers `double` desalineados.
El 2026-07-14 se volvió a ejecutar `verify_all.py` completo: reconstruyó las
wheels Debug y Release, pasó CTest 1/1 y pytest 37/37 en ambos perfiles, confirmó
ASan/UBSan sobre el core autónomo y repitió sdist→wheel, instalación limpia,
`pip check`, smoke desde un cwd externo, stubtest, typing positivo/negativo,
dependencias ELF y embedding. Todos los outputs generados permanecieron en
rutas temporales.

### Evidencia nativa Rust

El review consolidado registró el verificador completo desde capítulo 25 con
rustc/Cargo 1.97.0 fijados mediante rustup, PyO3 0.29.0 y maturin 1.14.1.
Pasaron fmt, clippy, Cargo tests, fallo esperado de ownership y recuperación,
primera extensión, wheel de hooks con 4/4 casos de concurrencia, sdist limpio,
typing/stubtest e instalaciones desde cwd externo. La wheel Release
`cp313-cp313-manylinux_2_34_x86_64` pasó 40 tests y dejó dos skips exclusivos
de hooks, ya cubiertos por la wheel dedicada. La wheel
`cp311-abi3-manylinux_2_34_x86_64` pasó inspección, instalación y smoke en
CPython 3.13. Esto no verifica Windows, macOS, CPython 3.11/3.12 ni Python
free-threaded.

La evidencia técnica histórica se conserva como prueba de sus comandos y host.
El estado vigente de paridad es el recuento 33/75 descrito arriba; ni ese estado
ni la topología 27/108 afirman aceptación humana o gate final aprobado.

## Frontera de revisión humana

| Puerta | Alcance pendiente | Condición real de cierre |
|---|---:|---|
| Auditoría canónica | 27 fuentes | Exactitud, seguridad, pedagogía, accesibilidad y procedencia contra el digest vigente. |
| Lingüística | 108 variantes | Fluidez, terminología, gramática, tono y equivalencia natural por idioma. |
| Técnica/pedagógica | 108 variantes | Código, claims, prerrequisitos, ejemplos, recovery, soluciones, evaluación y source refs. |
| Accesibilidad renderizada | 141 páginas | Inspección de los índices y de las 27×5 páginas según la matriz siguiente. |
| Árabe bidi/copy-paste | 28 páginas árabes | Índice raíz árabe más 27 unidades árabes. |
| Procedencia/licencia | Material tocado y siete entradas existentes | Decisión documentada por una persona competente; automation no decide derechos. |

Una misma persona puede cubrir las puertas lingüística y técnica solo cuando
tenga competencia demostrable en ambas; cada checklist y decisión sigue siendo
independiente. Ninguna de estas puertas se completa por conteos, tests o este
handoff.

## Procedencia y licencia

El inventario vigente de `ATTRIBUTIONS.toml` mantiene siete entradas neutrales
`review-required` que cubren 30 paths: ejercicios/prosa de capítulos 2 y 3,
fixtures TLS de capítulo 23, declaraciones/referencias de capítulos 24 y 25,
`icons/cc-by-sa.svg` y el texto `LICENSE`. El packet detallado está en
`openspec/changes/add-book-quality-gates/IMPLEMENTATION_REVIEW.md`.

No hay reviewer role/date ni decisión de originalidad, permiso, notice,
trademark o compatibilidad de licencia para esas entradas. Toda adaptación
externa introducida durante las oleadas debe registrar fuente, titular tal como
lo proporcione la fuente, licencia/permiso, notice visible y adaptación; si no
puede verificarse, el lote se bloquea o usa material original. Este handoff no
hace una auditoría histórica total ni una conclusión legal.

## Conjunto exacto para revisión renderizada

Se deben renderizar estos seis índices raíz:

```text
README.md
README.en.md
README.es.md
README.ca.md
README.sv.md
README.ar.md
```

Para cada una de las 27 unidades siguientes se deben renderizar exactamente
`README.md`, `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`:

```text
chapter-01-introduction
chapter-02-variables
chapter-03-lists
chapter-04-dictionaries
chapter-05-sets
chapter-06-tuples
chapter-07-queues
chapter-08-conditionals
chapter-09-input
chapter-10-loops
chapter-11-functions
chapter-12-oop
chapter-13-files
chapter-14-exceptions
chapter-15-modulos
chapter-16-entornos
chapter-17-persistencia
chapter-18-testing
chapter-19-http
chapter-20-logging
chapter-21-async
chapter-22-introspection
chapter-23-network-programming
chapter-24-python-cpp-integration
chapter-25-python-rust-integration
appendix-cli-parser
appendix-algorithms
```

Cada una de las 141 páginas se inspecciona en:

- viewport estrecho de `320×568`;
- viewport ancho de `1280×800`;
- zoom/reflow al `200 %`, registrando cualquier pérdida, solapamiento o scroll
  horizontal no contenido por un bloque técnico;
- navegación solo con teclado y lectura con tecnología asistiva, registrando
  sistema operativo, navegador y AT usados;
- navegación por headings, texto descriptivo de links, orden de lectura,
  tablas en estrecho, alt text y equivalente en prosa, y ausencia de
  instrucciones basadas solo en color, posición o dirección.

En las 28 páginas árabes se añade inspección manual de puntuación y flujo de
listas, mezcla RTL/LTR inline, orden visual de números/URLs y legibilidad LTR de
código, comandos, paths, identificadores y output. Se copian y pegan comandos
representativos en texto plano y se comparan byte por byte con Markdown. El
wrapper estático balanceado y la ausencia de marcas invisibles no sustituyen
esta prueba renderizada.

## Comandos de rerun y reconciliación

Después de inspeccionar el resultado ES/CA y los cambios canónicos, el
mantenedor debe refrescar primero el inventario, abrir explícitamente el nuevo
ciclo de drafts, validar el contenido y solo entonces registrar las señales
automáticas. Estos comandos cambian evidencia, pero nunca conceden aprobación
humana:

```sh
python -B tools/parity_review.py --write
python -B tools/parity_review.py --reconcile-drafts
python -B tools/validate_book.py
python -B tools/parity_review.py
python -B tools/parity_review.py --record-automated
```

Mientras permanezca el warning global no baselined sobre `LICENSE`, el
resultado conservador esperado de `--record-automated` es promover cero
registros. Debe resolverse mediante la revisión de procedencia correspondiente,
no mediante una promoción forzada.

La matriz compartida y sus comandos directos se vuelven a ejecutar desde la
raíz:

```sh
python -B -m unittest discover -s tools/tests -p 'test_*.py' -v
python -B tools/validate_curriculum.py
python -B tools/parity_review.py
python -B tools/validate_book.py
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
python -B tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
python -B tools/run_quality.py --profile handoff --format markdown
```

Los companions y matrices nativas requieren rerun independiente:

```sh
python -B -m unittest discover -s chapter-15-modulos/examples/src-layout/tests -p 'test_*.py' -v
python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py
python -B -m unittest discover -s chapter-19-http/tests -p 'test_*.py' -v
python -B -m unittest discover -s chapter-20-logging/tests -p 'test_*.py' -v
python -B -m unittest discover -s chapter-21-async/tests -p 'test_*.py' -v
python -B -m unittest discover -s chapter-22-introspection/tests -p 'test_*.py' -v
python -B -m unittest discover -s appendix-cli-parser/tests -p 'test_*.py' -v
python -B -m unittest discover -s appendix-algorithms/tests -p 'test_*.py' -v
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p 'test_*.py' -v
python -B chapter-24-python-cpp-integration/tools/verify_all.py
cd chapter-25-python-rust-integration
python -B examples/faststats-rs/tools/verify.py
cd ..
```

Las siete skills se revalidan con el `quick_validate.py` del skill-creator:

```sh
CODEX_HOME="${CODEX_HOME:-/home/aladroc/.codex-aladroc}"
for skill in \
  .codex/skills/verify-python-learning-assets \
  .codex/skills/engineer-python-network-labs \
  .codex/skills/python-packaging-release \
  .codex/skills/engineer-python-native-interop \
  .codex/skills/maintain-book-quality-tooling \
  .codex/skills/professor \
  .codex/skills/book-editor
do
  python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" "$skill"
done
```

El cierre técnico del handoff requiere además:

```sh
openspec validate restore-multilingual-content-parity --strict
openspec doctor
git diff --check
git status --short
```

Solo después de registrar las 27 auditorías canónicas, las dos revisiones
humanas de las 108 variantes, la revisión renderizada y las decisiones de
procedencia puede ejecutarse el gate de publicación:

```sh
python -B tools/parity_review.py --require-accepted
```

Hasta entonces, su salida no cero es la frontera esperada y no debe ocultarse,
reinterpretarse como aprobación parcial ni corregirse marcando tareas.
