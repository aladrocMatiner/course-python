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
- Recórrer diccionaris i transformar-los en estructures derivades.
- Combinar diccionaris i gestionar claus anidades amb coherència.
- Escriure proves que validin camps obligatoris.

## Per què importa
Els diccionaris són la base de JSON, el format amb què les APIs modernes envien dades. Dominar `dict` vol dir manipular payloads, respostes HTTP, paràmetres i configuracions sense fricció. També et prepara per serialitzar/deserialitzar dades entre Python i altres sistemes.

### Mini aventura
Un diccionari és com l’agenda del mòbil: busques un nom (clau) i et dóna una dada (valor). La gràcia és que el programa pot trobar el que vols “al moment” sense recórrer una llista sencera.

---

## 1. Model mental: diccionaris com mapes
Pensa en un diccionari com una agenda: busques una clau (nom) i recuperes un valor (dada).

```python
usuario = {
    "username": "ada",
    "email": "ada@example.com",
    "roles": ["admin", "editor"],
}

print(usuario["username"])  # acceso estricto
print(usuario.get("timezone", "UTC"))  # acceso tolerante con valor por defecto
```

- Les claus han de ser immutables (strings, números, tuples immutables). Els valors poden ser qualsevol objecte.
- Usa `get` quan no estiguis segura/o que la clau existeix: evita `KeyError` i posa defaults coherents.

---

## 2. Crear, llegir i normalitzar valors

```python
perfil = {}
perfil["first_name"] = "Grace"
perfil["last_name"] = "Hopper"
perfil.setdefault("language", "Python")  # sólo asigna si no existe

nombre_completo = f"{perfil['first_name']} {perfil['last_name']}"
print(nombre_completo)
```

- `setdefault` evita sobreescriure valors ja definits.
- Quan construeixis cadenes, valida claus o usa `get` amb defaults.

### Funció de format
```python
def formatear_perfil(data):
    first = data.get("first_name", "Desconocido")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Actualitzar, fusionar i netejar diccionaris

```python
config_base = {"timeout": 5, "retries": 3}
config_usuario = {"timeout": 10, "region": "eu-west"}

config_final = config_base | config_usuario  # Python 3.9+: crea un nuevo dict
config_base.update({"logging": True})        # modifica en sitio

print(config_final)
print(config_base)
```

```python
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

```python
permisos = {"alice": "admin", "bob": "editor", "carol": "viewer"}

for usuario, rol in permisos.items():
    print(f"{usuario} → {rol}")

roles = {rol for rol in permisos.values()}  # set por comprensión
print(roles)

saludos = {user: f"Hola, {user.title()}" for user in permisos.keys()}
print(saludos)
```

- `items()` dona parelles clau-valor.
- Les comprensions de diccionari (`{clau: valor for ...}`) creen mapes derivats de manera elegant.

---

## 5. Estructures anidades

```python
usuarios = {
    "ada": {"email": "ada@example.com", "active": True},
    "linus": {"email": "linus@example.com", "active": False},
}

for username, detalle in usuarios.items():
    estado = "activo" if detalle.get("active") else "inactivo"
    print(f"{username}: {estado}")
```

```python
# Diccionarios dentro de listas
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

fallidos = [item for item in api_response["results"] if item["status"] != "ok"]
print(fallidos)
```

- Valida que les claus existeixin abans d’indexar; APIs externes poden ometre-les.
- Per profunditats grans, crea helpers que encapsulin l’accés a claus anidades.

---

## 6. Validació i proves

```python
# profiles.py
def validar_perfil(datos):
    campos_requeridos = {"username", "email"}
    faltantes = campos_requeridos - datos.keys()
    if faltantes:
        raise ValueError(f"Faltan campos: {sorted(faltantes)}")
    if "@" not in datos["email"]:
        raise ValueError("Email inválido")
    return True
```

```python
# tests/test_profiles.py
import pytest
from profiles import validar_perfil

def test_validar_perfil_exitoso():
    payload = {"username": "ada", "email": "ada@example.com"}
    assert validar_perfil(payload) is True

def test_validar_perfil_detecta_campos_faltantes():
    with pytest.raises(ValueError) as exc:
        validar_perfil({"username": "ada"})
    assert "email" in str(exc.value)
```

Les proves garanteixen que el diccionari té el mínim necessari abans d’entrar a una vista o serializer.

---

## Exercicis guiats (amb TODOs)
1. **4-1 · Perfil públic**
   ```python
   perfil = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: afegeix first_name i last_name
   # TODO 2: imprimeix un missatge formatejat usant get amb defaults
   # TODO 3: afegeix un camp "links" que sigui un altre dict (github, linkedin)
   ```
   *Pista*: usa `setdefault` per no sobreescriure dades.

2. **4-2 · Configuració combinada**
   ```python
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: crea merge_config(base, custom) -> dict
   # TODO 2: assegura que base no es modifica (fes una còpia)
   # TODO 3: escriu una prova que confirmi que base queda igual
   ```
   *Pista*: `base | custom` o `copy()` + `update()`.

3. **4-3 · Auditoria de camps**
   ```python
   registro = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: escriu requires_fields(registro, campos_obligatorios)
   # TODO 2: retorna una tupla (valid, faltants)
   # TODO 3: afegeix una prova per confirmar que camps extra opcionals no trenquen res
   ```
   *Pista*: `campos_obligatorios - registro.keys()`.

---

## Errors comuns
- Assumir que una clau existeix ⇒ `KeyError`. Usa `get` o valida abans.
- Mutar el mateix diccionari a molts llocs ⇒ efectes secundaris. Fes còpies (`dict.copy()`, operador `|`).
- Confondre llistes amb diccionaris ⇒ indexar amb números quan tens un `dict` (o al revés).
- No normalitzar claus ⇒ majúscules/minúscules inconsistents generen duplicats.

---

## Explicació de solucions
1. **Perfil públic**: `perfil.setdefault("first_name", "")` omple dades sense perdre les prèvies; usa `get` amb defaults per evitar errors.
2. **Configuració combinada**: crea `merged = base | custom` (o `copy()` + `update()`) i comprova amb una prova que `base` no canvia.
3. **Auditoria**: `missing = required - registro.keys()` (i opcionalment `extra = registro.keys() - required`) ajuda a fer missatges d’error clars.

---

## Resum
Has practicat declarar, llegir, fusionar i validar diccionaris, recórrer-los i gestionar estructures anidades. Ja saps quan usar `[]` vs `get`, com moure claus amb `pop` i com comprovar que un payload està complet abans de processar-lo.

## Reflexió final
Cada API que construeixis es recolza en diccionaris. Ara pots estructurar-los amb cura, protegir-te de claus absents i escriure proves per evitar regressions. El següent capítol se centra en `set`, perfecte per deduplicar i raonar sobre pertinença.
