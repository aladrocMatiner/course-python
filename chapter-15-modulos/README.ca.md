# Capítol 15 · Mòduls, paquets i organització del codi

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a dividir un projecte en fitxers i carpetes, importar funcions i classes, crear paquets reutilitzables i evitar importacions circulars. Simularem una miniaplicació amb els mòduls `dominio`, `servicios` i `cli` perquè vegis com es connecten.

## Itinerari d'aprenentatge
1. **Model mental**: un fitxer `.py` és un mòdul.
2. **Imports bàsics**: `import` i `from ... import ...`.
3. **Carpetes com a paquets**: `__init__.py`, imports relatius i `PYTHONPATH`.
4. **Estructura de projecte recomanada**.
5. **Evitar cicles d'importació**.
6. **Packaging lleuger** amb `if __name__ == "__main__"`.

## Objectius d'aprenentatge
- Organitzar el codi en mòduls coherents.
- Importar funcions i classes d'altres fitxers en lloc de duplicar lògica.
- Crear paquets amb `__init__.py` i entendre els imports relatius.
- Detectar i corregir importacions circulars.
- Preparar un mòdul com a punt d'entrada net.

## Per què és important
Els projectes reals no caben en un únic fitxer. Separar responsabilitats facilita les proves, la reutilització i la col·laboració.

### Miniaventura
Imagina que equips diferents creen els personatges, els nivells i la música del teu joc preferit. Si tot fos en un sol fitxer, col·laborar seria impossible. Els mòduls són com habitacions endreçades: tothom sap on correspon cada tasca i després és fàcil trobar-la.

### Com practicar aquest capítol
1. Crea `saludos.py` i `app.py` dins la mateixa carpeta.
2. Executa `python app.py`.
3. Si apareix un error, llegeix-ne el nom i el número de línia. Equivocar-se durant la pràctica és normal.

## Prerequisits
Capítols previs recomanats: 11, 12, 13.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

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

## 3. Nivell extra: una estructura més professional (opcional)
Si tot just comences, pots saltar aquesta secció. Si vols treballar amb una estructura semblant a la d'un projecte real, aquesta distribució és útil:

```text illustrative
project/
├── src/
│   ├── __init__.py
│   ├── dominio/
│   │   ├── __init__.py
│   │   └── pedidos.py
│   ├── servicios/
│   │   ├── __init__.py
│   │   └── descuentos.py
│   └── cli.py
└── tests/
```

- `src/` conté el codi i `tests/` manté les proves separades.
- Com que aquest disseny didàctic converteix `src` en paquet, usa `from src.dominio.pedidos import Pedido`.

### Executar des de l'arrel del projecte
Quan treballes amb paquets, executa des de la carpeta arrel. Un patró habitual és:

```bash illustrative
python -m src.cli
```

### Verificació del paquet
```bash illustrative
python -c "from src.dominio.pedidos import Pedido; print(Pedido.__name__)"
```

Això vol dir «executa `cli.py` com a part del paquet `src`» i fa que els imports siguin més fiables.

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
   # TODO 1: create dominio/productos.py with class Producto
   # TODO 2: create servicios/precios.py and use Producto
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.
   Extra: afegeix el mètode `aplicar_descuento(porcentaje)` a `Producto`.

2. **15-2 · CLI modular**
   ```python todo
   # TODO 1: create cli.py that imports functions from servicios
   # TODO 2: run python -m cli to validate the import path
   ```
   Pista: si obtens `ModuleNotFoundError`, comprova que executes des de la carpeta correcta.

3. **15-3 · Corregir un cicle d'importació**
   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.
   Cas límit: escriu una prova que importi tots dos mòduls i confirmi que el cicle ha desaparegut.

---

## Errors habituals
- Fer imports relatius incorrectes, com `from .. import`, sense `__init__.py`.
- Duplicar codi entre mòduls en lloc d'importar-lo.
- Executar des de carpetes diferents i trencar les rutes; prefereix `python -m`.

---

## Solucions explicades
1. **Domini i serveis**: cada àrea té el seu mòdul; els serveis importen el domini per no barrejar responsabilitats.
2. **CLI modular**: `cli.py` només coordina; la lògica de negoci viu a `servicios` i és més fàcil de provar.
3. **Corregir el cicle**: moure les funcions compartides a `utils` elimina la dependència circular i aclareix les capes.

---

## Resum
Dividir el codi en mòduls i paquets manté el projecte organitzat. Ara pots importar només allò que necessites i crear punts d'entrada nets.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Pregunta't sempre: «On hauria de viure aquesta lògica?». Uns mòduls clars et preparen per a projectes més grans i frameworks com Django.
