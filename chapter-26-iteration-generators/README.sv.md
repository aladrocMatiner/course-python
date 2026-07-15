# Kapitel 26 · Iteration, iteratorer och generatorer

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Det här ska vi bygga

Många program tar emot en följd av värden och omvandlar den: namn blir etiketter,
mätvärden blir sammanfattningar och grupper blir en enda ström. Du kan redan
göra det med en `for`-loop. Kapitlet behåller den tillförlitliga mentala modellen
och lägger till tre verktyg i en avsiktlig ordning:

1. **Comprehensions, `enumerate` och `zip`** för små, läsbara omvandlingar av
   samlingar.
2. **Iteratorer** för att förstå var iterationens tillstånd finns och varför en
   dataström kan ta slut.
3. **Generatorer** för att skapa värden på begäran samtidigt som konsumenten har
   en tydlig gräns.

Det växande projektet är en iterationspipeline för en liten syntetisk resultattavla
från en workshop. Den körbara auktoriteten är
[`examples/iteration_pipeline.py`](examples/iteration_pipeline.py), med tester ur
standardbiblioteket som belägg. Den använder varken nätverk, autentiseringsuppgifter,
personuppgifter, filer, trådar eller tredjepartspaket.

## Lärandemål

När du har slutfört den väg du väljer kan du:

- **O1 — Omvandla tydligt:** härleda en list-, dictionary- eller set-comprehension
  från en vanlig loop och välja den tydligare formen.
- **O2 — Numrera och para säkert:** använda `enumerate` för visningspositioner och
  medvetet välja mellan avkortande `zip` och `zip(..., strict=True)`.
- **O3 — Förklara iteratortillstånd:** skilja en itererbar från en iterator,
  använda `iter` och `next`, observera när iteratorn tar slut och skapa en ny
  genomgång när källan tillåter det.
- **O4 — Skydda genomgången:** använda ett entydigt standardvärde när iteratorn
  är slut och undvika strukturell ändring av samlingen som just gås igenom.
- **O5 — Bygga begränsat arbete vid behov:** förklara generatoruttryck, `yield`,
  engångskonsumtion, `yield from` och en uttrycklig ändlig gräns.
- **O6 — Återhämta och städa:** hitta ett fördröjt fel vid konsumtionssteget,
  avsluta en generator med `return` och köra deterministisk städning efter en
  tidig stängning.

[Spårbarhetsregistret](TRACEABILITY.md) kopplar varje mål till undervisning,
övning, återhämtning, lösning, kontrollpunkt, companion-källa och tester.

## Förkunskaper och vägkarta

Den obligatoriska startpunkten är grundkontrollpunkten i
[kapitel 11: Funktioner](../chapter-11-functions/README.sv.md). Du ska redan vara
bekväm med listor, dictionaries, sets, villkor, `for`-/`while`-loopar och små
funktioner. Kapitelnumret betyder **inte** att nätverk, C++ eller Rust krävs.

- **Grundväg · 2 pass på 45–60 minuter.** Läs E1–E3, slutför grundutmaningen och
  använd dess bedömningsmatris. Resultat: skapa en numrerad resultattavla från
  två små samlingar och avvisa data som inte passar ihop. Slutförande: minst 4/5
  poäng, inklusive strikt parning. Trygg fortsättning: stanna här och fortsätt
  till [kapitel 12: Klasser och objekt](../chapter-12-oop/README.sv.md).
- **Professionell väg · 1–2 pass på 45–60 minuter.** Slutför först
  grundkontrollpunkten, därefter P1–P3 och den professionella utmaningen.
  Resultat: konsumera, diagnostisera och medvetet återskapa en genomgång för
  engångsbruk. Slutförande: minst 4/5 poäng, inklusive återhämtning efter att
  iteratorn tagit slut. Trygg stoppunkt: använd itererbara objekt säkert utan att
  skriva generatorer.
- **Frivillig avancerad väg · 2 pass på 60–75 minuter.** Slutför den professionella
  vägen och repetera [kapitel 14: Undantag](../chapter-14-exceptions/README.sv.md)
  före städningsavsnittet. Resultat: implementera och förklara en ändlig lazy
  pipeline, ett fördröjt fel, delegering och tidig städning. Slutförande: minst
  5/6 poäng, inklusive gränser och städning. Vägen är fortfarande frivillig för
  kursens grundläggande progression.

Återvänder du med tidigare erfarenhet? Förutsäg resultatet av
`list(zip(["A", "B"], [1], strict=True))`. Om du kan förklara varför felet
uppstår först när zip-objektet konsumeras kan du börja på den professionella
vägen. Om du också kan förklara varför ett anrop till en generatorfunktion inte
kör dess kropp kan du börja på den avancerade vägen och använda kontrollpunkterna
för att bekräfta eventuella luckor.

## En liten ordlista

- **Itererbar:** ett objekt som kan ge en iterator. Listor, tuples, dictionaries,
  sets och strängar är välbekanta exempel.
- **Iterator:** ett objekt med tillstånd som ger ett nästa värde i taget. Det
  minns hur långt genomgången har kommit.
- **Slut:** tillståndet när en iterator inte har något nästa värde. Ett direkt
  `next` höjer då `StopIteration` om inget standardvärde gavs.
- **Comprehension:** kompakt syntax som bygger en konkret samling från en
  itererbar.
- **Generator:** en iterator som skapas av ett generatoruttryck eller en funktion
  som innehåller `yield`.
- **Lazy:** arbete utförs när värden efterfrågas. Lazy betyder inte automatiskt
  ändligt, snabbt eller säkert.
- **Konsument:** loopen, `next`, `list` eller en annan operation som begär värden
  från en iterator.

Den observerbara följden är alltid densamma: hämta en iterator, begär ett värde,
ta emot ett värde eller ett slut och stanna eller begär igen. Den här följden i
text motsvarar varje tillståndsdiagram du kan rita för en iterator; ingen
betydelse beror på pilarnas riktning eller färg.

## Grundväg: läsbara omvandlingar

### E1. Härled en comprehension från en loop

Mål: bygg en liten samling utan att förlora den vanliga loopens mentala modell.

Anta att en workshop registrerar tre syntetiska poäng. Förutsäg värdet på
`doubled` efter varje loopvarv innan du kör exemplet.

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

Läs loopen i denna ordning: ta ett `score`, beräkna `score * 2`, lägg till
resultatet och upprepa. En list comprehension uttrycker samma omvandling med
resultatuttrycket först:

```python runnable
scores = [3, 5, 8]
doubled = [score * 2 for score in scores]
print(doubled)
```

```text output
[6, 10, 16]
```

Hakparenteserna betyder ”bygg en lista”. Inuti dem är:

1. `score * 2` värdet som ska lagras;
2. `score` det aktuella målnamnet; och
3. `scores` den itererbara som ger värden.

Ett enda villkor kan filtrera värden, men det står efter den itererbara. Förutsäg
vilka poäng som överlever innan du kör:

```python runnable
scores = [3, 5, 8]
large_doubles = [score * 2 for score in scores if score >= 5]
print(large_doubles)
```

```text output
[10, 16]
```

Dictionary- och set-comprehensions använder samma läsordning. En dictionary
lagrar nyckel/värde-par; ett set tar bort likadana dubbletter. Vi sorterar bara
setet för en stabil visning—iterationsordningen för ett set är inget
korrekthetskontrakt.

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

Tom indata är ett lugnt och användbart gränsfall: ingen kropp körs, så varje
comprehension skapar en tom samling av sin egen sort.

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

**Ändra — TODO O1:** skriv om loopen som en läsbar list comprehension. Behåll
exakt en omvandling och ett villkor.

```python todo
scores = [2, 4, 7, 9]
selected = []
for score in scores:
    if score >= 5:
        selected.append(score + 1)

# TODO: replace the loop with selected = [...]
print(selected)
```

**Ledtråd:** läs den ursprungliga kroppen i ordning: lagra `score + 1`, ta varje
`score` från `scores` och behåll det när `score >= 5`.

**Förklarad lösning:** resultatuttrycket kommer först, därefter samma loop och
samma villkor. Normalresultatet är `[8, 10]`; ett tomt `scores` ger fortfarande
`[]`.

```python runnable
scores = [2, 4, 7, 9]
selected = [score + 1 for score in scores if score >= 5]
print(selected)
```

```text output
[8, 10]
```

Vanligt misstag: flera nästlade loopar, villkor, sidoeffekter och tilldelningar
pressas in i ett uttryck. En comprehension är värdefull när den är lättare att
läsa. Behåll den vanliga loopen när den berättar händelseförloppet lugnare.

### E2. Numrera positioner utan en manuell räknare

Mål: lägg till människovänliga positioner utan att uppdatera en separat variabel.

`enumerate` ger paren `(position, value)`. `start=1` är användbart för etiketter
som en person ser; det ändrar inte samlingens nollbaserade indexering. Förutsäg
de två utskrivna raderna:

```python runnable
names = ["Noor", "Frej"]

for position, name in enumerate(names, start=1):
    print(f"{position}: {name}")
```

```text output
1: Noor
2: Frej
```

Gränsfallet är en tom itererbar: loopkroppen körs noll gånger och skriver inget.
Ingen särskild position behöver uppfinnas.

**Ändra — TODO O2:** ändra det första visade numret till `10` och förutsäg de
två etiketterna före körning.

```python todo
names = ["Noor", "Frej"]
# TODO: enumerate names starting at 10 and print "position: name"
```

**Ledtråd:** ändra bara argumentet `start`; lägg inte till och öka en separat
räknare.

**Förklarad lösning:** `enumerate(names, start=10)` ger `(10, "Noor")` och
`(11, "Frej")`. Själva listan ändras inte.

```python runnable
names = ["Noor", "Frej"]
print(list(enumerate(names, start=10)))
```

```text output
[(10, 'Noor'), (11, 'Frej')]
```

### E3. Para data utan tyst förlust

Mål: gör längdkontraktet synligt när två datakällor hör ihop.

Vanlig `zip` stannar när den kortare indatan tar slut. Det kan vara avsiktligt,
men kan också dölja en saknad poäng:

```python runnable
names = ["Noor", "Frej"]
scores = [7]
print(list(zip(names, scores)))
```

```text output
[('Noor', 7)]
```

`"Frej"` försvinner eftersom den itererbara med poäng saknar ett andra värde.
När lika längder ingår i korrektheten begär du kontraktet uttryckligen med
`strict=True`. Companion-funktionen konsumerar zip-objektet till en lista, så en
skillnad kan inte förbli dold i ett okonsumerat zip-objekt.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def strict_pairs(left, right):
    """Return pairs, rejecting unequal input lengths."""
    return list(zip(left, right, strict=True))
```

I det lyckade fallet verifierar testerna
`strict_pairs(["Noor", "Frej"], [7, 9]) == [("Noor", 7), ("Frej", 9)]`.
Två tomma indata ger korrekt `[]`.

Förutsäg när nästa exempel misslyckas: när `zip` skapas eller när `list` begär
värden från det?

<!-- bookcheck: expect-error="ValueError" -->
```python expected-error
names = ["Noor", "Frej"]
scores = [7]
pairs = zip(names, scores, strict=True)
print(list(pairs))
```

Den stabila signalen är `ValueError`. Konstruktionen skapar bara iteratorn;
konsumtionen upptäcker att höger indata tog slut först. Hela traceback-texten
kan skilja sig mellan underhållsversioner av Python.

**Återhämtning:** lägg till den saknade poängen och kör samma strikta kontrakt
igen.

```python runnable
names = ["Noor", "Frej"]
scores = [7, 9]
print(list(zip(names, scores, strict=True)))
```

```text output
[('Noor', 7), ('Frej', 9)]
```

Att ta bort `strict=True` är också en giltig design när det uttryckligen är
acceptabelt att ignorera avslutande värden. Skriv beslutet i domänkontraktet;
gör inte tyst avkortning till en oavsiktlig reparation.

### Guidad grundutmaning

Bygg en numrerad resultattavla. Förutsäg först de två utdataraderna och felet för
en saknad poäng.

```python todo
names = ["Noor", "Frej"]
scores = [7, 9]

# TODO 1: pair names and scores with strict=True.
# TODO 2: enumerate the pairs starting at 1.
# TODO 3: build lines like "1. Noor: 7" with a list comprehension.
# TODO 4: print each line.
```

**Ledtråd:** skapa `pairs` först. Därefter kan comprehension-uttrycket packa upp
`position, (name, score)` från `enumerate(pairs, start=1)`.

**Förklarad lösning:** strikt parning skyddar datas linjering, numreringen skapar
visningspositioner och comprehension-uttrycket formaterar en rad per par. Varje
steg har ett ansvar.

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

Med `names = []` och `scores = []` är `pairs` och `lines` tomma och inget skrivs
ut. För olika längder är `ValueError` den förväntade diagnostiken; reparera datan
i stället för att dölja skillnaden.

### Grundkontrollpunkt och bedömningsmatris

Slutför resultattavlan för normala, tomma och olika långa indata. Förklara varför
normalutdatan är ordnad, varför det tomma resultatet är giltigt och varför
skillnaden misslyckas under konsumtion.

Ge en poäng för varje kriterium:

- **Korrekthet:** normal indata ger exakt de två numrerade raderna.
- **Gräns:** två tomma indata ger ett tomt resultat utan en påhittad rad.
- **Återhämtning:** olika långa indata höjer `ValueError` och rättad indata lyckas.
- **Läsbarhet:** varje comprehension har en tydlig omvandling och högst ett
  enkelt villkor.
- **Förklaring:** du skiljer mellan visningspositioner, samlingsindex och det
  strikta parningskontraktet.

4/5, inklusive **Återhämtning**, slutför grundvägen. Du kan stanna tryggt och
fortsätta till kapitel 12. Reflektion: var i ett program du känner till skulle
tyst avkortning vara farlig?

## Professionell väg: iteratortillstånd du kan förklara

### P1. Itererbar och iterator är olika roller

Mål: hitta traverseringstillståndet i stället för att föreställa dig att en
`for`-loop magiskt minns en position.

En lista är **itererbar**: den kan tillhandahålla en iterator. `iter(values)`
ber om en. Iteratorn som returneras lagrar traverseringens förlopp.
`next(cursor)` ber just den iteratorn om ett värde.

Förutsäg varje rad innan du kör:

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

Sekvensen med ord är:

1. `values` kan skapa traverseringar.
2. `cursor` börjar före det första värdet.
3. den första `next` går framåt och returnerar `"A"`;
4. den andra går framåt och returnerar `"B"`; och
5. den tredje upptäcker att iteratorn är uttömd och returnerar det angivna
   standardvärdet.

`iter(cursor) is cursor` är `True` eftersom en iterator är sin egen iterator.
Separata anrop till `iter(values)` skapar däremot separata traverseringar med
eget tillstånd.

Den medföljande nedräkningen är också en iterator, men en engångsgenerator i
stället för en återanvändbar samling:

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

Testerna verifierar att `list(countdown(3))` är `[3, 2, 1]` och att
`list(countdown(0))` är den tomma gränsen `[]`. Negativa, booleska,
icke-heltals- och för stora gränser avvisas när konsumtionen börjar.

**Ändra — O3 TODO:** Skapa två iteratorer från samma lista. Konsumera två
värden från den första och ett från den andra. Förutsäg de tre resultaten.

```python todo
values = ["A", "B"]
first = iter(values)
second = iter(values)
# TODO: call next twice on first and once on second, then print each result.
```

**Ledtråd:** iteratortillståndet tillhör `first` eller `second`, inte `values`.

**Förklarad lösning:** observationerna är `A`, `B` och sedan `A`. Den andra
iteratorn börjar en egen traversering.

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

### P2. Uttömning, standardvärden och återhämtning

Mål: känna igen uttömning som en normal protokollhändelse och välja en
uttrycklig återhämtning.

Ett direkt `next` utan standardvärde höjer `StopIteration` efter det sista
värdet:

<!-- bookcheck: expect-error="StopIteration" -->
```python expected-error
cursor = iter(["A"])
print(next(cursor))
print(next(cursor))
```

Det första anropet skriver ut `A`; det andra når den avsedda stabila signalen
`StopIteration`. En `for`-loop hanterar signalen internt och avslutas normalt.
Fånga inte alla undantag brett bara för att fortsätta begära värden.

Det finns två vanliga återhämtningar:

1. Om källan är återanvändbar, be den om en **ny iterator**.
2. Om uttömning väntas i ett stegvis API, skicka ett avsiktligt standardvärde
   till `next`.

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

Ett standardvärde som är en sträng blir tvetydigt om strömmen legitimt kan
innehålla samma sträng. Ett privat sentinelobjekt gör frånvaro urskiljbar med
identitet:

```python runnable
missing = object()
value = next(iter([]), missing)
print(value is missing)
```

```text output
True
```

**Ändra — O4 TODO:** Med `values = [0]`, använd en privat sentinel för att
skilja det verkliga värdet `0` från uttömning. Observera båda förfrågningarna.

```python todo
values = [0]
missing = object()
cursor = iter(values)
# TODO: request twice with missing as the default and compare each result by identity.
```

**Ledtråd:** `0` är falskliknande men finns. Testa frånvaro med `is missing`,
inte med `if not value`.

**Förklarad lösning:** det första resultatet är `0` och `first is missing` är
`False`; det andra resultatet är sentineln och `second is missing` är `True`.

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

### P3. Håll källmutation åtskild

Mål: undvika att ändra strukturen som styr traverseringen, om inte ett särskilt
samlingskontrakt har lärts ut och testats.

Om du tar bort eller infogar element i samma lista som traverseras kan värden
hoppas över, eftersom positionerna flyttas medan iteratorn går framåt. Bygg ett
separat resultat i stället:

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

Originalet finns kvar för diagnostik och resultatet har ett tydligt kontrakt.
En comprehension är också tydlig här:
`[label for label in raw_labels if label]`.

Vanligt misstag: att se ett lyckat mutationsexempel och anta att alla samlingar
garanterar det. De delar inte ett enda kontrakt för mutation under iteration.
Föredra en ögonblicksbild eller ett separat resultat om inte det exakta
beteendet både behövs och är verifierat.

### Professionell guidad utmaning

Spåra en kö med syntetiska steg utan att ändra den. Konsumera `"draft"`, sedan
`"review"`, observera uttömning med en privat sentinel och återhämta dig genom
att skapa en ny traversering som åter returnerar `"draft"`.

```python todo
stages = ["draft", "review"]
missing = object()
cursor = iter(stages)
# TODO 1: consume and print both stages.
# TODO 2: request once more with missing as the default and prove identity.
# TODO 3: create a fresh iterator and print its first value.
```

**Ledtråd:** tilldela inte `fresh = cursor`; då får du samma uttömda objekt.
Anropa `iter(stages)` igen.

**Förklarad lösning:** traverseringstillståndet är isolerat i varje iterator.
Originallistan är återanvändbar; `cursor` återställs inte genom att ett annat
namn tilldelas.

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

### Professionell kontrollpunkt och bedömningsmatris

Slutför den guidade spårningen och nedräkningens kantfallstester. Förklara
itererbar, iterator, aktuellt tillstånd, uttömning, standardvärde och återskapande
med egna ord.

Ge en poäng för varje kriterium:

- **Identitet:** du skiljer en återanvändbar lista från varje iterator den skapar.
- **Tillstånd:** din förutsägelse följer varje iterator oberoende.
- **Gräns:** en tom iterator använder en entydig sentinel.
- **Återhämtning:** en ny traversering skapas från den återanvändbara källan.
- **Säkerhet och förklaring:** källan muteras inte strukturellt, och du kan
  förklara varför ett annat namn inte spolar tillbaka en iterator.

4/5, inklusive **Återhämtning**, slutför den professionella vägen. Reflektion:
vilka API:er du använder returnerar återanvändbara samlingar och vilka kan
returnera engångsiteratorer?

## Valfri avancerad väg: begränsade lata pipelines

Repetera kapitel 14 före A6 och A7: de avsnitten använder `try`, `finally` och
undantagskategorier. Allt nedan är fortfarande valfritt för grundkursens
framsteg.

### A1. Generatoruttryck skjuter upp arbetet

Mål: skilja en materialiserad samling från en iterator som arbetar vid behov.

Hakparenteser bygger alla listvärden direkt. Parenteser runt samma
comprehension-syntax skapar ett generatoruttryck:

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

Den första `next` konsumerar `1`; `list(lazy)` får bara de återstående
värdena. Generatorn är för engångsbruk. Lathet ändrar **när** värden begärs;
den lovar inte att arbetet går snabbt eller att en obegränsad konsument är säker.

**Ändra — O5 TODO:** Förutsäg resultatet av två anrop till `next(lazy)` följda
av `list(lazy)` för fyra indatavärden. Kör sedan en ändlig version.

**Ledtråd:** stryk ett källvärde varje gång konsumenten begär ett.

### A2. Generatorfunktioner pausar vid `yield`

En funktion som innehåller `yield` skapar en generator. När funktionen anropas
skapas generatorobjektet, men dess kropp körs ännu inte. Varje förfrågan
återupptar körningen fram till nästa `yield`, normala `return` eller fel.

Den testade `countdown`-källan visades i P1. För `countdown(3)` ger tre
förfrågningar `3`, `2` och `1`; nästa förfrågan observerar uttömning. Dess
validering börjar också vid konsumtion, så `countdown(-1)` kan konstrueras men
misslyckas med `ValueError` när den först konsumeras.

**Ändra — O5 TODO:** Förutsäg `list(countdown(0))` och
`list(countdown(2))` innan du tittar på testresultaten.

**Förklarad lösning:** noll ligger inom den giltiga gränsen men loopkroppen
körs aldrig, så resultatet är `[]`. Två ger `[2, 1]` och returnerar sedan
normalt.

### A3. Begränsa en annars oändlig källa

`itertools.count()` kan fortsätta producera heltal. Den medföljande koden
placerar en uttrycklig, validerad gräns framför den och begränsar den begärda
gränsen till `MAX_SQUARES = 10_000`. Detta är ett skyddsräcke för undervisning,
inte en universell domänkonstant.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def bounded_squares(limit):
    """Yield the first ``limit`` squares from an otherwise infinite source."""
    _require_bounded_integer(limit, name="limit", maximum=MAX_SQUARES)
    squares = (number * number for number in count())
    yield from islice(squares, limit)
```

Testerna konsumerar exakt fem värden och observerar `[0, 1, 4, 9, 16]`. En
nollgräns ger ingenting. Ett negativt, booleskt, icke-heltal eller för stort
värde avvisas vid det första konsumtionssteget.

Materialisera inte en oändlig källa utan en begränsare. Även en lat producent
blir obegränsad om konsumenten fortsätter begära för evigt eller lagrar varje
resultat. Begränsa antal element, tid, indata och ägda resurser vid rätt gräns.

**Ändra — O5 TODO:** Ändra en ändlig `islice`-gräns från 5 till 7 och förutsäg
de två sista kvadraterna. Testa sedan `limit = 0`.

**Ledtråd:** källan börjar vid noll; kvadrera index 5 och 6 för den nya svansen.

**Förklarad lösning:** sju värden är
`[0, 1, 4, 9, 16, 25, 36]`; noll värden ger `[]`. Begränsaren, inte
generatoruttrycket ensamt, ger terminering.

### A4. Delegera med `yield from`

Mål: vidarebefordra värden från en ändlig underliggande itererbar utan en
manuell nästlad `yield`-loop.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def flatten(groups):
    """Yield every value from each finite group in order."""
    for group in groups:
        yield from group
```

För `[["A", "B"], [], ["C"]]` är det verifierade resultatet
`["A", "B", "C"]`. Den tomma inre gruppen bidrar inte med något värde och
behöver inget specialfall.

**Ändra — O5 TODO:** Lägg till tomma grupper i början och slutet. Förutsäg samma
resultat innan du kör.

**Ledtråd:** `yield from []` avslutas helt enkelt direkt.

### A5. Fördröjt fel är fortfarande fel

Mål: koppla en diagnostik till konsumtionssteget som nådde ogiltiga data.

<!-- bookcheck: path="chapter-26-iteration-generators/examples/iteration_pipeline.py" check="learning:contract" -->
```python source-ref
def reciprocals(values):
    """Yield reciprocals; an invalid later value fails when it is consumed."""
    for value in values:
        yield 1 / value
```

Att konstruera `reciprocals([2, 0, 4])` lyckas eftersom ingen division ännu
har skett. Den första `next` ger `0.5`; den andra når noll och höjer den stabila
kategorin `ZeroDivisionError`. Det efterföljande värdet `4` konsumeras aldrig
från den misslyckade generatorn.

**Återhämtning — O6 TODO:** Rätta den ogiltiga indatan och skapa en ny
generator. Anta inte att det misslyckade objektet kan spolas tillbaka.

**Ledtråd:** den testade återhämtningsindatan är `[2, 4]`.

**Förklarad lösning:** en ny `reciprocals([2, 4])` producerar `[0.5, 0.25]`.
Rättningen ändrar det ogiltiga domänvärdet och startar om traverseringen från ett
känt tillstånd.

### A6. Deterministisk städning efter tidig stängning

Mål: frigöra en ägd lokal resurs när en startad generator slutförs, misslyckas
eller stängs uttryckligen.

Den medföljande koden tar emot ett falskt `close`-callback så att testet kan
observera städning utan att öppna en verklig fil eller nätverksanslutning:

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

Städningstestet startar generatorn, konsumerar `"A"`, anropar
`cursor.close()` och observerar `events == ["closed"]`. Att anropa `close`
igen lägger inte till en andra händelse. Normal fullständig uttömning kör också
städningen en gång. Ett icke-anropbart städningsvärde höjer `TypeError` när
konsumtionen börjar.

Viktigt kantfall: att stänga en generator som aldrig har startat går inte in i
dess kropp, så den kan inte förlita sig på kroppen för att först hämta och sedan
frigöra en resurs. Hämta en resurs endast inom den aktiva livstid du styr, och
stäng en startad generator uttryckligen när konsumenten slutar tidigt. Förlita
dig inte på tidpunkten för skräpinsamling.

**Ändra — O6 TODO:** Använd `events = []`, starta en `managed_values` med två
värden, konsumera ett värde, stäng den och kontrollera den enda
städningshändelsen.

**Ledtråd:** inspektera `events` före och efter `cursor.close()`.

### A7. Avsluta med `return`, inte `StopIteration`

En generator avslutas normalt när körningen når slutet eller exekverar
`return`. Om `StopIteration` uttryckligen höjs i kroppen översätts det till den
stabila kategorin `RuntimeError` på den deklarerade Python-körtiden. Förutsäg
den slutliga undantagskategorin:

<!-- bookcheck: expect-error="RuntimeError" -->
```python expected-error
def broken_generator():
    yield "ready"
    raise StopIteration("finished")

cursor = broken_generator()
print(next(cursor))
print(next(cursor))
```

Den första förfrågan skriver ut `ready`; den andra når den felaktiga
uttryckliga höjningen och misslyckas med `RuntimeError`. Fullständig
traceback-prosa ingår inte i kontraktet.

**Återhämtning:** ersätt den uttryckliga höjningen med `return`.

```python runnable
def finished_generator():
    yield "ready"
    return

print(list(finished_generator()))
```

```text output
['ready']
```

### Avancerad guidad utmaning

Bygg en ändlig rapport med enbart standardbiblioteksverktyg:

```python todo
from itertools import count, islice

limit = 4
# TODO 1: create a generator expression of squares from count().
# TODO 2: bound it with islice(..., limit).
# TODO 3: materialize only those four values and print them.
# TODO 4: repeat with limit = 0.
```

**Ledtråd:** konsumenten ska ta emot `islice(squares, limit)`, aldrig den
obegränsade källan direkt.

**Förklarad lösning:** skapa det lata kvadratuttrycket, placera `islice` mellan
det och `list` och materialisera sedan den ändliga vyn.

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

Nollgränsen returnerar `[]`. En negativ eller enorm gräns som eleven väljer
behöver validering innan den når denna konstruktion; den medföljande
`bounded_squares` äger det kontrollerade kontraktet.

### Avancerad kontrollpunkt och bedömningsmatris

Slutför den begränsade rapporten, återhämtningen från fördröjt fel och
städningens TODO. Förklara sedan när varje generator börjar arbeta och hur den
terminerar.

Ge en poäng för varje kriterium:

- **Lathet:** du skiljer konstruktion från det första konsumtionssteget.
- **Gränser:** varje annars oändlig källa har en uttrycklig, validerad och ändlig
  konsumentgräns.
- **Engångstillstånd:** en förbrukad eller misslyckad generator återskapas
  avsiktligt.
- **Återhämtning:** ogiltig indata rättas och den reparerade grannen lyckas.
- **Delegering:** `yield from` bevarar ordningen i ändliga grupper, inklusive
  tomma grupper.
- **Städning och förklaring:** en startad generator stänger sin falska resurs
  exakt en gång, och du förklarar varför `return` är normal terminering.

5/6, inklusive **Gränser** och **Städning och förklaring**, slutför den valfria
avancerade vägen. Reflektion: vilken gräns tillhör producenten, vilken tillhör
konsumenten och vem äger städningen i din pipeline?

## Vanliga misstag och lugna återhämtningar

- **Täta comprehensions:** om du behöver avkoda raden två gånger, återgå till
  en namngiven loop eller dela upp mellanliggande värden.
- **Beroende av mängdordning:** jämför medlemskap i mängden eller sortera bara
  för stabil visning; lova inte en godtycklig renderad ordning.
- **Vanlig `zip` när längder måste stämma:** välj `strict=True`, konsumera
  resultatet, rätta källskillnaden och kör igen.
- **Anta att `zip` validerar vid konstruktion:** den upptäcker uttömning i
  indata när konsumenten går framåt.
- **Anropa `next` för evigt:** hantera uttömning med en `for`-loop, ett
  avsiktligt standardvärde eller en ny iterator från en återanvändbar källa.
- **Behandla en generator som återspolningsbar:** återskapa den från den
  ursprungliga indatan.
- **Mutera samlingen som traverseras:** bygg ett separat resultat eller en
  uttrycklig ögonblicksbild.
- **Kalla en pipeline ”säker eftersom den är lat”:** lägg till en gräns för
  element, tid eller indata och deterministisk resursstädning.
- **Vänta sig validering vid generatorkonstruktion:** kom ihåg att en
  generatorkropp börjar vid konsumtion; testa den första förfrågan.
- **Höja `StopIteration` inuti en generator:** använd `return` för normalt slut.

Fel i det här kapitlet är observationer, inte personliga misslyckanden. Minska
exemplet till en producent, en konsument och ett förväntat nästa värde; reparera
sedan det minsta kontraktet och kör dess lyckade granne igen.

## Verifiera det körbara kontraktet

Kör den deklarerade standardbibliotekssviten från rotkatalogen:

```bash illustrative
python -B -m unittest discover -s chapter-26-iteration-generators/examples/tests -t chapter-26-iteration-generators/examples -p 'test_*.py'
```

`-B` förhindrar att bytekodscache skapas. Testupptäckten lägger till den
medföljande katalogen `examples` som importrot och kör bara `test_*.py` under
dess `tests`-paket. Sviten kontrollerar:

- normal och tom strikt parning samt `ValueError` för olika längder;
- normal nedräkning, noll, ogiltig gräns, uttömning och återskapande;
- de fem första begränsade kvadraterna och ogiltiga gränser;
- ändlig delegering med tomma grupper;
- fördröjt `ZeroDivisionError` och återhämtning med rättad indata; och
- delvis stängning, normal uttömning, ogiltig städning och städning exakt en gång.

Kommandot förväntas avslutas med kod noll. En saknad tolk eller ett
testresultat skilt från noll är inte godkänt: läs det första misslyckade testet,
rätta det minsta kontraktet, ta bort tillfälligt tillstånd och kör både det
fallet och dess lyckade granne igen.

Markdown-blocken `source-ref` är registrerade under `learning:contract`. De är
evidenslänkar, inte kod som körs av den generiska Markdown-vägen. Den
uttryckliga kontrollen av inlärningsbryggor äger deras medföljande beteende;
små block märkta `runnable` och `expected-error` kan fortfarande verifieras av
den begränsade generiska verifieraren.

Verifieringen bevisar beteendet som körts på den valda tolken. Den bevisar inte
i sig undervisningskvalitet, översättningsflyt, bred plattformskompatibilitet,
tillgänglighet eller publiceringsgodkännande.

## Sammanfattning och avslutande reflektion

Du kan nu välja ett traverseringsverktyg efter kontrakt:

- använd en vanlig loop när dess steg är tydligast;
- använd en enkel comprehension för att bygga en liten konkret samling;
- använd `enumerate` för positioner och strikt `zip` för lika lång parning;
- behandla iteratortillstånd och uttömning uttryckligt; och
- använd en generator endast med en avsiktlig konsumentgräns och en ägare av
  städningen.

Innan du går vidare, förklara en pipeline högt: var värdena uppstår, var
tillståndet finns, vad som stoppar konsumtionen, vilket fel som går att
återhämta sig från och vem som städar. Om varje svar är konkret är syntaxen inte
längre magisk—du designar dataflödet.
