# Capítol 10 · Bucles, eficiència i pensament iteratiu

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Estudiarem `for` i `while`, patrons com enumeració, acumulació i control de sortida, i introduirem nocions de complexitat temporal per entendre el cost de repetir operacions. Veureu exemples amb llistes, diccionaris i bucles anidats, i maneres simples d’estimar què tan car és el teu codi.

## Ordre pedagògic
1. **Model mental**: un bucle com a repetició controlada.
2. **`for` sobre iterables**: llistes, rangs, diccionaris.
3. **`while` i condicions**: repetir fins que una cosa canviï.
4. **Comptadors i acumuladors**.
5. **Bucles anidats**: quan usar-los i quin cost tenen.
6. **Complexitat**: O(n), O(n²) amb exemples.
7. **Optimització bàsica**: tallar amb `break`, estructures adequades.

## Objectius d’aprenentatge
- Escriure bucles `for` i `while` fàcils de llegir.
- Acumular resultats i controlar la sortida amb `break`/`continue`.
- Estimar quantes vegades s’executa un bucle i el seu creixement.
- Identificar quan un bucle anidat és car i buscar alternatives.
- Validar el comportament amb proves simples.

## Per què importa
Els bucles processen col·leccions senceres, però també poden convertir-se en colls d’ampolla. Entendre el cost t’ajuda a escriure codi que escala.

### Mini aventura
Un bucle és com entrenar un moviment: repeteixes fins que surt bé. Però si repeteixes massa, perds temps. Per això també parlarem del cost dels bucles.

---

## 1. `for` sobre iterables

```python
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

- `enumerate` afegeix un comptador sense bucles manuals.

### Rang controlat
```python
for numero in range(5):  # 0 a 4
    print(numero)
```

---

## 2. `while` quan no saps quantes iteracions faràs

```python
contador = 0
while contador < 3:
    print(f"Intento {contador}")
    contador += 1
```

- Defineix condicions clares i actualitza variables dins del bucle per evitar loops infinits.

### `break` i `continue`
```python
for intento in range(5):
    if intento == 3:
        break
    if intento % 2 == 0:
        continue
    print(intento)
```

---

## 3. Acumuladors i transformacions

```python
numeros = [1, 2, 3, 4]
acumulado = 0
for n in numeros:
    acumulado += n
print(acumulado)
```

### Crear noves col·leccions
```python
cuadrados = []
for n in numeros:
    cuadrados.append(n**2)
```

---

## 4. Bucles anidats i cost

```python
datos = [[1, 2], [3, 4, 5]]
for fila in datos:
    for valor in fila:
        print(valor)
```

- Si l’extern recorre `n` i l’intern `m`, el total és `n * m`.
- Quan `n ≈ m`, parlem d’O(n²).

### Exemple
```python
usuarios = ["noor", "frej", "taha"]
permisos = ["ver", "editar", "borrar"]
combinaciones = []
for usuario in usuarios:
    for permiso in permisos:
        combinaciones.append((usuario, permiso))
print(len(combinaciones))
```

---

## 5. Estimar complexitat (intuïtivament)

| Patró | Iteracions | Ordre aproximat |
| --- | --- | --- |
| Recórrer una llista | n | O(n) |
| Dos bucles seguits | n + m | O(n + m) |
| Bucles anidats | n * m | O(n·m) |
| Cerca lineal | n | O(n) |

### Mesurar amb `time.perf_counter()`
```python
import time

datos = list(range(100000))
start = time.perf_counter()
suma = 0
for valor in datos:
    suma += valor
end = time.perf_counter()
print(f"Loop O(n) tomó {end - start:.4f}s")
```

---

## 6. Optimització bàsica
- Evita bucles anidats si pots usar estructures més ràpides (`set` per cerques).
- Fes `break` tan aviat com trobis la resposta.
- Mou càlculs constants fora del bucle.

### Exemple: cerca eficient
```python
def contiene(lista, objetivo):
    for elemento in lista:
        if elemento == objetivo:
            return True
    return False
```

---

## Exercicis guiats (amb TODOs)
1. **10-1 · Comptador de vocals**
   ```python
   texto = "Hola mundo"
   # TODO 1: recorre el text i compta quantes vocals hi ha
   # TODO 2: usa un diccionari per comptar cada vocal
   # TODO 3: explica la complexitat
   ```

2. **10-2 · Taula de multiplicar**
   ```python
   # TODO 1: genera una taula 10x10 amb bucles anidats
   # TODO 2: imprimeix només resultats > 50 amb continue
   # TODO 3: descriu quantes iteracions totals fa
   ```

3. **10-3 · Cerca primerenca**
   ```python
   usuarios = ["ana", "bruno", "carla", "diego"]
   # TODO 1: crea buscar_usuario(nombre)
   # TODO 2: usa break o return per aturar-te quan el trobis
   # TODO 3: afegeix una prova per al cas “no existeix”
   ```

---

## Errors comuns
- Oblidar actualitzar comptadors en `while` ⇒ bucles infinits.
- Modificar la mateixa llista que recorres ⇒ elements “saltats”.
- Anidar bucles sense estimar mides ⇒ temps explosiu.
- Posar treball pesat dins del bucle quan es pot fer fora.

---

## Resum
Has après patrons per iterar, controlar la sortida i estimar quantes vegades s’executa el teu codi. També has vist com els bucles anidats incrementen el cost.

## Reflexió final
Entendre bucles i complexitat et dóna poder per processar moltes dades i anticipar l’impacte de les teves decisions.
