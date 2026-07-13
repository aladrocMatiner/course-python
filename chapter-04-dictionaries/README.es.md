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
- **Ruta esencial · 45–60 min:** secciones 1–3 y ejercicio 4-1. Resultado: crear, leer, actualizar, fusionar y limpiar un diccionario de perfil con seguridad.
- **Ruta intermedia · 25–35 min:** estructuras anidadas y ejercicio 4-2. Resultado: inspeccionar campos externos ausentes con `get` antes de indexar.
- **Preview profesional opcional · 35–45 min:** secciones 4 y 6 y ejercicio 4-3. Anticipan [condicionales](../chapter-08-conditionals/README.es.md), [bucles](../chapter-10-loops/README.es.md), [funciones](../chapter-11-functions/README.es.md), [excepciones](../chapter-14-exceptions/README.es.md) y [pytest](../chapter-18-testing/README.es.md). Copia los ejemplos completos u omítelos sin bloquear el checkpoint esencial.

## Por qué importa
Los diccionarios son la base de JSON, la forma en que APIs modernas envían datos. Dominar `dict` significa manipular payloads, respuestas HTTP, parámetros y objetos de configuración sin fricción. Además, te prepara para serializar y deserializar información entre Python y otros sistemas.

### Mini aventura
Un diccionario es como la agenda del móvil: buscas un nombre (clave) y te da un dato (valor). Si sabes usar agendas, ya entiendes la idea. La magia es que tu programa puede buscar “en un segundo” sin recorrer una lista entera.

## Predicción antes de ejecutar
En el primer ejemplo `usuario`, predice el resultado del acceso estricto a `"username"`, del acceso tolerante a `"timezone"` ausente y del acceso estricto a esa clave ausente. Ejecuta solo los dos primeros y explica cómo `get` ofrece recuperación frente a `KeyError`.

---

## 1. Modelo mental: diccionarios como mapas
Piensa en un diccionario como una agenda telefónica: buscas una clave (nombre) y recuperas un valor (número).

```python runnable
usuario = {
    "username": "noor",
    "email": "noor@example.com",
    "roles": ["admin", "editor"],
}

print(usuario["username"])  # acceso estricto
print(usuario.get("timezone", "UTC"))  # acceso tolerante con valor por defecto
```

- Las claves deben ser **hashable**. Las cadenas y números suelen ser claves hashable; una tupla solo sirve si todos sus valores internos también lo son. Por ejemplo, convierte una lista de coordenadas en tupla antes de usarla como clave. Los valores pueden ser cualquier objeto.
- Usa `get` cuando no estés seguro de que exista la clave; evita `KeyError` y define defaults coherentes.

---

## 2. Crear, leer y normalizar valores

```python runnable
perfil = {}
perfil["first_name"] = "Grace"
perfil["last_name"] = "Hopper"
perfil.setdefault("language", "Python")  # sólo asigna si no existe

nombre_completo = f"{perfil['first_name']} {perfil['last_name']}"
print(nombre_completo)
```

- `setdefault` evita sobrescribir valores ya definidos.
- Al construir cadenas, verifica que las claves existan o usa `get` con defaults.

### Función de formateo
```python runnable
def formatear_perfil(data):
    first = data.get("first_name", "Desconocido")
    last = data.get("last_name", "")
    return f"{first} {last}".strip()
```

---

## 3. Actualizar, fusionar y limpiar diccionarios

```python runnable
config_base = {"timeout": 5, "retries": 3}
config_usuario = {"timeout": 10, "region": "eu-west"}

config_final = config_base | config_usuario  # Python 3.9+: crea un nuevo dict
config_base.update({"logging": True})        # modifica en sitio

print(config_final)
print(config_base)
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
permisos = {"alice": "admin", "bob": "editor", "taha": "viewer"}

for usuario, rol in permisos.items():
    print(f"{usuario} → {rol}")

roles = {rol for rol in permisos.values()}  # set por comprensión
print(roles)

saludos = {user: f"Hola, {user.title()}" for user in permisos.keys()}
print(saludos)
```

- `items()` te da pares clave-valor.
- Las comprensiones de dict (`{clave: valor for ...}`) crean mapas derivados elegantes.

---

## 5. Estructuras anidadas

```python runnable
usuarios = {
    "noor": {"email": "noor@example.com", "active": True},
    "frej": {"email": "frej@example.com", "active": False},
}

for username, detalle in usuarios.items():
    estado = "activo" if detalle.get("active") else "inactivo"
    print(f"{username}: {estado}")
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

fallidos = [item for item in api_response["results"] if item["status"] != "ok"]
print(fallidos)
```

- Siempre valida que las claves existan antes de indexar; APIs externas pueden omitirlas.
- Para profundidades mayores, evalúa helpers que encapsulen el acceso a claves anidadas.

---

## 6. Validación y pruebas

```python runnable
# profiles.py
def validar_perfil(datos):
    campos_requeridos = {"username", "email"}
    faltantes = campos_requeridos - datos.keys()
    if faltantes:
        raise ValueError(f"Faltan campos: {sorted(faltantes)}")
    if "@" not in datos["email"]:
        raise ValueError("Email inválido")
    return True
```

```python illustrative
# tests/test_profiles.py
import pytest
from profiles import validar_perfil

def test_validar_perfil_exitoso():
    payload = {"username": "noor", "email": "noor@example.com"}
    assert validar_perfil(payload) is True

def test_validar_perfil_detecta_campos_faltantes():
    with pytest.raises(ValueError) as exc:
        validar_perfil({"username": "noor"})
    assert "email" in str(exc.value)
```

Las pruebas garantizan que los diccionarios incluyan lo mínimo necesario antes de entrar a una vista o serializer.

---

## Ejercicios guiados (con TODOs)
1. **4-1 · Perfil Público**
   ```python todo
   perfil = {"username": "alba", "skills": ["python", "django"]}
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
   registro = {"id": 1, "status": "ok", "duration_ms": 120}
   # TODO 1: escribe requires_fields(registro, campos_obligatorios)
   # TODO 2: la función debe devolver una tupla (valido, faltantes)
   # TODO 3: agrega una prueba que confirme que se permiten campos opcionales adicionales
   ```
   *Pista*: reutiliza operaciones de conjuntos (`campos_obligatorios - registro.keys()`).

---

## Errores comunes
- **Asumir que la clave existe** ⇒ `KeyError`. Usa `get` o valida antes.
- **Mutar el mismo diccionario en múltiples lugares** ⇒ efectos secundarios. Crea copias (`dict.copy()`, operador `|`).
- **Confundir listas con diccionarios** ⇒ intentar indexar con números cuando el dato es `dict` o viceversa.
- **Olvidar normalizar claves** ⇒ mayúsculas/minúsculas inconsistentes generan duplicados.

---

## Explicación de soluciones
1. **Perfil Público**: `perfil.setdefault("first_name", "")` permite rellenar datos sin perder lo previo; el mensaje se arma con `perfil.get("first_name", "Desconocida")` para evitar errores si falta.
2. **Configuración combinada**: la función crea `merged = base | custom` (o `merged = base.copy(); merged.update(custom)`) y verifica con una prueba que `base` conserva su valor original.
3. **Auditoría de campos**: `faltantes = campos_obligatorios - registro.keys()` (y, si lo necesitas, `sobrantes = registro.keys() - campos_obligatorios`) muestra con claridad qué falta o sobra y facilita mensajes de error explícitos.

---

## Checkpoint y autoevaluación
Crea un diccionario de perfil con `username`, `email` y un diccionario `links` anidado. Predice un acceso a clave existente y otro a clave ausente con `get`. Actualiza el email, fusiona preferencias sin cambiar el original y solicita a propósito una clave ausente con `[]`; recupérate sustituyéndolo por `get` y un valor por defecto explícito.

Suma un punto por criterio:
- **Corrección:** el diccionario final contiene los valores actualizados y fusionados esperados.
- **Legibilidad:** las claves describen sus valores y el anidamiento se sigue con facilidad.
- **Manejo del error:** explicas `KeyError` y te recuperas con validación o `get`.
- **Verificación:** imprimes original y fusionado y demuestras cuál cambió.
- **Explicación:** explicas por qué una clave debe ser hashable y por qué una tupla que contiene una lista no es válida.

La ruta esencial termina con 5/5. La opcional añade tests de campos ausentes, extra y válidos.

---

## Resumen
Practicamos cómo declarar, leer, fusionar y validar diccionarios, además de recorrerlos y manejar estructuras anidadas. Ya sabes cuándo usar `[]` vs `get`, cómo mover claves con `pop`, y cómo comprobar que un payload está completo antes de procesarlo.

## Reflexión final
Cada API que construyas se apoya en diccionarios para representar datos. Ahora puedes estructurarlos con cuidado, protegerte de claves faltantes y escribir pruebas que eviten regresiones. El siguiente capítulo se centrará en `set`, perfecto para deduplicar y razonar sobre pertenencia cuando tus colecciones crecen.
