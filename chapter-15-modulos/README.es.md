# Capítulo 15 · Módulos, paquetes y organización del código

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Aprenderás a dividir tu proyecto en archivos y carpetas, importar funciones/clases, crear paquetes reutilizables y evitar importaciones circulares. Simularemos una mini aplicación con módulos `dominio`, `servicios` y `cli` para que entiendas cómo se conectan.

## Orden pedagógico
1. **Modelo mental**: archivo `.py` = módulo.
2. **Importaciones básicas**: `import`, `from ... import ...`.
3. **Carpetas como paquetes**: `__init__.py` e importaciones relativas.
4. **Estructura instalable `src/<package>`**.
5. **Evitar ciclos de importación**.
6. **Empaquetado ligero** (`if __name__ == "__main__"`).

## Objetivos de aprendizaje
- Organizar código en módulos coherentes.
- Importar funciones y clases desde otros archivos sin duplicar lógica.
- Crear paquetes con `__init__.py` y comprender rutas relativas.
- Detectar y resolver importaciones circulares.
- Preparar un módulo principal ejecutable.
- Construir, instalar e importar un paquete fuera de su directorio fuente.

## Por qué importa
Los proyectos reales no caben en un solo archivo. Separar responsabilidades facilita pruebas, reutilización y colaboración.

### Mini aventura
Imagina que tu juego favorito está hecho por equipos distintos: quienes crean personajes, quienes diseñan niveles y quienes programan la música. Si todo estuviera en un único archivo sería imposible colaborar. Los módulos son como habitaciones ordenadas dentro de una misma casa; cada persona sabe dónde dejar su trabajo y es fácil encontrarlo después.

### Cómo practicar este capítulo (muy simple)
1. Crea dos archivos: `saludos.py` y `app.py` (en la misma carpeta).
2. Ejecuta `python app.py`.
3. Si aparece un error, lee el nombre del error y la línea: es normal al aprender.

## Prerrequisitos
- Funciones, clases, importaciones de la biblioteca estándar y navegación básica por la terminal.
- Un entorno local con CPython 3.11+ y permiso para crear una carpeta de proyecto desechable.

## Predice antes de ejecutar
Antes de importar el primer módulo, predice qué archivo proporciona `hola` y qué directorio debe poder encontrar Python. Después de ejecutar el ejemplo, inspecciona la ruta del módulo importado y compárala con tu predicción.

---

## 1. Módulos básicos
`saludos.py`
```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python illustrative
import saludos
print(saludos.hola("Taha"))
```

Salida esperada:
```text illustrative
Hola Taha!
```

Reto rápido: cambia `"Taha"` por tu nombre y vuelve a ejecutar.

### `from ... import ...`
```python illustrative
from saludos import hola
print(hola("Frej"))
```

- Evita `import *`, dificulta saber qué viene de dónde.

---

## 2. Paquetes
Estructura:
```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`
```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`
```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`
```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

Ejecuta:
```bash illustrative
python main.py
```

Salida esperada:
```text illustrative
90.0
```

- `.` indica importación relativa (mismo paquete).
- `__init__.py` puede estar vacío, sirve para que Python entienda que es un paquete.

---

## 3. Nivel extra: un layout `src` instalable (opcional)
Si estás empezando, puedes saltarte esta parte. En un layout `src` real, `src/` solo es un contenedor: el paquete importable vive un nivel por debajo. Aquí el paquete es `mi_app`, así que el código importa `mi_app`, nunca `src`.

```text illustrative
project/
├── pyproject.toml
├── src/
│   └── mi_app/
│       ├── __init__.py
│       ├── domain.py
│       └── cli.py
└── tests/
```

`pyproject.toml` indica al backend que descubra paquetes bajo `src`:

```toml illustrative
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "course-mi-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
```

### Construir, instalar y verificar desde otro lugar
En un entorno virtual nuevo instala el proyecto y cambia deliberadamente el directorio de trabajo antes de importar. Así demuestras que Python usa la distribución instalada y no el checkout por accidente:

```bash illustrative
# macOS/Linux (outside the checkout):
python -m venv /tmp/course-mi-app-venv
source /tmp/course-mi-app-venv/bin/activate
# Windows PowerShell alternative:
# python -m venv "$env:TEMP\course-mi-app-venv"
# & "$env:TEMP\course-mi-app-venv\Scripts\Activate.ps1"
# Run the remaining commands from project/
python -m pip install .
python -m unittest discover -s tests -v
python -c "import os, tempfile; os.chdir(tempfile.mkdtemp()); import mi_app; print(mi_app.__name__)"
```

La ruta del entorno queda deliberadamente fuera del checkout; desactívalo y bórralo al terminar. `pip install .` usa aislamiento PEP 517 y puede necesitar obtener `setuptools>=68` más el requisito `wheel` declarado por el backend desde un índice o una caché ya poblada. Para un laboratorio sin red, prepara antes wheels revisados y compatibles para ambas entradas de build. Usa `--no-build-isolation` solo si el backend y sus requisitos de build ya están instalados y has comprobado sus versiones; ese fallback no demuestra un build aislado.

El import debe imprimir `mi_app`. Hay una copia completa en [el ejemplo instalable `src` del capítulo 15](examples/src-layout/). Si falla, comprueba el intérprete con `python -m pip --version`, reinstala en ese entorno y confirma que existe `src/mi_app/__init__.py`. No añadas el checkout a `PYTHONPATH`: ocultaría el error de empaquetado.

Quien mantenga el libro puede ejecutar `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py` desde la raíz del repositorio. El verificador construye una copia temporal con PEP 517, inspecciona el contenido y los metadatos del wheel, instala ese wheel exacto en un segundo entorno y ejecuta `pip check`, el entry point instalado, la prueba y un import desde un directorio ajeno antes de borrar sus artefactos temporales. En un laboratorio sin red, pasa `--wheelhouse RUTA` con distribuciones revisadas y compatibles de `setuptools>=68` y `wheel`; no aprovisionar cualquiera de las dos es un fallo de prerrequisito, no un build aislado correcto.

---

## 4. Evitar importaciones circulares

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

Si te pasa, no es “culpa tuya”: es un tipo de problema normal cuando crecen los proyectos.

Soluciones:
- Mueve la lógica compartida a un módulo independiente.
- Usa importaciones locales dentro de funciones para romper el ciclo:
```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```
(La idea es que `aplicar_descuento` viva en un archivo como `servicios/descuentos.py`.)

---

## 5. Punto de entrada

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

- Permite ejecutar `python cli.py` o importar `main` en pruebas sin que se ejecute automáticamente.

---

## Ejercicios guiados (con TODOs)
1. **15-1 · Separar dominio y servicios**
   ```python todo
   # TODO 1: create src/mi_app/dominio.py with class Producto
   # TODO 2: create src/mi_app/precios.py and use Producto
   # TODO 3: add pyproject.toml and install the distribution in a clean venv
   ```
   Extra: añade un método `aplicar_descuento(porcentaje)` en `Producto`.
   Pista: `src` no es el paquete; haz explícito `mi_app` con `__init__.py` e importa los objetos de dominio en una sola dirección.

2. **15-2 · CLI modular**
   ```python todo
   # TODO 1: create src/mi_app/cli.py that imports functions from servicios
   # TODO 2: after installation, run python -m mi_app.cli to validate the import path
   ```
   Pista: si te sale `ModuleNotFoundError`, asegúrate de ejecutar desde la carpeta correcta.

3. **15-3 · Resolver ciclo**
   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   Edge case: escribe un test que importe ambos módulos para confirmar que ya no hay ciclo.
   Pista: mueve la dependencia compartida más pequeña a `utils.py` e inicia después un proceso de Python nuevo para probar la importación.

---

## Errores comunes
- Importar con rutas relativas incorrectas (`from .. import` sin `__init__.py`).
- Duplicar código en varios módulos en lugar de importarlo.
- Ejecutar desde directorios diferentes y romper las rutas (usa `python -m`).
- Poner `__init__.py` directamente bajo `src/` e importar `src`: instala el paquete real bajo `src/<package>/`.

---

## Explicación de soluciones
1. **Dominio vs servicios**: coloca ambos módulos bajo `src/mi_app/`, configura el descubrimiento en `pyproject.toml`, instala en un entorno nuevo y verifica `import mi_app` desde un directorio temporal.
2. **CLI modular**: `mi_app/cli.py` solo orquesta; la lógica vive en `servicios`. Ejecutar `python -m mi_app.cli` después de instalar prueba la ruta de importación del paquete y sigue siendo fácil de testear.
3. **Resolver ciclo**: mover funciones comunes a `utils` elimina dependencias circulares y clarifica capas.

---

## Resumen
Separar el código en módulos y paquetes mantiene tu proyecto ordenado. Ahora puedes importar sólo lo necesario y crear puntos de entrada limpios.

## Punto de control y rúbrica
- **Corrección**: la distribución se instala y el paquete real se importa fuera de la raíz del proyecto.
- **Legibilidad**: cada nombre de módulo refleja una sola responsabilidad.
- **Manejo de errores**: los fallos de importación incluyen un comando reproducible y una comprobación de recuperación.
- **Verificación**: el módulo y la importación desde otro directorio funcionan en un proceso nuevo.
- **Explicación**: describe por qué la dirección de las dependencias evita ciclos.

## Reflexión final
Piensa siempre en “¿dónde vive esta pieza de lógica?”. Tener módulos claros te prepara para proyectos más grandes y frameworks como Django.
