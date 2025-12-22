# Capítulo 16 · Entornos, dependencias y proyectos reproducibles

## Qué vamos a construir
Configurarás entornos virtuales (`venv`), instalarás dependencias con `pip`, manejarás archivos `requirements.txt` / `pyproject.toml` y aprenderás a cargar variables de entorno para configuraciones seguras. Practicaremos con un mini proyecto que instala `requests` y utiliza variables `.env`.

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

---

## 1. Crear y activar `venv`

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- `(.venv)` aparecerá en la terminal indicando que estás dentro del entorno.
- `deactivate` para salir.

---

## 2. Instalar paquetes

```bash
pip install requests
python -c "import requests; print(requests.__version__)"
```

- Cada entorno tiene su propio `pip`.

### `requirements.txt`
```bash
pip freeze > requirements.txt
git add requirements.txt
```

- Para instalar en otra máquina: `pip install -r requirements.txt`.

---

## 3. `pyproject.toml` (opcional pero moderno)

```toml
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

```python
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- No incluyas secretos en el repositorio.

### `.env` con `python-dotenv`
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

- Crea un `.env` con `API_KEY=valor` y agrégalo a `.gitignore`.

---

## Ejercicios guiados (con TODOs)
1. **16-1 · Preparar entorno**
   ```bash
   # TODO 1: crea .venv y actívalo
   # TODO 2: instala requests y python-dotenv
   # TODO 3: genera requirements.txt
   ```

2. **16-2 · Script configurado**
   ```python
   # TODO 1: crea config.py que cargue variables desde .env
   # TODO 2: usa os.environ para obtener API_KEY
   ```

3. **16-3 · pyproject minimal**
   ```
   # TODO 1: crea pyproject.toml con dependencias básicas
   # TODO 2: documenta en README cómo instalar
   ```

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

## Reflexión final
Estas bases te permitirán compartir proyectos sin “funciona en mi máquina”. Úsalas cada vez que inicies un repositorio nuevo.
