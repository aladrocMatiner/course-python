# Kapitel 28 · Professionellt slutprojekt: en orderhanterare, fyra steg

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Det här ska vi bygga

Du ska utveckla en lokal orderhanterare i stället för att starta fyra
fristående slutprojekt. Grundsteget kombinerar oföränderliga värden, klasser
och funktioner i minnet. Det praktiska steget behåller samma domän och lägger
till SQLite, ett kommandoradsgränssnitt (CLI), konfiguration, loggning och
tester. Ett valfritt systemsteg exponerar samma service genom en begränsad
loopback-adapter. Ett sista valfritt hero-steg verifierar en källdistribution
och en wheel utan att publicera någon av dem.

Alla exempel använder påhittade identifierare som `ORD-001` och
artikelbeteckningar som `widget`. Ersätt dem inte med verklig information om
kunder, adresser, betalningar, autentiseringsuppgifter eller produktion.

## Lärandemål

När du har slutfört de steg du väljer kan du:

- modellera en begränsad och oföränderlig `Order` och förklara varje tillåten
  övergång;
- skilja domänens, servicens, repositoryts, CLI:ets och det valfria nätverkets
  ansvarsområden åt;
- bevara det tidigare tillståndet efter fel i validering, dubblettkontroll,
  övergång, låsning eller databas;
- använda ett SQLite-baserat CLI med uttrycklig konfiguration, stabil utdata,
  meningsfulla slutkoder och loggar som skyddar integriteten;
- verifiera normalfall, gränsfall, ogiltiga fall och återhämtning vid den gräns
  som ansvarar för dem;
- köra ett valfritt loopback-labb med uttryckliga gränser för byte, begäranden,
  samtidighet och tid samt deterministisk avstängning; och
- skilja evidens från källträdet från evidens för en byggd, inspekterad och
  rent installerad artefakt, utan att ladda upp den.

## Förkunskaper och vägar som kan avslutas oberoende

Kapitelnumret gör inte kapitel 23–27 till automatiska förkunskaper. Börja bara
med ett steg vars namngivna startkontrollpunkt du uppfyller.

### Grundväg

- **Start:** [klasskontrollpunkten i kapitel 12](../chapter-12-oop/README.sv.md#kontrollpunkt-och-bedömningsmatris)
  och kapitlets [övning med en oföränderlig dataclass](../chapter-12-oop/README.sv.md#vägledda-övningar-med-todo),
  plus funktioner, villkor, loopar och samlingar från kapitel 3–11.
- **Tid:** 2–3 pass på 50–75 minuter.
- **Resultat:** en testad service i minnet som skapar, listar och flyttar
  oföränderliga syntetiska ordrar framåt.
- **Slutförande:** alla fem kriterier i grundstegets bedömningsmatris godkänns.
- **Trygg stoppunkt:** behåll artefakten i minnet; persistens, nätverk och
  paketering krävs inte.

### Praktisk väg

- **Start:** slutfört grundsteg plus kapitel
  [13](../chapter-13-files/README.sv.md#kontrollpunkt-och-bedömningsmatris) till
  [18](../chapter-18-testing/README.sv.md#kontrollpunkt-och-bedömningsmatris).
  Slutför [CLI-bilagans kontrollpunkt](../appendix-cli-parser/README.sv.md#kontrollpunkt-och-bedömningsmatris)
  innan du implementerar kommandoadaptern, och slutför
  [loggningskontrollpunkten i kapitel 20](../chapter-20-logging/README.sv.md#kontrollpunkt-och-bedömningsmatris)
  före delkontrollpunkten för loggintegritet. Då blir loggning inte ett dolt
  koncept som används för första gången.
- **Tid:** 4–6 pass på 50–80 minuter.
- **Resultat:** ett transaktionellt SQLite-CLI med uttrycklig konfiguration,
  integritetssäkra händelser, evidens från subprocesser och återhämtning.
- **Slutförande:** standardbibliotekssviten godkänns och eleven kan förklara
  en rollback och CLI:ets prioritetsregel.
- **Trygg stoppunkt:** detta är ett komplett praktiskt slutprojekt. Servern och
  paketbygget är valfria.

### Valfri systemväg

- **Start:** slutfört praktiskt steg,
  [asyncio-kontrollpunkten i kapitel 21](../chapter-21-async/README.sv.md#kontrollpunkt-och-bedömningsmatris)
  och [nätverksbedömningen i kapitel 23](../chapter-23-network-programming/README.sv.md#bedömningsmatris).
- **Tid:** 2–3 pass på 50–75 minuter.
- **Resultat:** en testad newline-JSON-service på `127.0.0.1` och en port som
  operativsystemet tilldelar, med återställd kapacitet och ren avstängning.
- **Slutförande:** de åtta loopback-testerna godkänns och varje deklarerad
  gräns kan förklaras.
- **Trygg stoppunkt:** ingen publik exponering, TLS, autentisering eller
  driftsättning påstås.

### Valfri hero-väg för paketering

- **Start:** slutfört praktiskt steg plus lektionerna om paket och miljöer i
  [kapitel 15](../chapter-15-modulos/README.sv.md#kontrollpunkt-och-bedömningsmatris)
  och [kapitel 16](../chapter-16-entornos/README.sv.md#kontrollpunkt-och-bedömningsmatris).
- **Tid:** 2–3 pass på 50–80 minuter efter att de exakta byggindata medvetet
  har tillhandahållits.
- **Resultat:** lokal evidens från sdist till wheel till ren installation från
  en främmande arbetskatalog.
- **Slutförande:** varje verifieringsfas godkänns och eleven kan ange vilken
  värd som faktiskt testades.
- **Trygg stoppunkt:** uppladdning, signering, attestering, token eller ändring
  av paketindex ingår inte i kapitlet.

## Arkitekturen i ord

CLI:et och den valfria loopback-adaptern översätter extern indata. Båda anropar
`OrderService`. Servicen skapar `Order`-värden och ber ett `OrderRepository`
att lagra dem eller flytta dem framåt. `InMemoryOrderRepository` och
`SQLiteOrderRepository` implementerar samma operationer. SQLite är därför en
utbytbar persistensdetalj, inte en andra uppsättning affärsregler.

Kontrollflödet är:

1. en adapter tolkar och begränsar indata;
2. servicen konstruerar eller begär en domänoperation;
3. den oföränderliga ordern validerar den exakta domänen;
4. det valda repositoryt bekräftar hela ändringen eller bevarar det tidigare
   tillståndet;
5. adaptern avger begränsad utdata eller en stabil felkategori.

Den numrerade beskrivningen är det fullständiga textalternativet till ett
arkitekturdiagram. Ingen betydelse beror på färg, pilar eller placering på
skärmen.

## Companion och arbetskatalog för verifiering

Den körbara auktoriteten är
`chapter-28-professional-capstone/examples/order-tracker/`. Kör hela sviten ur
standardbiblioteket från repositoryts rot:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

Kommandot testar domänen, båda repository-implementationerna, servicen,
CLI-subprocesser, loggintegritet, loopbacks livscykel, metadata, artefaktens
preflight och fixturer för arkivinspektion. Det använder tillfälliga kataloger,
falska data, tillfälliga portar, begränsad utdata från barnprocesser och
begränsade tidsgränser.

---

## Steg 1 · Grund: oföränderlig domän och service i minnet

### Grundstegets mål och sammanhang

En orderhanterare låter enkel tills en dubblett skriver över en tidigare order
eller en skickad order flyttas bakåt. Grundsteget gör reglerna observerbara
innan en databas eller adapter lägger till kognitiv belastning.

Du ska:

- skapa en oföränderlig order med status `pending`;
- bara flytta `pending → packed → shipped`;
- acceptera de exakta inkluderande text- och kvantitetsgränserna;
- lista efter `order_id` i stället för efter en tillfällig insättningsordning;
  och
- bevisa att varje avvisad operation lämnar det tidigare tillståndet oförändrat.

### Förutsäg livscykeln

Förutsäg följande observationer innan du läser implementationen:

1. Vilka statusar blir resultatet av två anrop till `advance("ORD-001")`?
2. Vad ska ett tredje anrop göra?
3. Om en andra create-operation använder `ORD-001` med en annan artikel,
   vilken order ska då finnas kvar?
4. Ska `True` godtas som kvantiteten `1`?

Skriv den förväntade statusen eller undantagskategorin, inte en fullständig
traceback.

### Minsta teori: värde, service och repository

`Order` är en fryst dataclass, enligt kapitel 12:s övning med en oföränderlig
dataclass. En övergång returnerar en ny ögonblicksbild; den redigerar inte det
tidigare värdet. `OrderService` samordnar användningsfallet. Ett litet
arvskontrakt namnger repositoryts fem operationer, och
`InMemoryOrderRepository` implementerar dem med en dictionary vars resultat
returneras i sorterad identifierarordning. Inget koncept för strukturell
typning från kapitel 27 krävs för det här steget.

De stabila domänfelen är:

- `OrderValidationError` för ogiltiga begränsade värden;
- `DuplicateOrderError` för en identifierare som redan finns;
- `UnknownOrderError` för en identifierare som saknas;
- `InvalidTransitionError` när `shipped` flyttas framåt; och
- `RepositoryError` för fel i persistens eller livscykel.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/domain.py check=learning:contract -->
```python source-ref
pending = Order("ORD-001", "widget", 2)
packed = pending.advanced()
assert pending.status == "pending"
assert packed.status == "packed"
```

### Domängränser

Efter att omgivande blanktecken har tagits bort gäller:

- `order_id` är 1–32 tecken långt;
- `item` är 1–80 tecken långt;
- `quantity` är exakt den inbyggda typen `int` från 1 till och med 1 000;
- `bool` och subklasser till `int` avvisas; och
- `status` är exakt `pending`, `packed` eller `shipped`.

Värdena 32, 80, 1 och 1 000 godtas. Tom text, längderna 33/81, kvantiteterna
0/1 001 och båda booleska värdena avvisas innan repositoryts tillstånd ändras.

### Vägledd TODO för grundsteget

Arbeta i en kopia som kan tas bort eller i en tillfällig fil som importerar
companion-koden:

```python todo
repository = InMemoryOrderRepository()
service = OrderService(repository)

# TODO 1: create ORD-001 for two widgets and record its status.
# TODO 2: advance it twice and record both new statuses.
# TODO 3: try one more advance and record the exception category.
# TODO 4: list again and prove ORD-001 is still shipped.
```

**Ledtråd:** jämför en oföränderlig ögonblicksbild som togs före den avvisade
operationen med `service.get("ORD-001")` efteråt. Fånga inte `Exception`; namnge
det domänfel du förväntar dig.

### Evidens för normalfall, gränsfall, fel och återhämtning

- **Normalfall:** `pending`, `packed` och `shipped` visas i den ordningen.
- **Gränsfall:** identifierarlängden 32, artikellängden 80 och kvantiteterna
  1/1 000 godkänns.
- **Återhämtningsbart fel:** en dubblett höjer `DuplicateOrderError` och
  behåller den ursprungliga artikeln och kvantiteten.
- **Återhämtning:** försök igen med en unik identifierare; det lyckas utan att
  repositoryts inre tillstånd repareras.
- **Slutgiltigt fel:** att flytta `shipped` framåt höjer
  `InvalidTransitionError`; en ny hämtning returnerar fortfarande `shipped`.

Kör den fokuserade evidensen:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_domain tests.test_service -v
```

### Förklarad lösning för grundsteget

Lösningen konstruerar `Order` innan `repository.add` anropas, så ogiltiga data
når aldrig lagringen. `advanced()` använder en uttrycklig karta med nästa
status och returnerar ett nytt fryst värde. Repositoryt tilldelar värdet först
när övergångsvalideringen har lyckats. Dubbletten upptäcks före tilldelningen i
dictionaryn. Den ordningen gör återhämtning med oförändrat tillstånd till en
egenskap hos designen, inte ett städningsknep.

### Vanliga misstag i grundsteget

- Att ändra `order.status` direkt motverkar oföränderliga ögonblicksbilder och
  misslyckas.
- Att behandla `bool` som en kvantitet godtar ett värde som tekniskt liknar ett
  heltal men har fel betydelse i domänen.
- Att fånga alla undantag döljer om validering, uppslagning, övergång eller
  persistens misslyckades.
- Att returnera dictionaryns insättningsordning skulle göra en tillfällig
  ordning till ett kontrakt; servicen kräver sorterade identifierare.

### Grundstegets kontrollpunkt och bedömningsmatris

Ge en poäng för varje kriterium:

- **Korrekthet:** en order når alla tre statusvärdena i ordning.
- **Gräns:** de inkluderande text- och kvantitetsgränserna godkänns och de
  första ogiltiga värdena underkänns.
- **Återhämtning:** fel vid dubblett och slutgiltig övergång bevarar
  ögonblicksbilderna.
- **Separation:** eleven kan skilja värde, service och repository åt.
- **Förklaring:** eleven förklarar varför en ny oföränderlig ögonblicksbild gör
  resonemang om rollback enklare.

Fem poäng slutför grundsteget. Vid fyra poäng upprepar du bara fallet som
saknas; under fyra återvänder du till testerna för gränser och bevarat
tillstånd. Du kan stanna här med en komplett, testad artefakt i minnet.

### Grundstegets reflektion

Vilket ordningsbeslut — validera, beräkna och sedan tilldela — gör mest för att
skydda tillståndet, och vad skulle gå sönder om tilldelningen skedde först?

---

## Steg 2 · Praktiskt: SQLite, CLI, konfiguration, loggning och tester

### Det praktiska stegets mål och förutsägelse

Det praktiska steget behåller samma service och byter bara ut dess repository.
Förutsäg följande innan du kör det:

- vilken databas som vinner när både `ORDER_TRACKER_DB` och `--database` finns;
- om en saknad databasinställning implicit ska skapa `orders.db`;
- vad som finns kvar efter att en SQLite-uppdatering avbryts före commit; och
- vilken stream som bär stabila resultat respektive diagnostik och händelser.

Svaren är: det uttryckliga argumentet vinner; ingen standardfil skapas; den
tidigare bekräftade statusen finns kvar; stdout bär resultat medan stderr bär
diagnostik och valfria händelser.

### SQLite-transaktionens gräns

`SQLiteOrderRepository` skapar sitt schema idempotent och öppnar kortlivade
anslutningar med en standardgräns på 250 ms för en upptagen databas.
Skrivoperationer inleder transaktionen uttryckligen, validerar och läser,
tillämpar en hel ändring och gör sedan commit. Ett databasundantag gör rollback
och mappas till `RepositoryError` utan att avslöja SQL, artikeltexten som
bundits som parameter eller en fullständig sökväg.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/repositories.py check=learning:contract -->
```python source-ref
repository = SQLiteOrderRepository(database, busy_timeout_ms=250)
service = OrderService(repository)
service.create("ORD-001", "widget", 2)
```

De gemensamma repository-testerna kör samma kontrakt för
add/get/list/advance mot minnet och SQLite. En kontrollerad trigger avbryter en
uppdatering; testet observerar `pending` efteråt, tar bara bort sin egen trigger
och flyttar sedan ordern framåt utan fel. Ett annat test håller ett uttryckligt
tillfälligt lås längre än 50 ms, observerar ett begränsat fel, släpper låset och
försöker igen.

### CLI-kontrakt

Det installerade kommandot stöder:

```bash illustrative
order-tracker --database path/to/disposable/orders.sqlite3 add ORD-001 widget 2
order-tracker --database path/to/disposable/orders.sqlite3 advance ORD-001
order-tracker --database path/to/disposable/orders.sqlite3 list
```

Stabil utdata vid framgång är kompakt JSON:

```text illustrative
{"order_id":"ORD-001","status":"pending"}
```

Att lista en order med status `pending` ger:

```text illustrative
{"item":"widget","order_id":"ORD-001","quantity":2,"status":"pending"}
```

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/cli.py check=learning:contract -->
```python source-ref
configured = args.database if args.database is not None else environment.get("ORDER_TRACKER_DB")
```

Slutkoden är en del av gränssnittet:

- `0`: kommandot slutfördes;
- `1`: domänen eller repositoryt avvisade operationen;
- `2`: argumenten eller databaskonfigurationen går inte att använda.

Utan konfiguration beskriver stderr hur du återhämtar dig och ingen databas
skapas. En CLI-kvantitet som inte är ett heltal är ett användningsfel (2); ett
heltal utanför domänen är ett domänfel (1). Ett senare giltigt anrop mot samma
valda databas lyckas.

### Integritet i loggningen

`--verbose` lägger till en begränsad händelse på stderr. En lyckad create ser ut
så här:

```text illustrative
event=add order_id=ORD-LOG outcome=success
```

Händelser får innehålla fas, stabil orderidentifierare, antal, resultat och
stabil kategori. De innehåller aldrig artikeltext, en fullständig databassökväg,
miljövärden, SQL med data, hemligheter eller traceback-detaljer från förväntade
fel. Stdout förblir oförändrad så att skript kan tolka den.

### Vägledd praktisk TODO

Lägg till ett subprocess-test, inte ett anrop till en privat CLI-hjälpare:

```python todo
# TODO 1: invoke the CLI to create ORD-RECOVER in a temporary database.
# TODO 2: invoke the same add again and assert exit 1 plus duplicate-order.
# TODO 3: invoke list and prove the original item/quantity remain.
# TODO 4: retry with ORD-RECOVER-2 and assert exit 0.
```

**Ledtråd:** kontrollera returkoden, stdout, stderr och databastillståndet.
Begränsa subprocessens tidsgräns och den fångade utdatan. Använd bara en
`TemporaryDirectory` och syntetiska värden.

### Praktisk evidens och förklarad lösning

Kör:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest \
  tests.test_repository_contract tests.test_cli tests.test_metadata -v
```

Den förklarade lösningen anropar `python -m order_tracker` från en främmande
tillfällig arbetskatalog, med bara companion-kodens `src`-katalog på
källtestets importsökväg. Den går inte runt `argparse`. Dubblettinsättning
avvisas med samma domän-/repositorykategori som servicen exponerar. Ett sista
`list` bevisar att den ursprungliga raden överlevde; en ny identifierare
bevisar återhämtningen.

### Vanliga misstag i det praktiska steget

- Att välja en dold standarddatabas får ett oskyldigt kommando att ändra
  arbetsträdet.
- Att skriva en fullständig databassökväg eller artikel i loggarna förvandlar
  diagnostik till en dataläcka.
- Att bara testa `cli.main` kan missa argumenttolkning vid startpunkten,
  streams, slutkod och problem med en främmande arbetskatalog.
- Att fånga `sqlite3.Error` i CLI:et läcker persistensdetaljer och duplicerar
  repositoryts ansvar.
- Att radera en låst eller skadad databas som ”återhämtning” kan förstöra
  orelaterade data. Rätta den tillfälliga sökvägen eller släpp bara det lås som
  testet äger.

### Det praktiska stegets kontrollpunkt och bedömningsmatris

Ge en poäng för varje kriterium:

- **Repository-kontrakt:** minnet och SQLite ger samma observerbara
  livscykel och fel.
- **Atomicitet:** en kontrollerad misslyckad uppdatering bevarar den tidigare
  raden och en senare ren transaktion lyckas.
- **CLI/konfiguration:** prioritet, JSON, stream-separation och slutkoderna
  0/1/2 matchar kontraktet.
- **Loggintegritet:** händelser innehåller fas och resultat men inget av de
  förbjudna värdena.
- **Testning/återhämtning:** subprocess-tester täcker normal-, gräns-, fel- och
  återförsöksbeteende utan rester.
- **Förklaring:** eleven kan förklara var commit sker och varför `--database`
  vinner.

Det praktiska steget är slutfört när alla sex kriterier är godkända. Valfritt
system- eller paketeringsarbete kan inte kompensera för en nolla här. Det här
är en trygg professionell stoppunkt.

### Det praktiska stegets reflektion

Varför är ”samma service, annat repository” starkare evidens än att skriva en
andra SQLite-specifik applikation från grunden?

---

## Steg 3 · Valfri systemutökning: begränsad loopback-adapter

### Systemmålet och de exakta gränserna

Den valfria adaptern lär ut livscykel, inte internetdriftsättning. Den använder
UTF-8-JSON avgränsad med radslut, en begäran per anslutning, `127.0.0.1` och en
port som operativsystemet tilldelar.

Standardgränserna är:

- byte i begäran: 1 024 inklusive radslutet;
- byte i svar: 4 096 inklusive radslutet;
- totalt antal godtagna begäranden: 8;
- samtidigt aktiva handlers: 4;
- ordrar som returneras av ett listsvar: 20; och
- tidsgräns för inaktiv läsning/skrivning: 0,5 sekunder.

Konstruktorvalideringen tillåter begäransstorlekar från 1 till och med 65 536
byte, svarsstorlekar från 38 till och med 65 536 byte, gränserna för totalt
antal begäranden och antal ordrar per listning från 1 till och med 100,
samtidighet från 1 till och med 32 och tidsgränser från 0,05 till och med 10
sekunder. Miniminivån 38 byte är den
fullständiga felramen `response-limit`, så även det återhämtningsmeddelandet
respekterar vald gräns. Adaptern behåller ingen begäranhistorik eller obegränsad
utdatakö. En anslutning som släpps igenom samtidighetsgrinden förbrukar en plats
i det totala antalet begäranden även om ramen senare är felaktig eller når sin
tidsgräns; en peer som avvisas som `busy` gör det inte.

### Förutsäg framing och kapacitet

Förutsäg vad som händer när en peer:

1. skickar giltig JSON under 1 024 byte;
2. skickar 1 025 byte före ett radslut;
3. öppnar den enda tillåtna handlern och stannar;
4. skickar felaktig UTF-8/JSON; eller
5. skickar en nionde begäran.

De stabila resultaten är i tur och ordning framgång, `request-too-large`,
`busy` för en samtidig peer följt av återställd kapacitet,
`malformed-request` samt `request-limit` följt av ren avstängning.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/loopback.py check=learning:contract -->
```python source-ref
async with LoopbackOrderServer(service) as server:
    response = await send_request(server.address, {"action": "list"})
```

En giltig begäran är:

```json illustrative
{"action":"add","order_id":"NET-1","item":"widget","quantity":2}
```

Det begränsade svaret är:

```json illustrative
{"ok":true,"order":{"item":"widget","order_id":"NET-1","quantity":2,"status":"pending"}}
```

### Vägledd TODO för systemsteget

Utöka det tillfälliga testet, inte en publik service:

```python todo
# TODO 1: start with max_concurrency=1 and an ephemeral port.
# TODO 2: open one client and wait on connection_started without sleeping.
# TODO 3: prove a second client receives busy.
# TODO 4: finish/close the first client, await capacity_available, and retry.
# TODO 5: close the server and assert zero active connections/tasks.
```

**Ledtråd:** beredskap och återhämtning är händelser. En fast väntetid kan inte
bevisa någon av dem. Stäng alltid klientens writer i `finally`.

### Fel, återhämtning, avbrytning och lösning

Sviten täcker konstruktorns gränser, en begäran på den exakta bytegränsen,
giltig add/list, felaktig indata, för stor indata, list-/svarsgränser, en
upptagen handler, tidsgräns vid inaktivitet, uttömt totalantal begäranden,
avbrytning av en handler som har stannat, återlämnad kapacitet och avstängning av
listenern. Servern stänger listenern, avbryter och inväntar varje handler den
äger och slutför sedan `wait_closed()`. `CancelledError` höjs på nytt efter att
varje writer har stängts.

Kör bara den valfria evidensen:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_loopback -v
```

Den förklarade lösningen binder aldrig till `0.0.0.0`, väljer aldrig en fast
port, kontaktar aldrig ett publikt mål, inaktiverar aldrig en säkerhetskontroll
och påstår aldrig TLS, autentisering eller produktionshärdning. Den tillämpar
byte- och tillståndsgränser innan data behålls och bevisar en senare begäran
eller en ren avstängning efter avvisning.

### Vanliga misstag i systemsteget

- En TCP-skrivning är inte garanterat en läsning; radslutet är den deklarerade
  ramgränsen.
- En fast väntetid är inte evidens för serverberedskap eller städning.
- Loopback tar bort publik routing, inte alla problem med applikationssäkerhet.
- Avbrytning utan att invänta tasks kan lämna sockets och varningar efter sig.
- En valfri adapter får inte bli ett beroende vid import eller paketering.

### Systemstegets kontrollpunkt och bedömningsmatris

Ge en poäng för **loopback/bindning till tillfällig port**, **framing och bytegränser**,
**gränser för begäranden/samtidighet**, **tidsgräns/återställd kapacitet**,
**avbrytning/avstängning** och **förklaring av varför detta inte är
produktion**. Alla sex slutför det valfria systemsteget. Behåll annars
resultatet från det praktiska steget och rapportera systemevidensen som
ofullständig.

### Systemstegets reflektion

Vilken resurs begränsas av varje tal, och vilken testkontroll bevisar att
kapaciteten återkommer?

---

## Steg 4 · Valfri hero-paketering: verifiera artefakten, inte checkouten

### Paketeringsmålet och evidensgränsen

Godkända källtester bevisar checkouten. De bevisar inte att en sdist innehåller
alla källor, att en wheel har korrekta metadata, att installationen fungerar
eller att importen löses utanför repositoryt. Hero-steget testar påståendena
separat.

Distributionen är `course-order-tracker`, importpaketet `order_tracker`,
kommandot `order-tracker`, versionen `1.0.0`, `Requires-Python >=3.11`, och den
har inga beroenden vid körning. Dess wheel deklarerar `py3-none-any`. Taggen är
en kompatibilitetsdeklaration, inte bevis för värdar där den inte har körts.

### Byggindata är direkta pins, inte en låsfil

`requirements-build.txt` registrerar `build==1.3.0`,
`setuptools==80.9.0` och `wheel==0.45.1` som exakta direkta pins för det här
arbetsflödet. Filen har inga hashar, ingen resolver-proveniens, ingen
plattformsmatris och ingen transitiv indexögonblicksbild, så den kallas inte en
fullständig låsfil.

Companion-filens [register över byggindata](examples/order-tracker/BUILD_INPUTS.md)
registrerar separat valda releasefilnamn, observerade SHA-256-värden från PyPI,
rapporterade licensmetadata och primära formatreferenser. Verifieraren
kontrollerar hashvärdena för de två backend-wheels som används offline. Den
proveniensobservationen är ändå inte en upplöst beroendegraf eller ett
mänskligt godkännande av licens eller publicering.

Den första hämtningen av verktyg är ett separat, medvetet underhållssteg som
kan behöva ett godkänt nätverk eller index. Verifieraren utför aldrig det
steget. Innan det godkända kommandot körs måste värden tillhandahålla
POSIX-processgrupper för begränsad städning av hela barnprocessträdet,
`build==1.3.0` måste redan kunna importeras och `ORDER_TRACKER_WHEELHOUSE`
måste ange en särskild offline-katalog som bara innehåller de exakt
registrerade artefakterna för setuptools och wheel. Saknad, extra eller
felmatchad indata är ett icke godkänt förkunskapsresultat.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py check=learning:contract -->
```python source-ref
wheelhouse = require_prerequisites()
verify(wheelhouse)
```

Det godkända kommandot från repositoryts rot är:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

Om verktygen inte har tillhandahållits i denna checkout är det sanningsenliga
resultatet nollskilt och börjar med:

```text illustrative
prerequisite missing:
```

Det är inte ett godkänt artefaktresultat och ogiltigförklarar inte det redan
slutförda praktiska källsteget.

### Verifieringsfaser

Verifieraren:

1. tar fingeravtryck av och skannar källträdet;
2. kopierar det till en oberoende tillfällig källrot;
3. kör isolerade PEP 517-byggen offline från deklarerad wheelhouse;
4. inspekterar exakt sdist och den första rena wheelen;
5. packar säkert upp sdist i en andra källrot;
6. bygger om en wheel från den distribuerade källan;
7. kontrollerar metadata, nödvändiga medlemmar, `RECORD`, licens, frånvaro av
   körtidsberoenden och `py3-none-any`;
8. installerar exakt den ombyggda wheelen med `--no-index --no-deps` i en ny
   miljö;
9. kör `pip check` samt smoke-test av metadata/import/domän/CLI från en
   främmande katalog;
10. rapporterar filnamn och SHA-256-observationer samt körda versioner; och
11. tar bort alla tillfälliga rötter för källa, utdata, installation, cache,
    databas och främmande arbetskatalog både vid framgång och fel.

Den avvisar en enskild käll-/arkivmedlem över 2 MiB, en projektögonblicksbild
över 8 MiB, ett arkiv över 12 MiB i komprimerad eller uppackad form, sammanlagd
utdata från barnprocesser över 16 KiB, en fas för första bygge, ombyggnad eller
installation över 180 sekunder eller någon annan barnprocessfas över 30
sekunder. En värd
som inte är POSIX rapporterar ett förkunskapsresultat; kursen ersätter inte
detta med ett svagare påstående om processstädning.

SHA-256 bevisar vilka byte som observerades i den körningen. Det är inte ett
påstående om ett reproducerbart bygge byte för byte.

### Vägledd TODO för paketering

Fyll i den här evidensplanen före körning:

```text todo
TODO 1: name the source input and the two independently built wheels.
TODO 2: predict where order_tracker.__file__ must resolve after clean install.
TODO 3: name the phase that should reject a database or .env inside an archive.
TODO 4: record the exact interpreter/host actually executed.
TODO 5: state why no command in the plan uploads an artifact.
```

**Ledtråd:** ”testerna godkändes” räcker inte. Registrera bygg, inspektion,
ombyggnad, installation, import, beteende, CLI och städning var för sig. En
saknad förkunskap förblir saknad.

### Paketeringsfel och återhämtning

- Saknad frontend/wheelhouse: tillhandahåll exakt indata uttryckligen;
  inaktivera inte isolering och tillåt inte implicit återgång till ett index.
- Saknad medlem i sdist: rätta `MANIFEST.in` eller metadata, kassera varje
  tillfällig artefakt och bygg om från början.
- Importläcka från källträdet: byt till den nya tolken och främmande
  arbetskatalogen; lägg inte checkouten i `PYTHONPATH`.
- Förbjuden databas/cache/autentiseringsuppgift: ta bort orsaken i källan och
  upprepa inspektionen före installation.
- Fel i CLI-smoke-test: rätta paketet eller entry point och kör om alla
  efterföljande faser, inte bara det sista kommandot.

Verifieringen stannar lokalt. Publicering kräver separat auktorisering,
autentiseringsuppgifter, granskning, policy för signering och attestering samt
indexkontroller som kapitlet varken begär eller använder.

### Vanliga misstag i paketeringssteget

- Att kalla direkta pins en universell låsfil överdriver deras evidens.
- Att behandla ett wheel-filnamn som körningsevidens överdriver kompatibilitet.
- Installation från checkouten låter en saknad paketfil döljas.
- Återanvändning av ett gammalt bygge eller cache ogiltigförklarar evidens för
  ett rent bygge.
- Att rapportera ett saknat byggverktyg som ”överhoppat/godkänt” hittar på ett
  godkänt resultat.
- Att lägga till ett uppladdningskommando utökar auktoriteten utanför
  slutprojektet.

### Paketeringsstegets kontrollpunkt och bedömningsmatris

Om du väljer steget ger du en poäng för **isolerat bygge**,
**sdist-inspektion**, **wheel ombyggd från sdist**, **ren installation och
`pip check`**, **evidens för metadata/import/domän/CLI från en främmande
katalog**, **register över digest/verktygskedja**, **städning** och **förklaring
av att inget publiceras**. Alla åtta slutför hero-steget. Om något inte är
tillgängligt rapporterar du den exakta icke godkända fasen och behåller det
praktiska steg som slutförts oberoende.

### Paketeringsstegets reflektion

Vilket fel kan källtester dölja men en wheel som byggts om från sdist avslöja?

---

## Slutbedömning för valda steg

Ingen obligatorisk kategori får noll poäng i något steg du har valt:

- **Domänkorrekthet:** värden och övergångar matchar det exakta kontraktet.
- **Ansvarsseparation:** adaptrar äger inte domän- eller SQLite-regler.
- **Persistensens atomicitet:** avvisning bevarar bekräftat tillstånd.
- **CLI/konfiguration:** prioritet, JSON, streams och slutkoder är stabila.
- **Loggintegritet:** diagnostik avslöjar inte artikel, sökväg, miljö, SQL-data,
  autentiseringsuppgift eller traceback från ett förväntat fel.
- **Testning och återhämtning:** normalt, gränsnära, ogiltigt och reparerat
  beteende är observerbart.
- **Systemlivscykel, om vald:** gränser, avbrytning och städning godkänns.
- **Artefaktevidens, om vald:** faserna från källa till installerad artefakt
  godkänns lokalt.
- **Förklaring:** eleven kan motivera ett designbeslut och en
  återhämtningsgräns.

Valfria poäng kan inte dölja ett fel i grundsteget eller det praktiska steget.
Ett godkänt verktyg utan en förklaring lämnar den kategorin i
bedömningsmatrisen ofullständig.

## Fullständig spårbarhet och verifiering

[Spårbarheten för kapitel 28](TRACEABILITY.md) kopplar varje egenskap till
tidigare undervisning, elevavsnittet, companion-källan, det exakta testet och
kriteriet i bedömningsmatrisen. Companion-kodens
[verifieringsguide](examples/order-tracker/README.md) registrerar kommandona och
gränsen för artefaktens förutsättningar.

## Kontroll av repositoryts hygien

Efter verifieringen ska du även inspektera ignorerade sökvägar under kapitlet.
Det får inte finnas en virtuell miljö, `build/`, `dist/`, wheel, sdist,
SQLite-databas, `*.egg-info`, cache, bytecode, coverage,
autentiseringsuppgift, elevdata, aktiv socket eller barnprocess. Allt genererat
tillstånd hör hemma i tillfälliga rötter.

## Källor, originalitet och gränsen för mänsklig granskning

Kapitlets prosa, påhittade orderscenarier, TODO-uppgifter, tester och
companion-kod skrevs som eget kursmaterial. Tekniskt beteende kontrollerades
mot den officiella Python-dokumentationen för
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html),
[`argparse`](https://docs.python.org/3/library/argparse.html) och
[`asyncio` streams](https://docs.python.org/3/library/asyncio-stream.html), samt
de primära paketeringsreferenser som anges i companion-filens register över
byggindata. Ingen prosa eller övning framställs som kopierad från dessa
referenser.

Deklarationen och den automatiserade strukturen och testerna godkänner inte
proveniens, licenskrav, översättningskvalitet, renderad tillgänglighet, arabisk
bidi eller publicering. De förblir uttryckliga grindar som kräver en sakkunnig
människas granskning.

## Avslutande reflektion

Slutprojektet är färdigt på det steg du valde när beteende, återhämtning,
städning och din förklaring stämmer överens. Vilken gräns — oföränderlig domän,
transaktion, adapter eller artefakt — gav dig starkast ny evidens, och vad
skulle du verifiera härnäst före en verklig release?
