# Capítulo 4 · Diccionarios y Datos Clave-Valor

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Aprenderás a modelar información estructurada usando diccionarios (`dict`). Trabajaremos con perfiles de usuario, configuraciones y respuestas JSON típicas de un backend. Practicaremos cómo crear, actualizar, fusionar y validar diccionarios antes de exponerlos como API o almacenarlos en una base de datos.

## Orden pedagógico
1. **Modelo mental**: diccionarios como mapas entre claves y valores.
2. **Crear y acceder**: lectura segura (`[]` vs `get`) y formatos amigables.
3. **Actualizar y eliminar**: `.update`, `del`, `pop` y valores por defecto.
4. **Recorrer**: `keys`, `values`, `items`, comprensión de diccionarios.
5. **Estructuras anidadas**: listas de dicts y dicts dentro de dicts.
6. **Validación y pruebas**: asegurar que los payloads tengan campos requeridos.

## Objetivos de aprendizaje
- Declarar diccionarios para representar entidades reales (usuarios, pedidos, configuraciones).
- Acceder y actualizar claves con seguridad, diferenciando entre lectura estricta y tolerante.
- En la ruta profesional opcional, recorrer diccionarios y transformarlos en estructuras derivadas.
- Combinar diccionarios y manejar claves anidadas sin perder consistencia.
- En la ruta profesional opcional, escribir pruebas que validen la presencia/ausencia de claves obligatorias.

## Prerrequisitos y rutas
- **Prerrequisito:** completa el checkpoint del [capítulo 3](../chapter-03-lists/README.es.md). La ruta esencial solo necesita fundamentos de listas y variables.
- **Ruta esencial · 45–60 min:** secciones 1–3, omitiendo el preview opcional de la función de formato, ejercicio 4-1 y checkpoint. Resultado: crear, leer, actualizar, fusionar y limpiar un diccionario con sentencias directas; no exige funciones.
- **Ruta intermedia · 25–35 min:** estructuras anidadas y ejercicio 4-2. Resultado: inspeccionar campos externos ausentes con `get` antes de indexar.
- **Preview profesional opcional · 35–45 min:** secciones 4 y 6 y ejercicio 4-3. Anticipan [condicionales](../chapter-08-conditionals/README.es.md), [bucles](../chapter-10-loops/README.es.md), [funciones](../chapter-11-functions/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pytest](../chapter-18-testing/README.es.md). Copia los ejemplos completos u omítelos sin bloquear el checkpoint esencial.

## Por qué importa
Los diccionarios son la base de JSON, la forma en que APIs modernas envían datos. Dominar `dict` significa manipular payloads, respuestas HTTP, parámetros y objetos de configuración sin fricción. Además, te prepara para serializar y deserializar información entre Python y otros sistemas.

### Mini aventura
Un diccionario es como la agenda del móvil: buscas un nombre (clave) y te da un dato (valor). Si sabes usar agendas, ya entiendes la idea. La magia es que tu programa puede buscar “en un segundo” sin recorrer una lista entera.

## Predicción antes de ejecutar
En el primer ejemplo `user`, predice el resultado del acceso estricto a `"username"`, del acceso tolerante a `"timezone"` ausente y del acceso estricto a esa clave ausente. Ejecuta solo los dos primeros y explica cómo `get` ofrece recuperación frente a `KeyError`.

---

## 1. Modelo mental: diccionarios como mapas
Piensa en un diccionario como una agenda telefónica: buscas una clave (nombre) y recuperas un valor (número).

```python runnable
user = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(user["username"])  # acceso estricto
print(user.get("timezone", "UTC"))  # acceso tolerante con valor por defecto
```

El acceso estricto a una clave ausente es evidencia útil. Este bloque provoca `KeyError` de forma intencional:

<!-- bookcheck: expect-error="KeyError" -->
```python expected-error
user = {"username": "noor"}
print(user["timezone"])
```

Recupérate con acceso tolerante y un valor por defecto explícito:

```python runnable
user = {"username": "noor"}
print(user.get("timezone", "UTC"))
```

- Las claves deben ser **hashable**, es decir, etiquetas de búsqueda estables para Python. Usa cadenas o números en la ruta esencial. Las claves tupla son un preview opcional posterior al [Capítulo 6](../chapter-06-tuples/README.es.md), y solo funcionan si todos sus valores también son hashable. Los valores pueden ser cualquier objeto.
- Usa `get` cuando no estés seguro de que exista la clave; evita `KeyError` y define defaults coherentes.

---

## 2. Crear, leer y normalizar valores

```python runnable
profile = {}
profile["first_name"] = "Grace"
profile["last_name"] = "Hopper"
profile.setdefault("language", "Python")  # sólo asigna si no existe

full_name = f"{profile['first_name']} {profile['last_name']}"
print(full_name)
```

- `setdefault` evita sobrescribir valores ya definidos.
- Al construir cadenas, verifica que las claves existan o usa `get` con defaults.

### Función de formateo
**Preview opcional de funciones:** `def` y `return` se enseñan en el [capítulo 11](../chapter-11-functions/README.es.md). Copia el patrón completo solo si te resulta útil u omítelo sin afectar al checkpoint esencial.

```python illustrative
def format_profile(data):
    first = data.get("first_name", "Desconocido")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Actualizar, fusionar y limpiar diccionarios

```python runnable
base_config = {"timeout": 5, "retries": 3}
user_config = {"timeout": 10, "region": "eu-west"}

final_config = base_config | user_config  # Python 3.9+: crea un nuevo dict
base_config.update({"logging": True})        # modifica en sitio

print(final_config)
print(base_config)
```

```python runnable
feature_flags = {"beta": True, "legacy": False}
legacy = feature_flags.pop("legacy")  # devuelve el valor eliminado
print(legacy)

del feature_flags["beta"]
print(feature_flags)
```

- Usa `|` o `|=` para fusionar configuraciones sin escribir bucles.
- `pop` elimina y devuelve, útil para mover valores a otro contexto.
- `del` elimina sin devolver; perfecto cuando no necesitas guardar el valor.

---

## 4. Recorrer diccionarios y construir derivados

```python runnable
permissions = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for user, role in permissions.items():
    print(f"{user} → {role}")

roles = {role for role in permissions.values()}  # set por comprensión
print(roles)

greetings = {user: f"Hola, {user.title()}" for user in permissions.keys()}
print(greetings)
```

- `items()` te da pares clave-valor.
- Las comprensiones de dict (`{clave: valor for ...}`) crean mapas derivados elegantes.

---

## 5. Estructuras anidadas

```python runnable
users = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, details in users.items():
    status = "activo" if details.get("active") else "inactivo"
    print(f"{username}: {status}")
```

```python runnable
# Diccionarios dentro de listas
api_response = {
    "results": [
        {"id": 1, "status": "ok"},
        {"id": 2, "status": "failed", "error": "timeout"},
    ],
    "meta": {"count": 2}
}

failed = [item for item in api_response["results"] if item["status"] != "ok"]
print(failed)
```

- Siempre valida que las claves existan antes de indexar; APIs externas pueden omitirlas.
- Para profundidades mayores, evalúa helpers que encapsulen el acceso a claves anidadas.

---

## 6. Validación y pruebas

```python runnable
# profiles.py
def validate_profile(data):
    required_fields = {"username", "email"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Faltan campos: {sorted(missing)}")
    if "@" not in data["email"]:
        raise ValueError("Email inválido")
    return True
```

```python illustrative
# tests/test_profiles.py
import pytest
from profiles import validate_profile

def test_validate_profile_success():
    payload = {"username": "noor", "email": "noor@example.com"}
    assert validate_profile(payload) is True

def test_validate_profile_detects_missing_fields():
    with pytest.raises(ValueError) as exc:
        validate_profile({"username": "noor"})
    assert "email" in str(exc.value)
```

Las pruebas garantizan que los diccionarios incluyan lo mínimo necesario antes de entrar a una vista o serializer.

---

## Ejercicios guiados (con TODOs)
1. **4-1 · Perfil Público**
   ```python todo
   profile = {"username": "alba", "skills": ["python", "django"]}
   # TODO 1: agrega los campos first_name y last_name
   # TODO 2: imprime un mensaje formateado usando get con valores por defecto
   # TODO 3: añade un campo "links" que sea otro dict (github, linkedin)
   ```
   *Pista*: Usa `setdefault` para no sobrescribir datos existentes.

2. **4-2 · Configuración combinada**
   ```python todo
   default = {"timeout": 5, "cache": True}
   user = {"timeout": 10, "debug": False}
   # TODO 1: crea una función merge_config(base, custom) -> dict
   # TODO 2: asegura que base no se modifique (usa copia)
   # TODO 3: escribe una prueba que confirme que base sigue igual luego del merge
   ```
   *Pista*: Usa `base | custom` o `copy()` + `update()`.

3. **4-3 · Auditoría de campos**
   ```python todo
   record = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: escribe requires_fields(record, required_fields)
   # TODO 2: la función debe devolver una tupla (valid, missing)
   # TODO 3: agrega una prueba que confirme que se permiten campos opcionales adicionales
   ```
   *Pista*: reutiliza operaciones de conjuntos (`required_fields - record.keys()`).

---

## Errores comunes
- **Asumir que la clave existe** ⇒ `KeyError`. Usa `get` o valida antes.
- **Mutar el mismo diccionario en múltiples lugares** ⇒ efectos secundarios. Crea copias (`dict.copy()`, operador `|`).
- **Confundir listas con diccionarios** ⇒ intentar indexar con números cuando el dato es `dict` o viceversa.
- **Olvidar normalizar claves** ⇒ mayúsculas/minúsculas inconsistentes generan duplicados.

---

## Explicación de soluciones
1. **Perfil Público**: `profile.setdefault("first_name", "")` permite rellenar datos sin perder lo previo; el mensaje se arma con `profile.get("first_name", "Desconocida")` para evitar errores si falta.
2. **Configuración combinada**: la función crea `merged = base | custom` (o `merged = base.copy(); merged.update(custom)`) y verifica con una prueba que `base` conserva su valor original.
3. **Auditoría de campos**: `missing = required - record.keys()` (y, si lo necesitas, `extra = record.keys() - required`) muestra con claridad qué falta o sobra y facilita mensajes de error explícitos.

---

## Checkpoint y autoevaluación

### Tarea esencial 4-0

Completa este inicio usando solo operaciones directas de diccionario:

```python todo
profile = {"username": "alba", "email": "alba@example.test"}
# TODO 1: update email and add one preference without changing profile
# TODO 2: merge profile and preference into a new dictionary
# TODO 3: remove the preference from the merged dictionary and print both
```

*Pista*: usa asignación por clave, `|`, `pop` y `get`; no necesitas funciones, bucles, sets, tuplas, manejo de excepciones ni frameworks de prueba.

### Solución explicada

Verifica la ruta normal de actualización, fusión y eliminación:

```python runnable
profile = {"username": "alba", "email": "alba@example.test"}
profile["email"] = "new@example.test"
preferences = {"theme": "dark"}
merged = profile | preferences
removed = merged.pop("theme")
print(profile)
print(merged)
print(removed)
```

Verifica el límite del diccionario vacío con acceso tolerante:

```python runnable
empty_profile = {}
print(empty_profile.get("timezone", "UTC"))
print(empty_profile)
```

Conserva tres evidencias: salida normal, default del límite vacío y `KeyError` esperado anterior seguido de su recuperación ejecutable con `get`. Reflexiona en una frase: ¿cuándo es preferible el acceso estricto `[]` al tolerante `get`?

Ejecuta la tarea 4-0 y compara el diccionario original con la copia fusionada. Después ejecuta una vez el acceso intencional a clave ausente, lee `KeyError` y recupérate con el ejemplo `get` adyacente. No uses funciones, bucles, manejo de excepciones, sets, tuplas ni frameworks de prueba.

Suma un punto por criterio:
- **Ruta normal:** actualización, fusión y `pop` producen los valores predichos.
- **Límite:** el acceso tolerante al diccionario vacío devuelve `"UTC"` sin cambiarlo.
- **Recuperación:** al `KeyError` esperado le sigue inmediatamente un acceso `get` funcional.
- **Verificación:** original y copia impresos demuestran qué operaciones mutaron datos.
- **Explicación:** justificas `[]` estricto frente a `get` tolerante para una clave concreta.

La ruta esencial termina con 4/5 o 5/5. Si no, repite la tarea 4-0 y el par error/recuperación. Funciones, iteración, registros externos anidados, helpers de validación, excepciones y pytest son evidencia de rutas posteriores.

---

## Resumen
Practicamos cómo declarar, leer, fusionar y validar diccionarios, además de recorrerlos y manejar estructuras anidadas. Ya sabes cuándo usar `[]` vs `get`, cómo mover claves con `pop`, y cómo comprobar que un payload está completo antes de procesarlo.

## Reflexión final
Cada API que construyas se apoya en diccionarios para representar datos. Ahora puedes estructurarlos con cuidado, protegerte de claves faltantes y escribir pruebas que eviten regresiones. El siguiente capítulo se centrará en `set`, perfecto para deduplicar y razonar sobre pertenencia cuando tus colecciones crecen.
