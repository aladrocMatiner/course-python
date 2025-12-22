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

---

## 1. Obrir fitxers de text

```python
archivo = open("notas.txt", mode="r", encoding="utf-8")
contenido = archivo.read()
archivo.close()
```

### Context manager
```python
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

- `with` tanca el fitxer automàticament.
- Iterar sobre `fh` llegeix línia a línia.

---

## 2. Escriure fitxers

```python
nuevas_notas = ["Aprender archivos", "Practicar streams"]
with open("notas.txt", mode="w", encoding="utf-8") as fh:
    for nota in nuevas_notas:
        fh.write(nota + "\n")
```

### `pathlib.Path`
```python
from pathlib import Path
ruta = Path("reportes") / "hoy.txt"
ruta.parent.mkdir(parents=True, exist_ok=True)
ruta.write_text("Reporte generado", encoding="utf-8")
```

---

## 3. Fitxers grans i buffering

```python
def contar_lineas(ruta):
    total = 0
    with open(ruta, encoding="utf-8") as fh:
        for _ in fh:
            total += 1
    return total
```

### Buffering
```python
with open("log.txt", mode="a", buffering=1, encoding="utf-8") as log:
    log.write("[INFO] Inicio\n")
```

---

## 4. Fitxers binaris

```python
with open("imagen.png", mode="rb") as fh:
    datos = fh.read()
print(len(datos))
```

```python
with open("copia.png", mode="wb") as destino:
    destino.write(datos)
```

### Streams binaris en blocs
```python
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## 5. JSON, CSV i helpers

```python
import json
from pathlib import Path

ruta = Path("config.json")
data = json.loads(ruta.read_text())
data["debug"] = True
ruta.write_text(json.dumps(data, indent=2))
```

```python
import csv
with open("usuarios.csv", newline="", encoding="utf-8") as fh:
    lector = csv.DictReader(fh)
    for fila in lector:
        print(fila["email"])
```

---

## 6. Streams estàndard

```python
import sys

for linea in sys.stdin:
    sys.stdout.write(linea.upper())
```

---

## 7. Proves

```python
def procesar_fichero(fh):
    return [linea.strip() for linea in fh]
```

```python
from io import StringIO

def test_procesar_fichero():
    fake = StringIO("uno\ndos\n")
    assert procesar_fichero(fake) == ["uno", "dos"]
```

---

## Exercicis guiats (amb TODOs)
1. **13-1 · Neteja de logs**
2. **13-2 · Copiar fitxer gran (chunks)**
3. **13-3 · CLI de concatenació**

---

## Errors comuns
- Oblidar tancar fitxers (usa `with`).
- Barrejar `r` i `rb`.
- Sobreescriure fitxers sense voler (`w`).
- Fer `.read()` amb fitxers enormes.

---

## Resum
Domines lectura/escriptura, modes de text o binari i processament en streaming. És la base d’ETLs, reportes i eines CLI.

## Reflexió final
Treballar amb fitxers demana disciplina: mode correcte, rutes validades i protecció contra fitxers grans. Amb pràctica, podràs processar dades de manera segura.
