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
```

`servicios.py`
```python
from .dominio import Pedido

def procesar_pedido(pedido: Pedido):
    ...
```

- `.` indica importación relativa (mismo paquete).
- `__init__.py` puede estar vacío, sirve para que Python entienda que es un paquete.

---

## 3. Organización sugerida
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

### `PYTHONPATH`
Ejecuta con `python -m src.cli` desde la raíz para que Python conozca el paquete.

---

## 4. Evitar importaciones circulares

```python
# dominio.py
from servicios import descuentos  # ⚠️ si servicios importa dominio → ciclo
```

Soluciones:
- Mueve la lógica compartida a un módulo independiente.
- Usa importaciones locales dentro de funciones para romper el ciclo:
```python
def calcular():
    from servicios import descuentos
    ...
```

---

## 5. Punto de entrada

```python
# cli.py
def main():
    ...

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

2. **15-2 · CLI modular**
   ```python
   # TODO 1: crea cli.py que importe funciones desde servicios
   # TODO 2: ejecuta python -m cli para validar ruta
   ```

3. **15-3 · Resolver ciclo**
   ```python
   # TODO 1: detecta un ciclo artificial y reorgánizalo moviendo funciones a utils
   ```

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
