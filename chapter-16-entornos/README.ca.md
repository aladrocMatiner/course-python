# Capítol 16 · Entorns, dependències i projectes reproduïbles

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Configuraràs entorns virtuals amb `venv`, instal·laràs dependències amb `pip`, distingiràs entre `pyproject.toml`, requisits, restriccions, snapshots i fitxers de bloqueig, i aprendràs a carregar variables d'entorn per configurar el projecte de manera segura. Practicarem amb un miniprojecte que instal·la `requests` i utilitza un fitxer `.env`.

## Itinerari d'aprenentatge
1. **Per què cal aïllar les dependències**.
2. **Crear i activar `venv`**.
3. **Instal·lar paquets amb `pip`**.
4. **Registrar dependències amb precisió**: declaracions, versions fixades, restriccions, snapshots i bloquejos.
5. **Introducció a `pyproject.toml`**.
6. **Variables d'entorn amb `os.environ` i `.env`**.

## Objectius d'aprenentatge
- Crear i activar entorns virtuals a Windows, macOS i Linux.
- Instal·lar llibreries i registrar deliberadament les dependències directes.
- Fer servir `pip freeze` com a snapshot específic de l'intèrpret i la plataforma, no com a resolutor ni fitxer de bloqueig.
- Explicar quina evidència més sòlida aporta un bloqueig resolt.
- Carregar configuració sensible des de variables d'entorn.

## Per què és important
Sense entorns aïllats, un projecte pot espatllar-ne un altre. Controlar les dependències és la base d'un treball en equip professional.

### Miniaventura
Imagina cada entorn virtual com una caixa de LEGO amb les peces exactes d'un projecte. Si barreges les peces de tots els jocs, construir qualsevol cosa es torna caòtic. Amb `venv`, cada joc queda separat i pots reconstruir el model sense perdre peces.

## Prerequisits
- Ordres bàsiques de terminal i mòduls del capítol 15.
- CPython 3.11+ amb `venv` i `pip`; instal·lar paquets requereix xarxa, però la pràctica amb variables d'entorn és local.

## Prediu abans d'executar
Abans de crear l'entorn, prediu a quin intèrpret apuntarà `python -m pip` abans i després d'activar-lo. Verifica totes dues rutes i explica després per què una ruta inesperada és un problema de configuració i no un error del paquet.

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
python -m pip install requests
python -c "import requests; print(requests.__version__)"
```

- Cada entorn té el seu propi `pip`.

### `requirements.txt`
```bash illustrative
python -m pip freeze > requirements.txt
git add requirements.txt
```

- Per recrear el snapshot en un altre entorn net: `python -m pip install -r requirements.txt`.
- `pip freeze` informa del que hi ha instal·lat amb la sintaxi d'un fitxer de requisits. No resol un entorn nou ni crea un bloqueig hermètic, i el resultat pot variar entre versions de Python i sistemes operatius.

### Cinc registres amb funcions diferents
- **Declaració del projecte:** `[project].dependencies` expressa requisits directes d'execució, sovint com a intervals compatibles. No registra tot el graf resolt.
- **Versió directa fixada:** `requests==X.Y.Z` fixa una dependència sol·licitada, però per si sola no diu res de totes les dependències transitives.
- **Restricció:** un fitxer de restriccions limita versions si un altre requisit les necessita; una entrada no n'engega la instal·lació. Exemple: `python -m pip install -c constraints.txt requests`.
- **Snapshot de l'entorn:** `pip freeze` captura els paquets instal·lats en l'intèrpret i la plataforma actuals amb format de requisits. És una evidència útil, però no és el resultat d'un resolutor ni un bloqueig multiplataforma.
- **Bloqueig resolt:** una eina de bloqueig registra la resolució completa i el seu àmbit de validesa, sovint amb hashes i marcadors d'entorn. Verifica l'eina i la matriu de destinació exactes abans d'afirmar que alguna cosa és reproduïble; el suport actual de `pip lock` és experimental i la sortida queda limitada a la versió de Python i la plataforma actuals.

---

## 3. Declarar dependències a `pyproject.toml` (opcional però modern)

```toml illustrative
[project]
name = "mi-proyecto"
version = "0.1.0"
dependencies = [
  "requests>=2.31",
]
```

- Això declara un requisit directe compatible a les metadades del paquet. No és un graf congelat de dependències transitives. La verificació de la construcció i de la importació des d'un altre directori pertany a l'exemple instal·lable `src/<package>` del capítol 15.

---

## 4. Variables d'entorn

```python runnable
import os
API_KEY = os.environ.get("API_KEY", "dummy")
```

- No desis secrets al repositori.

### `.env` amb `python-dotenv`
```bash illustrative
python -m pip install python-dotenv
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
   # TODO 3: generate a requirements.txt environment snapshot
   ```
   *Pista*: usa `python -m pip` perquè la instal·lació i el snapshot apuntin a l'intèrpret actiu; registra també la seva versió de Python i plataforma.

2. **16-2 · Script configurat**
   ```python todo
   # TODO 1: create config.py that loads variables from .env
   # TODO 2: use os.environ to read API_KEY
   ```
   *Pista*: crida `load_dotenv()` i, si falta `API_KEY`, falla amb un missatge clar en lloc d'utilitzar silenciosament un valor de producció alternatiu.

3. **16-3 · `pyproject` mínim**
   ```text todo
   # TODO 1: create pyproject.toml with basic dependencies
   # TODO 2: document in README how to install
   # TODO 3: explain why this declaration is not a lock file
   ```
   Nota: és un nivell extra. Si comences, `requirements.txt` ja és una opció molt bona.
   *Pista*: mantén mínima la taula `[project]` i documenta les ordres exactes per crear l'entorn i instal·lar.

---

## Errors habituals
- Oblidar activar l'entorn abans d'instal·lar paquets.
- Anomenar bloqueig multiplataforma una única versió directa fixada o un snapshot de `pip freeze`.
- Esperar que una entrada de restriccions instal·li per si sola un paquet.
- Pujar fitxers `.env` amb secrets; protegeix-los amb `.gitignore`.

---

## Solucions explicades
1. **Preparar l'entorn**: `python -m venv .venv` aïlla el projecte i `python -m pip freeze > requirements.txt` registra un snapshot d'aquell entorn. Reinstal·la'l en un entorn net amb la versió de Python i la plataforma declarades i verifica les importacions; no converteixis aquesta evidència en una afirmació hermètica o multiplataforma.
2. **Script configurat**: `load_dotenv()` permet que `os.environ` llegeixi variables des d'un fitxer local.
3. **`pyproject`**: documenta la dependència directa i les instruccions d'instal·lació, i indica que cal un bloqueig independent generat per un resolutor per congelar el graf complet.

---

## Resum
Ara saps crear entorns, instal·lar dependències i mantenir la configuració segura amb variables d'entorn.

## Punt de control i rúbrica
- **Correcció**: un entorn nou amb la versió de Python i la plataforma declarades instal·la el registre de dependències triat.
- **Llegibilitat**: estan documentades les ordres de preparació i la versió compatible de Python.
- **Errors**: una variable d'entorn absent falla amb claredat i sense revelar secrets.
- **Verificació**: recrea l'entorn i importa cada dependència directa.
- **Explicació**: distingeix aïllament, versions directes fixades, restriccions, snapshots d'entorn, bloquejos resolts i emmagatzematge de secrets.

## Reflexió final
Aquestes bases et permeten compartir projectes sense sentir «a la meva màquina funciona». Fes-les servir cada vegada que comencis un repositori.
