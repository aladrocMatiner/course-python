# Kapitel 27 · Gradvis typning och statisk analys

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad vi ska bygga

I Python kan du lägga till typinformation gradvis. Du kan annotera en användbar
gräns i dag utan att skriva om hela programmet. Annotationer hjälper en läsare,
en editor eller en statisk typkontroll att resonera om värden före körning. De
inspekterar eller avvisar inte automatiskt värden under körning.

Vi utvecklar ett litet, syntetiskt lagerexempel i tre lugna steg:

1. **Grundnivå:** annotera funktioner och samlingar, representera frånvaro med
   `None`, smalna av en union och håll körtidsvalidering uttrycklig.
2. **Professionell:** ge ordboksposter en form med `TypedDict`, acceptera
   beteende strukturellt med `Protocol`, skicka typade anropbara objekt, bevara
   en generisk resultattyp och använd `Self` för en fluent-metod.
3. **Valfri kontrollväg:** jämför en giltig konsument med en avsiktligt ogiltig,
   känn igen stabila felkategorier, reparera kontraktet och kör en begränsad
   verifierare när den exakta verktygsversionen redan har installerats.

Den körbara auktoriteten är
[`examples/typed_inventory.py`](examples/typed_inventory.py). Körtidstester och
kontrollfixturer använder bara syntetiska SKU:er och kvantiteter. De använder
inte nätverk, databas, autentiseringsuppgift, personpost, paketindex eller
elevfil.

## Lärandemål

När du har slutfört den väg du väljer kommer du att kunna:

- **O1 — Läsa och skriva annotationer:** annotera parametrar, returvärden och
  konkreta samlingar utan att påstå att annotationerna utför validering.
- **O2 — Modellera frånvaro:** använda `T | None`, bevara giltiga falska värden
  som kvantiteten `0` och smalna av frånvaro med `is None`.
- **O3 — Validera en körtidsgräns:** ta emot ett `object`, kontrollera dess
  verkliga typ och domängränser, avvisa `bool` när ett exakt heltal krävs och
  återhämta dig utan partiell mutation.
- **O4 — Beskriva postens form:** använda `TypedDict` för de stabila nycklarna
  och värdetyperna i en ordbok som redan finns i den typade kärnan.
- **O5 — Typa beteende och återanvändbara algoritmer:** använda `Callable`,
  strukturell `Protocol`, `TypeVar` och `Self` där varje verktyg gör ett verkligt
  kontrakt tydligare.
- **O6 — Läsa statisk evidens ärligt:** skilja kontrollverktygets diagnostik
  från Python-undantag, förlita dig på stabila kategorier snarare än fullständig
  formulering och rätta en ogiltig konsument till ett rent resultat.
- **O7 — Förklara evidensgränsen:** ange vad körtidstester, ett kontrollverktyg
  och mänsklig granskning var och en gör—och vad inget av dem ensamt bevisar.

[Spårbarhetsposten](TRACEABILITY.md) kopplar dessa mål till undervisning,
övning, lösningar, källreferenser, tester och kontrollpunkter.

## Förkunskaper och vägkarta

Slutför grundkontrollpunkterna i följande kapitel innan du börjar:

- [Kapitel 11: Funktioner](../chapter-11-functions/README.sv.md), för parametrar,
  returvärden och `None`;
- [Kapitel 15: Moduler](../chapter-15-modulos/README.sv.md), för importer och
  publika modulgränser;
- [Kapitel 18: Testning](../chapter-18-testing/README.sv.md), för observerbara
  normal- och felkontrakt; och
- [Kapitel 22: Introspektion](../chapter-22-introspection/README.sv.md), för
  skillnaden mellan ett objekts körtidsbeteende och information som verktyg
  inspekterar.

Den numeriska placeringen efter kapitel 26 gör inte nätverk, C++ eller Rust till
förkunskaper.

- **Grundväg · 2 pass på 45–60 minuter.** Läs E1–E4, slutför grundutmaningen
  och bedöm dess matris. Resultat: en typad uppslagning plus en uttryckligt
  validerad heltalsgräns. Slutförande: 1 poäng i var och en av de fem
  slutkategorierna — körtidskorrekthet, annotations- och statiskt kontrakt,
  gränsåterhämtning, läsbarhet och förklaring — så ingen kategori får 0. Säker
  stoppunkt: använd annotationerna i vanlig Python och fortsätt utan att
  installera ett kontrollverktyg.
- **Professionell väg · 2 pass på 50–70 minuter.** Slutför grundkontrollpunkten,
  sedan P1–P4 och den professionella utmaningen. Resultat: utöka det testade
  lagerkontraktet med typade rader, en generisk sökning, en strukturell
  priskälla och fluent-anrop som bevarar underklass. Slutförande: 1 poäng i var
  och en av samma fem slutkategorier; ingen kategori får 0. Säker stoppunkt: du
  kan konsumera typade biblioteksgränssnitt utan att köra den valfria
  kontrollvägen.
- **Valfri kontrollväg · 1 pass på 45–60 minuter.** Slutför den professionella
  kontrollpunkten och använd en isolerad miljö där den exakta direkta
  verktygsversionen redan medvetet har installerats. Resultat: förklara tre
  diagnostikkategorier, observera en förväntad fixtur med nollskild slutkod och
  bevisa att dess rättade motsvarighet är ren. Slutförande: körtid godkänns,
  positiv godkänns, negativ misslyckas för alla deklarerade kategorier, rättad
  godkänns och städning godkänns. Ett saknat eller annorlunda kontrollverktyg är
  ett saknat förkunskapsresultat, inte en misslyckad elevkontrollpunkt och aldrig
  ett godkänt resultat.

Återkommande elev? Förklara varför `def echo(value: str) -> str:` inte hindrar
ett körtidsanrop från att ta emot `7`. Förklara sedan varför `if value is None`
bevarar ett giltigt `0`. Om båda är tydliga, börja på den professionella vägen.
Om du också kan förklara strukturell undertypning och varför `list[Dog]` inte
automatiskt är en `list[Animal]`, använd den professionella kontrollpunkten som
en snabb revision före den valfria kontrollvägen.

## En liten ordlista

- **Annotation:** typinformation som fästs vid ett namn, en parameter eller en
  returposition. Det är metadata; Python gör den inte till en validerare som
  standard.
- **Statisk typkontroll:** ett separat verktyg som analyserar källkod utan att
  använda varje värde från en faktisk körning.
- **Körtidsvalidering:** körbara kontroller som `isinstance`, exakta
  typkontroller, intervallkontroller och uttryckliga undantag.
- **Union:** ett värde som kan ha en av flera deklarerade typer. `int | None`
  betyder ett heltal eller frånvaro.
- **Avsmalning:** evidens som låter ett kontrollverktyg och en läsare minska en
  union i en gren, som `value is None`.
- **Strukturell typning:** att acceptera ett objekt eftersom det har den
  metodform som krävs, inte för att det ärver från en namngiven basklass.
- **Generisk:** kod vars relation mellan indata och utdata uttrycks med en
  typvariabel i stället för en enda fast datatyp.
- **Nödutgång:** `Any`, `cast` eller en ignore som ber kontrollverktyget lita på
  kod det inte kan bevisa. Nödutgångar kräver en smal, förklarad gräns.

Det fullständiga flödet i prosa är: en utvecklare skriver källkod och
annotationer; ett kontrollverktyg kan analysera annotationerna före körning;
tolken kör källkoden; uttryckliga körtidskontroller inspekterar levande
gränsvärden; tester observerar valda körningar. Ingen pil, färg eller position i
ett diagram behövs för att skilja dessa fyra ansvarsområden.

## Grundväg: användbar information utan falsk verkställighet

### E1. Annotera en funktion du redan förstår

Mål: kommunicera typen för varje indata och det returnerade resultatet och
samtidigt bevara välbekant funktionsbeteende.

Läs signaturen från vänster till höger: `sku` förväntas vara en sträng,
`stock` mappar strängar till heltal och funktionen returnerar antingen ett
heltal eller `None`. Förutsäg båda raderna innan du kör. Avgör särskilt om en
lagrad kvantitet på `0` betyder ”saknas”.

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

Annotationen ändrar inte `dict.get`. Körtidsbeteendet kommer fortfarande från
funktionskroppen. Returannotationen gör de två utfallen synliga innan någon
läser varje anropsplats.

Typade samlingar beskriver sina medlemmar:

- `list[str]` är en lista vars värden är strängar;
- `dict[str, int]` mappar strängnycklar till heltalsvärden; och
- `tuple[str, int]` är en tuple med en sträng och sedan ett heltal i två
  positioner.

Föredra den konkreta typ som uttrycker den verkliga operationen. Lägg inte till
en typ bara för att den ser mer avancerad ut.

**Ändra — O1 TODO:** Lägg till parameter- och returannotationer utan att ändra
kroppen eller utdatan.

```python todo
def total_units(quantities):
    return sum(quantities)


print(total_units([2, 3, 5]))
```

**Ledtråd:** indatan är en konkret lista av heltal och `sum` returnerar ett
heltal för denna domän. Börja med `list[int]`; djupare generiskt itererbart
material tillhör den professionella vägen.

**Förklarad lösning:** `def total_units(quantities: list[int]) -> int:`
beskriver sanningsenligt samlingen som övningen accepterar. Kroppen förblir
`return sum(quantities)`, så utdatan är fortfarande `10`. En annotation är
mest användbar när den bevarar och förtydligar ett redan valt kontrakt.

### E2. Smalna av `None` utan att förlora ett giltigt noll

Mål: skilja frånvaro från ett falskt men närvarande värde.

När ett värde har typen `int | None`, kontrollera först `is None`. I den andra
grenen har värdet smalnats av till `int`. Förutsäg utdatan för `0` och `None`:

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

Det lockande `if not quantity:` skulle slå ihop `0` med frånvaro och ändra
lagerkontraktet. Sanningsvärde kan vara användbart, men det ersätter inte ett
uttryckligt beslut om frånvaro.

**Kantfall:** en tom samling, en tom sträng, `False` och `0` är alla falska i
booleska sammanhang, men inget av dem är sentineln `None`. Fråga ”är detta
frånvarande?” och ”är detta tomt eller noll?” som separata domänfrågor.

### E3. Observera att annotationer inte kör validering

Mål: skilja metadata, operationer och uttrycklig validering.

Den här funktionen utlovar strängar, men kroppen returnerar helt enkelt
objektet den tar emot. Python lagrar annotationerna och kör kroppen; det lägger
inte till en dold typkontroll. Förutsäg vad detta avsiktligt felaktiga anrop
skriver ut:

```python runnable
def echo_label(label: str) -> str:
    return label


print(echo_label(7))
```

```text output
7
```

Den framgångsrika processen är **inte** bevis för att anropet uppfyller det
deklarerade kontraktet. En statisk typkontroll kan rapportera skillnaden.
Körtiden kan också misslyckas senare när en operation behöver det utlovade
beteendet:

<!-- bookcheck: expect-error=TypeError timeout=5 -->
```python expected-error
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one("2"))
```

Den stabila signalen är `TypeError`; den fullständiga traceback-formuleringen
kan ändras. Felet kommer av försöket att addera en sträng och ett heltal, inte
av annotationen.

**Återhämtning:** ge funktionen ett verkligt heltal. Den här lyckade grannen
bevisar att rättningen når den avsedda operationen:

```python runnable
def add_one(quantity: int) -> int:
    return quantity + 1


print(add_one(2))
```

```text output
3
```

Vanligt misstag: att säga ”Python kontrollerade typen” eftersom ett felaktigt
värde råkade utlösa ett undantag. Operationen avvisade just det värdet. En annan
kropp kan acceptera det av misstag, som `echo_label` gjorde.

### E4. Validera gränsen och lita sedan på den typade kärnan

Mål: omvandla ett okänt körtidsvärde till ett validerat heltal eller ett tydligt
fel som går att återhämta sig från.

Vid en fil-, kommando-, HTTP- eller löst formad mapping-gräns kan den ärliga
indatatypen vara `object`. Kontrollera först körtidstypen och sedan
domänintervallet. En exakt typkontroll är avsiktlig här eftersom `bool` ärver
från `int`, medan en lagerkvantitet inte får acceptera `True` som en enhet.

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

Förutsäg undantagskategorin innan du kör detta gränsfel:

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

**Återhämtning:** ersätt `True` med det avsedda heltalet, kör igen och behåll
det ursprungliga externa värdet oförändrat tills valideringen lyckas.
Valideringen ska ske innan du lägger till i en samling eller uppdaterar något
annat tillstånd.

### Guidad grundutmaning

Bygg `reorder_message`. Den tar emot det valfria resultatet från
`find_quantity`. Den måste skilja mellan okänd, noll och en positiv kvantitet.

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

**Ledtråd:** smalna först av med `is None`. Efter den grenen är `quantity` ett
heltal, så jämför det med `0`.

**Förklarad lösning:** frågornas ordning bevarar domänen. Fråga först om värdet
saknas och sedan om det närvarande heltalet är noll.

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

### Grundkontrollpunkt och bedömningsmatris

Ge 0 eller 1 poäng för varje punkt:

1. **Körtidskorrekthet:** normal-, noll- och frånvarofallen ger det angivna
   resultatet, och ogiltiga gränsvärden avvisas före mutation.
2. **Annotations- och statiskt kontrakt:** parametrar och returer uttrycker det
   verkliga kontraktet, och du kan granska den statiska avsikten i källkoden
   utan att behöva köra ett kontrollverktyg.
3. **Gränsåterhämtning:** en ogiltig `bool`, fel typ eller ett värde utanför
   intervallet lämnar tillståndet oförändrat, och en rättad omkörning lyckas.
4. **Läsbarhet:** tydliga namn, explicit `is None`-avsmalning och en liten
   valideringsgräns gör besluten lätta att följa.
5. **Förklaring:** du kan säga varför en annotation, ett kontrollverktyg, en
   operation och uttrycklig validering är olika.

Slutförande kräver 1 poäng i var och en av de fem punkterna; ingen punkt får 0.
Du kan stanna här: du kan lägga till användbara annotationer utan att installera
något tredjepartsverktyg, och den valfria kontrollvägen ingår inte i denna
bedömning. Reflektion: vilken gräns i ett av dina program tar emot värden som
annotationer ensamma inte kan göra säkra?

## Professionell väg: form, beteende och relationer

### P1. Ge ordboksposter en stabil form med `TypedDict`

Mål: beskriva kända nycklar och samtidigt minnas att körtidsobjektet fortfarande
är en vanlig ordbok.

Den medföljande kodens normaliserade post har exakt de två fält som lektionen
använder:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class InventoryRow(TypedDict):
    """A normalized inventory record used inside the typed core."""

    sku: str
    quantity: int
```

`TypedDict` hjälper statiska verktyg att kontrollera fältnamn och värden. Det
slår inte in ordboken och avvisar inte en felaktig mapping vid körning. Den
uttryckliga gränsen är fortfarande `parse_row`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def parse_row(raw: Mapping[str, object]) -> InventoryRow:
    """Validate and normalize one untrusted mapping without mutating it.

    ``sku`` must be a string whose stripped form contains 1 through 32
    characters.  ``quantity`` must be a built-in ``int`` (never ``bool``) in
    the inclusive range 0 through 1,000,000.
    """
```

Det testade kontraktet tar bort omgivande blanksteg och gör SKU:n till versaler,
accepterar 1–32 normaliserade tecken och accepterar en exakt heltalskvantitet
från 0 till och med 1 000 000. Saknade eller feltypade fält höjer `TypeError`;
tomma eller för långa SKU:er och kvantiteter utanför intervallet höjer
`ValueError`. Indata-mappingen är oförändrad i samtliga fall.

Kör standardbiblioteksevidensen från rotkatalogen:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Giltig indata `{"sku": "  part-7 ", "quantity": 0}` blir
`{"sku": "PART-7", "quantity": 0}`. Den övre gränsen—32 tecken och
1 000 000 enheter—accepteras. En SKU med 33 tecken, `-1`, `1_000_001` eller
en boolesk kvantitet avvisas innan någon lagerrad läggs till.

**Ändra — O3/O4 TODO:** lägg till ett körtidstest för en saknad `quantity`.
Förutsäg undantagskategorin och kopiera indatan före anropet. **Ledtråd:** ett
saknat obligatoriskt fält är ett form-/typfel i detta undervisningskontrakt.
**Lösning:** kontrollera `TypeError` och sedan att mappningen fortfarande är
likadan som kopian. Försvaga inte det statiska fältet till valfritt bara för att
tysta ett verkligt gränskrav.

### P2. Uttryck en callback-relation med `Callable` och `TypeVar`

Mål: bevara elementtypen och samtidigt acceptera en enda predikatoperation.

`Callable[[T], bool]` betyder ”ett anropbart objekt som tar emot ett `T` och
returnerar ett booleskt värde”. Samma `T` i resultatet säger att funktionen
returnerar ett element av indatatypen, eller `None`:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
def first_matching(items: Iterable[T], predicate: Callable[[T], bool]) -> T | None:
    """Return the first matching item, or ``None`` after finite exhaustion."""

    for item in items:
        if predicate(item):
            return item
    return None
```

Funktionen stannar vid den första träffen. Tom eller omatchad ändlig indata
returnerar `None`. Om indatan är en engångsiterator ligger dess position kvar
efter det matchade elementet; typning spolar inte tillbaka den.

**Förutsäg:** hur många predikatanrop sker för generatorvärdena `1, 2, 3, 4`
och predikatet `value == 3`, och vad returnerar nästa direkta `next`? Testerna
observerar tre predikatanrop och sedan värdet `4`.

**Ändra — O5 TODO:** använd `first_matching` för att hitta den första raden med
kvantiteten `0`. **Ledtråd:** callback-parametern är en `InventoryRow`, så läs
`row["quantity"]`. Den förklarade lösningen returnerar `InventoryRow | None`;
smalna av med `is None` innan du läser `row["sku"]`.

Vanligt misstag: att ersätta `T` med `object`. Det skulle förlora den användbara
relationen mellan indatans element och den returnerade träffen. En typvariabel
är inte ”vilket värde som helst utan kontroll”; den kopplar samman positioner i
ett anrop.

### P3. Acceptera beteende strukturellt med `Protocol`

Mål: bero på en enda metodform utan att tvinga fram arv.

Lagret behöver en källa som kanske känner till ett pris:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
class PriceSource(Protocol):
    """Anything with this method shape can supply an optional unit price."""

    def unit_price(self, sku: str) -> float | None:
        """Return the unit price, or ``None`` when the SKU is unknown."""
```

En klass behöver inte ärva från `PriceSource`. Om dess metod tar emot `str` och
returnerar `float | None` kan en statisk typkontroll acceptera den strukturellt:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
class Catalogue:
    def unit_price(self, sku: str) -> float | None:
        return {"PART-7": 2.5}.get(sku)
```

Detta är en statisk relation. Basprotokollet är inte märkt
`runtime_checkable`, och inte ens en formkontroll vid körning skulle bevisa att
varje framtida returvärde följer annotationen. Tester och gränsvalidering äger
fortfarande körtidsbeteendet.

**Kantfall:** priset `0.0` finns och får inte blandas ihop med `None`.
**Återhämtningsbar skillnad:** om en implementation tar emot `int`-SKU:er och
returnerar `str`, rätta dess publika metodsignatur och beteende; lägg inte till
arv eller `cast` enbart för att tysta kontrollverktyget.

### P4. Bevara den fluenta instanstypen med `Self`

Mål: ange att en fluent-metod returnerar den exakta mottagartypen, inklusive
underklasser.

Den medföljande koden validerar och kopierar en rad före mutation och returnerar
sedan samma instans:

<!-- bookcheck: path=chapter-27-python-typing/examples/typed_inventory.py check=learning:contract -->
```python source-ref
    def add(self, row: InventoryRow) -> Self:
        """Validate, copy, and append ``row``; return this exact instance."""

        normalized = parse_row(row)
        self._rows.append(normalized)
        return self
```

`Self` är mer precist än att skriva `Inventory`: när ärvda `add` anropas på en
`LabelledInventory` förblir typen `LabelledInventory`. Vid körning bevisar
testet också identitet med `is`; det litar inte bara på annotationen.

**Fel och återhämtning:** att lägga till en boolesk kvantitet höjer ett undantag
före append. Den föregående tuplen av rader förblir likadan. Rätta indatan och
anropa `add` igen; samma instans får en normaliserad kopia. Varken mutation av
anroparens ursprungliga ordbok eller en ordbok som returneras av `.rows` ändrar
det lagrade tillståndet.

### Professionell guidad utmaning

Skapa en `WarehousePrices`-klass med
`unit_price(sku: str) -> float | None`, hitta sedan den första raden med
nollkvantitet och fråga efter dess pris.

```python todo
from typing import assert_type

# TODO 1: implement WarehousePrices without inheriting PriceSource
# TODO 2: find the first zero-quantity InventoryRow
# TODO 3: narrow the optional row and optional price with `is None`
# TODO 4: add the row to a subclass of Inventory and preserve the subclass type
```

**Ledtråd:** ett strukturellt protokoll bryr sig om den publika metodformen.
Håll de två frånvarobesluten åtskilda: ingen matchande rad och inget pris är
olika domänutfall.

**Förklarad lösning:** `WarehousePrices.unit_price` tar emot `str` och
returnerar resultatet från `dict[str, float].get`, så den uppfyller
`PriceSource` utan arv. `first_matching` bevarar `InventoryRow` som sitt `T`.
Efter varje `is None`-gren är det återstående värdet avsmalnat. `Self` bevarar
lagerunderklassen genom `add`. Körtidstester behövs fortfarande för
indatagränser, icke-mutation och objektidentitet.

### Professionell kontrollpunkt och bedömningsmatris

Ge 0 eller 1 poäng för varje punkt:

1. **Körtidskorrekthet:** tester täcker normala resultat, objektidentitet och att
   ogiltig gränsindata lämnar alla befintliga rader oförändrade.
2. **Annotations- och statiskt kontrakt:** `TypedDict`, `Callable`, `TypeVar`,
   `Protocol` och `Self` uttrycker de avsedda relationerna, verifierbara genom
   källgranskning utan den valfria kontrollvägen.
3. **Gränsåterhämtning:** ett avvisat anrop skadar inte tillståndet, och ett
   rättat anrop på samma instans lyckas med normaliserad indata.
4. **Läsbarhet:** namn, avsmalningsgrenar och gränskontroller håller dataflödet
   och de två frånvarofallen tydliga.
5. **Förklaring:** din förklaring skiljer statisk form, körtidsbeteende,
   validering och återhämtning.

Slutförande kräver 1 poäng i var och en av de fem punkterna; ingen punkt får 0.
Du kan stanna här med en fullt körbar och testad kodbas; den versionsbundna
kontrollvägen är fortfarande valfri och ingår inte i denna bedömning.
Reflektion: vilket gränssnitt i ett större projekt behöver ett beteendekontrakt
och vilken inkommande gräns behöver fortfarande körbar validering?

## Valfri avancerad väg: kontrollevidens och återhämtning

### A1. Installera det deklarerade verktyget medvetet

Körtidsvägen använder endast standardbiblioteket. Kontrollvägen deklarerar en
exakt direkt version av utvecklingsverktyget i `requirements-dev.lock`:
`mypy==2.2.0`. Trots filnamnet är filen **inte** en resolvergenererad,
hashkomplett, transitiv och plattformsöverskridande låsfil. Den registrerar en
direkt verktygsversion för det deklarerade evidenskontraktet.

Om en underhållare medvetet förbereder en kasserbar virtuell miljö utanför
arkivet kan detta installationskommando behöva åtkomst till nätverk eller index:

```text illustrative
python -m pip install -r chapter-27-python-typing/requirements-dev.lock
```

Installation är en separat förberedelseåtgärd. Verifieraren utför den aldrig,
kontaktar aldrig ett index och behandlar aldrig ett globalt eller annorlunda
versionssatt kontrollverktyg som likvärdigt. Skapa inte `.venv` i detta kapitel.

### A2. Jämför positiva, negativa och rättade konsumenter

Den positiva konsumenten kontrollerar typade rader, generisk returinferens, en
strukturell priskälla och `Self`:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_positive.py check=learning:contract -->
```python source-ref
prices: PriceSource = Catalogue()
assert_type(prices.unit_price(row["sku"]), float | None)

inventory = LabelledInventory()
assert_type(inventory.add(row), LabelledInventory)
```

Den negativa konsumenten är avsiktligt ogiltig. Läs den före körning och
förutsäg en kategori per misstag:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_negative.py check=learning:contract -->
```python source-ref
bad_row: InventoryRow = {"sku": "PART-7", "quantity": "many"}
Inventory().add("not an inventory row")


class BrokenPrices:
    def unit_price(self, sku: int) -> str:
        return str(sku)


prices: PriceSource = BrokenPrices()
```

De stabila acceptanskategorierna är:

- `[typeddict-item]` för fel värde i ett deklarerat `TypedDict`-fält;
- `[arg-type]` för det inkompatibla argumentet till `Inventory.add`; och
- `[assignment]` för att tilldela en klass med inkompatibel metod till
  `PriceSource`.

Fullständig formulering, källprefix, noter, färger och markörformatering är inte
gyllene utdata. Verifieraren kräver ett nollskilt resultat och alla tre
kategoritokens.

Den rättade konsumenten reparerar kontrakten i stället för att dölja dem:

<!-- bookcheck: path=chapter-27-python-typing/examples/checker_corrected.py check=learning:contract -->
```python source-ref
row: InventoryRow = {"sku": "PART-7", "quantity": 3}
inventory = Inventory().add(row)
assert_type(inventory, Inventory)


class FixedPrices:
    def unit_price(self, sku: str) -> float | None:
        return 1.25 if sku == "PART-7" else None
```

Vanligt misstag: att lägga till obegränsad `Any`, en vanlig `# type: ignore`
eller en `cast` som inte ändrar något körtidsbeteende. Rätta först värdet,
signaturen eller gränsen. När en verklig extern begränsning kräver en nödutgång,
begränsa den till det minsta uttrycket, använd en kodspecifik ignore där det
stöds och dokumentera varför körtidsevidens täcker luckan.

**Ändra — O6 TODO:** kopiera ett negativt fall till en kasserbar arbetsfil,
förutsäg dess kategori, rätta det underliggande kontraktet och kör samma
kontrollkonfiguration igen. **Ledtråd:** redigera inte den kanoniska negativa
fixturen; verifieraren behöver den som evidens för förväntat fel. **Lösning:**
den rättade fixturen demonstrerar alla tre reparationer medan körtidssviten
bevisar att den typade kärnan fortfarande fungerar.

### A3. Kör den begränsade verifieraren

Körtidsverifiering väljs alltid uttryckligen från rotkatalogen:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Kontrollverifiering är ett separat val:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

Verifieraren:

1. tar en ögonblicksbild av kapitlets källor och avvisar befintliga cachefiler
   eller bytekod;
2. kopierar endast den medföljande koden, testerna och de tre konsumenterna till
   en tillfällig rot;
3. använder den aktuella tolken med `-I -B`, ingen standardindata, en minimal
   miljö, en tidsgräns på 20 sekunder, en gräns på 64 KiB för kombinerad utdata
   och städning av processgruppen;
4. kör körtidstester eller kontrollerar den exakta versionen `mypy==2.2.0`;
5. kräver i kontrolläge att positiv är ren, negativ är nollskild med alla tre
   stabila kategorier och rättad är ren; och
6. tar bort den tillfälliga roten, jämför kapitlets ögonblicksbild, söker efter
   rester och rapporterar städningen separat.

Slutkod `0` betyder att det valda kontraktet och städningen godkändes. Kod `1`
betyder att ett valt beteende, en gräns, källintegritet eller städningskontroll
misslyckades. Kod `2` betyder felaktig kommandoanvändning eller att den exakta
förkunskapen för kontrollverktyget saknas. Saknad kontrollevidens måste förbli
**saknad förkunskap**; den får inte framställas som godkänd.

Verifieraren begränsar olyckor från betrodda lektionskällor; den är inte en
sandlåda för fientlig kod. Den bevisar bara den valda tolkens eller verktygets
körning. Den bevisar inte alla plattformar, alla Python-versioner, en
översättnings naturlighet, undervisningseffekt, tillgänglighet,
paketkompatibilitet eller produktionssäkerhet.

### Avancerad kontrollpunkt och bedömningsmatris

Ge 0 eller 1 poäng för varje punkt:

1. Det exakt installerade kontrollverktygets version matchar den direkta
   versionen.
2. Positiva och rättade konsumenter är rena under samma strikta alternativ.
3. Den negativa konsumenten avslutas nollskilt för alla tre stabila kategorier.
4. Körtidstesterna godkänns fortfarande efter rättningen.
5. Ingen bred `Any`, okvalificerad ignore eller evidensspecifik `cast` döljer
   en defekt.
6. Städningen godkänns och ingen kontrollcache uppstår i arkivet.

Slutförande kräver alla sex poäng. Om den exakta versionen saknas, låt denna väg
vara oavslutad och behåll den professionella kontrollpunkten. Reflektion: vad
hittade kontrollverktyget före körning och vilket viktigt körtidsfaktum kunde
det fortfarande inte bevisa?

### Gemensam slutregel för slutförande mellan vägar

Det inskickade typade lagertillägget är slutfört först när det får 1 poäng i
varje obligatorisk kategori: **körtidskorrekthet**, **annotations- och statiskt
kontrakt**, **gränsåterhämtning**, **läsbarhet** och **förklaring**. Grundvägens
och den professionella vägens bedömningsmatriser prövar dessa fem kategorier på
respektive djup. Den valfria avancerade kontrollvägen lägger till statisk
verktygsevidens, men professionellt eller avancerat djup kan inte kompensera för
0 i någon grundkategori. Ett otillgängligt kontrollverktyg ogiltigförklarar
aldrig en slutförd körtidsväg och räknas aldrig som godkänd evidens.

## Vanliga misstag och lugn återhämtning

- **”Annoterad betyder validerad.”** Gå tillbaka till E3, identifiera
  operationen som faktiskt kördes och placera uttrycklig validering vid den
  inkommande gränsen.
- **Använda `if not value` för `T | None`.** Gå tillbaka till fallet `0` och
  smalna av med `is None` när frågan gäller frånvaro.
- **Annotera varje värde med den bredaste typen.** Börja med det verkliga
  accepterade kontraktet; bredda endast när beteendet verkligen accepterar mer.
- **Använda `TypedDict` som körtidsparser.** Behåll `parse_row` vid den opålitliga
  gränsen och returnera den typade formen först efter validering.
- **Tvinga protokollarv.** Matcha den publika metodformen; arv är ett separat
  designval.
- **Tysta diagnostik.** Rätta den minsta skillnaden och kör sedan dess
  körtidsgranne och statiska kontroll igen från en ren tillfällig rot.
- **Kalla en direkt version för en universell låsfil.** Dokumentera verktyg,
  version, värd, Python-mål, hämtningsantaganden och faktisk körning. Dra inte
  slutsatsen att en transitiv eller plattformsöverskridande upplösning finns.

## Verifiering för underhållare och evidensgräns

Alla utdrag ur den medföljande koden i detta kapitel använder den registrerade
källreferenskontrollen `learning:contract`. Det ägande tillägget kan välja det
kontraktet; den generiska bokvalideringen kontrollerar Markdown och deklarerad
referensform utan att tyst köra godtyckliga medföljande filer.

Kör först den smala körtidsevidensen:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --runtime
```

Kör kontrollevidens endast när `mypy==2.2.0` redan finns i den valda tolken:

```text illustrative
python -B chapter-27-python-typing/tools/verify.py --checker
```

Installera inte ett kontrollverktyg som ett dolt valideringssteg. Dokumentera
körtids- och kontrollresultat oberoende. Ett godkänt kontrollverktyg ersätter
inte körtidstester; godkänd struktur godkänner inte språkflyt, pedagogik,
tillgänglighet, dubbelriktad rendering, proveniens eller publicering.

## Avslutande reflektion och nästa steg

Bra typning gör en verklig gräns lättare att förstå. Den gör inte Python mindre
dynamiskt och tar inte bort behovet av att validera externa värden. Använd den
minsta annotation som förtydligar en relation och bevisa sedan
körtidsbeteendet vid gränsen där misstag spelar roll.

Fortsätt oberoende till [Kapitel 24: Python och C++](../chapter-24-python-cpp-integration/README.sv.md)
eller [Kapitel 25: Python och Rust](../chapter-25-python-rust-integration/README.sv.md)
för gränssnitt till inbyggda paket. Fortsätt till
[Kapitel 28: Professionellt slutprojekt](../chapter-28-professional-capstone/README.sv.md)
för ett projekt som kombinerar domänmodellering, persistens, CLI, tester,
loggning och artefaktverifiering.
