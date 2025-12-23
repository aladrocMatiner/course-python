# Chapter 1 · Introduction & Setup

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
Before writing code, we’ll prepare your Python “workshop”: install a modern Python, make sure `pip` works and (optional) learn how to keep multiple versions without headaches. The goal is simple: when you run `python --version`, your computer answers and you can start coding without fighting your setup.

## Learning path
1. **Install Python** and confirm the command works.
2. **Check `pip`** so we can install libraries when we need them.
3. **Virtual environments**: create a small “box” (`.venv`) for each project.
4. **Bonus level**: use `asdf` if you want a super professional setup.

## Learning objectives
- Verify Python is installed and understand what the version means.
- Make sure `pip` works and update it.
- Create and activate a virtual environment (`venv`) for a project.
- Avoid the classic “it works on my machine” problems.

## Why it matters
If your setup isn’t right, something frustrating happens: you copy an example, run it… and you get an error that isn’t “your fault”. It’s your computer. This chapter prevents that. Once your setup is ready, the rest of the course becomes fun.

### Mini adventure
Your computer is like a new bike: before a long ride you adjust the seat, inflate the tires and check the brakes. Here we do the same thing: we prepare everything so the journey is safe.

### Meet our cast (optional fun)
Throughout the book, you’ll see **Noor**, **Frej**, and **Taha** show up as example names in code. They’re just placeholders — feel free to replace them with your name, your friends, or your favorite characters.

---

## 1. Install Python (v3.11+ recommended)

### Windows
1. Visit [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) and download the official installer (`python-3.x.x-amd64.exe`).
2. During installation, check **“Add python.exe to PATH”** to avoid manual setup later.
3. Finish the installer and validate:
   ```powershell
   python --version
   pip --version
   ```
4. Automated alternative (Windows 11+):
   ```powershell
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Download the `.pkg` from [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Run the installer and accept the defaults (it installs into `/Library/Frameworks/Python.framework`).
3. Verify:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Homebrew alternative:
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
For newer versions you can use the “deadsnakes” PPA:
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

## 2. Make sure `pip` is available
- Python 3.4+ includes `pip` by default, but if the command doesn’t exist run:
  ```bash
  python3 -m ensurepip --upgrade
  ```
- Recommended: update `pip` after installing Python:
  ```bash
  python3 -m pip install --upgrade pip
  ```

---

## 3. Manage multiple versions with `asdf` (optional but professional)
`asdf` lets you install and switch Python versions (and other tools) per project, so your environments stay consistent.

1. Install `asdf` (Linux/macOS):
   ```bash
   git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.13.1
   echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
   echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
   source ~/.bashrc   # or ~/.zshrc if you use Zsh
   ```
2. Add the Python plugin:
   ```bash
   asdf plugin add python https://github.com/danhper/asdf-python.git
   ```
3. List available versions and install the recommended one:
   ```bash
   asdf list all python
   asdf install python 3.11.6
   asdf global python 3.11.6   # or asdf local for a specific project
   ```
4. Verify:
   ```bash
   python --version
   pip --version
   ```

Benefits:
- Each repo can define a `.tool-versions` file to “pin” versions.
- You avoid conflicts between projects that need different releases.

---

## 4. First good practices
- **Virtual environments**: use `python -m venv .venv` and activate with `source .venv/bin/activate` (`.\\.venv\\Scripts\\activate` on Windows).
- **Permissions**: avoid `sudo pip install`; use virtual environments or `pipx`.
- **Quick check**: after installing, run `python -m pip list` to make sure `pip` responds without errors.

---

## Guided exercises (with TODOs)
1. **1-1 · Check Python**
   ```bash
   # TODO: run one of these commands and write down the version you get
   python --version
   python3 --version
   ```
   *Hint*: on Windows it’s usually `python`; on macOS/Linux it’s often `python3`.

2. **1-2 · Create your first “box” (.venv)**
   ```bash
   # TODO 1: create the virtual environment
   python -m venv .venv
   # TODO 2: activate it (pick the command for your system)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\\.venv\\Scripts\\Activate.ps1
   # TODO 3: install a library (example)
   python -m pip install requests
   ```

3. **1-3 · Hello, terminal**
   ```bash
   # TODO: create a file hello.py with a print and run it
   python hello.py
   ```

---

## Common mistakes
- Installing Python but not checking “Add python.exe to PATH” (Windows) ⇒ `python` is not found.
- Using `pip` from a different Python than the one you run ⇒ you install things “somewhere else” by accident.
- Forgetting to activate `.venv` ⇒ the project uses the wrong dependencies.
- Using `sudo pip install` ⇒ it can break your system (better: `.venv`).

---

## Explained solutions
- If `python` doesn’t exist: on Windows, re-check PATH or reinstall; on macOS/Linux try `python3`.
- To avoid the “wrong pip”: always use `python -m pip ...` (then `pip` is tied to that Python).
- If you can’t activate the `venv`: check you’re in the right folder and that `.venv/` exists.

---

## Summary
Now you have Python and `pip` working, you know how to create a virtual environment, and you understand why mixing dependencies between projects is a bad idea.

## Closing reflection
If you made it here, you already did something important: you turned your computer into a reliable place to learn. Now we’re ready: in Chapter 2 we start coding for real (variables and simple types).
