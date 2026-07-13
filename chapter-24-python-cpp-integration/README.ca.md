# Capítol 24: Integració de Python i C++ — De zero a hero

[English](README.md) | [Español](README.es.md) | Català | [Svenska](README.sv.md) | [العربية](README.ar.md)

Aquest capítol ensenya una frontera, no dos llenguatges inconnexos: Python conserva una API amable mentre C++ fa treball nadiu ben delimitat. Comences sense C++, compiles un executable petit, construeixes una primera extensió i acabes amb el paquet tipat `faststats_cpp` i un host separat que incrusta Python.

Els projectes es van verificar a Linux amb CPython 3.13.11, GCC 13.3.0, CMake 4.1.2, pip 25.3, pybind11 3.0.4 i scikit-build-core 1.0.3. El disseny apunta a CPython 3.11+, C++17, CMake 3.20+ i GCC/Clang/MSVC; aquest registre no afirma que tots els targets s'hagin executat.

## Objectius i prerequisits

En acabar podràs:

- distingir compilador, linker, loader, API/ABI de Python, ABI de C++ i tags de wheel;
- llegir el subconjunt C++17 necessari: valors, referències, `const`, vectors, classes, RAII, smart pointers i excepcions;
- separar core independent de Python, binding pybind11 fi, mòdul nadiu privat i façana pública tipada;
- raonar sobre còpies, memòria prestada, owners, lifetimes, Global Interpreter Lock (GIL), callbacks i threads;
- construir sdist i wheel i demostrar l'artefacte instal·lat en un entorn net;
- mesurar si la frontera ajuda sense suposar que C++ sempre és més ràpid;
- incrustar una estratègia Python local fiable amb inici i tancament controlats.

Preparació: [funcions](../chapter-11-functions/README.ca.md), [programació orientada a objectes](../chapter-12-oop/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md), [mòduls](../chapter-15-modulos/README.ca.md), [entorns](../chapter-16-entornos/README.ca.md), [testing](../chapter-18-testing/README.ca.md), [logging](../chapter-20-logging/README.ca.md) i [introspecció](../chapter-22-introspection/README.ca.md). No cal C++ previ.

Cal un compilador C++ local; instal·lar-lo pot requerir Internet o permisos del sistema. Els builds acceptats escriuen en temporals. No esborris dades alienes per compensar un build confús.

## Tria una ruta

| Ruta | Temps | Resultat executable | Comprovació |
|---|---:|---|---|
| Essencial | 4 sessions de 45–60 min | executable i extensió `hello_cpp` | explicar compile/link/load i reconstruir després d'un canvi |
| Professional | 5 sessions | core, façana, errors i ownership tipats | passen contracte nadiu/referència i lifetimes |
| Avançada | 5 sessions | buffers, callbacks, GIL i wheel segurs | passen concurrència i instal·lació neta |
| Hero | 3–4 sessions | core amb sanitizers i estratègia incrustada | declarar límits i decidir quan no usar C++ |

Un checkpoint de ruta és útil tot sol; no equival a acabar les rutes posteriors.

## Glossari i mapa de la frontera

- **Compilador:** converteix un source C++ en dades objecte amb codi màquina.
- **Linker:** connecta objectes i llibreries i resol noms.
- **Loader:** carrega executable o llibreria compartida al procés.
- **API:** noms i comportament que usa el caller.
- **ABI:** contracte binari; ABI CPython, ABI C++ i llibreries de plataforma són restriccions diferents.
- **RAII:** el lifetime d'un objecte C++ controla l'alliberament del recurs.
- **Préstec:** accés temporal sense transferir ownership.
- **GIL:** lock de CPython necessari en tocar objectes Python o la C API.
- **Wheel:** arxiu instal·lable amb tags de Python, ABI i plataforma.

```text illustrative
caller Python
  -> façana pública faststats_cpp
  -> binding privat _native (validar i convertir)
  -> valors C++ propis O buffer prestat durant la crida
  -> core faststats independent de Python
  -> Summary o excepció traduïda
```

La façana és el contracte públic; `_native`, maquinària reemplaçable. El core no inclou `Python.h`. Un buffer prestat no entra mai a la regió sense GIL.

## Preflight del toolchain

Crea un entorn d'un sol ús. La primera instal·lació pot usar xarxa i el gestor del compilador pot demanar permisos.

```console illustrative
python -m venv /tmp/course-cpp-venv
source /tmp/course-cpp-venv/bin/activate       # POSIX
# .\course-cpp-venv\Scripts\Activate.ps1     # PowerShell
python -m pip install -r chapter-24-python-cpp-integration/examples/faststats-cpp/requirements-dev.lock
python -B chapter-24-python-cpp-integration/tools/preflight.py
```

El preflight informa d'intèrpret, arquitectura, entorn, compilador, CMake, pip, pybind11, scikit-build-core, build, pytest i mypy. Repara la capa absent: el loader no arregla un compilador que falta.

Passos per plataforma, separats de la verificació: Ubuntu/Debian usa `build-essential`; macOS, Apple Command Line Tools amb `xcode-select --install`; Windows, Visual Studio Build Tools amb **Desktop development with C++** i Developer PowerShell. Poden requerir xarxa/permisos. Instal·la tooling Python/CMake bloquejat només al venv, repeteix preflight i declara només la plataforma executada.

Els builds PEP 517 acceptats fixen `PIP_BUILD_CONSTRAINT` a `constraints-build.txt`, de manera que l'aïllament usa pybind11 3.0.4 i scikit-build-core 1.0.3. Això no limita els paquets del runtime.

### Diagnostica la fase, no el símptoma

| Observació | Fase | Primera pregunta | Acció reversible |
|---|---|---|---|
| sintaxi o tipus desconegut | compile | es veu la declaració/header? | llegir el primer diagnòstic |
| símbol sense resoldre | link | s'ha enllaçat l'objecte? | revisar sources i llibreries |
| mòdul present que no importa | load | coincideixen tags/dependències? | provar wheel des d'un altre cwd |
| `TypeError` Python | binding/API | compleix el contracte? | reduir a una crida vàlida i una d'invàlida |

## Ruta essencial: primer programa C++

### Sessió 1 — valors, funcions, scope i diagnòstics

Prediu qui destrueix el vector de `ScoreReport report(std::vector<double>{6,8,10})`. Ho fa `ScoreReport`: el vector membre s'allibera en sortir de scope. Això és RAII; no hi ha cap `free()` manual.

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

Happy path: surt `practice batch: mean=8`. Edge case: vector buit llança `std::invalid_argument` i `main()` el captura. Error recuperable: compila per separat `expected_compile_error.cpp` i llegeix el primer diagnòstic; el build normal no l'inclou.

**TODO:** canvia les notes i prediu la mitjana. **Pista:** conserva `const`. **Solució:** `mean += (value - mean) / count` actualitza un `double` propi; encara no hi ha Python ni memòria manual.

Error comú: oblidar el namespace de la implementació. Llegeix el primer diagnòstic, comprova el nom qualificat i reconstrueix només el temporal.

### Sessió 2 — headers, referències, vectors, classes i excepcions

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/include/score.hpp check=cpp:contract -->
```cpp source-ref
class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);
    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;
};
```

El header declara; el source defineix. `const` final promet no mutar. `const std::string&` presta el membre sense copiar mentre viu el report. `explicit` evita conversions implícites. Una excepció recuperable es captura en un límit explícit i no surt d'un destructor.

Checkpoint: explica owner i lifetime de `label`; si no, torna al diagrama de scope.

**Microcicle:** prediu què canvia retornant còpia, executa el happy test i TODO retorna valor. Pista: compara signatures; constructor buit és edge recuperable. Solució: còpia versus dependència de lifetime. Reflexiona quin contracte es manté millor.

### Sessió 3 — compilador, linker i loader

Source→objecte és compile; objectes→executable és link; import activa loader. Practica un error de cada fase.

**TODO:** treu temporalment `src/score.cpp` del target. **Pista:** la declaració continua visible. **Solució:** compile passa, link no troba definicions. Restaura'l immediatament.

Verifica build restaurat i edge sense definició. Reflexiona: el primer diagnòstic assenyala la primera fase trencada; els altres solen ser conseqüències.

### Sessió 4 — primera extensió pybind11

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/01-first-extension/src/bindings.cpp check=cpp:contract -->
```cpp source-ref
PYBIND11_MODULE(hello_cpp, module) {
    module.def("add", &add, py::arg("left"), py::arg("right"));
}
```

La macro defineix l'entrada del loader; CMake construeix, scikit-build-core connecta PEP 517 i el wheel transporta. Instal·la en temporal i importa des d'un altre cwd.

Prediu `hello_cpp.add("20",22)`: `TypeError`, no parseig. Canvia suma per resta, observa el test, restaura i reconstrueix. Això tanca la ruta essencial.

## Ruta professional: congela el contracte abans d'optimitzar

### Sessió 5 — oracle Python i domini exacte

`_reference.py` és semàntica llegible, no fallback. `summarize` accepta 1–1.000.000 `int`/`float` built-in exactes; exclou `bool`, subclasses, `Fraction`, `Decimal`, scalar NumPy i `__float__`. Enters `abs(x)<=2**53`, valors finits `abs(x)<=1e150`, threshold finit `[0,1e150]`.

Mitjana en ordre d'entrada amb `mean += (value - mean) / count`; segona passada contra mitjana final. Delta compta si supera threshold i no és `isclose` a `1e-12`. `[-3,-3,-1]` amb `0.5` dona tres anomalies; igualtat no compta.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/python/faststats_cpp/_reference.py check=cpp:contract -->
```python source-ref
expected = summarize([-3, -3, -1], threshold=0.5)
assert expected.anomaly_count == 3
```

Happy: ints/floats exactes. Edge: una mostra i constants. Errors: buit, no finit, rang, tipus exacte, threshold. Paritat float: tolerància relativa/absoluta `1e-12`.

**TODO:** afegeix un boundary als tests. **Pista:** una restricció cada vegada. Solució: exception class i estat intacte. Reflexiona per què un contracte exacte supera “accepta nombres”.

### Sessió 6 — core, binding, façana i typing

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp check=cpp:contract -->
```cpp source-ref
[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);
```

CTest prova el core sense Python. `bindings.cpp` valida tipus/buffers. `_native` és privat; `__init__.py`, `_native.pyi` i `py.typed` defineixen façana i tipus. La façana distingeix “no construït” de binari trencat i no activa l'oracle silenciosament.

**Microcicle:** prediu quina capa coneix un tipus invàlid, executa CTest/pytest i TODO canvia un default només al stub. Pista: typing i stubtest ho detecten. Restaura el default i reflexiona sobre bindings fins.

### Sessió 7 — classes i errors transaccionals

`OnlineStats.add/extend/reset` exposa count/min/max/mean; buit `(0,None,None,None)`, màxim un milió. `extend` valida abans: després de `[1,2]`, `[3,inf]` conserva `(2,1,2,1.5)`.

L'error de domini esdevé `FaststatsError`; tipus/rang/layout, `TypeError`/`ValueError`. L'error del callback torna després del cleanup RAII. Res no creua `main()`, destructor ni `noexcept`.

**TODO:** estén valors vàlids i afegeix un invàlid; compara estat. **Pista:** storage temporal. Happy: commit; edge: extensió buida; error: rollback. Reflexiona si una operació parcial es pot reintentar.

### Sessió 8 — ownership, policies i smart holders

| Frontera | Owner | Durada préstec | Evidència |
|---|---|---|---|
| `Summary` | wrapper Python | cap | properties read-only |
| `Dataset.metadata` | pare `Dataset` | referència filla | `reference_internal` |
| `BorrowingView` | caller/keep-alive | lifetime view | `keep_alive<1,2>` |
| `TrackedResource` | smart holder únic | transferible | comptador torna a base |

`py::smart_holder` explicita smart pointers i trampolines; no justifica raw owner. `ObserverRunner` reté `ProgressObserver` derivat i el destructor no crida Python.

**TODO:** dibuixa owners. **Pista:** fletxa des de qui destrueix. **Solució:** `reference_internal` lliga fill/pare; `keep_alive` patient/nurse; `consume_resource` mou ownership i allibera una vegada.

Checkpoint professional: Debug/Release i explicació de domini, error i owner.

## Ruta avançada: buffers, GIL, mesura i wheels

### Sessió 9 — iterables copiats i buffers prestats

`summarize` copia a `std::vector`; és còmode però costa. `summarize_buffer` presta buffer 1D `double`, alineat, contigu i stride positiu. `normalize_in_place` també exigeix writable.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/tests/test_buffers.py check=cpp:contract -->
```python source-ref
values = array("d", [2.0, 4.0, 6.0])
faststats_cpp.normalize_in_place(values)
assert values.tolist() == [0.0, 0.5, 1.0]
```

Totes dues mantenen GIL, prohibeixen mutació concurrent i no retenen pointers. Validació completa abans de mutar: NaN, buit, gran, read-only, strided, multidimensional, format/alignment erronis no deixen canvis parcials. Constants→`0.0`. NumPy és opcional; `array('d')`/`memoryview` basten.

**TODO:** prova `memoryview` read-only i strided. **Pista:** format, dimensió, stride i writable abans de llegir. Happy: contigu; edge: constant; error: layout incompatible. Reflexiona quan copiar és més segur que zero-copy.

### Sessió 10 — callbacks, GIL i concurrència determinista

`summarize_many` valida/copia amb GIL, allibera només core amb storage propi i recupera abans del resultat/error. Buffers i callbacks no hi entren.

El test `_faststats_test` amb `FASTSTATS_TEST_HOOKS` usa mutex/condition-variable: dues crides han d'entrar. Una versió serial falla; el wheel no inclou hook.

Error comú: alliberar GIL amb `py::object`. Ordre: validar/convertir → posseir → alliberar → C++ pur → recuperar → Python.

**TODO:** treu `gil_scoped_release` només del target test. **Pista:** dos threads no creuen el rendezvous. Restaura després del timeout; happy demostra entrada simultània. Reflexiona per què un sleep prova menys.

### Sessió 11 — benchmarks honestos

Es valida paritat, warm-up, repeticions, mediana, context i mides 1, 10, 1.000, 100.000. Una crida petita pot perdre per frontera; és evidència.

```console illustrative
python chapter-24-python-cpp-integration/examples/faststats-cpp/benchmarks/benchmark.py --profile release --repeats 7
```

**TODO:** prediu el crossover. **Pista:** batching. **Solució:** mantén Python per feina petita/delegada; C++ només després de correcció i mesura.

### Sessió 12 — sdist, wheel, tags i instal·lació neta

`verify_artifacts.py` crea/inspecciona sdist, reconstrueix wheel des d'ell i l'instal·la en venv/cwd net. Fa `pip check`, smoke, `mypy.stubtest`, consumer estricte i absència del hook.

Tags codifiquen Python/ABI/plataforma, no compiler/C++ ABI/shared libs; s'auditen a part. No reanomenis `abi3`: Limited API, ABI CPython, ABI C++ i plataforma són promeses diferents.

Checkpoint: explica per què source import és més feble que sdist→wheel→venv.

**TODO:** inspecciona el wheel i allò que no promet. **Pista:** tags versus compiler/C++ ABI/shared libs. Happy: clean install; edge: intèrpret aliè; loader error visible. Reflexiona abans de dir portable.

## Ruta hero: debugging, embedding i límits

### Sessió 13 — Debug, warnings i sanitizers

Debug conserva símbols; Release distribueix. Warnings alts són errors. GCC/Clang amb `FASTSTATS_ENABLE_SANITIZERS=ON` aplica ASan/UBSan només al core autònom; altres toolchains fan skip explicat.

No provoquis segfault a Python. Usa diagrames, comptadors, tests C++ i sanitizer, sempre en un build temporal reversible.

**TODO:** executa core sanitized i localitza flags. **Pista:** només targets autònoms. Happy: net; toolchain no suportat: skip; informe: investigació recuperable. Reflexiona sobre el reproducer segur mínim.

### Sessió 14 — incrustar una estratègia fiable

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/embed-python/src/main.cpp check=cpp:contract -->
```cpp source-ref
py::scoped_interpreter interpreter;
py::module_ strategy = py::module_::import("trusted_strategy");
py::object result = strategy.attr("evaluate")(values);
```

El host exigeix `--strategy-dir`, canonicalitza, substitueix `sys.path`, importa nom fix, passa llista tipada i exigeix float exacte. Missing/raise/invalid tenen exits no zero. Un mòdul esquer al cwd no guanya.

Handles moren abans de l'intèrpret; `main()` captura errors. No evalua text ni codi no fiable: Python té permisos del host.

**TODO:** executa good, raising i invalid des del cwd esquer. **Pista:** mòdul del directori canonical. Happy: success; edges: callable/result; error Python: exit no zero. Reflexiona com `eval` canviaria l'amenaça.

### Sessió 15 — free-threading i subinterpreters són auditories futures

No s'usa `mod_gil_not_used()` ni es declara suport. Cal auditar globals, allocators, holders, callbacks, locks, init, dades per intèrpret, teardown i matriu real. Un tag no és evidència.

Cython, nanobind, SWIG, `ctypes` i C API són alternatives, no tutorials paral·lels. GPU, SIMD, OpenMP, cross-compilation, mòbil/WASM, publicació i gran llibreria queden fora.

**TODO:** escriu una matriu sense codi. **Pista:** runtime, intèrprets, callbacks, globals i teardown. Happy: build GIL provat; edges: free-threaded/subinterpreters. Solució: change amb evidència, no tag. Reflexiona el cost de compatibilitat.

## Verificació del capstone

```console illustrative
python -B chapter-24-python-cpp-integration/tools/verify_all.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
```

Cobreix survival, primera extensió, CTest, pytest Debug/Release, concurrència, sanitizer compatible, sdist→wheel, typing, dependències i embedding. L'escaneig ha de trobar zero venv/build/dist/archive/libreria/objecte/cache dins del capítol, també ignorats.

## Exercicis, pistes i solucions explicades

1. **Essencial:** afegeix `range()` a `ScoreReport`; prediu negatius. Pista: min/max en una passada. Solució: ownership a classe i buit abans d'indexar.
2. **Professional:** afegeix `variance` read-only primer a l'oracle. Pista: congela semàntica. Solució: referència→core→binding→stub→CTest→pytest→docs.
3. **Avançat:** compara iterable/buffer per 100.000 doubles. Pista: paritat abans de timing. Solució: atribueix cost a conversió/còpia/frontera.
4. **Hero:** proposa free-threading sense implementar. Pista: globals i accessos Python. Solució: matriu/tests abans de compatibilitat.

## Rúbrica d'autoavaluació

| Àrea | Preparat | Cal repàs | Evidència |
|---|---|---|---|
| Correcció/API | contracte i transaccions coincideixen | només sembla plausible | CTest i paritat pytest |
| Ownership/seguretat | explica owner/préstec/GIL | endevina policies | lifetime, buffers, callbacks, rendezvous |
| Verificació | Debug/Release i artefactes temporals | importa al source | logs i venv net |
| Criteri | mesura i declara límits | promet universalitat | benchmark i auditoria ABI |

Reflexió: quina frontera et genera menys confiança i quina evidència la milloraria? Si només “compila”, afegeix input invàlid, lifetime o packaging.

## Fonts i atribució

Prosa i exercicis originals. Referències: [Python extending and embedding](https://docs.python.org/3/extending/index.html), [build systems pybind11](https://pybind11.readthedocs.io/en/stable/compiling.html), [call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html), [smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html), [scikit-build-core](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html) i [CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html).
