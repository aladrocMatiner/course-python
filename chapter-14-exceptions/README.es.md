# Capítulo 14 · Excepciones: de principiante a heroína/hero

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

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

## Prerrequisitos
Capítulos previos recomendados: 8, 11, 12, 13.
Usa CPython 3.11+ en un entorno local desechable y mantén los datos, secretos y servicios fuera de sistemas reales.

---

## 1. `try/except` desde cero

```python runnable
try:
    result = int("abc")
    print(result)
except ValueError:
    print("That was not a valid number")
```

- El bloque `except` sólo se ejecuta si ocurre `ValueError`.
- Un `except:` sin tipo captura incluso `KeyboardInterrupt` y `SystemExit`; evítalo. `except Exception:` captura muchos errores de aplicación, así que úsalo solo en un límite deliberado y prefiere excepciones concretas.

### Capturar múltiples excepciones
```python runnable
import json

try:
    with open("config.txt", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError as exc:
    print("Missing file", exc)
except json.JSONDecodeError as exc:
    print("Invalid JSON", exc)
```

---

## 2. `else` y `finally`

```python runnable
def read_config():
    # Simple example: in real life you would read from a file/JSON
    return {"debug": True}

try:
    data = read_config()
except (FileNotFoundError, ValueError):
    data = {}
else:
    print("Config loaded successfully")
finally:
    print("End of process")
```

- `else` se ejecuta sólo si no hubo excepción.
- `finally` siempre se ejecuta (ideal para liberar recursos, cerrar conexiones).

---

## 3. Lanzar tus propias excepciones (`raise`)

```python runnable
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Denominator cannot be zero")
    return a / b
```

- `raise` detiene la función y propaga la excepción.
- Lanza excepciones estándar cuando describen bien el problema (`ValueError`, `TypeError`).

### `raise` sin argumentos
```python illustrative
try:
    divide(10, 0)
except ZeroDivisionError:
    raise  # re-raise the same exception
```

---

## 4. Excepciones personalizadas

```python runnable
class ConfigError(Exception):
    """Errors related to configuration."""

class MissingConfig(ConfigError):
    pass
```

```python runnable
def load_config(path):
    if not path.exists():
        raise MissingConfig(f"Missing {path}")
    # ...
```

- Heredar de `Exception` (o una subclase apropiada) permite distinguir tus errores del resto.
- Crea jerarquías pequeñas y descriptivas.

---

## 5. Encadenamiento (`raise ... from ...`)

```python illustrative
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Invalid config") from exc
```

- `from exc` conserva el stack trace original, facilitando depuración.

---

## 6. Context managers y limpieza

```python runnable
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("An error occurred", exc)
            return False  # Propagate the exception
```

- Context managers personalizados permiten asegurar limpieza incluso si ocurre un error dentro del `with`.

---

## 7. Pruebas con excepciones

```python illustrative
import pytest

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

- `pytest.raises` confirma que la función lanza la excepción esperada.
- Usa `match="texto"` para comprobar el mensaje.

---

## Ejercicios guiados (con TODOs)
1. **14-1 · Validador robusto**
   ```python todo
   def validate_payload(data):
       # TODO 1: raise ValueError if "email" is missing
       # TODO 2: use try/except to normalize type errors
   ```
   *Pista*: `if "email" not in data: raise ValueError(...)`.

2. **14-2 · CLI resistente**
   ```python todo
   # TODO 1: process files, catch FileNotFoundError and show a friendly message
   # TODO 2: use `sys.exit(1)` when it’s critical
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

3. **14-3 · Excepción personalizada**
   ```python todo
   class InsufficientFunds(Exception):
       pass
   # TODO 1: implement withdraw(amount) that raises InsufficientFunds
   # TODO 2: handle the exception and print the remaining balance
   ```
   *Pista*: empieza por el ejemplo más cercano y verifica un caso válido, un límite y la recuperación antes de mirar la solución.

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
Entender y controlar las excepciones te permite escribir código sólido: seleccionas qué errores manejar, cuáles propagar y cómo comunicar el problema. Las excepciones personalizadas agregan semántica a tus APIs.

## Punto de control y rúbrica
- **Corrección**: el resultado cumple el contrato de la unidad.
- **Legibilidad**: nombres y responsabilidades se entienden a la primera.
- **Errores**: se prueban un caso válido, un límite y una recuperación.
- **Verificación**: los ejemplos y ejercicios se ejecutan en un entorno limpio.
- **Explicación**: puedes justificar las decisiones y sus riesgos.

## Reflexión final
Ser “heroína/hero” en excepciones significa anticipar fallos, diseñar mensajes claros y no temer lanzar errores cuando algo no cumple las reglas. Sigue practicando con tus proyectos y notarás código más confiable y fácil de mantener.
