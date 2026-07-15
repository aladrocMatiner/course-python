# Capítulo 7 · Colas y Pilas con `collections.deque`

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Aprenderás a usar `collections.deque` para modelar colas (FIFO), pilas (LIFO) y ventanas deslizantes. Implementaremos ejemplos inspirados en colas de tareas, buffers de logs y rate limiters ligeros, listos para integrarse en servicios Django o scripts de automatización.

## Orden pedagógico
1. **Recordatorio de listas**: por qué `list.pop(0)` no escala.
2. **Puente de imports**: pedir al intérprete seleccionado un módulo de la biblioteca estándar y diagnosticar de forma segura los fallos de búsqueda.
3. **Introducción a `deque`**: creación y operaciones básicas.
4. **Cola FIFO**: encolar y desencolar con `append`/`popleft`.
5. **Pila LIFO**: usar `append`/`pop` con `deque` para mantener la consistencia.
6. **Ventana deslizante y rate limiting**: `maxlen`, conteo contra tiempo.
7. **Validaciones y pruebas**: asegurar que las estructuras respetan capacidad y orden.

## Objetivos de aprendizaje
- Crear `deque` con capacidad acotada o no acotada y comprender su ventaja frente a las listas.
- Distinguir módulos de la biblioteca estándar, locales y de terceros, y usar deliberadamente `import module`, `from module import name` y `python -m module`.
- Diagnosticar un módulo ausente u ocultado por accidente sin instalar paquetes arbitrarios ni modificar Python.
- Implementar colas y pilas con operaciones O(1) en ambos extremos.
- Utilizar `maxlen` para construir buffers rotativos.
- Montar ventanas deslizantes para cálculos o límites de peticiones.
- Probar el comportamiento de tus colas para garantizar orden e invariantes.

## Prerrequisitos y rutas
Las [listas](../chapter-03-lists/README.es.md) y el ciclo de archivo/ejecución del capítulo 1 son los únicos prerrequisitos. El puente de imports siguiente enseña el concepto adicional justo antes de que `deque` lo necesite por primera vez.

- **Ruta esencial · 60–80 min:** sección 1, el puente de imports completo, secciones 2–4, el ejemplo directo de `maxlen` de la sección 5 y ejercicios 7-import/7-0. Resultado: ejecutar un módulo local de la biblioteca estándar de dos formas y seguir el estado FIFO, LIFO y de un buffer acotado usando solo imports y operaciones de `deque`. No exige condicionales, funciones, clases, manejo de excepciones, instalación de paquetes ni pruebas.
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

## Puente de imports: módulos antes de `deque`

Un import pide al **mismo intérprete de Python seleccionado** que ejecuta tu archivo que localice y cargue un módulo. Un módulo suele ser un archivo `.py` o un módulo suministrado por Python. Debes distinguir tres procedencias:

- la **biblioteca estándar** se distribuye con la instalación de Python declarada; `collections` y `random` son ejemplos, así que no los instales con `pip`;
- un **módulo local** es tu propio archivo `.py` importable, como `queue_demo.py`;
- un **paquete de terceros** se instala por separado en un entorno. El capítulo 16 enseña ese flujo; esta ruta esencial no necesita ninguno.

La estructura de paquetes y las API públicas reutilizables se estudian por completo en el [capítulo 15](../chapter-15-modulos/README.es.md). Aquí solo necesitamos los imports imprescindibles para usar `deque` con honestidad.

### Dos formas de importar, dos espacios de nombres

Predice qué forma construye la cola en cada ejemplo completo:

```python runnable
import collections

queue = collections.deque(["A", "B"])
print(queue.popleft())
```

`import collections` vincula el nombre del módulo, por lo que el acceso se cualifica como `collections.deque`. En cambio:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

`from collections import deque` vincula directamente ese nombre público seleccionado. Ambos ejemplos imprimen exactamente `A`. Un `deque(...)` sin cualificar no está disponible después de ejecutar solo `import collections`, porque las dos formas vinculan nombres diferentes.

### Ejecuta un módulo local con el intérprete seleccionado

Guarda este contenido como `queue_demo.py` en un directorio desechable que te pertenezca:

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

Desde ese directorio, cada uno de estos comandos del shell ejecuta el archivo una vez y produce la misma línea:

```bash illustrative
python queue_demo.py
python -m queue_demo
```

La forma `-m` indica a este intérprete que busque el módulo local importable llamado `queue_demo` desde la ubicación de import actual. No incluye `.py`. Este ejemplo de un único archivo todavía no introduce imports relativos de paquetes.

### Predice y observa un módulo ausente

Este módulo inventado para el curso no existe:

```python illustrative
import course_module_that_does_not_exist
```

El contrato ejecutable del capítulo prueba este import en un subproceso aislado. La categoría estable es `ModuleNotFoundError`; el mensaje completo, que depende del entorno, no forma parte del contrato. Diagnostica en este orden:

1. Comprueba la ortografía.
2. Decide si el nombre debería pertenecer a la biblioteca estándar, ser local o ser de terceros.
3. Si es un módulo local, comprueba su nombre de archivo y el directorio de trabajo del shell.
4. Solo si se trata de una dependencia de terceros conocida, sigue más adelante las instrucciones de instalación revisadas de ese proyecto en el capítulo 16.

No respondas a cualquier import ausente instalando desde un índice un paquete con un nombre parecido.

### Shadowing: cuando tu archivo oculta el módulo previsto

La búsqueda de imports de Python puede encontrar un archivo que te pertenece antes que el módulo de biblioteca previsto. Por eso, un archivo o directorio llamado `collections.py`, `typing.py` o `random.py` dentro de la carpeta del ejercicio puede **ocultar** (*shadow*) ese módulo. Un síntoma puede ser una ruta de origen inesperada o un mensaje que indique que el módulo importado no contiene el atributo esperado.

La recuperación es local y reversible:

1. Inspecciona la ruta del módulo encontrada en un proceso de diagnóstico nuevo; por ejemplo, `python -c "import collections; print(collections.__file__)"`.
2. Si esa ruta identifica un archivo conflictivo que creaste en el directorio desechable del ejercicio, cambia solo su nombre por uno del dominio, como `queue_notes.py`.
3. Cierra el REPL anterior si sigue abierto, inicia un proceso de intérprete nuevo en el directorio previsto y vuelve a ejecutar `from collections import deque`.
4. Elimina únicamente archivos de caché creados dentro del directorio desechable del ejercicio si siguen allí; nunca borres ni edites un archivo de la biblioteca estándar.

El ejemplo de cola reparado vuelve a imprimir `A`. Reiniciar importa porque un proceso en ejecución puede conservar módulos que ya ha importado.

### TODO de import guiado, pista y solución explicada

```python todo
# queue_demo.py
# TODO 1: import the standard-library deque name from collections.
# TODO 2: create a deque containing "A" and "B".
# TODO 3: remove and print the oldest value.
# TODO 4: run this file as a path and then with `python -m queue_demo`.
```

**Pista:** la forma directa empieza con `from collections import ...`; `popleft()` elimina por el extremo de llegada. El nombre de archivo aparece en el comando de ruta, pero el sufijo `.py` se omite después de `-m`.

```python runnable
from collections import deque

queue = deque(["A", "B"])
print(queue.popleft())
```

```text output
A
```

Completa el puente de imports cuando las dos formas del shell produzcan esta línea, observes y clasifiques el fallo esperado del módulo inventado y puedas explicar por qué cambiar el nombre de un archivo propio que oculta otro módulo es más seguro que modificar la instalación de Python.

Suma un punto por **import directo correcto**, **explicación correcta de la forma cualificada**, **las dos formas de ejecución local**, **recuperación del módulo ausente/oculto** e **identificación de `collections` como biblioteca estándar**. Un 5/5 completa el puente; el capítulo 15 conserva la explicación avanzada.

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
0. **7-import · Importa y ejecuta `queue_demo`**

   Completa el TODO guiado de imports anterior, ejecuta las dos formas documentadas del shell y explica por qué `collections` no necesita una instalación separada. Conserva todos los archivos en un directorio desechable que te pertenezca.

   *Pista*: tras las dos ejecuciones correctas, usa el bloque del módulo deliberadamente inexistente para practicar el diagnóstico; no lo instales.

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
- **Instalar `collections` desde un índice de paquetes** ⇒ ya forma parte de la biblioteca estándar de Python; verifica en su lugar el intérprete seleccionado.
- **Llamar `collections.py` o `typing.py` a un archivo local** ⇒ puede ocultar el módulo previsto; cambia solo el nombre de tu código local y reinicia el proceso.
- **Escribir `python -m queue_demo.py`** ⇒ el modo módulo usa el nombre importable `queue_demo`, sin el sufijo del archivo.

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
Completa 7-import y 7-0. Ejecuta `queue_demo.py` como ruta y con `-m`, clasifica el `ModuleNotFoundError` documentado, explica la recuperación frente a shadowing, predice cada valor retirado o descartado, observa deliberadamente el `IndexError` de la deque vacía y vuelve a ejecutar el caso recuperado. El limitador y su frontera temporal son un avance profesional opcional.

Suma un punto por **import/ejecución correctos**, **FIFO correcto**, **LIFO correcto**, **límite de `maxlen`** y **las dos explicaciones de recuperación**. Con 5/5 completas la ruta esencial; si no, vuelve al puente de imports o a las secciones 2–5 y repite solo la observación que falta.

## Resumen
`collections.deque` ofrece una solución eficiente de la biblioteca estándar para colas, pilas y ventanas deslizantes. Ahora sabes cómo la resuelve el intérprete seleccionado, cuándo preferirla sobre listas, cómo aprovechar `maxlen` y cómo validar su comportamiento con pruebas sencillas.

## Reflexión final
¿Qué pregunta de diagnóstico harías primero ante un import ausente: ortografía, procedencia del módulo, directorio de trabajo o instalación? Explica por qué la respuesta depende de que el módulo pertenezca a la biblioteca estándar, sea local o sea de terceros. Con colas robustas puedes construir rate limiters, buffers y procesadores de eventos sin perder de vista una resolución de módulos comprensible y recuperable.
