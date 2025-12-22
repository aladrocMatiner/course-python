# Capítulo 6 · Tuplas e Inmutabilidad Practica

## Qué vamos a construir
Veremos cómo las tuplas ayudan a representar registros ligeros, retornos múltiples y claves inmutables. Trabajaremos con coordenadas, respuestas de funciones y pequeñas estructuras que no deberían cambiar tras crearse.

## Orden pedagógico
1. **Modelo mental**: diferencias entre listas y tuplas.
2. **Creación y acceso**: literales, `tuple()` y desempaquetado.
3. **Uso en retornos múltiples**: funciones que devuelven varias piezas de información.
4. **Tuplas como claves**: diccionarios que usan tuplas para indexar datos compuestos.
5. **`namedtuple` y dataclasses ligeras**: mejorar la legibilidad.
6. **Validaciones y pruebas**: garantizar que no se modifiquen datos críticos.

## Objetivos de aprendizaje
- Crear tuplas para representar datos que no deben mutar.
- Desempaquetar tuplas en variables individuales y usar `_` para los valores que no necesitas.
- Retornar múltiples valores de una función sin definir clases completas.
- Usar tuplas como claves de diccionarios o elementos de sets.
- Escribir pruebas que confirmen la inmutabilidad y estructura esperada.

## Por qué importa
En muchas APIs necesitas agrupar datos brevemente (coordenadas, rangos de fechas, estados). Las tuplas son más ligeras que las listas y comunican que esos valores no deben cambiar, lo cual evita bugs en pipelines, caches y claves compuestas.

---

## 1. Modelo mental: lista vs tupla

```python
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99      # ✔ se puede mutar
# punto_tupla[0] = 99    # ✘ TypeError: las tuplas son inmutables
```

- Usa tuplas cuando quieras señales claras de “solo lectura”.
- La inmutabilidad permite usar tuplas como claves de diccionarios o elementos de sets.

---

## 2. Crear y desempaquetar

```python
coordenada = (41.40338, 2.17403)
latitud, longitud = coordenada
print(latitud, longitud)

horas = tuple(range(0, 24))
print(horas[:3])
```

```python
registro = ("Ada", "Lovelace", 1815)
nombre, apellido, _ = registro  # ignora el año con _
print(nombre, apellido)
```

- El desempaquetado mejora la legibilidad y evita índices mágicos.
- Usa `_` (guion bajo) para valores que no necesitas.

---

## 3. Retornar múltiples valores

```python
def dividir_y_residuo(dividendo, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividendo // divisor, dividendo % divisor

cociente, residuo = dividir_y_residuo(10, 3)
print(cociente, residuo)
```

- Este patrón es más claro que devolver un diccionario cuando solo necesitas un par ordenado.
- Documenta el orden de los valores para evitar confusiones.

---

## 4. Tuplas como claves en diccionarios

```python
coordenadas_ciudad = {
    (41.3874, 2.1686): "Barcelona",
    (40.4168, -3.7038): "Madrid",
}

print(coordenadas_ciudad.get((41.3874, 2.1686)))
```

```python
cache_respuestas = {}

parametros = ("/api/report", "POST", frozenset({("team", "analytics")}))
cache_respuestas[parametros] = {"status": 200, "body": "OK"}
```

- Empaqueta argumentos significativos dentro de tuplas para crear claves de caché reproducibles.
- Mezclar tuplas con `frozenset` permite incluir parámetros en cualquier orden sin romper la clave.

---

## 5. `namedtuple` para dar semántica

```python
from collections import namedtuple

Coordenada = namedtuple("Coordenada", ["lat", "lon"])
punto = Coordenada(lat=41.4, lon=2.17)
print(punto.lat)
```

- Obtienes los beneficios de las tuplas (inmutables, ligeras) pero con acceso por nombre.
- Útil para retornar estructuras auto-documentadas desde funciones o servicios.

---

## 6. Validaciones y pruebas

```python
# ranges.py
from typing import Tuple

Hora = Tuple[int, int]

def validar_intervalo(intervalo: Hora) -> bool:
    inicio, fin = intervalo
    if not (0 <= inicio < 24 and 0 <= fin < 24):
        raise ValueError("Horas fuera de rango")
    if inicio >= fin:
        raise ValueError("El inicio debe ser menor que el fin")
    return True
```

```python
# tests/test_ranges.py
import pytest
from ranges import validar_intervalo

def test_validar_intervalo_correcto():
    assert validar_intervalo((9, 17)) is True

def test_validar_intervalo_rechaza_valores_invalidos():
    with pytest.raises(ValueError):
        validar_intervalo((20, 8))
```

---

## Ejercicios guiados (con TODOs)
1. **6-1 · Coordenadas inmutables**
   ```python
   ubicaciones = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: recorre la lista y muestra nombre + lat/lon
   # TODO 2: intenta modificar una coordenada para ver la excepción
   # TODO 3: crea un diccionario que use las coordenadas como claves
   ```
   *Hint*: maneja la excepción para explicar por qué la inmutabilidad protege los datos.

2. **6-2 · Rangos horarios**
   ```python
   rangos = [(9, 12), (13, 17)]
   # TODO 1: escribe total_horas(rangos) que sume cada intervalo
   # TODO 2: valida que ningún rango esté invertido
   # TODO 3: añade una prueba para el rango invertido
   ```
   *Hint*: reutiliza `validar_intervalo` o crea un helper similar.

3. **6-3 · namedtuple para métricas**
   ```python
   from collections import namedtuple
   Punto = namedtuple("Punto", ["x", "y", "label"])
   muestras = [Punto(1, 2, "ok"), Punto(3, 5, "alert")]
   # TODO 1: recorre y cuenta cuántas muestras tienen label "alert"
   # TODO 2: convierte cada namedtuple en dict usando _asdict()
   # TODO 3: crea una prueba que confirme que Punto es inmutable
   ```
   *Hint*: `pytest.raises(AttributeError)` al intentar reasignar `muestras[0].x`.

---

## Errores comunes
- **Olvidar la coma en tuplas de un elemento**: `(42)` es un int; usa `(42,)`.
- **Intentar modificar una tupla**: lanza `TypeError`. Convierte a lista si realmente necesitas cambios.
- **No documentar el orden de retorno**: provoca errores sutiles cuando alguien intercambia los valores.
- **Usar tuplas gigantes**: si necesitas muchos campos, evalúa dataclasses u objetos más expresivos.

---

## Explicación de soluciones
1. **Coordenadas inmutables**: al intentar `ubicaciones[0][1][0] = 0`, obtendrás un `TypeError`. Al usar las coordenadas como claves (`ciudades[ubicaciones[0][1]] = ...`), garantizas que la localización no se corrompa.
2. **Rangos horarios**: `total_horas` suma `fin - inicio` tras validar cada tupla; una prueba con `(15, 10)` confirma que la validación funciona.
3. **namedtuple para métricas**: `_asdict()` transforma cada punto en dict para serializar; la prueba intenta `muestras[0].x = 99` y espera `AttributeError`, demostrando la inmutabilidad.

---

## Resumen
Las tuplas te permiten empaquetar datos inmutables, retornar múltiples valores sin clases complejas y crear claves compuestas para cachés o diccionarios. Son ideales cuando necesitas liviandad y seguridad contra modificaciones accidentales.

## Reflexión final
Ahora puedes decidir cuándo usar tuplas (o `namedtuple`) para transmitir significado y proteger tus datos. Sigamos con colas eficientes en el siguiente capítulo, donde `collections.deque` nos permitirá modelar flujos de trabajo y ventanas deslizantes.
