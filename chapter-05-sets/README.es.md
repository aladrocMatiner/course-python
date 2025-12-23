# Capítulo 5 · Conjuntos (Sets) y Membresía

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Exploraremos los conjuntos (`set` y `frozenset`) para deduplicar datos, verificar pertenencia y combinar colecciones mediante operaciones matemáticas. Crearemos ejemplos centrados en permisos, etiquetas y sincronización de datos entre servicios.

## Orden pedagógico
1. **Concepto base**: qué significa una colección sin duplicados.
2. **Crear y consultar**: construcción desde listas, comprensión de sets, inmutabilidad.
3. **Operaciones principales**: unión, intersección, diferencia y subconjuntos.
4. **Casos reales**: permisos, etiquetas, sincronización entre fuentes.
5. **`frozenset` y uso como clave**: cuando necesitas sets inmutables.
6. **Validaciones y pruebas**: asegurar que se cumplan reglas de acceso o deduplicación.

## Objetivos de aprendizaje
- Construir sets a partir de otras colecciones y eliminar duplicados.
- Verificar pertenencia en O(1) utilizando `in`.
- Aplicar operaciones de conjuntos para comparar y combinar colecciones de datos.
- Elegir entre `set` y `frozenset` según necesidades de mutabilidad.
- Escribir pruebas que cubran casos felices y límites (conjuntos vacíos, ausencia de intersecciones).

## Por qué importa
Cuando manejas correos, roles o etiquetas, los duplicados generan bugs sutiles. Los sets simplifican estos problemas con sintaxis directa y eficiente. Son especialmente útiles en backend para controlar permisos, detectar inconsistencias y sincronizar datos con otras fuentes.

### Mini aventura
Imagina que coleccionas cromos y no quieres repetidos. Un `set` es esa caja donde, si intentas meter el mismo cromo otra vez, la caja dice: “ya lo tengo”. Así de simple.

---

## 1. Modelo mental: colección sin duplicados

```python
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(correos_unicos)  # {'noor@example.com', 'frej@example.com'}

print("noor@example.com" in correos_unicos)  # True
```

- Los sets no garantizan orden. Se enfocan en la membresía.
- Convertir listas a sets es la forma más sencilla de remover duplicados.

---

## 2. Crear sets y comprehensions

```python
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(cuadrados)
```

- Usa `{}` con elementos para sets literales. `{}` vacío crea un diccionario; usa `set()` para un set vacío.
- Las comprensiones de set funcionan como las de lista pero eliminan duplicados automáticamente.

---

## 3. Operaciones entre conjuntos

```python
permisos_admin = {"view", "edit", "delete"}
permisos_editor = {"view", "edit"}
permisos_guest = {"view"}

union = permisos_admin | permisos_guest           # {'view', 'edit', 'delete'}
interseccion = permisos_admin & permisos_editor   # {'view', 'edit'}
solo_admin = permisos_admin - permisos_editor     # {'delete'}
simetrica = permisos_admin ^ permisos_editor      # {'delete'}

print(permisos_guest <= permisos_editor)  # True: guest es subconjunto de editor
```

- `|` unión, `&` intersección, `-` diferencia, `^` diferencia simétrica.
- `<=`/`<` para comprobar si un set es subconjunto de otro.

---

## 4. Casos prácticos

### Control de etiquetas
```python
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {nuevas}")
```

### Sincronización de datos
```python
usuarios_local = {"noor", "frej", "taha"}
usuarios_remoto = {"frej", "taha", "grace"}

faltantes = usuarios_remoto - usuarios_local
inactivos = usuarios_local - usuarios_remoto
```

### Validación de permisos
```python
def validar_permisos(asignados, permitidos):
    extra = asignados - permitidos
    if extra:
        raise ValueError(f"Permisos inválidos: {extra}")
    return True
```

---

## 5. `frozenset` y sets como claves
Cuando necesites un set inmutable (por ejemplo, como clave en un diccionario), usa `frozenset`.

```python
segmentos = {
    frozenset({"ios", "premium"}): "Campaña A",
    frozenset({"android", "free"}): "Campaña B",
}

consulta = frozenset({"premium", "ios"})
print(segmentos.get(consulta))
```

- Un `frozenset` se comporta igual que un set, excepto que no permite añadir o remover elementos.
- Ideal para definir combinaciones únicas de atributos.

---

## 6. Validación y pruebas

```python
# permissions.py
PERMISOS_VALIDOS = {"view", "edit", "delete"}

def normalizar_permisos(lista_permisos):
    if not isinstance(lista_permisos, (list, set, tuple)):
        raise TypeError("permisos debe ser iterable")
    permisos = set(lista_permisos)
    invalidos = permisos - PERMISOS_VALIDOS
    if invalidos:
        raise ValueError(f"Permisos invalidos: {invalidos}")
    return permisos
```

```python
# tests/test_permissions.py
import pytest
from permissions import normalizar_permisos

def test_normalizar_permisos_elimina_duplicados():
    resultado = normalizar_permisos(["view", "view", "edit"])
    assert resultado == {"view", "edit"}

def test_normalizar_permisos_rechaza_invalidos():
    with pytest.raises(ValueError):
        normalizar_permisos(["hack"])
```

---

## Ejercicios guiados (con TODOs)
1. **5-1 · Etiquetas únicas**
   ```python
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convierte a set
   # TODO 2: pregunta al usuario por una etiqueta nueva y agrega si no existe
   # TODO 3: imprime cuántas etiquetas únicas hay
   ```
   *Pista*: Usa `if nueva not in etiquetas_set` antes de agregar.

2. **5-2 · Intersección de skills**
   ```python
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: calcula las skills compartidas
   # TODO 2: calcula las skills exclusivas de backend
   # TODO 3: crea un mensaje que explique el resultado
   ```
   *Pista*: `backend & frontend` y `backend - frontend`.

3. **5-3 · Validar roles**
   ```python
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: escribe check_roles(asignados, permitidos)
   # TODO 2: la función debe lanzar ValueError si detecta roles fuera de catálogo
   # TODO 3: agrega una prueba que confirme que conjuntos vacíos son válidos
   ```
   *Pista*: Reutiliza `extra = asignados - permitidos` y `pytest.raises`.

---

## Errores comunes
- **Intentar indexar un set**: no tienen orden ni posiciones. Convierte a lista si necesitas un índice.
- **Esperar un orden determinista**: los sets pueden cambiar el orden entre ejecuciones. No los uses para salidas UI sin convertirlos.
- **Olvidar que `{}` es un diccionario**: usa `set()` para crear un set vacío.
- **Comparar referencias en lugar de contenidos**: utiliza las operaciones de conjuntos para detectar diferencias de forma declarativa.

---

## Explicación de soluciones
1. **Etiquetas únicas**: `etiquetas_unicas = set(etiquetas)` elimina duplicados; el conteo sale de `len(etiquetas_unicas)`.
2. **Intersección de skills**: `compartidas = backend & frontend` y `solo_backend = backend - frontend`; explica los resultados en un f-string.
3. **Validar roles**: la función calcula `extra = asignados - permitidos` y lanza `ValueError` si el set no está vacío; una prueba adicional verifica que `check_roles(set(), permitidos)` retorna `True`.

---

## Resumen
Con los sets puedes deduplicar datos, comprobar membresía y combinar colecciones mediante operaciones declarativas. Esto simplifica la gestión de permisos, etiquetas y sincronizaciones en cualquier sistema backend.

## Reflexión final
Ya puedes detectar inconsistencias de un vistazo usando operaciones de conjuntos y validar catálogos completos antes de enviarlos a otra capa. En el próximo capítulo exploraremos tuplas para representar registros inmutables y retornos múltiples de funciones.
