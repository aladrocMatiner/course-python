# Capítol 6 · Tuples i immutabilitat pràctica

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Veurem com les tuples ajuden a representar registres lleugers, retorns múltiples i claus immutables. Treballarem amb coordenades, respostes de funcions i petites estructures que no haurien de canviar un cop creades.

## Ordre pedagògic
1. **Model mental**: diferències entre llistes i tuples.
2. **Creació i accés**: literals, `tuple()` i desempaquetat.
3. **Retorns múltiples**: funcions que tornen més d’una dada.
4. **Tuples com a claus**: diccionaris amb claus compostes.
5. **`namedtuple`**: millorar llegibilitat.
6. **Validacions i proves**: garantir estructura i immutabilitat.

## Objectius d’aprenentatge
- Crear tuples per a dades que no s’han de modificar.
- Desempaquetar tuples en variables i usar `_` per valors que no necessites.
- Retornar múltiples valors sense crear classes.
- Usar tuples com a claus de diccionaris o elements de sets.
- Escriure proves que confirmin immutabilitat i forma esperada.

## Per què importa
En moltes APIs necessites agrupar dades ràpidament (coordenades, rangs, estats). Les tuples són més lleugeres que les llistes i comuniquen “això no es canvia”, evitant bugs en caches, claus compostes i pipelines.

### Mini aventura
Una tupla és com escriure una coordenada en un mapa amb tinta permanent. Et serveix per recordar “aquest punt exacte”. Si algú el canvia, es trenca el mapa. Per això la tupla protegeix aquests valors.

---

## 1. Model mental: llista vs tupla

```python
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99      # ✔ se puede mutar
# punto_tupla[0] = 99    # ✘ TypeError: las tuplas son inmutables
```

- Usa tuples quan vulguis un senyal clar de “només lectura”.
- La immutabilitat permet usar tuples com a claus o elements de sets.

---

## 2. Crear i desempaquetar

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

- El desempaquetat millora la llegibilitat i evita índexos “màgics”.
- Usa `_` per valors que ignores expressament.

---

## 3. Retornar múltiples valors

```python
def dividir_y_residuo(dividendo, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividendo // divisor, dividendo % divisor

cociente, residuo = dividir_y_residuo(10, 3)
print(cociente, residuo)
```

- És més clar que retornar un diccionari quan només vols una parella ordenada.
- Documenta l’ordre del retorn per evitar confusions.

---

## 4. Tuples com a claus en diccionaris

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

- Empaqueta arguments significatius dins tuples per crear claus de cache reproduïbles.
- Barrejar tuples amb `frozenset` permet paràmetres en qualsevol ordre sense trencar la clau.

---

## 5. `namedtuple` per donar semàntica

```python
from collections import namedtuple

Coordenada = namedtuple("Coordenada", ["lat", "lon"])
punto = Coordenada(lat=41.4, lon=2.17)
print(punto.lat)
```

- Tens els avantatges de les tuples (immutables, lleugeres) però amb accés per nom.
- Útil per retornar estructures auto-documentades.

---

## 6. Validacions i proves

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

## Exercicis guiats (amb TODOs)
1. **6-1 · Coordenades immutables**
   ```python
   ubicaciones = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: recorre la llista i mostra nom + lat/lon
   # TODO 2: intenta modificar una coordenada per veure l’excepció
   # TODO 3: crea un diccionari que usi coordenades com a claus
   ```
   *Pista*: atrapa l’error per explicar per què la immutabilitat protegeix dades.

2. **6-2 · Rangs horaris**
   ```python
   rangos = [(9, 12), (13, 17)]
   # TODO 1: escriu total_horas(rangos) que sumi cada interval
   # TODO 2: valida que cap rang estigui invertit
   # TODO 3: afegeix una prova per al rang invertit
   ```
   *Pista*: reutilitza `validar_intervalo` o crea un helper similar.

3. **6-3 · namedtuple per a mètriques**
   ```python
   from collections import namedtuple
   Punto = namedtuple("Punto", ["x", "y", "label"])
   muestras = [Punto(1, 2, "ok"), Punto(3, 5, "alert")]
   # TODO 1: compta quantes mostres tenen label "alert"
   # TODO 2: converteix cada namedtuple a dict amb _asdict()
   # TODO 3: crea una prova que confirmi que Punto és immutable
   ```
   *Pista*: `pytest.raises(AttributeError)` si intentes reasignar `muestras[0].x`.

---

## Errors comuns
- Oblidar la coma a tuples d’un sol element: `(42)` és un int; usa `(42,)`.
- Intentar modificar una tuple: llança `TypeError`. Converteix a llista si realment cal canviar.
- No documentar l’ordre de retorn: provoca errors quan algú intercanvia valors.
- Usar tuples gegants: si tens molts camps, valora dataclasses o objectes més expressius.

---

## Explicació de solucions
1. **Coordenades**: si proves `ubicaciones[0][1][0] = 0`, obtindràs `TypeError`. Usar coordenades com a claus evita corrupció accidental.
2. **Rangs**: suma `fin - inicio` després de validar; una prova amb `(15, 10)` confirma que falla.
3. **namedtuple**: `_asdict()` ajuda a serialitzar; la prova intenta `muestras[0].x = 99` i espera `AttributeError`.

---

## Resum
Les tuples et permeten empaquetar dades immutables, retornar múltiples valors i crear claus compostes per a caches o diccionaris. Són ideals quan vols lleugeresa i protecció contra canvis accidentals.

## Reflexió final
Ara pots decidir quan usar tuples (o `namedtuple`) per transmetre significat i protegir dades. Al següent capítol veurem cues i piles eficients amb `collections.deque`.
