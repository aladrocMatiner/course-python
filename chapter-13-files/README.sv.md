# Kapitel 13 · Filer och streams från grunden

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Du arbetar med text- och binärfiler, context managers (`with`), loggar och streams i realtid och skyddar dig mot saknade filer, encodingproblem och enorma datamängder. Verktyg läser konfiguration, slår samman data och skapar rapporter utan att ladda allt i minnet.

## Lärväg

1. **Mental modell**: filer som sekventiella streams.
2. **Öppna och stäng** med lägena `r`, `w`, `a`, `b`.
3. **Context managers** mot resursläckor.
4. **Läsa radvis**.
5. **Skriva med buffering och loggar**.
6. **Binärfiler**.
7. **Standard streams**: `stdin` och `stdout`.
8. **Tester och övningar**.

## Lärandemål

- Öppna säkert i rätt text-, skriv-, append- eller binärläge.
- Bearbeta stora filer utan full minnesinläsning.
- Skriva loggar och rapporter med buffering.
- Hantera bytes med `rb` och `wb`.
- Komponera UNIX-liknande flöden med standard streams.

## Varför det spelar roll

Seriösa program läser konfigurationer, loggar och exporter. Korrekt streamhantering förebygger datakorruption och låter skript växa bortom klassrumsexempel.

### Miniäventyr

En fil är som en anteckningsbok: öppna rätt, skriv varsamt och stäng, så finns texten kvar. Fel sida eller ett glömt öppet handtag kan förstöra innehåll.

## Förkunskaper
- Funktioner, loopar, listor och grunderna i `pathlib` från tidigare kapitel.
- En lokal miljö med CPython 3.11+ och en tillfällig övningskatalog.
- **Valfri förhandsblick:** övning 13-3 fångar `FileNotFoundError`. Du kan kopiera det visade mönstret nu; [kapitel 14](../chapter-14-exceptions/README.sv.md) lär ut undantag fullständigt.

## Förutsäg innan du kör
Före det första exemplet: förutsäg vad som händer om filen saknas och vilken operation som ändå måste frigöra filhandtaget. Kör sedan ett säkert exempel i din tillfälliga katalog och jämför det observerade innehållet och städningen med din förutsägelse innan du fortsätter.

---

## 1. Öppna textfiler

```python illustrative
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- `r` läser, `w` skriver över och `a` lägger till.
- Stäng alltid handtaget; helst med `with`.

### Context manager

```python illustrative
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` stänger även om ett undantag uppstår.
- Iteration över `fh` läser en rad i taget.

---

## 2. Skriva filer

```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

nuevas_notas = ["Aprender archivos", "Practicar streams"]
with TemporaryDirectory() as temp_dir:
    ruta_notas = Path(temp_dir) / "notas.txt"
    with ruta_notas.open(mode="w", encoding="utf-8") as fh:
        for nota in nuevas_notas:
            fh.write(nota + "\n")
```

- `w` skriver över; `a` lägger till sist.
- `fh.write` lägger inte automatiskt till newline.

### `pathlib.Path`

```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta = Path(temp_dir) / "reportes" / "hoy.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("Reporte generado", encoding="utf-8")
```

`write_text` och `read_text` förenklar små operationer.

---

## 3. Stora filer och buffering

```python runnable
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

Radvis bearbetning undviker full inläsning.

### Styr buffering

```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta_log = Path(temp_dir) / "log.txt"
    with ruta_log.open(mode="a", buffering=1, encoding="utf-8") as log:
        log.write("[INFO] Inicio\n")
```

`buffering=1` ger radbuffering som flushar vid `\n`.

---

## 4. Binärfiler

```python illustrative
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python illustrative
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- Använd `rb`/`wb` för bytes och ange inte `encoding`.
- Läs stora filer i chunks, exempelvis `fh.read(4096)`.

### Binär streaming

```python illustrative
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV och hjälpare

```python illustrative
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

`json.dumps` och `loads` konverterar mellan dict och JSON; `indent=2` gör resultatet läsbart.

```python illustrative
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

`DictReader` ger en dict per rad så kolumner kan nås via namn.

---

## 6. Standard streams

```python runnable
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- Det möjliggör `cat archivo.txt | python script.py`.
- Skriv fel till `sys.stderr`, exempelvis `sys.stderr.write("Error\n")`.

---

## 7. Tester

Lägg logiken i funktioner som tar paths eller file-like objects.

```python runnable
def procesar_fichero(fh):
    return [linea.strip() for linea in fh]
```

```python runnable
from io import StringIO

def test_procesar_fichero():
    fake = StringIO("uno\ndos\n")
    assert procesar_fichero(fake) == ["uno", "dos"]
```

`StringIO` simulerar textfil och `BytesIO` binärfil.

---

## Vägledda övningar (med TODO)

1. **13-1 · Rensa logg**

   ```python todo
   # TODO 1: read logs.txt line by line
   # TODO 2: drop lines containing "DEBUG"
   # TODO 3: write the result to logs_filtrados.txt
   ```

   *Ledtråd*: öppna båda i samma `with`.

2. **13-2 · Kopiera stor fil**

   ```python todo
   # TODO 1: implement copiar(origen, destino) reading 4096-byte chunks
   # TODO 2: print progress every 1 MB using sys.stdout
   ```

   *Ledtråd*: öka `tamano` med `len(chunk)`.

3. **13-3 · Concat-CLI**

   ```python todo
   # TODO 1: use argparse to accept multiple files and a destination
   # TODO 2: concatenate their content into one file
   # TODO 3: handle errors when a file does not exist
   ```

   *Ledtråd*: `Path.exists()` och `try/except FileNotFoundError`.

---

## Vanliga misstag

- Glömma stängning; använd `with`.
- Blanda text och binärt, `r` mot `rb`, och få encodingfel.
- Skriva över av misstag med `mode="w"`.
- Läsa enorm fil med `.read()` och tömma minnet.

---

## Förklarade lösningar

1. **Logg**: skriv bara när `"DEBUG" not in linea`; allt sker som stream.
2. **Kopia**: chunks håller minnet stabilt och progress visar flaskhalsar.
3. **Concat**: öppna varje `args.archivos` i turordning, skriv till målet och ge tydliga fel.

---

## Sammanfattning

Du kan läsa och skriva text eller binärt och bearbeta streams utan att tömma resurser. Mönstren ligger bakom ETL, rapporter och CLI-verktyg.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Filer kräver disciplin: välj läge, validera paths och skydda mot storlek. Med övning kan verktygen säkert bearbeta gigabyte.
