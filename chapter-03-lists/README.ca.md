# Capítol 3 · Introducció a les llistes

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
En aquest capítol aprendràs què és una llista, com accedir a cada element i com modificar-los, ordenar-los i protegir-te d’errors comuns. També practicarem mètodes essencials (`append`, `insert`, `pop`, `remove`, `sort`) i escriurem mini proves perquè les nostres funcions facin el que toca.

## Ordre pedagògic
1. **Introducció**: model mental d’una llista i per què els claudàtors (`[]`) importen.
2. **Accés i ús**: índexos, `-1` per anar al final i com reutilitzar valors en missatges.
3. **Modificar/afegir/treure**: `append`, `insert`, `del`, `pop`, `remove` i quan triar cada un.
4. **Organitzar**: `sort`, `sorted`, `reverse`, `len` i comprovacions ràpides.
5. **Evitar errors**: detectar `IndexError` i prevenir-lo.
6. **Proves i exercicis guiats**: per fer les llistes segures.

## Objectius d’aprenentatge
- Definir una llista i accedir als elements amb índexos positius i negatius.
- Modificar elements i afegir/treure dades segons el context.
- Reordenar llistes de forma temporal o permanent i mesurar la longitud.
- Evitar `IndexError` validant índexos i usant bé `len()` i `-1`.
- A la ruta professional opcional, escriure proves petites per comprovar que una funció no modifica dades “sense voler”.

## Prerequisits i rutes
- **Prerequisit:** completa el checkpoint del [capítol 2](../chapter-02-variables/README.ca.md). La ruta essencial usa variables, cadenes, nombres i crides directes a `print`.
- **Ruta essencial · 55–70 min:** creació, accés, mutació, eliminació, ordenació, longitud i exercici 3-11. Resultat: mantenir una llista de convidats o tasques i recuperar-se d'un índex invàlid.
- **Ruta intermèdia · 30–40 min:** completa els exercicis 3-4 a 3-10 i explica quines operacions muten la llista original.
- **Preview professional opcional · 40–50 min:** comença a “Mini proves automàtiques” i segueix els TODO guiats. Anticipa [condicionals](../chapter-08-conditionals/README.ca.md), [bucles](../chapter-10-loops/README.ca.md), [funcions](../chapter-11-functions/README.ca.md), [excepcions](../chapter-14-exceptions/README.ca.md) i [pytest](../chapter-18-testing/README.ca.md). Pots copiar els exemples complets o saltar directament a “Errors comuns”; no són necessaris per al checkpoint essencial.

## Per què importa
Sense llistes, només podríem guardar un valor per variable. Les llistes permeten tenir catàlegs, usuaris, comandes o lectures en un contenidor ordenat i dinàmic. Dominar això obre la porta a processar centenars (o milers) d’elements amb pocs mètodes i bucles.

### Mini aventura
Imagina una llista com una motxilla amb butxaques numerades. Pots posar coses, treure-les, canviar-les de lloc i comptar quantes n’hi ha. Programant, aquesta motxilla t’evita crear una variable per a cada cosa.

## Predicció abans d'executar
Observa la primera llista `bicycles`. Abans d'executar-la, prediu els valors dels índexs `0`, `-1` i `4`. Executa primer només els accessos vàlids i usa després la secció d'`IndexError` per explicar i recuperar la predicció invàlida.

---

## Què és una llista?
Una llista és una col·lecció ordenada d’elements. En Python es defineixen amb `[]` i els elements se separen amb comes.

```python runnable
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Sortida:
```text illustrative
['trek', 'cannondale', 'redline', 'specialized']
```
Python mostra la representació literal, però normalment voldràs accedir a cada element.

### Accedir als elements d’una llista
Usa l’índex (posició) dins dels claudàtors per recuperar un element:

```python illustrative
print(bicycles[0])
print(bicycles[0].title())
```

### Els índexos comencen en 0
El primer element és a l’índex `0`, el segon a l’`1`, etc. Per al quart element has de demanar `bicycles[3]`. Els índexos negatius compten des del final (`-1` és l’últim, `-2` el penúltim).

### Usar valors individuals d’una llista
Pots inserir elements dins d’un missatge amb f-strings:

```python illustrative
message = f"La meva primera bicicleta va ser una {bicycles[0].title()}."
print(message)
```

Exemple amb persones:
```python runnable
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hola, {names[1]}!")
```

### Prova-ho tu (3-1 a 3-3)
1. **3-1 · Noms**: crea una llista `names` i mostra cada nom.
2. **3-2 · Salutacions**: reutilitza la llista i imprimeix una salutació personalitzada.
3. **3-3 · La teva llista**: crea una llista del teu transport favorit i fes frases com “M’agradaria tenir una …”.

---

## Modificar, afegir i eliminar elements
Les llistes són dinàmiques: pots ajustar el contingut mentre el programa funciona.

### Modificar elements d’una llista
```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Afegir elements al final
```python illustrative
motorcycles.append('ducati')
print(motorcycles)

# Construir des de zero
teams = []
teams.append('frontend')
teams.append('backend')
print(teams)
```

### Inserir elements
```python illustrative
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Eliminar elements
- `del lista[i]` elimina per posició sense retornar el valor.
- `pop()` extreu l’últim element i el retorna (accepta un índex opcional).
- `remove(valor)` localitza i elimina el primer element igual a `valor`.

```python runnable
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

last = motorcycles.pop()
print(f"Últim: {last}")

first = motorcycles.pop(0)
print(f"Primer: {first}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Nota: `remove` només elimina la primera coincidència. Més endavant aprendrem a eliminar-ne totes.

### Prova-ho tu (3-4 a 3-7)
1. **3-4 · Guest List**: crea una llista d’invitats i envia missatges.
2. **3-5 · Changing Guest List**: reemplaça algú que cancel·la i reimprimeix invitacions.
3. **3-6 · More Guests**: anuncia una taula més gran i afegeix tres persones amb `insert` i `append`.
4. **3-7 · Shrinking Guest List**: redueix a dues persones amb `pop` i elimina la resta amb `del`.

---

## Organitzar una llista
Quan les dades arriben en un ordre imprevisible, sovint cal presentar-les ordenades sense destruir l’ordre original.

### Ordenar permanentment amb `sort()`
```python runnable
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` inverteix l’ordre alfabètic i modifica la llista.

### Ordenar temporalment amb `sorted()`
```python illustrative
print(sorted(cars))          # còpia ordenada
print(sorted(cars, reverse=True))
print(cars)                  # l’original no ha canviat
```

### Mostrar en ordre invers
```python illustrative
cars.reverse()
print(cars)
```
`reverse()` inverteix l’ordre actual (no ordena alfabèticament) i és reversible si el tornes a aplicar.

### Longitud d’una llista
```python illustrative
print(len(cars))
```
La longitud t’ajuda a validar índexos i a mostrar quants elements tens.

### Prova-ho tu (3-8 a 3-10)
1. **3-8 · Veure el món**: practica `sorted`, `reverse`, `sort` i `len` sense perdre l’estat original.
2. **3-9 · Invitats a sopar**: usa `len()` per dir quanta gent invites.
3. **3-10 · Cada funció**: crea qualsevol llista i usa cada mètode del capítol com a mínim un cop.

---

## Evitar `IndexError` treballant amb llistes
L’error més comú és demanar un índex fora de rang:

<!-- bookcheck: expect-error="IndexError" -->
```python expected-error
motorcycles = ["honda", "yamaha", "suzuki"]
print(motorcycles[3])
```

El diagnòstic indica que la posició demanada no existeix. Recupera’t amb un índex derivat de la longitud observada, sense endevinar:

```python runnable
motorcycles = ["honda", "yamaha", "suzuki"]
last_index = len(motorcycles) - 1
print(motorcycles[last_index])
```

Consells per prevenir-ho:
- Comprova la longitud abans d’accedir (`if len(motorcycles) > 2:`).
- Usa `-1` per a l’últim element i evita assumir la mida.
- Si elimines mentre iteres, recorre una còpia (`for item in items[:]`).
- **Preview opcional:** la funció i el condicional següents pertanyen al [capítol 11](../chapter-11-functions/README.ca.md) i al [capítol 8](../chapter-08-conditionals/README.ca.md); no són necessaris a la ruta essencial. Si més endavant una funció rep un índex extern, valida’l:
  ```python illustrative
  def get_item(items, index):
      if not 0 <= index < len(items):
          raise IndexError("posición fuera de rango")
      return items[index]
  ```
- Si tens un `IndexError`, imprimeix la llista o `len(items)` per confirmar l’estat real.

### Prova-ho tu (3-11)
Completa l’inici sense bucles ni funcions. Executa una sola vegada l’error intencional anterior, llegeix `IndexError` i després executa la recuperació.

```python todo
tasks = ["read", "practice", "rest"]
# TODO 1: predict and print the first and last tasks
# TODO 2: append one task, remove one task, and print a sorted copy
# TODO 3: print the original list and its length
```

*Pista*: usa `[0]`, `[-1]`, `append`, `pop`, `sorted` i `len`; cap no exigeix un capítol posterior.

---

## Mini proves automàtiques
**Preview opcional:** les seccions següents usen `def`, `if`, `raise`, bucles, comprehensions, imports i `pytest`. La idea mínima és que una funció anomena feina reutilitzable i un test la crida amb una entrada coneguda. Copia cada fitxer complet o ajorna aquesta ruta fins als capítols enllaçats; no instal·lis `pytest` des d'una font no relacionada.

```python illustrative
# lists_utils.py
def prioritize_task(tasks, new_task):
    if not isinstance(tasks, list):
        raise TypeError("tasks ha de ser una llista")
    copy = tasks[:]
    copy.insert(0, new_task)
    return copy

# tests/test_lists_utils.py
import pytest
from lists_utils import prioritize_task

def test_prioritize_task_adds_to_front():
    original = ["documentar", "refactoritzar"]
    result = prioritize_task(original, "configurar CI")
    assert result[0] == "configurar CI"
    assert original[0] == "documentar"  # la còpia protegeix la llista original

def test_prioritize_task_rejects_non_lists():
    with pytest.raises(TypeError):
        prioritize_task("no-llista", "alguna cosa")
```

---

## Exemples progressius: jugant amb angles interessants
Aquests exemples pugen de dificultat i mostren com es comporten les llistes en situacions més reals.

### Exemple 1 · Checklist interactiva
```python runnable
checklist = ["Crear un entorn virtual", "Instal·lar dependències", "Executar proves"]

for step in checklist:
    print(f"- [ ] {step}")

print(f"La checklist té {len(checklist)} passos.")
last = checklist.pop()            # Recuperem l'últim pas
print(f"Últim pas completat: {last}")
checklist.append("Publicar la release")  # Afegeix una tasca nova al final
```
- Practiques `len()` i mutacions bàsiques (`pop`, `append`).
- És útil per a scripts CLI en què els passos canvien durant l'execució.

### Exemple 2 · Cua de suport (list as queue)
```python runnable
ticket_queue = ["BUG-101", "BUG-102", "BUG-103"]

def handle_ticket(queue):
    if not queue:
        return None
    return queue.pop(0)  # pop(0) simula una cola FIFO

def register_ticket(queue, ticket):
    queue.append(ticket)

current_ticket = handle_ticket(ticket_queue)
print(f"Atenent: {current_ticket}")
register_ticket(ticket_queue, "BUG-200")
print(f"Pendents: {ticket_queue}")
```
- `pop(0)` és més car, però fa clara la semàntica FIFO; més endavant el canviaràs per `collections.deque`.
- Aquests mètodes estan preparats per connectar-los a una vista de Django o a un webhook encara sense emmagatzematge.

### Exemple 3 · Normalitzador de lectures (validacions + proves)
```python runnable
# normalizer.py
def normalize_readings(readings, *, max_limit):
    if not isinstance(readings, list):
        raise TypeError("readings ha de ser una llista")
    if not all(isinstance(value, (int, float)) for value in readings):
        raise ValueError("totes les lectures han de ser numèriques")
    if not readings:
        return {"average": 0, "out_of_range": [], "top3": []}

    out_of_range = [value for value in readings if value > max_limit]
    average = sum(readings) / len(readings)
    top3 = sorted(readings, reverse=True)[:3]
    return {"average": average, "out_of_range": out_of_range, "top3": top3}
```

```python illustrative
# tests/test_normalizer.py
import pytest
from normalizer import normalize_readings

def test_normalize_readings_detects_outliers():
    data = [19.2, 20.1, 22.5, 18.0]
    result = normalize_readings(data, max_limit=20)
    assert result["out_of_range"] == [22.5]
    assert result["top3"][0] == 22.5

def test_normalize_readings_validates_types():
    with pytest.raises(ValueError):
        normalize_readings([10, "no-num"], max_limit=50)

def test_normalize_readings_empty_keeps_schema():
    result = normalize_readings([], max_limit=20)
    assert result == {"average": 0, "out_of_range": [], "top3": []}
```
- Combina slicing (`[:3]`), ordenació i una validació sòlida abans de situar-lo darrere d'una API.
- Observa com les proves descriuen els angles interessants: valors atípics i senyalització correcta dels errors de tipus.

---

## Exercicis guiats (amb TODOs)
1. **G3-1 · Invitacions dinàmiques**
   ```python todo
   guests = ["Noor", "Luis", "Marta"]
   # TODO 1: imprimeix un missatge personalitzat per a cada convidat
   # TODO 2: afegeix dues persones al final amb append
   # TODO 3: elimina el segon convidat i imprimeix qui ja no vindrà
   ```
   *Pista*: amb `append`, `pop` i un `for` n’hi ha prou.

2. **G3-2 · Llista de preus**
   ```python todo
   prices = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: calcula el preu mitjà amb sum/len
   # TODO 2: crea una llista amb els preus amb IVA (21%)
   # TODO 3: usa slicing per mostrar només els dos preus més alts
   ```
   *Pista*: combina `sorted(prices)` i `[-2:]`.

3. **G3-3 · Sensors i validacions**
   ```python todo
   readings = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: escriu la funció out_of_range(readings, limit)
   # TODO 2: afegeix una prova que confirmi False quan tot és dins
   # TODO 3: prova que llanci TypeError si readings no és una llista
   ```
   *Pista*: usa `any(value > limit for value in readings)` i el patró de proves anterior.

---

## Errors comuns
- Començar a comptar des d’1 i obtenir `IndexError`.
- Modificar una llista mentre la recorres sense copiar abans.
- Confondre `append` (afegeix la llista com a element) amb `extend`.
- Canviar l’ordre original amb `sort()` quan necessitaves una còpia (`sorted`).
- Oblidar que `remove` només elimina la primera aparició.

---

## Explicació de solucions guiades
1. **G3-1**: missatges amb `for`, `append` per afegir, `pop(1)` per treure i anunciar.
2. **G3-2**: la mitjana és `sum(prices)/len(prices)`; l'IVA es calcula amb `[price * 1.21 for price in prices]`; els dos valors més alts surten de `sorted(prices)[-2:]`.
3. **G3-3**: `any(value > limit for value in readings)` detecta valors fora de rang després de validar amb `isinstance(readings, list)`; les proves cobreixen el camí correcte i els errors de tipus.

---

## Checkpoint i autoavaluació

### Solució explicada de 3-11

Verifica primer la ruta normal:

```python runnable
tasks = ["read", "practice", "rest"]
print(tasks[0])
print(tasks[-1])
tasks.append("review")
removed = tasks.pop(1)
sorted_tasks = sorted(tasks)
print(removed)
print(sorted_tasks)
print(tasks)
print(len(tasks))
```

Verifica després el límit de la llista buida sense indexar-la:

```python runnable
tasks = []
print(tasks)
print(len(tasks))
print(sorted(tasks))
```

La verificació exigeix tres registres: la sortida normal, `0` per al límit buit i l’`IndexError` esperat anterior seguit de la recuperació executable. Reflexiona en una frase: per què derivar `last_index` de `len()` és més segur que endevinar una posició?

Crea una llista amb tres tasques. Prediu el primer i l'últim valor, afegeix una tasca, elimina'n una altra, mostra una còpia ordenada i demostra que l'ordre original no canvia. Després demana expressament un índex invàlid, llegeix `IndexError` i recupera't comprovant `len()` abans de tornar-ho a intentar.

Suma un punt per criteri:
- **Correcció:** accés, alta, baixa i còpia ordenada coincideixen amb les prediccions.
- **Llegibilitat:** els noms expliquen què conté la llista i cada operació té un propòsit clar.
- **Gestió de l'error:** expliques l'índex invàlid i et recuperes sense endevinar la longitud.
- **Verificació:** imprimeixes la llista original i la derivada i identifiques quina operació ha mutat dades.
- **Explicació:** justifiques triar `pop`, `remove`, `sort` o `sorted` en un cas concret.

La ruta essencial acaba amb 5/5. Amb 4/5, repassa l’evidència normal, límit o recuperació que falti abans de continuar; per sota de 4/5, repeteix 3-11. Funcions, bucles, excepcions, comprehensions i pytest queden com a previews opcionals.

---

## Resum
Has definit llistes, has accedit a elements amb índexos positius i negatius, has reutilitzat valors en cadenes, has modificat la llista en temps real, l’has ordenat i has fet servir `len()` i `reverse()`. També has après a evitar `IndexError` i a escriure proves.

## Reflexió final
Dominar llistes és poder manejar col·leccions completes amb poques línies: afegir, treure, tallar, ordenar i validar dades sense duplicar codi. Al següent capítol entrarem en `dict` (diccionaris), que és la base de JSON i de moltes APIs.
