## Context

El repositorio es un curso Python multilingüe sin Cargo, Rust, maturin, CI ni packaging global. Hay dos changes relevantes: redes reserva el capítulo 23 y C++ reserva el 24. Esta proposal reserva el 25; comparte con ellas únicamente los seis índices raíz y no depende de sus ejemplos ni validadores.

Rust presenta una dificultad pedagógica distinta de C++: el compiler obliga a razonar sobre ownership, borrowing y tipos antes de ejecutar. La integración con PyO3 añade un segundo modelo de memoria basado en reference counting y objetos Python compartidos. Por ello, el dominio Rust se enseñará y probará antes de introducir macros PyO3, y la región separada del intérprete solo recibirá valores Rust propios.

Baselines oficiales al redactar: Python 3.11+; Rust stable 1.97.0 con Edition 2024; PyO3 0.29.0; maturin >=1.14.1,<2. La feature histórica `pyo3/extension-module` está deprecada con maturin moderno y no aparecerá en la ruta base. El capítulo solo declara el toolchain 1.97.0 que verifica; no promete un MSRV 1.85 no probado. Las versiones se conservarán mediante `rust-toolchain.toml`, `Cargo.lock`, `requirements-dev.lock` y metadata.

## ASSUMPTIONS

- Assumption: el alumnado domina Python básico/intermedio del curso, pero puede no haber usado Rust, Cargo o un compiler nativo.
- Assumption: el contenido será capítulo 25 mientras estén reservados 23 para redes y 24 para C++; si cambia esa reserva se renumerará antes de implementar.
- Assumption: el capítulo C++ no es prerrequisito; una comparación C++/Rust será opcional y solo se enlazará si existe.
- Assumption: CPython 3.11+ es la ruta obligatoria; PyPy/GraalPy quedan fuera de aceptación.
- Assumption: el ejemplo pinneará Rust 1.97.0/Edition 2024 y PyO3 0.29; una ampliación de MSRV requeriría una matriz separada.
- Assumption: instalar Rust/maturin/crates requiere Internet inicialmente o caches preparados; no se promete setup offline.
- Assumption: maturin se instalará con pip/pipx/uv como binario/herramienta; `cargo install maturin` no será la ruta principal.
- Assumption: `README.md` será inglés canónico y se añadirán español, catalán, sueco y árabe, además de los seis índices.
- Assumption: la implementación comenzará solo tras aprobar la proposal.

## Goals / Non-Goals

### Goals

- Enseñar suficiente Rust para comprender, mantener y probar una extensión PyO3.
- Separar dominio Rust, binding, fachada Python, typing, tests y packaging.
- Hacer explícito qué se mueve, copia, presta o permanece ligado al intérprete.
- Traducir errores recuperables mediante `Result`/`PyResult` y evitar panics en el contrato.
- Demostrar `Python::detach` y concurrencia sin referencias Python dentro de la región nativa.
- Medir overhead/batching y construir wheels reales, incluida una variante `abi3-py311` auditada.
- Mantener aprendizaje gradual, localización completa y repositorio limpio.

### Non-Goals

- Sustituir un curso completo de Rust.
- Escribir `unsafe`, C ABI manual, raw pointers, lifetime extension o FFI con bibliotecas arbitrarias.
- Enseñar embedding de Python en Rust, async runtimes/Tokio, pyo3-async-runtimes o Rayon como rutas obligatorias.
- Requerir NumPy/Arrow/buffer zero-copy; se explicarán como siguientes pasos.
- Publicar a PyPI, usar credenciales, firmar artefactos o soportar cross-compilation/mobile/WASM.
- Declarar free-threaded/`abi3t` support en Python prerelease sin una matriz específica.
- Prometer que Rust siempre supera a Python o C++.
- Declarar aceptación humana de las traducciones, de la pedagogía renderizada, de la accesibilidad o del bidi árabe; esos gates de publicación pertenecen a `restore-multilingual-content-parity`.

## ARCHITECTURE SNAPSHOT

- Component map:
  - `chapter-25-python-rust-integration/README.md`: capítulo inglés de referencia.
  - `chapter-25-python-rust-integration/README.{es,ca,sv,ar}.md`: traducciones equivalentes.
  - `examples/00-rust-survival/`: Cargo, compiler feedback, ownership, borrowing, `Option`, `Result` y tests.
  - `examples/01-first-extension/`: primer módulo PyO3/maturin mínimo.
  - `examples/faststats-rs/Cargo.toml`: crate `cdylib`+`rlib`, PyO3 0.29 y features de packaging.
  - `examples/faststats-rs/Cargo.lock`: dependency graph verificado.
  - `examples/faststats-rs/rust-toolchain.toml`: stable exacto validado y componentes fmt/clippy.
  - `examples/faststats-rs/requirements-dev.lock`: maturin, pytest y mypy exactos usados para aceptación.
  - `examples/faststats-rs/src/domain.rs`: lógica Rust pura sin tipos PyO3.
  - `examples/faststats-rs/src/lib.rs`: módulo/binding fino y traducción.
  - `examples/faststats-rs/python/faststats_rs/`: `__init__.py`, `_reference.py`, `_native.pyi`, `py.typed`.
  - `examples/faststats-rs/tests/`: pytest de API, paridad, errores, typing, threads y wheel.
  - `examples/faststats-rs/benchmarks/`: benchmark por tamaños.
  - `examples/faststats-rs/tools/verify.py`: temp `CARGO_TARGET_DIR`, Cargo/maturin/test/sdist/wheel/type-check orchestration y rebuild desde el source distribuido.
  - `chapter-25-python-rust-integration/tools/bookcheck_plugin.py`: checks Rust/Cargo/PyO3/source-ref bajo `register(registry)` cuando existe el root gate; fallbacks genéricos solo si el capítulo llega primero y se retiran tras equivalence tests.
  - `openspec/changes/add-python-rust-integration-chapter/specs/teach-python-rust-integration/spec.md`: requisitos normativos.
- Key boundaries:
  - `domain.rs` no importa PyO3; `cargo test` verifica el core sin Python.
  - `lib.rs` convierte inputs a owned Rust values, llama el dominio y traduce `DomainError`.
  - El módulo base declara `#[pymodule(gil_used = true)]`; `gil_used = false` solo puede aparecer en una variante futura auditada.
  - `_native` es privado; `faststats_rs` mantiene el contrato público y tipado.
  - `_reference.py` es oráculo de paridad, no fallback silencioso ante un wheel roto.
  - `Python::detach` recibe únicamente datos Rust owned; no cruza `Python<'py>`, `Bound<'py,T>`, `Py<T>` accedido o referencias prestadas.
  - `Cargo.lock`, toolchain y rangos de maturin separan dependencia reproducible de compatibilidad futura.
  - `verify.py` usa `CARGO_TARGET_DIR`, wheel output, venv y cwd temporales fuera del chapter tree; `.gitignore` es defensa adicional, no evidencia.
- Data/control flow:
  - Python caller → fachada → `_native` → extraction PyO3 → owned `Vec<f64>`/config Rust → `domain::summarize` → `Result<Summary,DomainError>` → `#[pyclass(frozen)]` o excepción Python.
  - Trabajo CPU largo → extraction/copy con interpreter attached → `py.detach(|| domain(...))` → retorno owned → creación de objeto Python attached.
  - Packaging → Cargo/PyO3 cdylib → maturin mixed wheel → clean venv/cwd → import/contract smoke.

## Pedagogical Routes

### Preparación — 1–2 sesiones de 45–60 minutos

- Extensión nativa, compiler, crate, cdylib, Python module, wheel y ABI.
- Venv, rustup, rustc, Cargo y maturin; preflight y troubleshooting.
- `cargo new`, `cargo check`, `cargo run` y `cargo test`.
- Outcome: toolchain diagnosticado y primer programa/test Rust.

### Rust esencial — 4 sesiones de 45–60 minutos

- Variables, mutabilidad, funciones, tipos, `String`/`&str`, `Vec<T>`/`&[T]`.
- Moves, ownership, borrowing, references y compiler errors explicados.
- Structs/impl, enums/match, `Option`, `Result`, `?` y modules.
- Dominio `faststats` en Rust puro con casos límite.
- Outcome: library Rust probada sin Python ni PyO3.

### Integración — 3 sesiones de 45–60 minutos

- `cdylib`, `#[pymodule]`, `#[pyfunction]`, `PyResult` y `maturin develop`.
- Conversiones de numbers, strings, bytes, sequences y optionals; copy/borrow/lifetimes.
- Paquete mixto con `_native` privado y primera paridad Python/Rust.
- Outcome: Python llama al dominio Rust mediante API pública.

### Profesional — 3–4 sesiones de 45–60 minutos

- `#[pyclass(frozen)] Summary`, `OnlineStats`, métodos, repr, signatures y typing.
- Domain errors, custom Python exceptions, panic boundary y auditoría de `unwrap`.
- Tests Cargo+pytest, stubs, wheel metadata y diagnóstico de shadow import.
- Outcome: package mixto tipado, robusto y testeado.

### Hero — 3–4 sesiones de 45–60 minutos

- `Python::detach`, thread attachment, Send/Sync y límites de Python objects.
- Benchmarking, batching y interpretación por tamaños.
- Version-specific wheel, `abi3-py311`, tags e instalación limpia.
- Auditoría free-threaded/`abi3t`, hygiene y decisión “cuándo no usar Rust”.
- Outcome: wheel probado, API medida y compatibilidad declarada con evidencia.

Cada subsección sigue: objetivo/contexto → teoría mínima → predecir → ejecutar → observar → modificar → comprobar → happy path → edge case → error común → solución explicada → reflexión.

## Capstone Contract

- `summarize(samples, *, threshold)` acepta entre 1 y 1,000,000 elementos que sean exactamente built-in `int`/`float`; excluye `bool`, `Fraction`, `Decimal`, NumPy scalars y objetos arbitrarios con `__float__`. Los enteros exigen `abs(value)<=2**53`; todo valor convertido debe ser finito y satisfacer `abs(value)<=1e150`; threshold debe ser finito y estar en `[0,1e150]`.
- Devuelve `Summary` frozen con `count`, `minimum`, `maximum`, `mean`, `anomaly_count` y `anomaly_ratio`.
- Python y Rust calculan primero la media final en input order mediante `mean += (value - mean) / count`, sin reducción paralela ni fast-math/reordenación. En una segunda pasada comparan cada muestra contra ese `Summary.mean` final: una anomalía cumple `delta > threshold` y `not isclose(delta, threshold, rel_tol=1e-12, abs_tol=1e-12)`; igualdad y la banda no cuentan. Ratio es `anomaly_count / count`.
- Reference/native floats se comparan con `rel_tol=1e-12` y `abs_tol=1e-12`; integer fields son exactos.
- Empty, más de 1,000,000 muestras, rango/finitud o threshold inválido producen `ValueError`; tipos rechazados producen `TypeError`; ninguna validación fallida muta estado.
- `OnlineStats.add`, `extend`, `reset` y properties count/minimum/maximum/mean mantienen el mismo dominio de tipos/rangos y un total máximo de 1,000,000 muestras. En empty/reset, count=0 y min/max/mean=`None`. Tipo, rango, finitud o extensión por encima del límite conserva el estado anterior completo.
- `OnlineStats` nunca llama `Python::detach`; todos sus methods se ejecutan attached/GIL-held y usan runtime borrow checks de PyO3. No se presenta como primitive para concurrent mutation.

## Decisions

### Decision: Rust puro antes de PyO3

Ownership y `Result` se aprenderán en un crate normal. El compiler error será un resultado pedagógico con predicción y corrección. PyO3 se introduce solo cuando `domain.rs` ya tiene una API y tests estables.

Alternatives considered:

- Empezar con macros PyO3: produce un import rápido, pero mezcla errores de Rust, linker, Python y macros antes de entender ownership.

### Decision: Rust Edition 2024, toolchain pinned y locks completos

La ruta usa idioms actuales y `rust-toolchain.toml`/`rust-version` exactos en 1.97.0. `Cargo.lock` se versiona porque el artefacto es educativo/reproducible, y `requirements-dev.lock` fija maturin 1.14.1 y las versiones de pytest/mypy aceptadas. Al actualizar, se ejecuta la suite completa antes de mover pins.

### Decision: PyO3 0.29 y maturin 1.14 como ruta principal

PyO3 expresa módulos, funciones, clases y Python errors; maturin maneja build/wheel y configura extension linking. No se enseñará la feature deprecada `pyo3/extension-module`. Maturin se instala como binario/herramienta Python para no elevar innecesariamente el Rust mínimo mediante `cargo install`.

Alternatives considered:

- setuptools-rust: válido, pero añade otra capa de configuración sin mejorar el primer aprendizaje.
- CFFI/UniFFI/manual C ABI: útiles para otras arquitecturas, pero no como segunda ruta completa.

### Decision: mixed package y extensión privada

`python-source = "python"` y `module-name = "faststats_rs._native"` mantienen una fachada Python estable. `crate-type = ["cdylib", "rlib"]` permite extensión y tests/import interno del dominio. El package no capturará indiscriminadamente `ImportError` para ocultar incompatibilidad binaria.

### Decision: copy explícito antes de zero-copy

Una sequence Python se extraerá a `Vec<f64>` y el capítulo lo llamará copia/conversión. Esa simplicidad permite que `Python::detach` opere sobre datos owned. Buffers, NumPy/rust-numpy y Arrow se dejan como ampliación para no mezclar lifetimes FFI complejos con el primer capítulo.

### Decision: `Result` cruza; panic no es control de flujo

El dominio devuelve `Result<T,DomainError>`. El binding convierte el error a tipos Python documentados. `unwrap`/`expect` solo se permiten para invariantes locales demostradas o tests, nunca sobre input Python. Una demo de panic, si aporta valor, se ejecuta en subprocess y no forma parte del contrato.

### Decision: PyO3 lifetimes visibles

El capítulo explica `Python<'py>`, `Bound<'py,T>` y owned `Py<T>` con una tabla de owner/duración/operaciones válidas. No se extiende un lifetime manualmente ni se guarda una referencia prestada en una clase Rust. `Summary` frozen facilita lectura concurrente; `OnlineStats` documenta mutability/borrow rules.

### Decision: `Python::detach` solo sobre owned Rust data

Input extraction ocurre attached. El closure detached recibe `Vec`, numbers y config owned y devuelve un resultado Rust owned. La creación de Python objects y traducción de errors ocurre después. Un rendezvous exclusivo de tests con `std::sync::{Mutex,Condvar}` obliga a dos closures detached a entrar antes de continuar, por lo que una implementación serial no pasa. El hook vive bajo una feature `test-hooks` desactivada por defecto, se construye solo en un target de aceptación separado y su API/símbolo/source no aparece en sdist ni wheels de distribución. No se introduce Rayon.

### Decision: módulo base opt-out de free-threading y clase mutable GIL-bound

PyO3 0.29 considera por defecto que el módulo puede ejecutarse sin GIL; eso sería un support claim no auditado. El capstone declara `#[pymodule(gil_used = true)]`. `OnlineStats` se usa solo attached y no detacha sus methods; la concurrencia hero usa funciones batch sobre owned data, no una instancia mutable compartida. `gil_used = false` requiere otra variante/matriz y queda fuera del base.

### Decision: manual stable stubs verificados, introspection experimental opcional

El contrato usa `_native.pyi`/`py.typed`, `python -m mypy.stubtest faststats_rs` sobre wheel instalado y un consumer `python -m mypy --strict`. La generación basada en `experimental-inspect` se menciona porque sigue experimental y no sustituye verificación manual.

### Decision: wheel version-specific primero, `abi3-py311` después

La ruta profesional construye un sdist en temporal, lo desempaqueta y reconstruye desde ese source el wheel normal que refleja el intérprete. La ruta hero construye también desde el sdist una feature de packaging separada para `abi3-py311`, inspecciona tags y verifica en intérpretes disponibles compatibles. El contenido distribuido incluye metadata, licencia, README, package Python, stubs, Rust source y lockfiles requeridos, y excluye hooks/outputs. `abi3t` requiere Python 3.15+ y se mantiene como explicación/plan de prueba, no como criterio base.

### Decision: benchmarking honesto y batching

El benchmark verifica paridad, usa warm-up, múltiples muestras/mediana y tamaños. Debe mostrar overhead de extracción y al menos un caso pequeño donde Rust no gana. No existe speedup mínimo normativo.

### Decision: no claim multiplataforma sin matriz

Las instrucciones distinguen MSVC/GNU/Apple toolchains y los wheels son platform-specific incluso con stable ABI. Se registra el OS/arch/Python/Rust ejecutado. Otros targets se describen como diseñados o por validar, no como soportados.

### Decision: validador independiente y source refs

El root gate o fallback temporal ejecuta snippets seguros con timeout; fragmentos PyO3/Cargo referencian archivos cubiertos. `verify.py` crea `CARGO_TARGET_DIR`, output wheel y venv temporales para Cargo/maturin/test/type-check. El owner único de hygiene escanea incluso paths ignorados.

Si `add-book-quality-gates` se aprueba e implementa primero, `chapter-25-python-rust-integration/tools/bookcheck_plugin.py` expondrá el API versionado `register(registry)` y registrará solo checks Rust/Cargo/PyO3/source-ref; el root poseerá reglas editoriales e higiene. Mientras no exista, `validate_docs.py`/`check_hygiene.py` serán standalones temporales; tests de equivalencia precederán su eliminación/migración y no quedarán parsers genéricos duplicados.

### Decision: separar cierre técnico de aceptación editorial

Esta change es dueña de la autoría completa de los cinco documentos, sus companions Rust/PyO3, la navegación y la evidencia estructural/ejecutable. Esas señales no demuestran fluidez, equivalencia técnica/pedagógica localizada, accesibilidad renderizada ni bidi/copy-paste árabe. `maintain-multilingual-course-parity` conserva los digests, las doce dimensiones semánticas y las decisiones de revisores humanos competentes; archivar esta implementación no promueve ningún registro localizado a `accepted`.

La revisión de paridad puede reparar prosa dirigida al alumnado sin reabrir esta capability técnica. Un cambio al contrato de dominio, a los companions o a su comportamiento sí requiere una change técnica nueva o de corrección.

## Risks / Trade-offs

- Ownership intimida a principiantes → ejemplos pequeños, compiler feedback normalizado y dominio puro antes de macros.
- Toolchain/install voluminoso → preflight, rustup recomendado, maturin binario y requisitos explícitos de red/permisos.
- PyO3 API cambia en versiones 0.x → pin 0.29/Cargo.lock, usar documentación versionada y migration guide al actualizar.
- maturin/build metadata cambia → rango <2 y clean-wheel tests en cada actualización.
- Falso zero-copy → llamar copia a sequence→Vec y posponer buffers.
- Panic confundido con excepción → Result como default, auditoría de unwrap y demo aislada.
- Deadlock/UB lógico por detach → owned Rust only, no Python handles, tests concurrentes con timeout.
- `abi3` entendido como universal → separar Python ABI de OS/arch y probar wheel real.
- `abi3t`/free-threading evoluciona → horizonte condicionado, sin support claim.
- Benchmark engañoso → multiple sizes, equality first, no threshold.
- Source-tree import oculta wheel roto → venv/cwd temporales obligatorios.
- Artefactos Cargo ocupan mucho → temp target dir, `.gitignore` y hygiene audit.
- Traducciones divergen → freeze de code/commands/IDs y validator.
- Conflictos de índices → integración serial 23→24→25.

## EXECUTION ORDER

1. Aprobar proposal, confirmar numeración y congelar toolchain/versions/non-goals.
2. Crear preflight y Rust survival; lograr `cargo test` antes de instalar maturin.
3. Implementar `domain.rs` con tests y semántica alineada al oráculo Python.
4. Crear first extension y después el mixed package privado/público.
5. Añadir conversiones, clases, errors y typing en incrementos testables.
6. Auditar panics/unwrap antes de introducir threads.
7. Añadir `Python::detach` solo tras separar owned data de Python handles.
8. Medir después de congelar contrato/paridad.
9. Construir sdist, desempaquetarlo y reconstruir/clean-install el version-specific wheel; luego repetir desde ese source para `abi3-py311` y sus tags.
10. Auditar pedagogía y congelar source refs/código.
11. Traducir español; catalán/sueco/árabe en paralelo.
12. Integrar índices serialmente y ejecutar validación total.

## DEFINITION OF DONE

- `openspec validate add-python-rust-integration-chapter --strict` pasa.
- `openspec show add-python-rust-integration-chapter --json --deltas-only` reconoce todos los requisitos/scenarios.
- Existen cinco variantes y los seis índices enlazan capítulo 25 en orden coordinado.
- Un alumno sin Rust completa setup, ownership básico, dominio probado y primer import siguiendo solo el capítulo.
- `python -B chapter-25-python-rust-integration/examples/faststats-rs/tools/verify.py` crea temporales y ejecuta fmt, clippy, Cargo tests, maturin, pytest, mypy/stubtest, benchmark smoke, wheels y clean installs.
- El módulo base contiene `#[pymodule(gil_used = true)]`; no declara accidentalmente free-threading.
- `python -B -m pytest -p no:cacheprovider -q` pasa para API, parity, errors, classes, threads y artifact smoke.
- Python reference y Rust coinciden en tipos rechazados, 0/1/1,000,000/1,000,001 muestras, límites de entero/float/threshold, banda de anomalía y actualizaciones OnlineStats transaccionales según contrato.
- Input externo no alcanza `unwrap`/`expect`; errores esperados son exceptions estables y panics no forman parte de API.
- El closure `Python::detach` contiene solo datos Rust owned y el test de dos threads termina sin deadlock.
- El rendezvous Rust de tests demuestra entrada concurrente bajo `test-hooks`; sdist/wheels no contienen el hook, y `OnlineStats` permanece GIL-bound y nunca detacha methods.
- `.pyi`/`py.typed` pasan `python -m mypy.stubtest faststats_rs` y un consumer strict; experimental stub generation no es requisito.
- Benchmark comprueba igualdad, mide múltiples tamaños y no impone speedup.
- El sdist se inspecciona y reconstruye en temporal; los wheels version-specific y `abi3-py311` resultantes se inspeccionan e instalan desde venv/cwd temporales compatibles.
- `abi3t`/free-threaded se describe sin claim de soporte base.
- Con root-first, `tools/validate_book.py --plugin chapter-25-python-rust-integration/tools/bookcheck_plugin.py` pasa y detecta ignored artifacts; con Rust-first, standalones equivalentes pasan y se retiran tras migración probada.
- No quedan `.venv`, `target`, wheels, compiled libraries, Cargo temp, caches ni credentials versionados.
- La auditoría de implementación comprueba objectives, context, minimal theory, runnable examples, TODO/hints, happy/edge cases, mistakes, solutions, reflection, headings jerárquicos, links descriptivos y alternativas textuales, y prepara el handoff accesible sin atribuirle aprobación humana.
- La evidencia de scope comprueba ausencia de unsafe, manual C ABI, embedding, async runtime, publication y cross-compilation.
- La aceptación lingüística, técnica/pedagógica, accesible y bidi permanece pendiente en `restore-multilingual-content-parity`; no es requisito para cerrar la implementación técnica de esta change ni queda implícita por su archivo.

## References

- [Rust installation with rustup](https://rust-lang.org/tools/install/)
- [The Rust Book: ownership](https://doc.rust-lang.org/stable/book/ch04-01-what-is-ownership.html)
- [The Rust Book: error handling](https://doc.rust-lang.org/stable/book/ch09-00-error-handling.html)
- [PyO3 0.29 guide](https://pyo3.rs/v0.29.0/)
- [PyO3 parallelism and Python::detach](https://pyo3.rs/main/parallelism)
- [PyO3 building and distribution](https://pyo3.rs/v0.29.0/building-and-distribution)
- [maturin mixed project layout](https://www.maturin.rs/project_layout.html)
- [maturin bindings and stable ABI](https://www.maturin.rs/bindings.html)

## Open Questions

None.
