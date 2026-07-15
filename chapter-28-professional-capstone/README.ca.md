# Capítol 28 · Projecte final professional: un gestor de comandes en quatre etapes

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem

Faràs créixer un únic gestor de comandes local en lloc de començar quatre
projectes finals inconnexos. L'etapa de fonaments combina valors immutables,
classes i funcions en memòria. L'etapa pràctica manté el mateix domini i hi
afegeix SQLite, una interfície de línia d'ordres (CLI), configuració, registre
d'esdeveniments i proves. Una etapa opcional de sistemes exposa el mateix
servei mitjançant un adaptador loopback acotat. Una darrera etapa heroica
opcional verifica una distribució de fonts i una wheel sense publicar-ne cap.

Tots els exemples usen identificadors ficticis com `ORD-001` i etiquetes
d'article com `widget`. No els substitueixis per informació real de clients,
adreces, pagaments, credencials o producció.

## Objectius d'aprenentatge

En acabar les etapes que seleccionis, podràs:

- modelar un `Order` immutable i acotat, i explicar cada transició acceptada;
- separar les responsabilitats del domini, el servei, el repositori, la CLI i
  la xarxa opcional;
- conservar l'estat anterior després d'errors de validació, duplicació,
  transició, bloqueig o base de dades;
- operar una CLI recolzada per SQLite amb configuració explícita, sortida
  estable, codis de sortida significatius i registres respectuosos amb la
  privacitat;
- verificar comportaments normals, límit, invàlids i de recuperació a la
  frontera responsable;
- executar un laboratori loopback opcional amb límits explícits de bytes,
  peticions, concurrència i temps, i una aturada determinista; i
- distingir l'evidència de l'arbre de fonts de la d'un artefacte construït,
  inspeccionat i instal·lat en net, sense pujar-lo enlloc.

## Prerequisits i itineraris amb punts de parada independents

El número del catàleg no converteix automàticament els capítols 23–27 en
prerequisits. Entra només a l'etapa per a la qual compleixis el punt de control
indicat.

### Itinerari de fonaments

- **Entrada:** el [punt de control de classes del capítol 12](../chapter-12-oop/README.ca.md#punt-de-control-i-rúbrica)
  i el seu [exercici de classe de dades immutable](../chapter-12-oop/README.ca.md#exercicis-guiats-amb-todos),
  a més de les funcions, els condicionals, els bucles i les col·leccions dels
  capítols 3–11.
- **Temps:** 2–3 sessions de 50–75 minuts.
- **Resultat:** un servei en memòria provat que crea, llista i fa avançar
  comandes sintètiques immutables.
- **Sortida:** els cinc elements de la rúbrica de fonaments passen.
- **Parada segura:** conserva l'artefacte en memòria; la persistència, les
  xarxes i l'empaquetament no són obligatoris.

### Itinerari pràctic

- **Entrada:** la sortida de fonaments més els capítols
  [13](../chapter-13-files/README.ca.md#punt-de-control-i-rúbrica) a
  [18](../chapter-18-testing/README.ca.md#punt-de-control-i-rúbrica). Completa
  el [punt de control de l'apèndix de CLI](../appendix-cli-parser/README.ca.md#punt-de-control-i-rúbrica)
  abans d'implementar l'adaptador d'ordres, i completa el
  [punt de control de registre del capítol 20](../chapter-20-logging/README.ca.md#punt-de-control-i-rúbrica)
  abans del subpunt de control sobre privacitat del registre; així, el registre
  no queda amagat com un concepte nou.
- **Temps:** 4–6 sessions de 50–80 minuts.
- **Resultat:** una CLI transaccional amb SQLite, configuració explícita,
  esdeveniments respectuosos amb la privacitat, evidència de subprocessos i
  recuperació.
- **Sortida:** la suite de la biblioteca estàndard passa i l'estudiant pot
  explicar una reversió (rollback) i la regla de precedència de la CLI.
- **Parada segura:** aquest és un projecte final pràctic complet. El servidor i
  la construcció del paquet són opcionals.

### Itinerari opcional de sistemes

- **Entrada:** la sortida pràctica, el
  [punt de control d'asyncio del capítol 21](../chapter-21-async/README.ca.md#punt-de-control-i-rúbrica)
  i la [rúbrica d'avaluació de xarxes del capítol 23](../chapter-23-network-programming/README.ca.md#rúbrica-davaluació).
- **Temps:** 2–3 sessions de 50–75 minuts.
- **Resultat:** un servei JSON delimitat per salts de línia, provat a
  `127.0.0.1` i en un port assignat pel sistema operatiu, amb recuperació de
  capacitat i aturada neta.
- **Sortida:** les vuit proves de loopback passen i es pot explicar cada límit
  declarat.
- **Parada segura:** no s'afirma cap exposició pública, TLS, autenticació o
  desplegament.

### Itinerari heroic opcional d'empaquetament

- **Entrada:** la sortida pràctica més les lliçons de paquets i entorns del
  [capítol 15](../chapter-15-modulos/README.ca.md#punt-de-control-i-rúbrica) i
  del [capítol 16](../chapter-16-entornos/README.ca.md#punt-de-control-i-rúbrica).
- **Temps:** 2–3 sessions de 50–80 minuts després d'haver proveït
  deliberadament les entrades de construcció exactes.
- **Resultat:** evidència local de la seqüència sdist → wheel → instal·lació
  neta des d'un directori de treball extern.
- **Sortida:** totes les fases del verificador passen i l'estudiant pot indicar
  quin sistema amfitrió s'ha provat realment.
- **Parada segura:** cap pujada, signatura, attestació, token ni mutació d'un
  índex de paquets pertany a aquest capítol.

## Arquitectura expressada amb paraules

La CLI i l'adaptador loopback opcional tradueixen l'entrada externa. Tots dos
criden `OrderService`. El servei crea valors `Order` i demana a un
`OrderRepository` que els emmagatzemi o els faci avançar.
`InMemoryOrderRepository` i `SQLiteOrderRepository` implementen les mateixes
operacions. SQLite és, doncs, un detall de persistència substituïble, no un
segon conjunt de regles de negoci.

La seqüència de control és:

1. un adaptador analitza i acota l'entrada;
2. el servei construeix o sol·licita una operació de domini;
3. la comanda immutable valida el domini exacte;
4. el repositori seleccionat confirma el canvi complet o conserva l'estat
   anterior;
5. l'adaptador emet una sortida acotada o una categoria d'error estable.

Aquesta descripció numerada és l'equivalent textual complet d'un diagrama
d'arquitectura; cap significat depèn del color, les fletxes o la posició a la
pantalla.

## Codi complementari i directori de treball de verificació

L'autoritat executable és
`chapter-28-professional-capstone/examples/order-tracker/`. Executa la suite
completa de la biblioteca estàndard des de l'arrel del repositori:

```bash illustrative
python -B -m unittest discover \
  -s chapter-28-professional-capstone/examples/order-tracker/tests \
  -t chapter-28-professional-capstone/examples/order-tracker \
  -p 'test_*.py'
```

Aquesta ordre exercita el domini, tots dos repositoris, el servei, els
subprocessos de la CLI, la privacitat del registre, el cicle de vida de
loopback, les metadades, la comprovació prèvia d'artefactes i els casos
d'inspecció d'arxius. Usa directoris temporals, dades falses, ports efímers,
sortida de processos fills acotada i temps d'espera acotats.

---

## Etapa 1 · Fonaments: domini immutable i servei en memòria

### Objectius i context dels fonaments

Un gestor de comandes sembla senzill fins que un duplicat sobreescriu una
comanda anterior o una comanda enviada retrocedeix. L'etapa de fonaments fa
observables aquestes regles abans que cap base de dades o adaptador afegeixi
càrrega cognitiva.

Aprendràs a:

- crear una comanda immutable en estat `pending`;
- permetre només `pending → packed → shipped`;
- acceptar els límits inclusius exactes de text i quantitat;
- llistar per `order_id` en lloc de dependre accidentalment de l'ordre
  d'inserció; i
- demostrar que cada operació rebutjada deixa intacte l'estat anterior.

### Prediu el cicle de vida

Abans de llegir la implementació, prediu aquestes observacions:

1. Quins estats resulten de dues crides a `advance("ORD-001")`?
2. Què hauria de fer una tercera crida?
3. Si una segona creació usa `ORD-001` amb un article diferent, quina comanda
   s'ha de conservar?
4. S'ha d'acceptar `True` com a quantitat `1`?

Escriu l'estat previst o la categoria d'excepció, no un traceback complet.

### Teoria mínima: valor, servei i repositori

`Order` és una classe de dades congelada, d'acord amb l'exercici de classe de
dades immutable del capítol 12. Una transició retorna una instantània nova; no
edita el valor anterior. `OrderService` coordina el cas d'ús. Un petit contracte
d'herència defineix les cinc operacions del repositori, i
`InMemoryOrderRepository` les implementa amb un diccionari que es retorna amb
els identificadors ordenats. Aquesta etapa no requereix cap concepte de
tipatge estructural del capítol 27.

Els errors estables del domini són:

- `OrderValidationError` per a valors acotats invàlids;
- `DuplicateOrderError` per a un identificador existent;
- `UnknownOrderError` per a un identificador absent;
- `InvalidTransitionError` per fer avançar `shipped`; i
- `RepositoryError` per a errors de persistència o de cicle de vida.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/domain.py check=learning:contract -->
```python source-ref
pending = Order("ORD-001", "widget", 2)
packed = pending.advanced()
assert pending.status == "pending"
assert packed.status == "packed"
```

### Límits del domini

Després d'eliminar els espais dels extrems:

- `order_id` té entre 1 i 32 caràcters;
- `item` té entre 1 i 80 caràcters;
- `quantity` és un `int` integrat exacte entre 1 i 1.000;
- es rebutgen `bool` i les subclasses d'`int`; i
- `status` és exactament `pending`, `packed` o `shipped`.

S'accepten els valors 32, 80, 1 i 1.000. El text buit, les longituds 33/81, les
quantitats 0/1.001 i qualsevol booleà es rebutgen abans que canviï l'estat del
repositori.

### TODO guiat de fonaments

Treballa en una còpia d'un sol ús o en un fitxer temporal que importi el codi
complementari:

```python todo
repository = InMemoryOrderRepository()
service = OrderService(repository)

# TODO 1: create ORD-001 for two widgets and record its status.
# TODO 2: advance it twice and record both new statuses.
# TODO 3: try one more advance and record the exception category.
# TODO 4: list again and prove ORD-001 is still shipped.
```

**Pista:** compara una instantània immutable capturada abans de l'operació
rebutjada amb `service.get("ORD-001")` després. No capturis `Exception`; indica
l'error de domini que esperes.

### Evidència correcta, límit, d'error i de recuperació

- **Cas correcte:** `pending`, `packed` i `shipped` apareixen en aquest ordre.
- **Límit:** passen un identificador de longitud 32, un article de longitud 80
  i les quantitats 1/1.000.
- **Error recuperable:** un duplicat provoca `DuplicateOrderError` i conserva
  l'article i la quantitat originals.
- **Recuperació:** reintenta-ho amb un identificador únic; té èxit sense reparar
  l'estat intern del repositori.
- **Error terminal:** fer avançar `shipped` provoca
  `InvalidTransitionError`; tornar-lo a carregar encara retorna `shipped`.

Executa l'evidència específica:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_domain tests.test_service -v
```

### Solució de fonaments explicada

La solució construeix `Order` abans de cridar `repository.add`, de manera que
les dades invàlides no arriben mai a l'emmagatzematge. `advanced()` usa un únic
mapa explícit d'estats següents i retorna un valor congelat nou. El repositori
assigna aquest valor només després que la validació de la transició tingui èxit.
La detecció de duplicats es produeix abans de l'assignació al diccionari. Aquest
ordre converteix la recuperació sense canvis d'estat en una propietat del
disseny, no en un truc de neteja.

### Errors habituals dels fonaments

- Mutar directament `order.status` anul·la les instantànies immutables i falla.
- Tractar `bool` com una quantitat accepta un valor tècnicament semblant a un
  enter, però amb un significat de domini incorrecte.
- Capturar totes les excepcions amaga si ha fallat la validació, la consulta,
  la transició o la persistència.
- Retornar l'ordre d'inserció del diccionari crearia un contracte d'ordre
  accidental; el servei exigeix identificadors ordenats.

### Punt de control i rúbrica de fonaments

Puntua cada element amb un punt:

- **Correcció:** una comanda arriba als tres estats en ordre.
- **Límit:** els límits inclusius de text i quantitat passen i els primers
  valors invàlids fallen.
- **Recuperació:** els errors de duplicació i transició terminal conserven les
  instantànies.
- **Separació:** l'estudiant pot distingir el valor, el servei i el repositori.
- **Explicació:** l'estudiant explica per què una instantània immutable nova
  simplifica el raonament sobre la reversió (rollback).

Cinc punts completen l'etapa de fonaments. Amb quatre, repeteix només el cas que
falta; per sota de quatre, revisa les proves de límits i conservació d'estat.
Pots aturar-te aquí amb un artefacte en memòria complet i provat.

### Reflexió de fonaments

Quina decisió d'ordre —validar, calcular i després assignar— fa més per protegir
l'estat, i què es trencaria si l'assignació es produís primer?

---

## Etapa 2 · Pràctica: SQLite, CLI, configuració, registre i proves

### Objectius pràctics i predicció

L'etapa pràctica conserva el mateix servei i només en substitueix el repositori.
Abans d'executar-la, prediu:

- quina base de dades preval quan existeixen tant `ORDER_TRACKER_DB` com
  `--database`;
- si l'absència de configuració de base de dades ha de crear `orders.db`
  implícitament;
- què es conserva després que una actualització de SQLite s'interrompi abans
  de confirmar la transacció (commit); i
- quin flux transporta els resultats estables i quin transporta els
  diagnòstics i esdeveniments.

Les respostes són: preval l'argument explícit; no es crea cap fitxer per
defecte; es conserva l'estat prèviament confirmat; stdout transporta els
resultats i stderr, els diagnòstics i els esdeveniments opcionals.

### Frontera de transacció de SQLite

`SQLiteOrderRepository` crea el seu esquema de manera idempotent i obre
connexions de curta durada amb un temps d'espera d'ocupació de 250 ms per
defecte. Les escriptures inicien explícitament una transacció, validen o
llegeixen, apliquen una mutació completa i després confirmen la transacció
(commit). Una excepció de base de dades executa una reversió (rollback) i es
transforma en `RepositoryError` sense exposar SQL, el text de l'article passat
com a paràmetre ni un camí complet.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/repositories.py check=learning:contract -->
```python source-ref
repository = SQLiteOrderRepository(database, busy_timeout_ms=250)
service = OrderService(repository)
service.create("ORD-001", "widget", 2)
```

Les proves de repositori compartides executen el mateix contracte
d'add/get/list/advance contra memòria i SQLite. Un desencadenador (`trigger`)
controlat interromp una actualització; la prova observa `pending` després,
elimina només el seu desencadenador i llavors avança correctament. Una altra
prova manté un bloqueig temporal explícit durant més de 50 ms, observa un error
acotat, l'allibera i ho torna a intentar.

### Contracte de la CLI

L'ordre instal·lada admet:

```bash illustrative
order-tracker --database path/to/disposable/orders.sqlite3 add ORD-001 widget 2
order-tracker --database path/to/disposable/orders.sqlite3 advance ORD-001
order-tracker --database path/to/disposable/orders.sqlite3 list
```

La sortida estable quan hi ha èxit és JSON compacte:

```text illustrative
{"order_id":"ORD-001","status":"pending"}
```

Llistar una comanda pendent produeix:

```text illustrative
{"item":"widget","order_id":"ORD-001","quantity":2,"status":"pending"}
```

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/cli.py check=learning:contract -->
```python source-ref
configured = args.database if args.database is not None else environment.get("ORDER_TRACKER_DB")
```

El codi de sortida forma part de la interfície:

- `0`: l'ordre s'ha completat;
- `1`: el domini o el repositori ha rebutjat l'operació;
- `2`: els arguments o la configuració de la base de dades no es poden usar.

Sense configuració, stderr indica com recuperar-se i no es crea cap base de
dades. Una quantitat no entera a la CLI és un error d'ús (2); un enter fora del
domini és un error de domini (1). Una invocació vàlida posterior contra la
mateixa base de dades seleccionada té èxit.

### Privacitat del registre

`--verbose` afegeix un esdeveniment acotat a stderr. Una creació correcta
presenta aquest aspecte:

```text illustrative
event=add order_id=ORD-LOG outcome=success
```

Els esdeveniments poden contenir la fase, un identificador estable de comanda,
el recompte, el resultat i una categoria estable. Mai no contenen el text de
l'article, un camí complet de la base de dades, valors de l'entorn, SQL amb
dades, secrets ni detalls del traceback d'un error esperat. Stdout es manté
igual perquè els scripts el puguin analitzar.

### TODO pràctic guiat

Afegeix una prova de subprocés, no una crida a un auxiliar privat de la CLI:

```python todo
# TODO 1: invoke the CLI to create ORD-RECOVER in a temporary database.
# TODO 2: invoke the same add again and assert exit 1 plus duplicate-order.
# TODO 3: invoke list and prove the original item/quantity remain.
# TODO 4: retry with ORD-RECOVER-2 and assert exit 0.
```

**Pista:** comprova el codi de retorn, stdout, stderr i l'estat de la base de
dades. Acota el temps d'espera del subprocés i la sortida capturada. Usa només
un `TemporaryDirectory` i valors sintètics.

### Evidència pràctica i solució explicada

Executa:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest \
  tests.test_repository_contract tests.test_cli tests.test_metadata -v
```

La solució explicada invoca `python -m order_tracker` des d'un directori de
treball temporal extern amb només el directori `src` del codi complementari al
camí d'importació usat per les proves de fonts. No evita `argparse`. La mateixa
categoria de domini o repositori que exposa el servei rebutja la inserció
duplicada. Un `list` final demostra que la fila original ha sobreviscut; un
identificador nou demostra la recuperació.

### Errors pràctics habituals

- Triar una base de dades per defecte amagada fa que una ordre innocent modifiqui
  l'arbre de treball.
- Imprimir un camí complet de base de dades o un article als registres
  converteix els diagnòstics en una filtració de dades.
- Provar només `cli.main` pot passar per alt l'anàlisi de l'entrada, els fluxos,
  el codi de sortida i els problemes d'un directori de treball extern.
- Capturar `sqlite3.Error` a la CLI filtra detalls de persistència i duplica la
  responsabilitat del repositori.
- Eliminar una base de dades bloquejada o malmesa com a «recuperació» pot
  destruir dades alienes; corregeix el camí d'un sol ús o allibera només el
  bloqueig que posseeix la teva prova.

### Punt de control pràctic i rúbrica

Puntua cada element amb un punt:

- **Contracte de repositori:** memòria i SQLite produeixen el mateix cicle de
  vida i els mateixos errors observables.
- **Atomicitat:** una actualització controlada que falla conserva la fila
  anterior i una transacció neta posterior té èxit.
- **CLI/configuració:** la precedència, el JSON, la separació de fluxos i els
  codis de sortida 0/1/2 coincideixen amb el contracte.
- **Privacitat del registre:** els esdeveniments contenen la fase i el resultat,
  però cap valor prohibit.
- **Proves/recuperació:** les proves de subprocessos cobreixen els
  comportaments normal, límit, invàlid i de reintent sense deixar residus.
- **Explicació:** l'estudiant pot explicar on es confirma la transacció i per què
  preval `--database`.

L'etapa pràctica es completa amb els sis punts. El treball opcional de sistemes
o empaquetament no pot compensar un zero aquí. Aquest és un punt de parada
professional segur.

### Reflexió pràctica

Per què «el mateix servei, un repositori diferent» és una evidència més sòlida
que escriure des de zero una segona aplicació específica per a SQLite?

---

## Etapa 3 · Extensió opcional de sistemes: adaptador loopback acotat

### Objectiu de sistemes i límits exactes

Aquest adaptador opcional ensenya el cicle de vida, no el desplegament a
Internet. Usa JSON UTF-8 delimitat per salts de línia, una petició per connexió,
`127.0.0.1` i un port assignat pel sistema operatiu.

Els límits per defecte són:

- bytes de petició: 1.024 inclòs el salt de línia;
- bytes de resposta: 4.096 inclòs el salt de línia;
- total de peticions acceptades: 8;
- gestors actius simultanis: 4;
- comandes retornades per una resposta de llista: 20; i
- termini inactiu de lectura o escriptura: 0,5 segons.

La validació del constructor permet mides de petició d'1 a 65.536 bytes, mides
de resposta de 38 a 65.536 bytes, recomptes de peticions o llistes d'1 a 100,
concurrència d'1 a 32 i terminis de 0,05 a 10 segons. El mínim de 38 bytes és
la trama d'error `response-limit` completa, de manera que fins i tot aquest
missatge de recuperació respecta el límit seleccionat. L'adaptador no conserva
cap historial de peticions ni cap cua de sortida no acotada. Una connexió
admesa un cop supera el control de concurrència consumeix una plaça del total
de peticions encara que després la seva trama estigui mal formada o superi el
temps d'espera; un client rebutjat com a `busy` no en consumeix cap.

### Prediu l'emmarcat i la capacitat

Prediu què passa quan un client:

1. envia JSON vàlid per sota de 1.024 bytes;
2. envia 1.025 bytes abans d'un salt de línia;
3. obre l'únic gestor permès i queda aturat;
4. envia UTF-8 o JSON mal format; o
5. demana una novena petició.

Els errors estables són, respectivament: èxit; `request-too-large`; `busy` per
al client concurrent, seguit de recuperació de capacitat;
`malformed-request`; i `request-limit`, seguit d'una aturada neta.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/src/order_tracker/loopback.py check=learning:contract -->
```python source-ref
async with LoopbackOrderServer(service) as server:
    response = await send_request(server.address, {"action": "list"})
```

Una petició vàlida és:

```json illustrative
{"action":"add","order_id":"NET-1","item":"widget","quantity":2}
```

La resposta acotada és:

```json illustrative
{"ok":true,"order":{"item":"widget","order_id":"NET-1","quantity":2,"status":"pending"}}
```

### TODO guiat de sistemes

Amplia la prova temporal, no un servei públic:

```python todo
# TODO 1: start with max_concurrency=1 and an ephemeral port.
# TODO 2: open one client and wait on connection_started without sleeping.
# TODO 3: prove a second client receives busy.
# TODO 4: finish/close the first client, await capacity_available, and retry.
# TODO 5: close the server and assert zero active connections/tasks.
```

**Pista:** la disponibilitat inicial i la recuperació són esdeveniments. Una
espera fixa no pot demostrar-ne cap. Tanca sempre l'escriptor del client en un
bloc `finally`.

### Error, recuperació, cancel·lació i solució

La suite cobreix els límits del constructor, una petició al límit exacte de
bytes, add/list vàlids, entrada mal formada, entrada massa gran, topalls de
llista i resposta, un gestor ocupat, temps d'espera inactiu, esgotament del
total de peticions, cancel·lació d'un gestor aturat, retorn de la capacitat i
aturada del socket d'escolta. El servidor tanca el socket d'escolta, cancel·la
i espera cada gestor que posseeix i després completa `wait_closed()`.
`CancelledError` es torna a propagar després de tancar cada escriptor.

Executa només l'evidència opcional:

```bash illustrative
cd chapter-28-professional-capstone/examples/order-tracker
python -B -m unittest tests.test_loopback -v
```

La solució explicada mai no vincula `0.0.0.0`, mai no tria un port fix, mai no
contacta amb un objectiu públic, mai no desactiva una comprovació de seguretat
i mai no afirma oferir TLS, autenticació o enduriment per a producció. Aplica
els límits de bytes i estat abans de conservar dades i demostra una petició
posterior o una aturada neta després del rebuig.

### Errors habituals de sistemes

- No es garanteix que una escriptura TCP equivalgui a una lectura; el salt de
  línia és la frontera de la trama declarada.
- Una espera fixa no és evidència que el servidor estigui disponible ni que
  s'hagi netejat.
- Loopback elimina l'encaminament públic, no totes les preocupacions de
  seguretat de l'aplicació.
- Cancel·lar sense esperar les tasques pot deixar sockets i avisos.
- Un adaptador opcional no s'ha de convertir en un prerequisit d'importació o
  empaquetament.

### Punt de control i rúbrica de sistemes

Puntua amb un punt cadascun dels elements següents: **enllaç loopback i port
efímer**, **emmarcat i límits de bytes**, **límits de peticions i concurrència**,
**temps d'espera i recuperació de capacitat**, **cancel·lació i aturada** i
**explicació de per què això no és producció**. Els sis punts completen l'etapa
opcional de sistemes. En cas contrari, conserva el resultat de l'etapa pràctica
i informa que l'evidència de sistemes és incompleta.

### Reflexió de sistemes

Quin recurs acota cada nombre i quina asserció demostra que la capacitat torna?

---

## Etapa 4 · Empaquetament heroic opcional: verifica l'artefacte, no la còpia de treball

### Objectiu d'empaquetament i frontera de l'evidència

Que passin les proves executades sobre les fonts aporta evidència de la còpia
de treball (`checkout`). No demostra que una sdist contingui totes les fonts,
que una wheel tingui les metadades correctes, que la instal·lació funcioni ni
que la importació es resolgui fora del repositori. L'etapa heroica prova
aquestes afirmacions per separat.

La distribució és `course-order-tracker`, el paquet d'importació és
`order_tracker`, l'ordre és `order-tracker`, la versió és `1.0.0`,
`Requires-Python >=3.11` i no hi ha dependències en temps d'execució. La seva
wheel declara `py3-none-any`. Aquesta etiqueta és una declaració de
compatibilitat, no una prova per als hosts on no s'ha executat.

### Les entrades de construcció són versions directes fixades, no un lock complet

`requirements-build.txt` registra `build==1.3.0`, `setuptools==80.9.0` i
`wheel==0.45.1` com a versions directes exactes per a aquest flux de treball.
No conté hashes, procedència del resolutor, matriu multiplataforma ni
instantània transitiva de l'índex; per tant, no s'anomena un fitxer lock
complet.

El [registre d'entrades de construcció](examples/order-tracker/BUILD_INPUTS.md)
del codi complementari registra per separat els noms dels fitxers de
distribució seleccionats, els valors SHA-256 observats a PyPI, les metadades de
llicència publicades i les referències primàries dels formats. El verificador comprova els
dos hashes de les wheels de backend fora de línia. Aquesta observació de
procedència encara no és un graf de dependències resolt ni una aprovació humana
de llicència o publicació.

L'adquisició inicial de les eines és un pas de manteniment separat i deliberat
que pot necessitar una xarxa o un índex aprovats. El verificador no l'executa
mai. Abans d'executar l'ordre acceptada, el sistema amfitrió ha de proporcionar grups de
processos POSIX per a la neteja acotada de l'arbre de processos fills,
`build==1.3.0` ja ha de ser importable i `ORDER_TRACKER_WHEELHOUSE` ha
d'identificar un directori fora de línia dedicat que només contingui els
artefactes exactes registrats de setuptools i wheel. Una entrada absent,
addicional o incompatible és un estat de prerequisit no satisfet, no un
resultat aprovat.

<!-- bookcheck: path=chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py check=learning:contract -->
```python source-ref
wheelhouse = require_prerequisites()
verify(wheelhouse)
```

Des de l'arrel del repositori, l'ordre acceptada és:

```bash illustrative
python -B chapter-28-professional-capstone/examples/order-tracker/tools/verify_artifact.py
```

En aquesta còpia de treball, si les eines no s'han proveït, el resultat honest és
diferent de zero i comença així:

```text illustrative
prerequisite missing:
```

Això no és una verificació aprovada de l'artefacte i no invalida l'etapa
pràctica basada en fonts que ja s'ha completat.

### Fases de verificació

El verificador:

1. calcula l'empremta de l'arbre de fonts i l'escaneja;
2. el copia a una arrel de fonts temporal independent;
3. executa construccions PEP 517 aïllades i fora de línia des del wheelhouse
   declarat;
4. inspecciona la sdist exacta i la wheel pura inicial;
5. desempaqueta amb seguretat la sdist en una segona arrel de fonts;
6. reconstrueix una wheel a partir d'aquestes fonts distribuïdes;
7. comprova les metadades, els membres obligatoris, `RECORD`, la llicència,
   l'absència de dependències en temps d'execució i `py3-none-any`;
8. instal·la la wheel reconstruïda exacta amb `--no-index --no-deps` en un
   entorn nou;
9. executa `pip check` i proves ràpides de metadades, importació, domini i CLI
   des d'un directori extern;
10. informa dels noms de fitxer, les observacions SHA-256 i les versions
    executades; i
11. elimina totes les arrels temporals de fonts, sortida, instal·lació, memòria
    cau, base de dades i directori extern, tant en cas d'èxit com d'error.

Rebutja qualsevol membre individual de les fonts o d'un arxiu superior a
2 MiB, una instantània del projecte superior a 8 MiB, un arxiu superior a
12 MiB comprimit o expandit, una sortida combinada de processos fills superior
a 16 KiB, una fase inicial, de reconstrucció o instal·lació superior a
180 segons, o qualsevol altra fase executada com a procés fill superior a
30 segons. Un sistema amfitrió no POSIX informa d'un estat de prerequisit;
aquest curs no el substitueix per una afirmació més feble sobre la neteja dels
processos fills.

SHA-256 demostra quins bytes s'han observat en aquella execució. No és una
afirmació de construcció reproduïble byte per byte.

### TODO guiat d'empaquetament

Abans d'executar res, completa aquest pla d'evidència:

```text todo
TODO 1: name the source input and the two independently built wheels.
TODO 2: predict where order_tracker.__file__ must resolve after clean install.
TODO 3: name the phase that should reject a database or .env inside an archive.
TODO 4: record the exact interpreter/host actually executed.
TODO 5: state why no command in the plan uploads an artifact.
```

**Pista:** «les proves han passat» no és suficient. Registra per separat la
construcció, la inspecció, la reconstrucció, la instal·lació, la importació, el
comportament, la CLI i la neteja. Un prerequisit absent continua absent.

### Error i recuperació d'empaquetament

- Eina frontend o wheelhouse absent: proveeix explícitament les entrades
  exactes; no desactivis l'aïllament ni permetis una alternativa implícita de
  l'índex.
- Membre absent de la sdist: corregeix `MANIFEST.in` o les metadades, descarta
  tots els artefactes temporals i torna a construir des del principi.
- Fuita d'importació de l'arbre de fonts: canvia a l'intèrpret nou i al
  directori de treball extern; no afegeixis la còpia de treball a `PYTHONPATH`.
- Base de dades, memòria cau o credencial prohibida: elimina la causa de les
  fonts i repeteix la inspecció abans de la instal·lació.
- Error de la prova ràpida de la CLI: corregeix el paquet o el punt d'entrada i
  torna a executar totes les fases posteriors, no només l'ordre final.

La verificació s'atura localment. Publicar exigeix una autorització separada,
credencials, revisió, una política de signatura o attestació i controls de
l'índex que aquest capítol no demana ni exercita.

### Errors habituals d'empaquetament

- Anomenar lock universal unes versions directes fixades exagera l'evidència.
- Tractar el nom d'un fitxer wheel com a prova d'execució exagera la
  compatibilitat.
- Instal·lar des de la còpia de treball pot amagar un fitxer de paquet absent.
- Reutilitzar una construcció o memòria cau antiga invalida l'evidència de
  construcció neta.
- Informar que una eina de construcció absent s'ha «omès o aprovat» fabrica un
  èxit.
- Afegir una ordre de pujada amplia l'autoritat més enllà d'aquest projecte
  final.

### Punt de control i rúbrica d'empaquetament

Si selecciones aquesta etapa, puntua amb un punt cadascun dels elements
següents: **construcció aïllada**, **inspecció de la sdist**, **wheel
reconstruïda des de la sdist**, **instal·lació neta i `pip check`**,
**evidència de metadades, importació, domini i CLI des d'un directori extern**,
**registre de resums criptogràfics i cadena d'eines**, **neteja** i **explicació de
l'absència de publicació**. Els vuit punts completen l'etapa heroica. Si algun
no està disponible, informa de la fase exacta no aprovada i conserva l'etapa
pràctica completada de manera independent.

### Reflexió d'empaquetament

Quin defecte poden amagar les proves de fonts però revelar una wheel
reconstruïda des de la sdist?

---

## Avaluació final de les etapes seleccionades

Per a cada etapa seleccionada, cap categoria obligatòria no pot obtenir zero:

- **Correcció del domini:** els valors i les transicions coincideixen amb el
  contracte exacte.
- **Separació de responsabilitats:** els adaptadors no posseeixen les regles de
  domini ni de SQLite.
- **Atomicitat de la persistència:** el rebuig conserva l'estat confirmat.
- **CLI/configuració:** la precedència, el JSON, els fluxos i els codis de
  sortida són estables.
- **Privacitat del registre:** els diagnòstics no revelen l'article, el camí,
  l'entorn, dades SQL, credencials ni el traceback d'un error esperat.
- **Proves i recuperació:** els comportaments normal, límit, invàlid i reparat
  són observables.
- **Cicle de vida de sistemes, si se selecciona:** els límits, la cancel·lació
  i la neteja passen.
- **Evidència de l'artefacte, si se selecciona:** les fases des de les fonts
  fins a la instal·lació passen localment.
- **Explicació:** l'estudiant pot justificar una decisió de disseny i una
  frontera de recuperació.

Els punts opcionals no poden amagar un error de fonaments o de l'etapa
pràctica. Una eina que passa sense cap explicació deixa incompleta aquella
categoria de la rúbrica.

## Traçabilitat i verificació completes

La [traçabilitat del capítol 28](TRACEABILITY.md) relaciona cada funcionalitat
amb l'explicació anterior, la secció per a l'estudiant, el codi complementari,
la prova exacta i l'element de la rúbrica. La
[guia de verificació](examples/order-tracker/README.md) del codi complementari
registra les ordres i la frontera dels prerequisits de l'artefacte.

## Comprovació d'higiene del repositori

Després de la verificació, inspecciona fins i tot els camins ignorats sota el
capítol. No hi ha d'haver cap entorn virtual, `build/`, `dist/`, wheel, sdist,
base de dades SQLite, `*.egg-info`, memòria cau, bytecode, cobertura,
credencial, dades d'estudiants, socket viu ni procés fill. Tot l'estat generat
pertany a arrels temporals.

## Fonts, originalitat i frontera de revisió humana

La prosa del capítol, els escenaris ficticis de comandes, els TODO, les proves i
el codi complementari es van escriure com a material original del curs. El
comportament tècnic s'ha contrastat amb la documentació oficial de Python per a
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
[`sqlite3`](https://docs.python.org/3/library/sqlite3.html),
[`argparse`](https://docs.python.org/3/library/argparse.html) i els
[fluxos d'`asyncio`](https://docs.python.org/3/library/asyncio-stream.html), a
més de les referències d'empaquetament primàries enumerades al registre
d'entrades de construcció del codi complementari. No es presenta cap prosa ni
exercici com a còpia d'aquestes referències.

Aquesta declaració i l'estructura o les proves automatitzades no aproven la
procedència, les obligacions de llicència, la qualitat de la traducció,
l'accessibilitat renderitzada, la bidireccionalitat de l'àrab ni la publicació.
Continuen sent portes explícites per a persones competents.

## Reflexió final

El projecte final queda complet a l'etapa que has seleccionat quan el
comportament, la recuperació, la neteja i la teva explicació coincideixen. Quina
frontera —domini immutable, transacció, adaptador o artefacte— t'ha donat
l'evidència nova més sòlida, i què verificaries després abans d'una publicació
real?
