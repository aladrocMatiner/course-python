# Capítulo 16 · Entornos, dependencias y proyectos reproducibles

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Configurarás entornos virtuales (`venv`), instalarás dependencias con `pip`, distinguirás entre `pyproject.toml`, requisitos, restricciones, snapshots y archivos de bloqueo, y aprenderás a cargar variables de entorno para configuraciones seguras. Practicaremos con un mini proyecto que instala `requests` y utiliza un archivo `.env`.

## Orden pedagógico
1. **Por qué aislar dependencias**.
2. **Crear y activar `venv`**.
3. **Instalar dependencias con `pip`**.
4. **Registrar dependencias con precisión**: declaraciones, versiones fijadas, restricciones, snapshots y bloqueos.
5. **`pyproject.toml` básico**.
6. **Variables de entorno (`os.environ`) y `.env`**.

## Objetivos de aprendizaje
- Crear y activar entornos virtuales en Windows/macOS/Linux.
- Instalar librerías y registrar deliberadamente las dependencias directas.
- Usar `pip freeze` como snapshot específico del intérprete y la plataforma, no como resolutor ni archivo de bloqueo.
- Explicar qué evidencia más sólida aporta un bloqueo resuelto.
- Cargar configuración sensible desde variables de entorno.

## Por qué importa
Sin entornos aislados, un proyecto puede romper otro. Mantener dependencias controladas es la base de cualquier equipo profesional.

### Mini aventura
Piensa en cada entorno virtual como una caja de LEGO con piezas específicas para un proyecto. Si mezclas todas las piezas de todos tus sets, montar un castillo se vuelve caótico. Con `venv` guardas cada set por separado y siempre puedes reconstruir el modelo sin perder piezas ni colores.

## Prerrequisitos
- Comandos básicos de terminal y módulos del capítulo 15.
- CPython 3.11+ con `venv` y `pip`; instalar paquetes requiere red, pero la práctica con variables de entorno es local.

## Predice antes de ejecutar
Antes de crear el entorno, predice a qué intérprete apuntará `python -m pip` antes y después de activarlo. Verifica ambas rutas y explica después por qué una ruta inesperada es un problema de configuración y no un error del paquete.

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
python -m pip install requests
python -c "import requests; print(requests.__version__)"
```

- Cada entorno tiene su propio `pip`.

### `requirements.txt`
```bash illustrative
python -m pip freeze > requirements.txt
git add requirements.txt
```

- Para recrear el snapshot en otro entorno limpio: `python -m pip install -r requirements.txt`.
- `pip freeze` informa de lo instalado con la sintaxis de un archivo de requisitos. No resuelve un entorno nuevo ni crea un bloqueo hermético, y el resultado puede variar entre versiones de Python y sistemas operativos.

### Cinco registros con funciones diferentes
- **Declaración del proyecto:** `[project].dependencies` expresa requisitos directos de ejecución, normalmente como rangos compatibles. No registra todo el grafo resuelto.
- **Versión directa fijada:** `requests==X.Y.Z` fija una dependencia solicitada, pero por sí sola no dice nada sobre todas las dependencias transitivas.
- **Restricción:** un archivo de restricciones limita versiones si otro requisito las necesita; una entrada no provoca su instalación. Ejemplo: `python -m pip install -c constraints.txt requests`.
- **Snapshot del entorno:** `pip freeze` captura los paquetes instalados en el intérprete y la plataforma actuales con formato de requisitos. Es una evidencia útil, pero no el resultado de un resolutor ni un bloqueo multiplataforma.
- **Bloqueo resuelto:** una herramienta de bloqueo registra la resolución completa y su ámbito de validez, a menudo con hashes y marcadores de entorno. Verifica la herramienta y la matriz de destino exactas antes de afirmar que algo es reproducible; el soporte actual de `pip lock` es experimental y su salida se limita a la versión de Python y la plataforma actuales.

---

## 3. Declarar dependencias en `pyproject.toml` (opcional pero moderno)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- Esto declara un requisito directo compatible en los metadatos del paquete. No es un grafo congelado de dependencias transitivas. La verificación de la construcción y de la importación desde otro directorio pertenece al ejemplo instalable `src/<package>` del capítulo 15.

---

## 4. Variables de entorno

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- No incluyas secretos en el repositorio.

### `.env` con `python-dotenv`
```bash illustrative
python -m pip install python-dotenv
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
   # TODO 3: generate a requirements.txt environment snapshot
   ```
   *Pista*: usa `python -m pip` para que la instalación y el snapshot apunten al intérprete activo; registra también su versión de Python y plataforma.

2. **16-2 · Script configurado**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Pista*: llama a `load_dotenv()` y, si falta `API_KEY`, falla con un mensaje claro en vez de usar silenciosamente un valor de producción alternativo.

3. **16-3 · pyproject minimal**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   # TODO 3: explain why this declaration is not a lock file
   ```
   Nota: esto es “nivel extra”. Si estás empezando, `requirements.txt` ya está perfecto.
   *Pista*: mantén mínima la tabla `[project]` y documenta los comandos exactos para crear el entorno e instalar.

---

## Errores comunes
- Olvidar activar el entorno antes de instalar paquetes.
- Llamar bloqueo multiplataforma a una única versión directa fijada o a un snapshot de `pip freeze`.
- Esperar que una entrada de restricciones instale por sí sola un paquete.
- Subir archivos `.env` con secretos (usa `.gitignore`).

---

## Explicación de soluciones
1. **Preparar entorno**: `python -m venv .venv` aísla el proyecto y `python -m pip freeze > requirements.txt` registra un snapshot de ese entorno. Reinstálalo en un entorno limpio con la versión de Python y la plataforma declaradas y verifica las importaciones; no conviertas esa evidencia en una afirmación hermética o multiplataforma.
2. **Script configurado**: `load_dotenv()` permite que `os.environ` lea variables desde archivos locales.
3. **pyproject**: documenta la dependencia directa y las instrucciones de instalación, y aclara que hace falta un bloqueo independiente generado por un resolutor para congelar el grafo completo.

---

## Resumen
Ahora sabes crear entornos, instalar dependencias y mantener la configuración segura mediante variables de entorno.

## Punto de control y rúbrica
- **Corrección**: un entorno nuevo con la versión de Python y la plataforma declaradas instala el registro de dependencias elegido.
- **Legibilidad**: están documentados los comandos de preparación y la versión compatible de Python.
- **Errores**: una variable de entorno ausente falla con claridad y sin revelar secretos.
- **Verificación**: recrea el entorno e importa cada dependencia directa.
- **Explicación**: distingue aislamiento, versiones directas fijadas, restricciones, snapshots de entorno, bloqueos resueltos y almacenamiento de secretos.

## Reflexión final
Estas bases te permitirán compartir proyectos sin “funciona en mi máquina”. Úsalas cada vez que inicies un repositorio nuevo.
