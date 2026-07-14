# Kapitel 23 · Nätverksprogrammering med Python

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

I kapitlet utvecklar du ett lokalt telemetriprojekt från ett första TCP-eko till en resursbegränsad asynkron hubb. Du behöver Python 3.11 eller senare, men inga tidigare nätverkskunskaper, ingen internetanslutning, inga administratörsrättigheter och inga externa paket.

Alla servrar lyssnar enbart på loopback: `127.0.0.1` eller, i IPv6-utökningen, `::1`. Byt inte till ett publikt gränssnitt medan du lär dig. Skanning, sniffning, raw sockets, spoofing, exploatering, egen kryptografi och publik driftsättning ligger utanför kapitlet.

## Resultat, förkunskaper och vägar

Du lär dig vägen från text till bytes, att välja TCP eller UDP, rama in och validera ett protokoll, betjäna flera klienter utan obegränsat tillstånd, använda backpressure med `asyncio`, verifiera TLS-identitet samt testa fel och avstängning.

Repetera bara det du behöver:

- [Streams och context managers i kapitel 13](../chapter-13-files/README.sv.md): deterministisk städning.
- [Undantag i kapitel 14](../chapter-14-exceptions/README.sv.md): återhämtning från väntade fel.
- [Automatiserade tester i kapitel 18](../chapter-18-testing/README.sv.md): arrangera, agera och kontrollera.
- [HTTP i kapitel 19](../chapter-19-http/README.sv.md): HTTP är ett applikationsprotokoll, inte transporten.
- [Loggning i kapitel 20](../chapter-20-logging/README.sv.md): användbar diagnostik utan payload-läckor.
- [`asyncio` i kapitel 21](../chapter-21-async/README.sv.md): coroutines, tasks och cancellation.

| Väg | Tid | Startpunkt | Observerbart resultat |
|---|---:|---|---|
| Grund | 2 × 45–60 min | Funktioner och undantag | Förklarat lokalt TCP-eko |
| Mellan | 3 × 45–60 min | Grundcheckpoint | Testat sekventiellt protokoll och UDP-jämförelse |
| Avancerad | 3–4 × 45–60 min | Mellancheckpoint och kapitel 21 | Begränsad asynkron flerklientshubb |

TLS och IPv6 är valfria avancerade utökningar. Varje tidigare checkpoint är användbar utan dem.

## Grundväg — från ett meddelande till en TCP-ström

### 1. Ett litet nätverksordförråd

En **klient** inleder ett samtal; en **server** väntar på samtal. En **host** är en dator eller nätverksmiljö. Domännamnssystemet (**DNS**) kopplar namn till adresser. En **IP-adress** identifierar ett gränssnitt och en **port** väljer ett program på värden. En **socket** är operativsystemets ändpunkt. Ett **protokoll** är gemensamma meddelanderegler.

Tänk på ett brev: IP-adressen är byggnaden, porten är rummet och protokollet är den överenskomna blanketten. Analogin slutar där: TCP överför en ordnad byte-ström, inte separata kuvert.

Lager delar ansvar. IP flyttar paket, TCP eller UDP ger transportegenskaper och HTTP eller vår telemetri är applikationsprotokoll. Återvänd till kapitel 19 för HTTP-API:er; här bygger vi ett litet protokoll för att förstå lagret under.

#### Förutsäg, kör och observera

Python-sockets utbyter **bytes**. Text kräver en överenskommen kodning. Förutsäg `len(encoded)`:

<!-- bookcheck: expect="temperature=21.5\n16" timeout=2 -->
```python runnable
text = "temperature=21.5"
encoded = text.encode("utf-8")
print(encoded.decode("utf-8"))
print(len(encoded))
```

Du ser samma text och `16`. ASCII-tecknen tar en byte här; det gäller inte alla tecken.

**Ändra:** använd `café` och förutsäg antal tecken och bytes. **Ledtråd:** jämför `len(text)` med `len(text.encode("utf-8"))`. Förklarad lösning: `é` är ett Python-tecken men två UTF-8-bytes.

**Happy path:** båda peers använder UTF-8. **Edge case:** ett tecken kan vara flera bytes. **Återhämtningsbart fel:** ogiltiga bytes ger `UnicodeDecodeError`; avvisa ramen vid protokollgränsen i stället för att gissa kodning.

### 2. Adresser, namn och lokala försök

`localhost` är ett lokalt namn. IPv4-loopback är `127.0.0.1`, IPv6-loopback är `::1`. `socket.getaddrinfo()` ger kandidater utan att anta adressfamilj. Proben kontaktar aldrig en publik host.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/address_demo.py check=network:network-suite -->
```python source-ref
socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/address_demo.py
```

Adresser och ordning beror på miljön. Sista raden visar om IPv6-loopback kunde bindas; IPv4 är obligatorisk fallback.

Portar under 1024 kan kräva privilegier. Ekot använder `65432`; tester binder port `0` så operativsystemet väljer en ledig ephemeral port. Vid `Address already in use`, välj en annan icke-privilegierad port eller `0`. Avsluta inte okända processer blint.

### 3. Första blockerande TCP-utbytet

TCP ger en ordnad ström, anslutning och EOF. Server: skapa → bind → listen → accept → ta emot/skicka → stäng. Klient: skapa → connect → skicka/ta emot → stäng. Båda använder timeout och context managers.

Förutsäg vilken terminal som väntar och kör:

```text illustrative
# Terminal 1
python -B chapter-23-network-programming/examples/telemetry/echo.py server --port 65432

# Terminal 2, inom trettio sekunder
python -B chapter-23-network-programming/examples/telemetry/echo.py client --port 65432 --text "hello, network"
```

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/echo.py check=network:network-suite -->
```python source-ref
with socket.create_connection(("127.0.0.1", port), timeout=30.0) as connection:
    connection.sendall(text.encode("utf-8"))
```

Observera den returnerade texten och att båda processerna slutar. Tom `recv()` betyder EOF. `sendall()` skickar alla bytes eller höjer fel, men skapar inga meddelandegränser.

**Övning:** skicka `å` via `--text`. **TODO:** förutsäg UTF-8-bytes. **Ledtråd:** klienten sammanfogar chunks före avkodning. **Framgång:** samma text återkommer och båda slutar. Lösningen avkodar aldrig ett delvis chunk.

**Vanligt misstag:** klient först ger `ConnectionRefusedError`. Starta lyssnaren, kontrollera porten och försök igen. Timeout betyder att peer inte gjorde framsteg: rapportera och städa, utan eviga återförsök.

### Grundcheckpoint

Förklara bytes, adress kontra port och TCP-livscykel, och slutför loopback-ekot. Det begränsade tvåterminalsekot är din körbara produkt. Nu lägger vi till ramar och validering.

## Mellanväg — utforma ett verkligt kontrakt

### 4. TCP är ingen meddelandekö: framing

En `sendall()` kan komma genom flera `recv()` och flera sändningar kan komma tillsammans. `json.loads(connection.recv(4096))` går sönder för fragmenterad eller sammanslagen JSON.

Vi använder newline-delimited JSON (**NDJSON**): ett UTF-8-objekt och `\n`. `NDJSONDecoder` behåller en inkrementell buffer, lämnar varje hel rad och sparar endast ofullständig rest. 65 536 bytes före newline tillåts; byte 65 537 utan avgränsare avvisas och bufferten töms.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/protocol.py check=network:network-suite -->
```python source-ref
messages = decoder.feed(chunk)  # noll, ett eller flera kompletta objekt
```

| Fält | Accepterat värde | Avvisning |
|---|---|---|
| `version` | heltal `1`, aldrig `bool` | annan version → `unsupported_version` |
| `type` | strängen `reading` | annan typ → `invalid_message` |
| `sensor_id` | 1–64 ASCII, `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` | ogiltig → `invalid_message` |
| `sequence` | icke-bool heltal `0..2**31-1` | dublett/bakåt → `out_of_order` |
| `value` | ändligt icke-bool tal `-1_000_000..1_000_000` | typ/intervall → `invalid_message` |

Exakt dessa fem fält krävs. Ett godkänt meddelande svarar:

```json illustrative
{"version":1,"type":"ack","sensor_id":"lab.temperature","sequence":7,"status":"accepted"}
```

Fel innehåller endast `version`, `type`, stabil `code` och begränsad `message`, aldrig hela indata. Varje anslutning spårar högst 64 sensorer och behåller endast de 256 senaste godkända avläsningarna. Sensor 65 ger `resource_limit` utan vräkning. När historiken når gränsen tas den äldsta observationen bort, men sekvenstillståndet förblir korrekt. Validering före mutation gör alla avvisningar transaktionella.

#### Övning: utmana antaganden, inte system

Dela en giltig ram i tre delar och lägg två ramar i ett chunk. **TODO:** kontrollera noll/ett/två objekt. **Ledtråd:** `encode_frame()` och slices. **Framgång:** ordningen bevaras och buffer blir noll.

Ändra `sequence=True`, extra fält, värde `1_000_001`, dublett och sensor 65. Förutsäg koden. `test_protocol.py` förklarar lösningen och snapshots bevisar att avvisning inte ändrar tillstånd.

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p test_protocol.py -v
```

Ogiltig UTF-8/JSON, partiell EOF och osäker ram stänger anslutningen eftersom resynkronisering inte är pålitlig. Ett korrekt avgränsat objekt med schemafel kan få fel och fortsätta.

### 5. Jämför UDP-datagram

UDP bevarar datagramgränser men lovar inte leverans, unikhet eller ordning. Det har ingen TCP-anslutning eller EOF. Välj det bara när applikationen tolererar eller reparerar detta och håller meddelanden små.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/udp_demo.py check=network:network-suite -->
```python source-ref
sender.sendto(message, receiver_address)
data, sender_address = receiver.recvfrom(1024)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/udp_demo.py
```

Lokal happy path skriver `received:temperature=21.5`; edge case är timeout. Ett verkligt nät kan tappa, duplicera eller ordna om. UDP-signalen lovar inte TCP-kontraktets sequence/ack.

**Vägledd bedömning:** välj transport för en fil och en ersättningsbar spelposition. **Ledtråd:** måste alla bytes komma i ordning? Lösning: TCP för filen; UDP kan fungera för ersättningsbara uppdateringar om spelet hanterar förlust och storlek.

### 6. Robusthet, loggar och deterministiska tester

Begränsa tid, bytes, klienter, sensorer, sparad historik och väntande utdata. Selectorn stänger en peer efter en sekund utan läs- eller skrivframsteg; båda hubbarna behåller högst 256 godkända observationer för undervisningsinspektion. Logga peer och kategori, aldrig hemligheter eller hela payloads. Försök bara om säkra operationer ett fåtal gånger med backoff; projektet försöker inte automatiskt skriva igen.

Tester använder loopback, ephemeral ports, events/readiness, korta timeout och `finally`, inte Internet eller fasta sleeps. Timeout, avbrott mitt i ram och ogiltig input är väntade återhämtningsvägar.

**Vanligt misstag:** fånga `Exception` och fortsätt med skadat tillstånd. Fånga det konkreta gränsfelet, logga begränsat, stäng vid osäker framing och bevara godkänt tillstånd.

### Mellancheckpoint

Du har en testad sekventiell kärna och UDP-jämförelse. Du kan förklara fragmentering, coalescing, validering före mutation och gränser. Nu hindrar vi en långsam klient från att blockera andra.

## Avancerad väg — begränsad samtidighet, asyncio och TLS

### 7. Flera klienter med selectors

Den sekventiella servern väntar i `recv()`. `selectors.DefaultSelector` anger vilka sockets som är redo. Implementationen accepterar högst 32 klienter, 65 536 ofullständiga bytes, 64 sensorer och behåller de senaste 256 avläsningarna per anslutning, kodar ett väntande svar åt gången och stänger en peer efter en sekund utan framsteg.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
for key, mask in selector.select(timeout):
    # Acceptera, läs eller fortsätt en delskrivning endast när socket är redo.
    ...
```

En thread per anslutning lägger till livscykel och synkronisering. `socketserver` paketerar mönster. Vi implementerar selectors för synlig readiness och gränser; inget val är alltid bäst.

**Förutsägelse:** A skickar en halv ram, B en hel. B får ack först. Integreringstestet visar det och coalescing. Klient 33 stängs inom gränsen.

### 8. Asyncio-streams och backpressure

`asyncio.start_server()` skapar en task per stream. `reader.read()` ger fortfarande godtyckliga chunks och återanvänder decoder. Efter `writer.write()` ger `await writer.drain()` backpressure så utdata inte växer obegränsat.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/async_hub.py check=network:network-suite -->
```python source-ref
writer.write(encode_frame(response))
await asyncio.wait_for(writer.drain(), timeout=client_timeout)
```

Vanligt fel på grund av bindestrecket:

```text illustrative
python -B -m chapter-23-network-programming.examples.telemetry.async_hub
```

Korrekt portabelt kommando:

```text illustrative
cd chapter-23-network-programming/examples
python -B -m telemetry.async_hub
```

Det första är ett förklarat fel, inte körbar vägledning. Det andra använder ephemeral port, skickar en läsning, visar ack och stänger.

Avstängningsordning: sluta acceptera, stäng writers, vänta på `wait_closed()`, cancel återstående handlers och gather. `asyncio.Event` eller `KeyboardInterrupt` är plattformsoberoende; POSIX-signaler är valfria.

**Övning:** två `send_readings()` med `asyncio.gather()`. **TODO:** olika sensor-ID. **Ledtråd:** en begäran väntar på sitt svar. **Framgång:** två `accepted` och `hub.close()` utan handlers eller writers. Lösningen återanvänder testad helper.

### 9. Valfri utökning: verifierad TLS

Transport Layer Security (**TLS**) krypterar och verifierar servercertifikatet. Det autentiserar inte automatiskt klienten och ger ingen behörighet. Tokens, mTLS och policy ligger utanför.

Servern använder också klientgränsen på en sekund för TLS-förhandling och avstängning. En rå TCP-peer som aldrig skickar ClientHello löper därför ut innan applikationshandlaren finns och kan inte hålla avstängningen öppen obegränsat.

Nycklarna i `examples/certificates/` är publika testfixturer, aldrig för drift. Klienten litar endast på `lab-ca-cert.pem`; `ssl.create_default_context(cafile=...)` behåller certifikat- och hostname-kontroll. Använd aldrig `CERT_NONE` eller `check_hostname=False`.

Offline-tester visar lyckat betrodd CA + `localhost`, och stängt fel för fel hostname, utgånget certifikat och obetrodd CA. Det giltiga certifikatet går ut i juli 2046; ett test varnar med tio års marginal.

**Återhämtning:** kontrollera hostname, trust-källa, klocka och förnyelse. Kryptering utan identitetskontroll bevisar inte vem peer är.

### 10. Valfri utökning: IPv6

Om proben kan binda `::1`, använd `family=socket.AF_INET6`; annars registrera förklarad skip och använd IPv4. Det bevisar endast lokal kapacitet.

### 11. Kör all evidens

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
```

Första kommandot kör 33 standardbibliotekstester. Det andra lägger till generiska kontroller och `network:network-suite`. Pluginen äger lokalt protokoll/livscykel; rotverktyget äger Markdown, länkar, språkval, strukturell tillgänglighet, språkstruktur och hygien.

## Slututmaning

Utveckla en sensorklient utan att ändra version 1-kontraktet:

1. **Lätt:** skicka tre ökande läsningar för en sensor. **TODO:** kontrollera tre exakta ack. **Ledtråd:** börja med sekvens noll.
2. **Mellan:** skicka en dublett mellan giltiga läsningar. **TODO:** bevisa att `out_of_order` inte blockerar den senare, större sekvensen. **Ledtråd:** en avvisad läsning får inte mutera tillståndet.
3. **Avancerad:** kör två klienter medan en tredje stannar mitt i en ram och stäng sedan av. **TODO:** bevisa att de aktiva klienterna går framåt och att ingen task blir kvar. **Ledtråd:** använd events och en begränsad `wait_for`, aldrig en gissad väntetid.
4. **Hero-utökning:** aktivera den betrodda TLS-kontexten eller den villkorliga IPv6-vägen och ange exakt vad din dator testade.

En förklarad lösning kombinerar `AsyncTelemetryHub`, `send_readings()`, `ConnectionState` och de befintliga testerna; den skapar inte ett andra protokoll. Testa lyckade ack, ett error-envelope, serverns tillstånd, cleanup efter timeout och `hub.close()`. Behåll alla adresser på loopback.

## Bedömningsmatris

Ge varje område 0 (saknas), 1 (delvis) eller 2 (visat):

- **Protokoll:** exakta fält, framing, ack-/felkoder och sekvenssemantik.
- **Gränser:** ramstorlek, en sekunds selector-idle, 32 klienter, 64 sensorer, 256 sparade observationer och ett väntande svar.
- **Återhämtning:** felaktig input, timeout, EOF och avvisning utan partiell mutation.
- **Samtidighet:** en annan klient går framåt medan en klient står stilla.
- **Säkerhet:** loopback som standard, verifiering av TLS-förtroende och hostname samt ingen loggning av hemligheter.
- **Verifiering:** deterministiska enhets-/integrationstester och explicit lokal evidens.
- **Cleanup och förklaring:** inga övergivna resurser, och du kan förklara varje designval.

Tolv poäng eller mer utan noll i protokoll, gränser eller cleanup är ett starkt resultat. Poängen är återkoppling, inte en etikett; förbättra ett observerbart beteende i taget.

## Slutreflektion och ordlista

Varför behöver TCP framing? Varför validerar vi före mutation? Varför styr `drain()` och timeout resurser? Skilj det lokalt testade från driftsättningsfrågor som inte verifierats här.

- **Backpressure:** bromsa producenten när konsument eller buffer inte hinner med.
- **EOF:** slut på peers utgående ström, visat av tom TCP-läsning.
- **Ephemeral port:** ledig port vald av operativsystemet.
- **Framing:** regler för att hitta meddelanden i en byte-ström.
- **Loopback:** en hosts privata väg tillbaka till sig själv.
- **NDJSON:** ett JSON-värde per newline-avgränsad ram.
- **TLS:** krypterad transport med certifikatbaserad identitetskontroll.

Du har gått från att skicka text till att definiera, begränsa, observera, testa och stänga varje samtal. Samma disciplin används för HTTP, brokers, databaser och andra nätverkssystem.
