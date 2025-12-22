# Capítulo 15 · Módulos, paquetes y organización del código

## Qué vamos a construir
Aprenderás a dividir tu proyecto en archivos y carpetas, importar funciones/clases, crear paquetes reutilizables y evitar importaciones circulares. Simularemos una mini aplicación con módulos `dominio`, `servicios` y `cli` para que entiendas cómo se conectan.

## Orden pedagógico
1. **Modelo mental**: archivo `.py` = módulo.
2. **Importaciones básicas**: `import`, `from ... import ...`.
3. **Carpetas como paquetes**: `__init__.py`, rutas relativas, `PYTHONPATH`.
4. **Estructura recomendada de proyecto**.
5. **Evitar ciclos de importación**.
6. **Empaquetado ligero** (`if __name__ == "__main__"`).

## Objetivos de aprendizaje
- Organizar código en módulos coherentes.
- Importar funciones y clases desde otros archivos sin duplicar lógica.
- Crear paquetes con `__init__.py` y comprender rutas relativas.
- Detectar y resolver importaciones circulares.
- Preparar un módulo principal ejecutable.

## Por qué importa
Los proyectos reales no caben en un solo archivo. Separar responsabilidades facilita pruebas, reutilización y colaboración.

### Mini aventura
Imagina que tu juego favorito está hecho por equipos distintos: quienes crean personajes, quienes diseñan niveles y quienes programan la música. Si todo estuviera en un único archivo sería imposible colaborar. Los módulos son como habitaciones ordenadas dentro de una misma casa; cada persona sabe dónde dejar su trabajo y es fácil encontrarlo después.

### Cómo practicar este capítulo (muy simple)
1. Crea dos archivos: `saludos.py` y `app.py` (en la misma carpeta).
2. Ejecuta `python app.py`.
3. Si aparece un error, lee el nombre del error y la línea: es normal al aprender.

---

## 1. Módulos básicos
`saludos.py`
```python
def hola(nombre):
    return f"Hola {nombre}!"
```

`app.py`
```python
import saludos
print(saludos.hola("Ada"))
```

Salida esperada:
```
Hola Ada!
```

Reto rápido: cambia `"Ada"` por tu nombre y vuelve a ejecutar.

### `from ... import ...`
```python
from saludos import hola
print(hola("Linus"))
```

- Evita `import *`, dificulta saber qué viene de dónde.

---

## 2. Paquetes
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
    # Ejemplo: aplicar un descuento del 10%
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

Ejecuta:
```bash
python main.py
```

Salida esperada:
```
90.0
```

- `.` indica importación relativa (mismo paquete).
- `__init__.py` puede estar vacío, sirve para que Python entienda que es un paquete.

---

## 3. Nivel extra: una estructura más profesional (opcional)
Si estás empezando, puedes saltarte esta parte. Pero si quieres trabajar “como en un proyecto real”, esta estructura ayuda mucho:

```
project/
├── src/
│   ├── dominio/
│   │   ├── __init__.py
│   │   └── pedidos.py
│   ├── servicios/
│   │   └── descuentos.py
│   └── cli.py
└── tests/
```

- `src/` contiene la lógica; `tests/` separa pruebas.
- Usa rutas absolutas dentro de `src` (`from dominio.pedidos import Pedido`).

### Ejecutar desde la carpeta raíz
Cuando usas paquetes, intenta ejecutar siempre desde la carpeta raíz del proyecto. Un truco común es:

```bash
python -m src.cli
```

Eso significa: “ejecuta `cli.py` como parte del paquete `src`”, y así Python entiende mejor de dónde importar.

---

## 4. Evitar importaciones circulares

```python
# dominio.py
from servicios import descuentos  # ⚠️ si servicios importa dominio → ciclo
```

Si te pasa, no es “culpa tuya”: es un tipo de problema normal cuando crecen los proyectos.

Soluciones:
- Mueve la lógica compartida a un módulo independiente.
- Usa importaciones locales dentro de funciones para romper el ciclo:
```python
def calcular(total):
    # Import local: sólo se hace cuando llamas a la función
    from servicios.descuentos import aplicar_descuento
    return aplicar_descuento(total)
```
(La idea es que `aplicar_descuento` viva en un archivo como `servicios/descuentos.py`.)

---

## 5. Punto de entrada

```python
# cli.py
def main():
    print("Hola! Soy tu CLI")

if __name__ == "__main__":
    main()
```

- Permite ejecutar `python cli.py` o importar `main` en pruebas sin que se ejecute automáticamente.

---

## Ejercicios guiados (con TODOs)
1. **15-1 · Separar dominio y servicios**
   ```python
   # TODO 1: crea dominio/productos.py con clase Producto
   # TODO 2: crea servicios/precios.py y usa Producto
   ```
   Bonus: añade un método `aplicar_descuento(porcentaje)` en `Producto`.

2. **15-2 · CLI modular**
   ```python
   # TODO 1: crea cli.py que importe funciones desde servicios
   # TODO 2: ejecuta python -m cli para validar ruta
   ```
   Hint: si te sale `ModuleNotFoundError`, asegúrate de ejecutar desde la carpeta correcta.

3. **15-3 · Resolver ciclo**
   ```python
   # TODO 1: detecta un ciclo artificial y reorgánizalo moviendo funciones a utils
   ```
   Edge case: escribe un test que importe ambos módulos para confirmar que ya no hay ciclo.

---

## Errores comunes
- Importar con rutas relativas incorrectas (`from .. import` sin `__init__.py`).
- Duplicar código en varios módulos en lugar de importarlo.
- Ejecutar desde directorios diferentes y romper las rutas (usa `python -m`).

---

## Explicación de soluciones
1. **Dominio vs servicios**: cada área tiene su módulo; servicios importa dominio para evitar mezclar responsabilidades.
2. **CLI modular**: `cli.py` sólo orquesta; la lógica vive en `servicios`. Facilita pruebas.
3. **Resolver ciclo**: mover funciones comunes a `utils` elimina dependencias circulares y clarifica capas.

---

## Resumen
Separar el código en módulos y paquetes mantiene tu proyecto ordenado. Ahora puedes importar sólo lo necesario y crear puntos de entrada limpios.

## Reflexión final
Piensa siempre en “¿dónde vive esta pieza de lógica?”. Tener módulos claros te prepara para proyectos más grandes y frameworks como Django.
