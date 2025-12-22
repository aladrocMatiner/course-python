# Kapitel 10 · Loopar och komplexitet

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi lär oss `for` och `while`, `break`/`continue`, och får en första känsla för tidskomplexitet: O(n) och O(n²).

---

## `for` + `enumerate`
```python
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

---

## `while`
```python
contador = 0
while contador < 3:
    print(contador)
    contador += 1
```

---

## Nästlade loopar (O(n²)‑känsla)
```python
usuarios = ["ada", "linus", "carol"]
permisos = ["ver", "editar", "borrar"]
for u in usuarios:
    for p in permisos:
        pass
```

---

## Sammanfattning
Loopar är kraftfulla men kan bli dyra när data växer. Nästa kapitel: funktioner (och att skicka funktioner som argument).
