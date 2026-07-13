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

## Prerrequisitos
- No necesitas conocimientos previos de Python.
- Necesitas una terminal y permiso para instalar software en tu propio ordenador. En un equipo administrado por tu centro o empresa, pide ayuda a la persona responsable en lugar de saltarte las restricciones.
- Mantén este capítulo abierto en otra pestaña o dispositivo para poder leer la recuperación si falla un comando.

## Predicción antes de preparar el entorno
Antes de ejecutar nada, anota qué comando crees que inicia Python en tu sistema: `python`, `python3` o `py`. Después compararás esa predicción con el comando que realmente responde y con la ruta del ejecutable que muestra Python.

## Por qué importa
Si el entorno no está bien, lo que pasa es frustrante: copias un ejemplo, lo ejecutas… y sale un error que no es “tu culpa”, es del ordenador. Este capítulo evita eso. Una vez listo, el resto del curso se vuelve divertido.

### Mini aventura
Tu ordenador es como una bicicleta nueva: antes de salir a hacer una ruta larga, ajustas el sillín, inflas las ruedas y te aseguras de que los frenos funcionan. Aquí hacemos lo mismo: dejamos todo preparado para que el viaje sea seguro.

### Nuestro “reparto” (opcional y divertido)
A lo largo del libro verás a **Noor**, **Frej** y **Taha** como nombres de ejemplo dentro del código. Son solo nombres de muestra: puedes cambiarlos por el tuyo, el de tus amigos o el de tus personajes favoritos.

---

## 1. Instalar Python (v3.11+ recomendado)

### Windows
1. Visita [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/) y descarga el instalador oficial (`python-3.x.x-amd64.exe`).
2. Durante la instalación marca **“Add python.exe to PATH”** para evitar configuraciones manuales.
3. Completa el instalador y valida:
   ```powershell illustrative
   python --version
   pip --version
   ```
4. Alternativa automatizada (Windows 11+):  
   ```powershell illustrative
   winget install --id Python.Python.3.11 --source winget
   ```

### macOS
1. Descarga el paquete `.pkg` desde [https://www.python.org/downloads/macos/](https://www.python.org/downloads/macos/).
2. Ejecuta el instalador y acepta los valores por defecto (instala en `/Library/Frameworks/Python.framework`).
3. Verifica:
   ```bash illustrative
   python3 --version
   pip3 --version
   ```
4. Alternativa Homebrew:
   ```bash illustrative
   brew update
   brew install python@3.11
   python3.11 --version
   python3.11 -m pip --version
   ```
   No escribas `/opt/homebrew` de forma fija en tu perfil: Homebrew usa prefijos distintos en Apple Silicon e Intel. Si no se encuentra `python3.11`, ejecuta `brew info python@3.11` y sigue la indicación de tu instalación.

### Linux (Debian/Ubuntu)
```bash illustrative
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```
Si tu distribución ofrece una versión anterior a 3.11, no añadas un repositorio de terceros sin revisar solo para seguir este capítulo. Usa la documentación oficial de tu distribución o la ruta opcional con `asdf` que aparece más abajo.

### Linux (Fedora/CentOS/RHEL)
```bash illustrative
sudo dnf install -y python3 python3-pip
python3 --version
pip3 --version
```

---

## 2. Asegurar que `pip` esté disponible
- Primero comprueba el `pip` asociado al intérprete que vas a usar:
  ```bash illustrative
  python3 -m pip --version
  ```
- `ensurepip` es un módulo opcional de CPython. Si instalaste Python desde `python.org` y el módulo existe, puede inicializar `pip` sin descargarlo:
  ```bash illustrative
  python3 -m ensurepip --upgrade
  ```
- Si aparece `No module named ensurepip`, usa el instalador oficial o el gestor de paquetes del sistema (`python3-pip` en familias Debian/Fedora); no copies un script de arranque aleatorio.
- Actualiza `pip` solo después de activar el entorno virtual del proyecto:
  ```bash illustrative
  python -m pip install --upgrade pip
  ```

---

## 3. Gestionar múltiples versiones con `asdf` (opcional pero profesional)
`asdf` permite instalar y cambiar versiones de Python (y otras herramientas) por proyecto, garantizando entornos coherentes.

Esta ruta es opcional; el checkpoint esencial no la necesita. Instala la versión actual de `asdf` siguiendo la [guía oficial de inicio](https://asdf-vm.com/guide/getting-started.html), que cubre tu sistema y arquitectura. Los comandos siguientes usan la interfaz ejecutable actual; las instrucciones antiguas con `asdf.sh` y `asdf global` ya no se aplican.

1. Verifica la instalación:
   ```bash illustrative
   asdf --version
   ```
2. Añade el plugin comunitario de Python después de revisar la fuente mostrada por el índice oficial. Si `python` ya aparece en `asdf plugin list`, omite este comando:
   ```bash illustrative
   asdf plugin add python
   ```
3. Instala el último parche estable de 3.11 y escribe la elección resuelta en `.tool-versions` del proyecto:
   ```bash illustrative
   asdf install python latest:3.11
   asdf set python latest:3.11
   ```
4. Verifica:
   ```bash illustrative
   python --version
   python -m pip --version
   ```

Estas instrucciones sensibles a versiones se contrastaron con la documentación oficial de Python, Homebrew y `asdf` el 2026-07-13.

Beneficios:
- Cada repositorio puede definir `.tool-versions` para bloquear versiones.
- Evitas conflictos entre proyectos que requieren diferentes releases.

### Copia y recuperación para cambios opcionales del shell
La ruta esencial anterior no exige editar el archivo de inicio. Si la guía oficial de una herramienta opcional te pide cambiar `~/.zshrc` o `~/.bashrc`, cópialo primero, por ejemplo con `cp "$HOME/.zshrc" "$HOME/.zshrc.python-course.bak"`. Añade solo la línea documentada. Si un shell nuevo deja de funcionar, elimina esa línea desde la terminal antigua o restaura inmediatamente la copia. No restaures una copia antigua después de hacer otros cambios posteriores.

---

## 4. Buenas prácticas iniciales
- **Entornos virtuales**: usa `python -m venv .venv` y activa con `source .venv/bin/activate` (`.\.venv\Scripts\Activate.ps1` en Windows PowerShell).
- **Permisos**: evita `sudo pip install`; usa entornos virtuales o `pipx`.
- **Verificación**: después de instalar, ejecuta `python -m pip list` para asegurar que `pip` responde sin errores.

---

## Ejercicios guiados (con TODOs)
1. **1-1 · Comprobar Python**
   ```bash todo
   # TODO: ejecuta uno de estos comandos y apunta la versión que te salga
   python --version
   python3 --version
   ```
   *Pista*: en Windows suele ser `python`; en macOS/Linux a veces es `python3`.

2. **1-2 · Crear tu primera “cajita” (.venv)**
   ```bash todo
   # TODO 1: crea el entorno virtual
   python -m venv .venv
   # TODO 2: actívalo (elige el comando de tu sistema)
   # macOS/Linux: source .venv/bin/activate
   # Windows: .\.venv\Scripts\Activate.ps1
   # TODO 3: verify which Python and pip the environment uses
   python -c "import sys; print(sys.executable)"
   python -m pip --version
   ```

3. **1-3 · Hello, terminal**
   ```bash todo
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

## Checkpoint y autoevaluación
Dentro de `.venv` activado, confirma que `python --version`, `python -c "import sys; print(sys.executable)"` y `python -m pip --version` responden. La ruta del ejecutable debe apuntar dentro de `.venv`.

Suma un punto por cada criterio:
- **Corrección:** Python es 3.11 o posterior y las tres comprobaciones pasan.
- **Claridad:** tu nota breve registra el comando y la ruta del ejecutable que realmente usaste.
- **Recuperación:** sabes ejecutar `deactivate` y deshacer cualquier edición opcional del shell.
- **Verificación:** tras reactivar `.venv`, la ruta sigue apuntando dentro del entorno.
- **Explicación:** puedes explicar con tus palabras por qué `python -m pip` y un entorno virtual evitan mezclar instalaciones.

Estás listo para el capítulo 2 con 5/5. Si falla un criterio, usa las soluciones anteriores y repite solo esa comprobación.

## Reflexión final
Si llegaste hasta aquí, ya hiciste algo muy importante: convertir tu ordenador en un lugar confiable para aprender. Ahora sí: en el Capítulo 2 empezamos a escribir código de verdad (variables y tipos simples).
