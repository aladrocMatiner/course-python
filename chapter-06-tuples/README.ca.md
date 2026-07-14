# Capítol 6 · Tuples i immutabilitat pràctica

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Veurem com les tuples ajuden a representar registres lleugers, retorns múltiples i claus compostes amb elements hashables. Treballarem amb coordenades, respostes de funcions i estructures les posicions de les quals no haurien de canviar un cop creades.

## Ordre pedagògic

- **Essencial · 40–55 minuts.** Prerequisits: capítols 3–5. Llegeix les seccions 1–2 i el primer exemple de la secció 4; completa 6-0. Resultat: crear i desempaquetar una tuple, usar-la com a clau hashable i distingir-la d’una llista. Evidència: cas normal, límit buit, error de mutació i recuperació amb una tuple nova. Acabes quan pots explicar la reassignació; continua al capítol 7 o atura’t aquí.
- **Intermèdia · 30–45 minuts.** Prerequisits: checkpoint essencial i capítol 5. Estudia hashabilitat, mutabilitat niada i el segon exemple de la secció 4. Resultat: decidir si una tuple és hashable i construir una clau amb `frozenset`. Evidència: verifica `(1, [])` i `(1, "ok")`. És opcional abans del capítol 7.
- **Avançament professional opcional · 60–75 minuts.** Prerequisits: ruta intermèdia més [bucles](../chapter-10-loops/README.ca.md), [funcions](../chapter-11-functions/README.ca.md), [classes](../chapter-12-oop/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md). Estudia 3, 5, 6 i 6-1–6-3. Resultat: retorns, `namedtuple`, validació i pytest. Es pot ometre i no bloqueja el capítol següent.

## Objectius d’aprenentatge
- Crear tuples per a dades que no s’han de modificar.
- Desempaquetar tuples en variables i usar `_` per valors que no necessites.
- Retornar múltiples valors sense crear classes.
- Usar tuples com a claus de diccionaris o elements de sets quan tots els seus valors siguin hashables.
- Escriure proves que confirmin immutabilitat i forma esperada.

## Prerequisits i avançaments opcionals
Has de conèixer [llistes](../chapter-03-lists/README.ca.md), [diccionaris](../chapter-04-dictionaries/README.ca.md) i el checkpoint essencial de [sets](../chapter-05-sets/README.ca.md). La ruta essencial usa tuples directes, desempaquetat i una consulta de diccionari; no requereix definir funcions, gestionar excepcions, typing, `namedtuple` ni pytest.

## Per què importa
En moltes APIs necessites agrupar dades ràpidament (coordenades, rangs, estats). Les tuples són més lleugeres que les llistes i comuniquen “això no es canvia”, evitant bugs en caches, claus compostes i pipelines.

### Mini aventura
Una tupla és com escriure una coordenada en un mapa amb tinta permanent: les seves posicions no es poden reassignar. L'analogia acaba als objectes mutables niats, que la tuple no congela.

## Prediu abans d'executar
Abans del primer exemple, prediu quina assignació funciona i quina llança `TypeError`. Pregunta't després si `(1, [])` és hashable: la resposta separa l'estructura fixa de la tuple de la mutabilitat dels objectes que conté.

---

## 1. Model mental: llista vs tupla

```python runnable
point_list = [10, 20]
point_tuple = (10, 20)

point_list[0] = 99      # ✔ se puede mutar
# punto_tupla[0] = 99    # ✘ TypeError: las tuplas son inmutables
```

- Usa tuples quan vulguis un senyal clar d'estructura fixa o “només lectura”. La tuple mateixa no es pot reassignar, però un objecte mutable que contingui encara pot canviar.
- Una tuple només és hashable si tots els valors que conté ho són; únicament llavors pot ser una clau de diccionari o un element d'un set.

---

## 2. Crear i desempaquetar

```python runnable
coordinate = (41.40338, 2.17403)
latitude, longitude = coordinate
print(latitude, longitude)

hours = tuple(range(0, 24))
print(hours[:3])
```

```python runnable
record = ("Noor", "Frej", 1815)
first_name, last_name, _ = record  # ignora el año con _
print(first_name, last_name)
```

- El desempaquetat millora la llegibilitat i evita índexos “màgics”.
- Usa `_` per valors que ignores expressament.

---

## 3. Retornar múltiples valors

**Avançament professional opcional:** defineix una funció i llança una excepció. Salta a la secció 4 en la ruta essencial; estudia abans [funcions](../chapter-11-functions/README.ca.md) i [excepcions](../chapter-14-exceptions/README.ca.md).

```python runnable
def divide_and_remainder(dividend, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor no puede ser cero")
    return dividend // divisor, dividend % divisor

quotient, remainder = divide_and_remainder(10, 3)
print(quotient, remainder)
```

- És més clar que retornar un diccionari quan només vols una parella ordenada.
- Documenta l’ordre del retorn per evitar confusions.

---

## 4. Tuples com a claus en diccionaris

El primer exemple és essencial; la clau amb `frozenset` és intermèdia.

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

- Empaqueta arguments significatius dins tuples per crear claus de cache reproduïbles.
- Barrejar tuples amb `frozenset` permet paràmetres en qualsevol ordre sense trencar la clau.

---

## 5. `namedtuple` per donar semàntica

**Avançament professional opcional:** completa abans [classes](../chapter-12-oop/README.ca.md) o salta aquesta secció.

```python runnable
from collections import namedtuple

Coordinate = namedtuple("Coordenada", ["lat", "lon"])
point = Coordinate(lat=41.4, lon=2.17)
print(point.lat)
```

- Tens els avantatges de les tuples (immutables, lleugeres) però amb accés per nom.
- Útil per retornar estructures auto-documentades.

---

## 6. Validacions i proves

**Avançament professional opcional:** combina anotacions, excepcions i pytest; completa abans els capítols [11](../chapter-11-functions/README.ca.md), [14](../chapter-14-exceptions/README.ca.md) i [18](../chapter-18-testing/README.ca.md).

```python runnable
# ranges.py
from typing import Tuple

HourRange = Tuple[int, int]

def validate_range(interval: HourRange) -> bool:
    start, end = interval
    if not (0 <= start < 24 and 0 <= end < 24):
        raise ValueError("Horas fuera de rango")
    if start >= end:
        raise ValueError("L'inici ha de ser inferior al final")
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

## Exercicis guiats (amb TODOs)
1. **6-0 · Registre essencial de coordenada**

   Prediu quatre valors; `()` és el límit.

   ```python todo
   coordinate = (41.4, 2.2)
   # TODO 1: unpack coordinate into latitude and longitude
   # TODO 2: create places with coordinate as a key
   # TODO 3: print both values and the dictionary lookup
   # TODO 4: add () as a key and print its value
   ```

   *Pista*: usa `latitude, longitude = coordinate`; una tuple pot ser una clau si tots els elements són hashables. No cal cap bucle ni definir una funció.

2. **6-1 · Coordenades immutables** *(avançament professional opcional)*
   ```python todo
   locations = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: recorre la llista i mostra nom + lat/lon
   # TODO 2: intenta modificar una coordenada per veure l’excepció
   # TODO 3: crea un diccionari que usi coordenades com a claus
   ```
   *Pista*: atrapa l’error per explicar per què la immutabilitat protegeix dades.

3. **6-2 · Rangs horaris** *(avançament professional opcional)*
   ```python todo
   ranges = [(9, 12), (13, 17)]
   # TODO 1: escriu total_hours(ranges) que sumi cada interval
   # TODO 2: valida que cap rang estigui invertit
   # TODO 3: afegeix una prova per al rang invertit
   ```
   *Pista*: reutilitza `validate_range` o crea un helper similar.

4. **6-3 · namedtuple per a mètriques** *(avançament professional opcional)*
   ```python todo
   from collections import namedtuple
   Point = namedtuple("Point", ["x", "y", "label"])
   samples = [Point(1, 2, "ok"), Point(3, 5, "alert")]
   # TODO 1: compta quantes mostres tenen label "alert"
   # TODO 2: converteix cada namedtuple a dict amb _asdict()
   # TODO 3: crea una prova que confirmi que Point és immutable
   ```
   *Pista*: `pytest.raises(AttributeError)` si intentes reassignar `samples[0].x`.

---

## Errors comuns
- Oblidar la coma a tuples d’un sol element: `(42)` és un int; usa `(42,)`.
- Intentar modificar una tuple: llança `TypeError`. Converteix a llista si realment cal canviar.
- No documentar l’ordre de retorn: provoca errors quan algú intercanvia valors.
- Usar tuples gegants: si tens molts camps, valora dataclasses o objectes més expressius.

---

## Explicació de solucions

### Solució essencial 6-0

El desempaquetat dona nom a les posicions. `coordinate` i `()` només contenen valors hashables i poden ser claus; la tuple buida és un límit vàlid.

```python runnable
coordinate = (41.4, 2.2)
latitude, longitude = coordinate
places = {coordinate: "station", (): "no coordinate"}

print(latitude)
print(longitude)
print(places[coordinate])
print(places[()])
```

Observa `41.4`, `2.2`, `station` i `no coordinate`.

Aquest bloc intenta mutar una posició; el senyal estable és `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
coordinate = (41.4, 2.2)
coordinate[0] = 0.0
```

Recupera’t construint una tuple nova:

```python runnable
coordinate = (41.4, 2.2)
coordinate = (0.0, coordinate[1])
print(coordinate)
```

S’imprimeix `(0.0, 2.2)`: el nom apunta a una tuple nova; cap tuple s’ha modificat.

### Notes de les rutes opcionals

1. **Coordenades**: si proves `locations[0][1][0] = 0`, obtindràs `TypeError`. Usar coordenades com a claus (`cities[locations[0][1]] = ...`) evita la corrupció accidental.
2. **Rangs**: `total_hours` suma `end - start` després de validar cada tuple; una prova amb `(15, 10)` confirma que la validació funciona.
3. **namedtuple**: `_asdict()` ajuda a serialitzar; la prova intenta `samples[0].x = 99` i espera `AttributeError`.

---

## Punt de control i autoavaluació
Completa 6-0 i compara cas normal, límit buit, error i recuperació. Explica per què falla `coordinate[0] = 0.0` però funciona reassignar `coordinate`.

- **Correcció:** desempaquetat, consultes i recuperació coincideixen amb les observacions.
- **Llegibilitat:** els noms descriuen les posicions i les claus són petites.
- **Error:** identifiques `TypeError` i crees una tuple nova.
- **Verificació:** executes els quatre casos amb CPython 3.11+.
- **Explicació:** distingeixes estructura fixa, reassignació i hashabilitat.

**Avança quan es compleixin els cinc punts.** Continua al capítol 7; la resta és opcional. Si en falta un, revisa 1, 2 i el primer exemple de 4.

## Resum
Les tuples donen a les dades una estructura externa fixa, retornen múltiples valors i, si tots els elements són hashables, creen claus compostes. Són lleugeres, però no congelen els objectes mutables que contenen.

## Reflexió final
Ara pots decidir quan usar tuples (o `namedtuple`) per transmetre significat i protegir dades. Al següent capítol veurem cues i piles eficients amb `collections.deque`.
