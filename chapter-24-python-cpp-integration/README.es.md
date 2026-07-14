# Capítulo 24: Integración de Python y C++ — De cero a hero

[English](README.md) | Español | [Català](README.ca.md) | [Svenska](README.sv.md) | [العربية](README.ar.md)

Este capítulo enseña una frontera, no dos lenguajes inconexos: Python conserva una API amable mientras C++ realiza trabajo nativo cuidadosamente delimitado. Empiezas sin experiencia en C++, compilas un ejecutable pequeño, construyes una primera extensión y terminas con el paquete tipado `faststats_cpp` y un host separado que embebe Python.

Los proyectos se verificaron en Linux con CPython 3.13.11, GCC 13.3.0, CMake 4.1.2, pip 25.3, pybind11 3.0.4 y scikit-build-core 1.0.3. El diseño apunta a CPython 3.11+, C++17, CMake 3.20+ y GCC/Clang/MSVC, pero este registro no afirma que se hayan ejecutado todos esos destinos.

## Objetivos y prerrequisitos

Al terminar podrás:

- distinguir compilador, linker, loader, API/ABI de Python, ABI de C++ y tags de wheel;
- leer el subconjunto C++17 necesario: valores, referencias, `const`, vectores, clases, RAII, smart pointers y excepciones;
- separar core independiente de Python, binding pybind11 fino, módulo nativo privado y fachada pública tipada;
- razonar sobre copias, memoria prestada, owners, lifetimes, Global Interpreter Lock (GIL), callbacks y threads;
- construir sdist y wheel de plataforma y demostrar el artefacto instalado en un entorno limpio;
- medir si la frontera ayuda en lugar de suponer que C++ siempre es más rápido;
- embeber una estrategia Python local confiable con inicio y cierre controlados.

Preparación: [funciones](../chapter-11-functions/README.es.md), [programación orientada a objetos](../chapter-12-oop/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md), [módulos](../chapter-15-modulos/README.es.md), [entornos](../chapter-16-entornos/README.es.md), [testing](../chapter-18-testing/README.es.md), [logging](../chapter-20-logging/README.es.md) e [introspección](../chapter-22-introspection/README.es.md). No necesitas C++ previo.

Necesitas un compilador C++ local; instalarlo puede requerir Internet o permisos del sistema. Los builds aceptados escriben en temporales. No uses un borrado destructivo para compensar un build confuso.

## Elige una ruta

| Ruta | Tiempo | Resultado ejecutable | Comprobación |
|---|---:|---|---|
| Esencial | 4 sesiones de 45–60 min | ejecutable y extensión `hello_cpp` | explicar compile/link/load y reconstruir tras un cambio |
| Profesional | 5 sesiones | core, fachada, errores y ownership tipados | pasan contrato nativo/referencia y lifetimes |
| Avanzada | 5 sesiones | buffers, callbacks, GIL y wheel seguros | pasan concurrencia e instalación limpia |
| Hero | 3–4 sesiones | core con sanitizers y estrategia embebida | declarar límites y decidir cuándo no usar C++ |

Un checkpoint de ruta tiene valor propio; no equivale a completar las rutas posteriores.

## Glosario y mapa de la frontera

- **Compilador:** convierte un source C++ en datos objeto con código máquina.
- **Linker:** conecta objetos y librerías y resuelve nombres.
- **Loader:** carga el ejecutable o la librería compartida en el proceso.
- **API:** nombres y comportamiento que usa el caller.
- **ABI:** contrato binario. ABI CPython, ABI C++ y librerías de plataforma son restricciones diferentes.
- **RAII:** el lifetime de un objeto C++ controla la liberación de su recurso.
- **Préstamo:** acceso temporal sin transferir ownership.
- **GIL:** lock de CPython necesario al tocar objetos Python o su C API.
- **Wheel:** archivo instalable cuyos tags describen Python, ABI y plataforma.

```text illustrative
caller Python
  -> fachada pública faststats_cpp
  -> binding privado _native (validar y convertir)
  -> valores C++ propios O buffer prestado durante la llamada
  -> core faststats independiente de Python
  -> Summary o excepción traducida
```

La fachada es el contrato público. `_native` es maquinaria reemplazable. El core nunca incluye `Python.h`. Un buffer prestado nunca entra en la región sin GIL.

## Preflight del toolchain

Crea un entorno desechable. La primera instalación puede usar red; el gestor del compilador puede pedir permisos administrativos.

```console illustrative
python -m venv /tmp/course-cpp-venv
source /tmp/course-cpp-venv/bin/activate       # POSIX
# .\course-cpp-venv\Scripts\Activate.ps1     # PowerShell
python -m pip install -r chapter-24-python-cpp-integration/examples/faststats-cpp/requirements-dev.lock
python -B chapter-24-python-cpp-integration/tools/preflight.py
```

El preflight informa de intérprete, arquitectura, entorno activo, compilador, CMake, pip, pybind11, scikit-build-core, build, pytest y mypy. Repara la capa que falta: un truco del loader no arregla un compilador ausente.

Pasos por plataforma, separados de la verificación: Ubuntu/Debian usa el paquete `build-essential`; macOS, Apple Command Line Tools con `xcode-select --install`; Windows, Visual Studio Build Tools con **Desktop development with C++** y su Developer PowerShell. Pueden requerir red/permisos. `requirements-dev.lock` registra versiones directas exactas para el host verificado, pero no tiene grafo transitivo ni hashes y no es un lock hermético multiplataforma. Instálalo solo en el venv, usa `constraints-build.txt` para el build aislado, repite preflight y declara únicamente la plataforma ejecutada.

Los builds PEP 517 aceptados fijan `PIP_BUILD_CONSTRAINT` a `constraints-build.txt`, por lo que el aislamiento usa pybind11 3.0.4 y scikit-build-core 1.0.3. No es lo mismo que limitar paquetes del runtime.

### Diagnostica la fase, no el síntoma

| Observación | Fase | Primera pregunta | Acción reversible |
|---|---|---|---|
| sintaxis o tipo desconocido | compile | ¿se ve la declaración/header? | leer el primer diagnóstico |
| símbolo sin resolver | link | ¿se enlazó el objeto/librería? | revisar sources y link libraries |
| módulo presente que no importa | load | ¿coinciden tags/dependencias? | probar el wheel desde otro cwd |
| `TypeError` de Python | binding/API | ¿cumple el contrato? | reducir a una llamada válida y otra inválida |

## Ruta esencial: primer programa C++

### Sesión 1 — valores, funciones, scope y diagnósticos

Predice quién destruye el vector de `ScoreReport report(std::vector<double>{6, 8, 10})`. Lo hace el valor `ScoreReport`: su miembro vector se libera al salir de scope. Eso es RAII; no hay un `free()` emparejado en el código del alumno.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/src/main.cpp check=cpp:contract -->
```cpp source-ref
const course::ScoreReport report(std::vector<double>{6.0, 8.0, 10.0});
std::cout << report.label() << ": mean=" << report.mean() << '\n';
```

```console illustrative
cmake -S chapter-24-python-cpp-integration/examples/00-cpp-survival -B /tmp/cpp-survival-build -DCMAKE_BUILD_TYPE=Debug
cmake --build /tmp/cpp-survival-build --config Debug
ctest --test-dir /tmp/cpp-survival-build --output-on-failure -C Debug
```

Happy path: aparece `practice batch: mean=8`. Edge case: el vector vacío lanza `std::invalid_argument` y `main()` lo captura. Error recuperable: compila por separado `expected_compile_error.cpp` y lee el primer diagnóstico; no pertenece a CMake y no rompe el build normal.

**TODO:** cambia las tres notas y predice la media. **Pista:** conserva `const` y modifica solo el vector. **Solución:** `mean += (value - mean) / count` actualiza un `double` propio; todavía no intervienen Python ni memoria manual.

Error común: editar un header y olvidar el namespace de la implementación. Lee el primer diagnóstico, comprueba el nombre cualificado y reconstruye el temporal, no caches ajenas.

### Sesión 2 — headers, referencias, vectores, clases y excepciones

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/include/score.hpp check=cpp:contract -->
```cpp source-ref
class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);
    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;
};
```

El header declara lo utilizable; el source lo define. El `const` final promete no mutar el report. `const std::string&` presta el miembro sin copiar y solo vale mientras vive el report. `explicit` evita conversiones implícitas sorprendentes. Una excepción recuperable se captura en un límite explícito; nunca sale de un destructor.

Checkpoint: explica owner y lifetime de la referencia a `label`. Si no puedes, vuelve al diagrama de scope.

**Microciclo:** predice qué cambia al devolver una copia, ejecuta el happy test y TODO devuelve valor. Pista: compara signatures; el constructor vacío sigue siendo edge recuperable. Solución: una copia frente a una dependencia de lifetime. Reflexiona qué contrato se mantiene mejor.

### Sesión 3 — compilador, linker y loader

Source→objeto es compile; objetos→ejecutable/librería es link; importarla activa el loader. “Build” esconde tres fases. Clasifica un error de sintaxis, un símbolo sin definición y un módulo no instalado.

**TODO:** quita temporalmente `src/score.cpp` del target. **Pista:** la declaración sigue visible. **Solución:** compile pasa y link falla al no hallar definiciones. Restaura enseguida el source.

Verifica el build restaurado y el edge sin definición. Reflexiona: el primer diagnóstico señala la primera fase rota; los posteriores suelen ser consecuencias.

### Sesión 4 — primera extensión pybind11

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/01-first-extension/src/bindings.cpp check=cpp:contract -->
```cpp source-ref
PYBIND11_MODULE(hello_cpp, module) {
    module.def("add", &add, py::arg("left"), py::arg("right"));
}
```

`PYBIND11_MODULE` define la entrada del loader. CMake construye; scikit-build-core conecta con PEP 517; el wheel transporta el resultado. Instala en temporal e importa desde otro cwd para no ocultar defectos con el source.

Predice `hello_cpp.add("20", 22)`: pybind11 lanza `TypeError`, no parsea texto. Cambia suma por resta, observa el test fallar, restaura y reconstruye. Ese bucle completa la ruta esencial.

## Ruta profesional: congela el contrato antes de optimizar

### Sesión 5 — oráculo Python y dominio exacto

`_reference.py` es semántica legible, no fallback silencioso. `summarize` acepta 1–1.000.000 `int`/`float` built-in exactos: no `bool`, subclases, `Fraction`, `Decimal`, scalar NumPy ni `__float__`. Los enteros cumplen `abs(x)<=2**53`; valores convertidos finitos `abs(x)<=1e150`; threshold finito `[0,1e150]`.

La media usa orden de entrada y `mean += (value - mean) / count`. Una segunda pasada compara con la media final. Cuenta si delta supera threshold y no es `isclose` con tolerancias `1e-12`. Por eso `[-3,-3,-1]` con `0.5` tiene tres anomalías; la igualdad no cuenta.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/python/faststats_cpp/_reference.py check=cpp:contract -->
```python source-ref
expected = summarize([-3, -3, -1], threshold=0.5)
assert expected.anomaly_count == 3
```

Happy: mezcla exacta de ints/floats. Edge: una muestra o valores iguales. Errores recuperables: vacío, no finito, rango, tipo exacto o threshold. La paridad float usa tolerancia relativa/absoluta `1e-12`.

**TODO:** añade un boundary a tests de referencia y nativo. **Pista:** cambia una restricción cada vez. Solución: comprueba clase de excepción y estado intacto. Reflexiona por qué un contrato exacto es mejor que “acepta números”.

### Sesión 6 — core, binding, fachada y typing

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp check=cpp:contract -->
```cpp source-ref
[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);
```

CTest prueba el core sin Python. `bindings.cpp` valida tipos y buffers Python. `_native` queda privado; `__init__.py` ofrece la API, `_native.pyi` y `py.typed` el typing. La fachada diferencia extensión no construida de binario roto y nunca lo oculta con el oráculo.

**Microciclo:** predice qué capa conoce un tipo Python inválido, ejecuta CTest/pytest y TODO cambia un default solo en el stub. Pista: typing estricto y stubtest deben detectarlo. Restaura el default común y reflexiona por qué un binding fino duplica menos verdad.

### Sesión 7 — clases y errores transaccionales

`OnlineStats.add/extend/reset` expone count/min/max/mean. Vacío significa `(0,None,None,None)`, máximo total un millón. `extend` valida valores y capacidad antes de cambiar nada: tras `[1,2]`, `extend([3,inf])` conserva exactamente `(2,1,2,1.5)`.

La excepción de dominio C++ se traduce a `FaststatsError`; tipo/rango/layout usan `TypeError`/`ValueError`. Una excepción de callback vuelve al caller después del cleanup RAII. Nada cruza `main()`, destructor o `noexcept`.

**TODO:** extiende valores válidos y añade uno inválido; compara antes/después. **Pista:** valida en storage temporal. Happy: commit; edge: extensión vacía; fallo: rollback completo. Reflexiona si sería seguro reintentar una operación parcial.

### Sesión 8 — ownership, policies y smart holders

| Frontera | Owner | Duración del préstamo | Evidencia |
|---|---|---|---|
| `Summary` devuelto | wrapper Python | ninguna | properties read-only |
| `Dataset.metadata` | padre `Dataset` | referencia hija | test `reference_internal` |
| `BorrowingView` | caller/keep-alive | lifetime de view | test `keep_alive<1,2>` |
| `TrackedResource` | smart holder único | ownership transferible | contador vuelve al inicio |

`py::smart_holder` explicita smart pointers y trampolines Python; no justifica un raw pointer owner. `ObserverRunner` retiene un `ProgressObserver` derivado de Python y su destructor no llama Python.

**TODO:** dibuja owners antes del test. **Pista:** la flecha nace donde se controla destrucción. **Solución:** `reference_internal` liga hijo/padre; `keep_alive` liga patient/nurse; `consume_resource` mueve ownership único y libera una vez.

Checkpoint profesional: ejecuta Debug/Release y explica dominio, error y owner de cada operación.

## Ruta avanzada: buffers, GIL, medición y wheels

### Sesión 9 — iterables copiados frente a buffers prestados

`summarize(iterable)` copia a `std::vector<double>`: cómodo pero cuesta conversión/asignación. `summarize_buffer` presta buffer 1D de `double` nativo, alineado, contiguo y stride positivo. `normalize_in_place` exige además writable.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/tests/test_buffers.py check=cpp:contract -->
```python source-ref
values = array("d", [2.0, 4.0, 6.0])
faststats_cpp.normalize_in_place(values)
assert values.tolist() == [0.0, 0.5, 1.0]
```

Ambas APIs mantienen GIL durante el préstamo, prohíben mutación concurrente y no retienen pointers. Validan todo antes de mutar: NaN, vacío, demasiado grande, read-only, strided, multidimensional, formato/alignment incorrectos no dejan cambio parcial. Valores iguales se vuelven `0.0`. NumPy es ampliación opcional; aquí bastan `array('d')` y `memoryview`.

**TODO:** pasa `memoryview` read-only y strided antes de mirar el test. **Pista:** formato, dimensión, stride y writable antes de dereferenciar. Happy: contiguo; edge: constante; error recuperable: layout incompatible. Reflexiona cuándo copiar es más seguro que zero-copy.

### Sesión 10 — callbacks, GIL y concurrencia determinista

Los objetos Python requieren GIL. `summarize_many` valida/copia con GIL, libera solo alrededor del core sobre storage C++ propio y recupera antes de crear resultado o excepción. Buffers y callbacks no entran ahí.

El test no usa sleeps: target `_faststats_test` con `FASTSTATS_TEST_HOOKS` usa mutex/condition-variable; dos llamadas deben entrar antes de continuar. Una versión serial/GIL-held falla. El wheel no compila ni expone el hook.

Error común: soltar GIL alrededor de `py::object`. Secuencia correcta: validar/convertir → poseer → soltar → C++ puro → recuperar → resultado Python.

**TODO:** quita `gil_scoped_release` solo del target de test y predice el rendezvous. **Pista:** los dos threads no cruzan. Restaura tras el timeout acotado; el happy path prueba entrada simultánea. Reflexiona por qué un sleep fijo demuestra menos.

### Sesión 11 — benchmarks honestos

El benchmark verifica paridad, calienta, repite, muestra mediana, registra perfil/plataforma y usa tamaños 1, 10, 1.000 y 100.000. Una llamada pequeña puede ser más lenta por frontera y conversión; es evidencia útil.

```console illustrative
python chapter-24-python-cpp-integration/examples/faststats-cpp/benchmarks/benchmark.py --profile release --repeats 7
```

**TODO:** predice el cruce. **Pista:** compara batching. **Solución:** conserva Python para trabajo pequeño o ya delegado; usa C++ tras corrección y medición representativa.

### Sesión 12 — sdist, wheel, tags e instalación limpia

`verify_artifacts.py` construye e inspecciona sdist, lo desempaqueta, reconstruye el wheel desde esa fuente y lo instala en venv/cwd ajenos. Ejecuta `pip check`, smoke, `mypy.stubtest`, consumidor estricto, rechazos de tipos para tres constructores solo nativos y comprueba ausencia del hook. En hosts compatibles analiza dependencias y falla si `ldd` informa `not found`.

Los tags codifican Python/ABI/plataforma, no compiler, C++ ABI ni todas las shared libraries; se auditan aparte. Nunca renombres a `abi3`: Limited API, ABI CPython, ABI C++ y plataforma son promesas distintas.

Checkpoint avanzado: explica por qué importar desde source vale menos que reconstruir desde sdist e instalar limpiamente.

**TODO:** inspecciona el nombre del wheel y enumera lo que no promete. **Pista:** separa tags de compiler, C++ ABI y shared libs. Happy: clean install; edge: intérprete ajeno; loader error visible. Reflexiona antes de decir “portable”.

## Ruta hero: debugging, embedding y límites

### Sesión 13 — Debug, warnings y sanitizers

Debug conserva símbolos; Release representa distribución. El proyecto trata warnings altos como errores. En GCC/Clang, `FASTSTATS_ENABLE_SANITIZERS=ON` añade ASan/UBSan solo al core autónomo, no indiscriminadamente dentro de CPython. Otros toolchains registran skip.

No provoques segfault en una práctica Python. Explica use-after-free con diagramas, contadores, tests C++ y sanitizers. Usa otro build temporal para poder volver atrás.

**TODO:** ejecuta el core sanitized y localiza flags. **Pista:** solo targets autónomos. CMake escribe evidencia de capacidad; solo `enabled:<compiler>` permite informar éxito y un compiler no soportado produce un skip explícito. Un informe sanitizer inicia una investigación recuperable. Reflexiona sobre el reproducer mínimo seguro.

### Sesión 14 — embeber una estrategia confiable

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/embed-python/src/main.cpp check=cpp:contract -->
```cpp source-ref
py::scoped_interpreter interpreter;
py::module_ strategy = py::module_::import("trusted_strategy");
py::object result = strategy.attr("evaluate")(values);
```

El host exige `--strategy-dir`, canonicaliza el directorio local, sustituye `sys.path`, importa nombre fijo, pasa lista tipada y exige float exacto. Missing/raise/invalid tienen exits no cero. El test usa cwd con módulo señuelo, que no debe ganar.

Los handles mueren antes del intérprete. `main()` captura excepciones. No evalúa texto ni carga módulos no confiables: Python embebido tiene permisos del proceso host.

**TODO:** ejecuta good, raising e invalid desde el cwd señuelo. **Pista:** el módulo fijo viene del directorio canonical. Happy: success; edges: callable/result; excepción: exit no cero. Reflexiona cómo `eval` cambiaría el threat model.

### Sesión 15 — free-threading y subinterpreters son auditorías futuras

El módulo no usa `mod_gil_not_used()` ni declara soporte. Antes hay que auditar estado global, allocators, holders/trampolines, callbacks, locks, inicialización, datos por intérprete, teardown y matriz real. Un tag no es evidencia.

Cython, nanobind, SWIG, `ctypes` o C API son alternativas, no rutas paralelas. GPU, SIMD, OpenMP, cross-compilation, móvil/WASM, publicación, free-threading de producción y gran librería externa quedan fuera.

**TODO:** escribe una matriz de soporte sin tocar código. **Pista:** runtime, intérpretes, callbacks, globals y teardown. Happy probado: build con GIL; edges: free-threaded/subinterpreters. Solución: otra change con evidencia, no un tag. Reflexiona sobre el coste de prometer compatibilidad.

## Verificación del capstone

Ejecuta desde la raíz del repositorio. El verificador crea el venv, los builds y los wheels en directorios temporales, y puede necesitar acceso a la red para la instalación inicial de las herramientas directas con versiones fijadas.

```console illustrative
python -B chapter-24-python-cpp-integration/tools/verify_all.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
```

Se cubren survival, primera extensión, CTest, pytest Debug/Release, concurrencia, sanitizer compatible, sdist→wheel, typing, dependencias y embedding. Un scan explícito debe hallar cero venv/build/dist/archive/librería/objeto/cache dentro del capítulo, incluso ignorados.

## Ejercicios, pistas y soluciones explicadas

1. **Esencial:** añade `range()` a `ScoreReport`. Predice negativos. Pista: min/max en una pasada. Solución: ownership en la clase y vacío antes de indexar.
2. **Profesional:** añade `variance` read-only primero al oráculo. Pista: congela semántica. Solución: referencia→core→binding→stub→CTest→pytest→docs.
3. **Avanzado:** compara iterable/buffer con 100.000 doubles. Pista: paridad antes de timing. Solución: atribuye coste a conversión/copia/frontera, no a una etiqueta de lenguaje.
4. **Hero:** propone free-threading sin implementarlo. Pista: lista globals y accesos Python. Solución: matriz y tests deterministas antes de declarar compatibilidad.

## Rúbrica de autoevaluación

| Área | Preparado | Requiere repaso | Evidencia |
|---|---|---|---|
| Corrección/API | contrato y errores transaccionales coinciden | resultados solo plausibles | CTest y paridad pytest |
| Ownership/seguridad | explica owner, préstamo y GIL | adivina policies | lifetimes, buffers, callbacks, rendezvous |
| Verificación | Debug/Release y artefactos en temporales | importa junto al source | logs y venv limpio |
| Criterio | mide y declara límites | promete velocidad/portabilidad | contexto benchmark y auditoría ABI |

Reflexión: ¿qué frontera inspira menos confianza y qué evidencia la mejoraría? Si solo respondes “compila”, añade un input inválido, lifetime o escenario de packaging.

## Fuentes y atribución

Prosa y ejercicios son originales. Referencias: [Python extending and embedding](https://docs.python.org/3/extending/index.html), [build systems de pybind11](https://pybind11.readthedocs.io/en/stable/compiling.html), [call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html), [smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html), [guía scikit-build-core](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html) y [CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html).
