# Capítol 26 · Iteració, iteradors i generadors

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem

Molts programes reben una seqüència de valors i la transformen: els noms es
converteixen en etiquetes, les lectures en resums i diversos grups en un sol
flux. Ja saps fer-ho amb un bucle `for`. Aquest capítol conserva aquest model
mental fiable i hi afegeix tres eines en un ordre deliberat:

1. **Comprehensions, `enumerate` i `zip`** per transformar col·leccions petites
   de manera llegible.
2. **Iteradors** per entendre on viu l’estat del recorregut i per què un flux de
   dades es pot esgotar.
3. **Generadors** per produir valors sota demanda mantenint el consumidor
   explícitament acotat.

El projecte creixent és una pipeline d’iteració per al marcador sintètic d’un
taller petit. La seva autoritat executable és
[`examples/iteration_pipeline.py`](examples/iteration_pipeline.py), protegida
per proves de la biblioteca estàndard. No usa xarxa, credencials, dades
personals, fitxers, fils ni paquets de tercers.

## Objectius d’aprenentatge

Al final de la ruta que triïs, podràs:

- **O1 — Transformar amb claredat:** derivar una comprehension de llista,
  diccionari o conjunt a partir d’un bucle ordinari i triar la forma més clara.
- **O2 — Enumerar i emparellar amb seguretat:** usar `enumerate` per a posicions
  visibles i triar deliberadament entre un `zip` truncat i
  `zip(..., strict=True)`.
- **O3 — Explicar l’estat d’un iterador:** distingir un iterable d’un iterador,
  usar `iter` i `next`, observar l’esgotament i recrear un recorregut quan la
  font ho permet.
- **O4 — Protegir el recorregut:** usar un valor per defecte no ambigu en
  l’esgotament i evitar mutar estructuralment la col·lecció recorreguda.
- **O5 — Construir treball diferit acotat:** explicar expressions generadores,
  `yield`, el consum d’un sol ús, `yield from` i un límit finit explícit.
- **O6 — Recuperar i netejar:** situar una fallada diferida al pas de consum,
  acabar un generador amb `return` i executar una neteja determinista després
  d’un tancament anticipat.

El [registre de traçabilitat](TRACEABILITY.md) relaciona cada objectiu amb
l’explicació, la pràctica, la recuperació, la solució, el punt de control, el
codi complementari i les proves.

## Prerequisits i mapa de rutes

El punt d’entrada obligatori és el punt de control fonamental del
[capítol 11: Funcions](../chapter-11-functions/README.ca.md). Ja t’has de sentir
còmode amb llistes, diccionaris, conjunts, condicionals, bucles `for`/`while` i
funcions petites. El número del capítol **no** significa que necessitis xarxes,
C++ o Rust.

- **Ruta essencial · 2 sessions de 45–60 minuts.** Llegeix E1–E3, completa el
  repte essencial i usa’n la rúbrica. Resultat: produir un marcador numerat a
  partir de dues col·leccions petites i rebutjar dades desemparellades.
  Compleció: com a mínim 4/5 punts, inclòs el de l’emparellament estricte. Punt
  segur per continuar: atura’t aquí i ves al
  [capítol 12: Classes i objectes](../chapter-12-oop/README.ca.md).
- **Ruta professional · 1–2 sessions de 45–60 minuts.** Completa primer el
  punt de control essencial i després P1–P3 i el repte professional. Resultat:
  consumir, diagnosticar i recrear deliberadament un recorregut d’un sol ús.
  Compleció: com a mínim 4/5 punts, inclosa la recuperació de l’esgotament. Punt
  segur per aturar-te: pots usar iterables amb confiança sense escriure
  generadors.
- **Ruta avançada opcional · 2 sessions de 60–75 minuts.** Completa la ruta
  professional i repassa el
  [capítol 14: Excepcions](../chapter-14-exceptions/README.ca.md) abans de la
  secció de neteja. Resultat: implementar i explicar una pipeline diferida finita,
  una fallada diferida, delegació i neteja anticipada. Compleció: com a mínim
  5/6 punts, inclosos els límits i la neteja. Aquesta ruta continua sent
  opcional per al progrés essencial del curs.

Tornes al curs? Prediu el resultat de
`list(zip(["A", "B"], [1], strict=True))`. Si pots explicar per què la fallada
només apareix quan es consumeix l’objecte `zip`, comença per la ruta
professional. Si també pots explicar per què cridar una funció generadora no
n’executa el cos, comença per la ruta avançada i usa els checkpoints per
confirmar qualsevol buit.

## Glossari breu

- **Iterable:** objecte que pot proporcionar un iterador. Les llistes, tuples,
  diccionaris, conjunts i cadenes en són exemples coneguts.
- **Iterador:** objecte amb estat que produeix un valor següent cada vegada.
  Recorda fins on ha avançat el recorregut.
- **Esgotament:** estat en què l’iterador ja no té cap valor següent. Un `next`
  directe llavors llança `StopIteration` si no s’ha proporcionat un valor per
  defecte.
- **Comprehension:** sintaxi compacta per construir una col·lecció concreta a
  partir d’un iterable.
- **Generador:** iterador creat per una expressió generadora o per una funció
  que conté `yield`.
- **Lazy:** produir el treball a mesura que es demanen valors. Lazy no vol dir
  automàticament finit, ràpid ni segur.
- **Consumidor:** el bucle, `next`, `list` o una altra operació que demana valors
  a un iterador.

La seqüència observable sempre és la mateixa: obtenir un iterador, demanar un
valor, rebre un valor o l’esgotament i aturar-se o tornar a demanar. Aquesta
seqüència en prosa és l’equivalent textual de qualsevol diagrama d’estat de
l’iterador; cap significat depèn de la direcció d’una fletxa ni del color.

## Ruta essencial: transformacions llegibles

### E1. Deriva una comprehension d’un bucle

Objectiu: construir una col·lecció petita sense perdre el model mental del
bucle ordinari.

Suposa que un taller registra tres puntuacions sintètiques. Abans d’executar,
prediu el valor de `doubled` després de cada iteració.

```python runnable
scores = [3, 5, 8]
doubled = []

for score in scores:
    doubled.append(score * 2)

print(doubled)
```

```text output
[6, 10, 16]
```

Llegeix el bucle en aquest ordre: pren un `score`, calcula `score * 2`, afegeix
el resultat i repeteix. Una comprehension de llista expressa la mateixa
transformació posant primer l’expressió del resultat:

```python runnable
scores = [3, 5, 8]
doubled = [score * 2 for score in scores]
print(doubled)
```

```text output
[6, 10, 16]
```

Els claudàtors volen dir «construeix una llista». A dins:

1. `score * 2` és el valor que es desa;
2. `score` és el nom objectiu actual; i
3. `scores` és l’iterable que proporciona els valors.

Una sola condició pot filtrar valors, però apareix després de l’iterable.
Prediu quines puntuacions sobreviuen abans d’executar:

```python runnable
scores = [3, 5, 8]
large_doubles = [score * 2 for score in scores if score >= 5]
print(large_doubles)
```

```text output
[10, 16]
```

Les comprehensions de diccionari i de conjunt segueixen el mateix ordre de
lectura. Un diccionari desa parelles clau/valor; un conjunt elimina duplicats
iguals. Ordenem el conjunt només per mostrar-lo de manera estable: l’ordre
d’iteració d’un conjunt no és un contracte de correcció.

```python runnable
names = ["Noor", "Frej", "Taha"]
length_by_name = {name: len(name) for name in names}
unique_lengths = {len(name) for name in names}

print(length_by_name)
print(sorted(unique_lengths))
```

```text output
{'Noor': 4, 'Frej': 4, 'Taha': 4}
[4]
```

El cas límit d’una entrada buida és tranquil i útil: cap cos s’executa i cada
comprehension produeix una col·lecció buida del seu tipus.

```python runnable
print([value for value in []])
print({value: len(value) for value in []})
print({value for value in []})
```

```text output
[]
{}
set()
```

**Modifica — TODO O1:** Reescriu aquest bucle com una sola comprehension de
llista llegible. Mantén exactament una transformació i una condició.

```python todo
scores = [2, 4, 7, 9]
selected = []
for score in scores:
    if score >= 5:
        selected.append(score + 1)

# TODO: replace the loop with selected = [...]
print(selected)
```

**Pista:** llegeix el cos original en ordre: desa `score + 1`, pren cada
`score` de `scores` i conserva’l quan `score >= 5`.

**Solució explicada:** primer apareix l’expressió del resultat, després el
mateix bucle i finalment la mateixa condició. El resultat normal és `[8, 10]`;
si `scores` és buit, continua produint `[]`.

```python runnable
scores = [2, 4, 7, 9]
selected = [score + 1 for score in scores if score >= 5]
print(selected)
```

```text output
[8, 10]
```

Error comú: comprimir bucles imbricats, diverses condicions, efectes laterals i
assignacions en una sola expressió. Una comprehension és útil quan és més
fàcil de llegir. Conserva el bucle ordinari quan explica millor la història.

### E2. Enumera posicions sense un comptador manual

Objectiu: afegir posicions visibles per a una persona sense actualitzar una
variable separada.

`enumerate` produeix parelles `(position, value)`. `start=1` és útil per a
etiquetes mostrades a una persona; no modifica els índexs de base zero de la
col·lecció. Prediu les dues línies:

```python runnable
names = ["Noor", "Frej"]

for position, name in enumerate(names, start=1):
    print(f"{position}: {name}")
```

```text output
1: Noor
2: Frej
```

El cas límit és un iterable buit: el cos del bucle s’executa zero vegades i no
imprimeix res. No hi ha cap posició especial per inventar.

**Modifica — TODO O2:** Canvia el número inicial visible a `10` i prediu les
dues etiquetes abans d’executar.

```python todo
names = ["Noor", "Frej"]
# TODO: enumerate names starting at 10 and print "position: name"
```

**Pista:** canvia només l’argument `start`; no afegeixis ni incrementis un
comptador separat.

**Solució explicada:** `enumerate(names, start=10)` produeix `(10, "Noor")` i
`(11, "Frej")`. La llista no canvia.

```python runnable
names = ["Noor", "Frej"]
print(list(enumerate(names, start=10)))
```

```text output
[(10, 'Noor'), (11, 'Frej')]
```

### E3. Emparella dades sense pèrdua silenciosa

Objectiu: fer visible el contracte de longitud quan dues fonts de dades van
juntes.

Un `zip` ordinari s’atura quan s’esgota l’entrada més curta. Això pot ser
deliberat, però també pot ocultar una puntuació absent:

```python runnable
names = ["Noor", "Frej"]
scores = [7]
print(list(zip(names, scores)))
```

```text output
[('Noor', 7)]
```

`"Frej"` desapareix perquè l’iterable de puntuacions no té un segon valor.
Quan les longituds iguals formen part de la correcció, demana aquest contracte
explícitament amb `strict=True`. La funció complementària consumeix el `zip` dins
d’una llista, de manera que el desajust no pot quedar amagat en un objecte
`zip` no consumit.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def strict_pairs(left, right):
    """Return pairs, rejecting unequal input lengths."""
    return list(zip(left, right, strict=True))
```

En el camí normal, les proves verifiquen
`strict_pairs(["Noor", "Frej"], [7, 9]) == [("Noor", 7), ("Frej", 9)]`.
Dues entrades buides produeixen correctament `[]`.

Prediu quan falla l’exemple següent: quan es crea `zip` o quan `list` li demana
valors?

<!-- bookcheck: expect-error="ValueError" -->
```python expected-error
names = ["Noor", "Frej"]
scores = [7]
pairs = zip(names, scores, strict=True)
print(list(pairs))
```

El senyal estable és `ValueError`. La construcció només crea l’iterador; el
consum descobreix que l’entrada dreta s’ha acabat abans. El text complet del
traceback pot variar entre versions de manteniment de Python.

**Recuperació:** corregeix la puntuació absent i torna a executar el mateix
contracte estricte.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
print(list(zip(names, scores, strict=True)))
```

```text output
[('Noor', 7), ('Frej', 9)]
```

Eliminar `strict=True` també és un disseny vàlid només quan ignorar els valors
finals és explícitament acceptable. Escriu aquesta decisió al contracte del
domini; no facis del truncament silenciós una reparació accidental.

### Repte essencial guiat

Construeix un marcador numerat. Primer prediu les dues línies de sortida i la
fallada quan manca una puntuació.

```python todo
names = ["Noor", "Frej"]
scores = [7, 9]

# TODO 1: pair names and scores with strict=True.
# TODO 2: enumerate the pairs starting at 1.
# TODO 3: build lines like "1. Noor: 7" with a list comprehension.
# TODO 4: print each line.
```

**Pista:** crea primer `pairs`. Després, la comprehension pot desempaquetar
`position, (name, score)` des d’`enumerate(pairs, start=1)`.

**Solució explicada:** l’emparellament estricte protegeix l’alineació de les
dades; l’enumeració crea posicions visibles; la comprehension formata una línia
per parella. Cada pas té una sola responsabilitat.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
pairs = list(zip(names, scores, strict=True))
lines = [
    f"{position}. {name}: {score}"
    for position, (name, score) in enumerate(pairs, start=1)
]

for line in lines:
    print(line)
```

```text output
1. Noor: 7
2. Frej: 9
```

Amb `names = []` i `scores = []`, `pairs` i `lines` són buits i no s’imprimeix
res. Amb longituds diferents, `ValueError` és el diagnòstic esperat; repara les
dades en lloc d’ocultar el desajust.

### Punt de control i rúbrica essencials

Completa el marcador amb entrades normals, buides i desiguals. Explica per què
la sortida normal està ordenada, per què el resultat buit és vàlid i per què el
desajust falla durant el consum.

Suma un punt per cada criteri:

- **Correcció:** l’entrada normal produeix les dues línies numerades exactes.
- **Límit:** dues entrades buides produeixen un resultat buit sense una fila
  inventada.
- **Recuperació:** les entrades desiguals llancen `ValueError` i les dades
  corregides funcionen.
- **Llegibilitat:** cada comprehension té una transformació clara i com a màxim
  una condició simple.
- **Explicació:** pots distingir posicions visibles, índexs de col·lecció i el
  contracte d’emparellament estricte.

Un 4/5, inclosa la **Recuperació**, completa la ruta essencial. Pots aturar-te
amb seguretat i continuar al capítol 12. Reflexió: en quin lloc d’un programa
que coneguis seria perillós un truncament silenciós?

## Ruta professional: un estat d’iterador que pots explicar

### P1. Iterable i iterador són papers diferents

Objectiu: localitzar l’estat del recorregut en lloc d’imaginar que un bucle
`for` recorda màgicament una posició.

Una llista és un **iterable**: pot proporcionar un iterador. `iter(values)` en
demana un. L’iterador retornat desa el progrés del recorregut. `next(cursor)`
demana un valor a aquell iterador concret.

Prediu cada línia abans d’executar:

```python runnable
values = ["A", "B"]
cursor = iter(values)

print(iter(cursor) is cursor)
print(next(cursor))
print(next(cursor))
print(next(cursor, "done"))
```

```text output
True
A
B
done
```

La seqüència en prosa és:

1. `values` pot crear recorreguts;
2. `cursor` comença abans del primer valor;
3. el primer `next` avança i retorna `"A"`;
4. el segon avança i retorna `"B"`; i
5. el tercer troba l’esgotament i retorna el valor per defecte proporcionat.

`iter(cursor) is cursor` és `True` perquè un iterador és el seu propi iterador.
En canvi, crides separades a `iter(values)` produeixen recorreguts independents
amb estat propi.

El compte enrere del codi complementari també és un iterador, però és un generador d’un
sol ús i no una col·lecció reutilitzable:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def countdown(start):
    """Yield ``start`` down to 1 after validating a finite bound."""
    _require_bounded_integer(start, name="start", maximum=MAX_SQUARES)
    current = start
    while current > 0:
        yield current
        current -= 1
```

Les proves verifiquen que `list(countdown(3))` és `[3, 2, 1]` i que
`list(countdown(0))` és el límit buit `[]`. Els límits negatius, booleans, no
enters o massa grans es rebutgen quan comença el consum.

**Modifica — TODO O3:** Crea dos iteradors a partir de la mateixa llista.
Consumeix dos valors del primer i un del segon. Prediu els tres resultats.

```python todo
values = ["A", "B"]
first = iter(values)
second = iter(values)
# TODO: call next twice on first and once on second, then print each result.
```

**Pista:** l’estat de l’iterador pertany a `first` o `second`, no a `values`.

**Solució explicada:** les observacions són `A`, `B` i després `A`. El segon
iterador comença el seu propi recorregut.

```python runnable
values = ["A", "B"]
first = iter(values)
second = iter(values)
print(next(first))
print(next(first))
print(next(second))
```

```text output
A
B
A
```

### P2. Esgotament, valors per defecte i recuperació

Objectiu: reconèixer l’esgotament com un esdeveniment normal del protocol i
triar una recuperació explícita.

Un `next` directe sense valor per defecte llança `StopIteration` després de
l’últim valor:

<!-- bookcheck: expect-error="StopIteration" -->
```python expected-error
cursor = iter(["A"])
print(next(cursor))
print(next(cursor))
```

La primera crida imprimeix `A`; la segona arriba al senyal estable previst
`StopIteration`. Un bucle `for` gestiona aquest senyal internament i acaba amb
normalitat. No capturis àmpliament totes les excepcions només per continuar
demanant valors.

Hi ha dues recuperacions habituals:

1. Si la font és reutilitzable, demana-li un **iterador nou**.
2. Si l’esgotament és esperable en una API pas a pas, passa a `next` un valor
   per defecte deliberat.

```python runnable
values = ["A"]
spent = iter(values)
print(next(spent))
print(next(spent, "done"))

fresh = iter(values)
print(next(fresh))
```

```text output
A
done
A
```

Un valor per defecte de cadena és ambigu si el flux pot contenir legítimament
la mateixa cadena. Un objecte sentinella privat permet distingir l’absència per
identitat:

```python runnable
missing = object()
value = next(iter([]), missing)
print(value is missing)
```

```text output
True
```

**Modifica — TODO O4:** Amb `values = [0]`, usa un sentinella privat per
distingir el valor real `0` de l’esgotament. Observa les dues peticions.

```python todo
values = [0]
missing = object()
cursor = iter(values)
# TODO: request twice with missing as the default and compare each result by identity.
```

**Pista:** `0` és fals en un context booleà però hi és. Comprova l’absència amb `is missing`,
no amb `if not value`.

**Solució explicada:** el primer resultat és `0` i `first is missing` és
`False`; el segon resultat és el sentinella i `second is missing` és `True`.

```python runnable
values = [0]
missing = object()
cursor = iter(values)
first = next(cursor, missing)
second = next(cursor, missing)
print(first, first is missing)
print(second is missing)
```

```text output
0 False
True
```

### P3. Mantén separada la mutació de la font

Objectiu: no canviar l’estructura que controla el recorregut si no s’ha
ensenyat i provat un contracte específic de la col·lecció.

Eliminar o inserir elements a la mateixa llista que recorres pot saltar valors
perquè les posicions canvien mentre l’iterador avança. Construeix un resultat
separat:

```python runnable
raw_labels = ["draft", "", "review", ""]
clean_labels = []

for label in raw_labels:
    if label:
        clean_labels.append(label)

print(raw_labels)
print(clean_labels)
```

```text output
['draft', '', 'review', '']
['draft', 'review']
```

L’original continua disponible per al diagnòstic i el resultat té un contracte
clar. Aquí també és entenedora la comprehension
`[label for label in raw_labels if label]`.

Error comú: observar un exemple de mutació que funciona i suposar que totes les
col·leccions ho garanteixen. No comparteixen un sol contracte de mutació durant
la iteració. Prefereix un snapshot o un resultat separat si el comportament
exacte no és necessari i verificat.

### Repte professional guiat

Segueix una cua d’etapes sintètiques sense modificar-la. Consumeix `"draft"`,
després `"review"`, observa l’esgotament amb un sentinella privat i recupera’t
creant un recorregut nou que torni a produir `"draft"`.

```python todo
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
# TODO 1: consume and print both stages.
# TODO 2: request once more with missing as the default and prove identity.
# TODO 3: create a fresh iterator and print its first value.
```

**Pista:** no assignis `fresh = cursor`; això dona el mateix objecte esgotat.
Torna a cridar `iter(stages)`.

**Solució explicada:** l’estat del recorregut queda aïllat en cada iterador. La
llista original és reutilitzable; posar un altre nom a `cursor` no el reinicia.

```python runnable
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
print(next(cursor))
print(next(cursor))
print(next(cursor, missing) is missing)

fresh = iter(stages)
print(next(fresh))
```

```text output
draft
review
True
draft
```

### Punt de control i rúbrica professionals

Completa el seguiment guiat i les proves de límit del compte enrere. Explica
amb paraules teves iterable, iterador, estat actual, esgotament, valor per
defecte i recreació.

Suma un punt per cada criteri:

- **Identitat:** distingeixes una llista reutilitzable de cada iterador que crea.
- **Estat:** la predicció segueix cada iterador independentment.
- **Límit:** un iterador buit usa un sentinella no ambigu.
- **Recuperació:** es crea un recorregut nou a partir de la font reutilitzable.
- **Seguretat i explicació:** la font no es muta estructuralment i pots explicar
  per què assignar un altre nom no rebobina un iterador.

Un 4/5, inclosa la **Recuperació**, completa la ruta professional. Reflexió:
quines API que uses retornen col·leccions reutilitzables i quines podrien
retornar iteradors d’un sol ús?

## Ruta avançada opcional: pipelines diferides acotades

Repassa el capítol 14 abans d’A6 i A7: aquestes seccions usen `try`, `finally` i
categories d’excepció. Tot el que segueix continua sent opcional per al progrés
essencial del curs.

### A1. Les expressions generadores ajornen el treball

Objectiu: distingir una col·lecció materialitzada d’un iterador sota demanda.

Els claudàtors construeixen immediatament tots els valors de la llista. Els
parèntesis al voltant de la mateixa sintaxi de comprehension creen una
expressió generadora:

```python runnable
numbers = [1, 2, 3]
materialized = [number * number for number in numbers]
lazy = (number * number for number in numbers)

print(materialized)
print(next(lazy))
print(list(lazy))
```

```text output
[1, 4, 9]
1
[4, 9]
```

El primer `next` consumeix `1`; `list(lazy)` només rep els valors restants. El
generador és d’un sol ús. Laziness canvia **quan** es demanen els valors; no
promet que el treball sigui ràpid ni que un consumidor sense límits sigui segur.

**Modifica — TODO O5:** Prediu el resultat de dues crides a `next(lazy)`
seguides de `list(lazy)` per a quatre nombres d’entrada. Després executa una
versió finita.

**Pista:** ratlla un valor de la font cada vegada que el consumidor en demani un.

### A2. Les funcions generadores es pausen a `yield`

Una funció que conté `yield` crea un generador. Cridar-la crea l’objecte
generador però encara no n’executa el cos. Cada petició reprèn l’execució fins
al `yield` següent, un `return` normal o una fallada.

El codi provat de `countdown` apareix a P1. Per a `countdown(3)`, tres peticions
produeixen `3`, `2` i `1`; la següent observa l’esgotament. La validació també
comença durant el consum: es pot construir `countdown(-1)`, però el primer
consum falla amb `ValueError`.

**Modifica — TODO O5:** Prediu `list(countdown(0))` i
`list(countdown(2))` abans de consultar els resultats de les proves.

**Solució explicada:** zero és un límit vàlid però el cos del bucle no
s’executa, així que el resultat és `[]`. Dos produeix `[2, 1]` i després acaba
amb normalitat.

### A3. Acota una font que, altrament, seria infinita

`itertools.count()` pot continuar produint enters. El codi complementari posa un límit
explícit i validat al davant i limita la petició a `MAX_SQUARES = 10_000`.
Aquesta és una barrera didàctica, no una constant universal del domini.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def bounded_squares(limit):
    """Yield the first ``limit`` squares from an otherwise infinite source."""
    _require_bounded_integer(limit, name="limit", maximum=MAX_SQUARES)
    squares = (number * number for number in count())
    yield from islice(squares, limit)
```

Les proves consumeixen exactament cinc valors i observen
`[0, 1, 4, 9, 16]`. Un límit zero no produeix res. Un valor negatiu, booleà, no
enter o superior al límit es rebutja al primer pas de consum.

No materialitzis una font infinita sense limitador. Fins i tot un productor
diferit esdevé il·limitat si el consumidor demana valors per sempre o els desa
tots. Acota el nombre d’elements, el temps, l’entrada i els recursos posseïts a
la frontera corresponent.

**Modifica — TODO O5:** Canvia un límit finit d’`islice` de 5 a 7 i prediu els
dos últims quadrats. Després prova `limit = 0`.

**Pista:** la font comença a zero; eleva al quadrat els índexs 5 i 6 per obtenir
la nova cua.

**Solució explicada:** set valors són `[0, 1, 4, 9, 16, 25, 36]`; zero valors
produeixen `[]`. És el limitador, no l’expressió generadora tota sola, qui
garanteix la terminació.

### A4. Delega amb `yield from`

Objectiu: reenviar valors des d’un subiterable finit sense escriure manualment
un bucle imbricat de `yield`.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def flatten(groups):
    """Yield every value from each finite group in order."""
    for group in groups:
        yield from group
```

Per a `[["A", "B"], [], ["C"]]`, el resultat verificat és
`["A", "B", "C"]`. El grup interior buit no aporta cap valor ni necessita un
cas especial.

**Modifica — TODO O5:** Afegeix grups buits al principi i al final. Prediu el
mateix resultat abans d’executar.

**Pista:** `yield from []` simplement acaba de seguida.

### A5. Una fallada diferida continua sent una fallada

Objectiu: relacionar el diagnòstic amb el pas de consum que ha arribat a una
dada invàlida.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def reciprocals(values):
    """Yield reciprocals; an invalid later value fails when it is consumed."""
    for value in values:
        yield 1 / value
```

Construir `reciprocals([2, 0, 4])` funciona perquè encara no hi ha hagut cap
divisió. El primer `next` produeix `0.5`; el segon arriba a zero i llança la
categoria estable `ZeroDivisionError`. El `4` posterior no arriba a consumir-se
d’aquell generador fallit.

**Recuperació — TODO O6:** Corregeix l’entrada invàlida i crea un generador nou.
No suposis que l’objecte fallit es pot rebobinar.

**Pista:** l’entrada de recuperació provada és `[2, 4]`.

**Solució explicada:** un nou `reciprocals([2, 4])` produeix `[0.5, 0.25]`. La
correcció canvia el valor invàlid del domini i reinicia el recorregut des d’un
estat conegut.

### A6. Neteja determinista després d’un tancament anticipat

Objectiu: alliberar un recurs local posseït quan un generador iniciat acaba,
falla o es tanca explícitament.

Aquest codi complementari accepta un callback `close` fals perquè la prova pugui
observar la neteja sense obrir un fitxer real ni una connexió de xarxa:

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def managed_values(values, close):
    """Yield values and call ``close`` once when an active generator ends."""
    if not callable(close):
        raise TypeError("close must be callable")
    try:
        yield from values
    finally:
        close()
```

La prova de neteja inicia el generador, consumeix `"A"`, crida
`cursor.close()` i observa `events == ["closed"]`. Tornar a cridar `close` no
afegeix un segon esdeveniment. L’esgotament normal també executa la neteja una
sola vegada. Un valor de neteja que no sigui invocable llança `TypeError` quan
comença el consum.

Límit important: tancar un generador que no s’ha iniciat mai no entra al seu
cos; per tant, aquell cos no pot haver adquirit i després alliberat un recurs.
Adquireix el recurs només dins del temps de vida actiu que controles i tanca
explícitament un generador iniciat quan el consumidor s’atura abans d’hora. No
depenguis del moment en què actua el garbage collector.

**Modifica — TODO O6:** Usa `events = []`, inicia un `managed_values` de dos
valors, consumeix-ne un, tanca’l i comprova l’únic esdeveniment de neteja.

**Pista:** inspecciona `events` abans i després de `cursor.close()`.

### A7. Acaba amb `return`, no amb `StopIteration`

Un generador acaba normalment quan arriba al final o executa `return`. Llançar
explícitament `StopIteration` dins del cos es tradueix a la categoria estable
`RuntimeError` a l’entorn Python declarat. Prediu la categoria final:

<!-- bookcheck: expect-error="RuntimeError" -->
```python expected-error
def broken_generator():
    yield "ready"
    raise StopIteration("finished")

cursor = broken_generator()
print(next(cursor))
print(next(cursor))
```

La primera petició imprimeix `ready`; la segona arriba al llançament explícit
incorrecte i falla amb `RuntimeError`. El text complet del traceback no és el
contracte.

**Recuperació:** substitueix el `raise` explícit per `return`.

```python runnable
def finished_generator():
    yield "ready"
    return

print(list(finished_generator()))
```

```text output
['ready']
```

### Repte avançat guiat

Construeix un informe finit només amb eines de la biblioteca estàndard:

```python todo
from itertools import count, islice

limit = 4
# TODO 1: create a generator expression of squares from count().
# TODO 2: bound it with islice(..., limit).
# TODO 3: materialize only those four values and print them.
# TODO 4: repeat with limit = 0.
```

**Pista:** el consumidor ha de rebre `islice(squares, limit)`, mai la font
il·limitada directament.

**Solució explicada:** crea l’expressió diferida de quadrats, posa `islice` entre
ella i `list` i materialitza la vista finita.

```python runnable
from itertools import count, islice

limit = 4
squares = (number * number for number in count())
result = list(islice(squares, limit))
print(result)
```

```text output
[0, 1, 4, 9]
```

El límit zero retorna `[]`. Un límit negatiu o enorme triat per l’alumne
necessita validació abans d’arribar a aquesta construcció; `bounded_squares`
del codi complementari és propietari d’aquest contracte verificat.

### Punt de control i rúbrica avançats

Completa l’informe acotat, la recuperació de la fallada diferida i el TODO de
neteja. Després explica quan comença a treballar cada generador i com acaba.

Suma un punt per cada criteri:

- **Laziness:** distingeixes la construcció del primer pas de consum.
- **Límits:** cada font que, altrament, seria infinita té un límit de consumidor
  finit, explícit i validat.
- **Estat d’un sol ús:** un generador gastat o fallit es recrea deliberadament.
- **Recuperació:** l’entrada invàlida es corregeix i el cas reparat funciona.
- **Delegació:** `yield from` conserva l’ordre dels grups finits, inclosos els
  buits.
- **Neteja i explicació:** un generador iniciat tanca el recurs fals exactament
  una vegada i expliques per què `return` és la terminació normal.

Un 5/6, inclosos **Límits** i **Neteja i explicació**, completa la ruta avançada
opcional. Reflexió: quin límit pertany al productor, quin al consumidor i qui
és responsable de la neteja a la teva pipeline?

## Errors comuns i recuperacions tranquil·les

- **Comprehensions denses:** si has de desxifrar la línia dues vegades, torna a
  un bucle amb noms o separa valors intermedis.
- **Dependre de l’ordre d’un conjunt:** compara’n la pertinença o ordena’l només
  per mostrar-lo de manera estable; no prometis un ordre arbitrari.
- **Usar `zip` ordinari quan les longituds han de coincidir:** tria
  `strict=True`, consumeix el resultat, corregeix el desajust de la font i torna
  a executar.
- **Suposar que `zip` valida en construir-se:** descobreix l’esgotament de les
  entrades mentre avança el consumidor.
- **Cridar `next` per sempre:** gestiona l’esgotament amb un bucle `for`, un
  valor per defecte deliberat o un iterador nou d’una font reutilitzable.
- **Tractar un generador com si es pogués rebobinar:** recrea’l a partir de les
  entrades originals.
- **Mutar la col·lecció recorreguda:** construeix un resultat separat o un
  snapshot explícit.
- **Dir que una pipeline és «segura perquè és diferida»:** afegeix un límit
  d’elements/temps/entrada i una neteja determinista dels recursos.
- **Esperar validació quan es construeix el generador:** recorda que el cos
  comença durant el consum; prova la primera petició.
- **Llançar `StopIteration` dins d’un generador:** usa `return` per acabar
  normalment.

Els errors d’aquest capítol són observacions, no fracassos personals. Redueix
l’exemple a un productor, un consumidor i un valor següent esperat; després
repara aquest contracte mínim i torna a executar el seu cas normal veí.

## Verifica el contracte executable

Des de l’arrel del repositori, executa la suite declarada de la biblioteca
estàndard:

```bash illustrative
python -B -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'
```

`-B` impedeix crear memòria cau de bytecode. El descobriment afegeix el
directori complementari `examples` com a arrel d’importació de les proves i només
executa `test_*.py` sota el paquet `tests`. La suite comprova:

- emparellament estricte normal i buit, més `ValueError` per longituds desiguals;
- comptes enrere normals, zero, amb límits invàlids, esgotats i recreats;
- els cinc primers quadrats acotats i els límits invàlids;
- delegació finita amb grups buits;
- `ZeroDivisionError` diferit i recuperació amb entrada corregida; i
- tancament parcial, esgotament normal, neteja invàlida i neteja exactament una
  vegada.

S’espera que l’ordre acabi amb codi zero. Un intèrpret absent o un resultat de
proves no zero no és un resultat satisfactori: llegeix la primera prova que falla, corregeix el
contracte més petit, elimina l’estat temporal i torna a executar tant aquell
cas com el seu veí normal.

Els blocs Markdown `source-ref` estan registrats sota `learning:contract`. Són
enllaços d’evidència, no codi executat pel camí genèric de Markdown. La
comprovació explícita `learning-bridges` és propietària del comportament del
codi complementari; els blocs
petits `runnable` i `expected-error` continuen sent aptes per al verificador
genèric acotat.

La verificació demostra el comportament exercitat a l’intèrpret seleccionat.
Per si sola no demostra qualitat pedagògica, fluïdesa de la traducció,
compatibilitat àmplia de plataformes, accessibilitat ni aprovació de publicació.

## Resum i reflexió final

Ara pots triar una eina de recorregut segons el contracte:

- usa un bucle ordinari quan els passos siguin més clars;
- usa una comprehension simple per construir una col·lecció concreta petita;
- usa `enumerate` per a posicions i `zip` estricte per a emparellaments de
  longitud igual;
- tracta explícitament l’estat i l’esgotament de l’iterador; i
- usa un generador només amb un límit de consumidor i un responsable de neteja
  deliberats.

Abans de continuar, explica una pipeline en veu alta: d’on surten els valors,
on viu l’estat, què atura el consum, quina fallada és recuperable i qui neteja.
Si cada resposta és concreta, la sintaxi ja no és màgia: estàs dissenyant el
flux de dades.
