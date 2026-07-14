## TASK BREAKDOWN

## Phase 1: Contrato, toolchain y assets

### Task 1.1: Congelar rutas y trazabilidad

- **Objective:** Mapear requisitos a sesiones, source refs, ejercicios, tests y artefactos antes de escribir contenido largo.
- **Deliverables:** Esqueleto inglés, glosario/concept map, tabla route→session→outcome y matriz requirement→file→validation.
- **Validation:** Ownership/Result se explican antes de PyO3; cada ruta termina en un resultado ejecutable; capítulo 24 no es prerequisito.
- **Risk:** El alcance puede crecer a curso Rust completo; aplicar non-goals y un concepto principal por subsección.
- **Scope:** M
- [x] 1.1 Congelar temario, checkpoints y trazabilidad.

### Task 1.2: Crear preflight y política de versiones

- **Objective:** Diagnosticar Python, venv, rustup, rustc, Cargo, Edition, maturin y target antes de build.
- **Deliverables:** Tabla Linux/macOS/Windows, `rust-toolchain.toml`/`rust-version` 1.97.0, PyO3 0.29, rango maturin y `requirements-dev.lock` exacto para maturin/pytest/mypy.
- **Validation:** Falla con Python <3.11 o si rustup no activa 1.97.0; distingue PATH/linker/venv/maturin/import; no promete MSRV menor no probado; verifica locks exactos.
- **Risk:** `cargo install maturin` eleva MSRV y compile time; ruta base usa tool installation binaria/Python.
- **Scope:** M
- [x] 1.2 Definir preflight, pins y actualización segura.

### Task 1.3: Crear layouts y hygiene

- **Objective:** Separar Rust survival, first extension, mixed capstone, tests, benchmarks y build outputs.
- **Deliverables:** Survival/first/capstone dirs, locks, project `tools/verify.py`, `.gitignore` y root-plugin o fallback hygiene según orden de changes.
- **Validation:** Names coinciden; verify fuerza target/dist/venv/cwd temp fuera del chapter; el owner único de hygiene detecta artifacts incluso ignorados.
- **Scope:** S
- [x] 1.3 Crear el árbol de assets y la política de higiene.

### Task 1.4: Implementar validador documental independiente

- **Objective:** Verificar los cinco idiomas, seis índices y source refs sin depender de otras proposals.
- **Deliverables:** Marker contract; con root gate, `chapter-25-python-rust-integration/tools/bookcheck_plugin.py` `register(registry)` para Rust/Cargo/PyO3/source refs y ningún parser/hygiene genérico local; sin root, standalones temporales con migración explícita.
- **Validation:** Root CLI no se debilita y plugin cubre domain checks; si Rust llega primero, standalones cubren snippets/source refs/ignored scan y equivalence tests pasan antes de reemplazo; nunca quedan dos parsers genéricos mantenidos.
- **Scope:** M
- [x] 1.4 Crear y probar el validador documental.

## Phase 2: Preparación y Rust esencial

### Task 2.1: Explicar modelo nativo y setup

- **Objective:** Relacionar crate, compiler, cdylib, Python module, ABI y wheel con conceptos Python conocidos.
- **Deliverables:** Primeras secciones, instalación rustup/maturin, preflight, `cargo new/check/run/test` y troubleshooting.
- **Validation:** Un learner en entorno limpio identifica toolchain activo y ejecuta programa/test; errores de PATH/venv se reproducen y resuelven sin comandos destructivos.
- **Scope:** M
- [x] 2.1 Redactar y verificar setup/modelo nativo.

### Task 2.2: Enseñar tipos, collections y módulos

- **Objective:** Introducir variables/mutability, functions, `String`/`str`, `Vec`/slices, structs/impl y modules con ejemplos pequeños.
- **Deliverables:** Snippets/mini-projects y ejercicios graduados.
- **Validation:** `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings` y `cargo test`; cada tema incluye happy/edge case, TODO/hint y solution.
- **Scope:** L
- [x] 2.2 Crear la ruta de sintaxis/tipos necesaria para el dominio.

### Task 2.3: Enseñar ownership y borrowing mediante compiler feedback

- **Objective:** Comprender move, immutable/mutable borrow, slices y lifetimes inferidos antes de cruzar Python.
- **Deliverables:** Ejemplos que predicen un compile error, leen sus spans/help y aplican correcciones idiomáticas sin clones indiscriminados.
- **Validation:** Error esperado coincide con explicación; solución compila; learner explica owner, borrower, scope y por qué no hay dangling reference.
- **Risk:** Resolver todo con `.clone()` oculta el modelo; cada clone debe justificar coste/ownership.
- **Scope:** L
- [x] 2.3 Completar el laboratorio guiado de ownership/borrowing.

### Task 2.4: Implementar dominio Rust con `Option` y `Result`

- **Objective:** Fijar semántica y errores de `faststats` sin PyO3.
- **Deliverables:** `src/domain.rs`, `Summary`, `DomainError`, parsing/validation y Cargo unit/integration tests.
- **Validation:** El dominio ya convertido valida length 1..1M, finite abs<=1e150, threshold [0,1e150], input-order mean y second-pass tolerance-band anomaly; built-in Python types/int<=2**53 se prueban en reference/binding tasks 3.3/3.4; `cargo test --locked`; no external-input unwrap/expect.
- **Scope:** L
- [x] 2.4 Implementar y probar el dominio Rust puro.

## Phase 3: Primera integración PyO3

### Task 3.1: Crear el módulo PyO3 mínimo

- **Objective:** Exponer una función simple y entender `cdylib`, `#[pymodule]`, `#[pyfunction]` y `PyResult`.
- **Deliverables:** `examples/01-first-extension/{Cargo.toml,pyproject.toml,src/lib.rs,tests/}`.
- **Validation:** `maturin develop` en venv; external-cwd import; happy/wrong/rebuild; no deprecated `extension-module`; module declara `#[pymodule(gil_used = true)]`.
- **Risk:** Source-tree/shadow import puede producir falso positivo; usar path temporal.
- **Scope:** M
- [x] 3.1 Construir y explicar la primera extensión PyO3.

### Task 3.2: Crear el mixed package `faststats_rs`

- **Objective:** Estabilizar package público con extensión privada y Rust domain reusable.
- **Deliverables:** `pyproject.toml`, Cargo crate cdylib+rlib, `python-source`, module-name `_native`, fachada y `_reference.py`.
- **Validation:** `maturin develop --locked`; `import faststats_rs`; `_native` no se documenta; ausencia/incompatibilidad native tiene diagnóstico claro y no fallback silencioso.
- **Scope:** L
- [x] 3.2 Implementar el layout mixto y la fachada pública.

### Task 3.3: Enseñar conversiones y ownership de frontera

- **Objective:** Mapear primitives, strings, bytes, sequences, optionals y domain values indicando copy/move/borrow.
- **Deliverables:** Tabla Python↔Rust, binding extraction, owned `Vec<f64>` y ejemplos de `Python<'py>`, `Bound<'py,T>` y `Py<T>`.
- **Validation:** Acepta solo built-in int/float para stats y rechaza bool/Fraction/Decimal/NumPy scalar/`__float__`; límites exactos; Unicode/bytes en APIs auxiliares; sequence conversion; ningún borrowed reference escapa del `'py`; no claim zero-copy.
- **Scope:** L
- [x] 3.3 Implementar conversiones y documentar lifetimes PyO3.

### Task 3.4: Verificar paridad Python/Rust antes de ampliar API

- **Objective:** Demostrar que el binding llama al dominio correcto y conserva el contrato.
- **Deliverables:** `tests/test_parity.py` parametrizado y tolerancias numéricas justificadas.
- **Validation:** Reference/native coinciden en Welford input-order y segunda pasada contra final mean, límites, banda `isclose`, happy/edge/exceptions; vector `[-3,-3,-1]`, threshold `0.5`, diferencia streaming/final; integers exactos; test detecta fallback accidental.
- **Scope:** M
- [x] 3.4 Crear la suite inicial de contrato y paridad.

## Phase 4: Ruta profesional

### Task 4.1: Exponer clases Pythonic

- **Objective:** Modelar `Summary` inmutable y `OnlineStats` stateful sin ocultar borrow/mutability rules.
- **Deliverables:** `#[pyclass(frozen)] Summary`, methods/properties/repr, `OnlineStats`, signatures y docs.
- **Validation:** Construction/properties/add/extend/reset/repr; mismo dominio bounded y total<=1M; tipo/rango/finitud/over-limit es transaccional; methods always attached/GIL-held, never detach; class no se presenta como concurrent mutation primitive; no invalid internal reference.
- **Scope:** L
- [x] 4.1 Implementar y explicar clases PyO3.

### Task 4.2: Mapear domain errors y controlar panics

- **Objective:** Convertir errores recuperables a exceptions estables y excluir panic del API contract.
- **Deliverables:** `DomainError` conversions, built-in/custom exception mapping, sección `Result` vs panic y auditoría unwrap/expect.
- **Validation:** User input esperado nunca produce `PanicException`; exception type/message documentado; optional panic demo solo subprocess con exit esperado.
- **Risk:** PyO3 puede convertir un panic, pero eso no lo convierte en control de flujo aceptable.
- **Scope:** M
- [x] 4.2 Implementar el contrato de errores y la auditoría de panics.

### Task 4.3: Añadir typing y documentación de API

- **Objective:** Hacer que editor/type checker y runtime describan el mismo contrato público.
- **Deliverables:** `_native.pyi`, `py.typed`, typed consumer, stubtest config/allowlist estrecha y nota experimental.
- **Validation:** Installed wheel pasa `python -m mypy.stubtest faststats_rs` y `python -m mypy --strict <consumer>`; signatures/defaults/classes agree; allowlist explicada.
- **Scope:** M
- [x] 4.3 Crear y verificar stubs/typing.

### Task 4.4: Completar dual-language tests

- **Objective:** Cubrir dominio Rust, package Python, API, errors, classes y artifact boundary con capas apropiadas.
- **Deliverables:** Cargo tests y pytest contract/error/class/import suites.
- **Validation:** `cargo test --locked`; `python -B -m pytest -p no:cacheprovider -q`; tests no dependen de order/cache y usan extension construida.
- **Scope:** L
- [x] 4.4 Completar la suite Rust+Python profesional.

## Phase 5: Ruta hero — threads, performance y distribution

### Task 5.1: Implementar `Python::detach` correctamente

- **Objective:** Permitir que CPU work progrese en paralelo sin tocar Python dentro del closure detached.
- **Deliverables:** Owned batch function, `py.detach`, owned result y rendezvous `Mutex`/`Condvar` bajo feature `test-hooks` off-by-default en target de aceptación separado.
- **Validation:** No Python/Bound/borrowed handles; dos detached closures deben entrar antes de continuar; serial/GIL-held implementation no pasa; timeout/deadlock/parity; sdist y ambos wheels no contienen feature/API/símbolo/source del hook.
- **Risk:** Re-attaching desde worker o conservar handles puede deadlockear; mantener closure puro y pequeño.
- **Scope:** L
- [x] 5.1 Implementar detach/thread attachment y tests deterministas.

### Task 5.2: Diseñar benchmark y batching

- **Objective:** Medir overhead de extraction/call y cómputo Rust sobre cargas equivalentes.
- **Deliverables:** `benchmarks/benchmark.py`, deterministic data y interpretación por sizes/build profile.
- **Validation:** Equality first, warm-up, repetitions, median, small/medium/large; incluye caso donde Rust puede perder; no fixed speedup.
- **Scope:** M
- [x] 5.2 Crear benchmark educativo y guía de decisión.

### Task 5.3: Construir sdist, wheel version-specific y clean-install

- **Objective:** Empaquetar el mixed project e identificar tags reales antes de Stable ABI.
- **Deliverables:** `verify.py` crea sdist en temporal, lo desempaqueta, reconstruye wheel con temp `CARGO_TARGET_DIR`/out, inspecciona contenido y usa temp venv/cwd smoke.
- **Validation:** Sdist contiene metadata/licencia/README/package/stubs/Rust source/Cargo.lock y no hook/output; wheel se construye desde ese sdist, contiene package/stubs/native; install no-deps; external-cwd tests; pip check; mypy/stubtest; exact target documentado; no workspace target.
- **Scope:** L
- [x] 5.3 Construir, inspeccionar e instalar el wheel específico.

### Task 5.4: Añadir variante `abi3-py311` y horizonte `abi3t`

- **Objective:** Explicar Stable ABI como trade-off verificable, no como wheel universal.
- **Deliverables:** Cargo feature/config separada, `maturin build --features ...`, tag inspection y tabla version-specific/abi3/abi3t.
- **Validation:** `abi3-py311` wheel se reconstruye desde el sdist y se importa en CPython compatibles disponibles; OS/arch explicit; base module mantiene `gil_used=true`; `gil_used=false`/abi3t require separate audited variant and remain no-claim.
- **Risk:** Limited API restringe APIs/optimizations; tests deben ejecutarse contra ambos build modes.
- **Scope:** L
- [x] 5.4 Implementar el laboratorio abi3 y documentar abi3t/free-threading.

### Task 5.5: Consolidar el capstone

- **Objective:** Integrar dominio, binding, classes, errors, typing, detach, tests, benchmark y wheels en una narrativa única.
- **Deliverables:** `faststats_rs` completo y rúbrica final.
- **Validation:** Exact bounded type/size/range/mean/anomaly/tolerance/error/OnlineStats contract; all suites/sdist/build modes/clean installs; learner explains copy/owner/lifetime/error/interpreter/ABI.
- **Scope:** L
- [x] 5.5 Completar el capstone y su evaluación técnica.

## Phase 6: Pedagogía, localización y navegación

> **Frontera de ownership:** las tareas localizadas marcadas en esta change certifican autoría completa y verificación estructural/de dominio a nivel de implementación. No certifican aceptación humana lingüística, técnica/pedagógica localizada, accesibilidad renderizada, bidi ni procedencia. Esas tareas y transiciones de estado permanecen abiertas en `restore-multilingual-content-parity`.

### Task 6.1: Auditar microciclos y carga cognitiva

- **Objective:** Confirmar que la pedagogía está integrada en cada incremento y no añadida al final.
- **Deliverables:** Auditoría de implementación de objectives, prerequisites/glossary, context, theory, prediction, examples, TODO/hints, happy/edge, common mistakes, solutions, checkpoints, reflection y handoff de accesibilidad.
- **Validation:** Un concept principal por subsection; outcomes/rubric por ruta; compiler errors explicados con tono normalizador; headings/links/tables/visuals tienen estructura y alternativa textual accesible.
- **Scope:** L
- [x] 6.1 Ejecutar la auditoría pedagógica completa.

### Task 6.2: Crear versión española

- **Objective:** Traducir con detalle equivalente y links localizados.
- **Deliverables:** `README.es.md`.
- **Validation:** Authoring parity for headings/source refs/commands/code/warnings/exercises/rubric; prerequisites `README.es.md`. Human acceptance remains pending in `maintain-multilingual-course-parity`.
- **Scope:** L
- [x] 6.2 Completar la autoría y revisión de implementación de la versión española.

### Task 6.3: Crear versiones catalana, sueca y árabe

- **Objective:** Mantener contrato técnico en los otros idiomas y RTL usable.
- **Deliverables:** `README.ca.md`, `README.sv.md`, `README.ar.md`.
- **Validation:** Automated structural/domain parity and authoring audit pass; localized links, Arabic wrapper and LTR code remain correct. Manual linguistic, localized technical/pedagogical, rendered-accessibility and bidi acceptance remains pending in `maintain-multilingual-course-parity`.
- **Scope:** XL conjunto; paralelizable por idioma
- [x] 6.3a Completar la autoría y revisión de implementación de la versión catalana.
- [x] 6.3b Completar la autoría y revisión de implementación de la versión sueca.
- [x] 6.3c Completar la autoría y revisión de implementación de la versión árabe con dirección RTL.

### Task 6.4: Integrar seis índices compartidos

- **Objective:** Insertar capítulo 25 antes de apéndices, preservando lower chapters solo cuando estén implementados.
- **Deliverables:** seis `README*.md` raíz.
- **Validation:** No dangling links a pending chapters; preserve 23/24 if present; implemented numeric order; matching languages; English duplicate; manual rebase.
- **Risk:** Tres changes editan los mismos archivos; ejecutar serialmente al final.
- **Scope:** M
- [x] 6.4 Actualizar navegación y reconciliar changes concurrentes.

## Phase 7: Verificación y cierre OpenSpec

### Task 7.1: Ejecutar validación técnica end-to-end

- **Objective:** Demostrar toolchain, domain, binding, package, threads, typing y artifact builds en entorno registrado.
- **Deliverables:** Assets corregidos y resultados de commands en review.
- **Validation:** preflight; capstone `verify.py`; root CLI+Rust plugin o fallbacks temporales equivalentes; diff/status. Verify usa temp dirs y ejecuta fmt/clippy/Cargo/maturin/pytest/mypy/bench/sdist/wheels/installs; fallbacks se retiran tras migration tests.
- **Risk:** No convertir un build local en support matrix; registrar OS/arch/Python/Rust exactos.
- **Scope:** L
- [x] 7.1 Ejecutar y registrar la validación técnica completa.

### Task 7.2: Validar documentación/localización

- **Objective:** Demostrar que cinco variantes y seis índices reflejan los assets probados.
- **Deliverables:** Output limpio del root CLI + Rust plugin cuando existe, o standalone temporal y evidencia de migración; fixes.
- **Validation:** Un solo owner para guards/links/selectors/headings/alt/tables/parity/RTL/hygiene; Rust source refs/commands pasan mediante plugin sin duplicar reglas genéricas.
- **Scope:** M
- [x] 7.2 Ejecutar validación documental y multilingüe.

### Task 7.3: Cerrar trazabilidad de la spec

- **Objective:** Revisar cada requirement/scenario de implementación antes de completar checkboxes y conservar abiertos los gates humanos externos.
- **Deliverables:** Checklist final y review `teach-python-rust-integration`.
- **Validation:** `openspec validate add-python-rust-integration-chapter --strict`; `openspec show ... --json --deltas-only`; evidence for every mandatory implementation scenario y estado pendiente verificable de las decisiones humanas en `restore-multilingual-content-parity`.
- **Scope:** S
- [x] 7.3 Validar OpenSpec y cerrar la checklist.
