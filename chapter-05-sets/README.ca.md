# Capítol 5 · Conjunts (sets) i pertinença

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem els conjunts (`set` i `frozenset`) per deduplicar dades, comprovar si un element hi és dins i combinar col·leccions amb operacions “de matemàtiques”. Farem exemples centrats en permisos, etiquetes i sincronització de dades.

## Ordre pedagògic
1. **Idea base**: una col·lecció sense duplicats.
2. **Crear i consultar**: construir des de llistes, comprensions, mutabilitat.
3. **Operacions principals**: unió, intersecció, diferència i subconjunts.
4. **Casos reals**: permisos, etiquetes, sincronització entre fonts.
5. **`frozenset` i ús com a clau**: quan necessites conjunts immutables.
6. **Validacions i proves**: assegurar regles d’accés o deduplicació.

## Objectius d’aprenentatge
- Construir sets a partir d’altres col·leccions i eliminar duplicats.
- Comprovar pertinença en O(1) (promig) amb `in`.
- Aplicar operacions de conjunts per comparar i combinar dades.
- Triar entre `set` i `frozenset` segons mutabilitat.
- Escriure proves amb casos “feliços” i casos límit (sets buits, sense intersecció).

## Per què importa
Quan gestiones correus, rols o etiquetes, els duplicats creen bugs subtils. Els sets ho simplifiquen amb sintaxi directa i eficient. En backend són molt útils per permisos, inconsistències i sincronització.

### Mini aventura
Imagina que col·lecciones cromos i no en vols repetits. Un `set` és aquesta capsa on, si intentes posar el mateix cromo una altra vegada, et diu: “ja el tinc”.

---

## 1. Model mental: col·lecció sense duplicats

```python
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(correos_unicos)  # {'noor@example.com', 'frej@example.com'}

print("noor@example.com" in correos_unicos)  # True
```

- Els sets no garanteixen ordre. S’enfoquen en la pertinença.
- Convertir una llista a set és la manera més ràpida de treure duplicats.

---

## 2. Crear sets i comprensions

```python
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(cuadrados)
```

- Usa `{}` amb elements per crear sets literales. `{}` buit és un diccionari; usa `set()` per a un set buit.
- Les comprensions de set funcionen com les de llista però eliminen duplicats automàticament.

---

## 3. Operacions entre conjunts

```python
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
```python
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {nuevas}")
```

### Sincronització de dades
```python
usuarios_local = {"noor", "frej", "taha"}
usuarios_remoto = {"frej", "taha", "grace"}

faltantes = usuarios_remoto - usuarios_local
inactivos = usuarios_local - usuarios_remoto
```

### Validació de permisos
```python
def validar_permisos(asignados, permitidos):
    extra = asignados - permitidos
    if extra:
        raise ValueError(f"Permisos inválidos: {extra}")
    return True
```

---

## 5. `frozenset` i sets com a claus
Quan necessitis un set immutable (per exemple, com a clau d’un diccionari), usa `frozenset`.

```python
segmentos = {
    frozenset({"ios", "premium"}): "Campaña A",
    frozenset({"android", "free"}): "Campaña B",
}

consulta = frozenset({"premium", "ios"})
print(segmentos.get(consulta))
```

- Un `frozenset` es comporta com un set, però no permet afegir ni treure elements.
- Ideal per definir combinacions úniques d’atributs.

---

## 6. Validació i proves

```python
# permissions.py
PERMISOS_VALIDOS = {"view", "edit", "delete"}

def normalizar_permisos(lista_permisos):
    if not isinstance(lista_permisos, (list, set, tuple)):
        raise TypeError("permisos debe ser iterable")
    permisos = set(lista_permisos)
    invalidos = permisos - PERMISOS_VALIDOS
    if invalidos:
        raise ValueError(f"Permisos invalidos: {invalidos}")
    return permisos
```

```python
# tests/test_permissions.py
import pytest
from permissions import normalizar_permisos

def test_normalizar_permisos_elimina_duplicados():
    resultado = normalizar_permisos(["view", "view", "edit"])
    assert resultado == {"view", "edit"}

def test_normalizar_permisos_rechaza_invalidos():
    with pytest.raises(ValueError):
        normalizar_permisos(["hack"])
```

---

## Exercicis guiats (amb TODOs)
1. **5-1 · Etiquetes úniques**
   ```python
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: converteix a set
   # TODO 2: demana una etiqueta nova i afegeix-la si no existeix
   # TODO 3: imprimeix quantes etiquetes úniques hi ha
   ```
   *Pista*: `if nueva not in etiquetas_set` abans d’afegir.

2. **5-2 · Intersecció de skills**
   ```python
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: calcula les skills compartides
   # TODO 2: calcula les exclusives de backend
   # TODO 3: crea un missatge que expliqui el resultat
   ```
   *Pista*: `backend & frontend` i `backend - frontend`.

3. **5-3 · Validar rols**
   ```python
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: escriu check_roles(asignados, permitidos)
   # TODO 2: llança ValueError si detecta rols fora de catàleg
   # TODO 3: afegeix una prova que confirmi que sets buits són vàlids
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
1. **Etiquetes úniques**: `set(etiquetas)` elimina duplicats; `len(...)` compta.
2. **Intersecció**: `backend & frontend` i `backend - frontend`; explica-ho amb un f-string.
3. **Rols**: calcula `extra` i llança si no és buit; prova que `check_roles(set(), permitidos)` funciona.

---

## Resum
Amb sets pots deduplicar, comprovar pertinença i combinar col·leccions de manera declarativa. Això simplifica permisos, etiquetes i sincronitzacions.

## Reflexió final
Ara pots detectar inconsistències d’una ullada i validar catàlegs abans de passar-los a una altra capa. Al següent capítol explorarem tuples per representar registres immutables i retorns múltiples.
