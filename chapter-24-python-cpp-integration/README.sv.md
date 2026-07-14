# Kapitel 24: Integration mellan Python och C++ — Från noll till hero

[English](README.md) | [Español](README.es.md) | [Català](README.ca.md) | Svenska | [العربية](README.ar.md)

Kapitlet lär ut en gräns, inte två orelaterade språk: Python behåller ett vänligt API medan C++ gör noggrant avgränsat native-arbete. Du börjar utan C++-erfarenhet, kompilerar ett litet program, bygger din första extension och avslutar med det typade paketet `faststats_cpp` samt en separat värd som bäddar in Python.

Projekten verifierades på Linux med CPython 3.13.11, GCC 13.3.0, CMake 4.1.2, pip 25.3, pybind11 3.0.4 och scikit-build-core 1.0.3. Designen riktar sig mot CPython 3.11+, C++17, CMake 3.20+ och GCC/Clang/MSVC, men posten påstår inte att alla mål kördes.

## Lärandemål och förkunskaper

Efter kapitlet kan du:

- skilja compiler, linker, loader, Pythons API/ABI, C++ ABI och wheel-taggar;
- läsa den C++17-del som behövs: värden, referenser, `const`, vektorer, klasser, RAII, smart pointers och exceptions;
- separera en Python-oberoende kärna, tunn pybind11-gräns, privat native-modul och typad publik fasad;
- resonera om kopior, lånat minne, owners, lifetimes, Global Interpreter Lock (GIL), callbacks och threads;
- bygga sdist och plattforms-wheel och bevisa den installerade artefakten i en ren miljö;
- mäta om gränsen hjälper i stället för att anta att C++ alltid är snabbare;
- bädda in en betrodd lokal Python-strategi med kontrollerad start och stängning.

Förkunskaper: [funktioner](../chapter-11-functions/README.sv.md), [objektorientering](../chapter-12-oop/README.sv.md), [exceptions](../chapter-14-exceptions/README.sv.md), [moduler](../chapter-15-modulos/README.sv.md), [miljöer](../chapter-16-entornos/README.sv.md), [testning](../chapter-18-testing/README.sv.md), [loggning](../chapter-20-logging/README.sv.md) och [introspektion](../chapter-22-introspection/README.sv.md). Ingen C++ krävs.

Du behöver en lokal C++-compiler. Installation kan kräva nät och systembehörighet. Godkända byggen skriver till temporära kataloger; radera inte orelaterade data när ett bygge är oklart.

## Välj en väg

| Väg | Tid | Körbart resultat | Kontroll |
|---|---:|---|---|
| Grund | 4 pass à 45–60 min | program och `hello_cpp` | förklara compile/link/load och bygg om efter ändring |
| Professionell | 5 pass | typad kärna, fasad, fel och ownership | kontrakt/paritet/lifetimes passerar |
| Avancerad | 5 pass | säkra buffers, callbacks, GIL och wheel | concurrency och ren installation passerar |
| Hero | 3–4 pass | sanitiserad kärna och inbäddad strategi | ange gränser och avgör när C++ inte passar |

En vägkontroll är värdefull för sig; den betyder inte att senare vägar är klara.

## Ordlista och gränskarta

- **Compiler:** gör maskinkodsobjekt av en C++-source.
- **Linker:** kopplar objekt och bibliotek och löser namn.
- **Loader:** laddar program eller delat bibliotek i processen.
- **API:** namn och beteenden som caller använder.
- **ABI:** binärt kontrakt; CPython ABI, C++ ABI och plattformsbibliotek är olika begränsningar.
- **RAII:** ett C++-objekts lifetime styr resursens cleanup.
- **Lån:** tillfällig åtkomst utan ownership-överföring.
- **GIL:** CPython-lås som krävs vid Python-objekt eller C API.
- **Wheel:** installerbart arkiv med taggar för Python, ABI och plattform.

```text illustrative
Python-caller
  -> publik fasad faststats_cpp
  -> privat binding _native (validera och konvertera)
  -> ägda C++-värden ELLER buffer lånad under anropet
  -> Python-oberoende faststats-kärna
  -> Summary eller översatt exception
```

Fasaden är kontraktet; `_native` är utbytbar mekanik. Kärnan inkluderar aldrig `Python.h`. En lånad buffer går aldrig in i regionen utan GIL.

## Preflight för toolchain

Skapa en tillfällig miljö. Första installationen kan använda nätet och compiler-installation kan kräva administratörsrättigheter.

```console illustrative
python -m venv /tmp/course-cpp-venv
source /tmp/course-cpp-venv/bin/activate       # POSIX
# .\course-cpp-venv\Scripts\Activate.ps1     # PowerShell
python -m pip install -r chapter-24-python-cpp-integration/examples/faststats-cpp/requirements-dev.lock
python -B chapter-24-python-cpp-integration/tools/preflight.py
```

Preflight rapporterar interpreter, arkitektur, aktiv miljö, compiler, CMake, pip, pybind11, scikit-build-core, build, pytest och mypy. Laga lagret som saknas; ett loader-knep lagar ingen saknad compiler.

Plattformssteg hålls isär från verifiering: Ubuntu/Debian använder paketet `build-essential`; macOS använder Apple Command Line Tools via `xcode-select --install`; Windows använder Visual Studio Build Tools med **Desktop development with C++** och Developer PowerShell. De kan kräva nät/behörighet. `requirements-dev.lock` registrerar exakta direkta verktygsversioner för den verifierade värden men saknar transitivt graf och hashar och är inget hermetiskt plattformsöverskridande lock. Installera den bara i venv, använd `constraints-build.txt` för isolerad build, kör preflight igen och påstå stöd endast där du faktiskt körde.

Godkända PEP 517-byggen sätter `PIP_BUILD_CONSTRAINT` till `constraints-build.txt`, så isoleringen använder pybind11 3.0.4 och scikit-build-core 1.0.3. Det är inte samma som runtime-constraints.

### Diagnostisera fasen, inte symptomet

| Observation | Fas | Första fråga | Reversibel åtgärd |
|---|---|---|---|
| syntax eller okänd typ | compile | syns declaration/header? | läs första diagnostiken |
| unresolved symbol | link | länkades objekt/bibliotek? | granska target sources |
| modul finns men import misslyckas | load | matchar taggar/dependencies? | prova wheel från annat cwd |
| Python `TypeError` | binding/API | följde värdet kontraktet? | minska till ett giltigt/ogiltigt anrop |

## Grundväg: första C++-programmet

### Pass 1 — värden, funktioner, scope och diagnostik

Förutsäg vem som förstör vektorn i `ScoreReport report(std::vector<double>{6,8,10})`. `ScoreReport` gör det: medlemmen frigörs när objektet lämnar scope. Det är RAII; ingen manuell `free()` behövs.

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

Happy path: `practice batch: mean=8`. Edge case: tom vektor kastar `std::invalid_argument`, fångad i `main()`. Återställningsbart fel: kompilera `expected_compile_error.cpp` separat och läs första diagnostiken; CMake inkluderar inte filen.

**TODO:** byt poängen och förutsäg medelvärdet. **Ledtråd:** behåll `const`. **Lösning:** `mean += (value - mean) / count` uppdaterar en ägd `double`; ännu behövs varken Python eller manuell minneshantering.

Vanligt misstag: implementationen saknar namespace. Läs första felet, kontrollera kvalificerat namn och bygg bara om temporärkatalogen.

### Pass 2 — headers, referenser, vektorer, klasser och exceptions

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/00-cpp-survival/include/score.hpp check=cpp:contract -->
```cpp source-ref
class ScoreReport {
public:
    explicit ScoreReport(std::vector<double> values);
    [[nodiscard]] double mean() const;
    [[nodiscard]] const std::string& label() const noexcept;
};
```

Headern deklarerar; source definierar. Slutligt `const` lovar ingen mutation. `const std::string&` lånar medlemmen utan kopia medan report lever. `explicit` hindrar överraskande implicit konstruktion. Ett återställningsbart exception fångas vid en tydlig gräns och lämnar aldrig destructor.

Kontroll: förklara owner och lifetime för label-referensen innan du fortsätter.

**Mikrocykel:** förutsäg skillnaden med en kopierad retur, kör happy-testet och TODO returnera värde. Ledtråd: jämför signatures; tom konstruktion är återställningsbar edge. Lösningen väger kopia mot lifetime-beroende. Reflektera över vilket kontrakt som är lättast att underhålla.

### Pass 3 — compiler, linker och loader

Source→objekt är compile; objekt→program/bibliotek är link; import aktiverar loader. Klassificera ett fel i varje fas.

**TODO:** ta tillfälligt bort `src/score.cpp` ur target. **Ledtråd:** deklarationen syns. **Lösning:** compile går igenom, link hittar inte definitionerna. Återställ filen.

Verifiera återställt bygge och edge utan definition. Reflektera: första diagnostiken visar den tidigaste trasiga fasen; senare fel är ofta följder.

### Pass 4 — första pybind11-extension

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/01-first-extension/src/bindings.cpp check=cpp:contract -->
```cpp source-ref
PYBIND11_MODULE(hello_cpp, module) {
    module.def("add", &add, py::arg("left"), py::arg("right"));
}
```

Makrot definierar loader-ingången; CMake bygger, scikit-build-core kopplar PEP 517 och wheel levererar. Installera temporärt och importera från annat cwd.

Förutsäg `hello_cpp.add("20",22)`: `TypeError`, ingen textkonvertering. Byt plus mot minus, se testet misslyckas, återställ och bygg om. Då är grundvägen klar.

## Professionell väg: frys kontraktet före optimering

### Pass 5 — Python-orakel och exakt domän

`_reference.py` är läsbar semantik, inte tyst fallback. `summarize` tar 1–1 000 000 exakta built-in `int`/`float`; inte `bool`, subclasses, `Fraction`, `Decimal`, NumPy scalar eller `__float__`. Heltal `abs(x)<=2**53`, finita värden `abs(x)<=1e150`, threshold finit `[0,1e150]`.

Medelvärde i inputordning via `mean += (value - mean) / count`; andra passet jämför med slutligt medel. Delta räknas om större än threshold och inte `isclose` vid `1e-12`. `[-3,-3,-1]`, `0.5` ger tre anomalies; likhet räknas inte.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/python/faststats_cpp/_reference.py check=cpp:contract -->
```python source-ref
expected = summarize([-3, -3, -1], threshold=0.5)
assert expected.anomaly_count == 3
```

Happy: exakta ints/floats. Edge: ett värde och konstant batch. Fel: tomt, icke-finit, range, exakt typ, threshold. Floatparitet använder rel/abs `1e-12`.

**TODO:** lägg till ett boundary-fall i referens/native-tests. **Ledtråd:** ändra en begränsning åt gången. Lösning: kontrollera exception-klass och oförändrat state. Reflektera varför ett exakt kontrakt slår “tar tal”.

### Pass 6 — kärna, binding, fasad och typing

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/cpp/include/faststats_cpp/core.hpp check=cpp:contract -->
```cpp source-ref
[[nodiscard]] Summary summarize(const double* values, std::size_t size,
                                double threshold);
void normalize_in_place(double* values, std::size_t size);
```

CTest provar kärnan utan Python. `bindings.cpp` validerar Python-typer/buffers. `_native` är privat; `__init__.py`, `_native.pyi`, `py.typed` ger fasad och typer. Fasaden skiljer “inte byggd” från trasig binary och döljer aldrig felet med oraklet.

**Mikrocykel:** förutsäg vilket lager som känner en ogiltig Python-typ, kör CTest/pytest och TODO ändra default endast i stubben. Ledtråd: typing/stubtest ska hitta felet. Återställ default och reflektera över tunna bindings.

### Pass 7 — klasser och transaktionella fel

`OnlineStats.add/extend/reset` visar count/min/max/mean; tomt `(0,None,None,None)`, max en miljon. `extend` validerar först: efter `[1,2]` lämnar `[3,inf]` exakt `(2,1,2,1.5)`.

Domänfelet blir `FaststatsError`; typ/range/layout blir `TypeError`/`ValueError`. Callback-fel återvänder efter RAII-cleanup. Inget exception korsar `main()`, destructor eller `noexcept`.

**TODO:** extend giltiga värden och lägg sist ett ogiltigt; jämför state. Ledtråd: validera i temporär storage. Happy: commit; edge: tom extend; fel: full rollback. Reflektera om ett partiellt anrop kan återförsökas.

### Pass 8 — ownership, policies och smart holders

| Gräns | Owner | Lånets längd | Evidens |
|---|---|---|---|
| returnerad `Summary` | Python-wrapper | inget | read-only properties |
| `Dataset.metadata` | parent `Dataset` | child-reference | `reference_internal` |
| `BorrowingView` | caller/keep-alive | view lifetime | `keep_alive<1,2>` |
| `TrackedResource` | unik smart holder | kan överföras | räknare går till baslinje |

`py::smart_holder` gör smart pointers/trampolines tydliga men rättfärdigar inte raw owner. `ObserverRunner` håller Python-derived observer och destructor anropar inte Python.

**TODO:** rita owners. **Ledtråd:** pilen börjar hos den som förstör. **Lösning:** `reference_internal` binder child/parent; `keep_alive` patient/nurse; `consume_resource` flyttar ownership och frigör en gång.

Professionell kontroll: Debug/Release och förklaring av domän, fel och owner.

## Avancerad väg: buffers, GIL, mätning och wheels

### Pass 9 — kopierade iterables och lånade buffers

`summarize` kopierar till `std::vector`: bekvämt men kostar. `summarize_buffer` lånar 1D native-`double`, aligned, contiguous, positiv stride. `normalize_in_place` kräver writable.

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/faststats-cpp/tests/test_buffers.py check=cpp:contract -->
```python source-ref
values = array("d", [2.0, 4.0, 6.0])
faststats_cpp.normalize_in_place(values)
assert values.tolist() == [0.0, 0.5, 1.0]
```

Båda håller GIL, förbjuder samtidig mutation och sparar ingen pointer. All validering sker före mutation: NaN, tom, stor, read-only, strided, multidimensionell, fel format/alignment lämnar ingen deländring. Konstanta värden→`0.0`. NumPy är valfritt; `array('d')`/`memoryview` räcker.

**TODO:** prova read-only och strided `memoryview`. **Ledtråd:** format, dimension, stride, writable före läsning. Happy: contiguous; edge: konstant; återställningsbart fel: layout. Reflektera när kopia är säkrare än zero-copy.

### Pass 10 — callbacks, GIL och deterministisk concurrency

`summarize_many` validerar/kopierar med GIL, släpper bara runt kärnan på ägd storage och återtar före resultat/fel. Buffers och callbacks går inte in där.

Testtarget `_faststats_test` med `FASTSTATS_TEST_HOOKS` använder mutex/condition-variable: två anrop måste vara inne samtidigt. Seriell/GIL-hållen version misslyckas; wheel har ingen hook.

Vanligt fel: släpp GIL runt `py::object`. Rätt: validera/konvertera → äg → släpp → ren C++ → återta → Python.

**TODO:** ta bort `gil_scoped_release` bara i testtarget. **Ledtråd:** båda threads kan inte nå rendezvous. Återställ efter bounded timeout; happy visar samtidig native-entry. Reflektera varför sleep bevisar mindre.

### Pass 11 — ärliga benchmarks

Benchmark verifierar paritet, warm-up, upprepningar, median, kontext och storlekar 1, 10, 1 000, 100 000. Små native-anrop kan förlora; det är evidens.

```console illustrative
python chapter-24-python-cpp-integration/examples/faststats-cpp/benchmarks/benchmark.py --profile release --repeats 7
```

**TODO:** förutsäg crossover. **Ledtråd:** batching. **Lösning:** behåll Python för litet/delegerat arbete; välj C++ efter korrekthet och representativ mätning.

### Pass 12 — sdist, wheel, taggar och ren installation

`verify_artifacts.py` bygger/inspekterar sdist, bygger wheel från den och installerar i ren venv/cwd. Den kör `pip check`, smoke, `mypy.stubtest`, strikt consumer, negativa typkontroller för tre endast-nativa konstruktorer och kontrollerar att hook saknas. På stödda värdar misslyckas den om `ldd` rapporterar `not found`.

Taggar kodar Python/ABI/plattform, inte compiler/C++ ABI/shared libs; dessa granskas separat. Byt aldrig namn till `abi3`: Limited API, CPython ABI, C++ ABI och plattform är olika löften.

Kontroll: varför är source-import svagare än sdist→wheel→ren venv?

**TODO:** läs wheel-namnet och lista vad det inte lovar. **Ledtråd:** taggar kontra compiler/C++ ABI/shared libs. Happy: clean install; edge: annan interpreter; loader-fel syns. Reflektera innan ordet portable används.

## Hero-väg: debugging, embedding och gränser

### Pass 13 — Debug, warnings och sanitizers

Debug sparar symboler; Release distribueras. Höga warnings är errors. GCC/Clang med `FASTSTATS_ENABLE_SANITIZERS=ON` ger ASan/UBSan endast till den fristående kärnan; andra toolchains skippar med förklaring.

Framkalla inte segfault i Python. Använd owner-diagram, räknare, C++-tests och sanitizer i reversibel temporär build.

**TODO:** kör sanitiserad kärna och hitta flaggorna. **Ledtråd:** endast autonoma targets. CMake skriver kapacitetsevidens; bara `enabled:<compiler>` får rapportera framgång och en compiler utan stöd ger en uttrycklig skip. En rapport startar en återställningsbar utredning. Reflektera över minsta säkra reproducer.

### Pass 14 — bädda in betrodd strategi

<!-- bookcheck: path=chapter-24-python-cpp-integration/examples/embed-python/src/main.cpp check=cpp:contract -->
```cpp source-ref
py::scoped_interpreter interpreter;
py::module_ strategy = py::module_::import("trusted_strategy");
py::object result = strategy.attr("evaluate")(values);
```

Värden kräver `--strategy-dir`, canonicaliserar, ersätter `sys.path`, importerar fast namn, skickar typad lista och kräver exakt float. Missing/raise/invalid ger non-zero exit. En lockmodul i cwd får inte vinna.

Handles dör före interpreter; `main()` fångar fel. Ingen eval eller obetrodd modul: inbäddad Python har värdprocessens behörighet.

**TODO:** kör good, raising och invalid från decoy-cwd. **Ledtråd:** fast modul kommer från canonical katalog. Happy: success; edges: callable/result; Python-fel: non-zero exit. Reflektera hur `eval` ändrar hotmodellen.

### Pass 15 — free-threading och subinterpreters är framtida audits

Modulen använder inte `mod_gil_not_used()` och lovar inget stöd. Granska globals, allocators, holders, callbacks, locks, init, interpreter-local data, teardown och verklig matris. En tagg är inte evidens.

Cython, nanobind, SWIG, `ctypes` och C API är alternativ, inte parallella vägar. GPU, SIMD, OpenMP, cross-compilation, mobil/WASM, publicering och stort externt bibliotek ingår inte.

**TODO:** skriv en supportmatris utan kodändring. **Ledtråd:** runtime, interpreter-antal, callbacks, globals och teardown. Happy: testad GIL-build; edges: free-threaded/subinterpreters. Lösning: ny evidensbaserad change, inte tagg. Reflektera över kostnaden för löften.

## Verifiera capstone

Kör från repots rot. Verifieraren skapar venv, byggen och wheels i tillfälliga kataloger och kan behöva nätverksåtkomst för den första installationen av direkt pinnade verktyg.

```console illustrative
python -B chapter-24-python-cpp-integration/tools/verify_all.py
python -B tools/validate_book.py --plugin chapter-24-python-cpp-integration/tools/bookcheck_plugin.py
```

Det täcker survival, första extension, CTest, Debug/Release pytest, concurrency, kompatibel sanitizer, sdist→wheel, typing, dependencies och embedding. En explicit scan ska hitta noll venv/build/dist/archive/library/object/cache i kapitlet, även ignorerade.

## Övningar, ledtrådar och förklarade lösningar

1. **Grund:** lägg till `range()` i `ScoreReport`; förutsäg negativa tal. Ledtråd: min/max i ett pass. Lösning: ownership i klassen och tomkontroll före index.
2. **Professionell:** lägg read-only `variance` först i oraklet. Ledtråd: frys semantik. Lösning: referens→kärna→binding→stub→CTest→pytest→docs.
3. **Avancerad:** jämför iterable/buffer för 100 000 doubles. Ledtråd: paritet före timing. Lösning: tillskriv conversion/copy/boundary rätt kostnad.
4. **Hero:** föreslå free-threading utan implementation. Ledtråd: globals och Python-åtkomst. Lösning: matris/tests före kompatibilitetslöfte.

## Självbedömningsmatris

| Område | Redo | Behöver repetition | Evidens |
|---|---|---|---|
| Korrekthet/API | kontrakt och transaktioner matchar | verkar bara rimligt | CTest och pytest-paritet |
| Ownership/säkerhet | kan förklara owner/lån/GIL | gissar policies | lifetime, buffer, callback, rendezvous |
| Verifiering | Debug/Release/artefakter temporärt | importerar vid source | loggar och ren venv |
| Omdöme | mäter och anger gränser | lovar universell fart | benchmark och ABI-audit |

Reflektion: vilken gräns litar du minst på och vilken evidens behövs? Om svaret bara är “den kompilerar”, lägg till ogiltig input, lifetime- eller packaging-scenario.

## Källor och attribution

Text och övningar är original. Referenser: [Python extending and embedding](https://docs.python.org/3/extending/index.html), [pybind11 build systems](https://pybind11.readthedocs.io/en/stable/compiling.html), [call policies](https://pybind11.readthedocs.io/en/stable/advanced/functions.html), [smart holders](https://pybind11.readthedocs.io/en/stable/advanced/smart_ptrs.html), [scikit-build-core](https://scikit-build-core.readthedocs.io/en/stable/guide/getting_started.html) och [CMake FindPython](https://cmake.org/cmake/help/latest/module/FindPython.html).
