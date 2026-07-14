# Kapitel 5 · Sets, unikhet och medlemskap

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utforskar `set` och `frozenset` för att ta bort dubletter, kontrollera medlemskap och kombinera samlingar med matematikliknande operationer. Exemplen handlar om behörigheter, taggar och synkronisering mellan datakällor.

## Lärväg

- **Grundläggande · 40–55 minuter.** Förkunskaper: kapitel 3–4. Läs avsnitt 1 och 3 och gör övning 5-0. Resultat: deduplicera direkta data, kontrollera medlemskap och jämföra sets med `|`, `&` och `-`. Evidens: den förklarade lösningen täcker ett normalfall, ett tomt set som gränsfall, det avsiktliga indexeringsfelet och en lyckad återhämtning. Du är klar när du kan förklara varför ett set saknar position `0`; fortsätt till kapitel 6 eller stanna tryggt här.
- **Mellannivå · 45–60 minuter.** Förkunskaper: grundkontrollpunkten och [kapitel 10](../chapter-10-loops/README.sv.md). Studera avsnitt 2, tagg- och synkroniseringsexemplen i avsnitt 4 och avsnitt 5; gör 5-1 och 5-2. Resultat: skapa sets med en comprehension och välja `frozenset` för en hashbar grupp. Evidens: kör båda övningarna igen med tom indata. Vägen är frivillig före kapitel 6.
- **Frivillig professionell förhandsblick · 45–60 minuter.** Förkunskaper: mellannivån samt [funktioner](../chapter-11-functions/README.sv.md), [exceptions](../chapter-14-exceptions/README.sv.md) och [testning](../chapter-18-testing/README.sv.md). Studera behörighetsvalideringen, avsnitt 6 och 5-3. Resultat: validera en katalog med en funktion, en avsiktlig exception och pytest-evidens. Förhandsblicken kan hoppas över och blockerar inte nästa grundkapitel.

## Lärandemål

- Bygga sets från andra samlingar och ta bort dubletter.
- Kontrollera medlemskap med `in` i O(1) i genomsnitt.
- Jämföra och kombinera data med set-operationer.
- Välja `set` eller `frozenset` efter behovet av förändring.
- Testa happy paths och edge cases som tomma sets och tomma snitt.

## Förkunskaper och frivilliga förhandsblickar

Du bör känna dig trygg med [listor](../chapter-03-lists/README.sv.md) och [dictionaries](../chapter-04-dictionaries/README.sv.md). Grundvägen använder direkta set-värden och välkända built-ins; den kräver inga funktionsdefinitioner, exception-hantering, typing eller pytest. Comprehensions, funktioner, exceptions och tester är frivilliga förhandsblickar som länkas i vägarna ovan.

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

**Frivillig förhandsblick på mellannivå:** avsnittet använder `range` och en set comprehension, som [kapitel 10](../chapter-10-loops/README.sv.md) lär ut i ordning. På grundvägen kan du hoppa direkt till avsnitt 3.

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

**Frivillig professionell förhandsblick:** exemplet definierar en funktion och höjer en exception. Hoppa över det på grundvägen; kapitel [11](../chapter-11-functions/README.sv.md) och [14](../chapter-14-exceptions/README.sv.md) lär först ut verktygen.

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

Det här är mellannivå. Det är användbart men krävs inte av grundkontrollpunkten.

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

**Frivillig professionell förhandsblick:** avsnittet kombinerar funktioner, exceptions, typkontroller och pytest. Gör först kapitel [11](../chapter-11-functions/README.sv.md), [14](../chapter-14-exceptions/README.sv.md) och [18](../chapter-18-testing/README.sv.md), eller kopiera mönstret utan att behandla det som obligatoriskt arbete.

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

1. **5-0 · Grundläggande medlemskapskarta**

   Förutsäg de fyra utskrifterna innan du skriver kod. Det tomma setet är gränsfallet.

   ```python todo
   skills = ["python", "python", "git"]
   required = {"python", "sql"}
   # TODO 1: create unique_skills from skills
   # TODO 2: print membership for "python"
   # TODO 3: print the shared and missing sets in sorted order
   # TODO 4: print the size of an empty set
   ```

   *Ledtråd*: använd `set(skills)`, `&`, `-`, `sorted(...)` och `len(set())`. Ingen loop eller funktionsdefinition behövs.

2. **5-1 · Unika taggar** *(mellannivå)*

   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```

   *Ledtråd*: kontrollera `if nueva not in etiquetas_set` före tillägg.

3. **5-2 · Snitt av färdigheter** *(mellannivå)*

   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```

   *Ledtråd*: använd `backend & frontend` och `backend - frontend`.

4. **5-3 · Validera roller** *(frivillig professionell förhandsblick)*

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

### Grundlösning 5-0

Konvertera först listan en enda gång. Snittet behåller värden i båda seten; differensen behåller krav som fortfarande saknas. `set()` ger det tomma gränsfallet utan specialfall.

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

Observera `['git', 'python']`, `True`, `['python']`, `['sql']` och `0`, i den ordningen. Dubletten försvinner och det tomma setet är fortfarande giltig indata.

Ett set saknar stabila positioner. Blocket indexerar avsiktligt ett set, så den stabila diagnostiska signalen är `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
languages = {"python", "rust"}
print(languages[0])
```

Återhämta genom att fråga om medlemskap eller sortera enbart för visning:

```python runnable
languages = {"python", "rust"}
print("python" in languages)
print(sorted(languages))
```

Återhämtningen skriver `True` och `['python', 'rust']`; den låtsas inte att själva setet har fått en ordning.

### Lösningsanteckningar för frivilliga vägar

1. **Unika taggar**: `etiquetas_unicas = set(etiquetas)` tar bort dubletter och `len(etiquetas_unicas)` räknar dem.
2. **Snitt**: `compartidas = backend & frontend` och `solo_backend = backend - frontend`; beskriv resultatet med en f-sträng.
3. **Roller**: beräkna `extra = asignados - permitidos` och höj `ValueError` om mängden inte är tom; testa att `check_roles(set(), permitidos)` returnerar `True`.

---

## Kontrollpunkt och självbedömning

Gör 5-0, förutsäg före varje körning och jämför normalfallet, det tomma fallet, felet och återhämtningen med lösningen. Förklara sedan högt varför `languages[0]` misslyckas medan `"python" in languages` är meningsfullt.

- **Korrekthet:** dubletter försvinner; medlemskap, snitt, differens och den tomma gränsen stämmer med observationerna.
- **Läsbarhet:** namnen beskriver de två seten och sortering används endast för visning.
- **Felhantering:** du identifierar `TypeError` som stabil signal och återhämtar utan indexering eller beroende av iterationsordning.
- **Verifiering:** du kör faktiskt blocken för normalfall, gränsfall, förväntat fel och återhämtning med CPython 3.11+.
- **Förklaring:** du skiljer medlemskap från position och förklarar en operation med egna ord.

**Gå vidare när alla fem punkter stämmer.** Fortsätt till kapitel 6; mellan- och proffsvägen är fortfarande frivilliga. Om en punkt saknas, gå tillbaka till avsnitt 1 och 3 och kör 5-0 med `skills = []`.

## Sammanfattning

Sets deduplicerar data, kontrollerar medlemskap och kombinerar samlingar deklarativt. Det förenklar behörigheter, taggar och synkronisering.

## Avslutande reflektion

Nu kan du hitta inkonsekvenser med set-operationer och validera hela kataloger före nästa lager. Nästa kapitel använder tuples för oföränderliga poster och flera returvärden.
