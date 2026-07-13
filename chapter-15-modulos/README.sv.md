# Kapitel 15 · Moduler, packages och kodorganisation

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du delar projekt i filer och kataloger, importerar funktioner och klasser, skapar återanvändbara packages och undviker cirkulära imports. En miniapp med `dominio`, `servicios` och `cli` visar kopplingarna.

## Lärväg

1. **Mental modell**: en `.py`-fil är en modul.
2. **Imports**: `import` och `from ... import ...`.
3. **Kataloger som packages**: `__init__.py`, relativa imports och `PYTHONPATH`.
4. **Rekommenderad projektstruktur**.
5. **Undvika importcykler**.
6. **Entry point** med `if __name__ == "__main__"`.

## Lärandemål

- Organisera kod i sammanhängande moduler.
- Importera i stället för att duplicera logik.
- Skapa packages med `__init__.py` och förstå relativa imports.
- Upptäcka och reparera cirkulära imports.
- Förbereda en ren huvudmodul.

## Varför det spelar roll

Riktiga projekt ryms inte i en fil. Separerade ansvar förenklar testning, återanvändning och samarbete.

### Miniäventyr

Ett spel byggs av team för figurer, nivåer och musik. Allt i en fil vore omöjligt att samarbeta kring. Moduler är husets ordnade rum.

### Öva kapitlet enkelt

1. Skapa `saludos.py` och `app.py` i samma katalog.
2. Kör `python app.py`.
3. Läs feltyp och radnummer om det inte fungerar; fel är normala under lärandet.

## Förkunskaper
Rekommenderade tidigare kapitel: 11, 12, 13.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Grundläggande moduler

`saludos.py`:

```python runnable
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`:

```python illustrative
import saludos
print(saludos.hola("Taha"))
```

Förväntad utdata:

```text illustrative
Hola Taha!
```

Byt snabbt ut `"Taha"` mot ditt namn och kör igen.

### `from ... import ...`

```python illustrative
from saludos import hola
print(hola("Frej"))
```

Undvik `import *`; annars blir ursprunget för namn oklart.

---

## 2. Packages

Struktur:

```text illustrative
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`:

```python runnable
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`:

```python illustrative
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    # Ejemplo: aplicar un descuento del 10%
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`:

```python illustrative
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

Kör:

```bash illustrative
python main.py
```

Förväntad utdata:

```text illustrative
90.0
```

- `.` är en relativ import inom samma package.
- `__init__.py` kan vara tom och markerar katalogen som package.

---

## 3. Bonusnivå: mer professionell struktur (frivillig)

Nybörjare kan hoppa över detta; för ett projektlikt upplägg hjälper följande:

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

- `src/` innehåller kod och `tests/` tester.
- Eftersom den här undervisningsstrukturen gör `src` till paketet använder du `from src.dominio.pedidos import Pedido`.

### Kör från projektroten

Kör packages från roten:

```bash illustrative
python -m src.cli
```

### Verifiera paketet
```bash illustrative
python -c "from src.dominio.pedidos import Pedido; print(Pedido.__name__)"
```

Det kör `cli.py` som del av `src` och gör imports stabilare.

---

## 4. Undvika cirkulära imports

```python illustrative
# dominio.py
from servicios import descuentos  # ⚠️ if servicios imports dominio → cycle
```

Problemet är normalt när projekt växer. Flytta gemensam logik till en oberoende modul eller använd lokal import:

```python illustrative
def calcular(total):
    # Local import: only happens when the function is called
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```

Här ligger `aplicar_descuento` exempelvis i `servicios/descuentos.py`.

---

## 5. Entry point

```python runnable
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

Nu kan `python cli.py` köras, medan tester kan importera `main` utan automatisk körning.

---

## Vägledda övningar (med TODO)

1. **15-1 · Separera domain och services**

   ```python todo
   # TODO 1: create dominio/productos.py with class Producto
   # TODO 2: create servicios/precios.py and use Producto
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

   Extra: lägg `aplicar_descuento(porcentaje)` i `Producto`.

2. **15-2 · Modulär CLI**

   ```python todo
   # TODO 1: create cli.py that imports functions from servicios
   # TODO 2: run python -m cli to validate the import path
   ```

   Ledtråd: vid `ModuleNotFoundError`, kör från rätt katalog.

3. **15-3 · Reparera importcykel**

   ```python todo
   # TODO 1: create a small artificial cycle and fix it by moving functions to utils
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

   Edge case: testa import av båda modulerna efter reparationen.

---

## Vanliga misstag

- Fel relativ import som `from .. import` utan `__init__.py`.
- Duplicera i stället för att importera.
- Köra från olika kataloger och bryta paths; använd `python -m`.

---

## Förklarade lösningar

1. **Domain/services**: egna moduler; services importerar domain och blandar inte ansvar.
2. **CLI**: `cli.py` orkestrerar medan verksamhetslogik ligger i `servicios`, vilket förenklar test.
3. **Cykel**: gemensamma funktioner flyttas till `utils`, så beroenden och lager blir tydliga.

---

## Sammanfattning

Moduler och packages organiserar projekt. Du kan importera exakt vad som behövs och skapa rena entry points.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Fråga alltid var logiken hör hemma. Tydliga moduler förbereder större projekt och ramverk som Django.
