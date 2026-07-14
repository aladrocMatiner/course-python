# Capítol 5 · Conjunts (sets) i pertinença

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem els conjunts (`set` i `frozenset`) per deduplicar dades, comprovar si un element hi és dins i combinar col·leccions amb operacions “de matemàtiques”. Farem exemples centrats en permisos, etiquetes i sincronització de dades.

## Ordre pedagògic

- **Essencial · 40–55 minuts.** Prerequisits: capítols 3–4. Llegeix les seccions 1 i 3 i completa l’exercici 5-0. Resultat: deduplicar dades directes, comprovar pertinença i comparar conjunts amb `|`, `&` i `-`. Evidència: la solució explicada cobreix un cas normal, el límit del conjunt buit, l’error intencional d’indexació i una recuperació correcta. Acabes quan pots explicar per què un set no té posició `0`; continua al capítol 6 o atura’t aquí amb seguretat.
- **Intermèdia · 45–60 minuts.** Prerequisits: el checkpoint essencial i el [capítol 10](../chapter-10-loops/README.ca.md). Estudia la secció 2, els exemples d’etiquetes i sincronització de la secció 4 i la secció 5; completa 5-1 i 5-2. Resultat: crear sets amb una comprensió i triar `frozenset` per a un grup hashable. Evidència: torna a executar tots dos exercicis amb una entrada buida. Aquesta ruta és opcional abans del capítol 6.
- **Avançament professional opcional · 45–60 minuts.** Prerequisits: la ruta intermèdia més [funcions](../chapter-11-functions/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [proves](../chapter-18-testing/README.ca.md). Estudia la validació de permisos, la secció 6 i 5-3. Resultat: validar un catàleg amb una funció, una excepció deliberada i evidència de pytest. Pots ometre aquest avançament; no bloqueja el capítol essencial següent.

## Objectius d’aprenentatge
- Construir sets a partir d’altres col·leccions i eliminar duplicats.
- Comprovar pertinença en O(1) de mitjana amb `in`.
- Aplicar operacions de conjunts per comparar i combinar dades.
- Triar entre `set` i `frozenset` segons mutabilitat.
- Escriure proves amb casos “feliços” i casos límit (sets buits, sense intersecció).

## Prerequisits i avançaments opcionals
Cal estar còmode amb les [llistes](../chapter-03-lists/README.ca.md) i els [diccionaris](../chapter-04-dictionaries/README.ca.md). La ruta essencial usa valors set directes i built-ins ja coneguts; no exigeix definir funcions, gestionar excepcions, typing ni pytest. Les comprensions, funcions, excepcions i proves queden com a avançaments opcionals enllaçats a les rutes anteriors.

## Per què importa
Quan gestiones correus, rols o etiquetes, els duplicats creen bugs subtils. Els sets ho simplifiquen amb sintaxi directa i eficient. En backend són molt útils per permisos, inconsistències i sincronització.

### Mini aventura
Imagina que col·lecciones cromos i no en vols repetits. Un `set` és aquesta capsa on, si intentes posar el mateix cromo una altra vegada, et diu: “ja el tinc”.

## Prediu abans d'executar
Abans del primer exemple, prediu el contingut del conjunt i el resultat de la pertinença. No en predius l'ordre d'iteració: els sets no ofereixen un ordre estable i l'exemple només ordena per presentar el resultat.

---

## 1. Model mental: col·lecció sense duplicats

```python runnable
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(sorted(correos_unicos))  # ['frej@example.com', 'noor@example.com']

print("noor@example.com" in correos_unicos)  # True
```

- Els sets no garanteixen ordre. S’enfoquen en la pertinença.
- Convertir una llista a set és la manera més ràpida de treure duplicats.

---

## 2. Crear sets i comprensions

**Avançament intermedi opcional:** aquesta secció usa `range` i una comprensió de set, que el [capítol 10](../chapter-10-loops/README.ca.md) ensenya en ordre. A la ruta essencial pots saltar directament a la secció 3.

```python runnable
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(sorted(cuadrados))
```

- Usa `{}` amb elements per crear sets literales. `{}` buit és un diccionari; usa `set()` per a un set buit.
- Les comprensions de set funcionen com les de llista però eliminen duplicats automàticament.

---

## 3. Operacions entre conjunts

```python runnable
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}
permisos_guest = {"view"}

union = permisos_admin | permisos_guest           # {'view', 'edit', 'delete'}
interseccion = permisos_admin & permisos_editor   # {'view', 'edit'}
solo_admin = permisos_admin - permisos_editor     # {'delete'}
simetrica = permisos_admin ^ permisos_editor      # {'delete'}

print(permisos_guest <= permisos_editor)  # True: guest es subconjunto de editor
```

- `|` unió, `&` intersecció, `-` diferència, `^` diferència simètrica.
- `<=`/`<` per comprovar subconjunts.

---

## 4. Casos pràctics

### Control d’etiquetes
```python runnable
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {sorted(nuevas)}")
```

### Sincronització de dades
```python runnable
local_users = {"noor", "frej", "taha"}
remote_users = {"frej", "taha", "grace"}

missing = remote_users - local_users
inactive = local_users - remote_users
```

### Validació de permisos

**Avançament professional opcional:** aquest exemple defineix una funció i llança una excepció. Omet-lo a la ruta essencial; els capítols [11](../chapter-11-functions/README.ca.md) i [14](../chapter-14-exceptions/README.ca.md) ensenyen abans aquestes eines.

```python runnable
def validate_permissions(assigned, allowed):
    extra = assigned - allowed
    if extra:
        raise ValueError(f"Invalid permissions: {extra}")
    return True
```

---

## 5. `frozenset` i sets com a claus
Quan necessitis un set immutable (per exemple, com a clau d’un diccionari), usa `frozenset`.

Aquesta és profunditat intermèdia. És útil, però no és necessària per al checkpoint essencial.

```python runnable
segments = {
    frozenset({"ios", "premium"}): "Campaign A",
    frozenset({"android", "free"}): "Campaign B",
}

query = frozenset({"premium", "ios"})
print(segments.get(query))
```

- Un `frozenset` es comporta com un set, però no permet afegir ni treure elements.
- Ideal per definir combinacions úniques d’atributs.

---

## 6. Validació i proves

**Avançament professional opcional:** aquesta secció combina funcions, excepcions, comprovacions de tipus i pytest. Completa primer els capítols [11](../chapter-11-functions/README.ca.md), [14](../chapter-14-exceptions/README.ca.md) i [18](../chapter-18-testing/README.ca.md), o copia el patró sense tractar-lo com a treball obligatori.

```python runnable
# permissions.py
VALID_PERMISSIONS = {"view", "edit", "delete"}

def normalize_permissions(permission_list):
    if not isinstance(permission_list, (list, set, tuple)):
        raise TypeError("permissions must be iterable")
    permissions = set(permission_list)
    invalid = permissions - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}")
    return permissions
```

```python illustrative
# tests/test_permissions.py
import pytest
from permissions import normalize_permissions

def test_normalize_permissions_deduplicates():
    result = normalize_permissions(["view", "view", "edit"])
    assert result == {"view", "edit"}

def test_normalize_permissions_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_permissions(["hack"])
```

---

## Exercicis guiats (amb TODOs)
1. **5-0 · Mapa essencial de pertinença**

   Prediu els quatre resultats abans d’escriure codi. El conjunt buit és el cas límit.

   ```python todo
   skills = ["python", "python", "git"]
   required = {"python", "sql"}
   # TODO 1: create unique_skills from skills
   # TODO 2: print membership for "python"
   # TODO 3: print the shared and missing sets in sorted order
   # TODO 4: print the size of an empty set
   ```

   *Pista*: usa `set(skills)`, `&`, `-`, `sorted(...)` i `len(set())`. No cal cap bucle ni definir una funció.

2. **5-1 · Etiquetes úniques** *(intermèdia)*
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *Pista*: `if nueva not in etiquetas_set` abans d’afegir.

3. **5-2 · Intersecció de skills** *(intermèdia)*
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *Pista*: `backend & frontend` i `backend - frontend`.

4. **5-3 · Validar rols** *(avançament professional opcional)*
   ```python todo
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: write check_roles(asignados, permitidos)
   # TODO 2: the function must raise ValueError if it finds roles outside the catalog
   # TODO 3: add a test confirming empty sets are valid
   ```
   *Pista*: reutilitza `extra = asignados - permitidos` i `pytest.raises`.

---

## Errors comuns
- **Intentar indexar un set**: no tenen ordre. Converteix a llista si necessites índex.
- **Esperar un ordre determinista**: l’ordre pot canviar entre execucions.
- **Oblidar que `{}` és un diccionari**: usa `set()` per a un set buit.
- **Comparar “a mà”**: fes servir operacions de conjunts per detectar diferències.

---

## Explicació de solucions

### Solució essencial 5-0

Primer converteix la llista una sola vegada. La intersecció conserva els valors presents en tots dos sets; la diferència conserva els requisits que falten. `set()` proporciona el límit buit sense un cas especial.

```python runnable
skills = ["python", "python", "git"]
unique_skills = set(skills)
required = {"python", "sql"}

print(sorted(unique_skills))
print("python" in unique_skills)
print(sorted(unique_skills & required))
print(sorted(required - unique_skills))
print(len(set()))
```

Observa `['git', 'python']`, `True`, `['python']`, `['sql']` i `0`, en aquest ordre. El duplicat desapareix i el conjunt buit continua sent una entrada vàlida.

Un set no té posicions estables. Aquest bloc n’indexa un intencionadament, de manera que el senyal diagnòstic estable és `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
languages = {"python", "rust"}
print(languages[0])
```

Recupera’t preguntant per pertinença o ordenant només per mostrar:

```python runnable
languages = {"python", "rust"}
print("python" in languages)
print(sorted(languages))
```

La recuperació imprimeix `True` i `['python', 'rust']`; no simula que el mateix set hagi adquirit ordre.

### Notes de solució de les rutes opcionals

1. **Etiquetes úniques**: `set(etiquetas)` elimina duplicats; `len(...)` compta.
2. **Intersecció**: `backend & frontend` i `backend - frontend`; explica-ho amb un f-string.
3. **Rols**: calcula `extra` i llança si no és buit; prova que `check_roles(set(), permitidos)` funciona.

---

## Punt de control i autoavaluació
Completa 5-0, prediu abans de cada execució i compara els casos normal, buit, error i recuperació amb la solució. Després explica en veu alta per què falla `languages[0]` mentre que `"python" in languages` sí que té sentit.

- **Correcció:** desapareixen els duplicats; la pertinença, intersecció, diferència i el límit buit coincideixen amb les observacions.
- **Llegibilitat:** els noms descriuen els dos sets i només s’ordena per mostrar.
- **Gestió de l’error:** identifiques `TypeError` com a senyal estable i et recuperes sense indexar ni dependre de l’ordre d’iteració.
- **Verificació:** executes realment els blocs normal, límit, error esperat i recuperació amb CPython 3.11+.
- **Explicació:** diferencies pertinença de posició i expliques una operació amb les teves paraules.

**Avança quan es compleixin els cinc punts.** Continua al capítol 6; les rutes intermèdia i professional continuen sent opcionals. Si en falta un, torna a les seccions 1 i 3 i repeteix 5-0 amb `skills = []`.

## Resum
Amb sets pots deduplicar, comprovar pertinença i combinar col·leccions de manera declarativa. Això simplifica permisos, etiquetes i sincronitzacions.

## Reflexió final
Ara pots detectar inconsistències d’una ullada i validar catàlegs abans de passar-los a una altra capa. Al següent capítol explorarem tuples per representar registres immutables i retorns múltiples.
