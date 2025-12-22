# Kapitel 16 · Virtuella miljöer och beroenden

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi lär oss `venv`, `pip`, `requirements.txt` och hur man läser konfiguration från miljövariabler (så att hemligheter inte hamnar i git).

---

## Skapa `.venv`
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

---

## Frys beroenden
```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## Miljövariabler
```python
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

---

## Sammanfattning
Isolerade miljöer gör projekten reproducerbara. Nästa kapitel: lätt persistens (CSV/JSON/SQLite).
