# Capítulo 20 · Logging y gestión de configuración

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

---

## 1. Configuración básica

```python
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

```python
logger = logging.getLogger("pedidos")
logger.setLevel(logging.DEBUG)
logger.debug("Detalle interno")
```

- Usa un logger por módulo para filtrar selectivamente.

---

## 3. Handlers y archivos

```python
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

```python
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

- Ideal para cargar desde JSON/YAML.

---

## 5. Configuración vs entornos

```python
import os
nivel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=nivel)
```

- Permite subir/bajar verbosidad sin cambiar código.

Reto rápido: cambia `LOG_LEVEL` y observa cómo aparecen más o menos mensajes.
```bash
# macOS/Linux
LOG_LEVEL=DEBUG python tu_script.py
# Windows PowerShell
$env:LOG_LEVEL="DEBUG"; python tu_script.py
```

---

## Ejercicios guiados (con TODOs)
1. **20-1 · Logger modular**
   ```python
   # TODO 1: crea logger por módulo (dominio, servicios)
   # TODO 2: muestra niveles distintos
   ```

2. **20-2 · Handler de archivo**
   ```python
   # TODO 1: escribe logs en app.log con rotación (usar logging.handlers.RotatingFileHandler)
   ```

3. **20-3 · Config desde JSON (librería estándar)**
   ```python
   # TODO 1: guarda CONFIG en un archivo config.json
   # TODO 2: lee el JSON con json.load y aplícalo con dictConfig
   ```

Nivel extra (opcional): hacer lo mismo con YAML requiere instalar `pyyaml`.

---

## Errores comunes
- Llamar `basicConfig` varias veces (sólo toma efecto la primera).
- Loggear información sensible (tokens, contraseñas).
- No incluir timestamps: dificulta reconstruir eventos.

---

## Explicación de soluciones
1. **Logger modular**: `logging.getLogger(__name__)` en cada archivo te da control granular.
2. **Handler de archivo**: `RotatingFileHandler` mantiene tamaño manejable y crea backups.
3. **Config JSON**: `json.load(open("config.json"))` te permite cambiar formatos sin modificar código, usando solo la librería estándar.

---

## Resumen
Controlas distintos niveles de logging y puedes enviarlos a múltiples destinos con configuración centralizada.

## Reflexión final
Aprender a loggear te prepara para monitorear servicios reales. Empieza simple y expande según la necesidad de tu equipo.
