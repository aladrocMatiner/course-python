# Kapitel 12 · OOP: klasser och objekt

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi skapar våra första klasser i Python: attribut, metoder, `__init__`, representation (`__repr__`/`__str__`), lite arv/komposition och en kort del om att serialisera objekt (t.ex. till dict/JSON).

---

## En första klass
```python
class Usuario:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email
        self.activo = True

    def desactivar(self):
        self.activo = False
```

Exempel:
```python
noor = Usuario("Noor", "noor@example.com")
noor.desactivar()
print(noor.activo)  # False
```

---

## Serialisering (till dict)
```python
class Pedido:
    def __init__(self, id, total, items):
        self.id = id
        self.total = total
        self.items = items

    def to_dict(self):
        return {"id": self.id, "total": self.total, "items": self.items}
```

---

## Sammanfattning
Klasser hjälper dig modellera “saker” i programmet. Nästa kapitel: filer och streams.
