# Capítol 11 · Funcions, responsabilitat i funcions com a arguments

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprofundirem en funcions: definició, documentació, retorn de múltiples valors i el fet que a Python les funcions són dades. Les passarem com a arguments, les guardarem en col·leccions i farem petits pipelines. Veureu exemples inspirats en backend (validacions, hooks) que introdueixen funcions d’ordre superior.

## Ordre pedagògic
1. **Repàs**: definició, arguments i retorn.
2. **Responsabilitat única**: quan dividir en funcions petites.
3. **Defaults i arguments per nom**.
4. **Funcions com a “ciutadans” de primera**: guardar-les i passar-les.
5. **Funcions com a arguments**: callbacks, validadores i filtres.
6. **Funcions que retornen funcions (closures)**.
7. **Decoradors lleugers** (introducció).
8. **Proves i bones pràctiques**.

## Objectius d’aprenentatge
- Escriure funcions ben anomenades i amb docstring curta.
- Entendre posicional/keyword i valors per defecte.
- Passar funcions com a arguments i dissenyar APIs extensibles.
- Entendre closures i funcions que retornen funcions.
- Provar camins feliços/errores en funcions d’ordre superior.

## Prerequisits i anticipació opcional
Has de dominar les [llistes](../chapter-03-lists/README.ca.md), els [diccionaris](../chapter-04-dictionaries/README.ca.md), els [condicionals](../chapter-08-conditionals/README.ca.md) i els [bucles](../chapter-10-loops/README.ca.md). Repassa especialment com recórrer una col·lecció i retornar un resultat quan es compleix una condició.

La secció 7 anticipa les [proves amb pytest](../chapter-18-testing/README.ca.md). És opcional en una primera lectura: de moment, interpreta cada `assert` com «aquest resultat ha de ser igual al valor esperat».

## Per què importa
Funcions petites i llegibles redueixen errors i permeten reutilització. En backend, passar funcions (validadores, transformadores) fa que components siguin personalitzables sense duplicar codi.

### Mini aventura
Una funció és com una recepta: si està ben escrita, pots “cuinar” el resultat quan vulguis. I si algú més la llegeix, també pot cuinar-la.

## Predicció inicial
Sense executar codi, prediu el resultat de `procesar_items(["noor", "frej"], str.upper)`. Explica per què l’argument és `str.upper` i no `str.upper()`. Després prediu si canviar `[str.strip, str.upper]` per `[str.upper, str.strip]` altera el resultat del pipeline per a `"  hola  "`. Verifica cada predicció i anomena el valor que passa entre etapes.

---

## 1. Definir i documentar funcions

```python runnable
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

### Tipus i retorns múltiples
```python runnable
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

- Una docstring breu explica el contracte de la funció; les anotacions de tipus fan explícits els tipus esperats, però Python no els valida automàticament en temps d'execució.
- Retornar una tupla permet desempaquetar el resultat: `quantitat, mitjana = resumen_pedidos(pedidos)`.

---

## 2. Valors per defecte i arguments clau

```python runnable
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- Usa keyword args per claredat.
- Evita objectes mutables com a valor per defecte. Usa `None` i crea la llista o el diccionari dins de la funció.

---

## 3. Funcions com a ciutadans de primera classe

```python runnable
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

No hi ha parèntesis en `[notificar_email, notificar_sms]`: hi desem les funcions, no el resultat de cridar-les.

---

## 4. Passar funcions com a arguments

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

### Validadores personalitzables
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

Documenta sempre la signatura esperada del callback. Aquí ha de rebre un diccionari i retornar `None` o llançar una excepció.

---

## 5. Funcions que retornen funcions (closures)

```python runnable
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

### Exemple “backend”
```python runnable
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")
```

La funció interior conserva el valor de `minimo` encara que `crear_validador_longitud` ja hagi acabat: aquest estat capturat és el *closure*.

---

## 6. Decoradors lleugers (visió general)

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

`functools.wraps` conserva el nom i la documentació de la funció original, cosa important per a la depuració i els frameworks.

---

## 7. Proves per funcions d’ordre superior

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

La prova confirma que l'ordre importa i que s'apliquen totes les etapes.

---

## Exercicis guiats (amb TODOs)
1. **11-1 · Conversor flexible**
   ```python todo
   # TODO 1: crea convertir(items, funcion)
   # TODO 2: passa str.upper, després una funció que afegeixi prefix
   # TODO 3: valida que llanci excepció si funcion no és callable
   ```
   *Pista*: `callable(funcion)`.

2. **11-2 · Validadores encadenades**
   ```python todo
   def validar_no_vacio(texto):
       # TODO: ValueError si està buit
       pass

   def validar_minimo(texto):
       # TODO: ValueError si és més curt que un mínim
       pass
   # TODO 1: crea run_validators(texto, validadores)
   # TODO 2: atura’t al primer error i propaga’l
   # TODO 3: afegeix proves amb pytest
   ```

3. **11-3 · Decorador simple**
   ```python todo
   # TODO 1: escriu measure_time(func)
   # TODO 2: imprimeix quant ha trigat
   # TODO 3: usa’l en una funció amb bucles
   ```
   *Pista*: usa `time.perf_counter()` abans i després de la crida.

---

## Errors comuns
- Defaults mutables (`def foo(items=[])`): usa `None` i crea la llista a dins.
- Oblidar `return` en funcions que transformen.
- No documentar la signatura esperada dels callbacks: pot provocar crides incompatibles.
- Reutilitzar closures sense entendre què capturen: pot produir valors inesperats.

---

## Solucions explicades
1. **Conversor flexible**: `convertir(items, funcion)` recorre els elements i hi aplica la funció. Abans, `if not callable(funcion): raise TypeError(...)` rebutja valors que no es poden cridar. Així es poden combinar funcions integrades i funcions pròpies.
2. **Validadores encadenades**: `run_validators` recorre les funcions validadores. Si una llança `ValueError`, l'execució s'atura i l'error es propaga, igual que en molts fluxos de validació de serializers.
3. **Decorador simple**: `measure_time` embolcalla la funció original, mesura el temps abans i després i imprimeix la diferència. `functools.wraps` conserva les metadades de la funció decorada.

---

## Punt de control i rúbrica
Construeix `normalitzar_registres(registres, transformadors)` perquè cada diccionari passi per tots els transformadors en ordre sense mutar la llista d’entrada. Rebutja amb `TypeError` un transformador que no es pugui cridar i prova un pipeline buit, dues etapes ordenades i el camí d’error.

Suma un punt per criteri: **contracte** (entrades, sortida i errors explícits), **correcció** (funcionen l’ordre i tots els casos), **responsabilitat** (la funció conserva un únic propòsit), **verificació** (les proves cobreixen èxit i error) i **explicació** (distingeixes passar una funció de cridar-la). Amb 4/5 estàs preparat per a les classes; si no, repassa les seccions 3, 4 i 7.

---

## Resum
Les funcions són blocs reutilitzables amb responsabilitats clares. Quan les tractes com a dades, pots construir pipelines, validadores configurables i decoradors sense duplicar lògica.

## Reflexió final
Saber definir, combinar i passar funcions com a arguments et permet dissenyar APIs flexibles. És una habilitat molt útil en frameworks com Django.
