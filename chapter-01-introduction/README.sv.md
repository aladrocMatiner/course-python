# Kapitel 1 · Introduktion och installation

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Innan vi skriver kod förbereder vi din Python-verkstad: vi installerar en modern Python-version, kontrollerar att `pip` fungerar och lär oss, som frivillig fördjupning, att hantera flera versioner utan krångel. Målet är enkelt: när du kör `python --version` ska datorn svara, så att du kan börja programmera utan att kämpa mot installationen.

## Lärväg

1. **Installera Python** och kontrollera att kommandot fungerar.
2. **Kontrollera `pip`**, så att vi senare kan installera bibliotek.
3. **Virtuella miljöer**: skapa en liten avskild ”låda” (`.venv`) för varje projekt.
4. **Bonusnivå**: använd `asdf` om du vill ha en mer professionell installation.

## Lärandemål

- Kontrollera att Python är installerat och förstå vad versionsnumret betyder.
- Se till att `pip` fungerar och uppdatera det.
- Skapa och aktivera en virtuell miljö (`venv`) för ett projekt.
- Undvika det klassiska problemet ”det fungerar på min dator”.

## Förkunskaper

- Du behöver inga tidigare Python-kunskaper.
- Du behöver en terminal och tillåtelse att installera program på din egen dator. På en skola eller arbetsplats med administrerad dator ber du ansvarig person om hjälp i stället för att kringgå begränsningar.
- Ha kapitlet öppet i en annan flik eller enhet så att du kan läsa återställningsstegen om ett kommando misslyckas.

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
   # TODO: create a file hello.py with a print and run it
   python hello.py
   ```

---

## Vanliga misstag

- Python installeras utan att **“Add python.exe to PATH”** markeras i Windows, vilket gör att kommandot `python` inte hittas.
- `pip` hör till en annan Python än den du kör, så paketet installeras på fel ställe.
- `.venv` aktiveras inte, och projektet använder därför fel beroenden.
- `sudo pip install` används och riskerar att skada systemets Python. Använd hellre `.venv`.

---

## Förklarade lösningar

- Om `python` saknas: kontrollera PATH eller installera om i Windows; prova `python3` i macOS eller Linux.
- Undvik ”fel pip” genom att alltid skriva `python -m pip ...`. Då hör `pip` till just den Python-tolk som körs.
- Om `venv` inte går att aktivera: kontrollera att du står i rätt katalog och att `.venv/` faktiskt finns.

---

## Sammanfattning

Nu fungerar Python och `pip`, du kan skapa en virtuell miljö och du förstår varför projekt inte bör blanda sina beroenden.

## Kontrollpunkt och självbedömning

I aktiverad `.venv` kontrollerar du att `python --version`, `python -c "import sys; print(sys.executable)"` och `python -m pip --version` svarar. Sökvägen till den körbara filen ska ligga inuti `.venv`.

Ge dig en poäng för varje kriterium:
- **Korrekthet:** Python är 3.11 eller senare och alla tre kontroller lyckas.
- **Tydlighet:** din korta installationsanteckning visar kommandot och sökvägen du faktiskt använde.
- **Återställning:** du kan köra `deactivate` och vet hur en frivillig skaländring ångras.
- **Verifiering:** efter återaktivering pekar sökvägen fortfarande in i `.venv`.
- **Förklaring:** du kan med egna ord förklara varför `python -m pip` och en virtuell miljö hindrar installationer från att blandas.

Du är redo för kapitel 2 med 5/5. Om ett kriterium misslyckas använder du de förklarade lösningarna och upprepar bara den kontrollen.

## Avslutande reflektion

Om du kom hit har du redan gjort något viktigt: du har gjort datorn till en pålitlig plats för lärande. Nu är vi redo. I kapitel 2 börjar vi programmera på riktigt med variabler och enkla datatyper.
