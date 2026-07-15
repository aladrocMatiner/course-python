# Kapitel 1 · Introduktion och installation

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Det här ska vi bygga

Innan vi skriver kod förbereder vi din Python-verkstad: vi installerar en modern Python-version, kontrollerar att `pip` fungerar och lär oss hela kretsloppet redigera → spara → köra → diagnostisera → reparera. Målet är enkelt: när du kör `python --version` ska datorn svara, och när du kör ditt första sparade program ska du veta exakt vilken fil Python öppnade och hur du återhämtar dig från din första traceback.

## Lärväg

1. **Installera Python** och kontrollera att kommandot fungerar.
2. **Kontrollera `pip`**, så att vi senare kan installera bibliotek.
3. **Virtuella miljöer**: skapa en liten avskild ”låda” (`.venv`) för varje projekt.
4. **Bonusnivå**: använd `asdf` om du vill ha en mer professionell installation.
5. **Det första programmets kretslopp**: skapa en egen mapp, spara `hello.py`, kör filen, läs ett förväntat fel, reparera det och kör igen.

## Lärandemål

- Kontrollera att Python är installerat och förstå vad versionsnumret betyder.
- Se till att `pip` fungerar och uppdatera det.
- Skapa och aktivera en virtuell miljö (`venv`) för ett projekt.
- Undvika det klassiska problemet ”det fungerar på min dator”.
- Skilja mellan redigeraren, en sparad `.py`-fil, skalet, den valda tolken, standardutdata och den interaktiva REPL-miljön.
- Köra en fil från rätt arbetskatalog och använda de stabila delarna av en traceback för att reparera ett `NameError`.

## Förkunskaper

- Du behöver inga tidigare Python-kunskaper.
- Du behöver en terminal och tillåtelse att installera program på din egen dator. På en skola eller arbetsplats med administrerad dator ber du ansvarig person om hjälp i stället för att kringgå begränsningar.
- Ha kapitlet öppet i en annan flik eller enhet så att du kan läsa återställningsstegen om ett kommando misslyckas.
- **Grundläggande installations- och första-programväg · 60–90 min:** slutför avsnitt 1, 2, 4 och 5 samt båda kontrollpunkterna. Resultat: en lokal, tillfällig lärandemapp med en reparerad `hello.py` som skriver ut exakt en rad. Du kan stanna efter kontrollpunkten för det första programmet och återvända till frivilliga miljöverktyg senare.
- **Frivillig professionell installation · 30–60 min:** skapa `.venv` och följ bara `asdf`-vägen om du behöver flera tolkversioner. Varken `asdf` eller en redigerarspecifik körknapp krävs för kapitel 2.

## Förutsäg före installationen

Skriv först vilket kommando du tror startar Python på ditt system: `python`, `python3` eller `py`. Efter installationen jämför du förutsägelsen med kommandot som faktiskt svarar och med sökvägen som Python rapporterar.

## Varför det spelar roll

Om installationen inte stämmer kan något frustrerande hända: du kopierar ett exempel, kör det och får ett fel som inte beror på din kod, utan på datorns miljö. Det här kapitlet förebygger sådana problem. När verkstaden är klar blir resten av kursen betydligt roligare.

### Miniäventyr

Din dator är som en ny cykel. Före en lång tur justerar du sadeln, pumpar däcken och provar bromsarna. Här gör vi motsvarande kontroll så att färden kan börja tryggt.

### Möt våra personer (frivilligt och lekfullt)

I boken dyker **Noor**, **Frej** och **Taha** upp som exempelnamn i kod. De är bara platshållare. Du får gärna ersätta dem med ditt eget namn, dina vänners namn eller favoritfigurer.

---

## 1. Installera Python (v3.11+ rekommenderas)

### Windows

1. Besök [Pythons officiella nedladdningssida för Windows](https://www.python.org/downloads/windows/) och hämta installationsfilen (`python-3.x.x-amd64.exe`).
2. Markera **“Add python.exe to PATH”** under installationen, så slipper du konfigurera sökvägen manuellt senare.
3. Slutför installationen och kontrollera den:

   ```powershell illustrative
   python --version
   pip --version
   ```

4. Automatiserat alternativ för Windows 11 och senare:

   ```powershell illustrative
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS

1. Hämta `.pkg`-filen från [Pythons officiella nedladdningssida för macOS](https://www.python.org/downloads/macos/).
2. Kör installationen och acceptera standardvalen. Python installeras i `/Library/Frameworks/Python.framework`.
3. Kontrollera:

   ```bash illustrative
   python3 --version
   pip3 --version
   ```

4. Alternativ med Homebrew:

   ```bash illustrative
   brew update
   brew install python@3.11
   python3.11 --version
   python3.11 -m pip --version
   ```

   Skriv inte in `/opt/homebrew` permanent i din skalprofil: Homebrew använder olika prefix på Apple Silicon och Intel. Om `python3.11` inte hittas kör du `brew info python@3.11` och följer anvisningen för just din installation.

### Linux (Debian/Ubuntu)

```bash illustrative
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```

Om distributionen erbjuder en version äldre än 3.11 ska du inte lägga till ett ogranskat tredjepartsarkiv bara för att följa kapitlet. Använd distributionens officiella Python-instruktioner eller den frivilliga `asdf`-vägen nedan.

### Linux (Fedora/CentOS/RHEL)

```bash illustrative
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. Kontrollera att `pip` finns

- Kontrollera först det `pip` som hör till tolken du vill använda:

  ```bash illustrative
  python3 -m pip --version
  ```

- `ensurepip` är en valfri CPython-modul. Om du installerade Python från `python.org` och modulen finns kan den starta `pip` utan nedladdning:

  ```bash illustrative
  python3 -m ensurepip --upgrade
  ```

- Om du får `No module named ensurepip` använder du den officiella installeraren eller operativsystemets pakethanterare (`python3-pip` i Debian-/Fedora-familjerna). Kopiera inte ett slumpmässigt bootstrap-skript.
- Uppdatera `pip` först efter att projektets virtuella miljö har aktiverats:

  ```bash illustrative
  python -m pip install --upgrade pip
  ```

---

## 3. Hantera flera versioner med `asdf` (frivilligt men professionellt)

Med `asdf` kan du installera och växla mellan Python-versioner, och även andra verktyg, projekt för projekt. Då förblir miljöerna konsekventa.

Den här vägen är frivillig och behövs inte för den grundläggande kontrollpunkten. Installera aktuell `asdf` med den [officiella startguiden](https://asdf-vm.com/guide/getting-started.html), som behandlar ditt operativsystem och din arkitektur. Kommandona nedan använder det nuvarande körbara gränssnittet; gamla instruktioner med `asdf.sh` och `asdf global` gäller inte.

1. Kontrollera installationen:

   ```bash illustrative
   asdf --version
   ```

2. Lägg till gemenskapens Python-plugin efter att du granskat källan som visas i det officiella pluginindexet. Om `python` redan finns i `asdf plugin list` hoppar du över kommandot:

   ```bash illustrative
   asdf plugin add python
   ```

3. Installera den senaste stabila 3.11-korrigeringen och skriv det upplösta valet till projektets `.tool-versions`:

   ```bash illustrative
   asdf install python latest:3.11
   asdf set python latest:3.11
   ```

4. Kontrollera resultatet:

   ```bash illustrative
   python --version
   python -m pip --version
   ```

De versionskänsliga instruktionerna kontrollerades mot officiell dokumentation för Python, Homebrew och `asdf` 2026-07-13.

Fördelar:

- Varje kodförråd kan använda filen `.tool-versions` för att låsa verktygsversioner.
- Projekt som behöver olika utgåvor krockar inte med varandra.

### Säkerhetskopia och återställning vid frivilliga skaländringar

Grundvägen ovan kräver inte att du redigerar en startfil. Om en officiell guide för ett frivilligt verktyg ber dig ändra `~/.zshrc` eller `~/.bashrc` kopierar du filen först, till exempel med `cp "$HOME/.zshrc" "$HOME/.zshrc.python-course.bak"`. Lägg bara till den dokumenterade raden. Om ett nytt skal slutar fungera tar du bort raden från den gamla terminalen eller återställer kopian direkt. Återställ inte en gammal kopia efter senare, orelaterade ändringar.

---

## 4. Första goda vanor

- **Virtuella miljöer**: kör `python -m venv .venv` och aktivera med `source .venv/bin/activate` (`.\.venv\Scripts\Activate.ps1` i Windows PowerShell).
- **Behörigheter**: undvik `sudo pip install`; använd en virtuell miljö eller `pipx`.
- **Snabb kontroll**: kör `python -m pip list` efter installationen och kontrollera att `pip` svarar utan fel.

---

## 5. Från en mapp till ditt första program

Det här är det lilla kretslopp som du kommer att upprepa genom hela boken:

1. En **redigerare** ändrar text i en källfil. Redigeraren bevisar inte att programmet fungerar.
2. **Spara** filen som `hello.py` och kontrollera att namnet inte slutar med ett dolt extra suffix som `.txt`.
3. Ett **skal** kör kommandon i sin aktuella arbetskatalog. Öppna en terminal i din lärandemapp eller byt uttryckligen till den.
4. Den valda **Python-tolken** öppnar `hello.py` och kör filen.
5. `print` skickar text till **standardutdata**, som visas i terminalen.

Den interaktiva prompten som markeras med `>>>` är en **REPL**. Den tar emot ett Python-uttryck i taget. `python hello.py` är ett skalkommando, så lämna REPL-miljön med `exit()` innan du skriver kommandot. Ersätt vid behov `python` med den fungerande stavning som du antecknade tidigare (`python3` eller `py`) och använd samma stavning konsekvent i det här avsnittet.

### Förbered en arbetskatalog som du äger

Använd en egen mapp, inte en systemkatalog eller Pythons installationskatalog. Kommandona är exempel; välj blocket för ditt skal.

```bash illustrative
# macOS/Linux: quote a path that contains spaces
mkdir -p "$HOME/Python Course/chapter-01"
cd "$HOME/Python Course/chapter-01"
```

```powershell illustrative
# Windows PowerShell: quotes preserve the spaces
New-Item -ItemType Directory -Force "$HOME\Python Course\chapter-01"
Set-Location "$HOME\Python Course\chapter-01"
```

Prompten ändras normalt efter `cd` eller `Set-Location`. Om redigeraren har en åtgärd för att öppna en mapp ska du öppna just den här katalogen. Du behöver inte byta namn på en personlig mapp bara för att sökvägen innehåller mellanslag.

### Förutsäg, spara och kör

Förutsäg före körningen den enda rad som filen ska skriva ut. Skapa `hello.py` i redigeraren med exakt följande innehåll. Den lyckade observation som hör till det körbara blocket visas direkt efter det:

```python runnable
print("Hello, Python!")
```
```text output
Hello, Python!
```

Spara filen och skriv sedan detta i **skalet**, inte inne i filen eller efter `>>>`:

```bash illustrative
python hello.py
```

Om Python säger att `hello.py` inte kan öppnas är det stabila faktumet att den begärda sökvägen inte hittades från den aktuella arbetskatalogen. Kontrollera mappen, stavningen, suffixet `.py` och att redigeraren verkligen har sparat filen. Installera inte om Python, höj inte behörigheterna och flytta inte övningen till en systemkatalog.

### Avsiktlig första traceback och återhämtning

Ändra nu bara `print` till `pritn`, spara och förutsäg vad som händer. Det här blocket ska misslyckas:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
pritn("Hello, Python!")
```

En traceback kan innehålla versionsberoende formuleringar. Läs dess stabila ledtrådar nedifrån och upp:

- den sista undantagskategorin är `NameError`;
- det sista meddelandet pekar ut det okända namnet `pritn`; och
- den rapporterade sökvägen och raden pekar tillbaka på den sparade filen.

Rätta bara stavningen, spara igen och kör på nytt:

```python runnable
print("Hello, Python!")
```

Du ska åter se `Hello, Python!`. Den lyckade omkörningen slutför återhämtningen; att bara läsa felet räcker inte.

### Guidad TODO och ledtråd

```python todo
# hello.py
# TODO 1: write one print call for the exact text Hello, Python!
# TODO 2: save the file and run it from its directory.
# TODO 3: misspell print as pritn, observe NameError, repair it, save, and rerun.
```

**Ledtråd:** håll redigeraren, terminalen och filnamnet synliga. Fråga efter varje ändring: ”Sparade jag? Vilken katalog använder skalet? Vilket tolkkommando kör jag?”

Här kan du tryggt stanna. Du behöver inga variabler, funktioner, villkor, undantagshanterare, paket, testramverk eller särskilda redigerarknappar.

---

## Vägledda övningar (med TODO)

1. **1-1 · Kontrollera Python**

   ```bash todo
   # TODO: run one of these commands and write down the version you get
   python --version
   python3 --version
   ```

   *Ledtråd*: i Windows är kommandot oftast `python`; i macOS och Linux är det ofta `python3`.

2. **1-2 · Skapa din första ”låda” (.venv)**

   ```bash todo
   # TODO 1: create the virtual environment
   python -m venv .venv
   # TODO 2: activate it (pick the command for your system)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\.venv\Scripts\Activate.ps1
   # TODO 3: verify which Python and pip the environment uses
   python -c "import sys; print(sys.executable)"
   python -m pip --version
   ```

3. **1-3 · Hej, terminal**

   ```bash todo
   # TODO: complete section 5's save/run/error/repair loop, then rerun
   python hello.py
   ```

   *Ledtråd*: kommandot hör hemma i skalet när skalet står i mappen som innehåller `hello.py`.

---

## Vanliga misstag

- Python installeras utan att **“Add python.exe to PATH”** markeras i Windows, vilket gör att kommandot `python` inte hittas.
- `pip` hör till en annan Python än den du kör, så paketet installeras på fel ställe.
- `.venv` aktiveras inte, och projektet använder därför fel beroenden.
- `sudo pip install` används och riskerar att skada systemets Python. Använd hellre `.venv`.
- `python hello.py` skrivs efter prompten `>>>`. Lämna REPL-miljön med `exit()` och kör kommandot i skalet.
- Kommandot körs från en annan mapp eller filen sparas som `hello.py.txt`. Kontrollera den aktuella katalogen och hela filnamnet innan du ändrar Python-installationen.
- En ändring görs utan att filen sparas. Tolken kör då korrekt det äldre sparade innehållet; spara och kör igen.

---

## Förklarade lösningar

- Om `python` saknas: kontrollera PATH eller installera om i Windows; prova `python3` i macOS eller Linux.
- Undvik ”fel pip” genom att alltid skriva `python -m pip ...`. Då hör `pip` till just den Python-tolk som körs.
- Om `venv` inte går att aktivera: kontrollera att du står i rätt katalog och att `.venv/` faktiskt finns.
- För `NameError: ... 'pritn' ...`: använd den rapporterade filen och raden, ändra `pritn` till `print`, spara och kör igen tills den exakta lyckade raden visas.
- Om Python inte kan öppna `hello.py`: gå tillbaka till din egen lärandemapp och kontrollera hela filnamnet. Citattecken bevarar mellanslag i en sökväg; att ta bort mellanslagen är inte reparationen.

---

## Sammanfattning

Nu fungerar Python och `pip`, du kan skapa en virtuell miljö och du kan ta ett sparat program genom ett fullständigt fel- och återhämtningskretslopp. Du förstår också varför projekt inte bör blanda sina beroenden.

## Kontrollpunkt och självbedömning

### Kontrollpunkt för det första programmet

Skapa `hello.py` i en egen mapp, förutsäg utdata, spara filen och kör den med det tolkkommando du antecknade. Inför sedan `pritn`, identifiera källfilen, raden, `NameError` och det felstavade namnet, rätta felet, spara och kör igen. Den slutliga standardutdatan ska vara exakt `Hello, Python!` följt av en radbrytning.

Ge dig en poäng för varje kriterium:

- **Korrekthet:** den reparerade filen skriver ut exakt den förväntade raden.
- **Tydlighet:** du kan skilja mellan redigerare, källfil, skalkommando, tolk, REPL och utdata.
- **Återhämtning:** du använder stabila traceback-ledtrådar för att reparera `pritn` utan ominstallation eller höjda behörigheter.
- **Verifiering:** du sparar och observerar den lyckade omkörningen från rätt katalog.
- **Förklaring:** du kan förklara varför en osparad ändring eller fel arbetskatalog ändrar vad Python ser.

5/5 visar att du har uppnått resultatet för det första programmet. Om ett kriterium saknas upprepar du bara kretsloppet spara/köra/reparera; frivilliga installationsverktyg behövs inte.

### Kontrollpunkt för miljön

I aktiverad `.venv` kontrollerar du att `python --version`, `python -c "import sys; print(sys.executable)"` och `python -m pip --version` svarar. Sökvägen till den körbara filen ska ligga inuti `.venv`.

Ge dig en poäng för varje kriterium:
- **Korrekthet:** Python är 3.11 eller senare och alla tre kontroller lyckas.
- **Tydlighet:** din korta installationsanteckning visar kommandot och sökvägen du faktiskt använde.
- **Återställning:** du kan köra `deactivate` och vet hur en frivillig skaländring ångras.
- **Verifiering:** efter återaktivering pekar sökvägen fortfarande in i `.venv`.
- **Förklaring:** du kan med egna ord förklara varför `python -m pip` och en virtuell miljö hindrar installationer från att blandas.

Du är redo för kapitel 2 med 5/5. Om ett kriterium misslyckas använder du de förklarade lösningarna och upprepar bara den kontrollen.

## Avslutande reflektion

Om du kom hit har du redan gjort något viktigt: du har gjort datorn till en pålitlig plats för lärande och återhämtat dig från ditt första avsiktliga fel. Vilken ledtråd hjälpte mest: filnamnet, raden, undantagskategorin eller det okända namnet? I kapitel 2 börjar vi programmera på riktigt med variabler och enkla datatyper.
