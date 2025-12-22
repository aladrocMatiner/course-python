# Capítulo 1 · Introducción y Entorno

## Objetivo
Antes de escribir código necesitamos asegurarnos de que todas las personas tengan un intérprete de Python moderno, `pip` para instalar dependencias y, opcionalmente, una herramienta como `asdf` para gestionar múltiples versiones. Esta sección explica cómo hacerlo en los sistemas operativos más comunes de forma reproducible.

---

## 1. Instalar Python (v3.11+ recomendado)

### Windows
1. Visita [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) y descarga el instalador oficial (`python-3.x.x-amd64.exe`).
2. Durante la instalación marca **“Add python.exe to PATH”** para evitar configuraciones manuales.
3. Completa el instalador y valida:
   ```powershell
   python --version
   pip --version
   ```
4. Alternativa automatizada (Windows 11+):  
   ```powershell
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Descarga el paquete `.pkg` desde [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Ejecuta el instalador y acepta los valores por defecto (instala en `/Library/Frameworks/Python.framework`).
3. Verifica:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Alternativa Homebrew:
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
Para versiones más nuevas puedes usar el PPA “deadsnakes”:
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

## 2. Asegurar que `pip` esté disponible
- Python 3.4+ incluye `pip` por defecto, pero si el comando no aparece ejecuta:
  ```bash
  python3 -m ensurepip --upgrade
  ```
- Recomendado: actualizar `pip` tras cada instalación:
  ```bash
  python3 -m pip install --upgrade pip
  ```

---

## 3. Gestionar múltiples versiones con `asdf` (opcional pero profesional)
`asdf` permite instalar y cambiar versiones de Python (y otras herramientas) por proyecto, garantizando entornos coherentes.

1. Instala `asdf` (Linux/macOS):
   ```bash
   git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.13.1
   echo '. "$HOME/.asdf/asdf.sh"' >> ~/.bashrc
   echo '. "$HOME/.asdf/completions/asdf.bash"' >> ~/.bashrc
   source ~/.bashrc   # o ~/.zshrc si usas Zsh
   ```
2. Añade el plugin de Python:
   ```bash
   asdf plugin add python https://github.com/danhper/asdf-python.git
   ```
3. Lista versiones disponibles e instala la recomendada:
   ```bash
   asdf list all python
   asdf install python 3.11.6
   asdf global python 3.11.6   # o asdf local para un proyecto específico
   ```
4. Verifica:
   ```bash
   python --version
   pip --version
   ```

Beneficios:
- Cada repositorio puede definir `.tool-versions` para bloquear versiones.
- Evitas conflictos entre proyectos que requieren diferentes releases.

---

## 4. Buenas prácticas iniciales
- **Entornos virtuales**: usa `python -m venv .venv` y activa con `source .venv/bin/activate` (`.\.venv\Scripts\activate` en Windows).
- **Permisos**: evita `sudo pip install`; usa entornos virtuales o `pipx`.
- **Verificación**: después de instalar, ejecuta `python -m pip list` para asegurar que `pip` responde sin errores.

---

Con estas herramientas instaladas, estás listo para seguir el Capítulo 2 (variables y tipos simples) con un entorno profesional y reproducible.
