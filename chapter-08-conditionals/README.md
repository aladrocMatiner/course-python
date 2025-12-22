# Chapter 8 · Conditionals, Ternaries, and Logical Thinking

English (default) · [Español](README.es.md) · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## What we’re going to build
We’ll master decision-making in Python: `if/elif/else`, logical operators, ternary expressions, and common backend validation patterns. You’ll learn how to choose different paths depending on API data, how to compress simple decisions into one line, and how to translate real-world rules into code.

## Learning path
1. **Mental context**: why decisions are the bridge between data and actions.
2. **Basic `if`**: syntax, indentation, and boolean conditions.
3. **`elif`/`else` and cascades**: choose one exclusive path.
4. **Logical operators (`and`, `or`, `not`)**: combine rules like propositional logic.
5. **Ternary operator**: short decisions where only a value changes.
6. **Validation and tests**: make sure rules hold before exposing results.

## Learning objectives
- Write clear `if/elif/else` blocks aligned with business rules.
- Combine comparisons with `and`, `or`, `not` while understanding the logic.
- Use ternaries in a readable way for simple conditions.
- Understand “truthy”/“falsy” values and how they affect decisions.
- Create validation functions and test happy and error paths.

## Why it matters
Every API, form, or automation script needs to make decisions: allow or deny access, calculate prices, choose messages, etc. Conditionals are the foundation of backend logic. Mastering them avoids silent bugs and helps you express business rules without ambiguity.

### Mini adventure
This is “choose your own adventure” but in code: pick door A and one thing happens, pick door B and something else happens. Learning `if/else` is learning to build interactive stories.

---

## 1. Mental model: translate rules into code
Think of a conditional as a fork: “if A happens, do B; otherwise, do C”. The key is expressing the rule as a boolean condition.

```python
# payment.py
monto = 120

if monto > 100:
    print("Aplicar descuento del 10%")
else:
    print("Sin descuento")
```

- The condition must evaluate to `True` or `False`.
- Use 4-space indentation (PEP 8) for blocks.

---

## 2. Cascaded if/elif/else

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

- `elif` means “if the previous ones were false, but this is true”.
- Only one block runs.

### Truthy and falsy
```python
usuario = ""  # empty string counts as False
if usuario:
    print("Tenemos usuario")
else:
    print("Falta usuario")
```

Values like `0`, `""`, `[]`, `{}` and `None` are falsy. Everything else is truthy. This is handy for quick form validation.

---

## 3. Logical operators (`and`, `or`, `not`)

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

- `and` requires both conditions to be true.
- `or` is true if at least one condition is true.
- `not` flips the result.

### Short-circuiting
Python stops evaluating once it already knows the result. `condicion and expensive_call()` will only run `expensive_call` if `condicion` is `True`. Use this to check preconditions before costly work.

---

## 4. Ternary operator: short decisions
Use the ternary operator when the result is a simple value.

```python
# ternary.py
score = 75
estado = "aprobado" if score >= 60 else "recuperación"
print(estado)
```

- Syntax: `value_if_true if condition else value_if_false`.
- Use it for short assignments/returns, not long logic.

### Example in endpoints
```python
def status_response(exito: bool) -> dict:
    return {
        "status": "ok" if exito else "error",
        "timestamp": time()
    }
```

---

## 5. Thinking like propositional logic
We can rewrite rules using truth tables:

- `A and B` is only true when both are true.
- `A or B` is only false when both are false.
- `not A` flips A.

### Simplifying expressions
```python
# Before
if (not usuario_activo) or (usuario_activo and usuario_baneado):
    bloquear = True
else:
    bloquear = False

# After (using logic)
bloquear = (not usuario_activo) or usuario_baneado
```

De Morgan’s laws help reduce nested conditionals:
- `not (A and B)` is the same as `not A or not B`.
- `not (A or B)` is the same as `not A and not B`.

This improves readability and reduces mistakes.

### Note: `match` / `case` (Python 3.10+)
Python 3.10 introduced *structural pattern matching*, a modern alternative to a classic `switch/case`.

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

- `match` can compare structures (dicts, tuples, objects) and can include *guards* (`if total > 100`).
- Available in Python 3.10 and later. If you use older versions, stick to `if/elif/else`.

---

## 6. Validation and tests

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

- You can see three “happy paths” and one error case.
- Tests force you to think about boundary conditions.

---

## Guided exercises (with TODOs)
1. **8-1 · Temperature classifier**
   ```python
   temperatura = 27
   # TODO 1: print "Frío" if temp < 15, "Templado" if 15-25, "Calor" if >25
   # TODO 2: use a ternary to set a "hidrátate" message when temperature > 30
   ```
   *Hint*: combine `if/elif/else` with a ternary stored in a separate variable.

2. **8-2 · Access control**
   ```python
   usuario = {"activo": True, "rol": "editor"}
   # TODO 1: allow access if user is active AND role is admin OR editor
   # TODO 2: print "Requiere revisión" if the role is not recognized
   # TODO 3: add a test confirming inactive users are blocked
   ```
   *Hint*: use `if usuario["activo"] and usuario["rol"] in {"admin", "editor"}`.

3. **8-3 · Logical validation with De Morgan**
   ```python
   payload = {"email": "ada@example.com", "terms": True}
   # TODO 1: write a function es_valido(payload)
   # TODO 2: it must return False if email is missing OR terms is False
   # TODO 3: simplify the expression using `not` and sets
   ```
   *Hint*: `if not payload.get("email") or not payload.get("terms"):` is the direct form.

---

## Common mistakes
- **Forgetting indentation** ⇒ `IndentationError`. Use 4 spaces per block.
- **Confusing `=` with `==`** ⇒ `=` assigns, `==` compares.
- **Long conditions without parentheses** ⇒ precedence confusion. Group with `()` when mixing `and/or`.
- **Overusing ternaries** ⇒ if the line is hard to read, go back to classic `if/else`.

---

## Explained solutions
1. **Temperature classifier**: `if temperatura < 15: ... elif temperatura <= 25: ... else: ...` then `mensaje = "hidrátate" if temperatura > 30 else ""` shows both styles.
2. **Access control**: use `if usuario["activo"] and usuario["rol"] in {...}` to allow; handle inactive users in an `else` and unknown roles with an extra `elif`. The test builds an inactive payload and expects a block.
3. **Logical validation**: `return bool(payload.get("email")) and payload.get("terms")` is a compact form. De Morgan helps when you need the “opposite” condition for error messages: `if not payload.get("email") or not payload.get("terms"):` .

---

## Summary
You learned to express rules with `if/elif/else`, chain conditions with logical operators, use ternaries for simple decisions, and think in propositional logic to simplify code. You also validated rules with tests.

## Closing reflection
Every decision in your app goes through a conditional somewhere. Now you can write them confidently, reduce complexity with formal logic, and use ternaries when they increase clarity. Next we’ll move to loops to repeat actions based on those same conditions.
