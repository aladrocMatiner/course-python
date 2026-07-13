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
| Windows | MSVC Build Tools compatibles | usar Developer shell |

Els pins eviten la paraula inestable “latest”:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# Activa .venv amb l'ordre de la teva shell.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

La instal·lació pot usar Internet. Preflight revisa per ordre Python/venv, rustup/toolchain, Cargo/target, linker i maturin. Un linker absent no és un error PyO3; un venv inactiu no és un error Rust.

Errors recuperables:

- `rustup` absent: usa l'instal·lador oficial, reinicia la shell i verifica la versió;
- apareix Rust 1.96: executa `rustup run 1.97.0 rustc --version`, sense relaxar el pin;
- maturin no detecta el venv: activa'l o construeix un wheel;
- l'import només funciona des del source: canvia a un cwd temporal i inspecciona `module.__file__`.

**TODO:** desa l'informe JSON del preflight. **Pista:** `python -B tools/preflight.py --json` és read-only.

## 3. Primer programa Rust: valors, funcions i tests

Un crate és la unitat de paquet/compilació. `Cargo.toml` és el manifest. Edition 2024 selecciona idioms i `rust-version = "1.97.0"` fixa el compilador validat.

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

Ordre exacte: validar; actualitzar mean en ordre amb `mean += (value - mean) / count`; segona passada contra la mitjana final; comptar només delta superior i fora de la banda `1e-12`.

Per `[-3,-3,-1]`, threshold `0.5`, mean és `-7/3` i les tres mostres són anomalies. Una classificació streaming canviaria el resultat.

`OnlineStatsData.extend` modifica un clon i només el confirma després de validar. Una fallada conserva tot l'estat.

**TODO:** test de threshold negatiu. **Solució explicada:** esperar `DomainError::InvalidThreshold`; no fer clamp silenciós.

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

`faststats_rs._native` és implementació compilada; `faststats_rs` és l'API pública tipada. `python-source` i `module-name` munten les dues capes. El crate produeix `cdylib` i `rlib`.

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

`summarize(samples, *, threshold)` accepta 1–1.000.000 elements i retorna `Summary` frozen amb count/minimum/maximum/mean/anomaly_count/anomaly_ratio.

- domini/mida/rang/finitud/threshold invàlid → `ValueError`;
- tipus rebutjat → `TypeError`;
- igualtat o proximitat `1e-12` al threshold → no anomalia;
- camps enters exactes i floats comparats amb tolerància `1e-12`.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """El test company compara referència i natiu."""
```

**Exercici:** prediu `[True]`, `[2**53+1]`, `[nan]`. **Solució:** `True` produeix `TypeError`; els altres són tipus admesos amb valor invàlid i produeixen `ValueError`.

## 10. Classes Pythonic i estat transaccional

`Summary` frozen només permet lectura. `OnlineStats` té `add`, `extend`, `reset` i propietats; empty/reset és `0/None/None/None`. El màxim total és un milió.

Els mètodes sempre estan attached/GIL-held i mai detachen. No és una primitive de mutació concurrent. `extend([4,bad,5])` converteix i valida abans de confirmar: res canvia si falla.

Error comú: incrementar count durant l'extracció. Un error intermedi deixaria estat parcial; per això es prepara i després es confirma.

## 11. Errors i frontera de panic

Els errors esperats viatgen com `Result<T,DomainError>` i `TypeError`/`ValueError`. Les operacions PyO3 usen `PyResult` i `?` sense perdre l'excepció activa.

No hi ha `unwrap`/`expect` sobre input extern. Els dos `expect` de l'executable survival protegeixen invariants literals demostrats. Panic no és validació normal i no s'executa deliberadament dins l'intèrpret ni amb FFI manual.

Si apareix `PanicException`, reprodueix en subprocess, revisa l'invariant i converteix una fallada esperada en `Result`; no tractis panic com business logic.

## 12. Proves duals i typing

- fmt: format; clippy `-D warnings`: patrons sospitosos;
- Cargo tests: domini sense Python;
- pytest: façana, paritat, errors, classes, threads i import real;
- stubtest: runtime instal·lat contra stubs;
- mypy strict: experiència del consumidor.

`_native.pyi` manual i `py.typed` són estables. La introspection experimental de PyO3 és opcional. Els tests desactiven cache i expliquen el risc; un percentatge de coverage no substitueix comportament.

## 13. `Python::detach` i concurrència determinista

L'extracció ocorre attached i mou dades pròpies al closure:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

A dins no hi ha `Python`, `Bound`, callbacks ni préstecs Python. La classe/excepció es crea després, attached.

Un timeout no prova paral·lelisme. El build d'acceptació `test-hooks` usa `Mutex`/`Condvar`: dos closures han d'entrar abans de continuar. La feature està off per defecte, `src/test_hooks.rs` no entra a l'sdist i els wheels release no exposen API/símbol.

El mòdul base manté `gil_used=true`. Alliberar el GIL en una regió no audita tot per a free-threaded Python.

## 14. Benchmark honest: frontera, còpia i batching

Primer es verifica igualtat; després profile release, warm-up, repeticions, mediana i diverses mides. La còpia a `Vec` compta.

```bash illustrative
python benchmarks/benchmark.py
```

Un input petit pot perdre per overhead. Agrupa treball o conserva Python. No hi ha speedup mínim.

**TODO:** afegeix `n=100`. **Pista:** compara medianes i documenta context/soroll, sense generalitzar una màquina.

## 15. Distribució: sdist i dos wheels

L'sdist inclou metadata, llicència, README, façana/stubs, source Rust, Cargo/locks i toolchain; exclou targets, caches, binaris i rendezvous. Es desempaqueta i els dos wheels es reconstrueixen des d'ell.

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

Afegeix `-(2**53)` i `-(2**53)-1`. Pista: el primer passa i el segon dona `ValueError`. Èxit: referència i native coincideixen.

### Exercici B: transacció

Partint de `[1,2]`, intenta `[3,inf,4]`. Desa les quatre propietats, verifica excepció i snapshot intacte. `tests/test_classes.py` mostra la solució explicada.

### Exercici C: decidir no usar Rust

Mesura un workload Python, estudia batching i costos de build/release/manteniment. “Conservar Python” és correcte si l'evidència ho suporta.

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

Preparació: toolchain i recuperació. Essencial: owner/borrow/Result. Integració: call path. Professional: paritat/transacció/typing/import. Hero: detach/rendezvous/benchmark/tags.

Rúbrica 0–2: correcció, ownership idiomàtic, seguretat de frontera, API, recuperació, tests Rust/Python, concurrència, mesura, packaging/typing i explicació. Capstone complet: cap categoria 0 i almenys 16/20.

## 20. Glossari i reflexió

- **crate:** unitat Rust; **ownership:** responsable d'alliberar; **borrow:** accés temporal.
- **PyO3:** bindings/macros CPython; **GIL:** lock de l'intèrpret ordinari.
- **ABI:** acord binari; **sdist:** source distribuït; **wheel:** artefacte construït; **abi3:** ABI estable amb mínim Python i plataforma.

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
