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

## Prerrequisitos y avances opcionales
Las [listas](../chapter-03-lists/README.es.md) son el único prerrequisito. Los condicionales, las clases, las dependencias inyectadas, las excepciones y pytest son avances; sigue ahora los patrones y estudia después [condicionales](../chapter-08-conditionals/README.es.md), [funciones](../chapter-11-functions/README.es.md), [clases](../chapter-12-oop/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pruebas](../chapter-18-testing/README.es.md).

## Por qué importa
En sistemas backend es común procesar eventos en orden de llegada o mantener un historial de tamaño fijo. `deque` ofrece operaciones más eficientes que las listas para estos patrones y es parte de la librería estándar (no necesitas dependencias externas).

### Mini aventura
Piensa en una cola de un parque de atracciones: la primera persona que llega es la primera que se sube. Con `deque` haces esa fila de forma rápida: metes gente al final y sacas por delante sin empujar a todo el mundo.

## Predice antes de ejecutar
Antes de las primeras operaciones, dibuja la deque tras cada `append`, `popleft` y `pop`. Para el limitador, predice `[True, True, False, True]` y explica por qué caduca un instante situado exactamente en el límite.

---

## 1. ¿Por qué no usar solo listas?
`list.pop(0)` requiere desplazar el resto de elementos, lo que lo hace O(n). Para colas de tareas o logs, esto provoca cuellos de botella. `deque` fue diseñado para insertar y extraer en ambos extremos en O(1).

---

## 2. Creación y operaciones básicas

```python runnable
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

## 3. Cola FIFO (primero en entrar, primero en salir)

```python runnable
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

```python runnable
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
        ahora = self._clock()
        limite = ahora - self.window
        while self.timestamps and self.timestamps[0] <= limite:
            self.timestamps.popleft()
        if len(self.timestamps) >= self.max_requests:
            return False
        self.timestamps.append(ahora)
        return True

instantes = iter([0.0, 1.0, 2.0, 10.0])
limiter = RateLimiter(2, 10, clock=lambda: next(instantes))
assert [limiter.allow() for _ in range(4)] == [True, True, False, True]
```

- Se eliminan los instantes iguales o anteriores al límite; el intervalo activo es `(ahora - ventana, ahora]`.
- Se rechaza cuando `len(self.timestamps) >= max_requests`; el reloj monotónico inyectable hace determinista la prueba del borde.
- El reloj inyectado debe ser invocable y devolver números no decrecientes, como `monotonic()`.

### Buffers circulares con `maxlen`
```python illustrative
logs = deque(maxlen=3)
for evento in ["start", "connect", "query", "disconnect"]:
    logs.append(evento)
print(list(logs))  # solo conserva los últimos 3 eventos
```

---

## 6. Validaciones y pruebas

```python runnable
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

```python illustrative
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

## Ejercicios guiados (con TODOs)
1. **7-1 · Cola de emails**
   ```python todo
   from collections import deque
   emails = deque()
   # TODO 1: agrega tres correos simulados
   # TODO 2: escribe una función send_next(queue) que haga popleft y devuelva el correo
   # TODO 3: maneja el caso cola vacía devolviendo None
   ```
   *Pista*: Reutiliza la clase `ColaSoporte` como referencia.

2. **7-2 · Buffer de logs acotado**
   ```python todo
   from collections import deque
   logs = deque(maxlen=5)
   eventos = ["start", "init", "load", "ready", "request", "error"]
   # TODO 1: agrega cada evento al deque
   # TODO 2: imprime solo los eventos que quedaron guardados
   # TODO 3: explica por qué maxlen evita usar más memoria
   ```
   *Pista*: Convierte a lista para mostrar el buffer final.

3. **7-3 · Ventana deslizante de métricas**
   ```python todo
   from collections import deque
   mediciones = deque(maxlen=3)
   # TODO 1: escribe add_measurement(valor) que agregue y devuelva el promedio actual
   # TODO 2: asegúrate de que el promedio se calcule solo con los valores actuales en la ventana
   # TODO 3: agrega una prueba que confirme que la ventana nunca excede maxlen
   ```
   *Pista*: `sum(mediciones)/len(mediciones)` después de añadir.

---

## Errores comunes
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

## Punto de control y autoevaluación
Explica FIFO frente a LIFO, por qué `pop(0)` es O(n), cómo descarta valores `maxlen` y por qué un limitador usa `monotonic()` en vez de la hora civil. Prueba después capacidad, entrada vacía y el borde temporal exacto.

- **Preparado**: conservas los invariantes de orden y haces determinista el comportamiento temporal.
- **Casi**: las operaciones funcionan, pero aún necesitas ayuda con capacidad o límites.
- **Repasar**: vuelve a las secciones 1, 3 y 5 y traza cada estado de la deque en papel.

## Resumen
`collections.deque` ofrece una solución eficiente para colas, pilas y ventanas deslizantes. Ahora sabes cuándo preferirla sobre listas, cómo aprovechar `maxlen` y cómo validar su comportamiento con pruebas sencillas.

## Reflexión final
Con colas robustas puedes construir rate limiters, buffers y procesadores de eventos que escalen mejor. Tienes las bases para integrar estas estructuras en APIs, workers y herramientas de observabilidad, completando la introducción a las estructuras de datos esenciales de Python.
