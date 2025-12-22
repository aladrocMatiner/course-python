# Capítol 16 · Entorns, dependències i projectes reproduïbles

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Configuraràs entorns virtuals (`venv`), instal·laràs dependències amb `pip`, gestionaràs `requirements.txt` / `pyproject.toml` i aprendràs a carregar variables d’entorn per a configuració segura. Practicarem amb un mini projecte i un fitxer `.env`.

## Objectius d’aprenentatge
- Crear i activar entorns virtuals en Windows/macOS/Linux.
- Instal·lar llibreries i fixar versions.
- Exportar dependències amb `pip freeze`.
- Carregar secrets amb variables d’entorn (i no al repo).

---

## 1. Crear i activar `venv`

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Truc útil:
```bash
python -m pip install requests
```

---

## 2. `requirements.txt`

```bash
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## 3. Variables d’entorn

```python
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

### `.env` amb `python-dotenv`
```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

---

## Errors comuns
- Oblidar activar `.venv` abans d’instal·lar.
- No versionar `requirements.txt`.
- Pujar `.env` amb secrets.

---

## Resum
Ara saps aïllar dependències i carregar configuració de manera segura. Això evita el “funciona a la meva màquina”.
