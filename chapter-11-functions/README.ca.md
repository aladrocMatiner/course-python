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

## Prerequisits i rutes
Has de dominar les [llistes](../chapter-03-lists/README.ca.md), els [diccionaris](../chapter-04-dictionaries/README.ca.md), els [condicionals](../chapter-08-conditionals/README.ca.md) i els [bucles](../chapter-10-loops/README.ca.md). Repassa especialment com recórrer una col·lecció i retornar un resultat quan es compleix una condició.

- **Ruta fonamental · 60–75 min:** la secció fonamental, l’exercici 11-0 i el punt essencial. Resultat: definir i cridar una funció, usar arguments posicionals/anomenats/per defecte, distingir retorn de `None` implícit, explicar l’àmbit local i recuperar-se d’una crida invàlida. No exigeix `Callable`, closures, decoradors, pytest ni temporització.
- **Ruta intermèdia · 35–45 min:** seccions 1–2 després del punt fonamental. Resultat: documentar una responsabilitat, afegir tipus de Python 3.11, retornar diversos valors i usar un valor opcional segur.
- **Ruta avançada opcional · 75–110 min:** seccions 3–7 i exercicis 11-1 a 11-3. Resultat: construir i explicar un pipeline d’ordre superior amb callbacks, closures i un decorador lleuger. La secció 7 anticipa les [proves amb pytest](../chapter-18-testing/README.ca.md); copia-la o salta-la en la primera lectura.

## Per què importa
Funcions petites i llegibles redueixen errors i permeten reutilització. En backend, passar funcions (validadores, transformadores) fa que components siguin personalitzables sense duplicar codi.

### Mini aventura
Una funció és com una recepta: si està ben escrita, pots “cuinar” el resultat quan vulguis. I si algú més la llegeix, també pot cuinar-la.

## Predicció inicial
Sense executar codi, prediu `describir_tarea(" backup ")` i `describir_tarea(nombre="deploy", prioridad="high")` a l’exemple fonamental. Identifica cada argument, el valor per defecte i el valor que torna a qui ha cridat. La predicció del pipeline pertany a la ruta avançada opcional.

---

## Ruta fonamental: crides, retorn, àmbit i valors segurs
Una crida té un flux visible: els arguments entren pels paràmetres, s’executa el cos i `return` retorna un valor. Si s’arriba al final sense `return`, Python retorna `None`.

```python runnable
def describir_tarea(nombre, prioridad="normal"):
    etiqueta = nombre.strip()
    return f"{etiqueta}: {prioridad}"

print(describir_tarea(" backup "))
print(describir_tarea(nombre="deploy", prioridad="high"))
```

La primera crida és posicional i usa el valor per defecte. La segona anomena tots dos arguments. `etiqueta` és local: només existeix durant aquella crida.

```python runnable
def anunciar(mensaje):
    print(mensaje)

resultado = anunciar("ready")
print(resultado is None)
```

Imprimir és un efecte, no un valor retornat. L’última línia observa el `None` implícit.

Usa `None` com a senyal per a una llista opcional i crea la llista dins la crida; així no comparteixes un valor mutable:

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

Aquesta crida omet expressament l’argument obligatori; el senyal estable és `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
def saludar(nombre):
    return f"Hola, {nombre}"

saludar()
```

Recupera’t fent coincidir la crida amb la signatura i torna a executar:

```python runnable
def saludar(nombre):
    return f"Hola, {nombre}"

print(saludar("Noor"))
```

Verifica els fonaments amb crides directes i valors impresos. Les proves automatitzades arriben al Capítol 18; aquí no són un prerequisit ocult.

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
def resumen_pedidos(pedidos: list[int]) -> tuple[int, float]:
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

- Cada funció comparteix la mateixa «forma», és a dir, la mateixa signatura.
- Aquest patró apareix en hooks i sistemes d'esdeveniments.

---

## 4. Passar funcions com a arguments

```python runnable
def procesar_items(items, transformacion):
    return [transformacion(item) for item in items]

procesar_items(["noor", "frej"], str.upper)  # ['NOOR', 'FREJ']
```

- `transformacion` és una funció: hi pots passar una funció integrada com `str.upper` o una de pròpia.
- En projectes reals, documenta què esperes, per exemple `Callable[[str], str]`.

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
És útil per configurar comportaments, com ara crear filtres personalitzats.

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
`@loggear` aplica la funció decoradora. Reserva aquest patró per a preocupacions transversals com el logging o els permisos.

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
0. **11-0 · Funció fonamental d’etiquetes**
   ```python todo
   def crear_etiqueta(nombre, prefijo="user"):
       # TODO 1: neteja els espais de nombre en una variable local
       # TODO 2: retorna "prefijo:nombre_limpio"
       pass

   # TODO 3: crida-la una vegada per posició i una altra amb arguments anomenats
   # TODO 4: imprimeix els dos retorns i prova la frontera de cadena buida
   ```
   *Pista*: l’èxit essencial s’observa amb `print`; no calen callbacks, closures, decoradors, pytest ni temporitzador.

Els exercicis 11-1 a 11-3 pertanyen a la ruta avançada opcional.

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
### Solució fonamental 11-0
El `nombre_limpio` local pertany a una crida, el valor per defecte només s’usa si s’omet `prefijo` i qui crida rep la cadena després de `return`.

```python runnable
def crear_etiqueta(nombre, prefijo="user"):
    nombre_limpio = nombre.strip()
    return f"{prefijo}:{nombre_limpio}"

print(crear_etiqueta(" Noor "))
print(crear_etiqueta(nombre="Frej", prefijo="admin"))
print(crear_etiqueta(""))
```

La cadena buida és una frontera, no un error ocult. Un programa que l’hagi de rebutjar podrà afegir la política després; aquí s’entenen primer crida i retorn. El `TypeError` de la crida invàlida i la recuperació s’executen a la secció fonamental.

1. **Conversor flexible**: `convertir(items, funcion)` recorre els elements i hi aplica la funció. Abans, `if not callable(funcion): raise TypeError(...)` rebutja valors que no es poden cridar. Així es poden combinar funcions integrades i funcions pròpies.
2. **Validadores encadenades**: `run_validators` recorre les funcions validadores. Si una llança `ValueError`, l'execució s'atura i l'error es propaga, igual que en molts fluxos de validació de serializers.
3. **Decorador simple**: `measure_time` embolcalla la funció original, mesura el temps abans i després i imprimeix la diferència. `functools.wraps` conserva les metadades de la funció decorada.

---

## Punt de control i rúbrica
Construeix `crear_etiqueta(nombre, prefijo="user")`, crida-la per posició i amb noms, i verifica nom normal, buit i argument absent. Afegeix a part `mostrar(mensaje)` sense `return` i explica per què qui crida observa `None`. No usis callbacks, closures, decoradors, pytest ni temporització.

Suma un punt per **signatura i crides**, **retorns correctes**, **valor per defecte segur**, **recuperació documentada del `TypeError`** i **explicació d’àmbit local davant `None` implícit**. Amb 4/5 completes la ruta fonamental i pots seguir la ruta essencial del Capítol 12. L’antic repte de pipeline queda com a desafiament avançat opcional.

---

## Resum
Les funcions són blocs reutilitzables amb responsabilitats clares. Quan les tractes com a dades, pots construir pipelines, validadores configurables i decoradors sense duplicar lògica.

## Reflexió final
Saber definir, combinar i passar funcions com a arguments et permet dissenyar APIs flexibles. És una habilitat molt útil en frameworks com Django.
