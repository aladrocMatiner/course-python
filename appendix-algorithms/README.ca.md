# Apèndix B · Algorísmia bàsica: cerques en Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem tres patrons de cerca: cerca lineal, cerca binària i BFS (cerca en amplada) en grafs senzills. Implementarem funcions pures, mirarem complexitat i afegirem proves.

## Objectius d’aprenentatge
- Implementar cerques i saber quan usar-les.
- Entendre O(n), O(log n) i O(V+E) de manera intuïtiva.
- Recordar precondicions (binària = llista ordenada).
- Aplicar BFS amb `deque`.
- Provar casos d’èxit, fallida i entrades buides.

---

## Cerca lineal
```python
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

---

## Cerca binària
```python
def busqueda_binaria(ordenados, objetivo):
    izquierda, derecha = 0, len(ordenados) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor = ordenados[medio]
        if valor == objetivo:
            return medio
        if valor < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1
```

---

## BFS
```python
from collections import deque

def bfs(grafo, inicio, objetivo):
    visitados = set([inicio])
    cola = deque([inicio])

    while cola:
        nodo = cola.popleft()
        if nodo == objetivo:
            return True
        for vecino in grafo.get(nodo, []):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append(vecino)
    return False
```

---

## Resum
Saber triar l’algoritme de cerca adequat et pot estalviar molt de temps quan les dades creixen. Aquesta és una base clau per a reptes més avançats.
