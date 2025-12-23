# Kapitel 1 · Introduktion och miljö

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska · [العربية](README.ar.md)

## Vad ska vi bygga?
Innan vi skriver kod gör vi din Python‑“verkstad” redo: installera en modern Python, se till att `pip` fungerar och (valfritt) kunna hantera flera versioner utan kaos. Målet är enkelt: när du kör `python --version` ska datorn svara och du kan börja programmera utan strul.

## Lärstig
1. Installera Python och testa att kommandot fungerar.
2. Kontrollera `pip` så vi kan installera bibliotek vid behov.
3. Virtuella miljöer: en liten “låda” (`.venv`) per projekt.
4. Bonus: `asdf` för en mer professionell setup.

## Varför det spelar roll
Om miljön inte är rätt får du ofta fel som inte beror på dig, utan på datorn. När setupen är klar blir resten av kursen mycket roligare.

## Vår “rollista” (lite kul)
I exemplen använder vi ofta namnen **Noor**, **Frej** och **Taha**. De är bara exempel — byt gärna till ditt eget namn eller dina favoritkaraktärer.

---

## 1. Installera Python (rekommenderat v3.11+)

### Windows
1. Gå till [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) och ladda ner installern (`python-3.x.x-amd64.exe`).
2. Kryssa i **“Add python.exe to PATH”**.
3. Verifiera:
   ```powershell
   python --version
   pip --version
   ```
4. Alternativ (Windows 11+):
   ```powershell
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Ladda ner `.pkg` från [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Installera och kontrollera:
   ```bash
   python3 --version
   pip3 --version
   ```
3. Homebrew‑alternativ:
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

---

## 2. Se till att `pip` finns
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
```

---

## 3. Virtuell miljö (snabbt)
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install requests
```

---

## Övningar (med TODOs)
1. **1-1 · Kolla Python**
2. **1-2 · Skapa `.venv`**
3. **1-3 · Kör ett `hello.py`**

---

## Sammanfattning
Nu har du Python och `pip` igång och du kan skapa en virtuell miljö. Nästa kapitel: variabler och enkla typer.
