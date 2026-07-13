# Change: Añadir un capítulo avanzado de integración entre Python y C++

## Why

El curso enseña Python, entornos, testing, concurrencia e introspección, pero no explica cómo una aplicación Python llama código nativo ni cómo se construye, depura y distribuye una extensión compilada. Sin esa base, integrar una biblioteca C++ o acelerar un núcleo computacional queda reducido a copiar recetas que ocultan compiladores, ABI, memoria, errores y GIL.

El nuevo capítulo ofrecerá una ruta completa para alumnado sin experiencia previa en C++: empezará con la primera compilación y terminará con un paquete nativo tipado, probado, medido e instalable, además de una introducción controlada al embedding de Python en una aplicación C++.

## What Changes

- Crear el capítulo 24, `chapter-24-python-cpp-integration/`, como miniunidad de varias sesiones con rutas esencial, profesional, avanzada y hero.
- Enseñar el subconjunto de C++ necesario para interoperabilidad: toolchain, tipos, funciones, headers, referencias, `const`, `std::vector`, clases, RAII, smart pointers y excepciones.
- Explicar compilación, linking, librerías dinámicas, carga de módulos, API/ABI de CPython, ABI de C++ y tags de wheel.
- Usar CPython 3.11+, C++17, CMake, pybind11 3.x y scikit-build-core 1.x mediante un `pyproject.toml` moderno.
- Construir incrementalmente `faststats_cpp`: referencia Python, core C++ independiente, binding fino, módulo `_native` privado y fachada Python pública.
- Cubrir conversiones y copias, clases, enums, errores bidireccionales, ownership, lifetimes, políticas de retorno, `keep_alive`, `py::smart_holder` y buffers validados.
- Enseñar callbacks Python desde C++, límites de trampolines, liberación/recuperación del GIL, threads y cierre seguro.
- Añadir benchmarks que separen coste de llamada, conversión, asignación y cómputo, sin prometer una aceleración fija.
- Construir sdist y wheel con PEP 517, inspeccionar tags e instalar el wheel en un entorno limpio fuera del árbol fuente.
- Incluir un laboratorio hero separado donde un ejecutable C++ inicializa CPython e invoca una estrategia Python local confiable.
- Incluir tests del core con CTest, tests de contrato con pytest, pruebas de artefactos, typing con `.pyi`/`py.typed`, depuración y sanitizers opcionales.
- Publicar el capítulo en inglés, español, catalán, sueco y árabe con paridad completa y Markdown accesible, y actualizar los seis índices raíz.

## Impact

- Affected specs: `teach-python-cpp-integration` (nueva capability).
- Affected content: `chapter-24-python-cpp-integration/` y los seis índices raíz.
- Related content: capítulos 11, 12, 14, 15, 16, 18, 20 y 22.
- Toolchain: CPython 3.11+, compilador C++17, CMake >=3.20, pip >=25.3, pybind11 >=3.0.4,<4 y scikit-build-core >=1.0.3,<2; las versiones exactas verificadas se registrarán en los assets.
- Test dependencies: pytest, `build` y mypy/stubtest, bloqueados en un requirements de desarrollo; pip >=25.3 aplicará `constraints-build.txt` al aislamiento PEP 517 mediante `PIP_BUILD_CONSTRAINT`; su instalación inicial puede requerir Internet.
- Compatibility: se usarán APIs portables y comandos diferenciados para Linux, macOS y Windows, pero solo se afirmará compatibilidad en plataformas ejecutadas realmente.
- Active-change coordination: el capítulo 23 está reservado por `add-python-network-programming-chapter`; los índices se integrarán en orden 23 → 24 → 25.
- Security and safety: no se enseñará UB operativo, owning raw pointers, carga de código remoto/no confiable, publicación real ni secretos.
- Breaking changes: none; se añaden contenido y ejemplos aislados.
