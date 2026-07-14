# Capítulo 8 · Condicionales, Ternarios y Pensamiento Lógico

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Vamos a dominar las decisiones en Python: `if/elif/else`, evaluaciones lógicas, operadores ternarios y patrones típicos de validación en backend. Verás cómo elegir caminos distintos según los datos que recibes de una API, cómo resumir decisiones simples en una sola línea y cómo traducir reglas del mundo real al código.

## Orden pedagógico
1. **Contexto mental**: por qué las decisiones son el puente entre datos y acciones.
2. **`if` básico**: sintaxis, sangría y condiciones booleanas.
3. **`elif`/`else` y cascadas**: escoger un camino exclusivo.
4. **Operadores lógicos (`and`, `or`, `not`)**: combinar reglas como lo harías con lógica proposicional.
5. **Operadores ternarios**: decisiones breves cuando sólo cambia un valor.
6. **Validaciones y pruebas**: asegurar que las reglas se cumplen antes de exponer resultados.

## Objetivos de aprendizaje
- Escribir bloques `if/elif/else` claros y alineados con reglas de negocio.
- Combinar comparaciones con `and`, `or`, `not` entendiendo la lógica detrás.
- Usar operadores ternarios de forma legible para condiciones simples.
- Diferenciar entre valores “truthy”/“falsy” y cómo afectan las decisiones.
- Crear funciones que validan datos y probar sus rutas felices y de error.

## Prerrequisitos y rutas
Debes conocer las [variables y valores booleanos](../chapter-02-variables/README.es.md) y las [colecciones](../chapter-03-lists/README.es.md) básicas.

- **Ruta esencial · 45–60 min:** secciones 1–3, ejercicio 8-0, su recuperación y el punto esencial. Resultado: elegir exactamente una rama, combinar condiciones sencillas y explicar el límite. Las sentencias directas y la salida impresa son la evidencia; no exige funciones ni pytest.
- **Ruta intermedia · 30–40 min:** añade ternarios y transformaciones lógicas de las secciones 4–5. Detente cuando puedas reescribir una condición sin cambiar su tabla de verdad.
- **Ruta profesional opcional · 45–60 min:** estudia `match`, funciones de validación y pruebas. Anticipan las [funciones](../chapter-11-functions/README.es.md) y [pytest](../chapter-18-testing/README.es.md); copia los ejemplos completos o vuelve tras esos capítulos.

## Por qué importa
Toda API, formulario o automatización necesita tomar decisiones. Desde permitir o no un acceso hasta calcular tarifas distintas según la entrada, los condicionales son la base de la lógica backend. Dominar estas estructuras evita errores silenciosos y te ayuda a expresar reglas de negocio sin ambigüedad.

### Mini aventura
Esto es un “elige tu propia aventura” pero en código: si eliges la puerta A pasa una cosa, si eliges la B pasa otra. Aprender `if/else` es aprender a construir historias interactivas.

## Predice antes de ejecutar
Antes del primer ejemplo, predice qué rama se ejecuta con `amount = 120` y cambia solo el valor límite sobre el papel. Escribe la condición exacta que hace alcanzable cada rama antes de ejecutar.

---

## 1. Modelo mental: traducir reglas a código
Piensa en un condicional como una bifurcación: “si sucede A, haz B; si no, haz C”. La clave es expresar la regla en una condición booleana.

```python runnable
# payment.py
amount = 120

if amount > 100:
    print("Aplicar descuento del 10%")
else:
    print("Sin descuento")
```

- La condición debe evaluarse a `True` o `False`.
- Usa sangría de 4 espacios (PEP 8) para los bloques.

---

## 2. If/elif/else en cascada

```python runnable
# shipping.py
weight = 3.2

if weight <= 1:
    rate = 5
elif weight <= 5:
    rate = 10
else:
    rate = 20

print(f"Tarifa: {rate}€")
```

- `elif` significa “si no se cumplió lo anterior y esta condición sí”.
- Sólo uno de los bloques se ejecutará.

### Truthy y falsy
```python runnable
user = ""  # cadena vacía se considera False
if user:
    print("Tenemos usuario")
else:
    print("Falta usuario")
```

Valores como `0`, `""`, `[]`, `{}` y `None` son falsy. Todo lo demás es truthy. Aprovecha esto para validar formularios rápidamente.

---

## 3. Operadores lógicos (`and`, `or`, `not`)

```python runnable
age = 20
country = "ES"

if age >= 18 and country == "ES":
    print("Puede firmar el contrato")

if age < 18 or country != "ES":
    print("Necesitamos autorización adicional")

if not country:
    print("Debes indicar un país")
```

- `and` requiere que ambas condiciones sean verdaderas.
- `or` se cumple si al menos una es verdadera.
- `not` invierte el resultado.

### Cortocircuito
Python deja de evaluar si ya conoce el resultado. `condicion and expensive_call()` sólo ejecutará `expensive_call` si `condicion` es `True`. Aprovecha esto para validar precondiciones antes de trabajos costosos.

---

## 4. Operador ternario: decisiones breves
Usa el operador ternario cuando el resultado es un valor simple.

```python runnable
# ternary.py
score = 75
status = "aprobado" if score >= 60 else "recuperación"
print(status)
```

- Sintaxis: `valor_si_true if condicion else valor_si_false`.
- Úsalo para asignaciones o retornos cortos, no para lógica larga.

### Ejemplo en endpoints
```python runnable
from time import time

def status_response(success: bool) -> dict:
    return {
        "status": "ok" if success else "error",
        "timestamp": time()
    }
```

---

## 5. Pensando como lógica proposicional
Podemos reformular reglas con tablas de verdad:

- `A and B` sólo es verdadero cuando ambos lo son.
- `A or B` es falso sólo si ambos son falsos.
- `not A` invierte el valor de A.

### Simplificar expresiones
```python illustrative
# Antes
if (not user_active) or (user_active and user_banned):
    block = True
else:
    block = False

# Después (aplicando lógica)
block = (not user_active) or user_banned
```

Aplicar leyes de De Morgan ayuda a reducir condicionales anidados:
- `not (A and B)` equivale a `not A or not B`.
- `not (A or B)` equivale a `not A and not B`.

Esto mejora la legibilidad y reduce errores.

### Nota: `match` / `case` (Python 3.10+)
Python 3.10 introdujo *structural pattern matching*, una alternativa avanzada al `switch/case` tradicional.

```python runnable
def order_status(order):
    match order:
        case {"status": "pending", "total": total} if total > 100:
            return "revisión manual por importe alto"
        case {"status": "pending"}:
            return "en cola"
        case {"status": "shipped"}:
            return "enviado"
        case _:
            return "desconocido"
```

- `match` compara estructuras (diccionarios, tuplas, objetos) y puede incluir *guards* (`if total > 100`).
- Disponible sólo a partir de Python 3.10; si trabajas con versiones anteriores, mantén `if/elif/else`.

---

## 6. Validaciones y pruebas

```python runnable
# discounts.py
def calculate_discount(total, vip_customer):
    if total < 0:
        raise ValueError("total no puede ser negativo")
    if total >= 100 or vip_customer:
        return total * 0.1
    return 0
```

```python illustrative
# tests/test_discounts.py
import pytest
from discounts import calculate_discount

def test_discount_for_high_total():
    assert calculate_discount(150, vip_customer=False) == 15

def test_discount_for_vip_customer():
    assert calculate_discount(50, vip_customer=True) == 5

def test_no_discount():
    assert calculate_discount(50, vip_customer=False) == 0

def test_negative_total():
    with pytest.raises(ValueError):
        calculate_discount(-10, vip_customer=False)
```

- Notarás tres rutas felices y un caso de error.
- Las pruebas te obligan a pensar en condiciones límite.

---

## Práctica esencial y recuperación

### 8-0 · Una decisión explícita

Ejecuta este caso normal; después cambia `age` a `17` y predice la rama límite antes de repetirlo:

```python runnable
age = 18
has_permission = True

if age >= 18 and has_permission:
    print("Access granted")
else:
    print("Access denied")
```

Un error común es asignar dentro de la condición. El bloque siguiente es inválido a propósito; `SyntaxError` es el diagnóstico esperado:

<!-- bookcheck: expect-error="SyntaxError" -->
```python expected-error
age = 18
if age = 18:
    print("Access granted")
```

Recupérate comparando con `==` y explica por qué la rama es alcanzable:

```python runnable
age = 18
if age == 18:
    print("Access granted")
```

La evidencia de finalización son las dos salidas normales observadas y una frase que explique `>=` en el límite. Detente aquí en la ruta esencial; los ejercicios restantes son ampliaciones.

## Ejercicios guiados (con TODOs)
1. **8-1 · Clasificador de temperatura**
   ```python todo
   temperature = 27
   # TODO 1: imprime "Frío" si temp < 15, "Templado" si 15-25, "Calor" si >25
   # TODO 2: usa un operador ternario para definir un mensaje "hidrátate" cuando la temperatura > 30
   ```
   *Pista*: combina `if/elif/else` con un ternario en una variable aparte.

2. **8-2 · Control de acceso**
   ```python todo
   user = {"active": True, "role": "editor"}
   # TODO 1: permite acceso si el usuario está activo y su rol es admin o editor
   # TODO 2: imprime "Requiere revisión" si el rol no es reconocido
   # TODO 3: agrega una prueba que confirme que usuarios inactivos son bloqueados
   ```
   *Pista*: usa `if user["active"] and user["role"] in {"admin", "editor"}`.

3. **8-3 · Validación lógica con De Morgan**
   ```python todo
   payload = {"email": "noor@example.com", "terms": True}
   # TODO 1: escribe una función is_valid(payload)
   # TODO 2: la función debe devolver False si falta email o si terms es False
   # TODO 3: simplifica la expresión usando `not` y conjuntos
   ```
   *Pista*: `if not payload.get("email") or not payload.get("terms"):` es la forma directa.

---

## Errores comunes
- **Olvidar la sangría** ⇒ `IndentationError`. Usa 4 espacios por bloque.
- **Confundir `=` con `==`** ⇒ `=` asigna, `==` compara.
- **Condiciones largas sin paréntesis** ⇒ confusión de precedencia. Agrupa con `()` cuando combines `and/or`.
- **Abusar de ternarios** ⇒ si la línea es difícil de leer, vuelve a `if/else` clásico.

---

## Explicación de soluciones
1. **Clasificador de temperatura**: `if temperature < 15: ... elif temperature <= 25: ... else: ...` seguido de `message = "hidrátate" if temperature > 30 else ""` muestra ambos enfoques.
2. **Control de acceso**: se usa `if user["active"] and user["role"] in {...}` para permitir; un `else` maneja inactivos y un `elif` adicional detecta roles desconocidos. La prueba crea un payload inactivo y espera bloqueo.
3. **Validación lógica**: `return bool(payload.get("email")) and payload.get("terms")` resume la lógica. Aplicar De Morgan permite expresar la condición opuesta si necesitas mensajes de error: `if not payload.get("email") or not payload.get("terms"):`.

---

## Punto de control y autoevaluación
Crea un programa directo con `if/elif/else` para tres franjas de puntuación. Ejecuta un valor normal y los dos límites exactos; después reproduce y corrige el error entre `=` y `==` mostrado arriba. No uses funciones ni un framework de pruebas.

Da un punto por criterio: **ramas** (se ejecuta una sola), **límites** (ambos son correctos), **lógica** (explicas `and`/`or`), **recuperación** (al `SyntaxError` esperado le sigue código funcional) y **evidencia** (registras predicciones y salidas). Con 4/5 puedes continuar; si no, repasa las secciones 1–3. Ternarios, De Morgan, `match`, funciones y pytest quedan como evidencia opcional.

## Resumen
Aprendiste a expresar reglas con `if/elif/else`, encadenar condiciones con operadores lógicos, usar ternarios para decisiones simples y pensar en términos de lógica proposicional para simplificar código. También validaste reglas mediante pruebas.

## Reflexión final
Cada decisión en tu aplicación pasa por algún condicional. Ahora puedes formularlos con confianza, reducir la complejidad usando lógica formal y aprovechar ternarios cuando aporten claridad. El siguiente capítulo abordará bucles para repetir acciones basadas en esas mismas condiciones.
