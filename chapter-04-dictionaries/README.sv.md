# Kapitel 4 · Ordböcker (nyckel–värde)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig `dict` (ordbok): hur du lagrar data som nyckel → värde, läser säkert med `get`, uppdaterar, tar bort och validerar att “payloads” har obligatoriska fält.

---

## Skapa och läsa
```python
usuario = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(usuario["username"])              # strikt
print(usuario.get("timezone", "UTC"))   # tolerant med default
```

---

## Uppdatera och slå ihop
```python
config_base = {"timeout": 5, "retries": 3}
config_usuario = {"timeout": 10, "region": "eu-west"}

config_final = config_base | config_usuario  # Python 3.9+
config_base.update({"logging": True})
```

---

## Validera obligatoriska fält
```python
def validar_perfil(datos):
    campos_requeridos = {"username", "email"}
    faltantes = campos_requeridos - datos.keys()
    if faltantes:
        raise ValueError(f"Faltan campos: {sorted(faltantes)}")
    if "@" not in datos["email"]:
        raise ValueError("Email inválido")
    return True
```

---

## Sammanfattning
Ordböcker är grunden för JSON och API‑data. Nästa kapitel: mängder (sets) för att ta bort dubbletter och kolla medlemskap snabbt.
