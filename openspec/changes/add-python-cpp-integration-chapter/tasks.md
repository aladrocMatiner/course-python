## TASK BREAKDOWN

## Phase 1: Contrato, toolchain y arquitectura

### Task 1.1: Congelar rutas, sesiones y trazabilidad

- **Objective:** Mapear cada requisito a una subsección, un asset, un ejercicio y una evidencia verificable.
- **Deliverables:** Esqueleto de headings de `README.md`, glosario/concept map, tabla ruta→sesión→outcome y matriz requisito→archivo→test.
- **Validation:** Ningún concepto C++/CPython se usa antes de explicarse; las cuatro rutas terminan en resultados ejecutables y distinguen ruta completada de capítulo completo.
- **Risk:** El alcance puede convertirse en un curso completo de C++; aplicar estrictamente los non-goals.
- **Scope:** M
- [x] 1.1 Congelar el mapa pedagógico y la trazabilidad de la capability.

### Task 1.2: Definir preflight y versiones verificadas

- **Objective:** Dar diagnósticos reproducibles de Python, venv, compiler, CMake, pybind11 y backend antes de compilar ejemplos.
- **Deliverables:** Preflight, platform table, `requirements-dev.lock`, `constraints-build.txt` y commands/version capture.
- **Validation:** Exige Python/CMake/C++17/ranges y pip >=25.3; lock exacto para test tools; `PIP_BUILD_CONSTRAINT` fuerza pybind11 3.0.4/scikit-build-core 1.0.3 dentro de PEP517 isolation y el build log confirma versiones.
- **Risk:** Instalar toolchains requiere permisos distintos por SO; separar verificación de instrucciones de instalación.
- **Scope:** M
- [x] 1.2 Crear el preflight y registrar el conjunto de versiones soportado/probado.

### Task 1.3: Crear la estructura aislada de assets

- **Objective:** Separar survival kit, primera extensión, capstone, embedding, documentación y outputs de build.
- **Deliverables:** Asset dirs, `verify_native.py`, `verify_artifacts.py`, chapter `verify_all.py`, locks/constraints y `.gitignore`.
- **Validation:** Todos los commands aceptados escriben a temporales; el root hygiene o fallback temporal detecta outputs incluso ignorados; nombres públicos/privados coinciden en CMake, Python y stubs.
- **Scope:** S
- [x] 1.3 Crear el árbol de assets y la política de higiene.

### Task 1.4: Crear el validador documental independiente

- **Objective:** Validar enlaces, selectores, paridad y relación entre snippets y fuentes compiladas sin depender de otras proposals.
- **Deliverables:** Marker contract; con root gate, `chapter-24-python-cpp-integration/tools/bookcheck_plugin.py` `register(registry)` para C++/CMake/source refs y ningún parser/hygiene genérico local; sin root, `validate_docs.py`/`check_hygiene.py` temporales con plan de migración.
- **Validation:** Root CLI no se debilita y plugin cubre targets; si el capítulo llega primero, standalones ejecutan markers/source refs/ignored scan y equivalence tests pasan antes de sustituirlos; nunca quedan dos parsers genéricos mantenidos.
- **Scope:** M
- [x] 1.4 Implementar y probar el validador del capítulo.

## Phase 2: Ruta esencial — de cero C++ a primer import

### Task 2.1: Enseñar el survival kit de C++17

- **Objective:** Introducir solo la sintaxis y el modelo de recursos necesarios para comprender el binding.
- **Deliverables:** Lecciones y ejemplos sobre tipos, funciones, scopes, headers/source, referencias, `const`, `std::vector`, clases simples, RAII y excepciones.
- **Validation:** Los ejemplos compilan con warnings altos; cada subsección incluye predicción, happy path, edge case, TODO/pista, error de compiler explicado y solución razonada.
- **Scope:** L
- [x] 2.1 Redactar y verificar el survival kit C++17.

### Task 2.2: Hacer observable compiler, linker y loader

- **Objective:** Diferenciar las fases que convierten source en executable/shared library y finalmente en módulo importable.
- **Deliverables:** Primer executable C++, diagrama source→object→link→load/import y ejercicios con errores deliberados de compile/link/load no destructivos.
- **Validation:** El alumnado identifica la fase correcta a partir del diagnóstico y reconstruye limpiamente fuera del source tree.
- **Scope:** M
- [x] 2.2 Crear el laboratorio de compiler/linker/loader.

### Task 2.3: Construir la primera extensión pybind11

- **Objective:** Importar desde Python una función C++ mínima mediante PEP 517 sin flags manuales específicos de plataforma.
- **Deliverables:** `examples/01-first-extension/{pyproject.toml,CMakeLists.txt,src/bindings.cpp,tests/}`.
- **Validation:** Build limpio en venv activo, import desde fuera del directorio fuente, happy path, tipo inválido y rebuild después de modificar C++.
- **Risk:** Un import desde el source tree puede ocultar un layout incorrecto; usar cwd temporal.
- **Scope:** M
- [x] 2.3 Implementar y explicar la primera extensión importable.

## Phase 3: Ruta profesional — `faststats_cpp`

### Task 3.1: Fijar la referencia y el contrato Python

- **Objective:** Definir semántica, errores y API antes de escribir la optimización nativa.
- **Deliverables:** `_reference.py`, Summary, public APIs y exact bounded type/numeric contract from design/spec.
- **Validation:** Built-in int/float only en iterable/OnlineStats, int<=2**53, abs<=1e150, total<=1M, final mean Welford order/no-fast-math y anomalías en segunda pasada con tolerance band; `[-3,-3,-1]`/0.5 distingue streaming; normalization/OnlineStats errors son transaccionales.
- **Scope:** M
- [x] 3.1 Crear el oráculo Python y congelar el contrato público.

### Task 3.2: Implementar el core C++ independiente

- **Objective:** Construir el algoritmo sin incluir `Python.h` ni headers pybind11.
- **Deliverables:** `core.hpp`, `core.cpp`, tipos de resultado/error y `cpp/tests/core_tests.cpp` registrado con CTest.
- **Validation:** Debug/Release CTest; warnings as errors; explicit check harness; no fast-math; bounded inputs avoid overflow; exact contract/reference parity.
- **Scope:** L
- [x] 3.2 Implementar y probar el core C++ puro.

### Task 3.3: Crear fachada, bindings y typing

- **Objective:** Exponer una API Pythonic manteniendo el módulo compilado como detalle privado.
- **Deliverables:** `bindings.cpp`, `__init__.py`, `_native.pyi`, `py.typed`, funciones, enum, `OnlineStats`, kwargs/defaults, repr y docstrings.
- **Validation:** `import faststats_cpp` funciona; `_native` no aparece en la API documentada; signatures, tipos y comportamiento coinciden con la referencia.
- **Scope:** L
- [x] 3.3 Implementar la fachada pública, bindings básicos y typing.

### Task 3.4: Traducir errores en ambas direcciones

- **Objective:** Preservar tipos, contexto y control de flujo cuando C++ lanza o un callback Python falla.
- **Deliverables:** Error de dominio C++, translator a excepción Python, callback fallido y manejo superior del host embebido.
- **Validation:** Inputs esperables producen `TypeError`, `ValueError`, `OverflowError` o excepción propia documentada; callback/host propagan el error; ninguna excepción cruza destructor, `noexcept` o `main()`.
- **Scope:** M
- [x] 3.4 Implementar y explicar el contrato de excepciones bidireccional.

### Task 3.5: Enseñar ownership y lifetimes verificables

- **Objective:** Progresar de valores seguros a smart holders y referencias prestadas con políticas explícitas.
- **Deliverables:** Ejemplos de value/copy/move, RAII, `py::smart_holder`, `return_value_policy`, `reference_internal` y `keep_alive` integrados o aislados según riesgo.
- **Validation:** Tests de contadores/destructores prueban destrucción única y relación parent-child; no hay owning raw pointers ni UB; cualquier caso peligroso se analiza sin derribar Python.
- **Risk:** Una política incorrecta puede corromper memoria; cada ejemplo debe justificar owner, borrower y duración en una tabla.
- **Scope:** L
- [x] 3.5 Implementar la ruta de ownership, lifetimes y call policies.

### Task 3.6: Añadir containers copiados y buffers seguros

- **Objective:** Comparar la comodidad de convertir iterables a `std::vector` con acceso buffer sin copia innecesaria.
- **Deliverables:** `summarize`, `summarize_buffer` y `normalize_in_place` sobre `array('d')`/`memoryview`, con NumPy solo como ampliación.
- **Validation:** Tests cubren contiguo/read-only/writable, wrong format, multidimensional, strided, vacío, non-finite, constant, 1/1,000,000/1,000,001 elementos y valores en/a ambos lados de `abs(value)=1e150`; no partial mutation ni pointer retenido; buffer path mantiene GIL y documenta no concurrent mutation.
- **Risk:** Alignment y strides varían; rechazar contratos no soportados antes de llamar el core.
- **Scope:** L
- [x] 3.6 Implementar y documentar conversiones y buffer protocol.

## Phase 4: Rutas avanzada y hero

### Task 4.1: Añadir callbacks y trampolines acotados

- **Objective:** Mostrar llamadas C++→Python y overrides sin ocultar GIL, lifetime ni propagación de error.
- **Deliverables:** Ejemplo de callback de progreso y laboratorio aislado de virtual override/trampoline con `py::smart_holder`.
- **Validation:** Callback válido recibe eventos; callback que lanza vuelve como excepción Python; owner se mantiene y libera; destructor no llama Python.
- **Scope:** L
- [x] 4.1 Implementar callbacks y trampolines con ownership explícito.

### Task 4.2: Liberar el GIL y coordinar threads

- **Objective:** Permitir progreso concurrente alrededor de trabajo C++ puro sin acceder a Python fuera de una región válida.
- **Deliverables:** Owned `summarize_many`, GIL release/reacquire y rendezvous bajo `FASTSTATS_TEST_HOOKS` en target separado.
- **Validation:** Simultaneous entry; serial/GIL-held fails; release wheel macro off and no hook API/symbol source compiled; parity/timeout/state audit; no Python/borrowed buffers in region.
- **Risk:** Callbacks o traducción de errores con GIL liberado pueden bloquear o corromper; fronteras mínimas y revisión específica.
- **Scope:** L
- [x] 4.2 Implementar GIL, threads y tests deterministas.

### Task 4.3: Diseñar benchmarks educativos

- **Objective:** Medir por separado overhead, conversión y cómputo antes de afirmar que C++ conviene.
- **Deliverables:** `benchmarks/benchmark.py`, datasets deterministas y guía de interpretación Debug/Release/batching.
- **Validation:** Verifica paridad antes de medir; usa warm-up, repeticiones, mediana y varios tamaños; incluye un caso pequeño donde native puede perder; no impone speedup fijo.
- **Scope:** M
- [x] 4.3 Crear benchmark reproducible e interpretación honesta.

### Task 4.4: Construir y verificar sdist/wheel

- **Objective:** Convertir el proyecto en artefactos PEP 517 e interpretar compatibilidad real.
- **Deliverables:** Metadata/config, constraints-applied `verify_artifacts.py`, temp outputs, tag/content inspection, stubtest and strict consumer.
- **Validation:** Sdist→unpack→wheel con pip >=25.3 y `PIP_BUILD_CONSTRAINT`; clean install; pip check/smoke; `python -m mypy.stubtest faststats_cpp`; `python -m mypy --strict tests/typing_consumer.py`; no test hook; tag vs extra C++ ABI audit; no abi3 retag.
- **Risk:** El wheel local no representa otros OS/architectures; declarar solo el target construido.
- **Scope:** L
- [x] 4.4 Implementar packaging, inspección de tags y clean install.

### Task 4.5: Crear el laboratorio de embedding

- **Objective:** Iniciar un intérprete CPython desde un executable C++ y ejecutar una estrategia local confiable.
- **Deliverables:** `embed-python/`, target `pybind11::embed`, CLI `--strategy-dir`, módulo fijo y lifecycle RAII.
- **Validation:** Canonical trusted dir en `sys.path`; cwd externo con shadow module no se carga; success/missing/raise/invalid result dan exit codes; handles mueren antes del interpreter; no user eval.
- **Risk:** El orden de teardown es crítico; mantener todos los handles dentro del scope del intérprete.
- **Scope:** L
- [x] 4.5 Implementar y explicar embedding seguro de CPython.

### Task 4.6: Añadir debugging, warnings y sanitizers

- **Objective:** Dar un flujo reversible para diagnosticar errores nativos sin convertir crashes en ejercicios normales.
- **Deliverables:** Perfiles CMake Debug/Sanitized, símbolos, warnings y guía GCC/Clang/MSVC/debuggers.
- **Validation:** Debug build conserva símbolos; ASan/UBSan ejecuta core/tests en plataformas compatibles o registra skip; no se fuerzan flags incompatibles dentro de CPython.
- **Scope:** M
- [x] 4.6 Crear la ruta de depuración y auditoría de memoria.

### Task 4.7: Auditar free-threading y subinterpreters sin declarar soporte

- **Objective:** Enseñar qué habría que probar antes de afirmar compatibilidad avanzada.
- **Deliverables:** Checklist de estado global, allocators, holders, callbacks, locks, module init y lifecycle.
- **Validation:** El capstone base no usa `mod_gil_not_used()` ni promete subinterpreter safety; la documentación separa probado, diseñado y trabajo futuro.
- **Scope:** M
- [x] 4.7 Documentar la auditoría hero de runtimes avanzados.

## Phase 5: Pedagogía, localización y navegación

### Task 5.1: Auditar el microciclo y la evaluación

- **Objective:** Confirmar que cada subsección técnica ya enseña de forma gradual y verificable.
- **Deliverables:** Objetivos, prerrequisitos/glosario, contexto, teoría mínima, predicción, ejemplos, TODO/pistas, happy/edge cases, errores, soluciones, checkpoints, rúbrica, reflexión y accessibility review.
- **Validation:** Cada ruta tiene outcome y autoevaluación; ningún andamiaje esencial se pospone hasta el final; la rúbrica cubre corrección/API/seguridad/tests/medición/packaging; headings/links/tables/visuals tienen estructura y alternativa textual accesible.
- **Scope:** L
- [x] 5.1 Completar la auditoría pedagógica integral.

### Task 5.2: Crear la versión española

- **Objective:** Traducir el capítulo completo manteniendo precisión y enlaces localizados.
- **Deliverables:** `chapter-24-python-cpp-integration/README.es.md`.
- **Validation:** Paridad de headings, source refs, comandos, código, advertencias, ejercicios y rúbrica; prerrequisitos apuntan a `README.es.md`.
- **Scope:** L
- [x] 5.2 Traducir y revisar el capítulo en español.

### Task 5.3: Crear las versiones catalana, sueca y árabe

- **Objective:** Completar los otros idiomas con el mismo contrato técnico.
- **Deliverables:** `README.ca.md`, `README.sv.md` y `README.ar.md` con código LTR dentro del wrapper RTL árabe.
- **Validation:** Validador y revisión lingüística/técnica confirman paridad semántica, selectores, enlaces localizados, accesibilidad y código LTR legible.
- **Scope:** XL por conjunto; paralelizable por idioma
- [x] 5.3a Traducir y revisar catalán.
- [x] 5.3b Traducir y revisar sueco.
- [x] 5.3c Traducir y revisar árabe/RTL.

### Task 5.4: Integrar índices y resolver changes concurrentes

- **Objective:** Insertar capítulo 24 antes de apéndices, preservar solo entries realmente implementadas y ordenar 23→24→25 cuando existan.
- **Deliverables:** `README.md`, `README.en.md`, `README.es.md`, `README.ca.md`, `README.sv.md` y `README.ar.md`.
- **Validation:** No crea links a chapters pendientes; preserva 23/25 si ya existen; orden numérico de entries implementadas; language match; English duplicate; manual rebase.
- **Risk:** Tres changes editan los mismos seis índices; esta tarea debe ejecutarse serialmente al final.
- **Scope:** M
- [x] 5.4 Actualizar navegación y reconciliar los índices compartidos.

## Phase 6: Verificación y cierre OpenSpec

### Task 6.1: Ejecutar validación técnica completa

- **Objective:** Demostrar el funcionamiento del core, binding, concurrencia, packaging y embedding en el entorno declarado.
- **Deliverables:** Assets corregidos y resultados de comandos registrados en la revisión de implementación.
- **Validation:** preflight; `python -B chapter-24-python-cpp-integration/tools/verify_all.py` covers survival/first/faststats debug+release/artifacts/embedding; validator; hygiene; diff/status.
- **Risk:** No afirmar plataformas no ejecutadas; registrar compiler, Python, CMake y OS reales.
- **Scope:** L
- [x] 6.1 Ejecutar y registrar la validación técnica end-to-end.

### Task 6.2: Validar documentación y localización

- **Objective:** Confirmar que cinco variantes y seis índices describen exactamente los assets probados.
- **Deliverables:** Salida limpia del root CLI + C++ plugin cuando existe, o standalone temporal y evidencia de migración; correcciones de paridad/enlaces.
- **Validation:** Un solo owner para guard/links/selectors/headings/alt/tables/fences/RTL/hygiene; plugin/source refs/comandos C++ pasan sin duplicar reglas genéricas.
- **Scope:** M
- [x] 6.2 Ejecutar la validación documental y multilingüe.

### Task 6.3: Cerrar trazabilidad de la spec

- **Objective:** Confirmar requisito por requisito que no queda trabajo obligatorio pendiente.
- **Deliverables:** Checklist completa y revisión de escenarios `teach-python-cpp-integration`.
- **Validation:** `openspec validate add-python-cpp-integration-chapter --strict`; `openspec show ... --json --deltas-only`; marcar tareas solo con evidencia.
- **Scope:** S
- [x] 6.3 Validar OpenSpec y cerrar la checklist.
