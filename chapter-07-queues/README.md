# Capítulo 7 · Colas y Pilas con `collections.deque`

## Qué vamos a construir
Aprenderás a usar `collections.deque` para modelar colas (FIFO), pilas (LIFO) y ventanas deslizantes. Implementaremos ejemplos inspirados en colas de tareas, buffers de logs y rate limiters ligeros, listos para integrarse en servicios Django o scripts de automatización.

## Orden pedagógico
1. **Recordatorio de listas**: por qué `list.pop(0)` no escala.
2. **Introducción a `deque`**: creación y operaciones básicas.
3. **Cola FIFO**: encolar y desencolar con `append`/`popleft`.
4. **Pila LIFO**: usar `append`/`pop` con `deque` para consistencia.
5. **Ventana deslizante y rate limiting**: `maxlen`, conteo contra tiempo.
6. **Validaciones y pruebas**: asegurar que las estructuras respetan capacidad y orden.

## Learning Objectives
- Crear `deque` con capacidades acotadas y comprender su ventaja frente a listas.
- Implementar colas y pilas con operaciones O(1) en ambos extremos.
- Utilizar `maxlen` para construir buffers rotativos.
- Montar ventanas deslizantes para cálculos o límites de peticiones.
- Probar el comportamiento de tus colas para garantizar orden e invariantes.

## Why This Matters
En sistemas backend es común procesar eventos en orden de llegada o mantener un historial de tamaño fijo. `deque` ofrece operaciones más eficientes que las listas para estos patrones y es parte de la librería estándar (no necesitas dependencias externas).

---

## 1. ¿Por qué no usar solo listas?
`list.pop(0)` requiere desplazar el resto de elementos, lo que lo hace O(n). Para colas de tareas o logs, esto provoca cuellos de botella. `deque` fue diseñado para insertar y extraer en ambos extremos en O(1).

---

## 2. Creación y operaciones básicas

```python
from collections import deque

cola = deque(["task-1", "task-2"])
cola.append("task-3")
print(cola)

ultimo = cola.pop()
print(f"Último extraído: {ultimo}")
```

- Sin argumentos, `deque()` crea una estructura vacía.
- Acepta `maxlen` para delimitar el tamaño máximo.

---

## 3. Cola FIFO (First In, First Out)

```python
from collections import deque

class ColaSoporte:
    def __init__(self):
        self._cola = deque()

    def encolar(self, ticket):
        self._cola.append(ticket)

    def atender(self):
        if not self._cola:
            return None
        return self._cola.popleft()  # O(1)

    def pendientes(self):
        return list(self._cola)
```

- `append` y `popleft` mantienen el orden de llegada.
- Convertir a lista (`list(self._cola)`) facilita mostrar el estado en UI o logs.

---

## 4. Pila LIFO con la misma estructura

```python
from collections import deque

stack = deque()
stack.append("deploy")
stack.append("rollback")

ultimo = stack.pop()
print(ultimo)
```

- Usar `deque` para pilas unifica tus estructuras. Puedes cambiar fácilmente entre comportamientos sin cambiar de tipo.

---

## 5. Ventanas deslizantes, `maxlen` y rate limiting

```python
from collections import deque
from time import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.window = window_seconds
        self.max_requests = max_requests
        self.timestamps = deque()

    def allow(self):
        ahora = time()
        limite = ahora - self.window
        while self.timestamps and self.timestamps[0] < limite:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(ahora)
        return True
```

- Se elimina del frente todo lo que exceda la ventana de tiempo.
- `len(self.timestamps)` te indica cuántas peticiones siguen vigentes; si exceden, rechazas la solicitud.

### Buffers circulares con `maxlen`
```python
logs = deque(maxlen=3)
for evento in ["start", "connect", "query", "disconnect"]:
    logs.append(evento)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validaciones y pruebas

```python
# queues.py
from collections import deque

class ColaAcotada:
    def __init__(self, maxlen):
        if maxlen <= 0:
            raise ValueError("maxlen debe ser positivo")
        self._datos = deque(maxlen=maxlen)

    def push(self, valor):
        if len(self._datos) == self._datos.maxlen:
            raise OverflowError("Cola llena")
        self._datos.append(valor)

    def pop(self):
        if not self._datos:
            raise IndexError("Cola vacía")
        return self._datos.popleft()
```

```python
# tests/test_queues.py
import pytest
from queues import ColaAcotada

def test_cola_acotada_mantiene_orden():
    cola = ColaAcotada(maxlen=2)
    cola.push("a")
    cola.push("b")
    assert cola.pop() == "a"

def test_cola_acotada_no_supera_maxlen():
    cola = ColaAcotada(maxlen=1)
    cola.push("a")
    with pytest.raises(OverflowError):
        cola.push("b")
```

---

## Guided Exercises (con TODOs)
1. **7-1 · Cola de emails**
   ```python
   from collections import deque
   emails = deque()
   # TODO 1: agrega tres correos simulados
   # TODO 2: escribe una función send_next(queue) que haga popleft y devuelva el correo
   # TODO 3: maneja el caso cola vacía devolviendo None
   ```
   *Hint*: Reutiliza la clase `ColaSoporte` como referencia.

2. **7-2 · Buffer de logs acotado**
   ```python
   from collections import deque
   logs = deque(maxlen=5)
   eventos = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: agrega cada evento al deque
   # TODO 2: imprime solo los eventos que quedaron guardados
   # TODO 3: explica por qué maxlen evita usar más memoria
   ```
   *Hint*: Convierte a lista para mostrar el buffer final.

3. **7-3 · Ventana deslizante de métricas**
   ```python
   from collections import deque
   mediciones = deque(maxlen=3)
   # TODO 1: escribe add_measurement(valor) que agregue y devuelva el promedio actual
   # TODO 2: asegúrate de que el promedio se calcule solo con los valores actuales en la ventana
   # TODO 3: agrega una prueba que confirme que la ventana nunca excede maxlen
   ```
   *Hint*: `sum(mediciones)/len(mediciones)` después de añadir.

---

## Common Mistakes
- **Usar listas para colas intensivas** ⇒ rendimiento degradado. Cambia a `deque` cuando uses `pop(0)`/`insert(0)` con frecuencia.
- **Olvidar vaciar elementos antiguos** ⇒ las ventanas temporales crecen indefinidamente. Limpia con un `while` como en `RateLimiter`.
- **Asumir que `maxlen` lanza error** ⇒ por defecto descarta elementos del lado opuesto; si quieres error, comprueba `len` antes de `append` como hicimos en `ColaAcotada`.
- **Compartir la misma `deque` entre hilos sin bloqueo** ⇒ utiliza locks o colas thread-safe (como `queue.Queue`) si hay concurrencia.

---

## Explicación de soluciones
1. **Cola de emails**: `send_next` llama a `popleft()` y devuelve `None` si la cola está vacía, evitando excepciones y haciendo la función idempotente.
2. **Buffer de logs acotado**: iterar eventos y usar `logs.append(evento)` mantiene solo los últimos cinco; `list(logs)` muestra el contenido final para verificar.
3. **Ventana deslizante de métricas**: al agregar cada valor, calculas `promedio = sum(mediciones) / len(mediciones)`; la prueba valida que tras 10 inserciones, `len(mediciones)` siga siendo 3.

---

## Summary
`collections.deque` ofrece una solución eficiente para colas, pilas y ventanas deslizantes. Ahora sabes cuándo preferirla sobre listas, cómo aprovechar `maxlen` y cómo validar su comportamiento con pruebas sencillas.

## Closing Reflection
Con colas robustas puedes construir rate limiters, buffers y procesadores de eventos que escalen mejor. Tienes las bases para integrar estas estructuras en APIs, workers y herramientas de observabilidad, completando la introducción a las estructuras de datos esenciales de Python.
