# Capítulo 11 · Funciones, responsabilidades y funciones como argumentos

## Qué vamos a construir
Profundizaremos en la definición de funciones, su documentación, el retorno de múltiples valores y el uso de funciones como datos: las pasaremos como argumentos, las almacenaremos en estructuras y crearemos pequeños pipelines. Verás ejemplos diseñados para backend (validaciones, serializadores, hooks) que llevan gradualmente a pensar en funciones de orden superior.

## Orden pedagógico
1. **Repaso**: definición, argumentos y retorno.
2. **Responsabilidad única**: cuándo dividir en funciones.
3. **Valores por defecto y palabras clave**.
4. **Funciones como ciudadanos de primera clase**: guardarlas en variables y pasarlas.
5. **Funciones como argumentos**: callbacks, validadores y filtros personalizados.
6. **Funciones que devuelven funciones** y cierres simples.
7. **Decoradores ligeros** (solo introducción conceptual).
8. **Pruebas y buenas prácticas**.

## Objetivos de aprendizaje
- Declarar funciones bien nombradas con documentación breve.
- Identificar argumentos posicionales, keyword y valores por defecto.
- Pasar funciones como argumentos y diseñar APIs extensibles.
- Comprender cierres (closures) y funciones que retornan otras funciones.
- Escribir pruebas que cubran rutas felices/errores en funciones de orden superior.

## Por qué importa
Funciona más legibles y pequeñas reducen errores y permiten reutilización. En backend, pasar funciones como argumentos (por ejemplo, validadores o transformadores) te permite crear componentes personalizables sin duplicar código.

---

## 1. Definir funciones y documentar

```python
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

- Nombres verbales (`calcular_total`).
- Docstring breve explica qué hace y qué espera.

### Tipos y retornos múltiples
```python
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. Valores por defecto y argumentos clave

```python
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- Usa palabras clave para claridad: `aplicar_descuento(total=100, porcentaje=0.15)`.
- Evita usar objetos mutables como valor por defecto (listas, dicts).

---

## 3. Funciones como ciudadanos de primera clase
Las funciones se pueden almacenar y pasar igual que cualquier variable.

```python
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

- Cada función comparte la misma firma (`mensaje`).
- Este patrón aparece en hooks o eventos.

---

## 4. Pasar funciones como argumentos

```python
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["ada", "linus"], str.upper)  # ['ADA', 'LINUS']
```

- `transformacion` es una función. Puedes pasar funciones built-in (como `str.upper`) o definidas por ti.
- Documenta qué se espera de la función (`Callable[[str], str]`).

### Validadores personalizables
```python
from typing import Callable

def guardar_usuario(data, validador: Callable[[dict], None]):
    validador(data)
    print("Guardado", data)

def validar_email(data):
    if "@" not in data["email"]:
        raise ValueError("Email inválido")

payload = {"email": "ada@example.com"}
guardar_usuario(payload, validar_email)
```

---

## 5. Funciones que devuelven funciones (closures)

```python
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

- `multiplicar` recuerda el valor de `factor` aunque `crear_multiplicador` haya terminado.
- Útil para configurar comportamientos (por ejemplo, crear filtros configurables).

### Uso en backend
```python
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")  # OK
```

---

## 6. Decoradores ligeros (visión general)

```python
import functools

def loggear(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Ejecutando {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@loggear
def procesar():
    print("Procesando...")
```

- `@loggear` aplica la función decoradora.
- `functools.wraps` preserva nombre y docstring.
- Úsalo cuando necesites lógica transversal (logging, permisos).

---

## 7. Pruebas para funciones de orden superior

```python
# pipelines.py
def aplicar_pipeline(valor, etapas):
    for etapa in etapas:
        valor = etapa(valor)
    return valor
```

```python
# tests/test_pipelines.py
def test_aplicar_pipeline():
    etapas = [str.strip, str.upper]
    resultado = aplicar_pipeline("  hola  ", etapas)
    assert resultado == "HOLA"
```

- Las pruebas confirman que el orden importa y que se aplican todas las etapas.

---

## Ejercicios guiados (con TODOs)
1. **11-1 · Conversor flexible**
   ```python
   # TODO 1: crea convertir(items, funcion)
   # TODO 2: pásale str.upper, luego una función que agregue prefijo
   # TODO 3: valida que lanza excepción si funcion no es callable
   ```
   *Hint*: `callable(funcion)` devuelve True/False.

2. **11-2 · Validadores encadenados**
   ```python
   def validar_no_vacio(texto): ...
   def validar_minimo(texto): ...
   # TODO 1: crea run_validators(texto, validadores)
   # TODO 2: detente al primer error y propágalo
   # TODO 3: agrega pruebas con pytest
   ```

3. **11-3 · Decorador simple**
   ```python
   # TODO 1: escribe decorador measure_time(func)
   # TODO 2: que imprima cuánto tardó en ejecutarse
   # TODO 3: úsalo en una función con bucles para demostrarlo
   ```
   *Hint*: `time.perf_counter()` para medir.

---

## Errores comunes
- Usar objetos mutables como default (`def foo(items=[])`). Mejor usar `None` y crear la lista dentro.
- Olvidar el `return` en funciones que transforman datos.
- No documentar la firma esperada de las funciones que se pasan como argumento ⇒ llamadas incompatibles.
- Reutilizar closures sin entender qué variables capturan ⇒ valores inesperados.

---

## Explicación de soluciones
1. **Conversor flexible**: `convertir(items, funcion)` recorre y aplica la función; antes verifica `if not callable(funcion): raise TypeError`. Permite combinar funciones built-in con personalizadas.
2. **Validadores encadenados**: `run_validators` itera sobre una lista de funciones; si alguna lanza `ValueError`, se detiene, lo cual imita el flujo de validaciones en serializers Django.
3. **Decorador simple**: `measure_time` envuelve a la función original, mide tiempo antes/después y muestra el resultado. Permite evaluar el impacto de bucles o pipelines.

---

## Resumen
Las funciones son bloques reutilizables con responsabilidades claras. Al tratarlas como datos puedes construir pipelines, validadores configurables y decoradores que amplían comportamientos sin duplicar lógica.

## Reflexión final
Saber definir, combinar y pasar funciones como argumentos te permite diseñar APIs flexibles y expresivas. Estas habilidades son esenciales para trabajar con frameworks como Django, donde las funciones se conectan para formar vistas, middlewares y señales.
