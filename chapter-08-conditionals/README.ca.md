# Capítol 8 · Condicionals, ternaris i pensament lògic

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Dominarem les decisions en Python: `if/elif/else`, operadors lògics, operadors ternaris i patrons típics de validació en backend. Veuràs com escollir camins segons dades d’una API, com resumir decisions simples en una línia i com traduir regles del món real a codi.

## Ordre pedagògic
1. **Context mental**: decisions = pont entre dades i accions.
2. **`if` bàsic**: sintaxi, sagnat i condicions booleanes.
3. **`elif`/`else`**: escollir un camí exclusiu.
4. **Operadors lògics (`and`, `or`, `not`)**.
5. **Operador ternari**: decisions breus quan només canvia un valor.
6. **Validacions i proves**.

## Objectius d’aprenentatge
- Escriure blocs `if/elif/else` clars i alineats amb regles de negoci.
- Combinar comparacions amb `and`, `or`, `not` entenent la lògica.
- Usar ternaris de manera llegible per condicions simples.
- Diferenciar valors “truthy”/“falsy” i com afecten les decisions.
- Crear funcions de validació i provar camins feliços i d’error.

## Per què importa
Qualsevol API o automatització necessita prendre decisions: permetre o no un accés, calcular tarifes, validar dades… Els condicionals són la base de la lògica backend.

### Mini aventura
Això és un “tria la teva aventura” però en codi: si tries la porta A passa una cosa, si tries la B passa una altra.

---

## 1. Model mental: traduir regles a codi
Un condicional és una bifurcació: “si passa A, fes B; si no, fes C”.

```python
# payment.py
monto = 120

if monto > 100:
    print("Aplicar descuento del 10%")
else:
    print("Sin descuento")
```

- La condició ha de ser `True` o `False`.
- Usa sagnat de 4 espais (PEP 8).

---

## 2. `if/elif/else` en cascada

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

- `elif` vol dir “si el d’abans no s’ha complert i aquest sí”.
- Només s’executa un bloc.

### Truthy i falsy
```python
usuario = ""  # cadena buida = False
if usuario:
    print("Tenemos usuario")
else:
    print("Falta usuario")
```

Valors com `0`, `""`, `[]`, `{}` i `None` són falsy. La resta són truthy.

---

## 3. Operadors lògics (`and`, `or`, `not`)

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

- `and`: totes dues condicions han de ser veritat.
- `or`: n’hi ha prou amb una.
- `not`: inverteix el resultat.

### Curtcircuit (short‑circuit)
Python deixa d’avaluar si ja sap el resultat. `condicion and expensive_call()` només cridarà `expensive_call` si `condicion` és `True`.

---

## 4. Operador ternari: decisions breus
Útil quan el resultat és un valor simple.

```python
# ternary.py
score = 75
estado = "aprobado" if score >= 60 else "recuperación"
print(estado)
```

- Sintaxi: `valor_si_true if condicio else valor_si_false`.
- Si la línia es fa llarga, torna a `if/else`.

### Exemple en endpoints
```python
def status_response(exito: bool) -> dict:
    return {
        "status": "ok" if exito else "error",
        "timestamp": time()
    }
```

---

## 5. Pensar com a lògica proposicional
- `A and B` només és veritat quan totes dues ho són.
- `A or B` només és fals si totes dues són falses.
- `not A` inverteix A.

### Simplificar expressions
```python
# Antes
if (not usuario_activo) or (usuario_activo and usuario_baneado):
    bloquear = True
else:
    bloquear = False

# Después (aplicando lógica)
bloquear = (not usuario_activo) or usuario_baneado
```

Les lleis de De Morgan ajuden a reduir condicionals anidats:
- `not (A and B)` = `not A or not B`
- `not (A or B)` = `not A and not B`

### Nota: `match` / `case` (Python 3.10+)
Python 3.10 introdueix *structural pattern matching*, una alternativa moderna al `switch/case`.

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

- Disponible a partir de Python 3.10.

---

## 6. Validacions i proves

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

---

## Exercicis guiats (amb TODOs)
1. **8-1 · Classificador de temperatura**
   ```python
   temperatura = 27
   # TODO 1: imprimeix "Frío" si temp < 15, "Templado" si 15-25, "Calor" si >25
   # TODO 2: usa un ternari per posar un missatge "hidrátate" quan temperatura > 30
   ```

2. **8-2 · Control d’accés**
   ```python
   usuario = {"activo": True, "rol": "editor"}
   # TODO 1: permet accés si està actiu i el rol és admin o editor
   # TODO 2: imprimeix "Requiere revisión" si el rol no és reconegut
   # TODO 3: afegeix una prova que confirmi que usuaris inactius són bloquejats
   ```

3. **8-3 · Validació lògica amb De Morgan**
   ```python
   payload = {"email": "ada@example.com", "terms": True}
   # TODO 1: escriu es_valido(payload)
   # TODO 2: retorna False si falta email o si terms és False
   # TODO 3: simplifica l’expressió amb `not`
   ```

---

## Errors comuns
- Oblidar el sagnat ⇒ `IndentationError`.
- Confondre `=` amb `==`.
- Condicions llargues sense parèntesis ⇒ confusió de precedència.
- Abusar de ternaris ⇒ si costa llegir, millor `if/else`.

---

## Resum
Has après `if/elif/else`, operadors lògics, ternaris i idees de lògica proposicional per simplificar condicions. També has practicat validació amb proves.

## Reflexió final
Cada decisió en una app passa per algun condicional. Ara els pots escriure amb confiança i claredat. Al següent capítol treballarem bucles per repetir accions basades en condicions.
