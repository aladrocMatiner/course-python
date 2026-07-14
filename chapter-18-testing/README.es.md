# Capítulo 18 · Pruebas con pytest: asegura tus ideas

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Crearemos un entorno de pruebas con `pytest`, aprenderemos a escribir tests claros, usar fixtures, parametrizar casos y medir cobertura básica. Verás ejemplos para funciones, clases y código con excepciones.

## Orden pedagógico
1. **¿Por qué probar?**
2. **Instalación y estructura de carpetas**.
3. **Primer test y ejecución**.
4. **Fixtures**.
5. **Parametrización**.
6. **Cobertura rápida (`--cov`)**.

## Objetivos de aprendizaje
- Configurar `pytest` en tus proyectos.
- Escribir tests para funciones puras y con efectos laterales controlados.
- Reutilizar datos de prueba con fixtures.
- Parametrizar listas de casos en un solo test.
- Interpretar reportes de cobertura básicos.

## Por qué importa
Las pruebas te permiten cambiar código sin miedo y detectar errores antes de que lleguen a producción.

### Mini aventura
Antes de estrenar una obra de teatro hay ensayos generales. Imagínate que cada test es un mini ensayo: verificas que cada personaje diga su parte correcta. Así, cuando llegue el público (usuarios), la función saldrá perfecta y sin nervios de último minuto.

### Cómo usar este capítulo (3 pasos)
1. Crea los archivos del ejemplo (tal cual).
2. Ejecuta `pytest` y busca el mensaje `passed`.
3. Cambia un número a propósito para ver un `failed` (es normal: estás aprendiendo a detectar errores).

## Prerrequisitos
- Funciones, clases, excepciones, módulos y entornos virtuales de los capítulos 11–16.
- Un entorno local activado; instalar `pytest` y `pytest-cov` requiere acceso a paquetes una vez.

## Predice antes de ejecutar
Antes de ejecutar la primera prueba, predice su estado y el cambio de código más pequeño que haría que fallara. Ejecuta ambas versiones, observa el diagnóstico y restaura el comportamiento correcto antes de continuar.

---

## 1. Instalación y estructura

```bash illustrative
pip install pytest pytest-cov
mkdir tests
```

- Coloca tus pruebas en `tests/` y nómbralas `test_*.py`.

---

## 2. Primer test
`math_utils.py`
```python runnable
def sumar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

`tests/test_math_utils.py`
```python illustrative
from math_utils import sumar, dividir

def test_sumar():
    assert sumar(2, 3) == 5

def test_dividir():
    assert dividir(10, 2) == 5
```

`assert` se lee como: “asegúrate de que esto sea verdad”. Si no lo es, el test falla.

Ejecuta:
```bash illustrative
pytest
```

Si quieres una salida más corta (ideal para empezar):
```bash illustrative
pytest -q
```

Cuando todo va bien verás algo parecido a `2 passed`.

---

## 3. Fixtures

```python illustrative
import pytest

@pytest.fixture
def sample_pedidos():
    return [10, 20, 30]

def test_promedio(sample_pedidos):
    promedio = sum(sample_pedidos) / len(sample_pedidos)
    assert promedio == 20
```

- Las fixtures son funciones que proveen datos listos para usar.

---

## 4. Parametrización

```python illustrative
import pytest
from math_utils import dividir

@pytest.mark.parametrize(
    "a,b,resultado",
    [ (10, 2, 5), (9, 3, 3), (5, 2, 2.5) ]
)
def test_dividir(a, b, resultado):
    assert dividir(a, b) == resultado
```

- Un test se ejecuta varias veces con diferentes parámetros.
- Piensa en esto como una “lista de ensayos”: mismo guion, distintos actores.

---

## 5. Excepciones y `pytest.raises`

```python illustrative
from math_utils import dividir
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 6. Cobertura

```bash illustrative
pytest --cov=. --cov-report=term-missing
```

- Señala qué líneas no se ejecutaron durante las pruebas.

---

## Ejercicios guiados (con TODOs)
1. **18-1 · Fixture reutilizable**
   ```python todo
   # TODO 1: create fixture db_tmp that uses tmp_path to simulate a file
   # TODO 2: use it in two tests
   ```
   *Pista*: escribe mediante `tmp_path / "db.json"`; pytest elimina el directorio temporal después de la prueba.

2. **18-2 · Parametrizar validaciones**
   ```python todo
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```
   *Pista*: parametriza pares `(payload, expected)` y asigna ids legibles a los casos inválidos.

3. **18-3 · Cobertura**
   ```bash todo
   # TODO 1: run pytest --cov and read the report
   ```
   *Pista*: trata las líneas sin cubrir como preguntas sobre el comportamiento, no como un porcentaje objetivo por sí solo.

---

## Errores comunes
- Olvidar prefijo `test_` y pytest no detecta el archivo.
- Mezclar código de producción con código de prueba (usa carpetas separadas).
- Fixtures con efectos secundarios no reseteados (usa `yield` para limpieza).

---

## Explicación de soluciones
1. **Fixture db_tmp**: `tmp_path / "db.json"` genera rutas temporales sin ensuciar el repo.
2. **Parametrizar**: `pytest.mark.parametrize` reduce duplicación y te obliga a pensar en casos límite.
3. **Cobertura**: interpreta qué líneas faltan por probar y decide si necesitas más tests.

---

## Resumen
`pytest` te da un flujo rápido para validar cada módulo. Con fixtures y parametrización, tus pruebas serán expresivas y fáciles de mantener.

## Punto de control y rúbrica
- **Corrección**: las pruebas cubren el comportamiento normal, los límites y las excepciones.
- **Legibilidad**: los nombres indican el comportamiento y el fallo que se protegen.
- **Manejo de errores**: los fixtures limpian los efectos secundarios incluso cuando falla una aserción.
- **Verificación**: ejecuta `pytest -q` desde un entorno limpio e inspecciona un fallo intencional.
- **Explicación**: explica qué demuestra cada prueba más allá de su línea de cobertura.

## Reflexión final
Haz de las pruebas un hábito: incluso scripts pequeños se benefician de verificar su comportamiento antes de integrarlos en proyectos mayores.
