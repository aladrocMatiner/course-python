# Capítulo 20 · Logging y gestión de configuración

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Implementaremos logging con la librería estándar, aprenderemos a configurar distintos niveles (INFO, DEBUG, ERROR), escribir logs en archivos y controlar configuraciones mediante archivos y variables de entorno. También veremos cómo usar `logging.config.dictConfig` y guardar esa configuración en un archivo (por ejemplo, JSON). Como nivel extra (opcional), mencionaremos YAML.

## Orden pedagógico
1. **¿Por qué loggear?**
2. **Configuración básica (`logging.basicConfig`)**.
3. **Niveles y loggers nombrados**.
4. **Handlers/formatters (archivo + consola)**.
5. **Cargar configuración desde archivos (`dictConfig`)**.
6. **Conectar logging con variables de entorno**.

## Objetivos de aprendizaje
- Emitir logs con distintos niveles para depurar y monitorear.
- Configurar formateo y salida (consola, archivo).
- Cambiar niveles según el entorno (dev/prod).
- Centralizar la configuración en un archivo.

## Por qué importa
Los logs son tu caja negra: te dicen qué ocurrió en producción. Configurarlos bien desde el inicio ahorra horas de depuración.

### Mini aventura
Los logs son como la libreta del detective que investiga qué pasó durante la noche. Si anotas cada pista (hora, lugar, nivel de urgencia), al día siguiente podrás reconstruir la historia sin olvidar detalles. Sin esa libreta, todo queda en la memoria y los misterios se vuelven imposibles de resolver.

## Prerrequisitos
- Archivos, excepciones, módulos, JSON y variables de entorno de los capítulos 13–16.
- Un directorio local desechable para que los manejadores de archivo nunca escriban en un registro importante del proyecto.

## Predice antes de ejecutar
Antes del primer ejemplo de logging, predice qué mensajes superan el nivel configurado y qué destino los recibe. Ejecútalo, compara los registros observados con tu predicción e identifica la configuración responsable de cualquier diferencia.

---

## 1. Configuración básica

```python runnable
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.info("Iniciando app")
logging.warning("API lenta")
```

- `level` controla qué mensajes se muestran.
- `format` define la salida.

### `print` vs `logging` (en una frase)
- `print` es para “mostrar algo”.
- `logging` es para “dejar pistas” (y poder filtrar por nivel, guardar en archivo, etc.).

---

## 2. Loggers nombrados

```python illustrative
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

- Usa un logger por módulo para filtrar selectivamente.

---

## 3. Handlers y archivos

```python illustrative
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
console.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console)
logger.addHandler(file_handler)
logger.info("Listo")
```

- Puedes enviar el mismo mensaje a múltiples destinos.

---

## 4. Configuración por diccionario

```python runnable
import logging.config
CONFIG = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
    },
    "formatters": {
        "default": {
            "format": "%(levelname)s %(name)s %(message)s"
        }
    },
    "loggers": {
        "app": {
            "handlers": ["console"],
            "level": "INFO",
        }
    }
}
logging.config.dictConfig(CONFIG)
logger = logging.getLogger("app")
logger.info("Configurado por dict")
```

Este literal es configuración propiedad de la aplicación. `dictConfig` puede resolver clases importables y la clave especial de fábrica `"()"`, por lo que nunca debes pasarle directamente un diccionario arbitrario procedente de una petición, descarga o archivo controlado por quien aprende.

### Cargar un ajuste JSON de la aplicación mediante una lista permitida
```python illustrative
import json
import logging.config
from pathlib import Path

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def build_logging_config(settings):
    if not isinstance(settings, dict) or set(settings) != {"level"}:
        raise ValueError("logging settings must contain only 'level'")
    level = settings["level"]
    if not isinstance(level, str) or level not in ALLOWED_LEVELS:
        raise ValueError("unsupported logging level")
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": level,
            }
        },
        "formatters": {
            "default": {"format": "%(levelname)s %(name)s %(message)s"}
        },
        "root": {"handlers": ["console"], "level": level},
    }

def apply_application_logging_settings(path):
    with Path(path).open(encoding="utf-8") as fh:
        settings = json.load(fh)
    logging.config.dictConfig(build_logging_config(settings))
```

El archivo contiene solo `{"level": "INFO"}`. El código valida ese esquema mínimo y construye por sí mismo el diccionario completo. El límite de la aplicación captura los `OSError`, `JSONDecodeError` o `ValueError` esperados, informa de la ruta propiedad de la aplicación y usa una configuración de consola conocida. Si la configuración procede de una parte no fiable, recházala o copia únicamente valores primitivos expresamente permitidos en una configuración construida por ti; nunca reenvíes campos `class`, `()`, handler, formatter o filter.

Las [pruebas complementarias de configuración de logging fiable](trusted_logging.py) demuestran que un nivel permitido funciona y que se rechazan diccionarios con campos de fábrica o handlers. Desde `chapter-20-logging/`, ejecuta `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

### Rotación acotada de archivos
```python illustrative
from logging.handlers import RotatingFileHandler

rotating = RotatingFileHandler(
    "app.log",
    maxBytes=1_000_000,
    backupCount=3,
    encoding="utf-8",
)
logger.addHandler(rotating)
```

`maxBytes` limita el tamaño de cada archivo y `backupCount` limita las copias de respaldo conservadas.

---

## 5. Configuración vs entornos

```python illustrative
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

- Permite subir/bajar verbosidad sin cambiar código.

Reto rápido: cambia `LOG_LEVEL` y observa cómo aparecen más o menos mensajes.
```bash illustrative
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## Ejercicios guiados (con TODOs)
1. **20-1 · Logger modular**
   ```python todo
   # TODO 1: create one logger per module (dominio, servicios)
   # TODO 2: show different levels
   ```
   *Pista*: usa `logging.getLogger(__name__)` y configura los handlers una sola vez en el punto de entrada.

2. **20-2 · Handler de archivo**
   ```python todo
   # TODO 1: write logs into app.log with rotation (use logging.handlers.RotatingFileHandler)
   ```
   *Pista*: empieza con `RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)`.

3. **20-3 · Ajustes fiables desde JSON (librería estándar)**
   ```python todo
   # TODO 1: save only {"level": "INFO"} in an application-owned config.json
   # TODO 2: validate the allowlisted schema
   # TODO 3: construct the full dict in code and apply it with dictConfig
   ```
   *Pista*: rechaza claves adicionales, especialmente `"()"` y `"class"`; captura los errores esperados de archivo, JSON o valor en el límite de la aplicación y conserva una configuración de consola conocida.

Nivel extra (opcional): hacer lo mismo con YAML requiere instalar `pyyaml`.

---

## Errores comunes
- Llamar `basicConfig` varias veces (sólo toma efecto la primera).
- Loggear información sensible (tokens, contraseñas).
- No incluir timestamps: dificulta reconstruir eventos.
- Tratar JSON arbitrario como configuración de datos inocua: `dictConfig` puede resolver clases y fábricas, por lo que su entrada debe ser fiable o reducirse mediante una lista permitida estricta.

---

## Explicación de soluciones
1. **Logger modular**: `logging.getLogger(__name__)` en cada archivo te da control granular.
2. **Handler de archivo**: `RotatingFileHandler` mantiene tamaño manejable y crea backups.
3. **Ajustes JSON fiables**: carga el archivo de la aplicación, exige exactamente un `level` permitido, construye en código el diccionario conocido de handler y formatter y solo entonces llama a `dictConfig`. Rechaza campos no fiables de handler, clase, filtro y fábrica; captura los errores esperados de archivo, JSON o valor y aplica una configuración de consola conocida.

---

## Resumen
Controlas distintos niveles de logging y puedes enviarlos a múltiples destinos con configuración centralizada.

## Punto de control y rúbrica
- **Corrección**: los niveles, manejadores y formateadores producen los registros previstos.
- **Legibilidad**: los nombres de logger y las claves de configuración corresponden a las responsabilidades de los módulos.
- **Errores**: el JSON inválido o una clave no permitida activa un fallback seguro, ningún diccionario no fiable llega a `dictConfig` y los logs nunca contienen secretos.
- **Verificación**: prueba la salida de consola, el rechazo de campos de fábrica y la rotación acotada en un directorio temporal.
- **Explicación**: explica por qué la configuración pertenece al límite de la aplicación y por qué la entrada de `dictConfig` es un límite de confianza, no simples datos de usuario.

## Reflexión final
Aprender a loggear te prepara para monitorear servicios reales. Empieza simple y expande según la necesidad de tu equipo.
