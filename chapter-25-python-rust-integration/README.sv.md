# Kapitel 25 · Python och Rust: från första crate till verifierad wheel

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

Kapitlet kräver inga tidigare Rust-kunskaper. Du bygger först ett litet program och en statistikdomän i ren Rust. Först därefter korsar du gränsen till Python med PyO3. Resultatet är `faststats_rs`: ett typat blandpaket med deterministiska tester, begränsat parallellt arbete, sdist, versionsspecifik wheel och `abi3-py311`-wheel.

Alla exempel är egna companion-källor under [`examples/`](examples/). Den fullständiga verifieraren skriver byggen och miljöer i temporära kataloger; ingenting publiceras och inga autentiseringsuppgifter används.

## Lärandemål och förkunskaper

Efter kapitlet kan du:

- förklara crate, kompilator, extension module, application binary interface (ABI), sdist och wheel;
- läsa variabler, structs, `Vec<T>`, slices, ownership, borrowing, `Option` och `Result`;
- hålla Rust-domänen oberoende av PyO3 och översätta återhämtningsbara fel till Python-undantag;
- förklara vad som kopieras, flyttas, lånas eller referensräknas vid gränsen;
- fastställa ett exakt, begränsat numeriskt kontrakt före optimering;
- använda `Python::detach` endast med Rust-ägda data och inte förväxla det med free-threaded-stöd;
- testa Rust, Python, typing, samtidighet, sdist, wheels och rena importer;
- tolka benchmarks utan löftet att Rust alltid är snabbare.

Du behöver [undantag](../chapter-14-exceptions/README.sv.md), [moduler](../chapter-15-modulos/README.sv.md), [miljöer](../chapter-16-entornos/README.sv.md), [testning](../chapter-18-testing/README.sv.md), [loggning](../chapter-20-logging/README.sv.md) och [introspektion](../chapter-22-introspection/README.sv.md). Kapitel 23 och 24 är inte förkunskaper.

Du behöver CPython 3.11+, Internet för första installationen av toolchain/crates, plattformens linker och cirka 16 pass på 45–60 minuter. Implementationen verifierades på Linux x86-64, CPython 3.13.11, Rust 1.97.0, PyO3 0.29.0 och maturin 1.14.1. Andra plattformar är instruktioner att validera, inte påstått stöd.

## Karta över vägarna

| Väg | Tid | Synligt resultat | Kontroll |
|---|---:|---|---|
| Förberedelse | 1–2 pass | Toolchain-rapport och första Rust-test | `cargo test --locked` |
| Grundläggande Rust | 4 pass | Python-oberoende domän | fmt, clippy och tester |
| Integration | 3 pass | Python importerar privat PyO3-extension | wheel installerad utanför source |
| Professionell | 3–4 pass | Klasser, fel, typing och paritet | pytest, stubtest, mypy strict |
| Hero | 3–4 pass | Detached-arbete och två granskade wheels | rendezvous, sdist, rena installationer |

Du kan stanna efter varje checkpoint. Hero krävs inte för grundvägen.

## 1. Varför korsa språkgränsen?

Python är oftast den bästa starten. Rust lägger till kompilator, plattformsverktyg, packaging och en andra minnesmodell. Kostnaden är rimlig först när korrektheten är fast och mätning visar en användbar gräns.

Projektet sammanfattar upp till en miljon mätvärden. Python äger den publika upplevelsen; Rust får en avsiktligt smal domän. En ren Python-referens hindrar ett snabbt men felaktigt svar från att godkännas.

**Förutsäg:** vad är troligen snabbast, ett native-anrop med 100 000 värden eller 100 000 anrop med ett värde? Det senare betalar gränskostnaden om och om igen. Vi mäter.

**Checkpoint:** ange när Python bör behållas: tillräcklig fart, för små anrop, befintligt bibliotek eller större underhållskostnad än uppmätt nytta.

## 2. Förberedelse: diagnostisera före bygge

Installera Rust via `rustup` och maturin som publicerat Python-verktyg, inte med `cargo install maturin` på grundvägen. Linux behöver linker/build essentials, macOS Xcode command-line tools och Windows normalt MSVC Build Tools som matchar 64-bitars Python.

| System | Native-krav | Första diagnostik |
|---|---|---|
| Linux | distributionens C-verktyg/linker | `cc --version` |
| macOS | Xcode command-line tools | `xcode-select -p` |
| Windows | matchande MSVC Build Tools | använd Developer shell |

Pins ersätter det instabila ordet ”latest”:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# Aktivera .venv med kommandot för ditt shell.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

Installationen kan behöva Internet. Preflight kontrollerar i ordning Python/venv, rustup/toolchain, Cargo/target, linker och maturin. En saknad linker är inte ett PyO3-fel; en inaktiv venv är inte ett Rust-fel.

Återhämtningsbara setup-fel:

- `rustup` saknas: använd officiella installeraren, starta om shell och kontrollera versionen;
- Rust 1.96 syns: kör `rustup run 1.97.0 rustc --version`, sänk inte kravet;
- maturin hittar ingen venv: aktivera den eller bygg en wheel;
- import fungerar bara i source-katalogen: byt till temporär cwd och kontrollera `module.__file__`.

**TODO:** spara preflights JSON-rapport. **Ledtråd:** `python -B tools/preflight.py --json` är skrivskyddad.

## 3. Första Rust-programmet: värden, funktioner och tester

En crate är Rusts paket/kompileringsenhet. `Cargo.toml` är manifestet. Edition 2024 väljer idiom och `rust-version = "1.97.0"` låser den verifierade kompilatorn.

```bash illustrative
cd examples/00-rust-survival
cargo check --locked
cargo run --locked
cargo test --locked
```

Meningsfull utdata:

```text illustrative
workshop mean: 19.0
```

Biblioteket introducerar struct, lånad slice, `Option`, enum, `Result` och `?` med ett begränsat sensorvärde.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/src/lib.rs" check="rust:contract" -->
```rust source-ref
pub fn average(values: &[f64]) -> Option<f64> { /* testad källa */ }
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> { /* ... */ }
```

`Option` säger att medelvärdet kan saknas för en tom slice. `Result` beskriver kända återhämtningsbara fel utan magiska sentinelvärden.

**Ändra:** testa `"lab:NaN"`. **Ledtråd:** syntaxparsningen lyckas, sedan avvisar `is_finite()` värdet. Lösningen använder `NonFiniteNumber`: talform räcker inte för domänen.

## 4. Ownership och borrowing: kompilatorn ger återkoppling

Varje Rust-värde har en owner. Tilldelning kan flytta värdet. Ett lån `&T` ger tillfällig läsning; `&mut T` ger exklusiv muterbar åtkomst.

Förutsäg raden som misslyckas:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_move_error.rs" check="rust:contract" -->
```rust source-ref
let label = String::from("sensor-a");
let moved_label = label;
println!("{moved_label}");
println!("{label}"); // E0382: användning efter move
```

Kompilatorn kan föreslå `.clone()`, men fråga först vem som ska äga värdet efter anropet. Här räcker ett lån:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_borrow_solution.rs" check="rust:contract" -->
```rust source-ref
fn print_label(label: &str) { println!("{label}"); }
// Anroparen behåller String och lånar ut &str två gånger.
```

Vanligt misstag: klona tills compiler tystnar. Clone kräver en medveten kostnad och avsiktligt dubbelt ägande.

**Självkontroll:** i `average(values: &[f64])` äger anroparen samlingen; funktionen lånar slicen under anropet och lånet kan inte leva längre än datan.

## 5. Ren Rust-domän före PyO3

Domänen får redan konverterade `f64` och känner inte Python eller Global Interpreter Lock (GIL). Därför kan `cargo test` isolera numerisk semantik.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/domain.rs" check="rust:contract" -->
```rust source-ref
pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
pub fn summarize(values: &[f64], threshold: f64)
    -> Result<SummaryData, DomainError> { /* testad implementation */ }
```

Exakt ordning: validera; uppdatera mean i inputordning med `mean += (value - mean) / count`; andra passet använder slutligt mean; räkna endast delta som är större och utanför toleransbandet `1e-12`.

För `[-3,-3,-1]` och threshold `0.5` är mean `-7/3` och alla tre är anomalier. Streaming-klassificering skulle ge annat resultat.

`OnlineStatsData.extend` ändrar en klon och committar först efter validering. Fel bevarar hela tidigare tillståndet.

**TODO:** test för negativ threshold. **Förklarad lösning:** förvänta `DomainError::InvalidThreshold`; tyst clamp ändrar anroparens begäran.

## 6. Första PyO3-extension

`#[pyfunction]` exponerar funktioner och `#[pymodule]` initierar modulen. Basmodulen anger `gil_used = true` så att den inte råkar påstå otestad free-threaded-kompatibilitet.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/01-first-extension/src/lib.rs" check="rust:contract" -->
```rust source-ref
#[pyfunction]
fn double(value: i64) -> PyResult<i64> { /* kontrollerad multiplikation */ }

#[pymodule(gil_used = true)]
fn first_pyo3_extension(module: &Bound<'_, PyModule>) -> PyResult<()> { /* ... */ }
```

```bash illustrative
cd examples/01-first-extension
maturin develop --locked
python -c "import first_pyo3_extension as m; print(m.double(21))"
```

Observera:

```text illustrative
42
```

Overflow blir `ValueError`; fel typ blir `TypeError`. Lägg inte till den historiska deprecierade `pyo3/extension-module`-featuren: maturin-rutten behöver den inte.

## 7. Blandpaket: privat native, publik fasad

`faststats_rs._native` är den kompilerade detaljen; `faststats_rs` är den publika typade API:n. `python-source` och `module-name` kopplar lagren. Craten producerar `cdylib` och `rlib`.

`_reference.py` är oracle, inte tyst fallback. Saknad `_native` diagnostiseras som obyggd; ett internt binärfel behåller sitt ursprungliga undantag.

**Förutsäg:** test från en främmande cwd förhindrar att `sys.path` döljer filer som saknas i wheel.

**Checkpoint:** caller → fasad → `_native` → extraktion → ägd `Vec<f64>` → domän → klass eller undantag.

## 8. Exakta typer och PyO3-lifetimes

Endast exakt built-in `int`/`float` accepteras. `bool`, `Fraction`, `Decimal`, subclasses, NumPy scalars och `__float__` avvisas. Heltal: `abs<=2**53`; floats: finita och `abs<=1e150`.

Sekvensen konverteras/kopieras till `Vec<f64>` före detached-beräkning; det är inte zero-copy.

- `Python<'py>` bevisar att tråden är attached;
- `Bound<'py,T>` är bundet till attachment;
- `Py<T>` äger reference count men behöver korrekt attachment för åtkomst.

Inget Python-lån går in i `domain.rs` eller överlever detach. `describe_payload` testar Unicode, bytes och optionals.

**Optional preview:** NumPy/Arrow/buffers kräver kontrakt för layout, lifetime, aliasing och mutation; de ligger utanför capstone.

## 9. Det exakta `faststats_rs`-kontraktet

`summarize(samples, *, threshold)` accepterar 1–1 000 000 element och returnerar frozen `Summary` med count/minimum/maximum/mean/anomaly_count/anomaly_ratio.

- ogiltig domän/storlek/intervall/finitet/threshold → `ValueError`;
- avvisad typ → `TypeError`;
- likhet eller närhet `1e-12` till threshold → ingen anomali;
- heltalsfält exakt, floats jämförs med tolerans `1e-12`.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """Companion-testet jämför referens och native."""
```

**Övning:** förutsäg `[True]`, `[2**53+1]`, `[nan]`. **Lösning:** `True` ger `TypeError`; de andra har accepterad typ men ogiltigt värde och ger `ValueError`.

## 10. Pythoniska klasser och transaktionellt tillstånd

Frozen `Summary` är skrivskyddad. `OnlineStats` har `add`, `extend`, `reset` och properties; empty/reset är `0/None/None/None`. Totalt maximum är en miljon.

Metoderna är alltid attached/GIL-held och detachar aldrig. Klassen är inte en primitive för samtidig mutation. `extend([4,bad,5])` konverterar och validerar före commit; ingenting ändras vid fel.

Vanligt misstag: öka count under extraktion. Ett fel mitt i skulle ge delvis tillstånd; därför förbereder designen och committar sist.

## 11. Fel och panic-gräns

Förväntade fel går via `Result<T,DomainError>` och `TypeError`/`ValueError`. PyO3-operationer använder `PyResult` och `?` utan att tappa aktivt undantag.

Inga `unwrap`/`expect` används på extern input. Survival-programmets två `expect` skyddar demonstrerade literala invariants. Panic är inte normal validering och körs inte avsiktligt i tolken eller genom manuell FFI.

Om `PanicException` syns: reproducera i subprocess, kontrollera invariant och gör förväntat fel till `Result`; använd inte panic som business logic.

## 12. Tester i två språk och typing

- fmt: format; clippy `-D warnings`: misstänkta Rust-mönster;
- Cargo tests: domän utan Python;
- pytest: fasad, paritet, fel, klasser, trådar och riktigt native-import;
- stubtest: installerad runtime mot stubs;
- mypy strict: konsumentens typer.

Manuell `_native.pyi` och `py.typed` är stabila. PyO3:s experimentella introspection är valfri. Tester stänger av cache och anger risken; coverage-procent ersätter inte beteende.

## 13. `Python::detach` och deterministisk samtidighet

Extraktionen sker attached och flyttar ägda data till closure:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

Inuti finns ingen `Python`, `Bound`, callback eller lånad Python-data. Klass/undantag skapas efteråt, attached.

En timeout bevisar inte parallell entry. Acceptance-bygget `test-hooks` använder `Mutex`/`Condvar`: två closures måste gå in innan någon fortsätter. Featuren är av som standard, `src/test_hooks.rs` saknas i sdist och release-wheels exponerar ingen API/symbol.

Basmodulen behåller `gil_used=true`. Att släppa GIL i en region är inte en full free-threaded-audit.

## 14. Ärlig benchmark: gräns, kopia och batching

Först verifieras likhet; sedan release-profile, warm-up, repetitioner, median och flera storlekar. Kopian till `Vec` ingår.

```bash illustrative
python benchmarks/benchmark.py
```

Små inputs kan förlora på overhead. Batcha eller behåll Python. Inget minsta speedup krävs.

**TODO:** lägg till `n=100`. **Ledtråd:** jämför medianer och dokumentera kontext/brus, utan att generalisera en maskin.

## 15. Distribution: sdist och två wheels

Sdist innehåller metadata, licens, README, fasad/stubs, Rust-source, Cargo/locks och toolchain; den utesluter targets, caches, binärer och rendezvous. Båda wheels byggs från uppackad sdist.

Versionsspecifik wheel visar Python/ABI/plattform, till exempel `cp313-cp313-manylinux_..._x86_64`. Det lovar inte andra targets.

Featuren `abi3-py311` producerar `cp311-abi3-<platform>` för kompatibel GIL-baserad CPython från 3.11, men begränsas fortfarande av OS/arkitektur/API. `abi3t` kräver Python 3.15+ och separat free-threaded-audit; basen gör inget sådant claim.

## 16. Verifiering med ett kommando

Från kapitlet:

```bash illustrative
python -B examples/faststats-rs/tools/verify.py
```

Den använder temporära targets, wheels, venvs och cwd och kör pins, fmt/clippy/Cargo, move-felet och lösningen, första extension, hook-wheel, sdist, båda release-wheels, pytest, typing, benchmark, import/tag/content och hygiene.

Bokens gate anropar Rust-adaptern:

```bash illustrative
python -B ../tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

Pluginen äger bara Rust/Cargo/PyO3/source refs; root äger Markdown, språkval, länkar, RTL, tillgänglighet, klassificering och hygiene.

## 17. Guidade ändringar

### Övning A: heltalsgräns

Lägg till `-(2**53)` och `-(2**53)-1`. Ledtråd: den första godkänns och den andra ger `ValueError`. Klart när referens/native stämmer.

### Övning B: transaktion

Börja med `[1,2]`, försök `[3,inf,4]`. Spara fyra properties, kontrollera undantag och oförändrad snapshot. `tests/test_classes.py` visar den förklarade lösningen.

### Övning C: välj bort Rust

Mät en Python-workload, undersök batching och bygg/release/underhåll. ”Behåll Python” är korrekt när evidensen stödjer det.

## 18. Vanliga fel per lager

- Compiler: hitta move/borrow/scope före clone.
- Cargo: uppdatera lock avsiktligt och kör hela suite.
- Linker: installera build tools; Python-kod löser inte detta.
- maturin: aktivera venv eller bygg wheel.
- Import: främmande cwd och `module.__file__`.
- Extraction: kontrollera exakt typ.
- GIL: ägd data före detach, Python-resultat efteråt.
- Packaging: bygg alltid om från sdist.
- Performance: likhet, warm-up, repetitioner och kontext.

Fel är evidens från ett lager, inte ett omdöme om eleven. Diagnostisera lägsta felande lager först.

## 19. Checkpoints och bedömningsmatris

Förberedelse: toolchain och återhämtning. Grund: owner/borrow/Result. Integration: call path. Professionell: paritet/transaktion/typing/import. Hero: detach/rendezvous/benchmark/tags.

Poäng 0–2: korrekthet, idiomatisk ownership, säker gräns, API, återhämtning, Rust/Python-tester, deterministisk samtidighet, ärlig mätning, packaging/typing och förklaring. Komplett capstone: ingen nolla och minst 16/20.

## 20. Ordlista och reflektion

- **crate:** Rust-enhet; **ownership:** ansvar för frigörande; **borrow:** tillfällig åtkomst.
- **PyO3:** CPython-bindings/macron; **GIL:** lås i vanlig CPython.
- **ABI:** binär överenskommelse; **sdist:** källarkiv; **wheel:** byggd distribution; **abi3:** stabil ABI med minsta Python och plattform.

Reflektera: var är den smalaste nyttiga native-gränsen? Vad ändras med muterbar NumPy-buffer eller globala Python-handles? Om du inte kan namnge owner, lifetime, fel, test och kompatibilitet är gränsen inte klar.

## Verifierade referenser

- [Officiell Rust-installation](https://rust-lang.org/tools/install/)
- [The Rust Book om ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [The Rust Book om fel](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [PyO3 0.29-guiden](https://pyo3.rs/v0.29.0/)
- [PyO3-parallellism och `Python::detach`](https://pyo3.rs/main/parallelism)
- [maturins mixed-layout](https://www.maturin.rs/project_layout.html)
- [maturin bindings och stabil ABI](https://www.maturin.rs/bindings.html)

Versionskänsligt material kontrollerades 2026-07-13 och är pinnat i assets. Kör hela verifieraren innan en pin ändras.
