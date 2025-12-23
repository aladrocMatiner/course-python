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

## Por qué importa
Toda API, formulario o automatización necesita tomar decisiones. Desde permitir o no un acceso hasta calcular tarifas distintas según la entrada, los condicionales son la base de la lógica backend. Dominar estas estructuras evita errores silenciosos y te ayuda a expresar reglas de negocio sin ambigüedad.

### Mini aventura
Esto es un “elige tu propia aventura” pero en código: si eliges la puerta A pasa una cosa, si eliges la B pasa otra. Aprender `if/else` es aprender a construir historias interactivas.

---

## 1. Modelo mental: traducir reglas a código
Piensa en un condicional como una bifurcación: “si sucede A, haz B; si no, haz C”. La clave es expresar la regla en una condición booleana.

```python
# payment.py
monto = 120

if monto > 100:
    print("Aplicar descuento del 10%")
else:
    print("Sin descuento")
```

- La condición debe evaluarse a `True` o `False`.
- Usa sangría de 4 espacios (PEP 8) para los bloques.

---

## 2. If/elif/else en cascada

```python
# shipping.py
peso = 3.2

if peso <= 1:
    tarifa = 5
elif peso <= 5:
    tarifa = 10
else:
    tarifa = 20

print(f"Tarifa: {tarifa}€")
```

- `elif` significa “si no se cumplió lo anterior y esta condición sí”.
- Sólo uno de los bloques se ejecutará.

### Truthy y falsy
```python
usuario = ""  # cadena vacía se considera False
if usuario:
    print("Tenemos usuario")
else:
    print("Falta usuario")
```

Valores como `0`, `""`, `[]`, `{}` y `None` son falsy. Todo lo demás es truthy. Aprovecha esto para validar formularios rápidamente.

---

## 3. Operadores lógicos (`and`, `or`, `not`)

```python
edad = 20
pais = "ES"

if edad >= 18 and pais == "ES":
    print("Puede firmar el contrato")

if edad < 18 or pais != "ES":
    print("Necesitamos autorización adicional")

if not pais:
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

```python
# ternary.py
score = 75
estado = "aprobado" if score >= 60 else "recuperación"
print(estado)
```

- Sintaxis: `valor_si_true if condicion else valor_si_false`.
- Úsalo para asignaciones o retornos cortos, no para lógica larga.

### Ejemplo en endpoints
```python
def status_response(exito: bool) -> dict:
    return {
        "status": "ok" if exito else "error",
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
```python
# Antes
if (not usuario_activo) or (usuario_activo and usuario_baneado):
    bloquear = True
else:
    bloquear = False

# Después (aplicando lógica)
bloquear = (not usuario_activo) or usuario_baneado
```

Aplicar leyes de De Morgan ayuda a reducir condicionales anidados:
- `not (A and B)` equivale a `not A or not B`.
- `not (A or B)` equivale a `not A and not B`.

Esto mejora la legibilidad y reduce errores.

### Nota: `match` / `case` (Python 3.10+)
Python 3.10 introdujo *structural pattern matching*, una alternativa avanzada al `switch/case` tradicional.

```python
def estado_pedido(pedido):
    match pedido:
        case {\"status\": \"pending\", \"total\": total} if total > 100:
            return \"revisar manually por importe alto\"
        case {\"status\": \"pending\"}:
            return \"en cola\"
        case {\"status\": \"shipped\"}:
            return \"enviado\"
        case _:
            return \"desconocido\"
```

- `match` compara estructuras (diccionarios, tuplas, objetos) y puede incluir *guards* (`if total > 100`).
- Disponible sólo a partir de Python 3.10; si trabajas con versiones anteriores, mantén `if/elif/else`.

---

## 6. Validaciones y pruebas

```python
# discounts.py
def calcular_descuento(total, cliente_vip):
    if total < 0:
        raise ValueError("total no puede ser negativo")
    if total >= 100 or cliente_vip:
        return total * 0.1
    return 0
```

```python
# tests/test_discounts.py
import pytest
from discounts import calcular_descuento

def test_descuento_por_total_alto():
    assert calcular_descuento(150, cliente_vip=False) == 15

def test_descuento_por_cliente_vip():
    assert calcular_descuento(50, cliente_vip=True) == 5

def test_no_descuento():
    assert calcular_descuento(50, cliente_vip=False) == 0

def test_total_negativo():
    with pytest.raises(ValueError):
        calcular_descuento(-10, cliente_vip=False)
```

- Notarás tres rutas felices y un caso de error.
- Las pruebas te obligan a pensar en condiciones límite.

---

## Ejercicios guiados (con TODOs)
1. **8-1 · Clasificador de temperatura**
   ```python
   temperatura = 27
   # TODO 1: imprime "Frío" si temp < 15, "Templado" si 15-25, "Calor" si >25
   # TODO 2: usa un operador ternario para definir un mensaje "hidrátate" cuando la temperatura > 30
   ```
   *Pista*: combina `if/elif/else` con un ternario en una variable aparte.

2. **8-2 · Control de acceso**
   ```python
   usuario = {"activo": True, "rol": "editor"}
   # TODO 1: permite acceso si el usuario está activo y su rol es admin o editor
   # TODO 2: imprime "Requiere revisión" si el rol no es reconocido
   # TODO 3: agrega una prueba que confirme que usuarios inactivos son bloqueados
   ```
   *Pista*: usa `if usuario["activo"] and usuario["rol"] in {"admin", "editor"}`.

3. **8-3 · Validación lógica con De Morgan**
   ```python
   payload = {"email": "noor@example.com", "terms": True}
   # TODO 1: escribe una función es_valido(payload)
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
1. **Clasificador de temperatura**: `if temperatura < 15: ... elif temperatura <= 25: ... else: ...` seguido de `mensaje = "hidrátate" if temperatura > 30 else ""` muestra ambos enfoques.
2. **Control de acceso**: se usa `if usuario["activo"] and usuario["rol"] in {...}` para permitir; un `else` maneja inactivos y un `elif` adicional detecta roles desconocidos. La prueba crea un payload inactivo y espera bloqueo.
3. **Validación lógica**: `return bool(payload.get("email")) and payload.get("terms")` resume la lógica. Aplicar De Morgan permite expresar la condición opuesta si necesitas mensajes de error: `if not payload.get("email") or not payload.get("terms"):`.

---

## Resumen
Aprendiste a expresar reglas con `if/elif/else`, encadenar condiciones con operadores lógicos, usar ternarios para decisiones simples y pensar en términos de lógica proposicional para simplificar código. También validaste reglas mediante pruebas.

## Reflexión final
Cada decisión en tu aplicación pasa por algún condicional. Ahora puedes formularlos con confianza, reducir la complejidad usando lógica formal y aprovechar ternarios cuando aporten claridad. El siguiente capítulo abordará bucles para repetir acciones basadas en esas mismas condiciones.
