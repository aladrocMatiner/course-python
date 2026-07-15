# Capítol 27 · Tipatge gradual i anàlisi estàtica

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem

Python permet afegir informació de tipus gradualment. Avui pots anotar una
frontera útil sense haver de reescriure tot el programa. Les anotacions ajuden
una persona lectora, un editor o un analitzador estàtic a raonar sobre els
valors abans de l'execució. No inspeccionen ni rebutgen automàticament valors
en temps d'execució.

Farem créixer un petit exemple sintètic d'inventari en tres etapes tranquil·les:

1. **Essencial:** anotar funcions i col·leccions, representar l'absència amb
   `None`, refinar una unió i mantenir explícita la validació en temps d'execució.
2. **Professional:** donar forma als registres de diccionari amb `TypedDict`,
   acceptar comportaments estructuralment amb `Protocol`, passar cridables
   tipats, conservar el tipus genèric del resultat i emprar `Self` en un mètode
   fluid.
3. **Itinerari opcional amb analitzador:** comparar un consumidor vàlid amb un
   altre d'intencionadament invàlid, reconèixer categories d'error estables,
   reparar el contracte i executar un verificador acotat quan la versió exacta
   de l'analitzador ja estigui proveïda.

L'autoritat executable és
[`examples/typed_inventory.py`](examples/typed_inventory.py). Les proves en
temps d'execució i els casos de l'analitzador només fan servir SKU i quantitats
sintètics. No utilitzen cap xarxa, base de dades, credencial, registre personal,
índex de paquets ni fitxer de l'estudiant.

## Objectius d'aprenentatge

En acabar l'itinerari que triïs, podràs:

- **O1 — Llegir i escriure anotacions:** anotar paràmetres, valors de retorn i
  col·leccions concretes sense afirmar que les anotacions executen validacions.
- **O2 — Modelar l'absència:** usar `T | None`, conservar valors falsos vàlids
  com la quantitat `0` i refinar l'absència amb `is None`.
- **O3 — Validar una frontera en temps d'execució:** acceptar un `object`,
  comprovar-ne el tipus real i els límits del domini, rebutjar `bool` quan cal
  un enter exacte i recuperar-se sense mutacions parcials.
- **O4 — Descriure la forma d'un registre:** emprar `TypedDict` per a les claus
  estables i els tipus de valor d'un diccionari que ja és dins el nucli tipat.
- **O5 — Tipar comportaments i algorismes reutilitzables:** usar `Callable`,
  `Protocol` estructural, `TypeVar` i `Self` quan cada eina aclareix un contracte
  real.
- **O6 — Llegir honestament l'evidència estàtica:** separar els diagnòstics de
  l'analitzador de les excepcions de Python, basar-se en categories estables en
  lloc del text complet i corregir un consumidor invàlid fins a obtenir un
  resultat net.
- **O7 — Explicar el límit de l'evidència:** indicar què fan les proves en temps
  d'execució, un analitzador i la revisió humana, i què no demostra cap d'aquests
  elements per si sol.

El [registre de traçabilitat](TRACEABILITY.md) relaciona aquests objectius amb
l'explicació, la pràctica, les solucions, les referències al codi, les proves i
els punts de control.

## Prerequisits i mapa d'itineraris

Abans de començar, completa els punts de control fonamentals de:

- [Capítol 11: Funcions](../chapter-11-functions/README.ca.md), per als
  paràmetres, els valors de retorn i `None`;
- [Capítol 15: Mòduls](../chapter-15-modulos/README.ca.md), per a les
  importacions i les fronteres públiques dels mòduls;
- [Capítol 18: Proves](../chapter-18-testing/README.ca.md), per als contractes
  observables de funcionament normal i d'error; i
- [Capítol 22: Introspecció](../chapter-22-introspection/README.ca.md), per a la
  diferència entre el comportament d'un objecte en temps d'execució i la
  informació que inspeccionen les eines.

La posició numèrica després del capítol 26 no converteix les xarxes, C++ o Rust
en prerequisits.

- **Itinerari essencial · 2 sessions de 45–60 minuts.** Llegeix E1–E4, completa
  el repte essencial i puntua'n la rúbrica. Resultat: una consulta tipada més
  una frontera d'enters validada explícitament. Finalització: almenys 4/5 punts,
  incloses la distinció entre estàtic i temps d'execució i la recuperació de
  `None`. Punt de parada segur: aplica aquestes anotacions al Python habitual i
  continua sense instal·lar cap analitzador.
- **Itinerari professional · 2 sessions de 50–70 minuts.** Completa el punt de
  control essencial i després P1–P4 i el repte professional. Resultat: ampliar
  el contracte provat de l'inventari amb files tipades, una cerca genèrica, una
  font de preus estructural i crides fluides que conserven la subclasse.
  Finalització: almenys 5/6 punts, inclosa la preservació de la frontera en
  temps d'execució. Punt de parada segur: pots consumir interfícies de
  biblioteques tipades sense executar l'itinerari opcional amb analitzador.
- **Itinerari opcional amb analitzador · 1 sessió de 45–60 minuts.** Completa
  el punt de control professional i usa un entorn aïllat on s'hagi instal·lat
  deliberadament la versió directa i exacta de l'eina. Resultat: explicar tres
  categories de diagnòstic, observar un cas esperat amb codi de sortida diferent
  de zero i demostrar que la versió corregida queda neta. Finalització: el
  les proves en temps d'execució passen, el cas positiu passa, el negatiu falla
  per totes les categories declarades, el corregit passa i la neteja passa. Si
  l'analitzador falta o té
  una versió diferent, el resultat és «prerequisit absent», no un punt de
  control suspès i mai un aprovat.

Tornes al curs? Explica per què `def echo(value: str) -> str:` no impedeix que
una crida en temps d'execució rebi `7`. Després explica per què
`if value is None` conserva un `0` vàlid. Si totes dues idees són clares,
comença per l'itinerari professional. Si també pots explicar el subtipatge
estructural i per què `list[Dog]` no és automàticament `list[Animal]`, usa el
punt de control professional com a auditoria ràpida abans de l'itinerari
opcional amb analitzador.

## Glossari breu

- **Anotació:** informació de tipus associada a un nom, un paràmetre o una
  posició de retorn. És metadada; Python no la converteix per defecte en un
  validador.
- **Analitzador estàtic:** eina separada que analitza el codi font sense fer
  servir cada valor d'una execució real.
- **Validació en temps d'execució:** comprovacions executables com
  `isinstance`, comprovacions de tipus exacte, comprovacions de rang i
  excepcions explícites.
- **Unió:** valor que pot tenir un de diversos tipus declarats. `int | None`
  significa un enter o absència.
- **Refinament de tipus:** evidència que permet a l'analitzador i a la persona
  lectora reduir una unió dins una branca, com ara `value is None`.
- **Tipatge estructural:** acceptar un objecte perquè presenta la forma de
  mètode requerida, no perquè hereta d'una classe base amb nom.
- **Genèric:** codi en què la relació entre entrada i sortida s'expressa amb una
  variable de tipus en lloc d'un únic tipus de dades fix.
- **Via d'escapament:** `Any`, `cast` o una instrucció d'ignorar que demana a
  l'analitzador que confiï en codi que no pot demostrar. Les vies d'escapament
  exigeixen una frontera estreta i explicada.

El flux complet, expressat en prosa, és aquest: una persona desenvolupadora
escriu codi font i anotacions; un analitzador pot estudiar aquestes anotacions
abans d'una execució; l'intèrpret executa el codi font; les comprovacions
explícites en temps d'execució inspeccionen valors vius a la frontera; les
proves observen execucions seleccionades. No cal cap fletxa, color ni posició en
un diagrama per distingir aquestes quatre responsabilitats.

## Itinerari essencial: informació útil sense una aplicació falsa

### E1. Anota una funció que ja entens

Objectiu: comunicar el tipus de cada entrada i del resultat retornat tot
conservant el comportament conegut de la funció.

Llegeix aquesta signatura d'esquerra a dreta: s'espera que `sku` sigui una
cadena, `stock` associa cadenes amb enters i la funció retorna un enter o
`None`. Abans d'executar-la, prediu totes dues línies. En particular, decideix
si una quantitat emmagatzemada de `0` vol dir «absent».

```python runnable
def find_quantity(sku: str, stock: dict[str, int]) -> int | None:
    return stock.get(sku)


quantities = {"PART-7": 0, "PART-8": 4}
print(find_quantity("PART-7", quantities))
print(find_quantity("UNKNOWN", quantities))
```

```text output
0
None
```

L'anotació no modifica `dict.get`. El comportament en temps d'execució continua
provenint del cos de la funció. L'anotació de retorn fa visibles els dos
resultats sense que calgui llegir abans tots els punts de crida.

Les col·leccions tipades descriuen els seus membres:

- `list[str]` és una llista amb valors de cadena;
- `dict[str, int]` associa claus de cadena amb valors enters; i
- `tuple[str, int]` és una tupla de dues posicions, primer una cadena i després
  un enter.

Tria el tipus concret que expressa l'operació real. No hi afegeixis un tipus
només perquè sembla més avançat.

**Modifica — TODO d'O1:** afegeix anotacions al paràmetre i al retorn sense
canviar el cos ni la sortida.

```python todo
def total_units(quantities):
    return sum(quantities)


print(total_units([2, 3, 5]))
```

**Pista:** l'entrada és una llista concreta d'enters i `sum` retorna un enter
en aquest domini. Comença amb `list[int]`; la profunditat dels iterables
genèrics pertany a l'itinerari professional.

**Solució explicada:** `def total_units(quantities: list[int]) -> int:` diu la
veritat sobre la col·lecció que accepta aquest exercici. El cos continua sent
`return sum(quantities)`, de manera que la sortida es manté en `10`. Una
anotació és més útil quan conserva i aclareix un contracte ja triat.

### E2. Refina `None` sense perdre un zero vàlid

Objectiu: distingir l'absència d'un valor fals però present.

Quan un valor té el tipus `int | None`, comprova primer `is None`. A l'altra
branca, el valor s'ha refinat a `int`. Prediu la sortida per a `0` i `None`:

```python runnable
def quantity_label(quantity: int | None) -> str:
    if quantity is None:
        return "unknown"
    return f"{quantity} units"


print(quantity_label(0))
print(quantity_label(None))
```

```text output
0 units
unknown
```

El temptador `if not quantity:` fusionaria `0` amb l'absència i canviaria el
contracte de l'inventari. La veracitat booleana pot ser útil, però no substitueix
una decisió explícita sobre l'absència.

**Cas límit:** una col·lecció buida, una cadena buida, `False` i `0` són tots
falsos en contextos booleans, però cap d'ells és el sentinella `None`. Formula
«això és absent?» i «això és buit o zero?» com dues preguntes de domini
separades.

### E3. Observa que les anotacions no executen la validació

Objectiu: separar les metadades, les operacions i la validació explícita.

Aquesta funció declara cadenes, però el cos es limita a retornar l'objecte que
rep. Python emmagatzema les anotacions i executa el cos; no hi afegeix una
comprovació de tipus amagada. Prediu què imprimeix aquesta crida
intencionadament incorrecta:

```python runnable
def echo_label(label: str) -> str:
    return label


print(echo_label(7))
```

```text output
7
```

Que el procés acabi correctament **no** demostra que la crida compleixi el
contracte declarat. Un analitzador estàtic pot informar de la incompatibilitat.
El programa també pot fallar més tard en temps d'execució quan una operació necessita el comportament
promès:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one("2"))
```

El senyal estable és `TypeError`; el text complet del traceback pot canviar.
L'error prové d'intentar sumar una cadena i un enter, no pas de l'anotació.

**Recuperació:** proporciona a la funció un enter real. Aquest exemple correcte
veí demostra que la correcció arriba a l'operació prevista:

```python runnable
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one(2))
```

```text output
3
```

Error habitual: afirmar que «Python ha comprovat el tipus» perquè un valor
incorrecte ha provocat una excepció. L'operació ha rebutjat aquell valor
concret. Un cos diferent podria acceptar-lo accidentalment, com ha fet
`echo_label`.

### E4. Valida la frontera i després confia en el nucli tipat

Objectiu: convertir un valor desconegut en temps d'execució en un enter validat
o en un error clar i recuperable.

A la frontera d'un fitxer, una ordre, HTTP o un objecte de correspondències de
forma poc definida,
el tipus d'entrada honest pot ser `object`. Comprova primer el tipus en temps
d'execució i després el rang del domini. Aquí la comprovació de tipus exacte és
deliberada perquè `bool` és una subclasse d'`int`, mentre que una quantitat
d'inventari no ha d'acceptar `True` com una unitat.

```python runnable
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(0))
print(parse_quantity(1_000_000))
```

```text output
0
1000000
```

Prediu la categoria d'excepció abans d'executar aquest error de frontera:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def parse_quantity(value: object) -> int:
    if type(value) is not int:
        raise TypeError("quantity must be a built-in int, not bool")
    if not 0 <= value <= 1_000_000:
        raise ValueError("quantity must be between 0 and 1000000")
    return value


print(parse_quantity(True))
```

**Recuperació:** substitueix `True` per l'enter previst, torna-ho a executar i
mantén el valor extern original sense modificar fins que la validació tingui
èxit. Cal validar abans d'afegir a una col·lecció o d'actualitzar qualsevol
altre estat.

### Repte essencial guiat

Construeix `reorder_message`. Rep el resultat opcional de `find_quantity` i ha
de distingir una quantitat desconeguda, zero i una quantitat positiva.

```python todo
def reorder_message(quantity: int | None) -> str:
    # TODO 1: return "unknown SKU" only for None
    # TODO 2: return "reorder now" for zero
    # TODO 3: otherwise return "stock: N"
    ...


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

**Pista:** refina primer amb `is None`. Després d'aquesta branca, `quantity` és
un enter i, per tant, pots comparar-lo amb `0`.

**Solució explicada:** l'ordre de les preguntes conserva el domini. Pregunta
primer si el valor és absent i després si l'enter present és zero.

```python runnable
def reorder_message(quantity: int | None) -> str:
    if quantity is None:
        return "unknown SKU"
    if quantity == 0:
        return "reorder now"
    return f"stock: {quantity}"


print(reorder_message(None))
print(reorder_message(0))
print(reorder_message(4))
```

```text output
unknown SKU
reorder now
stock: 4
```

### Punt de control essencial i rúbrica

Puntua cada element amb 0 o 1 punt:

1. **Correcció:** els casos normal, zero i absent produeixen el resultat indicat.
2. **Claredat de les anotacions:** els paràmetres i els retorns expressen el
   contracte real.
3. **Frontera en temps d'execució:** els valors `bool`, de tipus incorrecte i
   fora de rang es rebutgen abans de cap mutació.
4. **Recuperació:** pots explicar i demostrar una repetició corregida.
5. **Explicació:** pots dir per què una anotació, un analitzador, una operació i
   la validació explícita són conceptes diferents.

Per completar-lo calen almenys 4/5 punts, inclosos els punts 3 i 5. Si vols,
atura't aquí: pots afegir anotacions útils sense instal·lar cap eina de tercers.
Reflexió: quina frontera d'un dels teus programes rep valors que les anotacions
no poden fer segurs per si soles?

## Itinerari professional: forma, comportament i relacions

### P1. Dona una forma estable als registres de diccionari amb `TypedDict`

Objectiu: descriure claus conegudes tot recordant que l'objecte en temps
d'execució encara és un diccionari ordinari.

El registre normalitzat del codi complementari té exactament els dos camps
emprats en aquesta lliçó:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class InventoryRow(TypedDict):
    """A normalized inventory record used inside the typed core."""

    sku: str
    quantity: int
```

`TypedDict` ajuda les eines estàtiques a comprovar noms de camps i valors. No
embolcalla el diccionari ni rebutja un objecte de correspondències incorrecte
en temps d'execució.
La frontera explícita continua sent `parse_row`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def parse_row(raw: Mapping[str, object]) -> InventoryRow:
    """Validate and normalize one untrusted mapping without mutating it.

    ``sku`` must be a string whose stripped form contains 1 through 32
    characters.  ``quantity`` must be a built-in ``int`` (never ``bool``) in
    the inclusive range 0 through 1,000,000.
    """
```

El contracte provat elimina espais als extrems i converteix l'SKU a majúscules,
accepta entre 1 i 32 caràcters normalitzats i una quantitat entera exacta entre
0 i 1.000.000. Els camps absents o de tipus incorrecte provoquen `TypeError`;
els SKU buits o massa llargs i les quantitats fora de rang provoquen
`ValueError`. L'objecte de correspondències d'entrada es manté sense canvis en
tots els casos.

Executa l'evidència de la biblioteca estàndard des de l'arrel del repositori:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

L'entrada correcta `{"sku": "  part-7 ", "quantity": 0}` es converteix en
`{"sku": "PART-7", "quantity": 0}`. S'accepta el límit superior: 32 caràcters i
1.000.000 d'unitats. Un SKU de 33 caràcters, `-1`, `1_000_001` o una quantitat
booleana es rebutgen abans d'afegir cap fila d'inventari.

**Modifica — TODO d'O3/O4:** afegeix una prova en temps d'execució per a un
camp `quantity` absent. Prediu la categoria d'excepció i copia l'entrada abans
de la crida. **Pista:** en aquest contracte didàctic, un camp obligatori absent
és un error de forma/tipus. **Solució:** comprova `TypeError` i després comprova
que l'objecte de correspondències encara és igual a la còpia. No converteixis
el camp estàtic en opcional només per silenciar un requisit real de frontera.

### P2. Expressa la relació d'un callback amb `Callable` i `TypeVar`

Objectiu: conservar el tipus de l'element tot acceptant una operació de
predicat passada com a callback.

`Callable[[T], bool]` es llegeix «un cridable que rep un `T` i retorna un
booleà». El mateix `T` al resultat indica que la funció retorna un element del
tipus d'entrada o `None`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    """Return the first matching item, or ``None`` after finite exhaustion."""

    for item in items:
        if predicate(item):
            return item
    return None
```

La funció s'atura a la primera coincidència. Una entrada finita buida o sense
coincidències retorna `None`. Si l'entrada és un iterador d'un sol ús, la seva
posició queda després de l'element coincident; el tipatge no el rebobina.

**Predicció:** per als valors generats `1, 2, 3, 4` i el predicat
`value == 3`, quantes crides al predicat es fan i què retorna el següent
`next` directe? Les proves observen tres crides al predicat i després el valor
`4`.

**Modifica — TODO d'O5:** usa `first_matching` per trobar la primera fila amb
quantitat `0`. **Pista:** el paràmetre del callback és un `InventoryRow`, per
tant accedeix a `row["quantity"]`. La solució explicada retorna
`InventoryRow | None`; refina amb `is None` abans de llegir `row["sku"]`.

Error habitual: substituir `T` per `object`. Això perdria la relació útil entre
els elements d'entrada i la coincidència retornada. Una variable de tipus no
significa «qualsevol valor sense comprovació»; connecta posicions dins una
mateixa crida.

### P3. Accepta comportaments estructuralment amb `Protocol`

Objectiu: dependre de la forma d'un sol mètode sense forçar l'herència.

L'inventari necessita una font que pot conèixer o no un preu:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class PriceSource(Protocol):
    """Anything with this method shape can supply an optional unit price."""

    def unit_price(self, sku: str) -> float | None:
        """Return the unit price, or ``None`` when the SKU is unknown."""
```

Una classe no ha d'heretar de `PriceSource`. Si el seu mètode accepta `str` i
retorna `float | None`, un analitzador estàtic pot acceptar-la estructuralment:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
class Catalogue:
    def unit_price(self, sku: str) -> float | None:
        return {"PART-7": 2.5}.get(sku)
```

Aquesta és una relació estàtica. El protocol base no està marcat amb
`runtime_checkable`, i fins i tot una comprovació de forma en temps d'execució
no demostraria que cada valor de retorn futur respecti l'anotació. Les proves i
la validació de la frontera continuen sent responsables del comportament en
temps d'execució.

**Cas límit:** el preu `0.0` és present i no s'ha de confondre amb `None`.
**Incompatibilitat recuperable:** si una implementació accepta SKU `int` i
retorna `str`, corregeix-ne la signatura pública i el comportament; no hi
afegeixis herència ni `cast` només per suprimir l'avís de l'analitzador.

### P4. Conserva el tipus de la instància fluida amb `Self`

Objectiu: declarar que un mètode fluid retorna el tipus exacte del receptor,
incloses les subclasses.

El codi complementari valida i copia una fila abans de la mutació i després
retorna la mateixa instància:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
    def add(self, row: InventoryRow) -> Self:
        """Validate, copy, and append ``row``; return this exact instance."""

        normalized = parse_row(row)
        self._rows.append(normalized)
        return self
```

`Self` és més precís que escriure `Inventory`: una crida a l'`add` heretat
sobre un `LabelledInventory` continua tipada com a `LabelledInventory`. En
temps d'execució, la prova també demostra la identitat amb `is`; no es limita a
confiar en l'anotació.

**Error i recuperació:** afegir una quantitat booleana provoca una excepció
abans d'afegir-la. La tupla anterior de files es manté igual. Corregeix l'entrada
i torna a cridar `add`; la mateixa instància rep una còpia normalitzada. Ni
modificar el diccionari original de la persona que crida ni un diccionari
retornat per `.rows` altera l'estat emmagatzemat.

### Repte professional guiat

Crea una classe `WarehousePrices` amb
`unit_price(sku: str) -> float | None`; després troba la primera fila amb
quantitat zero i consulta'n el preu.

```python todo
from typing import assert_type

# TODO 1: implement WarehousePrices without inheriting PriceSource
# TODO 2: find the first zero-quantity InventoryRow
# TODO 3: narrow the optional row and optional price with `is None`
# TODO 4: add the row to a subclass of Inventory and preserve the subclass type
```

**Pista:** a un protocol estructural li importa la forma del mètode públic.
Mantén separades les dues decisions d'absència: que no hi hagi cap fila
coincident i que no hi hagi preu són dos resultats de domini diferents.

**Solució explicada:** `WarehousePrices.unit_price` accepta `str` i retorna el
resultat de `dict[str, float].get`, de manera que satisfà `PriceSource` sense
herència. `first_matching` conserva `InventoryRow` com el seu `T`. Després de
cada branca `is None`, el valor restant queda refinat. `Self` conserva la
subclasse d'inventari al llarg d'`add`. Les proves en temps d'execució continuen
sent necessàries per als límits de l'entrada, la no-mutació i la identitat de
l'objecte.

### Punt de control professional i rúbrica

Puntua cada element amb 0 o 1 punt:

1. Els camps de `TypedDict` coincideixen amb el contracte normalitzat en temps
   d'execució.
2. `Callable` i `TypeVar` conserven la relació entre el callback i el retorn.
3. Una implementació estructural de `Protocol` funciona sense herència forçada.
4. `Self` conserva tant la subclasse estàtica com la identitat de l'objecte en
   temps d'execució.
5. Una entrada invàlida a la frontera deixa totes les files existents sense
   canvis.
6. La teva explicació separa la forma estàtica del comportament en temps
   d'execució.

Per completar-lo calen almenys 5/6 punts, inclosos els punts 5 i 6. Pots
aturar-te aquí amb un codi complementari completament executable i provat.
Reflexió: quina interfície d'un projecte més gran necessita un contracte de
comportament, i quina frontera d'entrada encara necessita validació executable?

## Itinerari avançat opcional: evidència de l'analitzador i recuperació

### A1. Proveeix deliberadament l'eina declarada

L'itinerari en temps d'execució només fa servir la biblioteca estàndard.
L'itinerari amb analitzador declara una única versió exacta i directa d'una
eina de desenvolupament a `requirements-dev.lock`: `mypy==2.2.0`. Malgrat el
nom del fitxer, **no** és un fitxer de bloqueig generat per un resolutor,
complet amb hashes,
transitiu i multiplataforma. Registra una única versió directa de l'eina per al
contracte d'evidència declarat.

Si una persona mantenidora prepara deliberadament un entorn virtual d'un sol ús
fora del repositori, aquesta ordre d'instal·lació pot necessitar accés a la
xarxa o a un índex:

```text illustrative
python -m pip install -r chapter-27-python-typing/requirements-dev.lock
```

La instal·lació és una acció de preparació separada. El verificador no
l'executa mai, no contacta cap índex i no considera equivalent un analitzador
global o d'una versió diferent. No creïs `.venv` dins aquest capítol.

### A2. Compara consumidors positius, negatius i corregits

El consumidor positiu comprova files tipades, la inferència del retorn genèric,
una font de preus estructural i `Self`:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
prices: PriceSource = Catalogue()
assert_type(prices.unit_price(row["sku"]), float | None)

inventory = LabelledInventory()
assert_type(inventory.add(row), LabelledInventory)
```

El consumidor negatiu és intencionadament invàlid. Llegeix-lo abans
d'executar-lo i prediu una categoria per error:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_negative.py check=learning:contract -->
```python source-ref
bad_row: InventoryRow = {"sku": "PART-7", "quantity": "many"}
Inventory().add("not an inventory row")


class BrokenPrices:
    def unit_price(self, sku: int) -> str:
        return str(sku)


prices: PriceSource = BrokenPrices()
```

Les categories estables d'acceptació són:

- `[typeddict-item]` per un valor incorrecte en un camp declarat d'un
  `TypedDict`;
- `[arg-type]` per l'argument incompatible d'`Inventory.add`; i
- `[assignment]` per assignar a `PriceSource` una classe amb un mètode
  incompatible.

El text complet, els prefixos de les fonts, les notes, els colors i el format
dels accents circumflexos no són una sortida de referència. El verificador
requereix un resultat diferent de zero i els tres tokens de categoria.

El consumidor corregit repara els contractes en lloc d'amagar-los:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_corrected.py check=learning:contract -->
```python source-ref
row: InventoryRow = {"sku": "PART-7", "quantity": 3}
inventory = Inventory().add(row)
assert_type(inventory, Inventory)


class FixedPrices:
    def unit_price(self, sku: str) -> float | None:
        return 1.25 if sku == "PART-7" else None
```

Error habitual: afegir un `Any` sense límits, un simple `# type: ignore` o un
`cast` que no canvia cap comportament en temps d'execució. Corregeix primer el
valor, la signatura o la frontera. Quan una limitació externa real exigeixi una
via d'escapament, limita-la a l'expressió més petita, usa una instrucció
d'ignorar específica per codi quan sigui possible i documenta per què
l'evidència en temps d'execució cobreix el buit.

**Modifica — TODO d'O6:** copia un cas negatiu a un fitxer de treball d'un sol
ús, prediu-ne la categoria, corregeix el contracte subjacent i torna a executar
la mateixa configuració de l'analitzador. **Pista:** no editis el cas negatiu
canònic; el verificador el necessita com a evidència d'error esperat.
**Solució:** el cas corregit demostra les tres reparacions mentre la suite en
temps d'execució prova que el nucli tipat continua funcionant.

### A3. Executa el verificador acotat

Des de l'arrel del repositori, selecciona sempre explícitament la verificació en
temps d'execució:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

La verificació amb l'analitzador és una selecció separada:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

El verificador:

1. captura l'estat del codi font del capítol i rebutja memòries cau o bytecode
   preexistents;
2. copia només el codi complementari, les proves i els tres consumidors a una
   arrel temporal;
3. usa l'intèrpret actual amb `-I -B`, sense stdin, amb un entorn mínim, un
   límit de 20 segons, un límit combinat de sortida de 64 KiB i neteja del grup
   de processos;
4. executa les proves en temps d'execució o comprova la versió exacta
   `mypy==2.2.0`;
5. en mode analitzador, exigeix que el positiu quedi net, que el negatiu surti
   diferent de zero amb les tres categories estables i que el corregit quedi
   net; i
6. elimina l'arrel temporal, compara l'estat del capítol, busca residus i
   informa de la neteja independentment.

El codi de sortida `0` significa que el contracte seleccionat i la neteja han
passat. El codi `1` significa que ha fallat un comportament seleccionat, un
límit, la integritat del codi font o una comprovació de neteja. El codi `2`
significa que l'ús de l'ordre és incorrecte o que falta el prerequisit exacte
de l'analitzador. L'evidència absent de l'analitzador ha de continuar sent
**prerequisit absent**; no es pot presentar com un aprovat.

El verificador limita els accidents de fonts didàctiques de confiança; no és un
entorn de confinament per a codi hostil. Només demostra l'execució amb
l'intèrpret o l'eina seleccionats. No demostra totes les plataformes, totes les versions de Python,
la naturalitat d'una traducció, l'eficàcia didàctica, l'accessibilitat, la
compatibilitat dels paquets ni la seguretat en producció.

### Punt de control avançat i rúbrica

Puntua cada element amb 0 o 1 punt:

1. La versió exacta proveïda de l'analitzador coincideix amb la versió directa.
2. Els consumidors positiu i corregit queden nets amb les mateixes opcions
   estrictes.
3. El consumidor negatiu surt diferent de zero per totes tres categories
   estables.
4. Les proves en temps d'execució encara passen després de la correcció.
5. Cap `Any` ampli, instrucció d'ignorar sense qualificar o `cast` només per a
   l'evidència amaga un defecte.
6. La neteja passa i no apareix cap memòria cau de l'analitzador al repositori.

Per completar-lo calen els sis punts. Si la versió no hi és, mantén aquest
itinerari pendent i conserva el punt de control professional. Reflexió: què ha
trobat l'analitzador abans de l'execució, i quin fet important del temps
d'execució encara no ha pogut demostrar?

## Errors habituals i recuperació tranquil·la

- **«Anotat vol dir validat».** Torna a E3, identifica l'operació que s'ha
  executat realment i situa la validació explícita a la frontera d'entrada.
- **Usar `if not value` per a `T | None`.** Revisa el cas `0` i refina amb
  `is None` quan la pregunta és l'absència.
- **Anotar cada valor amb el tipus més ampli.** Parteix del contracte realment
  acceptat; amplia'l només quan el comportament accepti de debò més possibilitats.
- **Usar `TypedDict` com a validador en temps d'execució.** Mantén `parse_row` a
  la frontera no fiable i retorna la forma tipada només després de validar.
- **Forçar l'herència d'un protocol.** Fes coincidir la forma del mètode públic;
  l'herència és una decisió de disseny separada.
- **Silenciar els diagnòstics.** Corregeix la incompatibilitat més petita i
  torna a executar l'exemple veí en temps d'execució i l'anàlisi estàtica des
  d'una arrel temporal neta.
- **Anomenar fitxer de bloqueig universal una versió directa.** Registra l'eina,
  la versió, el sistema amfitrió, l'objectiu de Python, els supòsits d'adquisició
  i l'execució real. No
  dedueixis una resolució transitiva o multiplataforma.

## Verificació de manteniment i límit de l'evidència

Tots els fragments del codi complementari d'aquest capítol usen la comprovació
de referència a font registrada `learning:contract`. El connector responsable
pot seleccionar aquest contracte; la validació genèrica del llibre comprova el
Markdown i la forma declarada de la referència sense executar silenciosament
fitxers complementaris arbitraris.

Executa primer l'evidència estreta en temps d'execució:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Executa l'evidència de l'analitzador només quan `mypy==2.2.0` ja sigui present a
l'intèrpret seleccionat:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

No instal·lis cap analitzador com a pas de validació ocult. Registra per separat
els resultats en temps d'execució i els de l'analitzador. Que l'analitzador
passi no substitueix les proves en temps d'execució; que l'estructura passi no
aprova la fluïdesa lingüística, la pedagogia, l'accessibilitat, la renderització
bidireccional, la procedència ni la publicació.

## Reflexió final i passos següents

Un bon tipatge facilita entendre una frontera real. No fa Python menys dinàmic
ni elimina la necessitat de validar els valors externs. Usa l'anotació més
petita que aclareixi una relació i després demostra el comportament en temps
d'execució a la frontera on els errors importen.

Per a interfícies de paquets nadius, continua de manera independent amb el
[Capítol 24: Python i C++](../chapter-24-python-cpp-integration/README.ca.md) o
el [Capítol 25: Python i Rust](../chapter-25-python-rust-integration/README.ca.md).
Per a un projecte que combina modelatge de domini, persistència, CLI, proves,
registre d'esdeveniments i verificació d'artefactes, continua amb el
[Capítol 28: Projecte professional](../chapter-28-professional-capstone/README.ca.md).
