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

## Prerequisits i anticipacions opcionals
Abans de començar, repassa les [llistes](../chapter-03-lists/README.ca.md), els [diccionaris](../chapter-04-dictionaries/README.ca.md), els [conjunts](../chapter-05-sets/README.ca.md) i els [condicionals](../chapter-08-conditionals/README.ca.md). Has de poder llegir una col·lecció i decidir quina branca pren una sentència `if`.

El capítol anticipa breument les [funcions](../chapter-11-functions/README.ca.md) i les [proves amb pytest](../chapter-18-testing/README.ca.md). Aquestes parts són opcionals en una primera lectura: només cal reconèixer que una funció agrupa instruccions i que una prova compara el comportament real amb l’esperat.

## Tria una ruta

- **Ruta essencial · 60–80 min:** seccions 1–3, pràctica 10-0, recuperació i punt essencial. Resultat: iterar amb seguretat, acumular valors i usar `break`/`continue`. Les sentències directes i resultats impresos són l’evidència; no exigeix funcions, pytest, mesures ni notació de complexitat.
- **Ruta intermèdia · 35–45 min:** seccions 4–5. Resultat: comptar treball niat i explicar creixement senzill sense promeses de rendiment.
- **Ruta professional opcional · 30–45 min:** secció 6 i ampliacions amb funcions/proves després del [capítol 11](../chapter-11-functions/README.ca.md) i el [capítol 18](../chapter-18-testing/README.ca.md).

## Per què importa
Els bucles processen col·leccions senceres, però també poden convertir-se en colls d’ampolla. Entendre el cost t’ajuda a escriure codi que escala.

### Mini aventura
Un bucle és com entrenar un moviment: repeteixes fins que surt bé. Però si repeteixes massa, perds temps. Per això també parlarem del cost dels bucles.

## Predicció inicial
Abans d’executar el primer exemple, prediu les tres línies impreses i quantes vegades s’executa el seu cos. Després respon: `range(2, 8, 2)` inclou el `8` i quants valors produeix? Escriu primer les respostes, executa els exemples i explica qualsevol diferència. Així l’execució es converteix en evidència i no en una conjectura.

---

## 1. `for` sobre iterables

```python runnable
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

- `enumerate` afegeix un comptador sense bucles manuals.
- També funciona amb cadenes, diccionaris (`for clave, valor in dic.items()`), conjunts (amb ordre arbitrari) i generadors.

### Rang controlat
```python runnable
for numero in range(5):  # 0 a 4
    print(numero)
```

---

## 2. `while` quan no saps quantes iteracions faràs

```python runnable
contador = 0
while contador < 3:
    print(f"Intento {contador}")
    contador += 1
```

- Defineix condicions clares i actualitza variables dins del bucle per evitar loops infinits.

### `break` i `continue`
```python runnable
for intento in range(5):
    if intento == 3:
        break
    if intento % 2 == 0:
        continue
    print(intento)
```

---

## 3. Acumuladors i transformacions

```python runnable
numeros = [1, 2, 3, 4]
acumulado = 0
for n in numeros:
    acumulado += n
print(acumulado)
```

### Crear noves col·leccions
```python illustrative
cuadrados = []
for n in numeros:
    cuadrados.append(n**2)
```

- És útil quan necessites més lògica de la que permet una list comprehension.

---

## 4. Bucles anidats i cost

```python runnable
datos = [[1, 2], [3, 4, 5]]
for fila in datos:
    for valor in fila:
        print(valor)
```

- Si l’extern recorre `n` i l’intern `m`, el total és `n * m`.
- Quan `n ≈ m`, parlem d’O(n²).

### Exemple
```python runnable
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

- Un recorregut que visita cada element una vegada acostuma a ser O(n).
- Dos recorreguts independents se sumen: O(n + m), no O(n·m).
- Dos bucles anidats multipliquen la feina; si totes dues dimensions creixen com `n`, el cost és O(n²).

### Mesurar amb `time.perf_counter()`
```python runnable
import time

datos = list(range(100000))
start = time.perf_counter()
suma = 0
for valor in datos:
    suma += valor
end = time.perf_counter()
print(f"El bucle O(n) ha trigat {end - start:.4f}s")
```

---

## 6. Optimització bàsica
- Evita bucles imbricats si pots usar estructures més ràpides (`set` per cerques).
- Fes `break` tan aviat com trobis la resposta.
- Mou càlculs constants fora del bucle.

### Exemple: cerca eficient
```python runnable
def contiene(lista, objetivo):
    for elemento in lista:
        if elemento == objetivo:
            return True
    return False
```

La cerca és O(n) en el pitjor cas. Si faràs moltes consultes, un `set` pot reduir cada cerca a O(1) de mitjana, a canvi de construir i emmagatzemar el conjunt.

---

## Pràctica essencial i recuperació

### 10-0 · Recorregut acotat

Prediu els valors acceptats i la suma; després executa el comportament normal i el límit en un bucle acotat:

```python runnable
values = [3, -1, 4, 0, 9]
accepted = []
total = 0

for value in values:
    if value < 0:
        continue
    if value == 0:
        break
    accepted.append(value)
    total += value

print(accepted)
print(total)
```

El bloc següent intenta recórrer un enter expressament; `TypeError` és el diagnòstic esperat:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
for item in 3:
    print(item)
```

Recupera’t proporcionant un iterable i verifica les tres iteracions acotades:

```python runnable
for item in range(3):
    print(item)
```

Registra la sortida normal, el límit de llista buida i la sortida recuperada. Atura’t aquí a la ruta essencial.

## Exercicis guiats (amb TODOs)
1. **10-1 · Comptador de vocals**
   ```python todo
   texto = "Hola mundo"
   # TODO 1: recorre el text i compta quantes vocals hi ha
   # TODO 2: usa un diccionari per comptar cada vocal
   # TODO 3: explica la complexitat
   ```
   *Pista*: un únic `for` sobre el text implica O(n).

2. **10-2 · Taula de multiplicar**
   ```python todo
   # TODO 1: genera una taula 10x10 amb bucles imbricats
   # TODO 2: imprimeix només resultats > 50 amb continue
   # TODO 3: descriu quantes iteracions totals fa
   ```
   *Pista*: 10 files × 10 columnes són 100 iteracions.

3. **10-3 · Cerca primerenca**
   ```python todo
   usuarios = ["ana", "bruno", "carla", "diego"]
   # TODO 1: crea buscar_usuario(nombre)
   # TODO 2: usa break o return per aturar-te quan el trobis
   # TODO 3: afegeix una prova per al cas “no existeix”
   ```
   *Pista*: combina `for` amb `return True` quan hi hagi coincidència i retorna `False` al final.

---

## Errors comuns
- Oblidar actualitzar comptadors en `while` ⇒ bucles infinits.
- Modificar la mateixa llista que recorres ⇒ elements “saltats”.
- Imbricar bucles sense estimar-ne les mides ⇒ temps explosiu.
- Posar treball pesat dins del bucle quan es pot fer fora.

---

## Solucions explicades
1. **Comptador de vocals**: recorre cada caràcter una sola vegada. Un diccionari pot incrementar el recompte amb `vocals[lletra] = vocals.get(lletra, 0) + 1`; per tant, el cost temporal és O(n).
2. **Taula de multiplicar**: dos bucles de 10 iteracions produeixen 100 combinacions. Si la mida fos variable, serien O(n²). `continue` evita imprimir els resultats petits, però no elimina les iteracions.
3. **Cerca primerenca**: dins de `for usuario in usuarios`, retorna `True` quan `usuario == nombre`. Si el bucle acaba sense coincidències, retorna `False`. Les proves han de cobrir tots dos resultats.

---

## Punt de control i rúbrica
Adapta 10-0 com a sentències directes per a tres llistes separades: sense zero, zero al principi i negatius abans del zero. Imprimeix valors acceptats i suma en cada execució; després reprodueix i corregeix el `TypeError` per objecte no iterable. No embolcallis el codi en una funció ni prova pytest.

Suma un punt per criteri: **correcció** (funcionen els tres casos), **llegibilitat** (noms clars i un bucle enfocat), **flux** (`continue`/`break` segueixen les regles), **recuperació** (a l’error esperat el segueix codi acotat funcional) i **evidència** (registres prediccions i sortides). Amb 4/5 pots continuar; si no, repassa les seccions 1–3. Complexitat, mesura, funcions i pytest són evidència opcional.

---

## Resum
Has après patrons per iterar, controlar la sortida i estimar quantes vegades s’executa el teu codi. També has vist com els bucles imbricats incrementen el cost.

## Reflexió final
Entendre bucles i complexitat et dóna poder per processar moltes dades i anticipar l’impacte de les teves decisions.
