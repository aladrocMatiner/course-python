# Capítulo 11 · Funciones, responsabilidades y funciones como argumentos

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Profundizaremos en la definición de funciones, su documentación, el retorno de múltiples valores y el uso de funciones como datos: las pasaremos como argumentos, las almacenaremos en estructuras y crearemos pequeños pipelines. Verás ejemplos diseñados para backend (validaciones, serializadores, hooks) que llevan gradualmente a pensar en funciones de orden superior.

## Orden pedagógico
1. **Repaso**: definición, argumentos y retorno.
2. **Responsabilidad única**: cuándo dividir en funciones.
3. **Valores por defecto y palabras clave**.
4. **Funciones como ciudadanos de primera clase**: guardarlas en variables y colecciones.
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

## Prerrequisitos y anticipo opcional
Debes manejar [listas](../chapter-03-lists/README.es.md), [diccionarios](../chapter-04-dictionaries/README.es.md), [condicionales](../chapter-08-conditionals/README.es.md) y [bucles](../chapter-10-loops/README.es.md). Repasa especialmente cómo recorrer una colección y devolver un resultado cuando se cumple una condición.

La sección 7 anticipa las [pruebas con pytest](../chapter-18-testing/README.es.md). Es opcional en una primera lectura: por ahora, interpreta cada `assert` como «este resultado debe ser igual al valor esperado».

## Por qué importa
Funciones más legibles y pequeñas reducen errores y permiten reutilización. En backend, pasar funciones como argumentos (por ejemplo, validadores o transformadores) te permite crear componentes personalizables sin duplicar código.

### Mini aventura
Una función es como una receta: si la escribes bien, puedes cocinar el plato cuando quieras sin volver a pensar cada paso. Y si alguien más la lee, puede cocinarlo también. Las recetas buenas ahorran tiempo y evitan accidentes.

## Predicción inicial
Sin ejecutar código, predice el resultado de `procesar_items(["noor", "frej"], str.upper)`. Explica por qué el argumento es `str.upper` y no `str.upper()`. Después predice si cambiar `[str.strip, str.upper]` por `[str.upper, str.strip]` altera el resultado del pipeline para `"  hola  "`. Verifica cada predicción y nombra el valor que pasa de una etapa a otra.

---

## 1. Definir funciones y documentar

```python runnable
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
```python runnable
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. Valores por defecto y argumentos clave

```python runnable
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

```python runnable
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

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

- `transformacion` es una función. Puedes pasar funciones built-in (como `str.upper`) o definidas por ti.
- Documenta qué se espera de la función (`Callable[[str], str]`).

### Validadores personalizables
```python runnable
from typing import Callable

def guardar_usuario(data, validador: Callable[[dict], None]):
    validador(data)
    print("Guardado", data)

def validar_email(data):
    if "@" not in data["email"]:
        raise ValueError("Email inválido")

payload = {"email": "noor@example.com"}
guardar_usuario(payload, validar_email)
```

---

## 5. Funciones que devuelven funciones (closures)

```python runnable
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
```python runnable
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

```python runnable
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

```python runnable
# pipelines.py
def aplicar_pipeline(valor, etapas):
    for etapa in etapas:
        valor = etapa(valor)
    return valor
```

```python illustrative
# tests/test_pipelines.py
from pipelines import aplicar_pipeline

def test_aplicar_pipeline():
    etapas = [str.strip, str.upper]
    resultado = aplicar_pipeline("  hola  ", etapas)
    assert resultado == "HOLA"
```

- Las pruebas confirman que el orden importa y que se aplican todas las etapas.

---

## Ejercicios guiados (con TODOs)
1. **11-1 · Conversor flexible**
   ```python todo
   # TODO 1: crea convertir(items, funcion)
   # TODO 2: pásale str.upper, luego una función que agregue prefijo
   # TODO 3: valida que lanza excepción si funcion no es callable
   ```
   *Pista*: `callable(funcion)` devuelve True/False.

2. **11-2 · Validadores encadenados**
   ```python todo
   def validar_no_vacio(texto):
       # TODO: lanza ValueError si texto está vacío
       pass

   def validar_minimo(texto):
       # TODO: lanza ValueError si len(texto) es menor a un mínimo
       pass
   # TODO 1: crea run_validators(texto, validadores)
   # TODO 2: detente al primer error y propágalo
   # TODO 3: agrega pruebas con pytest
   ```

3. **11-3 · Decorador simple**
   ```python todo
   # TODO 1: escribe decorador measure_time(func)
   # TODO 2: que imprima cuánto tardó en ejecutarse
   # TODO 3: úsalo en una función con bucles para demostrarlo
   ```
   *Pista*: `time.perf_counter()` para medir.

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

## Punto de control y rúbrica
Construye `normalizar_registros(registros, transformadores)` para que cada diccionario pase por todos los transformadores en orden sin mutar la lista de entrada. Rechaza con `TypeError` un transformador que no sea invocable y prueba un pipeline vacío, dos etapas ordenadas y la ruta de error.

Suma un punto por criterio: **contrato** (entradas, salida y errores explícitos), **corrección** (funcionan el orden y todos los casos), **responsabilidad** (la función mantiene un propósito), **verificación** (las pruebas cubren éxito y fallo) y **explicación** (distingues pasar una función de llamarla). Con 4/5 estás listo para las clases; si no, repasa las secciones 3, 4 y 7.

---

## Resumen
Las funciones son bloques reutilizables con responsabilidades claras. Al tratarlas como datos puedes construir pipelines, validadores configurables y decoradores que amplían comportamientos sin duplicar lógica.

## Reflexión final
Saber definir, combinar y pasar funciones como argumentos te permite diseñar APIs flexibles y expresivas. Estas habilidades son esenciales para trabajar con frameworks como Django, donde las funciones se conectan para formar vistas, middlewares y señales.
