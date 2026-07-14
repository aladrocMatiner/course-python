# Capítol 23 · Programació de xarxes amb Python

[English](README.md) · [Español](README.es.md) · Català (actual) · [Svenska](README.sv.md) · [العربية](README.ar.md)

En aquest capítol faràs créixer un projecte de telemetria local: des d'un primer eco TCP fins a una central asíncrona amb recursos acotats. Necessites Python 3.11 o posterior, però no coneixements previs de xarxes, Internet, permisos d'administració ni paquets externs.

Tots els servidors escolten només en loopback: `127.0.0.1` o, a l'extensió IPv6, `::1`. No els canviïs a una interfície pública mentre aprens. Escaneig, sniffing, raw sockets, spoofing, explotació, criptografia pròpia i desplegament públic queden fora del capítol.

## Resultats, prerequisits i rutes

Aprendràs el camí de text a bytes, a triar TCP o UDP, delimitar i validar un protocol, atendre diversos clients sense estat il·limitat, aplicar backpressure amb `asyncio`, verificar la identitat TLS i provar fallades i tancament.

Repassa només el que necessitis:

- [Streams i context managers del capítol 13](../chapter-13-files/README.ca.md): tancament determinista.
- [Excepcions del capítol 14](../chapter-14-exceptions/README.ca.md): recuperació de fallades esperades.
- [Proves automatitzades del capítol 18](../chapter-18-testing/README.ca.md): preparar, actuar i comprovar.
- [HTTP del capítol 19](../chapter-19-http/README.ca.md): HTTP és aplicació, no el transport.
- [Logging del capítol 20](../chapter-20-logging/README.ca.md): diagnòstics sense filtrar payloads.
- [`asyncio` del capítol 21](../chapter-21-async/README.ca.md): coroutines, tasques i cancel·lació.

| Ruta | Temps | Punt de partida | Resultat observable |
|---|---:|---|---|
| Essencial | 2 × 45–60 min | Funcions i excepcions | Eco TCP local explicat |
| Intermèdia | 3 × 45–60 min | Checkpoint essencial | Protocol seqüencial provat i comparació UDP |
| Avançada | 3–4 × 45–60 min | Checkpoint intermedi i capítol 21 | Central asíncrona multiclient acotada |

TLS i IPv6 són extensions avançades opcionals. Els checkpoints anteriors continuen sent útils.

## Ruta essencial — d'un missatge a un stream TCP

### 1. Vocabulari mínim de xarxa

Un **client** inicia una conversa; un **servidor** l'espera. Un **host** és una màquina o entorn de xarxa. El sistema de noms de domini (**DNS**) relaciona noms i adreces. Una **adreça IP** identifica una interfície i un **port** selecciona un programa. Un **socket** és l'extrem ofert pel sistema operatiu. Un **protocol** és el conjunt de regles compartides.

Imagina una carta: la IP és l'edifici, el port l'habitació i el protocol el formulari acordat. L'analogia s'acaba aquí: TCP transporta un stream ordenat de bytes, no sobres separats.

Les capes separen responsabilitats. IP mou paquets; TCP o UDP aporta semàntica de transport; HTTP i la telemetria són protocols d'aplicació. Per consumir API torna al capítol 19; aquí construïm un protocol petit per entendre la capa inferior.

#### Prediu, executa i observa

Els sockets intercanvien **bytes**. El text necessita una codificació acordada. Prediu `len(encoded)`:

<!-- bookcheck: expect="temperature=21.5\n16" timeout=2 -->
```python runnable
text = "temperature=21.5"
encoded = text.encode("utf-8")
print(encoded.decode("utf-8"))
print(len(encoded))
```

Observaràs el mateix text i `16`. Aquí els caràcters ASCII ocupen un byte; no sempre és així.

**Modifica:** usa `café` i prediu caràcters i bytes. **Pista:** compara `len(text)` amb `len(text.encode("utf-8"))`. Solució: `é` és un caràcter de Python, però dos bytes UTF-8.

**Happy path:** tots dos peers usen UTF-8. **Edge case:** un caràcter ocupa diversos bytes. **Error recuperable:** bytes invàlids causen `UnicodeDecodeError`; rebutja el frame al límit del protocol, sense endevinar la codificació.

### 2. Adreces, noms i proves locals

`localhost` és un nom local. El loopback IPv4 és `127.0.0.1` i l'IPv6 és `::1`. `socket.getaddrinfo()` retorna candidats sense assumir una família. El probe no consulta cap host públic.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/address_demo.py check=network:network-suite -->
```python source-ref
socket.getaddrinfo("localhost", 0, type=socket.SOCK_STREAM)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/address_demo.py
```

Les adreces i l'ordre depenen de l'entorn. La darrera línia indica si el bind IPv6 loopback funciona; IPv4 és el fallback obligatori.

Els ports per sota de 1024 poden requerir privilegis. L'eco usa `65432`; les proves fan bind al port `0` perquè el sistema triï un port efímer lliure. Davant `Address already in use`, tria un altre port no privilegiat o `0`; no finalitzis a cegues processos aliens.

### 3. Primer intercanvi TCP bloquejant

TCP ofereix un stream ordenat de bytes, establiment de connexió i EOF. El cicle de vida és:

1. Servidor: crear → bind → listen → accept → rebre/enviar → tancar.
2. Client: crear → connect → enviar/rebre → tancar.
3. Tots dos costats usen timeouts i context managers perquè els recursos també es tanquin quan hi ha una fallada.

Prediu quin terminal espera i executa:

```text illustrative
# Terminal 1
python -B chapter-23-network-programming/examples/telemetry/echo.py server --port 65432

# Terminal 2, abans de trenta segons
python -B chapter-23-network-programming/examples/telemetry/echo.py client --port 65432 --text "hello, network"
```

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/echo.py check=network:network-suite -->
```python source-ref
with socket.create_connection(("127.0.0.1", port), timeout=30.0) as connection:
    connection.sendall(text.encode("utf-8"))
```

Observa el text retornat i el final dels processos. Un `recv()` buit significa EOF. `sendall()` envia tots els bytes o falla, però no crea fronteres de missatge.

**Exercici:** envia `å` a `--text`. **TODO:** prediu-ne els bytes. **Pista:** el client uneix chunks abans de descodificar. **Èxit:** torna el mateix text i tots dos acaben. La solució evita descodificar un chunk parcial.

**Error comú:** començar pel client produeix `ConnectionRefusedError`. Inicia el listener, comprova el port i reintenta. Un timeout significa falta de progrés: informa i neteja, sense bucles infinits.

### Checkpoint essencial

Explica bytes, adreça davant port i cicle TCP, i completa l'eco loopback. Aquest eco acotat ja és un producte útil. Ara hi afegirem fronteres i validació.

## Ruta intermèdia — dissenyar un contracte real

### 4. TCP no és una cua de missatges: framing

Un `sendall()` pot arribar en diversos `recv()` i diversos enviaments poden arribar junts. `json.loads(connection.recv(4096))` falla amb JSON fragmentat o coalescit.

Fem servir JSON delimitat per línies (**NDJSON**): un objecte UTF-8 i `\n`. `NDJSONDecoder` conserva un buffer incremental, lliura cada línia completa i reté el sufix incomplet. Accepta 65.536 bytes abans del salt; el byte 65.537 sense delimitador falla de manera tancada.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/protocol.py check=network:network-suite -->
```python source-ref
messages = decoder.feed(chunk)  # zero, un o diversos objectes complets
```

| Camp | Valor acceptat | Rebuig |
|---|---|---|
| `version` | enter `1`, mai `bool` | altra versió → `unsupported_version` |
| `type` | string `reading` | altre tipus → `invalid_message` |
| `sensor_id` | 1–64 ASCII, `[A-Za-z0-9][A-Za-z0-9._-]{0,63}` | invàlid → `invalid_message` |
| `sequence` | enter no booleà `0..2**31-1` | duplicat/retrocés → `out_of_order` |
| `value` | número finit no booleà `-1_000_000..1_000_000` | tipus/rang → `invalid_message` |

Calen exactament aquests cinc camps. Una acceptació respon:

```json illustrative
{"version":1,"type":"ack","sensor_id":"lab.temperature","sequence":7,"status":"accepted"}
```

Els errors només contenen `version`, `type`, `code` estable i `message` acotat; mai l'entrada completa. Cada connexió manté com a màxim 64 sensors i només les 256 lectures acceptades més recents. El sensor 65 retorna `resource_limit` sense expulsar estat. Quan l'historial arriba al límit es descarta l'observació més antiga, però la seqüència continua correcta. Validar abans de mutar fa que cada rebuig sigui transaccional.

#### Exercici: qüestiona supòsits, no sistemes

Divideix un frame vàlid en tres parts i uneix dos frames en un chunk. **TODO:** comprova zero/un/dos objectes. **Pista:** `encode_frame()` i slices. **Èxit:** ordre conservat i buffer final zero.

Canvia `sequence=True`, afegeix un camp, usa `1_000_001`, duplica seqüència i prova el sensor 65. Prediu el codi. `test_protocol.py` explica la solució i usa snapshots per provar que el rebuig no muta estat.

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -p test_protocol.py -v
```

UTF-8/JSON invàlid, EOF parcial i framing insegur tanquen perquè no és fiable resincronitzar. Un objecte ben delimitat amb schema erroni pot rebre error i continuar.

### 5. Comparar datagrames UDP

UDP conserva fronteres de datagrama, però no promet lliurament, unicitat ni ordre. No té connexió ni EOF com TCP. Tria'l només si l'aplicació tolera o repara això i manté missatges petits.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/udp_demo.py check=network:network-suite -->
```python source-ref
sender.sendto(message, receiver_address)
data, sender_address = receiver.recvfrom(1024)
```

```text illustrative
python -B chapter-23-network-programming/examples/telemetry/udp_demo.py
```

El happy path imprimeix `received:temperature=21.5`; l'edge case és timeout. Una xarxa real pot perdre, duplicar o reordenar. La balisa UDP no promet el contracte fiable de sequence/ack.

**Decisió guiada:** transport per a un fitxer i per a una posició de joc reemplaçable. **Pista:** han d'arribar tots els bytes en ordre? Solució: TCP per al fitxer; UDP pot servir per updates reemplaçables si el joc gestiona pèrdua i mida.

### 6. Robustesa, logs i proves deterministes

Acota temps, bytes, clients, sensors, historial retingut i sortida pendent. El selector tanca un peer després d'un segon sense progrés de lectura o escriptura; tots dos hubs conserven com a màxim 256 observacions acceptades per inspecció didàctica. Registra peer i categoria, no secrets ni payloads. Reintenta només operacions segures, amb pocs intents i backoff; no reintentem escriptures automàticament.

Les proves usen loopback, ports efímers, events/readiness, timeouts curts i `finally`, sense Internet ni sleeps fixos. Timeout, desconnexió a mig frame i entrada invàlida són rutes recuperables.

**Error comú:** capturar `Exception` i continuar amb estat malmès. Captura l'error concret, registra un missatge acotat, tanca si el framing és insegur i preserva l'estat acceptat.

### Checkpoint intermedi

Tens un nucli seqüencial provat i una comparació UDP. Ja pots explicar fragmentació, coalescing, validació abans de mutació i límits. Ara evitarem que un client lent bloquegi la resta.

## Ruta avançada — concurrència acotada, asyncio i TLS

### 7. Diversos clients amb selectors

El servidor seqüencial espera dins `recv()`. `selectors.DefaultSelector` informa quins sockets estan preparats. La implementació accepta 32 clients, 65.536 bytes incomplets, 64 sensors i 256 lectures recents per connexió; només codifica una resposta pendent i tanca el peer després d'un segon sense progrés.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/selector_hub.py check=network:network-suite -->
```python source-ref
for key, mask in selector.select(timeout):
    # Accepta, llegeix o continua una escriptura parcial només quan està preparat.
    ...
```

Un thread per connexió afegeix cicle de vida i sincronització. `socketserver` empaqueta patrons. Implementem selectors per veure readiness i límits; cap opció és sempre millor.

**Predicció:** A envia mig frame; B n'envia un de complet. B rep primer l'ack. El test ho prova, també amb coalescing. El client 33 es tanca dins el límit.

### 8. Streams asyncio i backpressure

`asyncio.start_server()` crea una tasca per stream. `reader.read()` retorna chunks arbitraris i reutilitza el decoder. Després de `writer.write()`, `await writer.drain()` aplica backpressure i evita sortida il·limitada.

<!-- bookcheck: path=chapter-23-network-programming/examples/telemetry/async_hub.py check=network:network-suite -->
```python source-ref
writer.write(encode_frame(response))
await asyncio.wait_for(writer.drain(), timeout=client_timeout)
```

Error comú pel guionet del directori:

```text illustrative
python -B -m chapter-23-network-programming.examples.telemetry.async_hub
```

Comanda portable correcta:

```text illustrative
cd chapter-23-network-programming/examples
python -B -m telemetry.async_hub
```

La primera és un error explicat, no una instrucció executable. La segona crea port efímer, envia una lectura, mostra l'ack i tanca.

Ordre de shutdown: deixar d'acceptar, tancar writers, esperar `wait_closed()`, cancel·lar handlers i reunir-los. `asyncio.Event` o `KeyboardInterrupt` és multiplataforma; senyals POSIX són opcionals.

**Exercici:** dues `send_readings()` amb `asyncio.gather()`. **TODO:** sensor diferent. **Pista:** una petició pendent fins a la resposta. **Èxit:** dos `accepted` i `hub.close()` sense handlers ni writers. La solució reutilitza el helper provat.

### 9. Extensió opcional: TLS verificat

Transport Layer Security (**TLS**) xifra i verifica el certificat del servidor. No autentica automàticament el client ni autoritza. Tokens, mTLS i polítiques queden fora.

El servidor també aplica el límit de client d'un segon a la negociació i al tancament TLS. Així, un peer TCP que no envia mai ClientHello expira abans que existeixi el handler d'aplicació i no pot bloquejar el tancament indefinidament.

Les claus de `examples/certificates/` són fixtures públics, mai de desplegament. El client només confia en `lab-ca-cert.pem`; `ssl.create_default_context(cafile=...)` manté certificat i hostname. No facis servir `CERT_NONE` ni `check_hostname=False`.

Les proves offline cobreixen èxit amb CA confiable + `localhost`, i fallada tancada per hostname incorrecte, expiració i CA no confiable. El certificat vàlid expira el juliol de 2046 i una prova avisa amb deu anys.

**Recuperació:** revisa hostname, font de confiança, rellotge i renovació. Xifrar sense verificar identitat no demostra qui hi ha a l'altre extrem.

### 10. Extensió opcional: IPv6

Si el probe pot fer bind a `::1`, usa `family=socket.AF_INET6`; si no, registra el skip explicat i usa IPv4. Això només prova capacitat local.

### 11. Executar tota l'evidència

```text illustrative
python -B -m unittest discover -s chapter-23-network-programming/examples/tests -v
python -B tools/validate_book.py --plugin chapter-23-network-programming/tools/bookcheck_plugin.py
```

La primera comanda executa 33 proves estàndard. La segona afegeix checks genèrics i `network:network-suite`. El plugin només valida protocol/lifecycle local; l'eina arrel valida Markdown, enllaços, selectors, accessibilitat estructural, idiomes i higiene.

## Repte final

1. **Fàcil:** tres lectures creixents; TODO: tres acks exactes; pista: comença a zero.
2. **Intermedi:** duplicat entre lectures; prova que `out_of_order` no impedeix una seqüència posterior més gran.
3. **Avançat:** dos clients actius i un aturat a mig frame; prova progrés i shutdown, amb events i `wait_for`, mai esperes endevinades.
4. **Hero:** activa TLS fiable o IPv6 condicional i documenta exactament què has provat.

La solució combina `AsyncTelemetryHub`, `send_readings()`, `ConnectionState` i les proves; no crea un altre protocol. Comprova acks, error, estat, timeout i tancament en loopback.

## Rúbrica d'avaluació

Puntua cada àrea amb 0 (absent), 1 (parcial) o 2 (demostrat):

- **Protocol:** camps exactes, framing, codis d'ack/error i semàntica de seqüència.
- **Límits:** frame, un segon d'inactivitat del selector, 32 clients, 64 sensors, 256 observacions retingudes i una resposta pendent.
- **Recuperació:** entrada mal formada, timeout, EOF i rebuig sense mutació parcial.
- **Concurrència:** un altre client progressa mentre un roman bloquejat.
- **Seguretat:** valors predeterminats de loopback, confiança TLS i verificació del hostname, sense secrets als logs.
- **Verificació:** proves unitàries i d'integració deterministes i evidència local explícita.
- **Neteja i explicació:** no queden recursos orfes i pots explicar cada decisió de disseny.

Dotze punts o més, sense zero en protocol, límits ni neteja, és una finalització sòlida. La puntuació orienta, no etiqueta: millora un comportament observable cada vegada.

## Reflexió final i glossari

Per què TCP necessita framing? Per què validem abans de mutar? Per què `drain()` i timeouts controlen recursos? Separa allò provat localment dels problemes de desplegament no verificats.

- **Backpressure:** frenar el productor quan consumidor o buffer no segueixen.
- **EOF:** final del stream sortint del peer, indicat per lectura TCP buida.
- **Port efímer:** port lliure triat pel sistema operatiu.
- **Framing:** regles per recuperar missatges d'un stream de bytes.
- **Loopback:** camí privat d'un host cap a si mateix.
- **NDJSON:** un valor JSON per frame delimitat per salt de línia.
- **TLS:** transport xifrat amb verificació d'identitat per certificat.

Has passat d'enviar text a definir, acotar, observar, provar i tancar cada conversa. Aquesta disciplina serveix per HTTP, brokers, bases de dades i altres sistemes connectats.
