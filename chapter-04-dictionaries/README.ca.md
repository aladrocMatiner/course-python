# Capítol 4 · Diccionaris (dades clau-valor)

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a modelar informació estructurada amb diccionaris (`dict`). Treballarem amb perfils d’usuari, configuracions i respostes tipus JSON, molt típiques en backend. Practicarem com crear, actualitzar, fusionar i validar diccionaris abans d’exposar-los com a API o desar-los.

## Ordre pedagògic
1. **Model mental**: diccionaris com mapes entre claus i valors.
2. **Crear i accedir**: lectura segura (`[]` vs `get`) i format amigable.
3. **Actualitzar i eliminar**: `.update`, `del`, `pop` i valors per defecte.
4. **Recórrer**: `keys`, `values`, `items`, comprensions de diccionari.
5. **Estructures anidades**: llistes de dicts i dicts dins de dicts.
6. **Validació i proves**: assegurar que els payloads tenen camps requerits.

## Objectius d’aprenentatge
- Declarar diccionaris per representar entitats reals (usuaris, comandes, configuracions).
- Accedir i actualitzar claus amb seguretat (lectura estricta vs tolerant).
- A la ruta professional opcional, recórrer diccionaris i transformar-los en estructures derivades.
- Combinar diccionaris i gestionar claus anidades amb coherència.
- A la ruta professional opcional, escriure proves que validin camps obligatoris.

## Prerequisits i rutes
- **Prerequisit:** completa el checkpoint del [capítol 3](../chapter-03-lists/README.ca.md). La ruta essencial només necessita fonaments de llistes i variables.
- **Ruta essencial · 45–60 min:** seccions 1–3, ometent el preview opcional de la funció de format, exercici 4-1 i checkpoint. Resultat: crear, llegir, actualitzar, combinar i netejar un diccionari amb sentències directes; no exigeix funcions.
- **Ruta intermèdia · 25–35 min:** estructures anidades i exercici 4-2. Resultat: inspeccionar camps externs absents amb `get` abans d'indexar.
- **Preview professional opcional · 35–45 min:** seccions 4 i 6 i exercici 4-3. Anticipen [condicionals](../chapter-08-conditionals/README.ca.md), [bucles](../chapter-10-loops/README.ca.md), [funcions](../chapter-11-functions/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [pytest](../chapter-18-testing/README.ca.md). Copia els exemples complets o omet-los sense bloquejar el checkpoint essencial.

## Per què importa
Els diccionaris són la base de JSON, el format amb què les APIs modernes envien dades. Dominar `dict` vol dir manipular payloads, respostes HTTP, paràmetres i configuracions sense fricció. També et prepara per serialitzar/deserialitzar dades entre Python i altres sistemes.

### Mini aventura
Un diccionari és com l’agenda del mòbil: busques un nom (clau) i et dóna una dada (valor). La gràcia és que el programa pot trobar el que vols “al moment” sense recórrer una llista sencera.

## Predicció abans d'executar
Al primer exemple `user`, prediu el resultat de l'accés estricte a `"username"`, de l'accés tolerant a `"timezone"` absent i de l'accés estricte a aquesta clau absent. Executa només els dos primers i explica com `get` ofereix recuperació davant de `KeyError`.

---

## 1. Model mental: diccionaris com mapes
Pensa en un diccionari com una agenda: busques una clau (nom) i recuperes un valor (dada).

```python runnable
user = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(user["username"])  # acceso estricto
print(user.get("timezone", "UTC"))  # acceso tolerante con valor por defecto
```

L’accés estricte a una clau absent és evidència útil. Aquest bloc provoca `KeyError` expressament:

<!-- bookcheck: expect-error="KeyError" -->
```python expected-error
user = {"username": "noor"}
print(user["timezone"])
```

Recupera’t amb accés tolerant i un valor per defecte explícit:

```python runnable
user = {"username": "noor"}
print(user.get("timezone", "UTC"))
```

- Les claus han de ser **hashable**, és a dir, etiquetes de cerca estables per a Python. Usa cadenes o nombres a la ruta essencial. Les claus tuple són un preview opcional posterior al [Capítol 6](../chapter-06-tuples/README.ca.md), i només funcionen si tots els valors també són hashable. Els valors poden ser qualsevol objecte.
- Usa `get` quan no estiguis segura/o que la clau existeix: evita `KeyError` i posa defaults coherents.

---

## 2. Crear, llegir i normalitzar valors

```python runnable
profile = {}
profile["first_name"] = "Grace"
profile["last_name"] = "Hopper"
profile.setdefault("language", "Python")  # sólo asigna si no existe

full_name = f"{profile['first_name']} {profile['last_name']}"
print(full_name)
```

- `setdefault` evita sobreescriure valors ja definits.
- Quan construeixis cadenes, valida claus o usa `get` amb defaults.

### Funció de format
**Preview opcional de funcions:** `def` i `return` s’ensenyen al [capítol 11](../chapter-11-functions/README.ca.md). Copia el patró complet només si et resulta útil o omet-lo sense afectar el checkpoint essencial.

```python illustrative
def format_profile(data):
    first = data.get("first_name", "Desconocido")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Actualitzar, fusionar i netejar diccionaris

```python runnable
base_config = {"timeout": 5, "retries": 3}
user_config = {"timeout": 10, "region": "eu-west"}

final_config = base_config | user_config  # Python 3.9+: crea un nuevo dict
base_config.update({"logging": True})        # modifica en sitio

print(final_config)
print(base_config)
```

```python runnable
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # devuelve el valor eliminado
print(legacy)

del feature_flags["beta"]
print(feature_flags)
```

- Usa `|` o `|=` per fusionar configuracions sense bucles.
- `pop` elimina i retorna (útil per “moure” una clau a un altre lloc).
- `del` elimina sense retornar.

---

## 4. Recórrer diccionaris i crear derivats

```python runnable
permissions = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for user, role in permissions.items():
    print(f"{user} → {role}")

roles = {role for role in permissions.values()}  # set por comprensión
print(roles)

greetings = {user: f"Hola, {user.title()}" for user in permissions.keys()}
print(greetings)
```

- `items()` dona parelles clau-valor.
- Les comprensions de diccionari (`{clau: valor for ...}`) creen mapes derivats de manera elegant.

---

## 5. Estructures anidades

```python runnable
users = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, details in users.items():
    status = "actiu" if details.get("active") else "inactiu"
    print(f"{username}: {status}")
```

```python runnable
# Diccionarios dentro de listas
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

- Valida que les claus existeixin abans d’indexar; APIs externes poden ometre-les.
- Per profunditats grans, crea helpers que encapsulin l’accés a claus anidades.

---

## 6. Validació i proves

```python runnable
# profiles.py
def validate_profile(data):
    required_fields = {"username", "email"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Falten camps: {sorted(missing)}")
    if "@" not in data["email"]:
        raise ValueError("Email inválido")
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

Les proves garanteixen que el diccionari té el mínim necessari abans d’entrar a una vista o serializer.

---

## Exercicis guiats (amb TODOs)
1. **4-1 · Perfil públic**
   ```python todo
   profile = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: afegeix first_name i last_name
   # TODO 2: imprimeix un missatge formatejat usant get amb defaults
   # TODO 3: afegeix un camp "links" que sigui un altre dict (github, linkedin)
   ```
   *Pista*: usa `setdefault` per no sobreescriure dades.

2. **4-2 · Configuració combinada**
   ```python todo
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: crea merge_config(base, custom) -> dict
   # TODO 2: assegura que base no es modifica (fes una còpia)
   # TODO 3: escriu una prova que confirmi que base queda igual
   ```
   *Pista*: `base | custom` o `copy()` + `update()`.

3. **4-3 · Auditoria de camps**
   ```python todo
   record = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: escriu requires_fields(record, required_fields)
   # TODO 2: retorna una tupla (valid, missing)
   # TODO 3: afegeix una prova per confirmar que camps extra opcionals no trenquen res
   ```
   *Pista*: `required_fields - record.keys()`.

---

## Errors comuns
- Assumir que una clau existeix ⇒ `KeyError`. Usa `get` o valida abans.
- Mutar el mateix diccionari a molts llocs ⇒ efectes secundaris. Fes còpies (`dict.copy()`, operador `|`).
- Confondre llistes amb diccionaris ⇒ indexar amb números quan tens un `dict` (o al revés).
- No normalitzar claus ⇒ majúscules/minúscules inconsistents generen duplicats.

---

## Explicació de solucions
1. **Perfil públic**: `profile.setdefault("first_name", "")` omple dades sense perdre les prèvies; usa `profile.get("first_name", "Desconeguda")` amb un valor per defecte per evitar errors.
2. **Configuració combinada**: crea `merged = base | custom` (o `copy()` + `update()`) i comprova amb una prova que `base` no canvia.
3. **Auditoria**: `missing = required - record.keys()` (i opcionalment `extra = record.keys() - required`) ajuda a fer missatges d’error clars.

---

## Checkpoint i autoavaluació

### Tasca essencial 4-0

Completa aquest inici usant només operacions directes de diccionari:

```python todo
profile = {"username": "alba", "email": "alba@example.test"}
# TODO 1: update email and add one preference without changing profile
# TODO 2: merge profile and preference into a new dictionary
# TODO 3: remove the preference from the merged dictionary and print both
```

*Pista*: usa assignació per clau, `|`, `pop` i `get`; no necessites funcions, bucles, sets, tuples, gestió d’excepcions ni frameworks de prova.

### Solució explicada

Verifica la ruta normal d’actualització, combinació i eliminació:

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

Verifica el límit del diccionari buit amb accés tolerant:

```python runnable
empty_profile = {}
print(empty_profile.get("timezone", "UTC"))
print(empty_profile)
```

Conserva tres evidències: sortida normal, default del límit buit i `KeyError` esperat anterior seguit de la recuperació executable amb `get`. Reflexiona en una frase: quan és preferible l’accés estricte `[]` al tolerant `get`?

Executa la tasca 4-0 i compara el diccionari original amb la còpia combinada. Després executa una vegada l’accés intencional a clau absent, llegeix `KeyError` i recupera’t amb l’exemple `get` adjacent. No usis funcions, bucles, gestió d’excepcions, sets, tuples ni frameworks de prova.

Suma un punt per criteri:
- **Ruta normal:** actualització, combinació i `pop` produeixen els valors predits.
- **Límit:** l’accés tolerant al diccionari buit retorna `"UTC"` sense canviar-lo.
- **Recuperació:** al `KeyError` esperat el segueix immediatament un accés `get` funcional.
- **Verificació:** original i còpia impresos demostren quines operacions han mutat dades.
- **Explicació:** justifiques `[]` estricte davant `get` tolerant per a una clau concreta.

La ruta essencial acaba amb 4/5 o 5/5. Si no, repeteix la tasca 4-0 i el parell error/recuperació. Funcions, iteració, registres externs niats, ajudants de validació, excepcions i pytest són evidència de rutes posteriors.

---

## Resum
Has practicat declarar, llegir, fusionar i validar diccionaris, recórrer-los i gestionar estructures imbricades. Ja saps quan usar `[]` o `get`, com moure claus amb `pop` i com comprovar que un payload està complet abans de processar-lo.

## Reflexió final
Cada API que construeixis es recolza en diccionaris. Ara pots estructurar-los amb cura, protegir-te de claus absents i escriure proves per evitar regressions. El següent capítol se centra en `set`, perfecte per deduplicar i raonar sobre pertinença.
