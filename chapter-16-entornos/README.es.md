# Capítulo 16 · Entornos, dependencias y proyectos reproducibles

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Configurarás entornos virtuales (`venv`), instalarás dependencias con `pip`, manejarás archivos `requirements.txt` / `pyproject.toml` y aprenderás a cargar variables de entorno para configuraciones seguras. Practicaremos con un mini proyecto que instala `requests` y utiliza un archivo `.env`.

## Orden pedagógico
1. **Por qué aislar dependencias**.
2. **Crear y activar `venv`**.
3. **Instalar dependencias con `pip`**.
4. **Congelar versiones (`requirements.txt`)**.
5. **`pyproject.toml` básico**.
6. **Variables de entorno (`os.environ`) y `.env`**.

## Objetivos de aprendizaje
- Crear y activar entornos virtuales en Windows/macOS/Linux.
- Instalar librerías y fijar versiones para reproducir proyectos.
- Exportar/importar dependencias con `pip freeze`.
- Cargar configuración sensible desde variables de entorno.

## Por qué importa
Sin entornos aislados, un proyecto puede romper otro. Mantener dependencias controladas es la base de cualquier equipo profesional.

### Mini aventura
Piensa en cada entorno virtual como una caja de LEGO con piezas específicas para un proyecto. Si mezclas todas las piezas de todos tus sets, montar un castillo se vuelve caótico. Con `venv` guardas cada set por separado y siempre puedes reconstruir el modelo sin perder piezas ni colores.

## Prerrequisitos
Capítulos previos recomendados: 15.
Usa CPython 3.11+ en un entorno local desechable y mantén los datos, secretos y servicios fuera de sistemas reales.

---

## 1. Crear y activar `venv`

```bash illustrative
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- `(.venv)` aparecerá en la terminal indicando que estás dentro del entorno.
- `deactivate` para salir.

Si te lías con qué `pip` estás usando, este truco siempre funciona:
```bash illustrative
python -m pip install requests
```
Así te aseguras de instalar en el Python que estás ejecutando.

---

## 2. Instalar paquetes

```bash illustrative
pip install requests
python -c "import requests; print(requests.__version__)"
```

- Cada entorno tiene su propio `pip`.

### `requirements.txt`
```bash illustrative
pip freeze > requirements.txt
git add requirements.txt
```

- Para instalar en otra máquina: `pip install -r requirements.txt`.

---

## 3. `pyproject.toml` (opcional pero moderno)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- Herramientas como `pip-tools`, `poetry` o `pdm` usan este formato.

---

## 4. Variables de entorno

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- No incluyas secretos en el repositorio.

### `.env` con `python-dotenv`
```bash illustrative
pip install python-dotenv
```

```python illustrative
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

- Crea un `.env` con `API_KEY=valor` y agrégalo a `.gitignore`.

Ejemplo de `.gitignore` típico:
```gitignore illustrative
.venv/
.env
__pycache__/
```

---

## Ejercicios guiados (con TODOs)
1. **16-1 · Preparar entorno**
   ```bash todo
   # TODO 1: create .venv and activate it
   # TODO 2: install requests and python-dotenv
   # TODO 3: generate requirements.txt
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

2. **16-2 · Script configurado**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

3. **16-3 · pyproject minimal**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.
   Nota: esto es “nivel extra”. Si estás empezando, `requirements.txt` ya está perfecto.

---

## Errores comunes
- Olvidar activar el entorno antes de instalar paquetes.
- No versionar `requirements.txt` y perder el control de versiones.
- Subir archivos `.env` con secretos (usa `.gitignore`).

---

## Explicación de soluciones
1. **Preparar entorno**: `python -m venv .venv` y `pip freeze > requirements.txt` aseguran reproducibilidad.
2. **Script configurado**: `load_dotenv()` permite que `os.environ` lea variables desde archivos locales.
3. **pyproject**: documentar las instrucciones (`pip install -e .`) guía al equipo para instalar igual.

---

## Resumen
Ahora sabes crear entornos, instalar dependencias y mantener la configuración segura mediante variables de entorno.

## Punto de control y rúbrica
- **Corrección**: el resultado cumple el contrato de la unidad.
- **Legibilidad**: nombres y responsabilidades se entienden a la primera.
- **Errores**: se prueban un caso válido, un límite y una recuperación.
- **Verificación**: los ejemplos y ejercicios se ejecutan en un entorno limpio.
- **Explicación**: puedes justificar las decisiones y sus riesgos.

## Reflexión final
Estas bases te permitirán compartir proyectos sin “funciona en mi máquina”. Úsalas cada vez que inicies un repositorio nuevo.
