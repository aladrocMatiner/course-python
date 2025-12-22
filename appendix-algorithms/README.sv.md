# Bilaga B · Grundläggande algoritmer: sökning i Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Vi tittar på tre sökalgoritmer: linjär sökning, binär sökning och BFS (bredden‑först) i enkla grafer. Vi pratar också om komplexitet.

---

## Linjär sökning (O(n))
```python
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

---

## Binär sökning (O(log n), kräver sorterad lista)
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

## BFS (O(V+E))
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

## Sammanfattning
Att välja rätt algoritm sparar tid när data växer. Linjär är enkel, binär är snabb på sorterade listor, och BFS funkar för “nätverk” av noder.
