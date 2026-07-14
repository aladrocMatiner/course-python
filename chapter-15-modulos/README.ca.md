# Capítol 15 · Mòduls, paquets i organització del codi

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a dividir un projecte en fitxers i carpetes, importar funcions i classes, crear paquets reutilitzables i evitar importacions circulars. Simularem una miniaplicació amb els mòduls `dominio`, `servicios` i `cli` perquè vegis com es connecten.

## Itinerari d'aprenentatge
1. **Model mental**: un fitxer `.py` és un mòdul.
2. **Imports bàsics**: `import` i `from ... import ...`.
3. **Carpetes com a paquets**: `__init__.py` i imports relatius.
4. **Estructura instal·lable `src/<package>`**.
5. **Evitar cicles d'importació**.
6. **Packaging lleuger** amb `if __name__ == "__main__"`.

## Objectius d'aprenentatge
- Organitzar el codi en mòduls coherents.
- Importar funcions i classes d'altres fitxers en lloc de duplicar lògica.
- Crear paquets amb `__init__.py` i entendre els imports relatius.
- Detectar i corregir importacions circulars.
- Preparar un mòdul com a punt d'entrada net.
- Construir, instal·lar i importar un paquet fora del directori font.

## Per què és important
Els projectes reals no caben en un únic fitxer. Separar responsabilitats facilita les proves, la reutilització i la col·laboració.

### Miniaventura
Imagina que equips diferents creen els personatges, els nivells i la música del teu joc preferit. Si tot fos en un sol fitxer, col·laborar seria impossible. Els mòduls són com habitacions endreçades: tothom sap on correspon cada tasca i després és fàcil trobar-la.

### Com practicar aquest capítol
1. Crea `saludos.py` i `app.py` dins la mateixa carpeta.
2. Executa `python app.py`.
3. Si apareix un error, llegeix-ne el nom i el número de línia. Equivocar-se durant la pràctica és normal.

## Prerequisits
- Funcions, classes, importacions de la biblioteca estàndard i navegació bàsica pel terminal.
- Un entorn local amb CPython 3.11+ i permís per crear una carpeta de projecte d'un sol ús.

## Prediu abans d'executar
Abans d'importar el primer mòdul, prediu quin fitxer proporciona `hola` i quin directori ha de poder trobar Python. Després d'executar l'exemple, inspecciona la ruta del mòdul importat i compara-la amb la predicció.

---

## 1. Mòduls bàsics
`saludos.py`
```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python illustrative
import saludos
print(saludos.hola("Taha"))
```

Sortida esperada:
```text illustrative
Hola Taha!
```

Repte ràpid: substitueix `"Taha"` pel teu nom i torna a executar el programa.

### `from ... import ...`
```python illustrative
from saludos import hola
print(hola("Frej"))
```

- Evita `import *`: fa difícil saber d'on prové cada nom.

---

## 2. Paquets
Estructura:
```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`
```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`
```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`
```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

Executa:
```bash illustrative
python main.py
```

Sortida esperada:
```text illustrative
90.0
```

- El punt `.` indica un import relatiu dins el mateix paquet.
- `__init__.py` pot estar buit; indica a Python que la carpeta és un paquet.

---

## 3. Nivell extra: un layout `src` instal·lable (opcional)
Si tot just comences, pots saltar aquesta secció. En un layout `src` real, `src/` només és un contenidor: el paquet importable viu un nivell per sota. Aquí és `mi_app`; el codi importa `mi_app`, mai `src`.

```text illustrative
project/
├── pyproject.toml
├── src/
│   └── mi_app/
│       ├── __init__.py
│       ├── domain.py
│       └── cli.py
└── tests/
```

`pyproject.toml` indica al backend que descobreixi els paquets sota `src`:

```toml illustrative
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "course-mi-app"
version = "0.1.0"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
where = ["src"]
```

### Construir, instal·lar i verificar des d'un altre lloc
En un entorn virtual nou, instal·la el projecte i canvia deliberadament el directori de treball abans d'importar. Això prova que Python usa la distribució instal·lada i no el checkout accidentalment:

```bash illustrative
# macOS/Linux (outside the checkout):
python -m venv /tmp/course-mi-app-venv
source /tmp/course-mi-app-venv/bin/activate
# Windows PowerShell alternative:
# python -m venv "$env:TEMP\course-mi-app-venv"
# & "$env:TEMP\course-mi-app-venv\Scripts\Activate.ps1"
# Run the remaining commands from project/
python -m pip install .
python -m unittest discover -s tests -v
python -c "import os, tempfile; os.chdir(tempfile.mkdtemp()); import mi_app; print(mi_app.__name__)"
```

La ruta de l'entorn queda deliberadament fora del checkout; desactiva'l i esborra'l en acabar. `pip install .` usa aïllament PEP 517 i pot necessitar obtenir `setuptools>=68` més el requisit `wheel` declarat pel backend d'un índex o d'una memòria cau ja poblada. Per a un laboratori sense xarxa, prepara abans wheels revisats i compatibles per a totes dues entrades de build. Usa `--no-build-isolation` només si el backend i els seus requisits de build ja estan instal·lats i n'has comprovat les versions; aquest fallback no demostra un build aïllat.

L'import ha d'imprimir `mi_app`. Hi ha una còpia completa a [l'exemple `src` instal·lable del capítol 15](examples/src-layout/). Si falla, comprova `python -m pip --version`, reinstal·la en aquell entorn i confirma `src/mi_app/__init__.py`. No afegeixis el checkout a `PYTHONPATH`, perquè amagaria l'error de packaging.

Qui mantingui el llibre pot executar `python -B chapter-15-modulos/examples/src-layout/tools/verify_artifact.py` des de l'arrel del repositori. El verificador construeix una còpia temporal amb PEP 517, inspecciona el contingut i les metadades del wheel, instal·la aquell wheel exacte en un segon entorn i executa `pip check`, l'entry point instal·lat, la prova i un import des d'un directori aliè abans d'esborrar els artefactes temporals. En un laboratori sense xarxa, passa `--wheelhouse RUTA` amb distribucions revisades i compatibles de `setuptools>=68` i `wheel`; no aprovisionar-ne qualsevol és un error de prerequisit, no un build aïllat correcte.

---

## 4. Evitar importacions circulars

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

Si passa, no és culpa teva: és un problema habitual quan els projectes creixen.

Solucions:
- Mou la lògica compartida a un mòdul independent.
- Fes un import local dins una funció per trencar el cicle:
```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```
La idea és que `aplicar_descuento` visqui, per exemple, a `servicios/descuentos.py`.

---

## 5. Punt d'entrada

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

- Això permet executar `python cli.py` o importar `main` a les proves sense que s'executi automàticament.

---

## Exercicis guiats (amb TODO)
1. **15-1 · Separar domini i serveis**
   ```python todo
   # TODO 1: create src/mi_app/dominio.py with class Producto
   # TODO 2: create src/mi_app/precios.py and use Producto
   # TODO 3: add pyproject.toml and install the distribution in a clean venv
   ```
   Extra: afegeix el mètode `aplicar_descuento(porcentaje)` a `Producto`.
   Pista: `src` no és el paquet; fes explícit `mi_app` amb `__init__.py` i importa els objectes de domini en una sola direcció.

2. **15-2 · CLI modular**
   ```python todo
   # TODO 1: create src/mi_app/cli.py that imports functions from servicios
   # TODO 2: after installation, run python -m mi_app.cli to validate the import path
   ```
   Pista: si obtens `ModuleNotFoundError`, comprova que executes des de la carpeta correcta.

3. **15-3 · Corregir un cicle d'importació**
   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   Cas límit: escriu una prova que importi tots dos mòduls i confirmi que el cicle ha desaparegut.
   Pista: mou la dependència compartida més petita a `utils.py` i inicia després un procés de Python nou per provar la importació.

---

## Errors habituals
- Fer imports relatius incorrectes, com `from .. import`, sense `__init__.py`.
- Duplicar codi entre mòduls en lloc d'importar-lo.
- Executar des de carpetes diferents i trencar les rutes; prefereix `python -m`.
- Posar `__init__.py` directament sota `src/` i importar `src`: el paquet real ha de viure sota `src/<package>/` i instal·lar-se.

---

## Solucions explicades
1. **Domini i serveis**: posa els mòduls sota `src/mi_app/`, configura el descobriment a `pyproject.toml`, instal·la en un entorn nou i verifica `import mi_app` des d'un directori temporal.
2. **CLI modular**: `mi_app/cli.py` només coordina; la lògica de negoci viu a `servicios`. Executar `python -m mi_app.cli` després d'instal·lar comprova la ruta d'importació del paquet i continua sent fàcil de provar.
3. **Corregir el cicle**: moure les funcions compartides a `utils` elimina la dependència circular i aclareix les capes.

---

## Resum
Dividir el codi en mòduls i paquets manté el projecte organitzat. Ara pots importar només allò que necessites i crear punts d'entrada nets.

## Punt de control i rúbrica
- **Correcció**: la distribució s'instal·la i el paquet real s'importa fora de l'arrel del projecte.
- **Llegibilitat**: cada nom de mòdul reflecteix una sola responsabilitat.
- **Gestió d'errors**: les fallades d'importació inclouen una ordre reproduïble i una comprovació de recuperació.
- **Verificació**: el mòdul i la importació des d'un altre directori funcionen en un procés nou.
- **Explicació**: descriu per què la direcció de les dependències evita cicles.

## Reflexió final
Pregunta't sempre: «On hauria de viure aquesta lògica?». Uns mòduls clars et preparen per a projectes més grans i frameworks com Django.
