# Capítulo 5 · Conjuntos (Sets) y Membresía

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Exploraremos los conjuntos (`set` y `frozenset`) para deduplicar datos, verificar pertenencia y combinar colecciones mediante operaciones matemáticas. Crearemos ejemplos centrados en permisos, etiquetas y sincronización de datos entre servicios.

## Orden pedagógico

- **Esencial · 40–55 minutos.** Prerrequisitos: capítulos 3–4. Lee las secciones 1 y 3 y completa el ejercicio 5-0. Resultado: deduplicar datos directos, comprobar pertenencia y comparar conjuntos con `|`, `&` y `-`. Evidencia: la solución explicada cubre un caso normal, el límite del conjunto vacío, el error intencional al indexar y una recuperación correcta. Terminas cuando puedes explicar por qué un set no tiene posición `0`; continúa al capítulo 6 o detente aquí con seguridad.
- **Intermedia · 45–60 minutos.** Prerrequisitos: el checkpoint esencial y el [capítulo 10](../chapter-10-loops/README.es.md). Estudia la sección 2, los ejemplos de etiquetas y sincronización de la sección 4 y la sección 5; completa 5-1 y 5-2. Resultado: crear sets con una comprensión y elegir `frozenset` para un grupo hashable. Evidencia: vuelve a ejecutar ambos ejercicios con una entrada vacía. Esta ruta es opcional antes del capítulo 6.
- **Avance profesional opcional · 45–60 minutos.** Prerrequisitos: la ruta intermedia más [funciones](../chapter-11-functions/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pruebas](../chapter-18-testing/README.es.md). Estudia la validación de permisos, la sección 6 y 5-3. Resultado: validar un catálogo con una función, una excepción deliberada y evidencia de pytest. Puedes omitir este avance; no bloquea el siguiente capítulo esencial.

## Objetivos de aprendizaje
- Construir sets a partir de otras colecciones y eliminar duplicados.
- Verificar pertenencia en O(1) en promedio utilizando `in`.
- Aplicar operaciones de conjuntos para comparar y combinar colecciones de datos.
- Elegir entre `set` y `frozenset` según necesidades de mutabilidad.
- Escribir pruebas que cubran casos felices y límites (conjuntos vacíos, ausencia de intersecciones).

## Prerrequisitos y avances opcionales
Conviene dominar las [listas](../chapter-03-lists/README.es.md) y los [diccionarios](../chapter-04-dictionaries/README.es.md). La ruta esencial usa valores set directos y built-ins ya conocidos; no requiere definir funciones, gestionar excepciones, typing ni pytest. Las comprensiones, funciones, excepciones y pruebas quedan como avances opcionales enlazados en las rutas anteriores.

## Por qué importa
Cuando manejas correos, roles o etiquetas, los duplicados generan bugs sutiles. Los sets simplifican estos problemas con sintaxis directa y eficiente. Son especialmente útiles en backend para controlar permisos, detectar inconsistencias y sincronizar datos con otras fuentes.

### Mini aventura
Imagina que coleccionas cromos y no quieres repetidos. Un `set` es esa caja donde, si intentas meter el mismo cromo otra vez, la caja dice: “ya lo tengo”. Así de simple.

## Predice antes de ejecutar
Antes del primer ejemplo, predice el contenido del conjunto y el resultado de la pertenencia. No predigas el orden de iteración: los sets no ofrecen un orden estable y el ejemplo sólo ordena para mostrar el resultado.

---

## 1. Modelo mental: colección sin duplicados

```python runnable
correos = ["noor@example.com", "frej@example.com", "noor@example.com"]
correos_unicos = set(correos)
print(sorted(correos_unicos))  # ['frej@example.com', 'noor@example.com']

print("noor@example.com" in correos_unicos)  # True
```

- Los sets no garantizan orden. Se enfocan en la membresía.
- Convertir listas a sets es la forma más sencilla de remover duplicados.

---

## 2. Crear sets y comprehensions

**Avance intermedio opcional:** esta sección usa `range` y una comprensión de set, que el [capítulo 10](../chapter-10-loops/README.es.md) enseña en orden. En la ruta esencial puedes saltar directamente a la sección 3.

```python runnable
lenguajes = {"python", "go", "rust"}
otros = set(["python", "java"])  # desde iterable

cuadrados = {n**2 for n in range(5)}
print(sorted(cuadrados))
```

- Usa `{}` con elementos para sets literales. `{}` vacío crea un diccionario; usa `set()` para un set vacío.
- Las comprensiones de set funcionan como las de lista pero eliminan duplicados automáticamente.

---

## 3. Operaciones entre conjuntos

```python runnable
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
```python runnable
etiquetas_existentes = {"python", "django", "api"}
etiquetas_propuestas = {"python", "rest", "observability"}

nuevas = etiquetas_propuestas - etiquetas_existentes
print(f"Etiquetas a crear: {sorted(nuevas)}")
```

### Sincronización de datos
```python runnable
local_users = {"noor", "frej", "taha"}
remote_users = {"frej", "taha", "grace"}

missing = remote_users - local_users
inactive = local_users - remote_users
```

### Validación de permisos

**Avance profesional opcional:** este ejemplo define una función y lanza una excepción. Omítelo en la ruta esencial; los capítulos [11](../chapter-11-functions/README.es.md) y [14](../chapter-14-exceptions/README.es.md) enseñan antes esas herramientas.

```python runnable
def validate_permissions(assigned, allowed):
    extra = assigned - allowed
    if extra:
        raise ValueError(f"Invalid permissions: {extra}")
    return True
```

---

## 5. `frozenset` y sets como claves
Cuando necesites un set inmutable (por ejemplo, como clave en un diccionario), usa `frozenset`.

Esta es profundidad intermedia. Resulta útil, pero no es necesaria para el checkpoint esencial.

```python runnable
segments = {
    frozenset({"ios", "premium"}): "Campaign A",
    frozenset({"android", "free"}): "Campaign B",
}

query = frozenset({"premium", "ios"})
print(segments.get(query))
```

- Un `frozenset` se comporta igual que un set, excepto que no permite añadir o remover elementos.
- Ideal para definir combinaciones únicas de atributos.

---

## 6. Validación y pruebas

**Avance profesional opcional:** esta sección combina funciones, excepciones, comprobaciones de tipo y pytest. Completa primero los capítulos [11](../chapter-11-functions/README.es.md), [14](../chapter-14-exceptions/README.es.md) y [18](../chapter-18-testing/README.es.md), o copia el patrón sin tratarlo como trabajo obligatorio.

```python runnable
# permissions.py
VALID_PERMISSIONS = {"view", "edit", "delete"}

def normalize_permissions(permission_list):
    if not isinstance(permission_list, (list, set, tuple)):
        raise TypeError("permissions must be iterable")
    permissions = set(permission_list)
    invalid = permissions - VALID_PERMISSIONS
    if invalid:
        raise ValueError(f"Invalid permissions: {invalid}")
    return permissions
```

```python illustrative
# tests/test_permissions.py
import pytest
from permissions import normalize_permissions

def test_normalize_permissions_deduplicates():
    result = normalize_permissions(["view", "view", "edit"])
    assert result == {"view", "edit"}

def test_normalize_permissions_rejects_invalid():
    with pytest.raises(ValueError):
        normalize_permissions(["hack"])
```

---

## Ejercicios guiados (con TODOs)
1. **5-0 · Mapa esencial de pertenencia**

   Predice los cuatro resultados antes de escribir código. El conjunto vacío es el caso límite.

   ```python todo
   skills = ["python", "python", "git"]
   required = {"python", "sql"}
   # TODO 1: create unique_skills from skills
   # TODO 2: print membership for "python"
   # TODO 3: print the shared and missing sets in sorted order
   # TODO 4: print the size of an empty set
   ```

   *Pista*: usa `set(skills)`, `&`, `-`, `sorted(...)` y `len(set())`. No necesitas un bucle ni definir una función.

2. **5-1 · Etiquetas únicas** *(intermedia)*
   ```python todo
   etiquetas = ["api", "python", "api", "monitoring"]
   # TODO 1: convert to a set
   # TODO 2: ask the user for a new tag and add it if it doesn't exist
   # TODO 3: print how many unique tags there are
   ```
   *Pista*: Usa `if nueva not in etiquetas_set` antes de agregar.

3. **5-2 · Intersección de skills** *(intermedia)*
   ```python todo
   backend = {"python", "django", "postgres"}
   frontend = {"javascript", "react", "django"}
   # TODO 1: compute shared skills
   # TODO 2: compute backend-only skills
   # TODO 3: create a message explaining the result
   ```
   *Pista*: `backend & frontend` y `backend - frontend`.

4. **5-3 · Validar roles** *(avance profesional opcional)*
   ```python todo
   roles_permitidos = {"admin", "editor", "viewer"}
   asignados = {"admin", "auditor"}
   # TODO 1: write check_roles(asignados, permitidos)
   # TODO 2: the function must raise ValueError if it finds roles outside the catalog
   # TODO 3: add a test confirming empty sets are valid
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

### Solución esencial 5-0

Primero convierte la lista una sola vez. La intersección conserva los valores presentes en ambos sets; la diferencia conserva los requisitos que faltan. `set()` proporciona el límite vacío sin un caso especial.

```python runnable
skills = ["python", "python", "git"]
unique_skills = set(skills)
required = {"python", "sql"}

print(sorted(unique_skills))
print("python" in unique_skills)
print(sorted(unique_skills & required))
print(sorted(required - unique_skills))
print(len(set()))
```

Observa `['git', 'python']`, `True`, `['python']`, `['sql']` y `0`, en ese orden. El duplicado desaparece y el conjunto vacío sigue siendo una entrada válida.

Un set no tiene posiciones estables. Este bloque intenta indexar uno a propósito, así que la señal diagnóstica estable es `TypeError`:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
languages = {"python", "rust"}
print(languages[0])
```

Recupérate preguntando por pertenencia u ordenando solo para mostrar:

```python runnable
languages = {"python", "rust"}
print("python" in languages)
print(sorted(languages))
```

La recuperación imprime `True` y `['python', 'rust']`; no finge que el propio set haya adquirido orden.

### Notas de solución de las rutas opcionales

1. **Etiquetas únicas**: `etiquetas_unicas = set(etiquetas)` elimina duplicados; el conteo sale de `len(etiquetas_unicas)`.
2. **Intersección de skills**: `compartidas = backend & frontend` y `solo_backend = backend - frontend`; explica los resultados en un f-string.
3. **Validar roles**: la función calcula `extra = asignados - permitidos` y lanza `ValueError` si el set no está vacío; una prueba adicional verifica que `check_roles(set(), permitidos)` retorna `True`.

---

## Punto de control y autoevaluación
Completa 5-0, predice antes de cada ejecución y compara los casos normal, vacío, error y recuperación con la solución. Después explica en voz alta por qué falla `languages[0]` mientras que `"python" in languages` sí tiene sentido.

- **Corrección:** desaparecen los duplicados; la pertenencia, intersección, diferencia y el límite vacío coinciden con las observaciones.
- **Legibilidad:** los nombres describen los dos sets y solo se ordena para mostrar.
- **Gestión del error:** identificas `TypeError` como señal estable y te recuperas sin indexar ni depender del orden de iteración.
- **Verificación:** ejecutas de verdad los bloques normal, límite, error esperado y recuperación con CPython 3.11+.
- **Explicación:** diferencias pertenencia de posición y explicas una operación con tus palabras.

**Avanza cuando se cumplan los cinco puntos.** Continúa al capítulo 6; las rutas intermedia y profesional siguen siendo opcionales. Si falta uno, vuelve a las secciones 1 y 3 y repite 5-0 con `skills = []`.

## Resumen
Con los sets puedes deduplicar datos, comprobar membresía y combinar colecciones mediante operaciones declarativas. Esto simplifica la gestión de permisos, etiquetas y sincronizaciones en cualquier sistema backend.

## Reflexión final
Ya puedes detectar inconsistencias de un vistazo usando operaciones de conjuntos y validar catálogos completos antes de enviarlos a otra capa. En el próximo capítulo exploraremos tuplas para representar registros inmutables y retornos múltiples de funciones.
