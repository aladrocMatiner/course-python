# Kapitel 5 · Mängder (sets) och medlemskap

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi använder `set` och `frozenset` för att ta bort dubbletter, kolla om något finns i en samling och jämföra samlingar med union/intersection/difference.

---

## Deduplicera + `in`
```python
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print("noor@example.com" in correos_unicos)
```

---

## Mängdoperationer
```python
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}

print(permisos_admin & permisos_editor)  # intersection
print(permisos_admin - permisos_editor)  # difference
```

---

## `frozenset` som nyckel
```python
segmentos = {
    frozenset({"ios", "premium"}): "Campaña A",
}
```

---

## Sammanfattning
Mängder gör det lätt att tänka “inga dubbletter” och “är detta tillåtet?”. Nästa kapitel: tuples och immutabilitet.
