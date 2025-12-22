# Capítulo 14 · Excepciones: de principiante a heroína/hero

## Qué vamos a construir
Dominarás el sistema de excepciones de Python: detectar errores, manejarlos con `try/except`, lanzar tus propias excepciones, crear clases personalizadas y diseñar APIs robustas que informan claramente qué salió mal. Practicaremos patrones profesionales para validar entradas, envolver llamadas peligrosas y limpiar recursos.

## Orden pedagógico
1. **Modelo mental**: excepciones interrumpen el flujo normal.
2. **`try/except` básico**: atrapar errores conocidos.
3. **`else` y `finally`**: bloques complementarios.
4. **`raise`**: lanzar tus propias excepciones.
5. **Excepciones personalizadas**: `class` que heredan de `Exception`.
6. **Encadenar excepciones (`raise ... from ...`)**.
7. **Context managers y limpieza**.
8. **Pruebas y ejercicios**.

## Objetivos de aprendizaje
- Identificar qué excepciones pueden ocurrir y capturarlas selectivamente.
- Utilizar `else` y `finally` para controlar flujos secundarios y limpieza.
- Crear y lanzar excepciones personalizadas para describir errores de dominio.
- Encadenar excepciones para no perder el contexto original.
- Probar funciones que deben lanzar o manejar errores.

## Por qué importa
Ignorar excepciones provoca fallos silenciosos o mensajes crípticos. Un buen manejo de errores da confianza a tu API y facilita depurar problemas en producción.

### Mini aventura
Las excepciones son como las señales de tráfico y los airbags: no están para fastidiarte, están para avisarte y protegerte cuando algo sale mal. Si aprendes a leerlas y responder, tu programa se vuelve mucho más seguro.

---

## 1. `try/except` desde cero

```python
try:
    resultado = int("abc")
    print(resultado)
except ValueError:
    print("No era un número válido")
```

- El bloque `except` sólo se ejecuta si ocurre `ValueError`.
- Si no especificas la excepción, capturas todo (`except Exception:`), pero evita hacerlo salvo en casos muy controlados.

### Capturar múltiples excepciones
```python
import json

try:
    with open("config.txt", encoding="utf-8") as archivo:
        datos = json.load(archivo)
except FileNotFoundError as exc:
    print("Archivo faltante", exc)
except json.JSONDecodeError as exc:
    print("JSON inválido", exc)
```

---

## 2. `else` y `finally`

```python
def leer_config():
    # Ejemplo simple: en la vida real leerías de un archivo/JSON
    return {"debug": True}

try:
    datos = leer_config()
except (FileNotFoundError, ValueError):
    datos = {}
else:
    print("Config cargada correctamente")
finally:
    print("Fin del proceso")
```

- `else` se ejecuta sólo si no hubo excepción.
- `finally` siempre se ejecuta (ideal para liberar recursos, cerrar conexiones).

---

## 3. Lanzar tus propias excepciones (`raise`)

```python
def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("El denominador no puede ser cero")
    return a / b
```

- `raise` detiene la función y propaga la excepción.
- Lanza excepciones estándar cuando describen bien el problema (`ValueError`, `TypeError`).

### `raise` sin argumentos
```python
try:
    dividir(10, 0)
except ZeroDivisionError:
    raise  # vuelve a lanzar la misma excepción
```

---

## 4. Excepciones personalizadas

```python
class ConfigError(Exception):
    """Errores relacionados con la configuración."""

class MissingConfig(ConfigError):
    pass
```

```python
def cargar_config(path):
    if not path.exists():
        raise MissingConfig(f"No existe {path}")
    # ...
```

- Heredar de `Exception` (o una subclase apropiada) permite distinguir tus errores del resto.
- Crea jerarquías pequeñas y descriptivas.

---

## 5. Encadenamiento (`raise ... from ...`)

```python
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Config inválida") from exc
```

- `from exc` conserva el stack trace original, facilitando depuración.

---

## 6. Context managers y limpieza

```python
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("Ocurrió un error", exc)
            return False  # Propaga la excepción
```

- Context managers personalizados permiten asegurar limpieza incluso si ocurre un error dentro del `with`.

---

## 7. Pruebas con excepciones

```python
import pytest

def test_dividir_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

- `pytest.raises` confirma que la función lanza la excepción esperada.
- Usa `match="texto"` para comprobar el mensaje.

---

## Ejercicios guiados (con TODOs)
1. **14-1 · Validador robusto**
   ```python
   def validar_payload(data):
       # TODO 1: lanza ValueError si falta "email"
       # TODO 2: usa try/except para normalizar errores de tipo
   ```
   *Hint*: `if "email" not in data: raise ValueError(...)`.

2. **14-2 · CLI resistente**
   ```python
   # TODO 1: procesa archivos, captura FileNotFoundError y muestra mensaje amigable
   # TODO 2: usa `sys.exit(1)` cuando sea crítico
   ```

3. **14-3 · Excepción personalizada**
   ```python
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implementa withdraw(amount) que lance InsufficientFunds
   # TODO 2: maneja la excepción mostrando el saldo restante
   ```

---

## Errores comunes
- Capturar excepciones demasiado genéricas y ocultar el problema real.
- No volver a lanzar (`raise`) cuando no puedes resolver el error.
- Ignorar el bloque `finally` y dejar recursos abiertos.
- Lanzar excepciones con mensajes vagos; siempre incluye contexto.

---

## Explicación de soluciones
1. **Validador robusto**: `try: email = data["email"]` y `except KeyError as exc: raise ValueError("Falta email") from exc`. Los mensajes amigables facilitan la depuración.
2. **CLI resistente**: `try/except FileNotFoundError` muestra cuál archivo falló y sale con código 1 para que otros scripts lo detecten.
3. **Excepción personalizada**: `withdraw` verifica el saldo y lanza `InsufficientFunds`; el bloque `try/except` superior informa al usuario sin mostrar un stack trace crudo.

---

## Resumen
Entender y controlar las excepciones te permite escribir código sólido: seleccionas qué errores manejar, cuáles propagarse y cómo comunicar el problema. Las excepciones personalizadas agregan semántica a tus APIs.

## Reflexión final
Ser “heroína/hero” en excepciones significa anticipar fallos, diseñar mensajes claros y no temer lanzar errores cuando algo no cumple las reglas. Sigue practicando con tus proyectos y notarás código más confiable y fácil de mantener.
