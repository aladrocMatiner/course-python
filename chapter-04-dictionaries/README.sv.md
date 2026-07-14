# Kapitel 4 · Dictionaries (data med nyckel och värde)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du lär dig modellera strukturerad information med dictionaries (`dict`). Vi använder användarprofiler, konfiguration och JSON-liknande svar från backendarbete. Du får skapa, uppdatera, slå samman och validera dictionaries innan de exponeras i ett API eller lagras i en databas.

## Lärväg

1. **Mental modell**: en dictionary mappar nycklar till värden.
2. **Skapa och läsa**: strikt `[]`, tolerant `get` och tydlig formatering.
3. **Uppdatera och ta bort**: `.update`, `del`, `pop` och standardvärden.
4. **Iterera**: `keys`, `values`, `items` och comprehensions.
5. **Nästlade strukturer**: listor av dictionaries och dictionaries inuti dictionaries.
6. **Validering och tester**: säkra att en payload har obligatoriska fält.

## Lärandemål

- Representera verkliga entiteter som användare, order och konfiguration.
- Läsa och uppdatera nycklar säkert med strikt eller tolerant åtkomst.
- I den frivilliga professionella vägen iterera och bygga härledda strukturer.
- Slå samman dictionaries och hantera nästlade nycklar konsekvent.
- I den frivilliga professionella vägen testa att obligatoriska nycklar finns och otillåtna saknas.

## Förkunskaper och vägar

- **Förkunskap:** slutför kontrollpunkten i [kapitel 3](../chapter-03-lists/README.sv.md). Grundvägen behöver bara grunderna i listor och variabler.
- **Grundväg · 45–60 min:** avsnitt 1–3, men hoppa över den frivilliga formateringsfunktionen, samt övning 4-1 och kontrollpunkten. Resultat: skapa, läsa, uppdatera, slå samman och rensa en dictionary med direkta satser; funktioner krävs inte.
- **Mellanväg · 25–35 min:** nästlade strukturer och övning 4-2. Resultat: kontrollera saknade externa fält med `get` före indexering.
- **Frivillig professionell förhandsblick · 35–45 min:** avsnitt 4 och 6 samt övning 4-3. De förhandsvisar [villkor](../chapter-08-conditionals/README.sv.md), [loopar](../chapter-10-loops/README.sv.md), [funktioner](../chapter-11-functions/README.sv.md), [undantag](../chapter-14-exceptions/README.sv.md) och [pytest](../chapter-18-testing/README.sv.md). Kopiera de kompletta exemplen eller hoppa över dem utan att blockera grundkontrollpunkten.

## Varför det spelar roll

Dictionaries ligger bakom JSON, formatet som moderna API:er använder. Med `dict` kan du bearbeta payloads, HTTP-svar, parametrar och konfiguration och förbereds för serialisering mellan Python och andra system.

### Miniäventyr

En dictionary liknar kontaktlistan i en telefon: du söker ett namn, nyckeln, och får informationen, värdet. Programmet kan slå upp rätt sak utan att gå igenom en hel lista.

## Förutsäg före körning

I det första `user`-exemplet förutsäger du resultatet av strikt åtkomst till `"username"`, tolerant åtkomst till den saknade `"timezone"` och strikt åtkomst till samma saknade nyckel. Kör bara de två första och förklara hur `get` ger en återhämtningsväg från `KeyError`.

---

## 1. Mental modell: dictionaries som uppslag

Tänk på en telefonkatalog där en nyckel ger ett värde.

```python runnable
user = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(user["username"])  # strict access
print(user.get("timezone", "UTC"))  # tolerant access with a default
```

Strikt åtkomst till en saknad nyckel är användbart bevis. Detta block ger avsiktligt `KeyError`:

<!-- bookcheck: expect-error="KeyError" -->
```python expected-error
user = {"username": "noor"}
print(user["timezone"])
```

Återhämta dig med tolerant åtkomst och ett uttryckligt standardvärde:

```python runnable
user = {"username": "noor"}
print(user.get("timezone", "UTC"))
```

- Nycklar måste vara **hashable**, alltså stabila uppslagsnamn för Python. Använd strängar eller tal på den grundläggande vägen. Tuple-nycklar är en valfri förhandsvisning efter [kapitel 6](../chapter-06-tuples/README.sv.md) och fungerar bara när alla värden i tuplen också är hashable. Värden kan vara valfria objekt.
- Använd `get` när nyckeln kanske saknas. Då undviks `KeyError` och ett rimligt standardvärde kan ges.

---

## 2. Skapa, läsa och normalisera värden

```python runnable
profile = {}
profile["first_name"] = "Grace"
profile["last_name"] = "Hopper"
profile.setdefault("language", "Python")  # only sets if missing

full_name = f"{profile['first_name']} {profile['last_name']}"
print(full_name)
```

- `setdefault` skriver inte över ett värde som redan finns.
- Säkerställ nycklarna eller använd `get` med standardvärden när strängar byggs.

### Formateringsfunktion

**Frivillig funktionsförhandsblick:** `def` och `return` lärs ut i [kapitel 11](../chapter-11-functions/README.sv.md). Kopiera hela mönstret om det hjälper eller hoppa över det utan att påverka grundkontrollen.

```python illustrative
def format_profile(data):
    first = data.get("first_name", "Unknown")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Uppdatera, slå samman och rensa

```python runnable
base_config = {"timeout": 5, "retries": 3}
user_config = {"timeout": 10, "region": "eu-west"}

final_config = base_config | user_config  # Python 3.9+: creates a new dict
base_config.update({"logging": True})      # modifies in place

print(final_config)
print(base_config)
```

```python runnable
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # returns the removed value
print(legacy)

del feature_flags["beta"]
print(feature_flags)
```

- Använd `|` eller `|=` för sammanslagning utan egna loopar.
- `pop` tar bort och returnerar värdet, användbart när data flyttas.
- `del` tar bort utan returvärde när det borttagna inte behövs.

---

## 4. Iterera och bygga härledd data

```python runnable
permissions = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for user, role in permissions.items():
    print(f"{user} → {role}")

roles = {role for role in permissions.values()}  # set comprehension
print(roles)

greetings = {user: f"Hello, {user.title()}" for user in permissions.keys()}
print(greetings)
```

- `items()` ger par av nyckel och värde.
- Dictionary comprehensions (`{key: value for ...}`) bygger nya mappings tydligt.

---

## 5. Nästlade strukturer

```python runnable
users = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, details in users.items():
    status = "active" if details.get("active") else "inactive"
    print(f"{username}: {status}")
```

```python runnable
# Dictionaries inside lists
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

failed = [item for item in api_response["results"] if item["status"] != "ok"]
print(failed)
```

- Validera nycklar före indexering; externa API:er kan utelämna dem.
- Kapsla gärna djup nästlad åtkomst i hjälpfunktioner.

---

## 6. Validering och tester

```python runnable
# profiles.py
def validate_profile(data):
    required_fields = {"username", "email"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if "@" not in data["email"]:
        raise ValueError("Invalid email")
    return True
```

```python illustrative
# tests/test_profiles.py
import pytest
from profiles import validate_profile

def test_validate_profile_success():
    payload = {"username": "noor", "email": "noor@example.com"}
    assert validate_profile(payload) is True

def test_validate_profile_detects_missing_fields():
    with pytest.raises(ValueError) as exc:
        validate_profile({"username": "noor"})
    assert "email" in str(exc.value)
```

Testerna garanterar minimifälten innan data når en view eller serializer.

---

## Vägledda övningar (med TODO)

1. **4-1 · Offentlig profil**

   ```python todo
   profile = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: add first_name and last_name fields
   # TODO 2: print a formatted message using get with defaults
   # TODO 3: add a "links" field that is another dict (github, linkedin)
   ```

   *Ledtråd*: använd `setdefault` för att inte skriva över befintlig data.

2. **4-2 · Sammanslagen konfiguration**

   ```python todo
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: create merge_config(base, custom) -> dict
   # TODO 2: make sure base is not modified (use a copy)
   # TODO 3: write a test that confirms base stays the same after merge
   ```

   *Ledtråd*: använd `base | custom` eller `copy()` följt av `update()`.

3. **4-3 · Fältgranskning**

   ```python todo
   record = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: write requires_fields(record, required_fields)
   # TODO 2: the function must return a tuple (valid, missing)
   # TODO 3: add a test that confirms optional extra fields are allowed
   ```

   *Ledtråd*: återanvänd mängdoperationen `required_fields - record.keys()`.

---

## Vanliga misstag

- **Anta att en nyckel finns** ger `KeyError`; använd `get` eller validera.
- **Mutera samma dictionary på flera ställen** skapar sidoeffekter; kopiera med `dict.copy()` eller `|`.
- **Blanda listor och dictionaries** leder till talindex på en `dict` eller nyckelindex på en lista.
- **Inte normalisera nycklar** gör att olika skiftläge skapar dubletter.

---

## Förklarade lösningar

1. **Offentlig profil**: `profile.setdefault("first_name", "")` fyller utan att förlora data; bygg med `profile.get("first_name", "Unknown")` för att undvika fel.
2. **Sammanslagen konfiguration**: skapa `merged = base | custom`, eller kopiera och uppdatera, och testa att `base` förblir oförändrad.
3. **Fältgranskning**: `missing = required - record.keys()` och eventuellt `extra = record.keys() - required` ger tydliga felmeddelanden.

---

## Kontrollpunkt och självbedömning

### Grunduppgift 4-0

Slutför starten med enbart direkta dictionary-operationer:

```python todo
profile = {"username": "alba", "email": "alba@example.test"}
# TODO 1: update email and add one preference without changing profile
# TODO 2: merge profile and preference into a new dictionary
# TODO 3: remove the preference from the merged dictionary and print both
```

*Ledtråd*: använd nyckeltilldelning, `|`, `pop` och `get`; ingen funktion, loop, set, tuple, exceptionhantering eller testramverk behövs.

### Förklarad lösning

Verifiera normalvägen för uppdatering, sammanslagning och borttagning:

```python runnable
profile = {"username": "alba", "email": "alba@example.test"}
profile["email"] = "new@example.test"
preferences = {"theme": "dark"}
merged = profile | preferences
removed = merged.pop("theme")
print(profile)
print(merged)
print(removed)
```

Verifiera gränsen med en tom dictionary genom tolerant åtkomst:

```python runnable
empty_profile = {}
print(empty_profile.get("timezone", "UTC"))
print(empty_profile)
```

Spara tre bevis: normalutskriften, standardvärdet vid den tomma gränsen och tidigare förväntad `KeyError` direkt följd av körbar återhämtning med `get`. Reflektera i en mening: när är strikt `[]` bättre än tolerant `get`?


Kör uppgift 4-0 och jämför originaldictionaryn med den sammanslagna kopian. Kör sedan avsiktlig åtkomst till en saknad nyckel en gång, läs `KeyError` och återhämta dig med det intilliggande `get`-exemplet. Använd ingen funktion, loop, exceptionhantering, set, tuple eller testramverk.

Ge dig en poäng per kriterium:
- **Normalväg:** uppdatering, sammanslagning och `pop` ger förutsagda värden.
- **Gräns:** tolerant åtkomst till tom dictionary returnerar `"UTC"` utan ändring.
- **Återhämtning:** förväntad `KeyError` följs direkt av fungerande `get`-åtkomst.
- **Verifiering:** utskrivet original och kopia visar vilka operationer som muterade data.
- **Förklaring:** du motiverar strikt `[]` mot tolerant `get` för en konkret nyckel.

Grundvägen är klar vid 4/5 eller 5/5. Annars repeterar du uppgift 4-0 och fel/återhämtning. Funktioner, iteration, nästlade externa poster, valideringshjälpare, exceptions och pytest är bevis för senare vägar.

---

## Sammanfattning

Du har deklarerat, läst, slagit samman och validerat dictionaries, itererat dem och hanterat nästlade strukturer. Du vet när `[]` respektive `get` passar, hur `pop` flyttar ett värde och hur en payload kontrolleras före bearbetning.

## Avslutande reflektion

Varje API använder dictionaries för data. Nu kan du strukturera dem varsamt, skydda dig mot saknade nycklar och testa mot regressioner. Nästa kapitel tar upp `set`, som passar deduplicering och medlemskap i växande samlingar.
