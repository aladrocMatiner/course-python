# Kapitel 5 · Sets, unikhet och medlemskap

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utforskar `set` och `frozenset` för att ta bort dubletter, kontrollera medlemskap och kombinera samlingar med matematikliknande operationer. Exemplen handlar om behörigheter, taggar och synkronisering mellan datakällor.

## Lärväg

1. **Kärnidén**: en samling utan dubletter.
2. **Skapa och fråga**: listor, set comprehensions och muterbarhet.
3. **Operationer**: union, snitt, differens och delmängder.
4. **Praktik**: behörigheter, taggar och synkronisering.
5. **`frozenset` som nyckel** när oföränderlighet krävs.
6. **Validering och tester** av åtkomst- och dedupliceringsregler.

## Lärandemål

- Bygga sets från andra samlingar och ta bort dubletter.
- Kontrollera medlemskap med `in` i O(1) i genomsnitt.
- Jämföra och kombinera data med set-operationer.
- Välja `set` eller `frozenset` efter behovet av förändring.
- Testa happy paths och edge cases som tomma sets och tomma snitt.

## Förkunskaper och frivilliga förhandsblickar

Du bör känna dig trygg med [listor](../chapter-03-lists/README.sv.md) och [dictionaries](../chapter-04-dictionaries/README.sv.md). Funktioner, exceptions och pytest används här bara som återanvändbara mönster; de behandlas fullt ut i [kapitel 11](../chapter-11-functions/README.sv.md), [kapitel 14](../chapter-14-exceptions/README.sv.md) och [kapitel 18](../chapter-18-testing/README.sv.md).

## Varför det spelar roll

Dubletter bland e-postadresser, roller och taggar skapar subtila fel. Sets löser det direkt och passar i backend för behörigheter, inkonsekvenser och synkronisering.

### Miniäventyr

Tänk dig en låda med samlarkort som vägrar ta emot samma kort två gånger: ”Det finns redan.” Det är grundidén i ett `set`.

## Förutsäg före körning

Förutsäg mängdens innehåll och medlemskapstestets resultat före det första exemplet. Förutsäg inte iterationens ordning: sets har ingen stabil visningsordning, så exemplet sorterar endast för presentation.

---

## 1. Mental modell: en samling utan dubletter

```python runnable
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(sorted(correos_unicos))  # ['frej@example.com', 'noor@example.com']

print("noor@example.com" in correos_unicos)  # True
```

- Sets garanterar ingen ordning; fokus är medlemskap.
- Att konvertera en lista till ett set är enklaste sättet att ta bort dubletter.

---

## 2. Skapa sets och comprehensions

```python runnable
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(sorted(cuadrados))
```

- `{}` med element skapar ett set, men tomma `{}` är en dictionary; använd `set()` för ett tomt set.
- Set comprehensions liknar list comprehensions men tar automatiskt bort dubletter.

---

## 3. Set-operationer

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

- `|` är union, `&` snitt, `-` differens och `^` symmetrisk differens.
- `<=` och `<` kontrollerar om ett set är en delmängd.

---

## 4. Praktiska fall

### Taggkontroll

```python runnable
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {sorted(nuevas)}")
```

### Datasynkronisering

```python runnable
local_users = {"noor", "frej", "taha"}
remote_users = {"frej", "taha", "grace"}

missing = remote_users - local_users
inactive = local_users - remote_users
```

### Validera behörigheter

```python runnable
def validate_permissions(assigned, allowed):
    extra = assigned - allowed
    if extra:
        raise ValueError(f"Invalid permissions: {extra}")
    return True
```

---

## 5. `frozenset` och sets som nycklar

När ett set måste vara oföränderligt, exempelvis som dictionary-nyckel, används `frozenset`.

```python runnable
segments = {
    frozenset({"ios", "premium"}): "Campaign A",
    frozenset({"android", "free"}): "Campaign B",
}

query = frozenset({"premium", "ios"})
print(segments.get(query))
```

- `frozenset` beter sig som ett set men element kan inte läggas till eller tas bort.
- Det passar unika kombinationer av egenskaper.

---

## 6. Validering och tester

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

## Vägledda övningar (med TODO)

1. **5-1 · Unika taggar**

   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```

   *Ledtråd*: kontrollera `if nueva not in etiquetas_set` före tillägg.

2. **5-2 · Snitt av färdigheter**

   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```

   *Ledtråd*: använd `backend & frontend` och `backend - frontend`.

3. **5-3 · Validera roller**

   ```python todo
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: write check_roles(asignados, permitidos)
   # TODO 2: the function must raise ValueError if it finds roles outside the catalog
   # TODO 3: add a test confirming empty sets are valid
   ```

   *Ledtråd*: återanvänd `extra = asignados - permitidos` och `pytest.raises`.

---

## Vanliga misstag

- **Indexera ett set**: sets har varken ordning eller positioner. Konvertera till lista om index behövs.
- **Förvänta bestämd ordning**: ordningen kan ändras mellan körningar. Konvertera före UI-utskrift.
- **Glömma att `{}` är en dict**: ett tomt set skapas med `set()`.
- **Jämföra referenser i stället för innehåll**: använd set-operationer för att uttrycka skillnader.

---

## Förklarade lösningar

1. **Unika taggar**: `etiquetas_unicas = set(etiquetas)` tar bort dubletter och `len(etiquetas_unicas)` räknar dem.
2. **Snitt**: `compartidas = backend & frontend` och `solo_backend = backend - frontend`; beskriv resultatet med en f-sträng.
3. **Roller**: beräkna `extra = asignados - permitidos` och höj `ValueError` om mängden inte är tom; testa att `check_roles(set(), permitidos)` returnerar `True`.

---

## Kontrollpunkt och självbedömning

Förklara utan att köra kod varför medlemskap är O(1) i genomsnitt, när `frozenset` krävs och vad `|`, `&` och `-` returnerar. Lös sedan en övning och testa ett normalfall samt ett tomt set.

- **Redo**: du väljer rätt operation, förlitar dig inte på ordning och motiverar båda testerna.
- **Nästan**: koden fungerar, men du behöver fortfarande stöd för operation eller edge case.
- **Repetera**: gå tillbaka till avsnitt 1, 3 och 5 och försök med andra data.

## Sammanfattning

Sets deduplicerar data, kontrollerar medlemskap och kombinerar samlingar deklarativt. Det förenklar behörigheter, taggar och synkronisering.

## Avslutande reflektion

Nu kan du hitta inkonsekvenser med set-operationer och validera hela kataloger före nästa lager. Nästa kapitel använder tuples för oföränderliga poster och flera returvärden.
