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

## Prerequisits i rutes
Has de conèixer les [variables i els valors booleans](../chapter-02-variables/README.ca.md) i les [col·leccions](../chapter-03-lists/README.ca.md) bàsiques.

- **Ruta essencial · 45–60 min:** seccions 1–3, exercici 8-0, la recuperació i el punt essencial. Resultat: triar exactament una branca, combinar condicions senzilles i explicar el límit. Les sentències directes i la sortida impresa són l’evidència; no exigeix funcions ni pytest.
- **Ruta intermèdia · 30–40 min:** afegeix ternaris i transformacions lògiques de les seccions 4–5. Atura’t quan puguis reescriure una condició sense canviar-ne la taula de veritat.
- **Ruta professional opcional · 45–60 min:** estudia `match`, funcions de validació i proves. Anticipen les [funcions](../chapter-11-functions/README.ca.md) i [proves amb pytest](../chapter-18-testing/README.ca.md); copia els exemples complets o torna després d’aquests capítols.

## Per què importa
Qualsevol API o automatització necessita prendre decisions: permetre o no un accés, calcular tarifes, validar dades… Els condicionals són la base de la lògica backend.

### Mini aventura
Això és un “tria la teva aventura” però en codi: si tries la porta A passa una cosa, si tries la B passa una altra.

## Prediu abans d'executar
Abans del primer exemple, prediu quina branca s'executa amb `amount = 120` i canvia només el valor límit sobre el paper. Escriu la condició exacta que fa accessible cada branca abans d'executar.

---

## 1. Model mental: traduir regles a codi
Un condicional és una bifurcació: “si passa A, fes B; si no, fes C”.

```python runnable
# payment.py
amount = 120

if amount > 100:
    print("Aplicar descuento del 10%")
else:
    print("Sin descuento")
```

- La condició ha de ser `True` o `False`.
- Usa sagnat de 4 espais (PEP 8).

---

## 2. `if/elif/else` en cascada

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

- `elif` vol dir “si el d’abans no s’ha complert i aquest sí”.
- Només s’executa un bloc.

### Truthy i falsy
```python runnable
user = ""  # cadena buida = False
if user:
    print("Tenemos usuario")
else:
    print("Falta usuario")
```

Valors com `0`, `""`, `[]`, `{}` i `None` són falsy. La resta són truthy.

---

## 3. Operadors lògics (`and`, `or`, `not`)

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

- `and`: totes dues condicions han de ser veritat.
- `or`: n’hi ha prou amb una.
- `not`: inverteix el resultat.

### Curtcircuit (short‑circuit)
Python deixa d’avaluar si ja sap el resultat. `condicion and expensive_call()` només cridarà `expensive_call` si `condicion` és `True`.

---

## 4. Operador ternari: decisions breus
Útil quan el resultat és un valor simple.

```python runnable
# ternary.py
score = 75
status = "aprobado" if score >= 60 else "recuperación"
print(status)
```

- Sintaxi: `valor_si_true if condicio else valor_si_false`.
- Si la línia es fa llarga, torna a `if/else`.

### Exemple en endpoints
```python runnable
from time import time

def status_response(success: bool) -> dict:
    return {
        "status": "ok" if success else "error",
        "timestamp": time()
    }
```

El ternari només decideix el valor de `status`; no ha d'amagar una seqüència llarga d'efectes.

---

## 5. Pensar com a lògica proposicional
- `A and B` només és veritat quan totes dues ho són.
- `A or B` només és fals si totes dues són falses.
- `not A` inverteix A.

### Simplificar expressions
```python illustrative
# Antes
if (not user_active) or (user_active and user_banned):
    block = True
else:
    block = False

# Después (aplicando lógica)
block = (not user_active) or user_banned
```

Les lleis de De Morgan ajuden a reduir condicionals anidats:
- `not (A and B)` = `not A or not B`
- `not (A or B)` = `not A and not B`

### Nota: `match` / `case` (Python 3.10+)
Python 3.10 introdueix *structural pattern matching*, una alternativa moderna al `switch/case`.

```python runnable
def order_status(order):
    match order:
        case {"status": "pending", "total": total} if total > 100:
            return "revisió manual per import elevat"
        case {"status": "pending"}:
            return "en cua"
        case {"status": "shipped"}:
            return "enviat"
        case _:
            return "desconegut"
```

- `match` pot comparar estructures (diccionaris, tuples i objectes) i incloure *guards* com `if total > 100`.
- Està disponible a partir de Python 3.10. En versions anteriors, fes servir `if/elif/else`.

---

## 6. Validacions i proves

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

- Hi ha tres camins correctes i un cas d'error.
- Les proves obliguen a considerar les condicions límit, com ara un total exactament igual a 100.

---

## Pràctica essencial i recuperació

### 8-0 · Una decisió explícita

Executa aquest cas normal; després canvia `age` a `17` i prediu la branca límit abans de repetir-lo:

```python runnable
age = 18
has_permission = True

if age >= 18 and has_permission:
    print("Access granted")
else:
    print("Access denied")
```

Un error habitual és assignar dins la condició. El bloc següent és invàlid expressament; `SyntaxError` és el diagnòstic esperat:

<!-- bookcheck: expect-error="SyntaxError" -->
```python expected-error
age = 18
if age = 18:
    print("Access granted")
```

Recupera’t comparant amb `==` i explica per què la branca és assolible:

```python runnable
age = 18
if age == 18:
    print("Access granted")
```

L’evidència de finalització són les dues sortides normals observades i una frase que expliqui `>=` al límit. Atura’t aquí a la ruta essencial; els exercicis restants són ampliacions.

## Exercicis guiats (amb TODOs)
1. **8-1 · Classificador de temperatura**
   ```python todo
   temperature = 27
   # TODO 1: imprimeix "Fred" si temp < 15, "Temperat" si 15-25, "Calor" si >25
   # TODO 2: usa un ternari per posar un missatge "hidrata't" quan temperature > 30
   ```
   *Pista*: combina `if/elif/else` amb un ternari desat en una variable separada.

2. **8-2 · Control d’accés**
   ```python todo
   user = {"active": True, "role": "editor"}
   # TODO 1: permet accés si està actiu i el rol és admin o editor
   # TODO 2: imprimeix "Cal revisar" si el rol no és reconegut
   # TODO 3: afegeix una prova que confirmi que usuaris inactius són bloquejats
   ```
   *Pista*: usa `if user["active"] and user["role"] in {"admin", "editor"}`.

3. **8-3 · Validació lògica amb De Morgan**
   ```python todo
   payload = {"email": "noor@example.com", "terms": True}
   # TODO 1: escriu is_valid(payload)
   # TODO 2: retorna False si falta email o si terms és False
   # TODO 3: simplifica l’expressió amb `not`
   ```
   *Pista*: `if not payload.get("email") or not payload.get("terms"):` és la forma directa.

---

## Errors comuns
- Oblidar el sagnat ⇒ `IndentationError`.
- Confondre `=` amb `==`.
- Condicions llargues sense parèntesis ⇒ confusió de precedència.
- Abusar de ternaris ⇒ si costa llegir, millor `if/else`.

---

## Solucions explicades
1. **Classificador de temperatura**: `if temperature < 15: ... elif temperature <= 25: ... else: ...` separa els tres intervals. Després, `message = "hidrata't" if temperature > 30 else ""` mostra la mateixa idea amb un ternari breu.
2. **Control d'accés**: `if user["active"] and user["role"] in {"admin", "editor"}:` permet l'accés. Un `else` bloqueja els usuaris inactius i un `elif` addicional pot distingir els rols desconeguts. La prova crea un diccionari amb `"active": False` i comprova que el resultat sigui un bloqueig.
3. **Validació lògica**: `return bool(payload.get("email")) and bool(payload.get("terms"))` és una forma compacta. Per explicar l'error, De Morgan permet escriure l'oposat: `if not payload.get("email") or not payload.get("terms"):`.

---

## Punt de control i autoavaluació
Crea un programa directe amb `if/elif/else` per a tres franges de puntuació. Executa un valor normal i els dos límits exactes; després reprodueix i corregeix l’error entre `=` i `==` anterior. No facis servir funcions ni cap framework de proves.

Dona un punt per criteri: **branques** (se n’executa una), **límits** (tots dos són correctes), **lògica** (expliques `and`/`or`), **recuperació** (al `SyntaxError` esperat el segueix codi funcional) i **evidència** (registres prediccions i sortides). Amb 4/5 pots continuar; si no, repassa les seccions 1–3. Ternaris, De Morgan, `match`, funcions i pytest queden com a evidència opcional.

## Resum
Has après `if/elif/else`, operadors lògics, ternaris i idees de lògica proposicional per simplificar condicions. També has practicat validació amb proves.

## Reflexió final
Cada decisió en una app passa per algun condicional. Ara els pots escriure amb confiança i claredat. Al següent capítol treballarem bucles per repetir accions basades en condicions.
