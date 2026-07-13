## Context

El repositorio es un curso Markdown progresivo y multilingüe. No contiene CMake, código C++, CI ni infraestructura global de packaging. La change activa `add-python-network-programming-chapter` reserva el capítulo 23 y también modificará los seis índices raíz, por lo que esta change reserva el capítulo 24 pero no depende pedagógicamente del capítulo de redes.

La interoperabilidad nativa combina cuatro dominios que suelen enseñarse por separado: C++ básico, el modelo de extensión de CPython, el contrato Pythonic y el packaging binario. El capítulo debe convertirlos en una progresión observable, manteniendo el core C++ independiente del binding y usando un único proyecto que crece con el alumnado.

Las referencias oficiales vigentes al diseñar la proposal son CPython 3.11+; pybind11 3.0.4; scikit-build-core 1.0.3; CMake >=3.20 para el ejemplo y C++17. La spec expresa comportamiento; los ejemplos conservarán versiones verificadas para que una actualización de tooling sea deliberada.

## ASSUMPTIONS

- Assumption: el alumnado domina los fundamentos de Python del curso, pero puede no haber usado C++, un compilador, un linker o una extensión nativa.
- Assumption: el contenido se añadirá como capítulo 24 porque la proposal activa de redes reserva el capítulo 23.
- Assumption: el capítulo 25 de Rust podrá implementarse en paralelo, pero no será prerrequisito de este capítulo.
- Assumption: la ruta principal apunta a CPython 3.11 o posterior; PyPy, GraalPy y otros intérpretes quedan fuera del contrato.
- Assumption: C++17 será la baseline y el compilador deberá ser GCC, Clang/AppleClang o MSVC con soporte suficiente.
- Assumption: instalar compilador, CMake y dependencias Python puede requerir Internet y permisos del sistema; no se promete setup offline.
- Assumption: `README.md` será la versión inglesa de referencia; se mantendrán español, catalán, sueco y árabe, además de los seis índices raíz.
- Assumption: la implementación comenzará solo tras aprobar la proposal.

## Goals / Non-Goals

### Goals

- Llevar a una persona sin C++ desde el primer ejecutable hasta una extensión nativa profesional y comprensible.
- Separar lógica C++ pura, binding, fachada Python, typing, tests y packaging.
- Enseñar contratos explícitos de tipos, errores, ownership, lifetimes, buffers y GIL.
- Medir antes de optimizar y demostrar el coste de cruzar la frontera.
- Construir y probar artefactos reales fuera del árbol fuente.
- Introducir embedding como laboratorio hero aislado con lifecycle y errores controlados.
- Conservar la estructura pedagógica, localización y seguridad del curso.

### Non-Goals

- Sustituir un curso completo de C++ moderno.
- Enseñar en paralelo Cython, SWIG, Boost.Python, nanobind, ctypes o el C API crudo; se compararán solo para orientar decisiones.
- Prometer Stable ABI/`abi3` con pybind11 o renombrar manualmente tags de wheel.
- Declarar soporte para CPython free-threaded o subinterpreters sin una matriz específica.
- Enseñar GPU, SIMD manual, OpenMP, cross-compilation, Android, iOS, WASM o binding de una biblioteca externa grande.
- Publicar a PyPI, usar credenciales, firmar releases o ofrecer soporte de producción.
- Ejecutar ejemplos de use-after-free, double-free, segfault o UB dentro del intérprete.

## ARCHITECTURE SNAPSHOT

- Component map:
  - `chapter-24-python-cpp-integration/README.md`: capítulo técnico inglés de referencia.
  - `chapter-24-python-cpp-integration/README.{es,ca,sv,ar}.md`: traducciones con paridad temática y técnica.
  - `examples/00-cpp-survival/`: compilación, linking, headers, RAII y errores antes de Python.
  - `examples/01-first-extension/`: primer módulo mínimo con pybind11, CMake y PEP 517.
  - `examples/faststats-cpp/cpp/include/` y `cpp/src/core.cpp`: dominio C++ sin `Python.h` ni tipos pybind11.
  - `examples/faststats-cpp/cpp/src/bindings.cpp`: conversión, errores, lifetimes, buffers y GIL.
  - `examples/faststats-cpp/python/faststats_cpp/`: fachada, `_reference.py`, `_native.pyi` y `py.typed`.
  - `examples/faststats-cpp/cpp/tests/`: tests C++ registrados con CTest.
  - `examples/faststats-cpp/tests/`: tests pytest de contrato, paridad, ownership, buffers, callbacks y threads.
  - `examples/faststats-cpp/benchmarks/`: medición Python/reference/native por tamaños.
  - `examples/faststats-cpp/requirements-dev.lock`: versiones exactas verificadas de pytest, build y mypy.
  - `examples/faststats-cpp/constraints-build.txt`: pins pybind11/scikit-build-core aplicados también al build isolation mediante `PIP_BUILD_CONSTRAINT` con pip >=25.3.
  - `examples/faststats-cpp/tools/verify_native.py`: orquestación cross-platform de CMake Debug/Release, CTest y pytest desde el entorno correcto.
  - `examples/faststats-cpp/tools/verify_artifacts.py`: sdist en temporal, wheel reconstruido desde sdist, clean install, `pip check` y stubtest.
  - `examples/embed-python/`: ejecutable C++ hero que posee un único lifecycle de CPython.
  - `tools/verify_all.py` y `chapter-24-python-cpp-integration/tools/bookcheck_plugin.py`: survival/first/capstone/embedding y checks C++ registrados; standalones genéricos solo existen temporalmente si el capítulo precede al gate raíz.
  - `openspec/changes/add-python-cpp-integration-chapter/specs/teach-python-cpp-integration/spec.md`: requisitos de aceptación.
- Key boundaries:
  - El core C++ no conoce Python y se prueba sin inicializar el intérprete.
  - `_native` es detalle privado; `faststats_cpp` es el contrato público y tipado.
  - `_reference.py` es oráculo de corrección explícito; un error binario no se oculta mediante fallback silencioso.
  - Los datos Python se validan y convierten antes de liberar el GIL; ninguna referencia Python se usa en la región liberada.
  - El laboratorio de embedding es un proyecto separado y no comparte lifecycle con la extensión.
  - La validación genera builds, venvs, wheels, sdists, librerías y caches fuera del chapter tree en rutas temporales; `.gitignore` es defensa adicional, no evidencia de limpieza.
- Data/control flow:
  - Python caller → fachada pública → `_native` → validación/conversión pybind11 → valores C++ propios → core `faststats` → resultado o excepción → traducción Python.
  - `README*.md`: seis índices, integrados después de resolver capítulos 23 y 25.
  - `openspec/changes/add-python-cpp-integration-chapter/specs/teach-python-cpp-integration/spec.md`: requisitos normativos.
- `faststats_cpp` layout:
  - `pyproject.toml`: metadata PEP 517 y backend scikit-build-core.
  - `CMakeLists.txt`: targets C++17, extensión, tests y opciones Debug/sanitizers.
  - `cpp/include/faststats_cpp/core.hpp` y `cpp/src/core.cpp`: dominio C++ puro sin `Python.h` ni tipos pybind11.
  - `cpp/src/bindings.cpp`: conversión, validación, excepciones, ownership y GIL.
  - `cpp/tests/core_tests.cpp`: tests C++ registrados con CTest sin dependencia de Python.
  - `python/faststats_cpp/__init__.py`: fachada pública y mensajes de import claros.
  - `python/faststats_cpp/_reference.py`: oráculo Python explícito; no fallback silencioso.
  - `python/faststats_cpp/_native.pyi` y `py.typed`: contrato de tipos.
  - `tests/`: contrato, paridad, errores, buffers, lifetimes, callbacks y concurrencia.
  - `benchmarks/benchmark.py`: medición educativa por tamaños.
  - `tools/verify_native.py` y `tools/verify_artifacts.py`: comandos reproducibles con outputs en temporales.
  - `.gitignore`: `.venv`, build, dist, wheels, extensiones compiladas y caches locales.
- Key boundaries:
  - El core C++ no conoce Python y se prueba de forma autónoma.
  - `_native` es privado; el consumidor importa `faststats_cpp`.
  - `_reference.py` define semántica y paridad, pero no oculta un módulo nativo roto.
  - Ningún puntero prestado desde un objeto Python sobrevive a la llamada que lo adquirió.
  - Ninguna región con GIL liberado contiene `py::object`, callbacks o llamadas al C API.
  - El host de embedding controla un único lifecycle y destruye objetos Python antes del intérprete.
- Data/control flow:
  - Python público → validación/conversión pybind11 → valores/RAII C++ → core C++ → resultado o excepción C++ → traducción estable → Python.
  - Buffer Python → inspección de formato/shape/strides/writable → préstamo acotado a la llamada → core → retorno sin conservar pointer.
  - Trabajo largo → conversión completa → `py::gil_scoped_release` → core C++ puro → recuperación del GIL → resultado/error Python.

## Pedagogical Routes

### Ruta esencial — 4 sesiones de 45–60 minutos

- Modelo mental: source, compiler, object, linker, shared library, loader, import y wheel.
- Supervivencia C++: tipos, funciones, headers, `const`, referencias, `std::vector`, scope, RAII y excepciones.
- Preflight del toolchain y lectura de errores de compilación/linking.
- Primera función C++ importada desde Python.
- Outcome: módulo mínimo que compila limpiamente y tiene un test Python.

### Ruta profesional — 5 sesiones de 45–60 minutos

- Oráculo Python y contrato antes de optimizar.
- Separación core/binding/fachada y builds Debug/Release.
- Funciones, enums, clase `OnlineStats`, kwargs, defaults, repr y typing.
- Excepciones C++→Python y contrato de error Pythonic.
- RAII, `py::smart_holder`, return policies, `reference_internal` y `keep_alive`.
- Outcome: paquete `faststats_cpp` con API pública, core probado y ownership explícito.

### Ruta avanzada — 5 sesiones de 45–60 minutos

- Conversión de iterables frente a buffers `array`/`memoryview`.
- Validación de format, ndim, strides, contigüidad, alignment y writable.
- Callbacks/trampolines, GIL, threads, shared state y coordinación determinista.
- Benchmarking Debug/Release, batching y coste de frontera.
- Wheel/sdist, tags, ABI, clean install y diagnóstico de loader.
- Outcome: extensión medible, concurrente y empaquetada sin claims universales.

### Ruta hero — 3–4 sesiones de 45–60 minutos

- Debuggers, símbolos, warnings y sanitizers sobre el core donde se soporten.
- Embedding de CPython con `py::scoped_interpreter` y estrategia local confiable.
- Auditoría conceptual de Stable ABI, free-threading y subinterpreters.
- Endurecimiento del capstone, rúbrica final y decisión “cuándo no usar C++”.
- Outcome: capstone y host embebido verificados con límites de compatibilidad explícitos.

Cada subsección seguirá el microciclo: objetivo/contexto → teoría mínima → predecir → ejecutar → observar → modificar → comprobar → happy path → edge case → error común → solución explicada → reflexión.

## Capstone Contract

- Todas las APIs batch aceptan entre 1 y 1,000,000 muestras. `summarize(samples, *, threshold)` acepta exclusivamente built-in `int`/`float`, excluye `bool`, `Fraction`, `Decimal`, NumPy scalars y objetos `__float__`; los enteros exigen `abs(x)<=2**53`. `summarize_buffer(buffer, *, threshold)` y `normalize_in_place(buffer)` aceptan doubles. En todos los caminos cada valor debe ser finito y satisfacer `abs(value)<=1e150`; el threshold debe ser finito y estar en `[0,1e150]`.
- Ambas devuelven un `Summary` inmutable con `count`, `minimum`, `maximum`, `mean`, `anomaly_count` y `anomaly_ratio`.
- La media final usa `mean += (value - mean) / count` en input order, tanto en Python como C++, sin fast-math. Después, una segunda pasada compara cada muestra con ese `Summary.mean` final; una anomalía cumple `delta > threshold` y `not isclose(delta, threshold, rel_tol=1e-12, abs_tol=1e-12)`; igualdad/banda no cuenta.
- `anomaly_ratio` es `anomaly_count / count`. Los floats reference/native se comparan con `rel_tol=1e-12` y `abs_tol=1e-12`.
- Colección vacía, valor no finito o threshold inválido producen `ValueError`; tipo/elemento no numérico o `bool` produce `TypeError`; una validación fallida no muta estado.
- `normalize_in_place(buffer)` exige entre 1 y 1,000,000 doubles, todos finitos y con `abs(value)<=1e150`, en un buffer writable, 1D y contiguo. Valida el buffer completo antes de mutar y transforma `(x-min)/(max-min)`; si todos los valores son iguales, escribe `0.0` en todos.
- `OnlineStats.add(value)`, `extend(values)`, `reset()` y properties `count`, `minimum`, `maximum`, `mean` mantienen estadísticas incrementales. Cada valor acepta el mismo dominio built-in `int`/`float` y los mismos límites que el iterable batch; el estado total no supera 1,000,000 muestras. En estado vacío, min/max/mean son `None`; un tipo, valor o extensión que exceda el límite deja el estado anterior intacto.
- El API convenient iterable copia a owned C++ storage. Los APIs buffer prestan memoria solo durante la llamada, mantienen el GIL y prohíben mutación concurrente por el caller.

## Decisions

### Decision: C++17 como baseline y subconjunto deliberado

C++17 ofrece `std::optional`, RAII maduro y soporte amplio en GCC/Clang/MSVC sin exigir C++20. El capítulo enseñará solo construcciones necesarias para el proyecto y tratará los diagnósticos del compilador como feedback, no como castigo.

Alternatives considered:

- C++20: mejora algunas APIs, pero reduce compatibilidad y añade conceptos que no benefician el primer binding.
- Curso C++ completo antes de integrar: sería más exhaustivo, pero impediría llegar gradualmente a un resultado Python visible.

### Decision: pybind11 3.x con CMake y scikit-build-core

pybind11 reduce el uso directo del C API y pybind11 3 incorpora `py::smart_holder`. CMake modela el build nativo y scikit-build-core conecta CMake con PEP 517 desde `pyproject.toml`. El ejemplo registrará un conjunto verificado dentro de los rangos de major compatibles y conservará instrucciones de actualización.

CMake 3.20 se elige deliberadamente sobre el mínimo 3.15 de pybind11/scikit-build-core para disponer de un comportamiento FindPython moderno y homogéneo sin cargar el capítulo con ramas legacy. El preflight valida pip >=25.3, pybind11 >=3.0.4,<4, scikit-build-core >=1.0.3,<2 y build/mypy. `constraints-build.txt` pinnea pybind11 3.0.4 y scikit-build-core 1.0.3; todos los PEP 517 builds de aceptación reciben ese archivo mediante `PIP_BUILD_CONSTRAINT` y registran las versiones del entorno aislado.

Alternatives considered:

- `setup.py`/setuptools: sigue siendo posible, pero mezcla configuración Python y compilador con patrones heredados.
- Compilación manual: es útil para explicar una vez el linker, pero no es una base portable de packaging.
- nanobind/Cython/SWIG: tecnologías válidas, pero una segunda ruta diluiría ownership, GIL y packaging.

### Decision: proyecto único con oráculo Python explícito

`faststats_cpp` calculará resumen, anomalías y normalización de lotes numéricos. Primero se fijará la semántica en `_reference.py`; después el core C++ deberá producir resultados equivalentes. La fachada no capturará cualquier `ImportError` para activar un fallback silencioso: diferenciará “extensión no construida” de “wheel incompatible o rota”.

### Decision: core C++ separado del binding

El core aceptará tipos C++ propios y devolverá valores o errores C++ sin conocer Python. Esto permite CTest, sanitizers y benchmarking del algoritmo por separado, y reduce el tramo que debe razonar simultáneamente sobre dos runtimes.

### Decision: ownership seguro antes de borrowing avanzado

La progresión empieza con valores y copias, continúa con RAII y `py::smart_holder`, y solo después introduce referencias prestadas con políticas explícitas. No se aceptará un owning raw pointer en la API pública. Los tests usarán contadores/destructores observables y subprocess solo cuando aislar un fallo sea imprescindible; no provocarán UB como ejercicio normal.

### Decision: buffer protocol estándar antes de NumPy

El capítulo usará `array('d')` y `memoryview` de la librería estándar. `summarize_buffer` aceptará solo buffers unidimensionales, contiguos y de `double`; `normalize_in_place` además exigirá writable. Ambos mantendrán el GIL durante todo el préstamo y su contrato prohibirá mutación concurrente externa; no se intentará demostrar zero-copy concurrente. NumPy se mencionará como siguiente paso, no como dependencia obligatoria.

### Decision: GIL liberado solo sobre datos C++ propios

La conversión y validación ocurren con GIL. `py::gil_scoped_release` envolverá únicamente trabajo sobre storage C++ owned/copied; nunca un pointer prestado de `Py_buffer`/`memoryview`, y nunca `normalize_in_place`. Un callback se ejecutará fuera de esa región o tras `py::gil_scoped_acquire`; las excepciones se traducirán después de recuperar el GIL.

El test de concurrencia incluirá un hook exclusivo de tests implementado en C++17 con `std::mutex` y `std::condition_variable`: dos calls deben entrar en la región native antes de continuar. Se compila solo con `FASTSTATS_TEST_HOOKS` en un target de test separado; la extensión Release/wheel no define el macro ni exporta el hook. Así, una ejecución serial/GIL-held no pasa y el artefacto no shippea estado global de test.

### Decision: rendimiento basado en hipótesis y paridad

Los benchmarks validarán igualdad antes de medir, usarán warm-up, varias repeticiones, mediana y varios tamaños. Mostrarán al menos un lote pequeño donde C++ no gana por el overhead. No habrá umbral normativo de speedup dependiente del hardware.

### Decision: wheel real, tags reales y no `abi3` artificial

El capítulo construirá sdist y wheel mediante PEP 517 dentro de directorios temporales. `verify_artifacts.py` desempaquetará el sdist, reconstruirá el wheel desde ese source distribuido, lo instalará en un venv/cwd temporal, ejecutará `pip check`, smoke tests y `python -m mypy.stubtest faststats_cpp`. Los wheel tags expresan Python/ABI/plataforma; compiler version, C++ ABI y shared-library dependencies son compatibilidades adicionales que se registran/auditan, no información codificada directamente por el tag. Stable ABI/Limited API se explicarán, pero no se renombrará ni declarará `abi3` manualmente.

### Decision: embedding aislado del módulo de extensión

`embed-python/` tendrá su propio executable y lifecycle. Recibirá `--strategy-dir`, resolverá/canonicalizará un directorio de assets confiable, insertará exclusivamente esa ruta antes de importar un nombre de módulo fijo y se probará desde un cwd ajeno que contenga un módulo señuelo. Pasará datos tipados y capturará excepciones en `main()`. No evaluará strings aportadas por usuario ni mezclará su teardown con el capstone de extensión.

### Decision: soporte free-threaded y subinterpreters no declarado

Aunque pybind11 3 incluye mecanismos relacionados, el módulo base no usará `mod_gil_not_used()` ni prometerá subinterpreter safety. La ruta hero proporciona una checklist de estado global, allocators, holders, callbacks y locks; el soporte requeriría otra matriz y change si se quisiera aceptar formalmente.

### Decision: validación documental local e independiente

El root gate o fallback temporal comprobará Python 3.11+, enlaces, selectores, headings, fences, comandos y marcadores `source-ref`. Los bloques Python seguros podrán ejecutarse en temporal con timeout; los fragmentos C++ deberán corresponder a archivos compilados por targets reales.

Si `add-book-quality-gates` se aprueba e implementa primero, `chapter-24-python-cpp-integration/tools/bookcheck_plugin.py` expondrá el API versionado `register(registry)` y registrará únicamente checks C++/CMake/source-ref; el root poseerá Markdown/paridad/accesibilidad/higiene. Mientras no exista, `validate_docs.py`/`check_hygiene.py` serán standalones temporales; tests de equivalencia precederán su eliminación/migración, sin parsers genéricos duplicados.

## Risks / Trade-offs

- Alta carga cognitiva → cuatro rutas, un solo proyecto y resultados ejecutables por checkpoint.
- Toolchains diferentes por SO → preflight, tabla de comandos y lenguaje de “validado” distinto de “diseñado para”.
- Cambios en pybind11/scikit-build-core → rangos de major, versiones verificadas registradas y referencias oficiales versionadas.
- Segfaults y UB frustrantes → core aislado, RAII, no raw ownership, tests y sanitizers antes de borrowing avanzado.
- Expectativa de velocidad automática → oráculo, profiling conceptual, lotes múltiples y ningún speedup contractual.
- Import accidental desde source tree → tests obligatorios desde wheel instalado en cwd temporal.
- Lifetimes de buffers → no conservar pointers, validar metadatos y cubrir readonly/strided/wrong-format.
- Deadlocks por GIL/callbacks → región nativa pequeña, datos propios, coordinación determinista y timeouts.
- ABI mal interpretada → inspección de filename/contenido y prohibición de retag manual.
- Embedding ejecuta con permisos del proceso → módulo local confiable, sin eval de input y errores capturados arriba.
- Traducción extensa → congelar código/IDs antes de localizar y validar paridad automáticamente.
- Conflictos de índices con capítulos 23/25 → integrar esos seis archivos de forma serial y rebasar antes del merge.
- Artefactos pesados → todos los verificadores usan temporales y el owner de hygiene escanea también rutas ignoradas; `.gitignore` solo protege experimentos manuales.

## EXECUTION ORDER

1. Aprobar la proposal, reservar capítulo/capability y congelar baseline y límites.
2. Crear preflight y C++ survival kit; validar primer executable antes de involucrar Python.
3. Construir el módulo pybind11 mínimo con CMake/scikit-build-core.
4. Fijar API/oráculo Python y tests de contrato antes de optimizar.
5. Implementar y probar el core C++ autónomo.
6. Añadir fachada, bindings básicos, typing y errores.
7. Añadir ownership/lifetimes y después buffers; no avanzar sin tests de cada frontera.
8. Añadir callbacks y GIL solo cuando el core no dependa de objetos Python.
9. Medir Debug/Release después de congelar corrección y granularidad.
10. Construir sdist/wheel e instalar desde entorno/cwd limpios.
11. Implementar embedding y tooling de debugging como ruta hero aislada.
12. Auditar pedagogía y congelar bloques/código.
13. Traducir español; catalán, sueco y árabe pueden continuar en paralelo.
14. Integrar índices en orden 23 → 24 → 25 y ejecutar validación final.

## DEFINITION OF DONE

- `openspec validate add-python-cpp-integration-chapter --strict` pasa.
- `openspec show add-python-cpp-integration-chapter --json --deltas-only` reconoce todos los requisitos y escenarios.
- Existen cinco variantes completas y los seis índices enlazan el capítulo 24 en el idioma correcto.
- Un alumno sin C++ previo completa preflight, primer executable y primera extensión siguiendo el capítulo.
- El build C++17 configura fuera del source tree y registra versiones reales del entorno validado.
- El core C++ pasa CTest sin importar/inicializar Python.
- `python -B chapter-24-python-cpp-integration/examples/faststats-cpp/tools/verify_native.py --profile debug` y `--profile release` ejecutan configure/build/CTest/pytest desde temp paths y el package construido.
- `python -B chapter-24-python-cpp-integration/examples/faststats-cpp/tools/verify_artifacts.py` reconstruye wheel desde sdist, clean-installs, ejecuta `pip check`, smoke y `python -m mypy.stubtest faststats_cpp`.
- `verify_artifacts.py` también ejecuta `python -m mypy --strict tests/typing_consumer.py` contra el wheel instalado y comprueba que no existe el test hook.
- `verify_all.py` cubre survival/first/capstone/artifacts/embedding; con root-first, `tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py` cubre docs/hygiene/source refs; con chapter-first pasan standalones equivalentes que luego se retiran tras migración probada.
- `faststats_cpp` mantiene `_native` privado, expone `.pyi`/`py.typed` y no oculta un binario roto mediante fallback silencioso.
- Ningún pointer de buffer ni referencia prestada sobrevive fuera de su contrato documentado.
- Los buffers prestados mantienen el GIL y no se usan en el camino concurrente; solo owned/copied C++ storage entra en la región GIL-released.
- Ninguna excepción C++ cruza sin traducir el límite del módulo o `main()`.
- Los tests de concurrencia usan coordinación determinista y timeouts.
- El benchmark verifica resultados, mide varias escalas y no promete speedup fijo.
- Se construyen sdist y wheel; el wheel se instala y prueba desde venv/cwd temporales.
- Los tags se explican según el artefacto real y no se falsifica `abi3`.
- El ejemplo de embedding controla init, import, excepción y teardown con código confiable.
- Sanitizers pasan sobre el core donde estén disponibles o registran un skip explicado.
- La ruta base no declara soporte free-threaded ni subinterpreter.
- El validator documental pasa y no deja caches o binarios inesperados en el repositorio.
- La revisión pedagógica y accesible confirma objetivos, prerrequisitos/glosario, contexto, teoría mínima, ejemplos, ejercicios, pistas, happy/edge cases, errores comunes, soluciones, reflexión, headings jerárquicos, links descriptivos y alternativas textuales.
- La revisión de alcance confirma ausencia de publicación remota, secretos, UB operativo, GPU/SIMD/OpenMP, cross-compilation y un curso C++ completo.

## References

- [Python: Extending and Embedding](https://docs.python.org/3/extending/index.html)
- [pybind11 build systems](https://pybind11.readthedocs.io/en/stable/compiling.html)
- [pybind11 return-value and call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html)
- [pybind11 smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html)
- [scikit-build-core getting started](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html)
- [CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html)

## Open Questions

None.
