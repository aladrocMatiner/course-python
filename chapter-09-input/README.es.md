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
- Escribir pruebas para funciones puras que no dependan de la consola.

## Prerrequisitos y rutas
- **Prerrequisito:** completa el checkpoint del [capítulo 8](../chapter-08-conditionals/README.es.md). La ruta esencial usa cadenas, conversiones y condicionales.
- **Ruta esencial · 40–55 min:** secciones 1–3 y ejercicio 9-1. Resultado: normalizar texto, convertir un entero y recuperarse de una entrada inválida.
- **Ruta intermedia · 30–40 min:** reintentos limitados de la sección 4. Es un **preview opcional** de [bucles](../chapter-10-loops/README.es.md), [funciones](../chapter-11-functions/README.es.md) y [excepciones](../chapter-14-exceptions/README.es.md); copia los helpers completos u omítelos.
- **Ruta profesional opcional · 45–60 min:** CLI, archivos, CSV y tests. Anticipa [archivos](../chapter-13-files/README.es.md) y [pytest](../chapter-18-testing/README.es.md). Nada de esta ruta es necesario para el checkpoint esencial.

## Por qué importa
Los programas reales reciben datos desde usuarios u otros sistemas. Si confías ciegamente en la entrada, llegan bugs o vulnerabilidades. Dominar la lectura y validación te prepara para formularios web, scripts de automatización y comandos profesionales.

### Mini aventura
Piensa que tu programa es un robot amable. Si le hablas con frases raras, el robot se confunde. La validación es enseñarle al robot a decir: “no te entendí, ¿me lo repites de otra forma?”.

## Predicción antes de leer entrada
Si alguien escribe `14`, predice el valor y tipo que devuelve `input()` y después el valor y tipo tras `int()`. Predice también qué ocurre con `catorce`; ejecuta el ejemplo de conversión e identifica el mensaje de recuperación en lugar de adivinar.

---

## 1. Modelo mental: todo llega como texto
`input()` siempre devuelve una cadena. Tú decides si la conviertes a número, fecha o la comparas como texto.

```python illustrative
nombre = input("¿Cómo te llamas? ")
print(f"Hola, {nombre}")
```

- El prompt ayuda a la persona usuaria.
- Recorta espacios adicionales con `.strip()` si necesitas consistencia.

---

## 2. Conversión y manejo de errores

```python illustrative
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
```python illustrative
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

```python illustrative
ciudad = input("Ciudad (por defecto Barcelona): ").strip() or "Barcelona"
print(ciudad)
```

- La expresión `valor or "default"` usa la ciudad por defecto si el string quedó vacío.

---

## 4. Reintentos y validaciones combinadas

```python illustrative
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

```python illustrative
# cli_args.py
import sys

if len(sys.argv) < 2:
    print("Uso: python cli_args.py <archivo>")
    sys.exit(1)

ruta = sys.argv[1]
print(f"Procesando {ruta}")
```

### `argparse` abreviado
```python illustrative
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

```python illustrative
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

```python runnable
# forms.py
def normalizar_nombre(nombre):
    limpio = nombre.strip().title()
    if not limpio:
        raise ValueError("Nombre vacío")
    return limpio
```

```python illustrative
# tests/test_forms.py
import pytest
from forms import normalizar_nombre

def test_normalizar_nombre_ok():
    assert normalizar_nombre("  noor ") == "Noor"

def test_normalizar_nombre_rechaza_vacio():
    with pytest.raises(ValueError):
        normalizar_nombre("   ")
```

---

## Ejercicios guiados (con TODOs)
1. **9-1 · Registro rápido**
   ```python todo
   # TODO 1: pide nombre y apellido, combínalos con title()
   # TODO 2: valida que ninguno esté vacío
   # TODO 3: imprime un mensaje de bienvenida con valores por defecto si faltan
   ```
   *Pista*: Usa `.strip()` y `or "Invitada"`.

2. **9-2 · CLI de notas**
   ```python todo
   # TODO 1: usa argparse para aceptar --titulo y --mensaje
   # TODO 2: deriva una ruta confinada con safe_note_path(titulo)
   # TODO 3: escribe en UTF-8 y rechaza sobrescribir una nota existente
   ```
   *Pista*: `parser.add_argument("--titulo", required=True)`.

   Usa este helper para impedir que el título inyecte `/`, `\\` o `..` en la ruta de salida:
   ```python illustrative
   from pathlib import Path

   def safe_note_path(title, root=Path("notes")):
       safe_stem = "".join(
           char for char in title.strip()
           if char.isalnum() or char in ("-", "_")
       )
       if not safe_stem:
           raise ValueError("title must contain a letter or number")
       root.mkdir(parents=True, exist_ok=True)
       path = root / f"{safe_stem}.txt"
       if path.exists():
           raise FileExistsError(f"refusing to overwrite {path}")
       return path
   ```

3. **9-3 · Importar CSV sencillo**
   ```python todo
   import csv
   # TODO 1: pide la ruta de un archivo CSV usando input()
   # TODO 2: abre con newline="" y encoding="utf-8"
   # TODO 3: cuenta filas válidas con csv.reader
   ```
   *Pista*: pasa el archivo abierto a `csv.reader`; a diferencia de `split(",")`, conserva comas entrecomilladas.

---

## Errores comunes
- Confiar en que la entrada ya tiene el formato correcto ⇒ captura `ValueError` y valida explícitamente.
- No recortar espacios ⇒ cadenas que parecen iguales pero fallan las comparaciones.
- Olvidar `sys.exit(1)` en CLIs cuando faltan argumentos ⇒ el programa sigue en un estado incierto.
- Leer archivos sin verificar existencia ⇒ `FileNotFoundError` inesperado.
- Derivar una ruta directamente del título ⇒ traversal o sobrescritura accidental; confina y sanea primero el nombre.
- Procesar CSV con `split(",")` ⇒ las comas entrecomilladas crean columnas falsas; usa el módulo `csv`.

---

## Explicación de soluciones
1. **Registro rápido**: cada `input()` se limpia y se valida con `if not valor:`; los defaults (`"Invitada"`) evitan interrupciones.
2. **CLI de notas**: `argparse` exige `--titulo` y `--mensaje`; `safe_note_path` mantiene el nombre dentro de `notes/`, rechaza un título vacío tras sanearlo e impide sobrescribir antes de `path.write_text(args.mensaje, encoding="utf-8")`.
3. **Importar CSV**: `Path(ruta).exists()` evita el fallo por archivo ausente; `csv.reader` conserva campos entrecomillados y el contador solo aumenta para filas con el número esperado de columnas.

---

## Checkpoint y autoevaluación
Pide un nombre y una edad. Predice sus tipos iniciales, normaliza el nombre, convierte la edad y recupérate de una edad inválida con un mensaje claro y reintentos limitados. No guardes información personal real: usa un nombre ficticio y descarta los valores al terminar.

Suma un punto por criterio:
- **Corrección:** la entrada válida produce el nombre normalizado y la edad entera esperados.
- **Legibilidad:** los prompts indican el formato y las variables distinguen valores crudos de convertidos.
- **Manejo del error:** la entrada inválida recibe un mensaje útil y los reintentos están limitados.
- **Verificación:** pruebas entrada válida, vacía y no numérica y registras la rama observada.
- **Explicación:** explicas por qué todos los valores de `input()` comienzan como cadenas.

La ruta profesional opcional añade dos comprobaciones: los títulos no escapan de `notes/` ni sobrescriben y los campos CSV entrecomillados permanecen unidos.

---

## Resumen
Adquiriste patrones para leer datos desde la consola, argumentos y archivos, convirtiéndolos de forma segura y validando cada paso. Ahora puedes crear asistentes interactivos y scripts CLI sin temer entradas malformadas.

## Reflexión final
Cada interacción con personas o sistemas depende de entradas fiables. Con estas técnicas puedes guiar a quienes usan tus programas, anticipar errores y reaccionar con mensajes claros. En el próximo capítulo aplicaremos estas entradas para controlar bucles y estimar su coste.
