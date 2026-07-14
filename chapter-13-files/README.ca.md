# Capítol 13 · Gestió de fitxers i streams des de zero

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a treballar amb fitxers de text i binaris, usar context managers (`with`), escriure logs, processar streams en temps real i protegir-te d’errors comuns (fitxers inexistents, codificacions, streams grans). Farem utilitats que llegeixen configuracions i generen reportes sense carregar-ho tot a memòria.

## Ordre pedagògic
1. **Model mental**: fitxers com streams seqüencials.
2. **Obrir i tancar**: `open`, modes (`r`, `w`, `a`, `b`).
3. **`with`**: evitar fuites de recursos.
4. **Llegir línia a línia**.
5. **Escriure amb buffering i logs**.
6. **Binaris (bytes)**.
7. **Streams estàndard (`stdin`, `stdout`)**.
8. **Proves i exercicis**.

## Objectius d’aprenentatge
- Obrir fitxers de forma segura i triar el mode correcte.
- Processar fitxers grans sense carregar-los sencers.
- Escriure logs/reportes amb buffering.
- Llegir/escriure binaris amb `rb`/`wb`.
- Usar streams per composicions tipus UNIX.

## Per què importa
Qualsevol programa seriós llegeix o escriu fitxers: configuració, logs, exportacions… Si gestiones bé els streams, evites corrupció i el teu codi escala.

### Mini aventura
Un fitxer és com un quadern: si l’obres bé, escrius amb cura i el tanques, queda guardat. Si el deixes obert o escrius on no toca, pots perdre dades. Aquí aprendràs a ser “ordenat” amb els quaderns digitals.

## Prerequisits
- Funcions, bucles, llistes i fonaments de `pathlib` de capítols anteriors.
- Un entorn local amb CPython 3.11+ i un directori d'un sol ús per practicar.
- **Avançament opcional**: l'exercici 13-3 captura `FileNotFoundError`. Pots copiar ara el patró mostrat; el [capítol 14](../chapter-14-exceptions/README.ca.md) ensenya les excepcions en profunditat.

## Prediu abans d'executar
Abans del primer exemple, prediu què canvia si falta el fitxer i quina operació ha d'alliberar igualment el descriptor del fitxer. Després d'executar un exemple segur al directori d'un sol ús, compara el contingut observat i la neteja amb la predicció abans de continuar.

---

## 1. Obrir fitxers de text

```python illustrative
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

- `mode` indica com s'obre el fitxer: `r` llegeix, `w` escriu i sobreescriu, i `a` afegeix al final.
- Cal tancar-lo sempre per alliberar el descriptor; un bloc `with` ho garanteix millor.

### Context manager
```python illustrative
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` tanca el fitxer automàticament fins i tot si es produeix una excepció.
- Iterar sobre `fh` llegeix línia a línia i evita carregar tot el contingut a memòria.

---

## 2. Escriure fitxers

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

- `w` sobreescriu el contingut; usa `a` si vols afegir dades al final.
- `fh.write` no incorpora un salt de línia automàticament.

### `pathlib.Path`
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta = Path(temp_dir) / "reportes" / "hoy.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text("Reporte generado", encoding="utf-8")
```

`write_text` i `read_text` simplifiquen operacions breus amb text.

---

## 3. Fitxers grans i buffering

```python runnable
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

El processament línia a línia manté estable l'ús de memòria encara que el fitxer sigui gran.

### Buffering
```python runnable
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as temp_dir:
    ruta_log = Path(temp_dir) / "log.txt"
    with ruta_log.open(mode="a", buffering=1, encoding="utf-8") as log:
        log.write("[INFO] Inicio\n")
```

`buffering=1` activa el buffer per línies i buida les dades quan troba `\n`.

---

## 4. Fitxers binaris

```python illustrative
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python illustrative
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

- Usa `rb` i `wb` per a bytes i no hi indiquis cap `encoding`.
- Per a fitxers grans, llegeix blocs petits amb `fh.read(4096)`.

### Streams binaris en blocs
```python illustrative
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV i helpers

```python illustrative
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

- `json.dumps` i `json.loads` converteixen entre diccionaris i JSON.
- `indent=2` fa que el document sigui llegible per a persones.

```python illustrative
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

`DictReader` produeix un diccionari per fila, de manera que pots accedir a les columnes pel nom.

---

## 6. Streams estàndard

```python runnable
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

- Això permet composicions com `cat archivo.txt | python script.py`.
- Escriu els errors a `sys.stderr`, per exemple amb `sys.stderr.write("Error\n")`.

---

## 7. Proves
Mantén la lògica en funcions que rebin rutes o objectes semblants a fitxers; així les proves no depenen del sistema de fitxers real.

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

`StringIO` simula un fitxer de text; per a dades binàries, usa `BytesIO`.

---

## Exercicis guiats (amb TODOs)
1. **13-1 · Neteja de logs**
   ```python todo
   # TODO 1: read logs.txt line by line
   # TODO 2: drop lines containing "DEBUG"
   # TODO 3: write the result to logs_filtrados.txt
   ```
   *Pista*: usa dos context managers en una línia: `with open(...) as origen, open(...) as destino:`.

2. **13-2 · Copiar fitxer gran (chunks)**
   ```python todo
   # TODO 1: implement copiar(origen, destino) reading 4096-byte chunks
   # TODO 2: print progress every 1 MB using sys.stdout
   ```
   *Pista*: acumula `tamano += len(chunk)` dins del bucle.

3. **13-3 · CLI de concatenació**
   ```python todo
   # TODO 1: use argparse to accept multiple files and a destination
   # TODO 2: concatenate their content into one file
   # TODO 3: handle errors when a file does not exist
   ```
   *Pista*: combina `Path.exists()` amb `try/except FileNotFoundError`.

---

## Errors comuns
- Oblidar tancar fitxers (usa `with`).
- Barrejar els modes de text i binari (`r` i `rb`) i obtenir errors de codificació.
- Sobreescriure fitxers sense voler (`mode="w"`); practica en un directori temporal abans de triar un destí real.
- Fer `.read()` amb fitxers enormes i esgotar la memòria.

---

## Solucions explicades
1. **Neteja de logs**: per cada línia, `if "DEBUG" not in linea: destino.write(linea)`. Com que no acumula les línies en una llista, el processament continua sent en streaming.
2. **Copiar fitxer gran**: les lectures per blocs mantenen estable la memòria; acumular els bytes copiats permet mostrar progrés i detectar colls d'ampolla.
3. **CLI de concatenació**: recorre `args.archivos`, obre cada ruta individualment i escriu-la a la destinació. Si una ruta falla, captura `FileNotFoundError` i mostra quin fitxer no s'ha pogut llegir.

---

## Resum
Domines lectura/escriptura, modes de text o binari i processament en streaming. És la base d’ETLs, informes i eines CLI.

## Punt de control i rúbrica
- **Correcció**: els modes de text i binari corresponen a les dades i l'streaming en conserva el contingut.
- **Llegibilitat**: les rutes i les responsabilitats dels fitxers tenen noms clars.
- **Gestió d'errors**: els fitxers absents i els destins no vàlids tenen una via de recuperació.
- **Verificació**: executa els exercicis en un directori temporal i prova entrades buides i de diverses línies.
- **Explicació**: explica per què `with` i les lectures per blocs protegeixen els recursos.

## Reflexió final
Treballar amb fitxers demana disciplina: mode correcte, rutes validades i protecció contra fitxers grans. Amb pràctica, podràs processar dades de manera segura.
