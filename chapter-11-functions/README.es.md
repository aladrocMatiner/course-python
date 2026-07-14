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

## Prerrequisitos y rutas
Debes manejar [listas](../chapter-03-lists/README.es.md), [diccionarios](../chapter-04-dictionaries/README.es.md), [condicionales](../chapter-08-conditionals/README.es.md) y [bucles](../chapter-10-loops/README.es.md). Repasa especialmente cómo recorrer una colección y devolver un resultado cuando se cumple una condición.

- **Ruta fundamental · 60–75 min:** la sección fundamental, el ejercicio 11-0 y el punto esencial. Resultado: definir y llamar una función, usar argumentos posicionales/nombrados/por defecto, distinguir retorno de `None` implícito, explicar el ámbito local y recuperarse de una llamada inválida. No exige `Callable`, closures, decoradores, pytest ni temporización.
- **Ruta intermedia · 35–45 min:** secciones 1–2 tras el punto fundamental. Resultado: documentar una responsabilidad, añadir tipos de Python 3.11, devolver varios valores y usar un valor opcional seguro.
- **Ruta avanzada opcional · 75–110 min:** secciones 3–7 y ejercicios 11-1 a 11-3. Resultado: construir y explicar un pipeline de orden superior con callbacks, closures y un decorador ligero. La sección 7 anticipa las [pruebas con pytest](../chapter-18-testing/README.es.md); cópiala o sáltala en la primera lectura.

## Por qué importa
Funciones más legibles y pequeñas reducen errores y permiten reutilización. En backend, pasar funciones como argumentos (por ejemplo, validadores o transformadores) te permite crear componentes personalizables sin duplicar código.

### Mini aventura
Una función es como una receta: si la escribes bien, puedes cocinar el plato cuando quieras sin volver a pensar cada paso. Y si alguien más la lee, puede cocinarlo también. Las recetas buenas ahorran tiempo y evitan accidentes.

## Predicción inicial
Sin ejecutar código, predice `describir_tarea(" backup ")` y `describir_tarea(nombre="deploy", prioridad="high")` en el ejemplo fundamental. Identifica cada argumento, el valor por defecto y el valor que vuelve a quien llamó. La predicción del pipeline pertenece a la ruta avanzada opcional.

---

## Ruta fundamental: llamadas, retorno, ámbito y valores seguros
Una llamada tiene un flujo visible: los argumentos entran por los parámetros, se ejecuta el cuerpo y `return` devuelve un valor. Si se llega al final sin `return`, Python devuelve `None`.

```python runnable
def describir_tarea(nombre, prioridad="normal"):
    etiqueta = nombre.strip()
    return f"{etiqueta}: {prioridad}"

print(describir_tarea(" backup "))
print(describir_tarea(nombre="deploy", prioridad="high"))
```

La primera llamada es posicional y usa el valor por defecto. La segunda nombra ambos argumentos. `etiqueta` es local: solo existe durante esa llamada.

```python runnable
def anunciar(mensaje):
    print(mensaje)

resultado = anunciar("ready")
print(resultado is None)
```

Imprimir es un efecto, no un valor devuelto. La última línea observa el `None` implícito.

Usa `None` como señal para una lista opcional y crea la lista dentro de la llamada; así no compartes un valor mutable entre llamadas:

```python runnable
def registrar(mensaje, historial=None):
    if historial is None:
        historial = []
    historial.append(mensaje)
    return historial

primero = registrar("start")
segundo = registrar("stop")
print(primero, segundo)
```

Esta llamada omite a propósito el argumento obligatorio; la señal estable es `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
def saludar(nombre):
    return f"Hola, {nombre}"

saludar()
```

Recupérate haciendo coincidir la llamada con la firma y vuelve a ejecutar:

```python runnable
def saludar(nombre):
    return f"Hola, {nombre}"

print(saludar("Noor"))
```

Verifica los fundamentos con llamadas directas y valores impresos. Las pruebas automatizadas llegan en el Capítulo 18; aquí no son un prerrequisito oculto.

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
def resumen_pedidos(pedidos: list[int]) -> tuple[int, float]:
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
0. **11-0 · Función fundamental de etiquetas**
   ```python todo
   def crear_etiqueta(nombre, prefijo="user"):
       # TODO 1: limpia los espacios de nombre en una variable local
       # TODO 2: devuelve "prefijo:nombre_limpio"
       pass

   # TODO 3: llámala una vez por posición y otra con argumentos nombrados
   # TODO 4: imprime ambos retornos y prueba la frontera de cadena vacía
   ```
   *Pista*: el éxito esencial se observa con `print`; no necesitas callbacks, closures, decoradores, pytest ni temporizador.

Los ejercicios 11-1 a 11-3 pertenecen a la ruta avanzada opcional.

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
### Solución fundamental 11-0
El `nombre_limpio` local pertenece a una llamada, el valor por defecto solo se usa si se omite `prefijo` y quien llama recibe la cadena tras `return`.

```python runnable
def crear_etiqueta(nombre, prefijo="user"):
    nombre_limpio = nombre.strip()
    return f"{prefijo}:{nombre_limpio}"

print(crear_etiqueta(" Noor "))
print(crear_etiqueta(nombre="Frej", prefijo="admin"))
print(crear_etiqueta(""))
```

La cadena vacía es una frontera, no un fallo oculto. Un programa que deba rechazarla podrá añadir esa política después; aquí se comprenden primero llamada y retorno. El `TypeError` de llamada inválida y su recuperación se ejecutan en la sección fundamental.

1. **Conversor flexible**: `convertir(items, funcion)` recorre y aplica la función; antes verifica `if not callable(funcion): raise TypeError`. Permite combinar funciones built-in con personalizadas.
2. **Validadores encadenados**: `run_validators` itera sobre una lista de funciones; si alguna lanza `ValueError`, se detiene, lo cual imita el flujo de validaciones en serializers Django.
3. **Decorador simple**: `measure_time` envuelve a la función original, mide tiempo antes/después y muestra el resultado. Permite evaluar el impacto de bucles o pipelines.

---

## Punto de control y rúbrica
Construye `crear_etiqueta(nombre, prefijo="user")`, llámala por posición y con nombres, y verifica nombre normal, vacío y argumento ausente. Añade aparte `mostrar(mensaje)` sin `return` y explica por qué quien llama observa `None`. No uses callbacks, closures, decoradores, pytest ni temporización.

Suma un punto por **firma y llamadas**, **retornos correctos**, **valor por defecto seguro**, **recuperación documentada del `TypeError`** y **explicación de ámbito local frente a `None` implícito**. Con 4/5 completas la ruta fundamental y puedes seguir la ruta esencial del Capítulo 12. El antiguo reto de pipeline queda como desafío avanzado opcional.

---

## Resumen
Las funciones son bloques reutilizables con responsabilidades claras. Al tratarlas como datos puedes construir pipelines, validadores configurables y decoradores que amplían comportamientos sin duplicar lógica.

## Reflexión final
Saber definir, combinar y pasar funciones como argumentos te permite diseñar APIs flexibles y expresivas. Estas habilidades son esenciales para trabajar con frameworks como Django, donde las funciones se conectan para formar vistas, middlewares y señales.
