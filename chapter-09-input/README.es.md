# Capítulo 9 · Entrada de datos y validación segura

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Aprenderás a recoger datos desde la terminal (`input()`), argumentos de línea de comandos y archivos sencillos, siempre validando y convirtiendo los valores antes de usarlos. Verás ejemplos de formularios conversacionales y mini herramientas en consola que simulan flujos comunes en backend.

## Orden pedagógico
1. **Modelo mental**: cada entrada es un string; tú decides cómo convertirla.
2. **`input()` interactivo**: lecturas básicas y preguntas encadenadas.
3. **Conversión y validación**: `int()`, `float()`, `str.strip()` y manejos de `ValueError`.
4. **Valores por defecto y reintentos**: bucles hasta recibir algo válido.
5. **Argumentos de línea de comandos**: `sys.argv` y breve introducción a `argparse`.
6. **Lectura de archivos simples**: abrir, leer y asegurar que existan.
7. **Pruebas y ejercicios guiados**.

## Objetivos de aprendizaje
- Recoger entradas desde la consola y convertirlas al tipo correcto.
- Validar datos antes de usarlos, mostrando mensajes útiles si fallan.
- Implementar reintentos seguros con límites claros.
- Leer argumentos de línea de comandos y archivos básicos desde la librería estándar.
- Escribir pruebas que simulen entradas para funciones puras.

## Por qué importa
Los programas reales reciben datos desde usuarios u otros sistemas. Si confías ciegamente en la entrada, llegan bugs o vulnerabilidades. Dominar la lectura y validación te prepara para formularios web, scripts de automatización y comandos profesionales.

### Mini aventura
Piensa que tu programa es un robot amable. Si le hablas con frases raras, el robot se confunde. La validación es enseñarle al robot a decir: “no te entendí, ¿me lo repites de otra forma?”.

---

## 1. Modelo mental: todo llega como texto
`input()` siempre devuelve una cadena. Tú decides si la conviertes a número, fecha o la comparas como texto.

```python
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

- El prompt ayuda a la persona usuaria.
- Recorta espacios adicionales con `.strip()` si necesitas consistencia.

---

## 2. Conversión y manejo de errores

```python
raw_age = input("Edad: ")
try:
    edad = int(raw_age)
except ValueError:
    print("La edad debe ser un número entero.")
    edad = None
```

- Captura `ValueError` para informar qué salió mal.
- Puedes encapsular esta lógica en funciones reutilizables.

### Helper reutilizable
```python
def pedir_entero(prompt, intentos=3):
    for _ in range(intentos):
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Debes escribir un número entero.")
    raise RuntimeError("Intentos agotados")
```

---

## 3. Valores por defecto

```python
ciudad = input("Ciudad (por defecto Barcelona): ").strip() or "Barcelona"
print(ciudad)
```

- La expresión `valor or "default"` usa la ciudad por defecto si el string quedó vacío.

---

## 4. Reintentos y validaciones combinadas

```python
def pedir_email():
    while True:
        correo = input("Email: ").strip().lower()
        if "@" in correo and "." in correo:
            return correo
        print("Formato inválido. Intenta de nuevo.")
```

- Usa `while True` con `return` cuando necesitas repetir hasta lograr un formato válido.
- Asegura un camino de salida (por ejemplo, máximo de intentos) en scripts largos.

---

## 5. Argumentos de línea de comandos

```python
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Uso: python cli_args.py <archivo>")
    sys.exit(1)

ruta = sys.argv[1]
print(f"Procesando {ruta}")
```

### `argparse` abreviado
```python
import argparse

parser = argparse.ArgumentParser(description="Calculadora")
parser.add_argument("operacion", choices=["suma", "resta"])
parser.add_argument("a", type=int)
parser.add_argument("b", type=int)
args = parser.parse_args()

if args.operacion == "suma":
    print(args.a + args.b)
else:
    print(args.a - args.b)
```

- `argparse` valida y genera ayuda automáticamente.

---

## 6. Lectura simple de archivos

```python
from pathlib import Path

ruta = Path("datos.txt")
if not ruta.exists():
    raise FileNotFoundError("datos.txt no encontrado")

contenido = ruta.read_text(encoding="utf-8")
print(contenido)
```

- Usa `Path` para manipular rutas de forma portable.
- Maneja `FileNotFoundError` para dar mensajes comprensibles.

---

## 7. Pruebas para funciones puras
En lugar de probar `input()` directo, encapsula la lógica y pásale datos como argumentos. Así puedes usar `pytest` sin depender de la consola.

```python
# forms.py
def normalizar_nombre(nombre):
    limpio = nombre.strip().title()
    if not limpio:
        raise ValueError("Nombre vacío")
    return limpio
```

```python
# tests/test_forms.py
import pytest
from forms import normalizar_nombre

def test_normalizar_nombre_ok():
    assert normalizar_nombre("  ada ") == "Ada"

def test_normalizar_nombre_rechaza_vacio():
    with pytest.raises(ValueError):
        normalizar_nombre("   ")
```

---

## Ejercicios guiados (con TODOs)
1. **9-1 · Registro rápido**
   ```python
   # TODO 1: pide nombre y apellido, combínalos con title()
   # TODO 2: valida que ninguno esté vacío
   # TODO 3: imprime un mensaje de bienvenida con valores por defecto si faltan
   ```
   *Pista*: Usa `.strip()` y `or "Invitada"`.

2. **9-2 · CLI de notas**
   ```python
   # TODO 1: usa argparse para aceptar --titulo y --mensaje
   # TODO 2: guarda la nota en un archivo .txt con Path.write_text()
   # TODO 3: maneja errores si no se pasa el título
   ```
   *Pista*: `parser.add_argument("--titulo", required=True)`.

3. **9-3 · Importar CSV sencillo**
   ```python
   # TODO 1: pide la ruta de un archivo CSV usando input()
   # TODO 2: verifica que exista y léelo línea a línea
   # TODO 3: imprime cuántas filas válidas encontraste
   ```
   *Pista*: Usa `Path.open()` y `split(",")` para separar campos.

---

## Errores comunes
- Confiar en que la entrada ya tiene el formato correcto ⇒ captura `ValueError` y valida explícitamente.
- No recortar espacios ⇒ strings aparentemente diferentes que fallan las comparaciones.
- Olvidar `sys.exit(1)` en CLIs cuando faltan argumentos ⇒ el programa sigue en un estado incierto.
- Leer archivos sin verificar existencia ⇒ `FileNotFoundError` inesperado.

---

## Explicación de soluciones
1. **Registro rápido**: cada `input()` se limpia y se valida con `if not valor:`; los defaults (`"Invitada"`) evitan interrupciones.
2. **CLI de notas**: `argparse` asegura que `--titulo` y `--mensaje` estén presentes; `Path(titulo).with_suffix(".txt")` produce el archivo final.
3. **Importar CSV**: `Path(ruta).exists()` evita fallos; un contador acumula filas válidas y reporta al usuario.

---

## Resumen
Adquiriste patrones para leer datos desde la consola, argumentos y archivos, convirtiéndolos de forma segura y validando cada paso. Ahora puedes crear asistentes interactivos y scripts CLI sin temer entradas malformadas.

## Reflexión final
Cada interacción con personas o sistemas depende de entradas fiables. Con estas técnicas puedes guiar a quienes usan tus programas, anticipar errores y reaccionar con mensajes claros. En el próximo capítulo aplicaremos estas entradas para controlar bucles y estimar su coste.
