# Capítol 16 · Entorns, dependències i projectes reproduïbles

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Configuraràs entorns virtuals amb `venv`, instal·laràs dependències amb `pip`, gestionaràs `requirements.txt` i `pyproject.toml` i aprendràs a carregar variables d'entorn per configurar el projecte de manera segura. Practicarem amb un miniprojecte que instal·la `requests` i utilitza un fitxer `.env`.

## Itinerari d'aprenentatge
1. **Per què cal aïllar les dependències**.
2. **Crear i activar `venv`**.
3. **Instal·lar paquets amb `pip`**.
4. **Fixar versions amb `requirements.txt`**.
5. **Introducció a `pyproject.toml`**.
6. **Variables d'entorn amb `os.environ` i `.env`**.

## Objectius d'aprenentatge
- Crear i activar entorns virtuals a Windows, macOS i Linux.
- Instal·lar llibreries i fixar-ne les versions per reproduir projectes.
- Exportar i importar dependències amb `pip freeze`.
- Carregar configuració sensible des de variables d'entorn.

## Per què és important
Sense entorns aïllats, un projecte pot espatllar-ne un altre. Controlar les dependències és la base d'un treball en equip professional.

### Miniaventura
Imagina cada entorn virtual com una caixa de LEGO amb les peces exactes d'un projecte. Si barreges les peces de tots els jocs, construir qualsevol cosa es torna caòtic. Amb `venv`, cada joc queda separat i pots reconstruir el model sense perdre peces.

## Prerequisits
Capítols previs recomanats: 15.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1. Crear i activar `venv`

```bash illustrative
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

- Veuràs `(.venv)` al terminal quan l'entorn sigui actiu.
- Executa `deactivate` per sortir-ne.

Si no tens clar quin `pip` estàs fent servir, aquest patró és fiable:
```bash illustrative
python -m pip install requests
```
Garanteix que instal·les al mateix Python que estàs executant.

---

## 2. Instal·lar paquets

```bash illustrative
pip install requests
python -c "import requests; print(requests.__version__)"
```

- Cada entorn té el seu propi `pip`.

### `requirements.txt`
```bash illustrative
pip freeze > requirements.txt
git add requirements.txt
```

- En una altra màquina, instal·la amb `pip install -r requirements.txt`.

---

## 3. `pyproject.toml` (opcional però modern)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- Eines com `pip-tools`, `poetry` o `pdm` utilitzen aquest format.

---

## 4. Variables d'entorn

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- No desis secrets al repositori.

### `.env` amb `python-dotenv`
```bash illustrative
pip install python-dotenv
```

```python illustrative
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.environ["API_KEY"]
```

- Crea `.env` amb `API_KEY=value` i afegeix-lo a `.gitignore`.

Un `.gitignore` habitual:
```gitignore illustrative
.venv/
.env
__pycache__/
```

---

## Exercicis guiats (amb TODO)
1. **16-1 · Preparar l'entorn**
   ```bash todo
   # TODO 1: create .venv and activate it
   # TODO 2: install requests and python-dotenv
   # TODO 3: generate requirements.txt
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

2. **16-2 · Script configurat**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **16-3 · `pyproject` mínim**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.
   Nota: és un nivell extra. Si comences, `requirements.txt` ja és una opció molt bona.

---

## Errors habituals
- Oblidar activar l'entorn abans d'instal·lar paquets.
- No versionar `requirements.txt` i perdre el control de versions.
- Pujar fitxers `.env` amb secrets; protegeix-los amb `.gitignore`.

---

## Solucions explicades
1. **Preparar l'entorn**: `python -m venv .venv` i `pip freeze > requirements.txt` fan que el projecte sigui reproduïble.
2. **Script configurat**: `load_dotenv()` permet que `os.environ` llegeixi variables des d'un fitxer local.
3. **`pyproject`**: documentar les instruccions d'instal·lació ajuda tot l'equip a instal·lar de la mateixa manera.

---

## Resum
Ara saps crear entorns, instal·lar dependències i mantenir la configuració segura amb variables d'entorn.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Aquestes bases et permeten compartir projectes sense sentir «a la meva màquina funciona». Fes-les servir cada vegada que comencis un repositori.
