# Capítol 1 · Introducció i entorn

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Abans d’escriure codi, prepararem el teu “taller” de Python: instal·lar un Python modern, assegurar-nos que `pip` funciona i (opcional) aprendre a tenir diverses versions sense embolics. L’objectiu és molt simple: quan executis `python --version`, l’ordinador respongui i tu puguis començar a programar sense baralles.

## Ordre pedagògic
1. **Instal·lar Python** i comprovar que el comandament funciona.
2. **Comprovar `pip`** per poder instal·lar llibreries quan les necessitem.
3. **Entorns virtuals**: crear una “capseta” (`.venv`) per a cada projecte.
4. **Nivell extra**: usar `asdf` si vols un entorn súper professional.

## Objectius d’aprenentatge
- Verificar que Python està instal·lat i entendre què significa la versió.
- Assegurar que `pip` funciona i actualitzar-lo.
- Crear i activar un entorn virtual (`venv`) per a un projecte.
- Evitar els errors típics del “a la meva màquina funciona”.

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
   ```powershell
   python --version
   pip --version
   ```
4. Alternativa automatitzada (Windows 11+):
   ```powershell
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Descarrega el paquet `.pkg` des de [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Executa l’instal·lador i accepta els valors per defecte (instal·la a `/Library/Frameworks/Python.framework`).
3. Verifica:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Alternativa amb Homebrew:
   ```bash
   brew update
   brew install python@3.11
   echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```
Per a versions més noves pots usar el PPA “deadsnakes”:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev
```

### Linux (Fedora/CentOS/RHEL)
```bash
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. Assegurar que `pip` estigui disponible
- Python 3.4+ inclou `pip` per defecte, però si el comandament no apareix executa:
  ```bash
  python3 -m ensurepip --upgrade
  ```
- Recomanat: actualitzar `pip` després d’instal·lar Python:
  ```bash
  python3 -m pip install --upgrade pip
  ```

---

## 3. Gestionar múltiples versions amb `asdf` (opcional però professional)
`asdf` permet instal·lar i canviar versions de Python (i d’altres eines) per projecte, garantint entorns coherents.

1. Instal·la `asdf` (Linux/macOS):
   ```bash
   git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.13.1
   echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
   echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
   source ~/.bashrc   # o ~/.zshrc si uses Zsh
   ```
2. Afegeix el plugin de Python:
   ```bash
   asdf plugin add python https://github.com/danhper/asdf-python.git
   ```
3. Llista versions disponibles i instal·la la recomanada:
   ```bash
   asdf list all python
   asdf install python 3.11.6
   asdf global python 3.11.6   # o asdf local per a un projecte concret
   ```
4. Verifica:
   ```bash
   python --version
   pip --version
   ```

Beneficis:
- Cada repositori pot definir `.tool-versions` per fixar versions.
- Evites conflictes entre projectes que necessiten diferents versions.

---

## 4. Bones pràctiques inicials
- **Entorns virtuals**: usa `python -m venv .venv` i activa amb `source .venv/bin/activate` (`.\\.venv\\Scripts\\activate` a Windows).
- **Permisos**: evita `sudo pip install`; usa entorns virtuals o `pipx`.
- **Verificació**: després d’instal·lar, executa `python -m pip list` per assegurar que `pip` respon sense errors.

---

## Exercicis guiats (amb TODOs)
1. **1-1 · Comprovar Python**
   ```bash
   # TODO: executa un d’aquests comandaments i apunta la versió que et surt
   python --version
   python3 --version
   ```
   *Pista*: a Windows sol ser `python`; a macOS/Linux sovint és `python3`.

2. **1-2 · Crear la teva primera “capseta” (.venv)**
   ```bash
   # TODO 1: crea l’entorn virtual
   python -m venv .venv
   # TODO 2: activa’l (tria el comandament del teu sistema)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\\.venv\\Scripts\\Activate.ps1
   # TODO 3: instal·la una llibreria (exemple)
   python -m pip install requests
   ```

3. **1-3 · Hola, terminal**
   ```bash
   # TODO: crea un fitxer hello.py amb un print i executa’l
   python hello.py
   ```

---

## Errors comuns
- Instal·lar Python però no marcar “Add python.exe to PATH” (Windows) ⇒ no es troba `python`.
- Usar el `pip` d’un Python diferent del que executes ⇒ instal·les “a un altre lloc” sense voler.
- Oblidar activar `.venv` ⇒ el projecte usa dependències equivocades.
- Usar `sudo pip install` ⇒ pots trencar el sistema (millor `.venv`).

---

## Explicació de solucions
- Si `python` no existeix: a Windows revisa la casella de PATH o reinstal·la; a macOS/Linux prova `python3`.
- Per evitar el “pip equivocat”: usa sempre `python -m pip ...` (així `pip` queda lligat a aquell Python).
- Si `venv` no s’activa: revisa que siguis a la carpeta correcta i que existeixi `.venv/`.

---

## Resum
Ara tens Python i `pip` funcionant, saps crear un entorn virtual i entens per què no convé barrejar dependències entre projectes.

## Reflexió final
Si has arribat fins aquí, ja has fet una cosa molt important: convertir el teu ordinador en un lloc fiable per aprendre. Ara sí: al Capítol 2 començarem a escriure codi de veritat (variables i tipus simples).
