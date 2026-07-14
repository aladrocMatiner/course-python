# Capítulo 7 · Colas y Pilas con `collections.deque`

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Aprenderás a usar `collections.deque` para modelar colas (FIFO), pilas (LIFO) y ventanas deslizantes. Implementaremos ejemplos inspirados en colas de tareas, buffers de logs y rate limiters ligeros, listos para integrarse en servicios Django o scripts de automatización.

## Orden pedagógico
1. **Recordatorio de listas**: por qué `list.pop(0)` no escala.
2. **Introducción a `deque`**: creación y operaciones básicas.
3. **Cola FIFO**: encolar y desencolar con `append`/`popleft`.
4. **Pila LIFO**: usar `append`/`pop` con `deque` para consistencia.
5. **Ventana deslizante y rate limiting**: `maxlen`, conteo contra tiempo.
6. **Validaciones y pruebas**: asegurar que las estructuras respetan capacidad y orden.

## Objetivos de aprendizaje
- Crear `deque` con capacidad acotada o no acotada y comprender su ventaja frente a las listas.
- Implementar colas y pilas con operaciones O(1) en ambos extremos.
- Utilizar `maxlen` para construir buffers rotativos.
- Montar ventanas deslizantes para cálculos o límites de peticiones.
- Probar el comportamiento de tus colas para garantizar orden e invariantes.

## Prerrequisitos y rutas
Las [listas](../chapter-03-lists/README.es.md) son el único prerrequisito.

- **Ruta esencial · 45–60 min:** secciones 1–4, el ejemplo directo de `maxlen` de la sección 5 y el ejercicio 7-0. Resultado: seguir el estado FIFO, LIFO y de un buffer acotado usando solo operaciones de `deque`. No exige condicionales, funciones, clases, excepciones ni pruebas.
- **Ruta intermedia · 25–35 min:** ejercicio 7-2 después de aprender [bucles](../chapter-10-loops/README.es.md). Resultado: llenar un buffer fijo y explicar qué valor se descarta.
- **Avance profesional opcional · 60–90 min:** la clase, el limitador, la sección 6 y los ejercicios 7-1/7-3. Anticipa [condicionales](../chapter-08-conditionals/README.es.md), [funciones](../chapter-11-functions/README.es.md), [clases](../chapter-12-oop/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pruebas](../chapter-18-testing/README.es.md). Copia los ejemplos completos o sáltalos; no son necesarios para el punto esencial.

## Por qué importa
En sistemas backend es común procesar eventos en orden de llegada o mantener un historial de tamaño fijo. `deque` ofrece operaciones más eficientes que las listas para estos patrones y es parte de la librería estándar (no necesitas dependencias externas).

### Mini aventura
Piensa en una cola de un parque de atracciones: la primera persona que llega es la primera que se sube. Con `deque` haces esa fila de forma rápida: metes gente al final y sacas por delante sin empujar a todo el mundo.

## Predice antes de ejecutar
Antes de las primeras operaciones, dibuja la deque tras cada `append`, `popleft` y `pop`. Predice qué elemento descarta `deque(maxlen=3)` al añadir un cuarto. La predicción del limitador pertenece al avance profesional opcional.

---

## 1. ¿Por qué no usar solo listas?
`list.pop(0)` requiere desplazar el resto de elementos, lo que lo hace O(n). Para colas de tareas o logs, esto provoca cuellos de botella. `deque` fue diseñado para insertar y extraer en ambos extremos en O(1).

---

## 2. Creación y operaciones básicas

```python runnable
from collections import deque

queue = deque(["task-1", "task-2"])
queue.append("task-3")
print(queue)

last = queue.pop()
print(f"Último extraído: {last}")
```

- Sin argumentos, `deque()` crea una estructura vacía.
- Acepta `maxlen` para delimitar el tamaño máximo.

---

## 3. Cola FIFO (primero en entrar, primero en salir)

```python runnable
from collections import deque

queue = deque(["ticket-a", "ticket-b"])
queue.append("ticket-c")
first = queue.popleft()
print(first)
print(list(queue))
```

`append` añade por el extremo de llegada y `popleft` retira el elemento más antiguo. Este es el modelo FIFO esencial completo.

### Avance opcional: envolver la cola en una clase

```python runnable
from collections import deque

class SupportQueue:
    def __init__(self):
        self._queue = deque()

    def enqueue(self, ticket):
        self._queue.append(ticket)

    def handle_next(self):
        if not self._queue:
            return None
        return self._queue.popleft()  # O(1)

    def pending(self):
        return list(self._queue)
```

- `append` y `popleft` mantienen el orden de llegada.
- Convertir a lista (`list(self._queue)`) facilita mostrar el estado en UI o logs.

---

## 4. Pila LIFO con la misma estructura

```python runnable
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

last = stack.pop()
print(last)
```

- Usar `deque` para pilas unifica tus estructuras. Puedes cambiar fácilmente entre comportamientos sin cambiar de tipo.

---

## 5. Ventanas deslizantes, `maxlen` y rate limiting

```python runnable
from collections import deque

logs = deque(["start", "connect", "query"], maxlen=3)
logs.append("disconnect")
print(list(logs))  # ['connect', 'query', 'disconnect']
```

La cuarta inserción descarta el valor más antiguo. Este buffer directo y acotado pertenece a la ruta esencial.

### Avance profesional opcional: limitador basado en tiempo

```python runnable
from collections import deque
from time import monotonic

class RateLimiter:
    def __init__(self, max_requests, window_seconds, clock=monotonic):
        if isinstance(max_requests, bool) or not isinstance(max_requests, int) or max_requests <= 0:
            raise ValueError("max_requests debe ser un entero positivo")
        if isinstance(window_seconds, bool) or not isinstance(window_seconds, (int, float)) or window_seconds <= 0:
            raise ValueError("window_seconds debe ser positivo")
        if not callable(clock):
            raise TypeError("clock debe ser invocable")
        self.window = float(window_seconds)
        self.max_requests = max_requests
        self.timestamps = deque()
        self._clock = clock

    def allow(self):
        now = self._clock()
        cutoff = now - self.window
        while self.timestamps and self.timestamps[0] <= cutoff:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(now)
        return True

ticks = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(ticks))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- Se eliminan los instantes iguales o anteriores al límite; el intervalo activo es `(ahora - ventana, ahora]`.
- Se rechaza cuando `len(self.timestamps) >= max_requests`; el reloj monotónico inyectable hace determinista la prueba del borde.
- El reloj inyectado debe ser invocable y devolver números no decrecientes, como `monotonic()`.

### Buffers circulares con `maxlen`
```python illustrative
logs = deque(maxlen=3)
for event in ["start", "connect", "query", "disconnect"]:
    logs.append(event)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validaciones y pruebas

```python runnable
# queues.py
from collections import deque

class BoundedQueue:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen debe ser positivo")
        self._data = deque(maxlen=maxlen)

    def push(self, value):
        if len(self._data) == self._data.maxlen:
            raise OverflowError("Cola llena")
        self._data.append(value)

    def pop(self):
        if not self._data:
            raise IndexError("Cola vacía")
        return self._data.popleft()
```

```python illustrative
# tests/test_queues.py
import pytest
from queues import BoundedQueue

def test_bounded_queue_keeps_order():
    queue = BoundedQueue(maxlen=2)
    queue.push("a")
    queue.push("b")
    assert queue.pop() == "a"

def test_bounded_queue_respects_maxlen():
    queue = BoundedQueue(maxlen=1)
    queue.push("a")
    with pytest.raises(OverflowError):
        queue.push("b")
```

---

## Ejercicios guiados (con TODOs)
0. **7-0 · Seguimiento esencial de una cola**
   ```python todo
   from collections import deque
   tickets = deque(["A", "B"])
   # TODO 1: añade "C" y retira el ticket más antiguo con popleft
   # TODO 2: usa otra deque como pila y retira el elemento más nuevo con pop
   # TODO 3: crea deque(["one", "two"], maxlen=2), añade "three" y predice el resultado
   ```
   *Pista*: dibuja los dos extremos tras cada operación; no necesitas `if`, funciones, clases ni pruebas.

Los ejercicios restantes son avances opcionales que usan capítulos posteriores.

1. **7-1 · Cola de emails**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: agrega tres correos simulados
   # TODO 2: escribe una función send_next(queue) que haga popleft y devuelva el correo
   # TODO 3: maneja el caso cola vacía devolviendo None
   ```
   *Pista*: reutiliza la clase `SupportQueue` como referencia.

2. **7-2 · Buffer de logs acotado**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   events = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: agrega cada evento al deque
   # TODO 2: imprime solo los eventos que quedaron guardados
   # TODO 3: explica por qué maxlen evita usar más memoria
   ```
   *Pista*: Convierte a lista para mostrar el buffer final.

3. **7-3 · Ventana deslizante de métricas**
   ```python todo
   from collections import deque
   measurements = deque(maxlen=3)
   # TODO 1: escribe add_measurement(value) que agregue y devuelva el promedio actual
   # TODO 2: asegúrate de que el promedio se calcule solo con los valores actuales en la ventana
   # TODO 3: agrega una prueba que confirme que la ventana nunca excede maxlen
   ```
   *Pista*: `sum(measurements)/len(measurements)` después de añadir.

---

## Errores comunes
- **Usar listas para colas intensivas** ⇒ rendimiento degradado. Cambia a `deque` cuando uses `pop(0)`/`insert(0)` con frecuencia.
- **Olvidar vaciar elementos antiguos** ⇒ las ventanas temporales crecen indefinidamente. Limpia con un `while` como en `RateLimiter`.
- **Asumir que `maxlen` lanza error** ⇒ por defecto descarta elementos del lado opuesto; si quieres error, comprueba `len` antes de `append` como hicimos en `BoundedQueue`.
- **Compartir la misma `deque` entre hilos sin bloqueo** ⇒ utiliza locks o colas thread-safe (como `queue.Queue`) si hay concurrencia.

---

## Explicación de soluciones
### Solución esencial 7-0 y recuperación
`append` cambia el extremo derecho, `popleft` el izquierdo, `pop` el derecho y `maxlen` descarta por el extremo opuesto.

```python runnable
from collections import deque
tickets = deque(["A", "B"])
tickets.append("C")
print(tickets.popleft())
stack = deque(["draft", "publish"])
print(stack.pop())
bounded = deque(["one", "two"], maxlen=2)
bounded.append("three")
print(list(bounded))
```

Un `popleft` extra sobre una deque vacía falla con la señal estable `IndexError`:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
from collections import deque
deque().popleft()
```

Recupérate comprobando la longitud dibujada o impresa y ejecutando solo una extracción válida:

```python runnable
from collections import deque
tickets = deque(["A"])
print(tickets.popleft())
```

1. **Cola de emails**: `send_next` llama a `popleft()` y devuelve `None` si la cola está vacía, evitando excepciones y haciendo la función idempotente.
2. **Buffer de logs acotado**: iterar eventos y usar `logs.append(event)` mantiene solo los últimos cinco; `list(logs)` muestra el contenido final para verificar.
3. **Ventana deslizante de métricas**: al agregar cada valor, calculas `average = sum(measurements) / len(measurements)`; la prueba valida que tras muchas inserciones, `len(measurements)` siga siendo 3.

---

## Punto de control y autoevaluación
Completa 7-0, predice cada valor retirado o descartado, ejecuta el caso normal, observa deliberadamente el `IndexError` documentado de la deque vacía y vuelve a ejecutar el caso recuperado. El limitador y su frontera temporal son un avance profesional opcional.

Suma un punto por **FIFO correcto**, **LIFO correcto**, **límite de `maxlen`**, **recuperación del error** y **explicación de ambos extremos**. Con 4/5 completas la ruta esencial; si no, vuelve a las secciones 2–5 y redibuja el estado.

## Resumen
`collections.deque` ofrece una solución eficiente para colas, pilas y ventanas deslizantes. Ahora sabes cuándo preferirla sobre listas, cómo aprovechar `maxlen` y cómo validar su comportamiento con pruebas sencillas.

## Reflexión final
Con colas robustas puedes construir rate limiters, buffers y procesadores de eventos que escalen mejor. Tienes las bases para integrar estas estructuras en APIs, workers y herramientas de observabilidad, completando la introducción a las estructuras de datos esenciales de Python.
