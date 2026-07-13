# Capítol 6 · Tuples i immutabilitat pràctica

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Veurem com les tuples ajuden a representar registres lleugers, retorns múltiples i claus compostes amb elements hashables. Treballarem amb coordenades, respostes de funcions i estructures les posicions de les quals no haurien de canviar un cop creades.

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
- Usar tuples com a claus de diccionaris o elements de sets quan tots els seus valors siguin hashables.
- Escriure proves que confirmin immutabilitat i forma esperada.

## Prerequisits i avançaments opcionals
Has de conèixer les [llistes](../chapter-03-lists/README.ca.md) i els [diccionaris](../chapter-04-dictionaries/README.ca.md). Els retorns de funcions, les excepcions, `namedtuple` i pytest són avançaments: segueix ara els patrons i estudia després [funcions](../chapter-11-functions/README.ca.md), [classes](../chapter-12-oop/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md) als seus capítols.

## Per què importa
En moltes APIs necessites agrupar dades ràpidament (coordenades, rangs, estats). Les tuples són més lleugeres que les llistes i comuniquen “això no es canvia”, evitant bugs en caches, claus compostes i pipelines.

### Mini aventura
Una tupla és com escriure una coordenada en un mapa amb tinta permanent: les seves posicions no es poden reassignar. L'analogia acaba als objectes mutables niats, que la tuple no congela.

## Prediu abans d'executar
Abans del primer exemple, prediu quina assignació funciona i quina llança `TypeError`. Pregunta't després si `(1, [])` és hashable: la resposta separa l'estructura fixa de la tuple de la mutabilitat dels objectes que conté.

---

## 1. Model mental: llista vs tupla

```python runnable
punto_lista = [10, 20]
punto_tupla = (10, 20)

punto_lista[0] = 99      # ✔ se puede mutar
# punto_tupla[0] = 99    # ✘ TypeError: las tuplas son inmutables
```

- Usa tuples quan vulguis un senyal clar d'estructura fixa o “només lectura”. La tuple mateixa no es pot reassignar, però un objecte mutable que contingui encara pot canviar.
- Una tuple només és hashable si tots els valors que conté ho són; únicament llavors pot ser una clau de diccionari o un element d'un set.

---

## 2. Crear i desempaquetar

```python runnable
coordenada = (41.40338, 2.17403)
latitud, longitud = coordenada
print(latitud, longitud)

horas = tuple(range(0, 24))
print(horas[:3])
```

```python runnable
registro = ("Noor", "Frej", 1815)
nombre, apellido, _ = registro  # ignora el año con _
print(nombre, apellido)
```

- El desempaquetat millora la llegibilitat i evita índexos “màgics”.
- Usa `_` per valors que ignores expressament.

---

## 3. Retornar múltiples valors

```python runnable
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

```python runnable
coordenadas_ciudad = {
    (41.3874, 2.1686): "Barcelona",
    (40.4168, -3.7038): "Madrid",
}

print(coordenadas_ciudad.get((41.3874, 2.1686)))
```

```python runnable
cache_respuestas = {}

parametros = ("/api/report", "POST", frozenset({("team", "analytics")}))
cache_respuestas[parametros] = {"status": 200, "body": "OK"}
```

- Empaqueta arguments significatius dins tuples per crear claus de cache reproduïbles.
- Barrejar tuples amb `frozenset` permet paràmetres en qualsevol ordre sense trencar la clau.

---

## 5. `namedtuple` per donar semàntica

```python runnable
from collections import namedtuple

Coordenada = namedtuple("Coordenada", ["lat", "lon"])
punto = Coordenada(lat=41.4, lon=2.17)
print(punto.lat)
```

- Tens els avantatges de les tuples (immutables, lleugeres) però amb accés per nom.
- Útil per retornar estructures auto-documentades.

---

## 6. Validacions i proves

```python runnable
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

```python illustrative
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
   ```python todo
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
   ```python todo
   rangos = [(9, 12), (13, 17)]
   # TODO 1: escriu total_horas(rangos) que sumi cada interval
   # TODO 2: valida que cap rang estigui invertit
   # TODO 3: afegeix una prova per al rang invertit
   ```
   *Pista*: reutilitza `validar_intervalo` o crea un helper similar.

3. **6-3 · namedtuple per a mètriques**
   ```python todo
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

## Punt de control i autoavaluació
Explica sense executar codi la coma de `(42,)`, el desempaquetat amb `_`, els retorns múltiples i la regla que fa hashable una tuple. Resol després un exercici i prova'n el resultat i una entrada invàlida.

- **Preparat**: distingeixes estructura fixa d'immutabilitat profunda i tries tuple, llista o `namedtuple` deliberadament.
- **Gairebé**: uses tuples, però encara consultes el desempaquetat o la hashabilitat.
- **Repassa**: torna a les seccions 1, 2 i 4 i prova amb una tuple que contingui una llista.

## Resum
Les tuples donen a les dades una estructura externa fixa, retornen múltiples valors i, si tots els elements són hashables, creen claus compostes. Són lleugeres, però no congelen els objectes mutables que contenen.

## Reflexió final
Ara pots decidir quan usar tuples (o `namedtuple`) per transmetre significat i protegir dades. Al següent capítol veurem cues i piles eficients amb `collections.deque`.
