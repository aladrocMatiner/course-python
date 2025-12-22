# Kapitel 15 · Moduler, paket och struktur

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig dela upp kod i flera `.py`‑filer (moduler), skapa paket med `__init__.py`, importera på ett säkert sätt och undvika cirkulära imports.

---

## Modul‑exempel
`saludos.py`
```python
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python
import saludos
print(saludos.hola("Ada"))
```

---

## Entry point
```python
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

---

## Sammanfattning
Bra struktur gör större projekt möjliga och testbara. Nästa kapitel: virtuella miljöer och beroenden.
