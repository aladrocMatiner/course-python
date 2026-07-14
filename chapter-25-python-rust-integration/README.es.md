# Capítulo 25 · Python y Rust: desde el primer crate hasta un wheel verificado

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

Este capítulo parte de cero conocimientos de Rust. Primero construirás un programa y un dominio de estadísticas en Rust puro; solo después cruzarás la frontera con Python mediante PyO3. El resultado es `faststats_rs`: paquete mixto tipado con pruebas deterministas, trabajo paralelo acotado, sdist, wheel específico y wheel `abi3-py311`.

Todos los ejemplos son fuentes originales bajo [`examples/`](examples/). El verificador completo escribe builds y entornos en directorios temporales; no publica nada ni usa credenciales.

## Objetivos y prerrequisitos

Al terminar podrás:

- explicar crate, compilador, módulo de extensión, interfaz binaria de aplicación (ABI), sdist y wheel;
- leer variables, structs, `Vec<T>`, slices, ownership, borrowing, `Option` y `Result`;
- separar dominio Rust de PyO3 y convertir errores recuperables en excepciones Python;
- explicar qué se copia, mueve, presta o cuenta por referencias en la frontera;
- fijar un contrato numérico exacto y acotado antes de optimizar;
- usar `Python::detach` solo con datos propios de Rust y no confundirlo con soporte free-threaded;
- probar Rust, Python, typing, concurrencia, sdist, wheels e imports limpios;
- interpretar benchmarks sin prometer que Rust siempre gana.

Necesitas el contenido de [excepciones](../chapter-14-exceptions/README.es.md), [módulos](../chapter-15-modulos/README.es.md), [entornos](../chapter-16-entornos/README.es.md), [testing](../chapter-18-testing/README.es.md), [logging](../chapter-20-logging/README.es.md) e [introspección](../chapter-22-introspection/README.es.md). Los capítulos 23 y 24 no son prerrequisitos.

Se requiere CPython 3.11+, Internet para instalar inicialmente toolchain/crates, linker de plataforma y unas 16 sesiones de 45–60 minutos. La implementación se verificó en Linux x86-64, CPython 3.13.11, Rust 1.97.0, PyO3 0.29.0 y maturin 1.14.1. Otros sistemas son instrucciones por validar, no soporte afirmado.

## Mapa de rutas

| Ruta | Tiempo | Resultado observable | Criterio |
|---|---:|---|---|
| Preparación | 1–2 sesiones | Informe del toolchain y primer test Rust | `cargo test --locked` |
| Rust esencial | 4 sesiones | Dominio independiente de Python | fmt, clippy y tests |
| Integración | 3 sesiones | Python importa extensión PyO3 privada | wheel instalado fuera del source |
| Profesional | 3–4 sesiones | Clases, errores, typing y paridad | pytest, stubtest, mypy strict |
| Hero | 3–4 sesiones | Trabajo detached y dos wheels auditados | rendezvous, sdist e installs limpios |

Puedes parar tras cualquier checkpoint; Hero no es necesario para completar la ruta esencial.

## 1. ¿Por qué cruzar la frontera?

Python suele ser el mejor comienzo. Rust añade compilador, herramientas de plataforma, packaging y otro modelo de memoria. Ese coste se justifica después de fijar la corrección y medir una frontera útil.

El proyecto resume hasta un millón de muestras. Python conserva la experiencia pública; Rust recibe un dominio estrecho. Una referencia Python impide aceptar una respuesta rápida pero incorrecta.

**Predice:** ¿será mejor una llamada con 100 000 valores o 100 000 llamadas con un valor? La segunda paga la frontera repetidamente. Lo mediremos.

**Checkpoint:** explica cuándo conservar Python: ya es suficientemente rápido, las llamadas son pequeñas, existe una biblioteca o el coste de mantenimiento supera el beneficio.

## 2. Preparación: diagnostica antes de compilar

Instala Rust con `rustup` y maturin como herramienta Python publicada, no mediante `cargo install maturin` en la ruta base. Linux necesita linker/build essentials; macOS, command-line tools de Xcode; Windows, normalmente MSVC Build Tools compatibles con Python de 64 bits.

| Sistema | Prerrequisito nativo | Primer diagnóstico |
|---|---|---|
| Linux | herramientas C/linker de la distribución | `cc --version` |
| macOS | command-line tools de Xcode | `xcode-select -p` |
| Windows | MSVC Build Tools compatibles | ejecutar `cl` o `clang-cl` desde Developer shell |

Los pins evitan la palabra inestable “latest”:

```bash illustrative
rustup toolchain install 1.97.0 --profile minimal --component rustfmt --component clippy
python -m venv .venv
# Activa .venv con el comando de tu shell.
python -m pip install -r examples/faststats-rs/requirements-dev.lock
python -B tools/preflight.py --require-venv
```

La instalación puede usar Internet. `requirements-dev.lock` fija las dependencias Python directas de verificación, pero no es un lock transitivo generado por un resolver con hashes. `Cargo.lock` fija el grafo Rust y `rust-toolchain.toml` selecciona Rust 1.97.0. Preflight revisa por orden Python/venv, rustup/toolchain, Cargo/target, linker y maturin; en Windows acepta `cl` o `clang-cl`. Un linker ausente no es un error de PyO3 y un venv inactivo no es un error de Rust.

### Errores de configuración recuperables

- `rustup` ausente: usa el instalador oficial, reinicia el shell y verifica la versión;
- aparece Rust 1.96: ejecuta `rustup run 1.97.0 rustc --version`, sin relajar el pin;
- maturin no detecta venv: actívalo o construye un wheel;
- import solo funciona desde el source: cambia a un cwd temporal e inspecciona `module.__file__`.

**TODO:** ejecuta preflight y registra Python, arquitectura, target del host, rustc, Cargo y maturin. **Pista:** `python -B tools/preflight.py --json` crea un informe copiable sin modificar el repositorio.

## 3. Primer programa Rust: valores, funciones y tests

Un crate es la unidad de paquete/compilación. `Cargo.toml` es el manifiesto. Edition 2024 selecciona idioms. `rust-version = "1.97.0"` declara el MSRV; el `rust-toolchain.toml` versionado selecciona exactamente 1.97.0 para los ejercicios.

```bash illustrative
cd examples/00-rust-survival
cargo check --locked
cargo run --locked
cargo test --locked
```

Salida significativa:

```text illustrative
workshop mean: 19.0
```

La biblioteca introduce struct, slice prestado, `Option`, enum, `Result` y `?` con una lectura de sensor acotada.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/src/lib.rs" check="rust:contract" -->
```rust source-ref
pub fn average(values: &[f64]) -> Option<f64> { /* fuente probada */ }
pub fn parse_reading(text: &str) -> Result<Reading, ParseReadingError> { /* ... */ }
```

`Option` expresa que el promedio vacío no existe; `Result` expresa fallos recuperables sin sentinels mágicos.

**Modifica:** prueba `"lab:NaN"`. **Pista:** el parse sintáctico funciona y después `is_finite()` lo rechaza. La solución usa `NonFiniteNumber`: tener forma numérica no basta para pertenecer al dominio.

## 4. Ownership y borrowing: el compilador da pistas

Cada valor Rust tiene owner. Una asignación puede moverlo. Un préstamo `&T` permite leer temporalmente; `&mut T` concede acceso mutable exclusivo.

Predice la línea errónea:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_move_error.rs" check="rust:contract" -->
```rust source-ref
let label = String::from("sensor-a");
let moved_label = label;
println!("{moved_label}");
println!("{label}"); // E0382: uso después del move
```

Aunque el compilador sugiera `.clone()`, pregunta primero quién debe conservar ownership. Aquí basta prestar:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/00-rust-survival/lessons/ownership_borrow_solution.rs" check="rust:contract" -->
```rust source-ref
fn print_label(label: &str) { println!("{label}"); }
// El caller conserva String y presta &str dos veces.
```

Error común: clonar hasta silenciar el compiler. Un clone necesita una justificación de coste y dos owners deliberados.

**Autoevaluación:** en `average(values: &[f64])`, el caller posee la colección, `average` presta un slice durante la llamada y el préstamo no puede sobrevivir a los datos.

## 5. Dominio Rust puro antes de PyO3

El dominio recibe `f64` ya convertidos y desconoce Python y el Global Interpreter Lock (GIL). Así `cargo test` aísla la semántica numérica.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/domain.rs" check="rust:contract" -->
```rust source-ref
pub const MAX_SAMPLES: usize = 1_000_000;
pub const MAX_ABS_VALUE: f64 = 1.0e150;
pub fn summarize(values: &[f64], threshold: f64)
    -> Result<SummaryData, DomainError> { /* implementación probada */ }
```

El orden exacto es importante:

1. valida el recuento, la finitud, el rango de los valores y el threshold;
2. actualiza `mean += (value - mean) / count` en el orden de entrada;
3. realiza una segunda pasada respecto a la media final;
4. cuenta un delta solo si es mayor que el threshold y está fuera de la banda de tolerancia `1e-12`.

Para `[-3,-3,-1]`, threshold `0.5`, mean es `-7/3` y las tres muestras son anomalías. Una clasificación streaming cambiaría el resultado.

`OnlineStatsData.extend` modifica un clon y lo confirma solo tras validar. Un fallo conserva todo el estado.

**TODO:** añade una prueba de dominio para un threshold negativo. **Pista:** llama a `validate_threshold` antes de calcular. **Solución explicada:** espera `DomainError::InvalidThreshold`; no hagas clamp silencioso porque cambiaría la petición de quien llama.

## 6. Primera extensión PyO3

`#[pyfunction]` expone funciones y `#[pymodule]` inicializa. El módulo declara `gil_used = true` para no anunciar compatibilidad free-threaded no auditada.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/01-first-extension/src/lib.rs" check="rust:contract" -->
```rust source-ref
#[pyfunction]
fn double(value: i64) -> PyResult<i64> { /* multiplicación comprobada */ }

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

Overflow se convierte en `ValueError`; tipo incorrecto en `TypeError`. No añadas la feature histórica deprecada `pyo3/extension-module`: esta ruta maturin no la necesita.

## 7. Paquete mixto: nativo privado, fachada pública

`faststats_rs` usa dos capas:

- `faststats_rs._native`: detalle de implementación compilado;
- `faststats_rs`: fachada Python documentada y superficie de tipos estable.

`pyproject.toml` establece `python-source = "python"` y `module-name = "faststats_rs._native"`. El crate produce `cdylib` para Python y `rlib` para las pruebas del lado de Rust.

`_reference.py` es oráculo, no fallback silencioso. Un `_native` ausente se diagnostica como no construido; un fallo binario interno conserva el error original.

**Predice:** probar fuera del directorio evita que `sys.path` oculte archivos ausentes del wheel.

**Checkpoint:** caller → fachada → `_native` → extracción → `Vec<f64>` propio → dominio → clase o excepción.

## 8. Tipos exactos y lifetimes PyO3

Solo se aceptan `int`/`float` built-in exactos. Se rechazan `bool`, `Fraction`, `Decimal`, subclasses, NumPy scalars y `__float__`. Enteros: `abs<=2**53`; flotantes: finitos y `abs<=1e150`.

La secuencia se convierte/copia a `Vec<f64>` antes del cómputo detached; no es zero-copy.

- `Python<'py>` prueba que el thread está attached;
- `Bound<'py,T>` está ligado a esa attachment;
- `Py<T>` posee reference count, pero necesita attachment correcta para acceder.

Ningún préstamo Python entra en `domain.rs` ni escapa a detach. `describe_payload` prueba Unicode, bytes y opcionales.

**Optional preview:** NumPy/Arrow/buffers requieren contratos de layout, lifetime, aliasing y mutación; quedan fuera.

## 9. Contrato exacto de `faststats_rs`

`summarize(samples, *, threshold)` exige entre 1 y 1 000 000 valores. Threshold debe ser un número built-in exacto, finito y dentro de `[0, 1e150]`. Devuelve `Summary(count, minimum, maximum, mean, anomaly_count, anomaly_ratio)` frozen.

- entrada vacía, 1 000 001 elementos, valores no finitos, fuera de rango, enteros demasiado grandes o threshold inválido → `ValueError`;
- tipo Python rechazado → `TypeError`;
- un solo valor → ratio `0.0` con cualquier threshold no negativo válido;
- igualdad o cercanía al threshold dentro de la tolerancia `1e-12` → no anomalía;
- los campos enteros se comparan exactamente; los campos flotantes usan `rel_tol=abs_tol=1e-12` en las pruebas de paridad.

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/tests/test_parity.py" check="rust:contract" -->
```python source-ref
def assert_equivalent(samples, threshold):
    """El test compañero compara referencia y nativo."""
```

**Ejercicio:** predice la excepción para `[True]`, `[2**53 + 1]` y `[float("nan")]`. **Pista:** la validación de tipos ocurre antes que la validación del rango numérico. **Solución:** `True` produce `TypeError`; los otros dos son tipos admitidos con valores inválidos y producen `ValueError`.

## 10. Clases Pythonic y estado transaccional

`Summary` frozen solo permite lectura. `OnlineStats` tiene `add`, `extend`, `reset` y propiedades; empty/reset es `0/None/None/None`. El máximo total es un millón.

Sus métodos siempre están attached/GIL-held y nunca detachan. No es una primitive de mutación concurrente. `extend([4,bad,5])` convierte y valida antes de confirmar: nada cambia si falla.

Error común: incrementar count mientras se extrae. Un error intermedio dejaría estado parcial; por eso el diseño prepara y luego confirma.

## 11. Errores y frontera de panic

Los errores esperados viajan como `Result<T,DomainError>` y `TypeError`/`ValueError`. Las operaciones PyO3 usan `PyResult` y `?` sin perder la excepción activa.

No hay `unwrap`/`expect` sobre input externo. Los dos `expect` del ejecutable survival protegen invariantes literales demostrados. Panic no es validación normal y no se ejecuta deliberadamente dentro del intérprete ni mediante FFI manual.

Si aparece `PanicException`, reproduce en subprocess, revisa el invariant y convierte un fallo esperado en `Result`; no trates panic como business logic.

## 12. Pruebas duales y typing

- `cargo fmt --check`: formato estable;
- clippy con `-D warnings`: patrones Rust sospechosos;
- `cargo test --locked`: comportamiento del dominio sin Python;
- pytest: fachada, extracción, paridad, errores, clases, threads e importación nativa;
- `python -m mypy.stubtest faststats_rs`: el runtime instalado concuerda con los stubs;
- `python -m mypy --strict tests/typing_consumer.py`: quien consume recibe tipos útiles.

`_native.pyi` manual y `py.typed` son estables. Introspection experimental de PyO3 es opcional. Los tests desactivan cache y explican el riesgo protegido; un número de cobertura no sustituye comportamiento.

## 13. `Python::detach` y concurrencia determinista

La extracción sucede attached y mueve datos propios al closure:

<!-- bookcheck: path="chapter-25-python-rust-integration/examples/faststats-rs/src/lib.rs" check="rust:contract" -->
```rust source-ref
let result = py.detach(move || domain::summarize(&values, threshold));
```

Dentro no hay `Python`, `Bound`, callbacks ni préstamos Python. La clase/excepción se crea después, attached.

Un timeout no prueba paralelismo. El build de aceptación `test-hooks` usa `Mutex`/`Condvar`: dos closures deben entrar antes de continuar. Si vence su límite de un segundo, el binding devuelve un `RuntimeError` específico en vez de clasificarlo como input inválido. La feature está off por defecto, `src/test_hooks.rs` no entra en el sdist y los wheels release no exponen API/símbolo.

El módulo base conserva `gil_used=true`. Liberar el GIL en una región no audita todo para free-threaded Python.

## 14. Benchmark honesto: frontera, copia y batching

Primero se comparan con el oracle Python todos los campos públicos (`count`, `minimum`, `maximum`, `mean`, `anomaly_count` y `anomaly_ratio`) y casos representativos de `TypeError`/`ValueError`; solo después se miden profile release, warm-up, repeticiones, mediana y varios tamaños. La copia a `Vec` cuenta.

```bash illustrative
python benchmarks/benchmark.py
```

Un input pequeño puede perder por overhead. Agrupa trabajo o conserva Python. No existe speedup mínimo.

**TODO:** añade `n=100`. **Pista:** compara medianas y documenta contexto/ruido, sin generalizar una máquina.

## 15. Distribución: sdist y dos wheels

El sdist incluye metadata, licencia, README, fachada/stubs, source Rust, `Cargo.lock`, el toolchain fijado y los pins directos de herramientas Python; excluye targets, caches, binarios y rendezvous. Se desempaqueta y ambos wheels se reconstruyen desde él.

El wheel específico refleja Python/ABI/plataforma, por ejemplo `cp313-cp313-manylinux_..._x86_64`. No promete otros targets.

La feature `abi3-py311` produce `cp311-abi3-<platform>` para CPython compatible con GIL desde 3.11, pero sigue limitada por OS/arquitectura/APIs. `abi3t` exige Python 3.15+ y auditoría free-threaded separada: no es claim del base.

## 16. Verificación en un comando

Desde este capítulo:

```bash illustrative
python -B examples/faststats-rs/tools/verify.py
```

Usa targets, wheels, venvs y cwd temporales; ejecuta pins, fmt/clippy/Cargo, error de move y solución, primera extensión, hook wheel, sdist, ambos wheels, pytest, typing, benchmark, imports/tags/contenido e hygiene.

El gate del libro llama al adapter Rust:

```bash illustrative
python -B ../tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py
```

El plugin solo posee Rust/Cargo/PyO3/source refs; el root posee Markdown, selectores, links, RTL, accesibilidad, clasificación e hygiene.

## 17. Modificaciones guiadas

### Ejercicio A: límite entero

Objetivo: proteger el contrato exacto de los enteros. Añade pruebas para `-(2**53)` y `-(2**53)-1`.

- TODO: añade los valores a las pruebas de paridad.
- Pista: el primero se acepta; el segundo lanza `ValueError`.
- Éxito: referencia y native concuerdan y las pruebas existentes siguen pasando.
- Por qué: una frontera de conversión sin un límite probado se desvía con facilidad.

### Ejercicio B: transacción

Objetivo: hacer observable la mutación parcial. Extiende un `OnlineStats` que contiene `[1, 2]` con `[3, float("inf"), 4]`.

- TODO: guarda un snapshot de las cuatro propiedades antes de la llamada.
- Pista: comprueba la excepción y después el snapshot completo.
- Solución: `tests/test_classes.py` usa el mismo patrón preparar/fallar/comparar para varios tipos inválidos.

### Ejercicio C: decidir no usar Rust

Objetivo: practicar el criterio de ingeniería. Elige una carga pequeña de tu proyecto y escribe una nota de decisión.

- Mide el comportamiento actual de Python.
- Identifica si las llamadas pueden agruparse en lotes.
- Incluye el coste de build, release y mantenimiento.
- Acepta «conservar Python» como resultado satisfactorio cuando la evidencia lo respalde.

## 18. Errores comunes por capa

- Compiler: localiza move/borrow/scope antes de clonar.
- Cargo: actualiza lock deliberadamente y repite la suite.
- Linker: instala build tools; cambiar Python no lo arregla.
- maturin: activa venv o construye wheel.
- Import: usa cwd externo y `module.__file__`.
- Extraction: valida tipo exacto.
- GIL: datos propios antes de detach; resultado Python después.
- Packaging: reconstruye siempre desde sdist.
- Performance: igualdad, warm-up, repeticiones y contexto.

Los errores son evidencia de una capa, no un juicio sobre la persona. Diagnostica la capa más baja que falla.

## 19. Checkpoints y rúbrica

En cada ruta, explica el resultado en voz alta o por escrito:

- **Preparación:** identifica Python, Rust y target activos, y recupérate de un error de configuración.
- **Esencial:** explica quién posee un `String`, por qué un slice se toma prestado y cómo `Result` transporta el fallo.
- **Integración:** traza una llamada por la fachada, PyO3, los datos propios, el dominio y la excepción o el resultado.
- **Profesional:** demuestra paridad, estado transaccional, typing e importación limpia instalada.
- **Hero:** explica la seguridad del closure separado, la prueba de rendezvous, los límites del benchmark y los tags del wheel.

Rúbrica final, con 0–2 puntos por categoría: corrección; ownership idiomático; seguridad de la frontera; claridad de la API; recuperación de errores; pruebas Rust/Python; concurrencia determinista; medición honesta; evidencia de packaging/typing; y tu explicación. Un capstone completo no tiene ninguna categoría a 0 y suma al menos 16/20.

## 20. Glosario y reflexión

- **crate:** unidad de compilación y paquete de Rust.
- **ownership:** regla que define qué valor es responsable de liberar un recurso.
- **borrow:** acceso temporal sin asumir la propiedad.
- **PyO3:** bindings y macros de Rust para integrar CPython.
- **GIL:** lock que usan las compilaciones ordinarias de CPython para proteger el acceso al intérprete.
- **ABI:** acuerdo a nivel binario entre componentes compilados.
- **sdist:** archivo fuente usado para reconstruir un paquete.
- **wheel:** distribución Python construida y etiquetada para runtimes y plataformas compatibles.
- **abi3:** modo de ABI estable de CPython con una versión mínima de Python y un wheel específico de plataforma.

Reflexiona: ¿cuál es la frontera nativa mínima útil? ¿Qué cambiaría con un buffer NumPy mutable o handles Python globales? Si no puedes nombrar owner, lifetime, error, test y compatibilidad, aún no está lista.

## Referencias verificadas

- [Instalación oficial de Rust](https://rust-lang.org/tools/install/)
- [Rust Book sobre ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [Rust Book sobre errores](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [Guía PyO3 0.29](https://pyo3.rs/v0.29.0/)
- [Paralelismo PyO3 y `Python::detach`](https://pyo3.rs/main/parallelism)
- [Layout mixto de maturin](https://www.maturin.rs/project_layout.html)
- [Bindings y ABI estable de maturin](https://www.maturin.rs/bindings.html)

Material version-sensitive comprobado el 2026-07-13 y fijado en los assets. Repite el verificador antes de mover pins.
