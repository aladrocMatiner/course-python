# Capítol 14 · Excepcions: de principiant a heroïna/heroi

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Dominaràs el sistema d’excepcions de Python: detectar errors, gestionar-los amb `try/except`, llançar excepcions pròpies, crear classes personalitzades i dissenyar APIs robustes amb missatges clars. Practicarem patrons per validar entrades i netejar recursos.

## Ordre pedagògic
1. Model mental: les excepcions interrompen el flux normal.
2. `try/except` bàsic.
3. `else` i `finally`.
4. `raise`.
5. Excepcions personalitzades.
6. Encadenar (`raise ... from ...`).
7. Context managers.
8. Proves i exercicis.

## Objectius d’aprenentatge
- Capturar excepcions selectivament.
- Usar `else` i `finally` per controlar flux i neteja.
- Crear excepcions de domini.
- Encadenar excepcions sense perdre context.
- Provar funcions que han de llançar errors.

## Per què importa
Ignorar excepcions crea fallades silencioses o missatges críptics. Un bon maneig d’errors dona confiança i facilita depurar en producció.

### Mini aventura
Les excepcions són com senyals i airbags: t’avisen i et protegeixen quan alguna cosa va malament. Aprendre-les et fa el programa més segur.

---

## 1. `try/except` des de zero

```python
try:
    resultado = int("abc")
    print(resultado)
except ValueError:
    print("No era un número válido")
```

### Capturar múltiples excepcions
```python
import json

try:
    with open("config.txt", encoding="utf-8") as archivo:
        datos = json.load(archivo)
except FileNotFoundError as exc:
    print("Archivo faltante", exc)
except json.JSONDecodeError as exc:
    print("JSON inválido", exc)
```

---

## 2. `else` i `finally`

```python
def leer_config():
    return {"debug": True}

try:
    datos = leer_config()
except (FileNotFoundError, ValueError):
    datos = {}
else:
    print("Config cargada correctamente")
finally:
    print("Fin del proceso")
```

---

## 3. Llançar excepcions (`raise`)

```python
def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("El denominador no puede ser cero")
    return a / b
```

---

## 4. Excepcions personalitzades

```python
class ConfigError(Exception):
    """Errores relacionados con la configuración."""

class MissingConfig(ConfigError):
    pass
```

---

## 5. Encadenament (`raise ... from ...`)

```python
import json

class ConfigDecodeError(ConfigError):
    pass

try:
    config = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ConfigDecodeError("Config inválida") from exc
```

---

## 6. Context managers i neteja

```python
class TemporaryFile:
    def __enter__(self):
        self.fh = open("temp.txt", "w")
        return self.fh

    def __exit__(self, exc_type, exc, tb):
        self.fh.close()
        if exc_type:
            print("Ocurrió un error", exc)
            return False
```

---

## 7. Proves amb excepcions

```python
import pytest

def test_dividir_zero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## Exercicis guiats (amb TODOs)
1. **14-1 · Validador robust**
2. **14-2 · CLI resistent**
3. **14-3 · Excepció personalitzada**

---

## Resum
Controlar excepcions et permet escriure codi sòlid: decideixes què gestiones, què propagues i com ho expliques. Les excepcions personalitzades donen semàntica a la teva API.

## Reflexió final
Ser “heroïna/heroi” amb excepcions és anticipar fallades, escriure missatges clars i no tenir por de llançar errors quan una regla no es compleix.
