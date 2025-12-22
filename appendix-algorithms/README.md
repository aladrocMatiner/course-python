# Apéndice B · Algoritmia básica: algoritmos de búsqueda en Python

## Qué vamos a construir
Exploraremos tres patrones de búsqueda fundamentales: búsqueda lineal, búsqueda binaria y búsqueda en anchura (BFS) sobre grafos sencillos. Implementaremos funciones puras, analizaremos su complejidad temporal y practicaremos pruebas que demuestren su corrección.

## Orden pedagógico
1. **Búsqueda lineal**: sencilla pero O(n).
2. **Búsqueda binaria**: precondición de lista ordenada; O(log n).
3. **Búsqueda en estructuras conectadas**: BFS para grafos/árboles.
4. **Análisis de complejidad y casos límite**.
5. **Pruebas automatizadas para cada algoritmo**.

## Objetivos de aprendizaje
- Implementar búsquedas iterativas y entender cuándo usarlas.
- Medir el impacto del tamaño de la entrada en cada algoritmo.
- Identificar las precondiciones necesarias (e.g., lista ordenada).
- Aplicar BFS con colas (`deque`) para recorrer grafos.
- Escribir pruebas que cubran éxitos, fallos y entradas vacías.

## Por qué importa
La mayoría de problemas reales se reducen a encontrar información. Saber qué algoritmo aplicar evita recorridos innecesarios y abre la puerta a estructuras más avanzadas.

### Mini aventura
Buscar en una lista puede ser como buscar un libro en tu habitación: si está todo desordenado, toca mirar uno por uno (búsqueda lineal). Si está ordenado por letras, puedes ir por la mitad y descartar rápido (búsqueda binaria). Elegir bien la estrategia te ahorra tiempo.

---

## 1. Búsqueda lineal

```python
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

- Complejidad O(n). Ideal para colecciones pequeñas o no ordenadas.
- Si hay elementos duplicados, devuelve el primero.

### Prueba rápida
```python
def test_busqueda_lineal():
    datos = [3, 5, 7]
    assert busqueda_lineal(datos, 5) == 1
    assert busqueda_lineal(datos, 2) == -1
```

---

## 2. Búsqueda binaria

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

- Requiere una lista ordenada ascendente.
- O(log n): cada iteración elimina la mitad de la búsqueda.

### Casos a cubrir
- Objetivo al principio, mitad, final y ausente.
- Lista vacía (`derecha = -1` ⇒ retorna -1 de inmediato).

---

## 3. Búsqueda en anchura (BFS)

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

- `grafo` es un dict donde cada clave tiene una lista de vecinos.
- Complejidad O(V + E) (V = nodos, E = aristas).
- Útil para detectar conexiones, rutas cortas o ciclos básicos.

### Ejemplo de grafo
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

## 4. Comparativa de complejidad

| Algoritmo | Mejor caso | Peor caso | Precondiciones |
| --- | --- | --- | --- |
| Lineal | O(1) (primer elemento) | O(n) | Ninguna |
| Binaria | O(1) (mitad) | O(log n) | Lista ordenada |
| BFS | O(1) (inicio = objetivo) | O(V + E) | Grafo representado |

- Recuerda que O(log n) crece mucho más lento que O(n).
- BFS es más costoso pero permite explorar estructuras complejas.

---

## 5. Pruebas sugeridas

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

- Agrega pruebas para listas vacías y nodos sin vecinos.

---

## Ejercicios guiados (con TODOs)
1. **B-1 · Detección de duplicados**
   ```python
   numeros = [1, 2, 3, 2]
   # TODO 1: usa un set para detectar si hay duplicados (complejidad O(n))
   # TODO 2: compara con la versión O(n²) (dos bucles)
   ```
   *Hint*: crea una función `tiene_duplicados` que devuelva bool.

2. **B-2 · Índice de primera ocurrencia**
   ```python
   datos = [2, 4, 6, 8, 10]
   # TODO 1: implementa busqueda_binaria que devuelva la posición
   # TODO 2: añade pruebas para casos ausentes
   ```

3. **B-3 · Camino más corto con BFS**
   ```python
   grafo = {
       "origen": ["A", "B"],
       "A": ["destino"],
       "B": []
   }
   # TODO 1: modifica bfs para que regrese el camino seguido
   # TODO 2: maneja el caso donde no hay ruta devolviendo []
   ```
   *Hint*: guarda padres en un dict y reconstruye el camino al final.

---

## Errores comunes
- Olvidar la condición de salida en binaria ⇒ bucle infinito.
- Comparar valores sin convertir a tipos compatibles (e.g., strings vs ints).
- Reutilizar estructuras mutables en BFS sin clonar ⇒ referencias compartidas.
- No verificar si el nodo inicial existe en el grafo.

---

## Explicación de soluciones
1. **Duplicados**: usar un set mantiene O(n) porque cada inserción es O(1) promedio; la versión doble bucle es O(n²) y poco escalable.
2. **Búsqueda binaria**: devuelve la posición exacta o -1; las pruebas demuestran ambos resultados.
3. **BFS con camino**: almacena `padres[vecino] = nodo`; al encontrar el objetivo, reconstruye con un while inverso hasta el inicio.

---

## Resumen
Los algoritmos de búsqueda son la base de la mayoría de sistemas. Conocer lineal, binaria y BFS te permite elegir la estrategia adecuada según el tamaño y la estructura de los datos.

## Reflexión final
Practicar estas técnicas te prepara para desafíos más avanzados como árboles balanceados, grafos ponderados o motores de búsqueda. Usa estas implementaciones como bloques de construcción para proyectos futuros.
