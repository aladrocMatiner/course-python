# Kapitel 6 · Tuples och praktisk oföränderlighet

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi ser hur tuples representerar små poster, flera returvärden och sammansatta nycklar med hashbara element. Exemplen använder koordinater, funktionsresultat och strukturer vars positioner inte ska ändras efter skapandet.

## Lärväg

1. **Mental modell**: skillnaden mellan listor och tuples.
2. **Skapa och läsa**: litteraler, `tuple()` och unpacking.
3. **Flera returvärden** från en funktion.
4. **Tuples som nycklar** för sammansatt data.
5. **`namedtuple`** för mer läsbara dataobjekt.
6. **Validering och tester** som säkrar kritisk struktur.

## Lärandemål

- Skapa tuples för data som inte ska muteras.
- Packa upp tuples till variabler och ignorera värden med `_`.
- Returnera flera värden utan att skapa hela klasser.
- Använda tuples som dictionary-nycklar och set-element när alla värden i dem är hashbara.
- Testa oföränderlighet och förväntad struktur.

## Förkunskaper och frivilliga förhandsblickar

Du bör kunna [listor](../chapter-03-lists/README.sv.md) och [dictionaries](../chapter-04-dictionaries/README.sv.md). Funktionsreturer, exceptions, `namedtuple` och pytest är förhandsblickar: följ mönstren nu och studera sedan [funktioner](../chapter-11-functions/README.sv.md), [klasser](../chapter-12-oop/README.sv.md), [exceptions](../chapter-14-exceptions/README.sv.md) och [testning](../chapter-18-testing/README.sv.md).

## Varför det spelar roll

API:er behöver ofta kort gruppera koordinater, datumintervall eller statuspar. Tuples är lättviktiga och signalerar ”ändra inte”, vilket förebygger fel i pipelines, cache och sammansatta nycklar.

### Miniäventyr

En tuple är som en kartkoordinat skriven med permanent bläck: positionerna kan inte tilldelas om. Liknelsen gäller inte muterbara objekt inuti, som tuplen inte fryser.

## Förutsäg före körning

Förutsäg vilken tilldelning som lyckas och vilken som ger `TypeError` före det första exemplet. Fråga sedan om `(1, [])` är hashbar; svaret skiljer tuple-strukturens fasthet från muterbarheten hos objekt inuti.

---

## 1. Mental modell: lista eller tuple

```python runnable
point_list = [10, 20]
point_tuple = (10, 20)

point_list[0] = 99       # ✔ can mutate
# point_tuple[0] = 99    # ✘ TypeError: tuples are immutable
```

- Använd tuples som en tydlig signal om fast struktur eller ”read-only”. Själva tuplen kan inte tilldelas om, men ett muterbart objekt inuti den kan fortfarande ändras.
- En tuple är hashbar endast om varje värde i den är hashbart; först då kan den vara dictionary-nyckel eller set-element.

---

## 2. Skapa och packa upp

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

- Unpacking är tydligare än ”magiska index”.
- `_` markerar ett värde som medvetet ignoreras.

---

## 3. Returnera flera värden

```python runnable
def divide_and_remainder(dividend, divisor):
    if divisor == 0:
        raise ZeroDivisionError("Divisor cannot be zero")
    return dividend // divisor, dividend % divisor

quotient, remainder = divide_and_remainder(10, 3)
print(quotient, remainder)
```

- Ett ordnat par är tydligare än en dictionary i det här lilla kontraktet.
- Dokumentera returordningen så att värden inte förväxlas.

---

## 4. Tuples som dictionary-nycklar

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

- Samla betydelsefulla argument i tuples för stabila cache-nycklar.
- Med `frozenset` kan parametrars ordning ignoreras utan att nyckeln bryts.

---

## 5. `namedtuple` ger fälten mening

```python runnable
from collections import namedtuple

Coordinate = namedtuple("Coordinate", ["lat", "lon"])
point = Coordinate(lat=41.4, lon=2.17)
print(point.lat)
```

- Du får tuple-fördelarna, oföränderlighet och låg vikt, plus namnåtkomst.
- Det passar självdokumenterande returvärden från funktioner och tjänster.

---

## 6. Validering och tester

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

## Vägledda övningar (med TODO)

1. **6-1 · Oföränderliga koordinater**

   ```python todo
   locations = [
       ("HQ", (41.0, 2.0)),
       ("DataCenter", (40.4, -3.7)),
   ]
   # TODO 1: iterate and print name + lat/lon
   # TODO 2: try to modify a coordinate to see the exception
   # TODO 3: create a dict that uses coordinates as keys
   ```

   *Ledtråd*: fånga undantaget och förklara hur oföränderlighet skyddar data.

2. **6-2 · Tidsintervall**

   ```python todo
   ranges = [(9, 12), (13, 17)]
   # TODO 1: write total_hours(ranges) that sums each interval
   # TODO 2: validate that no range is reversed
   # TODO 3: add a test for the reversed range
   ```

   *Ledtråd*: återanvänd `validate_range` eller skapa motsvarande hjälpfunktion.

3. **6-3 · namedtuple för mätvärden**

   ```python todo
   from collections import namedtuple
   Point = namedtuple("Point", ["x", "y", "label"])
   samples = [Point(1, 2, "ok"), Point(3, 5, "alert")]
   # TODO 1: count how many samples have label "alert"
   # TODO 2: convert each namedtuple into dict using _asdict()
   # TODO 3: create a test that confirms Point is immutable
   ```

   *Ledtråd*: förvänta `AttributeError` med `pytest.raises` när `samples[0].x` tilldelas om.

---

## Vanliga misstag

- **Glömma kommat i en enelementstuple**: `(42)` är en `int`; skriv `(42,)`.
- **Försöka ändra en tuple** ger `TypeError`; konvertera till lista om ändring verkligen behövs.
- **Inte dokumentera returordning** skapar svårfunna förväxlingar.
- **Använda enorma tuples**: många fält passar bättre i dataclasses eller uttrycksfulla objekt.

---

## Förklarade lösningar

1. **Koordinater**: `locations[0][1][0] = 0` ger `TypeError`. Koordinaten kan vara nyckel, exempelvis `cities[locations[0][1]]`, utan risk att nyckeln ändras.
2. **Tidsintervall**: `total_hours` summerar `end - start` efter validering; testet `(15, 10)` bekräftar det omvända fallet.
3. **Mätvärden**: `_asdict()` gör varje punkt serialiserbar som dict; försök till `samples[0].x = 99` ska ge `AttributeError`.

---

## Kontrollpunkt och självbedömning

Förklara utan körning kommat i `(42,)`, unpacking med `_`, flera returvärden och regeln som gör en tuple hashbar. Lös sedan en övning och testa resultatet samt en ogiltig indata.

- **Redo**: du skiljer fast struktur från djup oföränderlighet och väljer tuple, lista eller `namedtuple` medvetet.
- **Nästan**: du använder tuples men behöver ännu stöd för unpacking eller hashbarhet.
- **Repetera**: gå tillbaka till avsnitt 1, 2 och 4 och prova en tuple som innehåller en lista.

## Sammanfattning

Tuples ger data en fast yttre struktur, returnerar flera värden och kan, när alla element är hashbara, bygga sammansatta nycklar. De är lättviktiga men fryser inte muterbara objekt inuti.

## Avslutande reflektion

Nu kan du välja tuple eller `namedtuple` för att uttrycka mening och skydda data. Nästa kapitel använder `collections.deque` för effektiva köer, arbetsflöden och glidande fönster.
