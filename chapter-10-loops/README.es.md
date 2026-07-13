# Capítulo 10 · Bucles, eficiencia y pensamiento iterativo

[English](README.md) · Español · [Català](README.ca.md) · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Qué vamos a construir
Estudiaremos `for` y `while`, patrones como enumeración, acumulación y control de salida, y daremos nuestros primeros pasos en complejidad temporal para entender el coste de repetir operaciones. Verás ejemplos con listas, diccionarios y bucles anidados, junto con métricas sencillas para estimar qué tan caro es tu código.

## Orden pedagógico
1. **Modelo mental**: un bucle como repetición controlada.
2. **`for` sobre iterables**: listas, rangos, diccionarios.
3. **`while` y condiciones**: repetir hasta que algo cambie.
4. **Contadores y acumuladores**: patrones profesionales.
5. **Bucles anidados**: cuándo usarlos y qué coste implican.
6. **Noción de complejidad**: O(n), O(n²) con ejemplos medibles.
7. **Optimización básica**: romper bucles, usar estructuras apropiadas.

## Objetivos de aprendizaje
- Escribir bucles `for` y `while` que sean fáciles de leer y razonar.
- Acumular resultados (sumas, listas nuevas) y detenerse con `break`/`continue`.
- Analizar cuántas veces se ejecuta un bucle y estimar su orden de crecimiento.
- Identificar cuándo un bucle anidado puede ser costoso y buscar alternativas.
- Validar el comportamiento de los bucles mediante pruebas simples.

## Prerrequisitos y anticipos opcionales
Antes de empezar, repasa [listas](../chapter-03-lists/README.es.md), [diccionarios](../chapter-04-dictionaries/README.es.md), [conjuntos](../chapter-05-sets/README.es.md) y [condicionales](../chapter-08-conditionals/README.es.md). Debes poder leer una colección y decidir qué rama toma una sentencia `if`.

El capítulo anticipa brevemente las [funciones](../chapter-11-functions/README.es.md) y las [pruebas con pytest](../chapter-18-testing/README.es.md). Esas partes son opcionales en una primera lectura: basta con saber que una función agrupa instrucciones y que una prueba compara el comportamiento real con el esperado.

## Por qué importa
Los bucles procesan colecciones completas, pero también pueden convertirse en cuellos de botella. Entender su comportamiento te permite escribir código que escala y detectar oportunidades de mejora antes de que llegue a producción.

### Mini aventura
Un bucle es como entrenar un movimiento en deporte: repites lo mismo muchas veces hasta que sale bien. Pero si repites “demasiadas” veces, te cansas y pierdes tiempo. Por eso aprenderemos también el coste de los bucles anidados.

## Predicción inicial
Antes de ejecutar el primer ejemplo, predice las tres líneas impresas y cuántas veces se ejecuta su cuerpo. Después responde: ¿`range(2, 8, 2)` incluye el `8` y cuántos valores produce? Escribe primero tus respuestas, ejecuta los ejemplos y explica cualquier diferencia. Así la ejecución se convierte en evidencia y no en una conjetura.

---

## 1. `for` sobre iterables

```python runnable
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

- `enumerate` añade un contador sin que tengas que llevar la cuenta manualmente.
- También funciona con cadenas, diccionarios (`for clave, valor in dic.items()`), sets (orden arbitrario) y generadores.

### Rango controlado
```python runnable
for numero in range(5):  # 0 a 4
    print(numero)
```

---

## 2. `while` cuando no conoces la cantidad de iteraciones

```python runnable
contador = 0
while contador < 3:
    print(f"Intento {contador}")
    contador += 1
```

- Define condiciones claras y actualiza las variables dentro del bucle para evitar loops infinitos.

### `break` y `continue`
```python runnable
for intento in range(5):
    if intento == 3:
        break  # detiene el bucle por completo
    if intento % 2 == 0:
        continue  # salta al siguiente valor
    print(intento)
```

---

## 3. Acumuladores y transformaciones

```python runnable
numeros = [1, 2, 3, 4]
acumulado = 0
for n in numeros:
    acumulado += n
print(acumulado)
```

### Crear nuevas colecciones
```python illustrative
cuadrados = []
for n in numeros:
    cuadrados.append(n**2)
```

- Útil cuando necesitas lógica más compleja que una comprensión de listas.

---

## 4. Bucles anidados y coste

```python runnable
datos = [[1, 2], [3, 4, 5]]
for fila in datos:
    for valor in fila:
        print(valor)
```

- Si el bucle externo recorre `n` elementos y el interno `m`, el total es `n * m` iteraciones.
- Cuando `n ≈ m`, hablamos de O(n²). Es normal en tablas pequeñas, pero caro si crece.

### Ejemplo con verificación
```python runnable
usuarios = ["noor", "frej", "taha"]
permisos = ["ver", "editar", "borrar"]
combinaciones = []
for usuario in usuarios:
    for permiso in permisos:
        combinaciones.append((usuario, permiso))
print(len(combinaciones))  # 9, producto cartesiano
```

---

## 5. Estimar complejidad de forma intuitiva

| Patrón | Iteraciones | Orden aproximado |
| --- | --- | --- |
| Recorrer lista una vez | n | O(n) |
| Dos bucles secuenciales | n + m | O(n + m) |
| Bucles anidados (n * m) | n * m | O(n·m) |
| Búsqueda lineal | n | O(n) |

- O(n) significa que el tiempo crece de forma proporcional al tamaño de la entrada.
- O(n²) crece mucho más rápido: duplicar n implica ~4× iteraciones.

### Medir con `time.perf_counter()`
```python runnable
import time

datos = list(range(100000))
start = time.perf_counter()
suma = 0
for valor in datos:
    suma += valor
end = time.perf_counter()
print(f"Loop O(n) tomó {end - start:.4f}s")
```

---

## 6. Optimización básica
- Evita bucles anidados cuando puedas usar estructuras más rápidas (`set` para búsquedas en O(1) en promedio).
- `break` tan pronto como encuentres la respuesta.
- Haz cálculos constantes fuera del bucle si no cambian.

### Ejemplo: búsqueda eficiente
```python runnable
def contiene(lista, objetivo):
    for elemento in lista:
        if elemento == objetivo:
            return True
    return False
```

- Complejidad O(n). Con un set podrías reducirlo a O(1) promedio.

---

## Ejercicios guiados (con TODOs)
1. **10-1 · Contador de vocales**
   ```python todo
   texto = "Hola mundo"
   # TODO 1: recorre el texto y cuenta cuántas vocales hay
   # TODO 2: usa un diccionario para contar cada vocal por separado
   # TODO 3: explica la complejidad
   ```
   *Pista*: un solo `for` → O(n).

2. **10-2 · Tabla de multiplicar**
   ```python todo
   # TODO 1: genera una tabla 10x10 usando bucles anidados
   # TODO 2: imprime solo los resultados mayores a 50 usando continue
   # TODO 3: describe cuántas iteraciones totales ejecuta
   ```
   *Pista*: 10 filas × 10 columnas ⇒ 100 iteraciones.

3. **10-3 · Búsqueda temprana**
   ```python todo
   usuarios = ["ana", "bruno", "carla", "diego"]
   # TODO 1: crea una función buscar_usuario(nombre)
   # TODO 2: usa break para detenerte cuando lo encuentres
   # TODO 3: agrega una prueba para el caso en que no exista
   ```
   *Pista*: `for` + `return True` cuando coincide; al final retorna False.

---

## Errores comunes
- Olvidar actualizar contadores en `while` ⇒ bucles infinitos.
- Modificar la misma lista que estás recorriendo ⇒ elementos saltados; usa una copia.
- Anidar bucles sin estimar el tamaño ⇒ tiempos de ejecución explosivos.
- Colocar trabajo pesado dentro del bucle cuando podría hacerse una vez fuera.

---

## Explicación de soluciones
1. **Contador de vocales**: un `for` recorre cada carácter; un diccionario suma frecuencias (`vocales[letra] = vocales.get(letra, 0) + 1`). Complejidad O(n).
2. **Tabla de multiplicar**: dos bucles `for` de 10 iteraciones cada uno → 100 iteraciones (O(n²) si n crece). `continue` evita imprimir resultados menores o iguales a 50.
3. **Búsqueda temprana**: `for usuario in usuarios` y `if usuario == nombre: return True`; si el bucle termina sin encontrar, retorna `False`. La prueba cubre ambos caminos.

---

## Punto de control y rúbrica
Escribe un bucle que recorra una lista de enteros, omita los negativos, se detenga en el primer cero y devuelva tanto los valores aceptados como su suma. Prueba una lista sin cero, otra que empiece por cero y otra con negativos antes del cero.

Suma un punto por criterio: **corrección** (funcionan los tres casos), **legibilidad** (nombres claros y un bucle enfocado), **flujo de control** (`continue`/`break` cumplen las reglas), **verificación** (se comprueban los resultados esperados) y **explicación** (puedes indicar el máximo de iteraciones). Con 4/5 puedes continuar; por debajo, repasa las secciones 2–5 e inténtalo de nuevo.

---

## Resumen
Te llevaste patrones concretos para iterar sobre colecciones, controlar la salida y estimar cuántas veces se ejecuta tu código. También viste cómo los bucles anidados incrementan el coste y cuándo conviene romperlos o reemplazarlos con estructuras más eficientes.

## Reflexión final
Comprender los bucles te da poder para procesar datos masivos y anticipar el impacto de tus decisiones. Esta intuición sobre complejidad será clave cuando abordemos estructuras de datos y algoritmos más avanzados.
