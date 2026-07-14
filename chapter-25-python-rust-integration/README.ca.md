# Capítol 25 · Python i Rust: del primer crate a un wheel verificat

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

Aquest capítol parteix de zero coneixements de Rust. Primer construiràs un programa i un domini d'estadístiques en Rust pur; només després creuaràs la frontera amb Python mitjançant PyO3. El resultat és `faststats_rs`: un paquet mixt tipat amb proves deterministes, treball paral·lel acotat, un sdist, un wheel específic i un wheel `abi3-py311`.

Tots els exemples són fonts originals sota [`examples/`](examples/). El verificador complet escriu compilacions i entorns en directoris temporals; no publica res ni utilitza credencials.

## Objectius i prerequisits

En acabar podràs:

- explicar crate, compilador, mòdul d'extensió, interfície binària d'aplicació (ABI), sdist i wheel;
- llegir variables, structs, `Vec<T>`, slices, ownership, borrowing, `Option` i `Result`;
- separar el domini Rust de PyO3 i convertir errors recuperables en excepcions Python;
- explicar què es copia, mou, presta o compta per referències a la frontera;
- fixar un contracte numèric exacte i acotat abans d'optimitzar;
- usar `Python::detach` només amb dades pròpies de Rust sense confondre-ho amb suport free-threaded;
- provar Rust, Python, typing, concurrència, sdist, wheels i imports nets;
- interpretar benchmarks sense prometre que Rust sempre guanya.

Necessites [excepcions](../chapter-14-exceptions/README.ca.md), [mòduls](../chapter-15-modulos/README.ca.md), [entorns](../chapter-16-entornos/README.ca.md), [testing](../chapter-18-testing/README.ca.md), [logging](../chapter-20-logging/README.ca.md) i [introspecció](../chapter-22-introspection/README.ca.md). Els capítols 23 i 24 no són prerequisits.

Cal CPython 3.11+, Internet per a la instal·lació inicial del toolchain/crates, linker de plataforma i unes 16 sessions de 45–60 minuts. Aquesta implementació es va verificar en Linux x86-64, CPython 3.13.11, Rust 1.97.0, PyO3 0.29.0 i maturin 1.14.1. Altres sistemes són instruccions per validar, no suport afirmat.

## Mapa de rutes

| Ruta | Temps | Resultat observable | Criteri |
|---|---:|---|---|
| Preparació | 1–2 sessions | Informe del toolchain i primer test Rust | `cargo test --locked` |
| Rust essencial | 4 sessions | Domini independent de Python | fmt, clippy i tests |
| Integració | 3 sessions | Python importa una extensió PyO3 privada | wheel instal·lat fora del source |
| Professional | 3–4 sessions | Classes, errors, typing i paritat | pytest, stubtest, mypy strict |
| Hero | 3–4 sessions | Treball detached i dos wheels auditats | rendezvous, sdist i installs nets |

Pots aturar-te després de qualsevol checkpoint; Hero no és necessari per completar la ruta essencial.

## 1. Per què creuar la frontera?

Python sol ser el millor inici. Rust afegeix compilador, eines de plataforma, packaging i un altre model de memòria. Aquest cost només es justifica després de fixar la correcció i mesurar una frontera útil.

El projecte resumeix fins a un milió de mostres. Python conserva l'experiència pública; Rust rep un domini estret. Una referència Python impedeix acceptar una resposta ràpida però incorrecta.

**Prediu:** què anirà millor, una crida amb 100.000 valors o 100.000 crides amb un valor? La segona paga la frontera repetidament. Ho mesurarem.

**Checkpoint:** explica quan conservar Python: ja és prou ràpid, les crides són petites, existeix una biblioteca o el cost de manteniment supera el benefici.

## 2. Preparació: diagnostica abans de compilar

Instal·la Rust amb `rustup` i maturin com a eina Python publicada, no amb `cargo install maturin` a la ruta base. Linux necessita linker/build essentials; macOS, command-line tools d'Xcode; Windows, normalment MSVC Build Tools compatibles amb Python de 64 bits.

| Sistema | Prerequisit natiu | Primer diagnòstic |
|---|---|---|
| Linux | eines C/linker de la distribució | `cc --version` |
| macOS | command-line tools d'Xcode | `xcode-select -p` |
| Windows | MSVC Build Tools compatibles | executar `cl` o `clang-cl` des de Developer shell |

Els pins eviten la paraula inestable “latest”:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# Activa .venv amb l'ordre de la teva shell.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

La instal·lació pot usar Internet. `requirements-dev.lock` fixa les dependències Python directes de verificació, però no és un lock transitiu generat per un resolver amb hashes. `Cargo.lock` fixa el graf Rust i `rust-toolchain.toml` selecciona Rust 1.97.0. Preflight revisa per ordre Python/venv, rustup/toolchain, Cargo/target, linker i maturin; a Windows accepta `cl` o `clang-cl`. Un linker absent no és un error de PyO3 i un venv inactiu no és un error de Rust.

### Errors de configuració recuperables

- `rustup` absent: usa l'instal·lador oficial, reinicia la shell i verifica la versió;
- apareix Rust 1.96: executa `rustup run 1.97.0 rustc --version`, sense relaxar el pin;
- maturin no detecta el venv: activa'l o construeix un wheel;
- l'import només funciona des del source: canvia a un cwd temporal i inspecciona `module.__file__`.

**TODO:** executa el preflight i registra Python, arquitectura, target del host, rustc, Cargo i maturin. **Pista:** `python -B tools/preflight.py --json` crea un informe copiable sense modificar el repositori.

## 3. Primer programa Rust: valors, funcions i tests

Un crate és la unitat de paquet/compilació. `Cargo.toml` és el manifest. Edition 2024 selecciona idioms. `rust-version = "1.97.0"` declara l'MSRV; el `rust-toolchain.toml` versionat selecciona exactament 1.97.0 per als exercicis.

```bash illustrative
cd examples/00-rust-survival
cargo check --locked
cargo run --locked
cargo test --locked
```

Sortida significativa:

```text illustrative
workshop mean: 19.0
```

La biblioteca introdueix struct, slice prestat, `Option`, enum, `Result` i `?` amb una lectura de sensor acotada.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/src/lib.rs" check="rust:contract" -->
```rust source-ref
pub fn average(values: &[f64]) -> Option<f64> { /* font provada */ }
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> { /* ... */ }
```

`Option` expressa que la mitjana buida no existeix; `Result` expressa fallades recuperables sense sentinels màgics.

**Modifica:** prova `"lab:NaN"`. **Pista:** el parse sintàctic funciona i després `is_finite()` el rebutja. La solució usa `NonFiniteNumber`: tenir forma numèrica no basta per pertànyer al domini.

## 4. Ownership i borrowing: el compilador dona pistes

Cada valor Rust té owner. Una assignació pot moure'l. Un préstec `&T` permet llegir temporalment; `&mut T` concedeix accés mutable exclusiu.

Prediu la línia errònia:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_move_error.rs" check="rust:contract" -->
```rust source-ref
let label = String::from("sensor-a");
let moved_label = label;
println!("{moved_label}");
println!("{label}"); // E0382: ús després del move
```

Encara que el compilador suggereixi `.clone()`, pregunta qui ha de conservar ownership. Aquí n'hi ha prou amb prestar:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_borrow_solution.rs" check="rust:contract" -->
```rust source-ref
fn print_label(label: &str) { println!("{label}"); }
// El caller conserva String i presta &str dues vegades.
```

Error comú: clonar fins a silenciar el compiler. Un clone necessita una justificació del cost i dos owners deliberats.

**Autoavaluació:** a `average(values: &[f64])`, el caller posseeix la col·lecció, `average` presta un slice durant la crida i el préstec no pot sobreviure a les dades.

## 5. Domini Rust pur abans de PyO3

El domini rep `f64` ja convertits i desconeix Python i el Global Interpreter Lock (GIL). Així `cargo test` aïlla la semàntica numèrica.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/domain.rs" check="rust:contract" -->
```rust source-ref
pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
pub fn summarize(values: &[f64], threshold: f64)
    -> Result<SummaryData, DomainError> { /* implementació provada */ }
```

L'ordre exacte és important:

1. valida el recompte, la finitud, el rang dels valors i el threshold;
2. actualitza `mean += (value - mean) / count` en l'ordre d'entrada;
3. fes una segona passada respecte a la mitjana final;
4. compta un delta només si és superior al threshold i queda fora de la banda de tolerància `1e-12`.

Per `[-3,-3,-1]`, threshold `0.5`, mean és `-7/3` i les tres mostres són anomalies. Una classificació streaming canviaria el resultat.

`OnlineStatsData.extend` modifica un clon i només el confirma després de validar. Una fallada conserva tot l'estat.

**TODO:** afegeix una prova de domini per a un threshold negatiu. **Pista:** crida `validate_threshold` abans de calcular. **Solució explicada:** espera `DomainError::InvalidThreshold`; no facis clamp silenciós perquè canviaria la petició de qui crida.

## 6. Primera extensió PyO3

`#[pyfunction]` exposa funcions i `#[pymodule]` inicialitza. El mòdul declara `gil_used = true` per no anunciar compatibilitat free-threaded no auditada.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/01-first-extension/src/lib.rs" check="rust:contract" -->
```rust source-ref
#[pyfunction]
fn double(value: i64) -> PyResult<i64> { /* multiplicació comprovada */ }

#[pymodule(gil_used = true)]
fn first_pyo3_extension(module: &Bound<'_, PyModule>) -> PyResult<()> { /* ... */ }
```

```bash illustrative
cd examples/01-first-extension
maturin develop --locked
python -c "import first_pyo3_extension as m; print(m.double(21))"
```

Observa:

```text illustrative
42
```

Overflow es converteix en `ValueError`; tipus incorrecte en `TypeError`. No afegeixis la feature històrica deprecada `pyo3/extension-module`: aquesta ruta maturin no la necessita.

## 7. Paquet mixt: natiu privat, façana pública

`faststats_rs` usa dues capes:

- `faststats_rs._native`: detall d'implementació compilat;
- `faststats_rs`: façana Python documentada i superfície de tipus estable.

`pyproject.toml` estableix `python-source = "python"` i `module-name = "faststats_rs._native"`. El crate produeix `cdylib` per a Python i `rlib` per a les proves del costat de Rust.

`_reference.py` és oracle, no fallback silenciós. Un `_native` absent es diagnostica com no construït; una fallada binària interna conserva l'error original.

**Prediu:** provar fora del directori evita que `sys.path` amagui fitxers absents del wheel.

**Checkpoint:** caller → façana → `_native` → extracció → `Vec<f64>` propi → domini → classe o excepció.

## 8. Tipus exactes i lifetimes PyO3

Només s'accepten `int`/`float` built-in exactes. Es rebutgen `bool`, `Fraction`, `Decimal`, subclasses, NumPy scalars i `__float__`. Enters: `abs<=2**53`; floats: finits i `abs<=1e150`.

La seqüència es converteix/copia a `Vec<f64>` abans del còmput detached; no és zero-copy.

- `Python<'py>` prova que el thread està attached;
- `Bound<'py,T>` està lligat a l'attachment;
- `Py<T>` posseeix reference count, però necessita attachment correcta per accedir.

Cap préstec Python entra a `domain.rs` ni escapa a detach. `describe_payload` prova Unicode, bytes i opcionals.

**Optional preview:** NumPy/Arrow/buffers exigeixen layout, lifetime, aliasing i mutació; queden fora.

## 9. Contracte exacte de `faststats_rs`

`summarize(samples, *, threshold)` exigeix entre 1 i 1.000.000 valors. Threshold ha de ser un nombre built-in exacte, finit i dins de `[0, 1e150]`. Retorna `Summary(count, minimum, maximum, mean, anomaly_count, anomaly_ratio)` frozen.

- entrada buida, 1.000.001 elements, valors no finits, fora de rang, enters massa grans o threshold no vàlid → `ValueError`;
- tipus Python rebutjat → `TypeError`;
- un sol valor → ratio `0.0` amb qualsevol threshold no negatiu vàlid;
- igualtat o proximitat al threshold dins de la tolerància `1e-12` → no anomalia;
- els camps enters es comparen exactament; els camps flotants usen `rel_tol=abs_tol=1e-12` a les proves de paritat.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """El test company compara referència i natiu."""
```

**Exercici:** prediu l'excepció per a `[True]`, `[2**53 + 1]` i `[float("nan")]`. **Pista:** la validació de tipus té lloc abans que la validació del rang numèric. **Solució:** `True` produeix `TypeError`; els altres dos són tipus admesos amb valors no vàlids i produeixen `ValueError`.

## 10. Classes Pythonic i estat transaccional

`Summary` frozen només permet lectura. `OnlineStats` té `add`, `extend`, `reset` i propietats; empty/reset és `0/None/None/None`. El màxim total és un milió.

Els mètodes sempre estan attached/GIL-held i mai detachen. No és una primitive de mutació concurrent. `extend([4,bad,5])` converteix i valida abans de confirmar: res canvia si falla.

Error comú: incrementar count durant l'extracció. Un error intermedi deixaria estat parcial; per això es prepara i després es confirma.

## 11. Errors i frontera de panic

Els errors esperats viatgen com `Result<T,DomainError>` i `TypeError`/`ValueError`. Les operacions PyO3 usen `PyResult` i `?` sense perdre l'excepció activa.

No hi ha `unwrap`/`expect` sobre input extern. Els dos `expect` de l'executable survival protegeixen invariants literals demostrats. Panic no és validació normal i no s'executa deliberadament dins l'intèrpret ni amb FFI manual.

Si apareix `PanicException`, reprodueix en subprocess, revisa l'invariant i converteix una fallada esperada en `Result`; no tractis panic com business logic.

## 12. Proves duals i typing

- `cargo fmt --check`: format estable;
- clippy amb `-D warnings`: patrons Rust sospitosos;
- `cargo test --locked`: comportament del domini sense Python;
- pytest: façana, extracció, paritat, errors, classes, threads i importació nativa;
- `python -m mypy.stubtest faststats_rs`: el runtime instal·lat concorda amb els stubs;
- `python -m mypy --strict tests/typing_consumer.py`: qui consumeix rep tipus útils.

`_native.pyi` manual i `py.typed` són estables. La introspection experimental de PyO3 és opcional. Els tests desactiven cache i expliquen el risc; un percentatge de coverage no substitueix comportament.

## 13. `Python::detach` i concurrència determinista

L'extracció ocorre attached i mou dades pròpies al closure:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

A dins no hi ha `Python`, `Bound`, callbacks ni préstecs Python. La classe/excepció es crea després, attached.

Un timeout no prova paral·lelisme. El build d'acceptació `test-hooks` usa `Mutex`/`Condvar`: dos closures han d'entrar abans de continuar. Si venç el límit d'un segon, el binding retorna un `RuntimeError` específic en comptes de classificar-lo com a input invàlid. La feature està off per defecte, `src/test_hooks.rs` no entra a l'sdist i els wheels release no exposen API/símbol.

El mòdul base manté `gil_used=true`. Alliberar el GIL en una regió no audita tot per a free-threaded Python.

## 14. Benchmark honest: frontera, còpia i batching

Primer es comparen amb l'oracle Python tots els camps públics (`count`, `minimum`, `maximum`, `mean`, `anomaly_count` i `anomaly_ratio`) i casos representatius de `TypeError`/`ValueError`; només després es mesuren profile release, warm-up, repeticions, mediana i diverses mides. La còpia a `Vec` compta.

```bash illustrative
python benchmarks/benchmark.py
```

Un input petit pot perdre per overhead. Agrupa treball o conserva Python. No hi ha speedup mínim.

**TODO:** afegeix `n=100`. **Pista:** compara medianes i documenta context/soroll, sense generalitzar una màquina.

## 15. Distribució: sdist i dos wheels

L'sdist inclou metadata, llicència, README, façana/stubs, source Rust, `Cargo.lock`, el toolchain fixat i els pins directes d'eines Python; exclou targets, caches, binaris i rendezvous. Es desempaqueta i els dos wheels es reconstrueixen des d'ell.

El wheel específic reflecteix Python/ABI/plataforma, per exemple `cp313-cp313-manylinux_..._x86_64`. No promet altres targets.

La feature `abi3-py311` produeix `cp311-abi3-<platform>` per a CPython compatible amb GIL des de 3.11, però continua limitada per OS/arquitectura/APIs. `abi3t` exigeix Python 3.15+ i auditoria free-threaded separada: no és claim del base.

## 16. Verificació en una ordre

Des d'aquest capítol:

```bash illustrative
python -B examples/faststats-rs/tools/verify.py
```

Usa targets, wheels, venvs i cwd temporals; executa pins, fmt/clippy/Cargo, error de move i solució, primera extensió, hook wheel, sdist, els dos wheels, pytest, typing, benchmark, imports/tags/contingut i hygiene.

El gate del llibre crida l'adapter Rust:

```bash illustrative
python -B ../tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

El plugin només posseeix Rust/Cargo/PyO3/source refs; el root posseeix Markdown, selectors, links, RTL, accessibilitat, classificació i hygiene.

## 17. Modificacions guiades

### Exercici A: límit enter

Objectiu: protegir el contracte exacte dels enters. Afegeix proves per a `-(2**53)` i `-(2**53)-1`.

- TODO: afegeix els valors a les proves de paritat.
- Pista: el primer s'accepta; el segon llança `ValueError`.
- Èxit: referència i native concorden i les proves existents continuen passant.
- Per què: una frontera de conversió sense un límit provat es desvia amb facilitat.

### Exercici B: transacció

Objectiu: fer observable la mutació parcial. Estén un `OnlineStats` que conté `[1, 2]` amb `[3, float("inf"), 4]`.

- TODO: desa un snapshot de les quatre propietats abans de la crida.
- Pista: comprova l'excepció i després el snapshot complet.
- Solució: `tests/test_classes.py` usa el mateix patró preparar/fallar/comparar per a diversos tipus no vàlids.

### Exercici C: decidir no usar Rust

Objectiu: practicar el criteri d'enginyeria. Tria una càrrega petita del teu projecte i escriu una nota de decisió.

- Mesura el comportament actual de Python.
- Identifica si les crides es poden agrupar en lots.
- Inclou el cost de build, release i manteniment.
- Accepta «conservar Python» com a resultat satisfactori quan l'evidència ho avali.

## 18. Errors comuns per capa

- Compiler: localitza move/borrow/scope abans de clonar.
- Cargo: actualitza lock deliberadament i repeteix la suite.
- Linker: instal·la build tools; canviar Python no ho arregla.
- maturin: activa venv o construeix wheel.
- Import: usa cwd extern i `module.__file__`.
- Extraction: valida el tipus exacte.
- GIL: dades pròpies abans de detach; resultat Python després.
- Packaging: reconstrueix sempre des de sdist.
- Performance: igualtat, warm-up, repeticions i context.

Els errors són evidència d'una capa, no un judici sobre la persona. Diagnostica la capa més baixa que falla.

## 19. Checkpoints i rúbrica

En cada ruta, explica el resultat en veu alta o per escrit:

- **Preparació:** identifica Python, Rust i target actius, i recupera't d'un error de configuració.
- **Essencial:** explica qui posseeix un `String`, per què un slice es pren en préstec i com `Result` transporta la fallada.
- **Integració:** traça una crida per la façana, PyO3, les dades pròpies, el domini i l'excepció o el resultat.
- **Professional:** demostra paritat, estat transaccional, typing i importació neta instal·lada.
- **Hero:** explica la seguretat del closure separat, la prova de rendezvous, els límits del benchmark i els tags del wheel.

Rúbrica final, amb 0–2 punts per categoria: correcció; ownership idiomàtic; seguretat de la frontera; claredat de l'API; recuperació d'errors; proves Rust/Python; concurrència determinista; mesura honesta; evidència de packaging/typing; i la teva explicació. Un capstone complet no té cap categoria a 0 i suma almenys 16/20.

## 20. Glossari i reflexió

- **crate:** unitat de compilació i paquet de Rust.
- **ownership:** regla que defineix quin valor és responsable d'alliberar un recurs.
- **borrow:** accés temporal sense assumir-ne la propietat.
- **PyO3:** bindings i macros de Rust per integrar CPython.
- **GIL:** lock que usen les compilacions ordinàries de CPython per protegir l'accés a l'intèrpret.
- **ABI:** acord a nivell binari entre components compilats.
- **sdist:** arxiu font usat per reconstruir un paquet.
- **wheel:** distribució Python construïda i etiquetada per a runtimes i plataformes compatibles.
- **abi3:** mode d'ABI estable de CPython amb una versió mínima de Python i un wheel específic de plataforma.

Reflexiona: quina és la frontera nativa mínima útil? Què canviaria amb un buffer NumPy mutable o handles Python globals? Si no pots dir owner, lifetime, error, test i compatibilitat, encara no està preparada.

## Referències verificades

- [Instal·lació oficial de Rust](https://rust-lang.org/tools/install/)
- [Rust Book sobre ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [Rust Book sobre errors](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [Guia PyO3 0.29](https://pyo3.rs/v0.29.0/)
- [Paral·lelisme PyO3 i `Python::detach`](https://pyo3.rs/main/parallelism)
- [Layout mixt de maturin](https://www.maturin.rs/project_layout.html)
- [Bindings i ABI estable de maturin](https://www.maturin.rs/bindings.html)

Material sensible a versions comprovat el 2026-07-13 i fixat als assets. Repeteix el verificador abans de moure pins.
