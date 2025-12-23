# Chapter 10 · Loops, Efficiency, and Iteration

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll study `for` and `while`, patterns like enumeration, accumulation and early exit, and we’ll take our first steps into time complexity to understand the cost of repeating operations. You’ll see examples with lists, dictionaries and nested loops, plus simple ways to estimate how “expensive” your code is.

## Learning path
1. **Mental model**: a loop as controlled repetition.
2. **`for` over iterables**: lists, ranges, dictionaries.
3. **`while` and conditions**: repeat until something changes.
4. **Counters and accumulators**: professional patterns.
5. **Nested loops**: when to use them and what they cost.
6. **Complexity intuition**: O(n), O(n²) with measurable examples.
7. **Basic optimization**: break early, choose the right data structure.

## Learning objectives
- Write readable `for` and `while` loops you can reason about.
- Accumulate results (sums, new lists) and stop with `break`/`continue`.
- Analyze how many times a loop runs and estimate its growth order.
- Recognize when a nested loop may be costly and look for alternatives.
- Validate loop behavior with simple tests.

## Why it matters
Loops process whole collections — but they can also become bottlenecks. Understanding how they behave helps you write code that scales and spot optimization opportunities before production.

### Mini adventure
A loop is like practicing a sports move: you repeat the same action until it becomes easy. But if you repeat “too many” times, you get tired and waste time. That’s why we’ll also learn the cost of nested loops.

---

## 1. `for` over iterables

```python
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

- `enumerate` adds a counter without manual bookkeeping.
- It also works with strings, dictionaries (`for clave, valor in dic.items()`), sets (arbitrary order) and generators.

### Controlled ranges
```python
for numero in range(5):  # 0 to 4
    print(numero)
```

---

## 2. `while` when you don’t know the number of iterations

```python
contador = 0
while contador < 3:
    print(f"Intento {contador}")
    contador += 1
```

- Define a clear condition and update variables inside the loop to avoid infinite loops.

### `break` and `continue`
```python
for intento in range(5):
    if intento == 3:
        break  # stops the loop completely
    if intento % 2 == 0:
        continue  # jumps to the next iteration
    print(intento)
```

---

## 3. Accumulators and transformations

```python
numeros = [1, 2, 3, 4]
acumulado = 0
for n in numeros:
    acumulado += n
print(acumulado)
```

### Creating new collections
```python
cuadrados = []
for n in numeros:
    cuadrados.append(n**2)
```

- Useful when you need more logic than a list comprehension.

---

## 4. Nested loops and cost

```python
datos = [[1, 2], [3, 4, 5]]
for fila in datos:
    for valor in fila:
        print(valor)
```

- If the outer loop runs `n` times and the inner runs `m` times, total iterations are `n * m`.
- When `n ≈ m`, that’s O(n²). Fine for small tables, expensive when it grows.

### Example with verification
```python
usuarios = ["noor", "frej", "taha"]
permisos = ["ver", "editar", "borrar"]
combinaciones = []
for usuario in usuarios:
    for permiso in permisos:
        combinaciones.append((usuario, permiso))
print(len(combinaciones))  # 9, cartesian product
```

---

## 5. Estimating complexity (intuitively)

| Pattern | Iterations | Approx. order |
| --- | --- | --- |
| Loop a list once | n | O(n) |
| Two sequential loops | n + m | O(n + m) |
| Nested loops (n * m) | n * m | O(n·m) |
| Linear search | n | O(n) |

- O(n) means time grows proportional to input size.
- O(n²) grows much faster: doubling n means ~4× iterations.

### Measuring with `time.perf_counter()`
```python
import time

datos = list(range(100000))
start = time.perf_counter()
suma = 0
for valor in datos:
    suma += valor
end = time.perf_counter()
print(f"Loop O(n) took {end - start:.4f}s")
```

---

## 6. Basic optimization
- Avoid nested loops when a faster structure exists (`set` membership is O(1) on average).
- `break` as soon as you find what you need.
- Move constant work outside the loop.

### Example: efficient search
```python
def contiene(lista, objetivo):
    for elemento in lista:
        if elemento == objetivo:
            return True
    return False
```

- Complexity is O(n). With a set you can reduce it to average O(1).

---

## Guided exercises (with TODOs)
1. **10-1 · Vowel counter**
   ```python
   texto = "Hola mundo"
   # TODO 1: iterate the text and count how many vowels exist
   # TODO 2: use a dict to count each vowel separately
   # TODO 3: explain the complexity
   ```
   *Hint*: one `for` → O(n).

2. **10-2 · Multiplication table**
   ```python
   # TODO 1: generate a 10x10 table using nested loops
   # TODO 2: print only results greater than 50 using continue
   # TODO 3: describe how many total iterations run
   ```
   *Hint*: 10 rows × 10 columns ⇒ 100 iterations.

3. **10-3 · Early search**
   ```python
   usuarios = ["ana", "bruno", "carla", "diego"]
   # TODO 1: create buscar_usuario(nombre)
   # TODO 2: use break to stop once you find it
   # TODO 3: add a test for the “not found” case
   ```
   *Hint*: `for` + `return True` when it matches; return False at the end.

---

## Common mistakes
- Forgetting to update counters in `while` ⇒ infinite loops.
- Modifying the same list you’re iterating ⇒ you skip items; use a copy.
- Nesting loops without estimating sizes ⇒ exploding runtime.
- Doing heavy work inside the loop when it could be done once outside.

---

## Explained solutions
1. **Vowel counter**: one `for` per character; a dict increments counts (`vocales[letra] = vocales.get(letra, 0) + 1`). Complexity O(n).
2. **Multiplication table**: two `for` loops of 10 iterations each → 100 iterations (O(n²) if n grows). `continue` skips printing small results.
3. **Early search**: `for usuario in usuarios` and `if usuario == nombre: return True`; if the loop ends, return `False`. The test covers both paths.

---

## Summary
You took concrete patterns for iterating collections, controlling exit, and estimating how many times your code runs. You also saw how nested loops increase cost — and when to break early or swap in a faster structure.

## Closing reflection
Understanding loops gives you the power to process large data sets and predict the impact of your choices. This complexity intuition will be key when we tackle more advanced data structures and algorithms.
