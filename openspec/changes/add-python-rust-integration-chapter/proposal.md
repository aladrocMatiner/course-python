# Change: Añadir un capítulo avanzado de integración entre Python y Rust

## Why

El curso no ofrece una ruta para construir extensiones Python con Rust ni para comprender cómo ownership, borrowing, errores, GIL y packaging interactúan en la frontera entre ambos lenguajes. Las guías rápidas suelen conseguir un primer import, pero dejan sin resolver API pública, panics, typing, threads, ABI, wheels, pruebas de contrato y medición honesta.

El nuevo capítulo permitirá empezar sin conocimientos de Rust y avanzar paso a paso hasta un paquete mixto profesional: dominio Rust puro, extensión PyO3 privada, fachada Python tipada, tests en ambos lenguajes, ejecución concurrente correcta y wheel verificado en un entorno limpio.

## What Changes

- Crear el capítulo 25, `chapter-25-python-rust-integration/`, como miniunidad con rutas preparación, Rust esencial, integración, profesional y hero.
- Enseñar desde cero el subconjunto de Rust necesario: Cargo, tipos, mutabilidad, `String`/`str`, `Vec`/slices, ownership, borrowing, structs, enums, pattern matching, `Option`, `Result`, módulos y tests.
- Usar Python 3.11+, Rust estable/Edition 2024, PyO3 0.29 y maturin 1.14 mediante un proyecto mixto moderno.
- Construir incrementalmente `faststats_rs`: referencia Python, dominio Rust independiente, binding PyO3 fino, `_native` privado y fachada pública.
- Fijar antes de optimizar un contrato numérico acotado y determinista compartido con la referencia Python: dominio exacto de tipos, máximo de muestras, rangos, orden de cálculo, tolerancia de anomalías y actualizaciones transaccionales.
- Cubrir `#[pymodule]`, `#[pyfunction]`, `#[pyclass]`, conversiones, copias, lifetimes `Python<'py>`/`Bound<'py,T>`, clases inmutables/mutables y typing.
- Diseñar un contrato de errores basado en `Result`, `PyResult` y excepciones Python; prohibir `unwrap`/`expect` sobre datos externos y aislar cualquier demostración de panic.
- Enseñar GIL/thread attachment y `Python::detach` solo alrededor de cómputo Rust que posee sus datos y no toca objetos Python.
- Declarar explícitamente `#[pymodule(gil_used = true)]` en el módulo base PyO3 0.29 para no afirmar soporte free-threaded accidentalmente.
- Añadir benchmarks que muestren overhead, batching y casos donde Rust puede ser más lento, sin speedup contractual.
- Construir un sdist, reconstruir desde él wheels version-specific y `abi3-py311`, inspeccionar contenido/tags e instalar cada artefacto fuera del árbol fuente.
- Explicar free-threaded Python y `abi3t` como horizonte hero condicionado, sin declarar soporte no probado.
- Añadir `cargo fmt`, clippy, `cargo test`, pytest, tests de paridad/threads/artefactos, `.pyi`, `py.typed`, `Cargo.lock` y validación documental.
- Publicar las cinco variantes lingüísticas con paridad completa, Markdown accesible y actualización coordinada de los seis índices raíz.

## Impact

- Affected specs: `teach-python-rust-integration` (nueva capability).
- Affected content: `chapter-25-python-rust-integration/` y los seis índices raíz.
- Related content: capítulos 14, 15, 16, 18, 20 y 22; los capítulos 23/24 serán enlaces opcionales, no prerrequisitos.
- Toolchain: CPython 3.11+, Rust 1.97.0 pinned con Edition 2024, PyO3 0.29 y maturin >=1.14.1,<2; no se promete un MSRV menor no ejecutado.
- Development lock: maturin 1.14.1 y versiones exactas verificadas de pytest/mypy se registrarán en `requirements-dev.lock`, además de `Cargo.lock`.
- Installation: `rustup` y maturin/build/test dependencies pueden requerir Internet inicialmente; maturin se instalará como herramienta/binario Python, no con `cargo install` en la ruta base.
- Compatibility: los layouts y comandos se diseñarán para Linux, macOS y Windows, pero solo se afirmarán targets realmente construidos/probados.
- Active-change coordination: capítulo 23 está reservado para redes y 24 para C++; capítulo 25 no dependerá pedagógicamente de ellos y los índices se reconciliarán serialmente.
- Safety: el alumnado no escribirá `unsafe`, C ABI manual, loaders arbitrarios ni embedding; no habrá publicación, tokens ni secretos.
- Breaking changes: none; se añaden contenido y ejemplos aislados.
