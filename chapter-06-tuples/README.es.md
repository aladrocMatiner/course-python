# Capítulo 6 · Tuplas e Inmutabilidad Practica

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Veremos cómo las tuplas ayudan a representar registros ligeros, retornos múltiples y claves compuestas cuyos elementos sean hashables. Trabajaremos con coordenadas, respuestas de funciones y pequeñas estructuras cuyas posiciones no deberían cambiar tras crearse.

## Orden pedagógico

- **Esencial · 40–55 minutos.** Prerrequisitos: capítulos 3–5. Lee las secciones 1–2 y el primer ejemplo de la sección 4; después completa 6-0. Resultado: crear y desempaquetar una tupla, usar una tupla hashable como clave y distinguir su estructura fija de una lista. Evidencia: la solución cubre una coordenada normal, el límite de la tupla vacía, un error intencional de mutación y la recuperación creando otra tupla. Terminas cuando puedes explicar por qué la reasignación crea otro objeto; continúa al capítulo 7 o detente aquí con seguridad.
- **Intermedia · 30–45 minutos.** Prerrequisitos: el checkpoint esencial y el capítulo 5. Estudia la hashabilidad, la mutabilidad anidada y el segundo ejemplo de la sección 4. Resultado: decidir si una tupla es hashable y construir una clave compuesta con `frozenset`. Evidencia: predice y verifica si `(1, [])` y `(1, "ok")` pueden ser claves. Esta ruta es opcional antes del capítulo 7.
- **Avance profesional opcional · 60–75 minutos.** Prerrequisitos: la ruta intermedia más [bucles](../chapter-10-loops/README.es.md), [funciones](../chapter-11-functions/README.es.md), [clases](../chapter-12-oop/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pruebas](../chapter-18-testing/README.es.md). Estudia las secciones 3, 5 y 6 y los ejercicios 6-1–6-3. Resultado: devolver tuplas desde funciones, usar `namedtuple`, validar rangos y verificar con pytest. Puedes omitir este avance; no bloquea el capítulo esencial siguiente.

## Objetivos de aprendizaje
- Crear tuplas para representar datos que no deben mutar.
- Desempaquetar tuplas en variables individuales y usar `_` para los valores que no necesitas.
- Retornar múltiples valores de una función sin definir clases completas.
- Usar tuplas como claves de diccionarios o elementos de sets cuando todos sus valores sean hashables.
- Escribir pruebas que confirmen la inmutabilidad y estructura esperada.

## Prerrequisitos y avances opcionales
Debes conocer [listas](../chapter-03-lists/README.es.md), [diccionarios](../chapter-04-dictionaries/README.es.md) y el checkpoint esencial de [sets](../chapter-05-sets/README.es.md). La ruta esencial usa tuplas directas, desempaquetado y una consulta de diccionario; no requiere definir funciones, gestionar excepciones, typing, `namedtuple` ni pytest. Esos conceptos posteriores son avances opcionales enlazados arriba.

## Por qué importa
En muchas APIs necesitas agrupar datos brevemente (coordenadas, rangos de fechas, estados). Las tuplas son más ligeras que las listas y comunican que esos valores no deben cambiar, lo cual evita bugs en pipelines, caches y claves compuestas.

### Mini aventura
Una tupla es como escribir una coordenada en un mapa con tinta permanente: sus posiciones no se pueden reasignar. La analogía termina en los objetos mutables anidados, que la tupla no congela.

## Predice antes de ejecutar
Antes del primer ejemplo, predice qué asignación funciona y cuál lanza `TypeError`. Pregúntate después si `(1, [])` es hashable: la respuesta separa la estructura fija de la tupla de la mutabilidad de los objetos contenidos.

---

## 1. Modelo mental: lista vs tupla

```python runnable
point_list = [10, 20]
point_tuple = (10, 20)

point_list[0] = 99       # ✔ can mutate
# point_tuple[0] = 99    # ✘ TypeError: tuples are immutable
```

- Usa tuplas cuando quieras una señal clara de estructura fija o “solo lectura”. La propia tupla no se puede reasignar, pero un objeto mutable guardado dentro sí puede cambiar.
- Una tupla sólo es hashable si todos los valores que contiene lo son; únicamente entonces puede usarse como clave de diccionario o elemento de un set.

---

## 2. Crear y desempaquetar

```python runnable
coordinate = (41.40338, 2.17403)
latitude, longitude = coordinate
print(latitude, longitude)

hours = tuple(range(0, 24))
print(hours[:3])
```

```python runnable
record = ("Noor", "Frej", 1815)
first_name, last_name, _ = record  # ignore the year with _
print(first_name, last_name)
```

- El desempaquetado mejora la legibilidad y evita índices mágicos.
- Usa `_` (guion bajo) para valores que no necesitas.

---

## 3. Retornar múltiples valores

**Avance profesional opcional:** esta sección define una función y lanza una excepción. En la ruta esencial salta a la sección 4 y estudia antes [funciones](../chapter-11-functions/README.es.md) y [excepciones](../chapter-14-exceptions/README.es.md).

```python runnable
def divide_and_remainder(dividend, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor cannot be zero")
    return dividend // divisor, dividend % divisor

quotient, remainder = divide_and_remainder(10, 3)
print(quotient, remainder)
```

- Este patrón es más claro que devolver un diccionario cuando solo necesitas un par ordenado.
- Documenta el orden de los valores para evitar confusiones.

---

## 4. Tuplas como claves en diccionarios

El primer ejemplo pertenece a la ruta esencial. La clave de caché con `frozenset` que aparece después es profundidad intermedia.

```python runnable
city_coordinates = {
    (41.3874, 2.1686): "Barcelona",
    (40.4168, -3.7038): "Madrid",
}

print(city_coordinates.get((41.3874, 2.1686)))
```

```python runnable
response_cache = {}

params = ("/api/report", "POST", frozenset({("team", "analytics")}))
response_cache[params] = {"status": 200, "body": "OK"}
```

- Empaqueta argumentos significativos dentro de tuplas para crear claves de caché reproducibles.
- Mezclar tuplas con `frozenset` permite incluir parámetros en cualquier orden sin romper la clave.

---

## 5. `namedtuple` para dar semántica

**Avance profesional opcional:** `namedtuple` crea una clase similar a una tupla. Completa primero el capítulo fundamental de [clases](../chapter-12-oop/README.es.md) u omite esta sección sin perder el checkpoint esencial.

```python runnable
from collections import namedtuple

Coordinate = namedtuple("Coordinate", ["lat", "lon"])
point = Coordinate(lat=41.4, lon=2.17)
print(point.lat)
```

- Obtienes los beneficios de las tuplas (inmutables, ligeras) pero con acceso por nombre.
- Útil para retornar estructuras auto-documentadas desde funciones o servicios.

---

## 6. Validaciones y pruebas

**Avance profesional opcional:** esta sección combina anotaciones de funciones, excepciones y pytest. Completa primero los capítulos [11](../chapter-11-functions/README.es.md), [14](../chapter-14-exceptions/README.es.md) y [18](../chapter-18-testing/README.es.md).

```python runnable
# ranges.py
from typing import Tuple

HourRange = Tuple[int, int]

def validate_range(interval: HourRange) -> bool:
    start, end = interval
    if not (0 <= start < 24 and 0 <= end < 24):
        raise ValueError("Hours out of range")
    if start >= end:
        raise ValueError("Start must be before end")
    return True
```

```python illustrative
# tests/test_ranges.py
import pytest
from ranges import validate_range

def test_validate_range_ok():
    assert validate_range((9, 17)) is True

def test_validate_range_rejects_invalid():
    with pytest.raises(ValueError):
        validate_range((20, 8))
```

---

## Ejercicios guiados (con TODOs)
1. **6-0 · Registro esencial de coordenada**

   Predice los cuatro valores antes de completar los TODO. La tupla vacía es el caso límite.

   ```python todo
   coordinate = (41.4, 2.2)
   # TODO 1: unpack coordinate into latitude and longitude
   # TODO 2: create places with coordinate as a key
   # TODO 3: print both values and the dictionary lookup
   # TODO 4: add () as a key and print its value
   ```

   *Pista*: desempaqueta con `latitude, longitude = coordinate`; una tupla puede ser clave si todos sus elementos son hashables. No necesitas un bucle ni definir una función.

2. **6-1 · Coordenadas inmutables** *(avance profesional opcional)*
   ```python todo
   locations = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: iterate and print name + lat/lon
   # TODO 2: try to modify a coordinate to see the exception
   # TODO 3: create a dict that uses coordinates as keys
   ```
   *Pista*: maneja la excepción para explicar por qué la inmutabilidad protege los datos.

3. **6-2 · Rangos horarios** *(avance profesional opcional)*
   ```python todo
   ranges = [(9, 12), (13, 17)]
   # TODO 1: write total_hours(ranges) that sums each interval
   # TODO 2: validate that no range is reversed
   # TODO 3: add a test for the reversed range
   ```
   *Pista*: reutiliza `validar_intervalo` o crea un helper similar.

4. **6-3 · namedtuple para métricas** *(avance profesional opcional)*
   ```python todo
   from collections import namedtuple
   Point = namedtuple("Point", ["x", "y", "label"])
   samples = [Point(1, 2, "ok"), Point(3, 5, "alert")]
   # TODO 1: count how many samples have label "alert"
   # TODO 2: convert each namedtuple into dict using _asdict()
   # TODO 3: create a test that confirms Point is immutable
   ```
   *Pista*: `pytest.raises(AttributeError)` al intentar reasignar `muestras[0].x`.

---

## Errores comunes
- **Olvidar la coma en tuplas de un elemento**: `(42)` es un int; usa `(42,)`.
- **Intentar modificar una tupla**: lanza `TypeError`. Convierte a lista si realmente necesitas cambios.
- **No documentar el orden de retorno**: provoca errores sutiles cuando alguien intercambia los valores.
- **Usar tuplas gigantes**: si necesitas muchos campos, evalúa dataclasses u objetos más expresivos.

---

## Explicación de soluciones

### Solución esencial 6-0

El desempaquetado da nombres con significado a las dos posiciones. Tanto `coordinate` como `()` contienen solo valores hashables, por lo que pueden ser claves; la tupla vacía es un límite válido, no un dato ausente por sí sola.

```python runnable
coordinate = (41.4, 2.2)
latitude, longitude = coordinate
places = {coordinate: "station", (): "no coordinate"}

print(latitude)
print(longitude)
print(places[coordinate])
print(places[()])
```

Observa `41.4`, `2.2`, `station` y `no coordinate`, en ese orden.

Las posiciones de una tupla no se pueden reasignar. Este bloque intenta mutar una a propósito, así que la señal estable es `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
coordinate = (41.4, 2.2)
coordinate[0] = 0.0
```

Recupérate construyendo y asignando una tupla nueva en vez de mutar la anterior:

```python runnable
coordinate = (41.4, 2.2)
coordinate = (0.0, coordinate[1])
print(coordinate)
```

La recuperación imprime `(0.0, 2.2)`. El nombre apunta ahora a otra tupla; ninguna tupla cambió en el sitio.

### Notas de solución de las rutas opcionales

1. **Coordenadas inmutables**: al intentar `locations[0][1][0] = 0`, obtendrás un `TypeError`. Al usar las coordenadas como claves (`cities[locations[0][1]] = ...`), garantizas que la localización no se corrompa.
2. **Rangos horarios**: `total_hours` suma `end - start` tras validar cada tupla; una prueba con `(15, 10)` confirma que la validación funciona.
3. **namedtuple para métricas**: `_asdict()` transforma cada punto en dict para serializar; la prueba intenta `samples[0].x = 99` y espera `AttributeError`, demostrando que se bloquea la reasignación de campos.

---

## Punto de control y autoevaluación
Completa 6-0, predice antes de cada ejecución y compara los comportamientos normal, vacío, error y recuperación con la solución. Después explica en voz alta por qué falla `coordinate[0] = 0.0` pero funciona reasignar `coordinate`.

- **Corrección:** el desempaquetado, las dos consultas y la coordenada recuperada coinciden con las observaciones.
- **Legibilidad:** los nombres describen sus posiciones y las claves siguen siendo pequeñas y significativas.
- **Gestión del error:** identificas `TypeError` como señal estable y te recuperas construyendo una tupla nueva.
- **Verificación:** ejecutas los bloques normal, límite, error esperado y recuperación con CPython 3.11+.
- **Explicación:** diferencias con tus palabras estructura fija, reasignación de un nombre y la regla de hashabilidad.

**Avanza cuando se cumplan los cinco puntos.** Continúa al capítulo 7; los avances intermedio y profesional son opcionales. Si falta uno, vuelve a las secciones 1, 2 y al primer ejemplo de la 4 y repite 6-0 con `coordinate = ()` solo para la consulta límite.

## Resumen
Las tuplas dan a los datos una estructura externa fija, retornan múltiples valores sin clases complejas y, si todos los elementos son hashables, crean claves compuestas. Son ligeras, pero no congelan los objetos mutables que contienen.

## Reflexión final
Ahora puedes decidir cuándo usar tuplas (o `namedtuple`) para transmitir significado y proteger tus datos. Sigamos con colas eficientes en el siguiente capítulo, donde `collections.deque` nos permitirá modelar flujos de trabajo y ventanas deslizantes.
