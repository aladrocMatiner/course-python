# Apèndix B · Algorismes bàsics: cerca amb Python

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Explorarem tres patrons fonamentals de cerca: cerca lineal, cerca binària i cerca en amplada, o BFS, sobre grafs senzills. Implementarem funcions pures, analitzarem la complexitat temporal i practicarem amb proves que demostrin que són correctes.

## Itinerari d'aprenentatge
1. **Cerca lineal**: senzilla, però O(n).
2. **Cerca binària**: exigeix una llista ordenada i és O(log n).
3. **Cerca en estructures connectades**: BFS per a grafs i arbres.
4. **Anàlisi de complexitat i casos límit**.
5. **Proves automatitzades per a cada algorisme**.

## Objectius d'aprenentatge
- Implementar cerques iteratives i saber quan convé utilitzar-les.
- Entendre com la mida de l'entrada canvia el cost de cada algorisme.
- Identificar precondicions, com ara que la llista estigui ordenada.
- Aplicar BFS amb cues `deque` per recórrer grafs.
- Escriure proves per a èxits, absències i entrades buides.

## Per què és important
Molts problemes reals es poden reduir a «trobar alguna cosa». Escollir l'algorisme adequat evita feina innecessària i obre la porta a estructures de dades més avançades.

### Miniaventura
Buscar dins una llista és com buscar un llibre a l'habitació: si tot està desordenat, mires un element rere l'altre, com a la cerca lineal. Si els llibres estan ordenats alfabèticament, pots saltar al mig i descartar-ne molts de cop, com a la cerca binària. Triar l'estratègia adequada estalvia temps.

## Prerequisits
- Llistes, conjunts, cues amb `deque`, funcions, bucles i assercions bàsiques de pytest.
- Has de poder indicar si l'entrada està ordenada, si cada node del graf està representat i si els nodes són hashables.

## Prediu abans d'executar
Per a la primera cerca, prediu l'índex retornat per a un valor present, un valor absent i un duplicat. Executa aquests casos, compara els resultats amb la predicció i explica quin contracte determina la resposta.

---

## 1. Cerca lineal

```python runnable
def busqueda_lineal(elementos, objetivo):
    for indice, valor in enumerate(elementos):
        if valor == objetivo:
            return indice
    return -1
```

- Té complexitat O(n) i és una bona opció per a col·leccions petites o desordenades.
- Si hi ha duplicats, retorna la primera coincidència.

### Prova ràpida
```python illustrative
def test_busqueda_lineal():
    datos = [3, 5, 7]
    assert busqueda_lineal(datos, 5) == 1
    assert busqueda_lineal(datos, 2) == -1
```

---

## 2. Cerca binària

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

- Necessita una llista ordenada de manera ascendent.
- És O(log n): cada iteració redueix l'espai de cerca a la meitat.

### Casos que cal cobrir
- L'objectiu és al principi, al mig, al final o no existeix.
- La llista és buida; `derecha = -1` i retorna -1 immediatament.

---

## 3. Cerca en amplada (BFS)

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

- `grafo` és un diccionari on cada clau té una llista de veïns.
- Cada clau i node veí ha de ser hashable perquè els diccionaris i el conjunt `visitados` utilitzen hashing. Cada node referenciat també hauria d'aparèixer com a clau, encara que tingui una llista de veïns buida.
- La complexitat esperada és O(V + E), on V són els vèrtexs i E les arestes, per a aquesta representació de llistes d'adjacència, suposant que cada node s'encua una vegada i que pertinença, hashing i igualtat a diccionaris i conjunts són O(1) de mitjana. Un hashing o una igualtat personalitzats costosos, o col·lisions adversàries, invaliden aquesta cota simplificada.
- Aquesta versió booleana comprova l’abastabilitat. Una variant amb pares recupera el camí més curt; detectar cicles requereix una altra condició.

### Exemple de graf
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

## 4. Comparació de complexitat

| Algorisme | Millor cas | Pitjor cas | Precondicions |
| --- | --- | --- | --- |
| Lineal | O(1), primer element | O(n) | Cap |
| Binària | O(1), element central | O(log n) | Llista ordenada |
| BFS | O(1), inici = objectiu | O(V + E) esperat | Llista d'adjacència; nodes hashables; hashing/igualtat O(1) de mitjana |

- O(log n) creix molt més lentament que O(n).
- BFS explora estructures més riques. La seva cota habitual O(V + E) inclou les hipòtesis anteriors sobre hashabilitat i cost mitjà de les operacions de diccionaris i conjunts.

---

## 5. Proves suggerides

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

- Afegeix proves per a llistes buides i nodes sense veïns.
- El [contracte de cerca i les proves](search_contract.py) verifica grafs abastables i desconnectats i mostra el `TypeError` que es produeix quan un veí viola la precondició de hashabilitat. Des d'`appendix-algorithms/`, executa `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v`.

---

## Exercicis guiats (amb TODO)
1. **B-1 · Detectar duplicats**
   ```python todo
   numeros = [1, 2, 3, 2]
   # TODO 1: use a set to detect duplicates (O(n))
   # TODO 2: compare with the O(n²) version (two loops)
   ```
   *Pista*: escriu una funció `tiene_duplicados` que retorni un bool.

2. **B-2 · Índex de la primera aparició**
   ```python todo
   datos = [2, 4, 6, 8, 10]
   # TODO 1: modify busqueda_binaria to keep searching left after a match
   # TODO 2: add tests for missing targets
   ```
   *Pista*: desa l'índex coincident a `resultado`, mou `derecha = medio - 1` i retorna l'índex desat quan acabi el bucle.

3. **B-3 · Camí més curt amb BFS**
   ```python todo
   grafo = {
       "origen": ["A", "B"],
       "A": ["destino"],
       "B": []
   }
   # TODO 1: modify bfs so it returns the path followed
   # TODO 2: when there is no route, return []
   ```
   *Pista*: desa els pares en un diccionari i reconstrueix el camí al final.

---

## Errors habituals
- Oblidar la condició de sortida de la cerca binària i crear un bucle infinit.
- Comparar valors sense convertir-ne els tipus, com strings i ints.
- Afegir una llista o un altre objecte no hashable com a node provoca `TypeError` en consultar conjunts o diccionaris; usa identificadors de node estables i hashables.
- Marcar un node com a visitat només en desencuar-lo permet que el mateix node entri a la cua repetidament; marca'l en encuar-lo.
- No comprovar si el node inicial existeix al graf.

---

## Solucions explicades
1. **Duplicats**: utilitzar un set conserva O(n), perquè cada inserció és O(1) de mitjana; la versió amb dos bucles és O(n²) i no escala bé.
2. **Cerca binària**: desa cada coincidència i continua per la meitat esquerra; així retorna la primera aparició o -1 si no n’hi ha cap.
3. **BFS amb camí**: exigeix identificadors hashables, marca cada veí quan l'encues i desa `padres[vecino] = nodo`; quan trobis l'objectiu, reconstrueix el camí cap enrere. Amb hashing i igualtat O(1) de mitjana, cada vèrtex i aresta abastables es processen un nombre constant de vegades.

---

## Resum
Els algorismes de cerca són sota molts sistemes. Conèixer la cerca lineal, la binària i BFS ajuda a triar l'estratègia segons la mida i l'estructura de les dades.

## Punt de control i rúbrica
- **Correcció**: les cerques retornen el resultat especificat per a entrades presents, absents, duplicades i buides.
- **Llegibilitat**: els invariants i els prerequisits tenen noms clars.
- **Gestió d'errors**: els prerequisits incomplerts de grafs o llistes tenen un resultat definit.
- **Verificació**: prova els límits, la primera aparició de duplicats, nodes desconnectats i nodes inicials absents.
- **Explicació**: justifica la complexitat a partir del treball dels bucles i anomena les hipòtesis de hashabilitat i cost mitjà de BFS.

## Reflexió final
Practicar aquestes tècniques et prepara per a temes més avançats, com arbres equilibrats, grafs amb pesos o motors de cerca. Reutilitza aquestes implementacions com a peces per a futurs projectes.
