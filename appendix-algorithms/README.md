# Appendix B · Basic Algorithms: Search in Python

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll explore three fundamental search patterns: linear search, binary search, and breadth‑first search (BFS) on simple graphs. We’ll implement pure functions, analyze time complexity, and practice tests that prove correctness.

## Learning path
1. **Linear search**: simple but O(n).
2. **Binary search**: requires a sorted list; O(log n).
3. **Search in connected structures**: BFS for graphs/trees.
4. **Complexity analysis and edge cases**.
5. **Automated tests for each algorithm**.

## Learning objectives
- Implement iterative searches and know when to use them.
- Understand how input size changes the cost of each algorithm.
- Identify required preconditions (e.g., sorted list).
- Apply BFS with queues (`deque`) to traverse graphs.
- Write tests for successes, failures, and empty inputs.

## Why it matters
Many real problems reduce to “find something”. Picking the right algorithm avoids unnecessary work and opens the door to more advanced data structures.

### Mini adventure
Searching a list can be like looking for a book in your room: if everything is messy, you check one by one (linear search). If it’s sorted by letters, you can jump to the middle and discard fast (binary search). Choosing the right strategy saves time.

---

## 1. Linear search

```python
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

- Complexity O(n). Great for small or unsorted collections.
- If there are duplicates, it returns the first match.

### Quick test
```python
def test_busqueda_lineal():
    datos = [3, 5, 7]
    assert busqueda_lineal(datos, 5) == 1
    assert busqueda_lineal(datos, 2) == -1
```

---

## 2. Binary search

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

- Requires an ascending sorted list.
- O(log n): each iteration cuts the search space in half.

### Cases to cover
- Target at the beginning, middle, end, and missing.
- Empty list (`derecha = -1` ⇒ returns -1 immediately).

---

## 3. Breadth‑first search (BFS)

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

- `grafo` is a dict where each key has a list of neighbors.
- Complexity O(V + E) (V = vertices, E = edges).
- Useful to detect connections, shortest paths in unweighted graphs, or simple cycles.

### Graph example
```python
grafo = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": [],
    "D": []
}
assert bfs(grafo, "A", "D") is True
assert bfs(grafo, "C", "D") is False
```

---

## 4. Complexity comparison

| Algorithm | Best case | Worst case | Preconditions |
| --- | --- | --- | --- |
| Linear | O(1) (first element) | O(n) | None |
| Binary | O(1) (middle) | O(log n) | Sorted list |
| BFS | O(1) (start = target) | O(V + E) | Graph representation |

- O(log n) grows much slower than O(n).
- BFS is more expensive but explores richer structures.

---

## 5. Suggested tests

```python
import pytest

def test_busqueda_binaria_extremos():
    datos = [1, 2, 3, 4, 5]
    assert busqueda_binaria(datos, 1) == 0
    assert busqueda_binaria(datos, 5) == 4

def test_bfs_grafo_desconectado():
    grafo = {"A": ["B"], "B": [], "C": []}
    assert bfs(grafo, "A", "C") is False
```

- Add tests for empty lists and nodes with no neighbors.

---

## Guided exercises (with TODOs)
1. **B-1 · Duplicate detection**
   ```python
   numeros = [1, 2, 3, 2]
   # TODO 1: use a set to detect duplicates (O(n))
   # TODO 2: compare with the O(n²) version (two loops)
   ```
   *Hint*: write a `tiene_duplicados` function that returns bool.

2. **B-2 · Index of first occurrence**
   ```python
   datos = [2, 4, 6, 8, 10]
   # TODO 1: implement busqueda_binaria that returns the position
   # TODO 2: add tests for missing targets
   ```

3. **B-3 · Shortest path with BFS**
   ```python
   grafo = {
       "origen": ["A", "B"],
       "A": ["destino"],
       "B": []
   }
   # TODO 1: modify bfs so it returns the path followed
   # TODO 2: when there is no route, return []
   ```
   *Hint*: store parents in a dict and rebuild the path at the end.

---

## Common mistakes
- Forgetting the exit condition in binary search ⇒ infinite loop.
- Comparing values without converting types (e.g., strings vs ints).
- Reusing mutable structures in BFS without cloning ⇒ shared references.
- Not checking whether the start node exists in the graph.

---

## Explained solutions
1. **Duplicates**: using a set keeps O(n) because each insert is average O(1); the double-loop version is O(n²) and doesn’t scale.
2. **Binary search**: return the exact index or -1; tests prove both outcomes.
3. **BFS with path**: store `padres[vecino] = nodo`; when you find the target, rebuild by walking backwards to the start.

---

## Summary
Search algorithms sit under most systems. Knowing linear, binary, and BFS helps you choose the right strategy based on data size and structure.

## Closing reflection
Practicing these techniques prepares you for more advanced topics like balanced trees, weighted graphs, or search engines. Use these implementations as building blocks for future projects.
