# Capítulo 1 · Introducción y Entorno

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Antes de escribir código, vamos a preparar tu “taller” de Python: instalar un Python moderno, asegurarnos de que `pip` funciona y (opcional) aprender a tener varias versiones sin líos. Lo importante es que, cuando escribas `python --version`, tu ordenador responda y tú puedas empezar a programar sin peleas.

## Orden pedagógico
1. **Instalar Python** y comprobar que el comando funciona.
2. **Comprobar `pip`** para poder instalar librerías cuando las necesitemos.
3. **Entornos virtuales**: crear una “cajita” (`.venv`) para cada proyecto.
4. **Nivel extra**: usar `asdf` si quieres un entorno súper profesional.

## Objetivos de aprendizaje
- Verificar que Python está instalado y entender qué significa la versión.
- Asegurar que `pip` funciona y actualizarlo.
- Crear y activar un entorno virtual (`venv`) para un proyecto.
- Evitar los errores típicos del “funciona en mi máquina”.

## Por qué importa
Si el entorno no está bien, lo que pasa es frustrante: copias un ejemplo, lo ejecutas… y sale un error que no es “tu culpa”, es del ordenador. Este capítulo evita eso. Una vez listo, el resto del curso se vuelve divertido.

### Mini aventura
Tu ordenador es como una bicicleta nueva: antes de salir a hacer una ruta larga, ajustas el sillín, inflas las ruedas y te aseguras de que los frenos funcionan. Aquí hacemos lo mismo: dejamos todo preparado para que el viaje sea seguro.

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

## Ejercicios guiados (con TODOs)
1. **1-1 · Comprobar Python**
   ```bash
   # TODO: ejecuta uno de estos comandos y apunta la versión que te salga
   python --version
   python3 --version
   ```
   *Pista*: en Windows suele ser `python`; en macOS/Linux a veces es `python3`.

2. **1-2 · Crear tu primera “cajita” (.venv)**
   ```bash
   # TODO 1: crea el entorno virtual
   python -m venv .venv
   # TODO 2: actívalo (elige el comando de tu sistema)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\\.venv\\Scripts\\Activate.ps1
   # TODO 3: instala una librería (ejemplo)
   python -m pip install requests
   ```

3. **1-3 · Hello, terminal**
   ```bash
   # TODO: crea un archivo hello.py con un print y ejecútalo
   python hello.py
   ```

---

## Errores comunes
- Instalar Python, pero no marcar “Add python.exe to PATH” (Windows) ⇒ `python` no se encuentra.
- Usar `pip` de un Python distinto al que ejecutas ⇒ instala “en otro sitio” sin querer.
- Olvidar activar `.venv` ⇒ el proyecto usa dependencias equivocadas.
- Usar `sudo pip install` ⇒ rompe el sistema (mejor `.venv`).

---

## Explicación de soluciones
- Si `python` no existe: en Windows revisa la casilla de PATH o reinstala; en macOS/Linux prueba `python3`.
- Para evitar el “pip equivocado”: usa siempre `python -m pip ...` (así `pip` está ligado a ese Python).
- Si `venv` no se activa: revisa que estés en la carpeta correcta y que exista `.venv/`.

---

## Resumen
Ya tienes Python y `pip` funcionando, sabes crear un entorno virtual y entiendes por qué no conviene mezclar dependencias entre proyectos.

## Reflexión final
Si llegaste hasta aquí, ya hiciste algo muy importante: convertir tu ordenador en un lugar confiable para aprender. Ahora sí: en el Capítulo 2 empezamos a escribir código de verdad (variables y tipos simples).
