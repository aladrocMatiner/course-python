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

## Prerequisites
- No previous Python knowledge is required.
- You need a terminal and permission to install software on your own computer. On a managed school or work device, ask the administrator instead of bypassing restrictions.
- Keep this chapter open on another device or tab so you can read the recovery steps if a shell command fails.

## Predict before setup
Before running anything, write down which command you expect to start Python on your system: `python`, `python3`, or `py`. After installation you will compare that prediction with the command that actually responds and with the executable path reported by Python.

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
   ```powershell illustrative
   python --version
   pip --version
   ```
4. Automated alternative (Windows 11+):
   ```powershell illustrative
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Download the `.pkg` from [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Run the installer and accept the defaults (it installs into `/Library/Frameworks/Python.framework`).
3. Verify:
   ```bash illustrative
   python3 --version
   pip3 --version
   ```
4. Homebrew alternative:
   ```bash illustrative
   brew update
   brew install python@3.11
   python3.11 --version
   python3.11 -m pip --version
   ```
   Do not hard-code `/opt/homebrew` into your shell profile: Homebrew uses different prefixes on Apple Silicon and Intel. If `python3.11` is not found, run `brew info python@3.11` and follow the caveat printed for your installation.

### Linux (Debian/Ubuntu)
```bash illustrative
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```
If your distribution provides a version older than 3.11, do not add an unreviewed third-party repository just to follow this chapter. Use your distribution's official Python instructions or the optional `asdf` route below.

### Linux (Fedora/CentOS/RHEL)
```bash illustrative
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. Make sure `pip` is available
- First check the `pip` tied to the interpreter you intend to use:
  ```bash illustrative
  python3 -m pip --version
  ```
- `ensurepip` is an optional CPython module. If you installed Python from `python.org` and the module exists, it can bootstrap `pip` without downloading it:
  ```bash illustrative
  python3 -m ensurepip --upgrade
  ```
- If that reports `No module named ensurepip`, use the official installer or your operating system's package manager (`python3-pip` on Debian/Fedora families); do not copy a random bootstrap script.
- Update `pip` only after activating the project virtual environment:
  ```bash illustrative
  python -m pip install --upgrade pip
  ```

---

## 3. Manage multiple versions with `asdf` (optional but professional)
`asdf` lets you install and switch Python versions (and other tools) per project, so your environments stay consistent.

This route is optional. The essential checkpoint does not require it. Install the current `asdf` release using the [official Getting Started guide](https://asdf-vm.com/guide/getting-started.html), which covers your operating system and architecture. The commands below use the current executable-based interface; old `asdf.sh` and `asdf global` instructions do not apply.

1. Verify the installation:
   ```bash illustrative
   asdf --version
   ```
2. Add the community Python plugin after reviewing the source shown by the official plugin index. If `python` already appears in `asdf plugin list`, skip this command:
   ```bash illustrative
   asdf plugin add python
   ```
3. Install the latest stable 3.11 patch and write the resolved choice to this project's `.tool-versions`:
   ```bash illustrative
   asdf install python latest:3.11
   asdf set python latest:3.11
   ```
4. Verify:
   ```bash illustrative
   python --version
   python -m pip --version
   ```

These version-sensitive instructions were checked against the official Python, Homebrew, and `asdf` documentation on 2026-07-13.

Benefits:
- Each repo can define a `.tool-versions` file to “pin” versions.
- You avoid conflicts between projects that need different releases.

### Backup and rollback for optional shell changes
The essential route above does not require editing a shell startup file. If an official optional-tool guide asks you to edit `~/.zshrc` or `~/.bashrc`, first copy it, for example with `cp "$HOME/.zshrc" "$HOME/.zshrc.python-course.bak"`. Add only the documented line. If a new shell stops working, use the old terminal to remove that line or restore the backup immediately. Do not restore an old backup after making newer unrelated changes.

---

## 4. First good practices
- **Virtual environments**: use `python -m venv .venv` and activate with `source .venv/bin/activate` (`.\.venv\Scripts\Activate.ps1` in Windows PowerShell).
- **Permissions**: avoid `sudo pip install`; use virtual environments or `pipx`.
- **Quick check**: after installing, run `python -m pip list` to make sure `pip` responds without errors.

---

## Guided exercises (with TODOs)
1. **1-1 · Check Python**
   ```bash todo
   # TODO: run one of these commands and write down the version you get
   python --version
   python3 --version
   ```
   *Hint*: on Windows it’s usually `python`; on macOS/Linux it’s often `python3`.

2. **1-2 · Create your first “box” (.venv)**
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

3. **1-3 · Hello, terminal**
   ```bash todo
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

## Checkpoint and self-assessment
Inside the activated `.venv`, confirm that `python --version`, `python -c "import sys; print(sys.executable)"`, and `python -m pip --version` all respond. The executable path should point inside `.venv`.

Score one point for each item:
- **Correctness:** Python is 3.11 or newer and all three checks succeed.
- **Clarity:** your short setup note records the command and executable path you actually used.
- **Recovery:** you can run `deactivate` and know how to undo any optional shell edit.
- **Verification:** after reactivating `.venv`, the executable path still points inside it.
- **Explanation:** in your own words, you can explain why `python -m pip` and a virtual environment prevent mixing installations.

You are ready for Chapter 2 with 5/5. If one item fails, use the explained solutions above and repeat only that check.

## Closing reflection
If you made it here, you already did something important: you turned your computer into a reliable place to learn. Now we’re ready: in Chapter 2 we start coding for real (variables and simple types).
