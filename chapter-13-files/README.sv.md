# Kapitel 13 · Filer och strömmar (streams)

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Du lär dig läsa/skriva textfiler och binära filer, använda `with` för att alltid stänga filer, och hantera stora filer genom att läsa i rader eller “chunks”.

---

## Läs en textfil
```python
with open("notas.txt", mode="r", encoding="utf-8") as fh:
    for linea in fh:
        print(linea.strip())
```

---

## Skriv en fil
```python
nuevas_notas = ["Aprender archivos", "Practicar streams"]
with open("notas.txt", mode="w", encoding="utf-8") as fh:
    for nota in nuevas_notas:
        fh.write(nota + "\n")
```

---

## Binär kopiering i chunks
```python
with open("entrada.dat", "rb") as origen, open("salida.dat", "wb") as destino:
    while chunk := origen.read(8192):
        destino.write(chunk)
```

---

## Sammanfattning
Filer är grunden för konfiguration, loggar och export. Nästa kapitel: undantag (exceptions).
