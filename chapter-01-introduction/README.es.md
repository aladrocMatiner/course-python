# Capítulo 1 · Introducción y Entorno

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Antes de escribir código, vamos a preparar tu “taller” de Python: instalar un Python moderno, asegurarnos de que `pip` funciona y aprender el ciclo completo editar → guardar → ejecutar → diagnosticar → reparar. El objetivo es sencillo: cuando escribas `python --version`, tu ordenador responderá; y cuando ejecutes tu primer programa guardado, sabrás exactamente qué archivo ha abierto Python y cómo recuperarte del primer traceback.

## Orden pedagógico
1. **Instalar Python** y comprobar que el comando funciona.
2. **Comprobar `pip`** para poder instalar librerías cuando las necesitemos.
3. **Entornos virtuales**: crear una “cajita” (`.venv`) para cada proyecto.
4. **Nivel extra**: usar `asdf` si quieres un entorno súper profesional.
5. **Ciclo del primer programa**: crear una carpeta propia, guardar `hello.py`, ejecutarlo, leer un error esperado, repararlo y volver a ejecutarlo.

## Objetivos de aprendizaje
- Verificar que Python está instalado y entender qué significa la versión.
- Asegurar que `pip` funciona y actualizarlo.
- Crear y activar un entorno virtual (`venv`) para un proyecto.
- Evitar los errores típicos del “funciona en mi máquina”.
- Distinguir el editor, un archivo `.py` guardado, el shell, el intérprete seleccionado, la salida estándar y el REPL interactivo.
- Ejecutar un archivo desde el directorio de trabajo correcto y usar las partes estables de un traceback para reparar un `NameError`.

## Prerrequisitos
- No necesitas conocimientos previos de Python.
- Necesitas una terminal y permiso para instalar software en tu propio ordenador. En un equipo administrado por tu centro o empresa, pide ayuda a la persona responsable en lugar de saltarte las restricciones.
- Mantén este capítulo abierto en otra pestaña o dispositivo para poder leer la recuperación si falla un comando.
- **Ruta esencial de entorno y primer programa · 60–90 min:** completa las secciones 1, 2, 4 y 5, además de ambos checkpoints. Resultado: una carpeta de aprendizaje local y desechable con un `hello.py` reparado que imprime una línea exacta. Puedes detenerte tras el checkpoint del primer programa y volver más tarde a las herramientas opcionales de entorno.
- **Entorno profesional opcional · 30–60 min:** crea `.venv` y, solo si necesitas varias versiones del intérprete, sigue la ruta de `asdf`. Ni `asdf` ni un botón de ejecución específico de un editor son necesarios para el capítulo 2.

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

## 5. De una carpeta a tu primer programa

Este es el pequeño ciclo que repetirás a lo largo del libro:

1. Un **editor** cambia el texto de un archivo de código fuente. El editor no demuestra que el programa funcione.
2. **Guarda** el archivo como `hello.py`; comprueba que el nombre no termina con un segundo sufijo oculto como `.txt`.
3. Un **shell** ejecuta comandos en su directorio de trabajo actual. Abre una terminal en tu carpeta de aprendizaje o cambia a ella de forma explícita.
4. El **intérprete de Python** seleccionado abre `hello.py` y lo ejecuta.
5. `print` envía texto a la **salida estándar**, que muestra tu terminal.

El prompt interactivo marcado con `>>>` es el **REPL**. Acepta expresiones de Python de una en una. `python hello.py` es un comando del shell, así que sal del REPL con `exit()` antes de escribirlo. En esta sección, sustituye `python` por el comando que anotaste antes (`python3` o `py`) cuando sea necesario y usa siempre la misma forma.

### Prepara un directorio de trabajo que te pertenezca

Usa una carpeta propia, no un directorio del sistema ni de la instalación de Python. Estos comandos son ejemplos; elige el bloque de tu shell.

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

El prompt suele cambiar después de `cd` o `Set-Location`. Si tu editor ofrece la acción «Abrir carpeta», abre ese mismo directorio. No tienes que cambiar el nombre de una carpeta personal porque contenga espacios.

### Predice, guarda y ejecuta

Antes de ejecutarlo, predice la única línea que imprimirá este archivo. Crea `hello.py` en el editor con exactamente este contenido. La observación correcta asociada al bloque ejecutable aparece justo después:

```python runnable
print("Hello, Python!")
```
```text output
Hello, Python!
```

Guárdalo y escribe después este comando en el **shell**, no dentro del archivo ni junto a `>>>`:

```bash illustrative
python hello.py
```

Si Python indica que no puede abrir `hello.py`, el hecho estable es que no ha encontrado la ruta solicitada desde el directorio de trabajo actual. Comprueba la carpeta, el nombre, el sufijo `.py` y que el editor haya guardado el archivo. No reinstales Python, no eleves privilegios ni muevas el ejercicio a un directorio del sistema.

### Primer traceback deliberado y recuperación

Cambia ahora solo `print` por `pritn`, guarda y predice qué ocurrirá. Este bloque debe fallar:

<!-- bookcheck: expect-error="NameError" -->
```python expected-error
pritn("Hello, Python!")
```

Un traceback puede contener texto que cambie entre versiones. Lee de abajo arriba sus pistas estables:

- la categoría final de la excepción es `NameError`;
- el mensaje final identifica el nombre desconocido `pritn`;
- la ruta y la línea indicadas apuntan a tu archivo guardado.

Corrige únicamente la ortografía, vuelve a guardar y ejecuta otra vez:

```python runnable
print("Hello, Python!")
```

Debes observar de nuevo `Hello, Python!`. La ejecución correcta después de reparar completa la recuperación; limitarse a leer el error no basta.

### TODO guiado y pista

```python todo
# hello.py
# TODO 1: write one print call for the exact text Hello, Python!
# TODO 2: save the file and run it from its directory.
# TODO 3: misspell print as pritn, observe NameError, repair it, save, and rerun.
```

**Pista:** mantén visibles el editor, la terminal y el nombre del archivo. Tras cada cambio, pregúntate: «¿He guardado? ¿Qué directorio usa el shell? ¿Qué comando de intérprete estoy ejecutando?»

Este es un punto seguro donde detenerte. No necesitas variables, funciones, condicionales, manejadores de excepciones, paquetes, frameworks de pruebas ni un botón especial del editor.

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
   # TODO: completa el ciclo guardar/ejecutar/error/reparación de la sección 5 y vuelve a ejecutar
   python hello.py
   ```
   *Pista*: este comando pertenece al shell cuando se encuentra en la carpeta que contiene `hello.py`.

---

## Errores comunes
- Instalar Python, pero no marcar “Add python.exe to PATH” (Windows) ⇒ `python` no se encuentra.
- Usar `pip` de un Python distinto al que ejecutas ⇒ instala “en otro sitio” sin querer.
- Olvidar activar `.venv` ⇒ el proyecto usa dependencias equivocadas.
- Usar `sudo pip install` ⇒ rompe el sistema (mejor `.venv`).
- Escribir `python hello.py` después del prompt `>>>` ⇒ sal del REPL con `exit()` y ejecuta el comando en el shell.
- Ejecutar desde otra carpeta o guardar `hello.py.txt` ⇒ revisa el directorio actual y el nombre completo antes de cambiar la instalación de Python.
- Editar sin guardar ⇒ el intérprete ejecuta correctamente el contenido guardado anterior; guarda y vuelve a ejecutar.

---

## Explicación de soluciones
- Si `python` no existe: en Windows revisa la casilla de PATH o reinstala; en macOS/Linux prueba `python3`.
- Para evitar el “pip equivocado”: usa siempre `python -m pip ...` (así `pip` está ligado a ese Python).
- Si `venv` no se activa: revisa que estés en la carpeta correcta y que exista `.venv/`.
- Para `NameError: ... 'pritn' ...`: usa el archivo y la línea indicados, corrige `pritn` por `print`, guarda y vuelve a ejecutar hasta que aparezca la línea correcta exacta.
- Si Python no puede abrir `hello.py`: regresa a tu carpeta de aprendizaje y comprueba el nombre completo. Las comillas conservan los espacios de una ruta; eliminar esos espacios no es la reparación.

---

## Resumen
Ya tienes Python y `pip` funcionando, sabes crear un entorno virtual y puedes llevar un programa guardado por un ciclo completo de fallo y recuperación. También entiendes por qué no conviene mezclar dependencias entre proyectos.

## Checkpoint y autoevaluación

### Checkpoint del primer programa

En una carpeta que te pertenezca, crea `hello.py`, predice su salida, guárdalo y ejecútalo con el comando de intérprete que anotaste. Introduce después `pritn`, identifica el archivo, la línea, `NameError` y el nombre mal escrito, corrígelo, guarda y vuelve a ejecutar. La salida estándar final debe ser exactamente `Hello, Python!` seguida de un salto de línea.

Suma un punto por cada criterio:

- **Corrección:** el archivo reparado imprime exactamente la línea esperada.
- **Claridad:** distingues editor, archivo de código, comando del shell, intérprete, REPL y salida.
- **Recuperación:** usas las pistas estables del traceback para reparar `pritn` sin reinstalar nada ni elevar privilegios.
- **Verificación:** guardas y observas la ejecución correcta desde el directorio previsto.
- **Explicación:** puedes explicar por qué un cambio sin guardar o un directorio de trabajo equivocado altera lo que ve Python.

Un 5/5 demuestra el resultado del primer programa. Si falla un criterio, repite solo el ciclo guardar/ejecutar/reparar; las herramientas opcionales de entorno no son necesarias.

### Checkpoint del entorno

Dentro de `.venv` activado, confirma que `python --version`, `python -c "import sys; print(sys.executable)"` y `python -m pip --version` responden. La ruta del ejecutable debe apuntar dentro de `.venv`.

Suma un punto por cada criterio:
- **Corrección:** Python es 3.11 o posterior y las tres comprobaciones pasan.
- **Claridad:** tu nota breve registra el comando y la ruta del ejecutable que realmente usaste.
- **Recuperación:** sabes ejecutar `deactivate` y deshacer cualquier edición opcional del shell.
- **Verificación:** tras reactivar `.venv`, la ruta sigue apuntando dentro del entorno.
- **Explicación:** puedes explicar con tus palabras por qué `python -m pip` y un entorno virtual evitan mezclar instalaciones.

Estás listo para el capítulo 2 con 5/5. Si falla un criterio, usa las soluciones anteriores y repite solo esa comprobación.

## Reflexión final
Si llegaste hasta aquí, ya hiciste algo muy importante: convertir tu ordenador en un lugar confiable para aprender y recuperarte de tu primer error intencionado. ¿Qué pista te ayudó más: el nombre del archivo, la línea, la categoría de la excepción o el nombre desconocido? En el capítulo 2 empezamos a escribir código de verdad con variables y tipos simples.
