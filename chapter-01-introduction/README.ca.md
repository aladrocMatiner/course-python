# Capítol 1 · Introducció i entorn

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Abans d’escriure codi, prepararem el teu “taller” de Python: instal·lar un Python modern, assegurar-nos que `pip` funciona i aprendre el cicle complet editar → desar → executar → diagnosticar → reparar. L’objectiu és molt simple: quan executis `python --version`, l’ordinador respondrà, i quan executis el primer programa desat sabràs exactament quin fitxer ha obert Python i com recuperar-te del primer traceback.

## Ordre pedagògic
1. **Instal·lar Python** i comprovar que el comandament funciona.
2. **Comprovar `pip`** per poder instal·lar llibreries quan les necessitem.
3. **Entorns virtuals**: crear una “capseta” (`.venv`) per a cada projecte.
4. **Nivell extra**: usar `asdf` si vols un entorn súper professional.
5. **Cicle del primer programa**: crear una carpeta pròpia, desar `hello.py`, executar-lo, llegir un error esperat, reparar-lo i tornar-lo a executar.

## Objectius d’aprenentatge
- Verificar que Python està instal·lat i entendre què significa la versió.
- Assegurar que `pip` funciona i actualitzar-lo.
- Crear i activar un entorn virtual (`venv`) per a un projecte.
- Evitar els errors típics del “a la meva màquina funciona”.
- Distingir l’editor, un fitxer `.py` desat, el shell, l’intèrpret seleccionat, la sortida estàndard i el REPL interactiu.
- Executar un fitxer des del directori de treball correcte i usar les parts estables d’un traceback per reparar un `NameError`.

## Prerequisits
- No cal tenir coneixements previs de Python.
- Necessites un terminal i permís per instal·lar programari al teu ordinador. En un equip administrat per l'escola o la feina, demana ajuda a la persona responsable en lloc d'evitar les restriccions.
- Mantén aquest capítol obert en una altra pestanya o dispositiu per poder llegir la recuperació si falla una ordre.
- **Ruta essencial de preparació i primer programa · 60–90 min:** completa les seccions 1, 2, 4 i 5 i els dos checkpoints. Resultat: una carpeta d’aprenentatge local i d’un sol ús amb un `hello.py` reparat que imprimeix una línia exacta. Pots aturar-te després del checkpoint del primer programa i tornar més endavant a les eines d’entorn opcionals.
- **Preparació professional opcional · 30–60 min:** crea `.venv` i, només si necessites diverses versions de l’intèrpret, segueix la ruta d’`asdf`. Ni `asdf` ni cap botó d’execució específic de l’editor són prerequisits del capítol 2.

## Predicció abans de preparar l'entorn
Abans d'executar res, anota quina ordre creus que inicia Python al teu sistema: `python`, `python3` o `py`. Després compararàs aquesta predicció amb l'ordre que respon i amb la ruta de l'executable que mostra Python.

## Per què importa
Si l’entorn no està bé, passa una cosa frustrant: copies un exemple, l’executes… i surt un error que no és “culpa teva”, és de l’ordinador. Aquest capítol evita això. Un cop tot està llest, la resta del curs es torna divertit.

### Mini aventura
El teu ordinador és com una bicicleta nova: abans de fer una ruta llarga, ajustes el seient, infles les rodes i comproves els frens. Aquí fem el mateix: ho deixem tot preparat perquè el viatge sigui segur.

### El nostre “repartiment” (opcional i divertit)
Al llarg del llibre veuràs **Noor**, **Frej** i **Taha** com a noms d’exemple dins el codi. Són només noms de mostra: pots canviar-los pel teu, el dels teus amics o el dels teus personatges preferits.

---

## 1. Instal·lar Python (recomanat v3.11+)

### Windows
1. Visita [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) i descarrega l’instal·lador oficial (`python-3.x.x-amd64.exe`).
2. Durant la instal·lació marca **“Add python.exe to PATH”** per evitar configuracions manuals.
3. Completa l’instal·lador i valida:
   ```powershell illustrative
   python --version
   pip --version
   ```
4. Alternativa automatitzada (Windows 11+):
   ```powershell illustrative
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Descarrega el paquet `.pkg` des de [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Executa l’instal·lador i accepta els valors per defecte (instal·la a `/Library/Frameworks/Python.framework`).
3. Verifica:
   ```bash illustrative
   python3 --version
   pip3 --version
   ```
4. Alternativa amb Homebrew:
   ```bash illustrative
   brew update
   brew install python@3.11
   python3.11 --version
   python3.11 -m pip --version
   ```
   No escriguis `/opt/homebrew` de manera fixa al perfil: Homebrew usa prefixos diferents a Apple Silicon i Intel. Si no es troba `python3.11`, executa `brew info python@3.11` i segueix la indicació de la teva instal·lació.

### Linux (Debian/Ubuntu)
```bash illustrative
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```
Si la teva distribució ofereix una versió anterior a 3.11, no afegeixis un repositori de tercers sense revisar només per seguir aquest capítol. Usa la documentació oficial de la distribució o la ruta opcional amb `asdf` de més avall.

### Linux (Fedora/CentOS/RHEL)
```bash illustrative
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. Assegurar que `pip` estigui disponible
- Primer comprova el `pip` associat a l'intèrpret que faràs servir:
  ```bash illustrative
  python3 -m pip --version
  ```
- `ensurepip` és un mòdul opcional de CPython. Si has instal·lat Python des de `python.org` i el mòdul existeix, pot inicialitzar `pip` sense descarregar-lo:
  ```bash illustrative
  python3 -m ensurepip --upgrade
  ```
- Si apareix `No module named ensurepip`, usa l'instal·lador oficial o el gestor de paquets del sistema (`python3-pip` a les famílies Debian/Fedora); no copiïs un script d'arrencada aleatori.
- Actualitza `pip` només després d'activar l'entorn virtual del projecte:
  ```bash illustrative
  python -m pip install --upgrade pip
  ```

---

## 3. Gestionar múltiples versions amb `asdf` (opcional però professional)
`asdf` permet instal·lar i canviar versions de Python (i d’altres eines) per projecte, garantint entorns coherents.

Aquesta ruta és opcional; el checkpoint essencial no la necessita. Instal·la la versió actual d'`asdf` amb la [guia oficial d'inici](https://asdf-vm.com/guide/getting-started.html), que cobreix el teu sistema i arquitectura. Les ordres següents usen la interfície executable actual; les instruccions antigues amb `asdf.sh` i `asdf global` ja no s'apliquen.

1. Verifica la instal·lació:
   ```bash illustrative
   asdf --version
   ```
2. Afegeix el plugin comunitari de Python després de revisar la font mostrada per l'índex oficial. Si `python` ja apareix a `asdf plugin list`, omet aquesta ordre:
   ```bash illustrative
   asdf plugin add python
   ```
3. Instal·la l'últim pedaç estable de 3.11 i escriu l'elecció resolta al `.tool-versions` del projecte:
   ```bash illustrative
   asdf install python latest:3.11
   asdf set python latest:3.11
   ```
4. Verifica:
   ```bash illustrative
   python --version
   python -m pip --version
   ```

Aquestes instruccions sensibles a versions s'han contrastat amb la documentació oficial de Python, Homebrew i `asdf` el 2026-07-13.

Beneficis:
- Cada repositori pot definir `.tool-versions` per fixar versions.
- Evites conflictes entre projectes que necessiten diferents versions.

### Còpia i recuperació per a canvis opcionals del shell
La ruta essencial anterior no exigeix editar el fitxer d'inici. Si la guia oficial d'una eina opcional et demana canviar `~/.zshrc` o `~/.bashrc`, copia'l primer, per exemple amb `cp "$HOME/.zshrc" "$HOME/.zshrc.python-course.bak"`. Afegeix només la línia documentada. Si un shell nou deixa de funcionar, elimina aquella línia des del terminal antic o restaura immediatament la còpia. No restauris una còpia antiga després de fer altres canvis posteriors.

---

## 4. Bones pràctiques inicials
- **Entorns virtuals**: usa `python -m venv .venv` i activa amb `source .venv/bin/activate` (`.\.venv\Scripts\Activate.ps1` a Windows PowerShell).
- **Permisos**: evita `sudo pip install`; usa entorns virtuals o `pipx`.
- **Verificació**: després d’instal·lar, executa `python -m pip list` per assegurar que `pip` respon sense errors.

---

## 5. D’una carpeta al teu primer programa

Aquest és el petit cicle que repetiràs al llarg del llibre:

1. Un **editor** modifica text en un fitxer de codi font. L’editor no demostra que el programa funcioni.
2. **Desa** el fitxer com a `hello.py`; comprova que el nom no acabi amb un segon sufix ocult com ara `.txt`.
3. Un **shell** executa ordres al directori de treball actual. Obre un terminal a la carpeta d’aprenentatge o canvia-hi explícitament.
4. L’**intèrpret de Python** seleccionat obre `hello.py` i l’executa.
5. `print` envia text a la **sortida estàndard**, que el terminal mostra.

L’indicador interactiu marcat amb `>>>` és el **REPL**. Accepta expressions de Python d’una en una. `python hello.py` és una ordre del shell; per tant, surt del REPL amb `exit()` abans d’escriure-la. En aquesta secció, substitueix `python` per l’ordre que abans t’ha funcionat (`python3` o `py`) quan calgui, i mantén-la de manera coherent.

### Prepara un directori de treball propi

Usa una carpeta que sigui teva, no un directori del sistema ni de la instal·lació de Python. Aquestes ordres són exemples; tria el bloc del teu shell.

```bash illustrative
# macOS/Linux: les cometes preserven una ruta amb espais
mkdir -p "$HOME/Python Course/chapter-01"
cd "$HOME/Python Course/chapter-01"
```

```powershell illustrative
# Windows PowerShell: les cometes preserven els espais
New-Item -ItemType Directory -Force "$HOME\Python Course\chapter-01"
Set-Location "$HOME\Python Course\chapter-01"
```

Normalment, l’indicador del shell canvia després de `cd` o `Set-Location`. Si uses l’acció “Obre una carpeta” de l’editor, obre aquest mateix directori. No cal canviar el nom d’una carpeta personal perquè contingui espais.

### Prediu, desa i executa

Abans d’executar-lo, prediu l’única línia que imprimirà el fitxer. Crea `hello.py` a l’editor amb exactament aquest contingut. L’observació correcta associada al bloc executable apareix just després:

```python runnable
print("Hello, Python!")
```
```text output
Hello, Python!
```

Desa’l i escriu això al **shell**, no dins del fitxer ni després de `>>>`:

```bash illustrative
python hello.py
```

Si Python diu que no pot obrir `hello.py`, el fet estable és que no ha trobat la ruta demanada des d’aquest directori de treball. Comprova la carpeta actual, l’ortografia, el sufix `.py` i si l’editor ha desat el fitxer. No reinstal·lis Python, no usis privilegis d’administració ni moguis l’exercici a un directori del sistema.

### Primer traceback deliberat i recuperació

Ara canvia només `print` per `pritn`, desa el fitxer i prediu què passarà. Aquest bloc ha de fallar:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
pritn("Hello, Python!")
```

Un traceback pot contenir text que varia entre versions. Llegeix-ne les pistes estables de baix cap amunt:

- la categoria final de l’excepció és `NameError`;
- el missatge final identifica el nom desconegut `pritn`;
- la ruta i la línia indicades apunten al fitxer desat.

Repara només l’ortografia, torna a desar i executa de nou:

```python runnable
print("Hello, Python!")
```

Has de tornar a observar `Hello, Python!`. L’execució correcta completa la recuperació; llegir l’error sense reparar-lo no la completa.

### TODO guiat i pista

```python todo
# hello.py
# TODO 1: escriu una crida a print amb el text exacte Hello, Python!
# TODO 2: desa el fitxer i executa'l des del seu directori.
# TODO 3: escriu pritn, observa NameError, repara-ho, desa i torna a executar.
```

**Pista:** mantén visibles l’editor, el terminal i el nom del fitxer. Després de cada canvi, pregunta’t: «Ho he desat? Quin directori usa el shell? Quina ordre d’intèrpret estic executant?»

Aquest és un punt segur per aturar-te. No calen variables, funcions, condicionals, gestors d’excepcions, paquets, frameworks de proves ni botons especials de l’editor.

---

## Exercicis guiats (amb TODOs)
1. **1-1 · Comprovar Python**
   ```bash todo
   # TODO: executa un d’aquests comandaments i apunta la versió que et surt
   python --version
   python3 --version
   ```
   *Pista*: a Windows sol ser `python`; a macOS/Linux sovint és `python3`.

2. **1-2 · Crear la teva primera “capseta” (.venv)**
   ```bash todo
   # TODO 1: crea l’entorn virtual
   python -m venv .venv
   # TODO 2: activa’l (tria el comandament del teu sistema)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\.venv\Scripts\Activate.ps1
   # TODO 3: verify which Python and pip the environment uses
   python -c "import sys; print(sys.executable)"
   python -m pip --version
   ```

3. **1-3 · Hola, terminal**
   ```bash todo
   # TODO: completa el cicle desar/executar/error/reparació de la secció 5 i torna a executar
   python hello.py
   ```
   *Pista*: aquesta ordre va al shell quan el shell és a la carpeta que conté `hello.py`.

---

## Errors comuns
- Instal·lar Python però no marcar “Add python.exe to PATH” (Windows) ⇒ no es troba `python`.
- Usar el `pip` d’un Python diferent del que executes ⇒ instal·les “a un altre lloc” sense voler.
- Oblidar activar `.venv` ⇒ el projecte usa dependències equivocades.
- Usar `sudo pip install` ⇒ pots trencar el sistema (millor `.venv`).
- Escriure `python hello.py` després de l’indicador `>>>` ⇒ surt del REPL amb `exit()` i executa l’ordre al shell.
- Executar des d’una altra carpeta o desar `hello.py.txt` ⇒ inspecciona el directori actual i el nom complet abans de modificar la instal·lació de Python.
- Editar sense desar ⇒ l’intèrpret executa correctament el contingut antic que hi ha desat; desa i torna a executar.

---

## Explicació de solucions
- Si `python` no existeix: a Windows revisa la casella de PATH o reinstal·la; a macOS/Linux prova `python3`.
- Per evitar el “pip equivocat”: usa sempre `python -m pip ...` (així `pip` queda lligat a aquell Python).
- Si `venv` no s’activa: revisa que siguis a la carpeta correcta i que existeixi `.venv/`.
- Per a `NameError: ... 'pritn' ...`: usa el fitxer i la línia indicats, corregeix `pritn` per `print`, desa i torna a executar fins que aparegui la línia correcta exacta.
- Si Python no pot obrir `hello.py`: torna a la teva carpeta d’aprenentatge i comprova el nom complet. Posar una ruta entre cometes preserva els espais; eliminar-los no és la reparació.

---

## Resum
Ara tens Python i `pip` funcionant, saps crear un entorn virtual i pots portar un programa desat a través d’un cicle complet de fallada i recuperació. També entens per què no convé barrejar dependències entre projectes.

## Checkpoint i autoavaluació

### Checkpoint del primer programa

En una carpeta pròpia, crea `hello.py`, prediu-ne la sortida, desa’l i executa’l amb l’ordre d’intèrpret que has registrat. Després introdueix `pritn`, identifica el fitxer font, la línia, `NameError` i el nom mal escrit, corregeix-lo, desa i torna a executar. La sortida estàndard final ha de ser exactament `Hello, Python!` seguida d’un salt de línia.

Suma un punt per cada criteri:

- **Correcció:** el fitxer reparat imprimeix la línia exacta esperada.
- **Claredat:** pots distingir editor, fitxer font, ordre del shell, intèrpret, REPL i sortida.
- **Recuperació:** uses les pistes estables del traceback per reparar `pritn` sense reinstal·lar res ni elevar privilegis.
- **Verificació:** deses i observes l’execució correcta des del directori previst.
- **Explicació:** pots explicar per què un canvi no desat o un directori de treball equivocat canvia allò que Python veu.

Un 5/5 demostra el resultat del primer programa. Si falla un criteri, repeteix només el cicle desar/executar/reparar; les eines de preparació opcionals no són necessàries.

### Checkpoint de l’entorn

Dins de `.venv` activat, confirma que `python --version`, `python -c "import sys; print(sys.executable)"` i `python -m pip --version` responen. La ruta de l'executable ha d'apuntar dins de `.venv`.

Suma un punt per cada criteri:
- **Correcció:** Python és 3.11 o posterior i les tres comprovacions passen.
- **Claredat:** la teva nota breu registra l'ordre i la ruta de l'executable que has usat realment.
- **Recuperació:** saps executar `deactivate` i desfer qualsevol edició opcional del shell.
- **Verificació:** després de reactivar `.venv`, la ruta continua apuntant dins de l'entorn.
- **Explicació:** pots explicar amb paraules teves per què `python -m pip` i un entorn virtual eviten barrejar instal·lacions.

Estàs preparat per al capítol 2 amb 5/5. Si falla un criteri, usa les solucions anteriors i repeteix només aquella comprovació.

## Reflexió final
Si has arribat fins aquí, ja has fet una cosa molt important: convertir el teu ordinador en un lloc fiable per aprendre i recuperar-te del primer error intencionat. Quina pista t’ha ajudat més: el nom del fitxer, la línia, la categoria de l’excepció o el nom desconegut? Al capítol 2 començarem a programar de debò amb variables i tipus simples.
