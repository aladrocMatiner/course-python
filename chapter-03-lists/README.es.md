# Capítulo 3 · Introducción a las listas

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
En este capítulo aprenderás qué es una lista, cómo acceder a cada elemento y cómo modificarlos, ordenarlos y protegerte de errores comunes. Además, practicaremos los métodos esenciales (`append`, `insert`, `pop`, `remove`, `sort`) y escribiremos pruebas breves que garanticen el comportamiento esperado de nuestras funciones.

## Orden pedagógico
1. **Introducción**: modelo mental de una lista y por qué los corchetes (`[]`) importan.
2. **Acceso y uso**: índices, `-1` para el final y cómo reutilizar valores dentro de mensajes.
3. **Modificar/agregar/quitar**: `append`, `insert`, `del`, `pop`, `remove` y cuándo elegir cada uno.
4. **Organizar**: `sort`, `sorted`, `reverse`, `len` y cálculos rápidos.
5. **Evitar errores**: detectar `IndexError` y cómo prevenirlos.
6. **Pruebas y ejercicios guiados**: refuerzan la manipulación segura de listas.

## Objetivos de aprendizaje
- Definir una lista y acceder a sus elementos por posición o mediante índices negativos.
- Modificar elementos existentes y añadir/quitar elementos según el contexto del programa.
- Reordenar listas temporal o permanentemente y medir su longitud.
- Evitar `IndexError` mediante validaciones y uso correcto de `len()` y `-1`.
- En la ruta profesional opcional, escribir pruebas pequeñas que confirmen que nuestras funciones manipulan listas sin efectos secundarios.

## Prerrequisitos y rutas
- **Prerrequisito:** completa el checkpoint del [capítulo 2](../chapter-02-variables/README.es.md). La ruta esencial usa variables, cadenas, números y llamadas directas a `print`.
- **Ruta esencial · 55–70 min:** creación, acceso, mutación, eliminación, ordenación, longitud y ejercicio 3-11. Resultado: mantener una lista de invitados o tareas y recuperarse de un índice inválido.
- **Ruta intermedia · 30–40 min:** completa los ejercicios 3-4 a 3-10 y explica qué operaciones mutan la lista original.
- **Preview profesional opcional · 40–50 min:** comienza en “Mini pruebas automáticas” y sigue con los TODO guiados. Anticipa [condicionales](../chapter-08-conditionals/README.es.md), [bucles](../chapter-10-loops/README.es.md), [funciones](../chapter-11-functions/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pytest](../chapter-18-testing/README.es.md). Puedes copiar los ejemplos completos o saltar directamente a “Errores comunes”; no son necesarios para el checkpoint esencial.

## Por qué importa
Sin listas sólo podríamos manejar un valor por variable. Las listas permiten almacenar catálogos, usuarios, pedidos o lecturas en un contenedor ordenado y dinámico. Dominar estos patrones abre la puerta a procesar cientos o miles de elementos con unos cuantos métodos y ciclos.

### Mini aventura
Piensa en una lista como una mochila con bolsillos numerados. Puedes meter cosas, sacarlas, cambiarlas de sitio y contar cuántas hay. Cuando programas, esa mochila te permite llevar “muchas cosas parecidas” sin volverte loca/o creando una variable por cada una.

## Predicción antes de ejecutar
Observa la primera lista `bicycles`. Antes de ejecutarla, predice los valores de los índices `0`, `-1` y `4`. Ejecuta primero solo los accesos válidos y usa después la sección de `IndexError` para explicar y recuperar la predicción inválida.

---

## ¿Qué es una lista?
Una lista es una colección ordenada de elementos. En Python se definen con corchetes `[]` y los elementos se separan con comas.

```python runnable
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Salida:
```text illustrative
['trek', 'cannondale', 'redline', 'specialized']
```
Python muestra la representación literal, pero normalmente querrás acceder a cada elemento.

### Acceder a los elementos de una lista
Usa el índice (posición) dentro de corchetes para recuperar un elemento:

```python illustrative
print(bicycles[0])
print(bicycles[0].title())
```

### Los índices comienzan en 0
El primer elemento está en el índice `0`, el segundo en el `1`, etc. Para el cuarto elemento debes pedir `bicycles[3]`. Los índices negativos recorren desde el final (`-1` es el último, `-2` el penúltimo).

### Usar valores individuales de una lista
Puedes insertar elementos dentro de mensajes usando f-strings:

```python illustrative
message = f"Mi primera bicicleta fue una {bicycles[0].title()}."
print(message)
```

Ejemplo con personas:
```python runnable
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hola, {names[1]}!")
```

### Pruébalo tú (3-1 a 3-3)
1. **3-1 · Nombres**: crea una lista `names` con amistades y muestra cada nombre individualmente.
2. **3-2 · Saludos**: reutiliza la lista anterior pero imprime un saludo personalizado para cada persona.
3. **3-3 · Tu propia lista**: crea una lista de tu medio de transporte favorito y genera frases como “Me gustaría tener una …”.

---

## Modificar, añadir y eliminar elementos
Las listas son dinámicas: puedes ajustar su contenido conforme el programa avanza.

### Modificar elementos de una lista
```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Añadir elementos al final
```python illustrative
motorcycles.append('ducati')
print(motorcycles)

# Construir desde cero
teams = []
teams.append('frontend')
teams.append('backend')
print(teams)
```

### Insertar elementos en una lista
```python illustrative
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Eliminar elementos
- `del lista[i]` elimina por posición sin devolver el valor.
- `pop()` extrae el último elemento y lo retorna (acepta un índice opcional).
- `remove(valor)` localiza y elimina el primer elemento igual a `valor`.

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

last = motorcycles.pop()
print(f"Último: {last}")

first = motorcycles.pop(0)
print(f"Primero: {first}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Nota: `remove` sólo elimina la primera coincidencia; si necesitas quitar todas, recorre la lista o usa comprensiones más adelante.

### Pruébalo tú (3-4 a 3-7)
1. **3-4 · Guest List**: crea una lista con invitadas/os y envía mensajes personalizados.
2. **3-5 · Changing Guest List**: reemplaza a la persona que cancela y vuelve a imprimir invitaciones.
3. **3-6 · More Guests**: informa que encontraste una mesa más grande; usa `insert` y `append` para añadir tres personas adicionales.
4. **3-7 · Shrinking Guest List**: limita la lista a dos personas usando `pop`; agradece y elimina el resto con `del`.

---

## Organizar una lista
A medida que recibes datos en orden impredecible, necesitarás presentarlos ordenados sin destruir la información original.

### Ordenar permanentemente con `sort()`
```python runnable
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` invierte el orden alfabético y modifica la lista en sitio.

### Ordenar temporalmente con `sorted()`
```python illustrative
print(sorted(cars))          # copia ordenada
print(sorted(cars, reverse=True))
print(cars)                  # la lista original no cambió
```

### Mostrar una lista en orden inverso
```python illustrative
cars.reverse()
print(cars)
```
`reverse()` invierte el orden actual (no ordena alfabéticamente) y es reversible aplicándolo nuevamente.

### Calcular la longitud de una lista
```python illustrative
print(len(cars))
```
Saber la longitud te ayuda a validar índices y mostrar cuántos registros tienes (usuarios invitados, entradas restantes, etc.).

### Pruébalo tú (3-8 a 3-10)
1. **3-8 · Ver el mundo**: crea una lista de lugares y practica `sorted`, `reverse`, `sort` y `len` sin perder el estado original.
2. **3-9 · Invitadas/os a cenar**: a partir de los ejercicios 3-4 a 3-7, usa `len()` para decir cuántas personas invitas.
3. **3-10 · Cada función**: elige cualquier lista (montañas, ciudades, etc.) y usa cada método visto en el capítulo al menos una vez.

---

## Evitar `IndexError` al trabajar con listas
El error más común es pedir un índice fuera de rango:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
motorcycles = ["honda", "yamaha", "suzuki"]
print(motorcycles[3])
```

El diagnóstico indica que la posición solicitada no existe. Recupérate con un índice derivado de la longitud observada, sin adivinar:

```python runnable
motorcycles = ["honda", "yamaha", "suzuki"]
last_index = len(motorcycles) - 1
print(motorcycles[last_index])
```

Consejos para prevenirlo:
- Verifica la longitud antes de acceder (`if len(motorcycles) > 2:`).
- Usa `-1` para el último elemento y evita asumir el tamaño actual.
- Cuando elimines mientras recorres, itera sobre una copia (`for item in items[:]`).
- **Preview opcional:** la función y el condicional siguientes pertenecen al [capítulo 11](../chapter-11-functions/README.es.md) y al [capítulo 8](../chapter-08-conditionals/README.es.md); no se exigen en la ruta esencial. Si más adelante una función recibe índices externos, valida:
  ```python illustrative
  def get_item(items, index):
      if not 0 <= index < len(items):
          raise IndexError("posición fuera de rango")
      return items[index]
  ```
- Si ves un `IndexError`, imprime la lista o `len(items)` para confirmar su estado real.

### Pruébalo tú (3-11)
Completa el inicio sin bucles ni funciones. Ejecuta una sola vez el error intencional anterior, lee `IndexError` y después ejecuta su recuperación.

```python todo
tasks = ["read", "practice", "rest"]
# TODO 1: predict and print the first and last tasks
# TODO 2: append one task, remove one task, and print a sorted copy
# TODO 3: print the original list and its length
```

*Pista*: usa `[0]`, `[-1]`, `append`, `pop`, `sorted` y `len`; ninguno exige un capítulo posterior.

---

## Mini pruebas automáticas
**Preview opcional:** las secciones siguientes usan `def`, `if`, `raise`, bucles, comprehensions, imports y `pytest`. La idea mínima es que una función nombra trabajo reutilizable y un test la llama con una entrada conocida. Copia cada archivo completo o pospón esta ruta hasta los capítulos enlazados; no instales `pytest` desde una fuente no relacionada.

```python illustrative
# lists_utils.py
def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tareas debe ser una lista")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

# tests/test_lists_utils.py
import pytest
from lists_utils import prioritize_task

def test_prioritize_task_adds_to_front():
    original = ["documentar", "refactorizar"]
    result = prioritize_task(original, "configurar CI")
    assert result[0] == "configurar CI"
    assert original[0] == "documentar"  # la copia protege la lista original

def test_prioritize_task_rejects_non_lists():
    with pytest.raises(TypeError):
        prioritize_task("no-lista", "algo")
```

---

## Ejemplos progresivos: jugando con los ángulos interesantes
Estos ejemplos suben de dificultad gradualmente para mostrar cómo las listas se comportan en situaciones reales de backend.

### Ejemplo 1 · Checklist interactiva
```python runnable
checklist = ["Crear entorno virtual", "Instalar dependencias", "Correr pruebas"]

for step in checklist:
    print(f"- [ ] {step}")

print(f"La checklist tiene {len(checklist)} pasos.")
last = checklist.pop()            # Recuperamos el último paso
print(f"Último paso completado: {last}")
checklist.append("Publicar release")  # Añade una nueva tarea al final
```
- Practicas acceso directo, `len()` y mutaciones básicas (`pop`, `append`).
- Útil para scripts CLI donde los pasos cambian durante la ejecución.

### Ejemplo 2 · Cola de soporte (list as queue)
```python runnable
ticket_queue = ["BUG-101", "BUG-102", "BUG-103"]

def handle_ticket(queue):
    if not queue:
        return None
    return queue.pop(0)  # pop(0) simula una cola FIFO

def register_ticket(queue, ticket):
    queue.append(ticket)

current_ticket = handle_ticket(ticket_queue)
print(f"Atendiendo: {current_ticket}")
register_ticket(ticket_queue, "BUG-200")
print(f"Pendientes: {ticket_queue}")
```
- `pop(0)` tiene un coste mayor pero clarifica la semántica FIFO; más adelante podrás reemplazarlo por `collections.deque`.
- Los métodos quedan listos para conectarse a una vista Django o a un webhook sin depender del almacenamiento todavía.

### Ejemplo 3 · Normalizador de lecturas (validaciones + pruebas)
```python runnable
# normalizer.py
def normalize_readings(readings, *, max_limit):
    if not isinstance(readings, list):
        raise TypeError("lecturas debe ser lista")
    if not all(isinstance(value, (int, float)) for value in readings):
        raise ValueError("todas las lecturas deben ser numéricas")
    if not readings:
        return {"average": 0, "out_of_range": [], "top3": []}

    out_of_range = [value for value in readings if value > max_limit]
    average = sum(readings) / len(readings)
    top3 = sorted(readings, reverse=True)[:3]
    return {"average": average, "out_of_range": out_of_range, "top3": top3}
```

```python illustrative
# tests/test_normalizer.py
import pytest
from normalizer import normalize_readings

def test_normalize_readings_detects_outliers():
    data = [19.2, 20.1, 22.5, 18.0]
    result = normalize_readings(data, max_limit=20)
    assert result["out_of_range"] == [22.5]
    assert result["top3"][0] == 22.5

def test_normalize_readings_validates_types():
    with pytest.raises(ValueError):
        normalize_readings([10, "no-num"], max_limit=50)

def test_normalize_readings_empty_keeps_schema():
    result = normalize_readings([], max_limit=20)
    assert result == {"average": 0, "out_of_range": [], "top3": []}
```
- Reúne slicing (`[:3]`), ordenamiento y validaciones robustas antes de integrar en una API.
- Observa cómo las pruebas describen los ángulos interesantes: detección de outliers y correcta propagación de errores de tipo.

---

## Ejercicios guiados (con TODOs)
1. **G3-1 · Invitaciones Dinámicas**
   ```python todo
   guests = ["Noor", "Luis", "Marta"]
   # TODO 1: imprime un mensaje personalizado para cada invitado
   # TODO 2: agrega dos personas nuevas al final usando append
   # TODO 3: elimina al segundo invitado e imprime quién ya no asistirá
   ```
   *Pista*: `append`, `pop` y un bucle `for` bastan.

2. **G3-2 · Lista de Precios**
   ```python todo
   prices = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: calcula el precio promedio con sum/len
   # TODO 2: crea una lista con los precios más IVA (21%)
   # TODO 3: usa slicing para mostrar sólo los dos precios más altos
   ```
   *Pista*: combina `sorted(prices)` y `[-2:]`.

3. **G3-3 · Sensores y Validaciones**
   ```python todo
   readings = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: escribe la función out_of_range(readings, limit)
   # TODO 2: añade una prueba que confirme False cuando todos estan dentro
   # TODO 3: prueba que lance TypeError si readings no es una lista
   ```
   *Pista*: usa `any(value > limit for value in readings)` y el patrón de pruebas anterior.

---

## Errores comunes
- Empezar a contar desde 1 y obtener `IndexError`.
- Modificar una lista mientras se recorre sin copiar antes.
- Confundir `append` (agrega la lista completa como un elemento) con `extend`.
- Cambiar el orden original usando `sort()` cuando necesitabas una copia ordenada (`sorted`).
- Olvidar quitar todas las apariciones de un valor al usar `remove`.

---

## Explicación de soluciones guiadas
1. **G3-1**: los mensajes se generan con un bucle `for`, `append` agrega invitados y `pop(1)` devuelve quién salió para anunciarlo.
2. **G3-2**: el promedio es `sum(prices)/len(prices)`; la lista con IVA se crea con `[price * 1.21 for price in prices]`; los dos mayores salen de `sorted(prices)[-2:]`.
3. **G3-3**: `any(value > limit for value in readings)` detecta valores fuera de rango tras confirmar con `isinstance(readings, list)`; las pruebas cubren el caso feliz y los errores de tipo.

---

## Checkpoint y autoevaluación

### Solución explicada de 3-11

Verifica primero la ruta normal:

```python runnable
tasks = ["read", "practice", "rest"]
print(tasks[0])
print(tasks[-1])
tasks.append("review")
removed = tasks.pop(1)
sorted_tasks = sorted(tasks)
print(removed)
print(sorted_tasks)
print(tasks)
print(len(tasks))
```

Verifica después el límite de la lista vacía sin indexarla:

```python runnable
tasks = []
print(tasks)
print(len(tasks))
print(sorted(tasks))
```

La verificación exige tres registros: la salida normal, `0` para el límite vacío y el `IndexError` esperado anterior seguido de su recuperación ejecutable. Reflexiona en una frase: ¿por qué derivar `last_index` de `len()` es más seguro que adivinar una posición?

Crea una lista con tres tareas. Predice el primer y último valor, añade una tarea, elimina otra, muestra una copia ordenada y demuestra que el orden original no cambia. Después solicita a propósito un índice inválido, lee `IndexError` y recupérate comprobando `len()` antes de volver a intentarlo.

Suma un punto por criterio:
- **Corrección:** acceso, alta, baja y copia ordenada coinciden con tus predicciones.
- **Legibilidad:** los nombres explican qué contiene la lista y cada operación tiene un propósito claro.
- **Manejo del error:** explicas el índice inválido y te recuperas sin adivinar la longitud.
- **Verificación:** imprimes lista original y derivada e identificas qué operación mutó datos.
- **Explicación:** justificas elegir `pop`, `remove`, `sort` o `sorted` en un caso concreto.

La ruta esencial termina con 5/5. Con 4/5, repasa la evidencia normal, límite o recuperación que falte antes de continuar; por debajo de 4/5, repite 3-11. Funciones, bucles, excepciones, comprehensions y pytest quedan como previews opcionales.

---

## Resumen
En este capítulo definiste listas, accediste a elementos mediante índices positivos y negativos, reutilizaste valores en cadenas, modificaste la lista en tiempo real (agregar, insertar, eliminar), la ordenaste de forma permanente o temporal y empleaste `len()` y `reverse()` para inspeccionarla. También aprendiste a evitar `IndexError` e incluso a escribir pruebas que validan estas operaciones.

## Reflexión final
Dominar listas significa poder manejar colecciones completas de datos con pocas líneas: puedes añadir, quitar, cortar, ordenar y validar información sin duplicar código. En el siguiente capítulo pasaremos a estructuras que asocian *claves* con *valores* (diccionarios), la base de JSON y de las API.
