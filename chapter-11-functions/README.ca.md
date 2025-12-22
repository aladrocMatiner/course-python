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

## Per què importa
Funcions petites i llegibles redueixen errors i permeten reutilització. En backend, passar funcions (validadores, transformadores) fa que components siguin personalitzables sense duplicar codi.

### Mini aventura
Una funció és com una recepta: si està ben escrita, pots “cuinar” el resultat quan vulguis. I si algú més la llegeix, també pot cuinar-la.

---

## 1. Definir i documentar funcions

```python
def calcular_total(items):
    """Suma los precios en una lista de items."""
    total = 0
    for item in items:
        total += item
    return total
```

### Tipus i retorns múltiples
```python
from typing import List, Tuple
def resumen_pedidos(pedidos: List[int]) -> Tuple[int, float]:
    cantidad = len(pedidos)
    total = sum(pedidos)
    promedio = total / cantidad if cantidad else 0
    return cantidad, promedio
```

---

## 2. Valors per defecte i arguments clau

```python
def aplicar_descuento(total, porcentaje=0.1):
    return total * (1 - porcentaje)

print(aplicar_descuento(100))      # usa 10%
print(aplicar_descuento(100, 0.2)) # 20%
```

- Usa keyword args per claredat.
- Evita objectes mutables com a default.

---

## 3. Funcions com a ciutadans de primera classe

```python
def notificar_email(mensaje):
    print(f"Email: {mensaje}")

def notificar_sms(mensaje):
    print(f"SMS: {mensaje}")

canales = [notificar_email, notificar_sms]
for canal in canales:
    canal("Deploy completado")
```

---

## 4. Passar funcions com a arguments

```python
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["ada", "linus"], str.upper)  # ['ADA', 'LINUS']
```

### Validadores personalitzables
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

## 5. Funcions que retornen funcions (closures)

```python
def crear_multiplicador(factor):
    def multiplicar(valor):
        return valor * factor
    return multiplicar

duplicar = crear_multiplicador(2)
print(duplicar(10))  # 20
```

### Exemple “backend”
```python
def crear_validador_longitud(minimo):
    def validar(texto):
        if len(texto) < minimo:
            raise ValueError("Muy corto")
        return texto
    return validar

validar_usuario = crear_validador_longitud(3)
validar_usuario("api")
```

---

## 6. Decoradors lleugers (visió general)

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

---

## 7. Proves per funcions d’ordre superior

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

---

## Exercicis guiats (amb TODOs)
1. **11-1 · Conversor flexible**
   ```python
   # TODO 1: crea convertir(items, funcion)
   # TODO 2: passa str.upper, després una funció que afegeixi prefix
   # TODO 3: valida que llanci excepció si funcion no és callable
   ```
   *Pista*: `callable(funcion)`.

2. **11-2 · Validadores encadenades**
   ```python
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
   ```python
   # TODO 1: escriu measure_time(func)
   # TODO 2: imprimeix quant ha trigat
   # TODO 3: usa’l en una funció amb bucles
   ```

---

## Errors comuns
- Defaults mutables (`def foo(items=[])`).
- Oblidar `return` en funcions que transformen.
- No documentar la “signatura” esperada de callbacks.
- Reutilitzar closures sense entendre què capturen.

---

## Resum
Les funcions són blocs reutilitzables amb responsabilitats clares. Quan les tractes com a dades, pots construir pipelines, validadores configurables i decoradors sense duplicar lògica.

## Reflexió final
Saber definir, combinar i passar funcions com a arguments et permet dissenyar APIs flexibles. És una habilitat molt útil en frameworks com Django.
