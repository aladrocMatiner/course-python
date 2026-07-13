# Appendix B · Grundalgoritmer: sökning i Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi utforskar linjär sökning, binär sökning och breadth-first search (BFS) i enkla grafer. Rena funktioner, tidskomplexitet och tester visar korrekthet.

## Lärväg

1. **Linjär sökning**: enkel O(n).
2. **Binär sökning**: sorterad lista och O(log n).
3. **BFS** i sammanlänkade strukturer.
4. **Komplexitet och edge cases**.
5. **Automatiserade tester**.

## Lärandemål

- Implementera iterativa sökningar och välja rätt.
- Förstå hur inputstorlek påverkar kostnad.
- Identifiera preconditions som sortering.
- Traversera grafer med BFS och `deque`.
- Testa träff, miss och tom input.

## Varför det spelar roll

Många problem är ”hitta något”. Rätt algoritm sparar arbete och leder vidare till avancerade datastrukturer.

### Miniäventyr

I ett stökigt rum söker du bok för bok; i en alfabetisk hylla kan halva området kastas varje steg. Strategin sparar tid.

## Förkunskaper
Rekommenderade tidigare kapitel: 3, 5, 7, 10, 18.
Använd CPython 3.11+ i en tillfällig lokal miljö och håll data, hemligheter och tjänster borta från verkliga system.

---

## 1. Linjär sökning

```python runnable
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

- O(n), bra för små eller osorterade samlingar.
- Vid dubletter returneras första träffen.

### Snabbt test

```python illustrative
def test_busqueda_lineal():
    datos = [3, 5, 7]
    assert busqueda_lineal(datos, 5) == 1
    assert busqueda_lineal(datos, 2) == -1
```

---

## 2. Binär sökning

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

- Kräver stigande sorterad lista.
- O(log n) halverar sökområdet varje iteration.

### Fall att täcka

- Målet först, i mitten, sist och saknat.
- Tom lista där `derecha = -1` genast ger `-1`.

---

## 3. Breadth-first search (BFS)

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

- `grafo` mappar varje nod till grannar.
- O(V + E), vertices plus edges.
- Den booleska versionen testar nåbarhet. En variant med föräldrar återger den kortaste vägen; cykeldetektering kräver ett annat villkor.

### Grafexempel

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

## 4. Jämför komplexitet

| Algoritm | Bästa fall | Värsta fall | Förvillkor |
| --- | --- | --- | --- |
| Linjär | O(1), första | O(n) | Inget |
| Binär | O(1), mitten | O(log n) | Sorterad lista |
| BFS | O(1), start=mål | O(V + E) | Grafrepresentation |

- O(log n) växer mycket långsammare än O(n).
- BFS kostar mer men utforskar rikare struktur.

---

## 5. Föreslagna tester

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

Lägg till tomma listor och noder utan grannar.

---

## Vägledda övningar (med TODO)

1. **B-1 · Upptäck dubletter**

   ```python todo
   numeros = [1, 2, 3, 2]
   # TODO 1: use a set to detect duplicates (O(n))
   # TODO 2: compare with the O(n²) version (two loops)
   ```

   *Ledtråd*: skriv `tiene_duplicados` som returnerar bool.

2. **B-2 · Index för första förekomst**

   ```python todo
   datos = [2, 4, 6, 8, 10]
   # TODO 1: modify busqueda_binaria to keep searching left after a match
   # TODO 2: add tests for missing targets
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **B-3 · Kortaste väg med BFS**

   ```python todo
   grafo = {
       "origen": ["A", "B"],
       "A": ["destino"],
       "B": []
   }
   # TODO 1: modify bfs so it returns the path followed
   # TODO 2: when there is no route, return []
   ```

   *Ledtråd*: lagra parents i dict och bygg vägen baklänges.

---

## Vanliga misstag

- Saknat exitvillkor i binär sökning och oändlig loop.
- Jämföra strängar med ints utan konvertering.
- Återanvända muterbara BFS-strukturer utan kopia.
- Inte kontrollera att startnoden finns.

---

## Förklarade lösningar

1. **Dubletter**: set ger O(n) med O(1)-insert i genomsnitt; dubbelloop är O(n²).
2. **Binär sökning**: spara varje träff och fortsätt i vänstra halvan; då returneras den första förekomsten eller -1 utan träff.
3. **BFS-väg**: spara `padres[vecino] = nodo` och gå bakåt från målet.

---

## Sammanfattning

Linjär, binär och BFS-sökning låter dig välja strategi efter datastorlek och struktur.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Teknikerna förbereder balanserade träd, viktade grafer och sökmotorer. Återanvänd implementationerna som byggblock.
