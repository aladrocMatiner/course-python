# Capítol 15 · Mòduls, paquets i organització del codi

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Aprendràs a dividir un projecte en fitxers i carpetes, importar funcions/classes, crear paquets reutilitzables i evitar importacions circulars. Simularem una mini app amb mòduls `dominio`, `servicios` i `cli`.

## Ordre pedagògic
1. Fitxer `.py` = mòdul.
2. Imports bàsics: `import`, `from ... import ...`.
3. Carpetes com a paquets: `__init__.py`, imports relatius.
4. Estructura recomanada de projecte.
5. Evitar cicles d’importació.
6. Punt d’entrada (`if __name__ == "__main__"`).

## Objectius d’aprenentatge
- Organitzar codi en mòduls coherents.
- Importar funcions i classes sense duplicar lògica.
- Crear paquets amb `__init__.py`.
- Detectar i arreglar importacions circulars.
- Preparar un mòdul principal executable.

## Per què importa
Els projectes reals no caben en un sol fitxer. Separar responsabilitats facilita proves, reutilització i col·laboració.

---

## 1. Mòduls bàsics
`saludos.py`
```python
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python
import saludos
print(saludos.hola("Taha"))
```

### `from ... import ...`
```python
from saludos import hola
print(hola("Frej"))
```

---

## 2. Paquets
Estructura:
```
mi_app/
    __init__.py
    dominio.py
    servicios.py
main.py
```

`mi_app/dominio.py`
```python
class Pedido:
    def __init__(self, id, total):
        self.id = id
        self.total = total
```

`mi_app/servicios.py`
```python
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    pedido.total = pedido.total * 0.9
    return pedido
```

`main.py`
```python
from mi_app.dominio import Pedido
from mi_app.servicios import procesar_pedido

pedido = Pedido(1, 100)
pedido = procesar_pedido(pedido)
print(pedido.total)
```

---

## 3. Evitar importacions circulars
Si un mòdul A importa B i B importa A, tens un cicle.

Solucions típiques:
- Mou lògica compartida a un mòdul independent.
- Fes imports locals dins funcions quan cal:
```python
def calcular(total):
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```

---

## 4. Punt d’entrada

```python
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

---

## Exercicis guiats (amb TODOs)
1. **15-1 · Separar domini i serveis**
2. **15-2 · CLI modular**
3. **15-3 · Resoldre un cicle**

---

## Resum
Separar el codi en mòduls i paquets manté el projecte ordenat. Ara pots importar només el necessari i crear punts d’entrada nets.

## Reflexió final
Pensa sempre: “on viu aquesta lògica?”. Mòduls clars et preparen per projectes més grans i frameworks com Django.
