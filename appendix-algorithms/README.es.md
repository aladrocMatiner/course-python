# Apéndice B · Algoritmia básica: algoritmos de búsqueda en Python

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

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
- Identificar las precondiciones necesarias (p. ej., una lista ordenada).
- Aplicar BFS con colas (`deque`) para recorrer grafos.
- Escribir pruebas que cubran éxitos, fallos y entradas vacías.

## Por qué importa
La mayoría de problemas reales se reducen a encontrar información. Saber qué algoritmo aplicar evita recorridos innecesarios y abre la puerta a estructuras más avanzadas.

### Mini aventura
Buscar en una lista puede ser como buscar un libro en tu habitación: si está todo desordenado, toca mirar uno por uno (búsqueda lineal). Si está ordenado por letras, puedes ir por la mitad y descartar rápido (búsqueda binaria). Elegir bien la estrategia te ahorra tiempo.

## Prerrequisitos
- Listas, conjuntos, colas con `deque`, funciones, bucles y aserciones básicas de pytest.
- Debes poder indicar si la entrada está ordenada, si cada nodo del grafo está representado y si los nodos son hashables.

## Predice antes de ejecutar
Para la primera búsqueda, predice el índice devuelto para un valor presente, un valor ausente y un duplicado. Ejecuta esos casos, compara los resultados con tu predicción y explica qué contrato determina la respuesta.

---

## 1. Búsqueda lineal

```python runnable
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

- Complejidad O(n). Ideal para colecciones pequeñas o no ordenadas.
- Si hay elementos duplicados, devuelve el primero.

### Prueba rápida
```python illustrative
def test_busqueda_lineal():
    datos = [3, 5, 7]
    assert busqueda_lineal(datos, 5) == 1
    assert busqueda_lineal(datos, 2) == -1
```

---

## 2. Búsqueda binaria

```python runnable
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

```python runnable
from collections import deque

def bfs(grafo, inicio, objetivo):
    if inicio not in grafo or objetivo not in grafo:
        return False
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
- Cada clave y cada nodo vecino deben ser hashables porque los diccionarios y el conjunto `visitados` usan hashing. Cada nodo referenciado también debería aparecer como clave, aunque su lista de vecinos esté vacía.
- La complejidad esperada es O(V + E) (V = nodos, E = aristas) para esta representación con listas de adyacencia, suponiendo que cada nodo se encola una vez y que la pertenencia, el hashing y la igualdad en diccionarios y conjuntos cuestan O(1) de media. Un hashing o una igualdad personalizados costosos, o colisiones adversarias, invalidan esa cota simplificada.
- Esta versión booleana comprueba alcanzabilidad. Una variante con padres recupera el camino más corto; detectar ciclos requiere otra condición.

### Ejemplo de grafo
```python illustrative
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
| BFS | O(1) (inicio = objetivo) | O(V + E) esperado | Lista de adyacencia; nodos hashables; hashing/igualdad O(1) de media |

- Recuerda que O(log n) crece mucho más lento que O(n).
- BFS explora estructuras más ricas. Su cota habitual O(V + E) incluye las hipótesis anteriores sobre hashabilidad y coste medio de las operaciones de diccionarios y conjuntos.

---

## 5. Pruebas sugeridas

```python illustrative
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
- El [contrato de búsqueda y sus pruebas](search_contract.py) verifica grafos alcanzables y desconectados y muestra el `TypeError` que se produce cuando un vecino viola la precondición de hashabilidad. Desde `appendix-algorithms/`, ejecuta `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Ejercicios guiados (con TODOs)
1. **B-1 · Detección de duplicados**
   ```python todo
   numeros = [1, 2, 3, 2]
   # TODO 1: use a set to detect duplicates (O(n))
   # TODO 2: compare with the O(n²) version (two loops)
   ```
   *Pista*: crea una función `tiene_duplicados` que devuelva bool.

2. **B-2 · Índice de primera ocurrencia**
   ```python todo
   datos = [2, 4, 6, 8, 10]
   # TODO 1: modify busqueda_binaria to keep searching left after a match
   # TODO 2: add tests for missing targets
   ```
   *Pista*: guarda el índice coincidente en `resultado`, mueve `derecha = medio - 1` y devuelve el índice guardado al terminar el bucle.

3. **B-3 · Camino más corto con BFS**
   ```python todo
   grafo = {
       "origen": ["A", "B"],
       "A": ["destino"],
       "B": []
   }
   # TODO 1: modify bfs so it returns the path followed
   # TODO 2: when there is no route, return []
   ```
   *Pista*: guarda padres en un dict y reconstruye el camino al final.

---

## Errores comunes
- Olvidar la condición de salida en binaria ⇒ bucle infinito.
- Comparar valores sin convertir a tipos compatibles (e.g., strings vs ints).
- Añadir una lista u otro objeto no hashable como nodo ⇒ la pertenencia en conjuntos/diccionarios lanza `TypeError`; usa identificadores de nodo estables y hashables.
- Marcar un nodo como visitado solo al desencolarlo ⇒ el mismo nodo puede entrar varias veces en la cola; márcalo al encolarlo.
- No verificar si el nodo inicial existe en el grafo.

---

## Explicación de soluciones
1. **Duplicados**: usar un set mantiene O(n) porque cada inserción es O(1) promedio; la versión doble bucle es O(n²) y poco escalable.
2. **Búsqueda binaria**: guarda cada coincidencia y continúa por la mitad izquierda; así devuelve la primera aparición o -1 si no hubo ninguna.
3. **BFS con camino**: exige identificadores hashables, marca cada vecino al encolarlo y almacena `padres[vecino] = nodo`; al encontrar el objetivo, reconstruye hacia atrás hasta el inicio. Con hashing e igualdad O(1) de media, cada vértice y arista alcanzables se procesan un número constante de veces.

---

## Resumen
Los algoritmos de búsqueda son la base de la mayoría de sistemas. Conocer lineal, binaria y BFS te permite elegir la estrategia adecuada según el tamaño y la estructura de los datos.

## Punto de control y rúbrica
- **Corrección**: las búsquedas devuelven el resultado especificado para entradas presentes, ausentes, duplicadas y vacías.
- **Legibilidad**: los invariantes y los prerrequisitos tienen nombres claros.
- **Manejo de errores**: los prerrequisitos incumplidos de grafos o listas tienen un resultado definido.
- **Verificación**: prueba los límites, la primera aparición de duplicados, nodos desconectados y nodos iniciales ausentes.
- **Explicación**: justifica la complejidad a partir del trabajo de los bucles y nombra las hipótesis de hashabilidad y coste medio de BFS.

## Reflexión final
Practicar estas técnicas te prepara para desafíos más avanzados como árboles balanceados, grafos ponderados o motores de búsqueda. Usa estas implementaciones como bloques de construcción para proyectos futuros.
