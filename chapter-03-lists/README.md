# Capítulo 3 · Introducción a las listas

## Qué vamos a construir
En este capítulo aprenderás qué es una lista, cómo acceder a cada elemento y cómo modificarlos, ordenarlos y protegerte de errores comunes. Además, practicaremos los métodos esenciales (`append`, `insert`, `pop`, `remove`, `sort`) y escribiremos pruebas breves que garanticen el comportamiento esperado de nuestras funciones.

## Orden pedagógico
1. **Introducción**: modelo mental de una lista y por qué los corchetes (`[]`) importan.
2. **Acceso y uso**: índices, `-1` para el final y cómo reutilizar valores dentro de mensajes.
3. **Modificar/agregar/quitar**: `append`, `insert`, `del`, `pop`, `remove` y cuándo elegir cada uno.
4. **Organizar**: `sort`, `sorted`, `reverse`, `len` y cálculos rápidos.
5. **Evitar errores**: detectar `IndexError` y cómo prevenirlos.
6. **Pruebas y ejercicios guiados**: refuerzan la manipulación segura de listas.

## Objetivos de aprendizaje
- Definir una lista y acceder a sus elementos por posición o mediante índices negativos.
- Modificar elementos existentes y añadir/quitar elementos según el contexto del programa.
- Reordenar listas temporal o permanentemente y medir su longitud.
- Evitar `IndexError` mediante validaciones y uso correcto de `len()` y `-1`.
- Escribir pruebas pequeñas que confirmen que nuestras funciones manipulan listas sin efectos secundarios.

## Por qué importa
Sin listas sólo podríamos manejar un valor por variable. Las listas permiten almacenar catálogos, usuarios, pedidos o lecturas en un contenedor ordenado y dinámico. Dominar estos patrones abre la puerta a procesar cientos o miles de elementos con unos cuantos métodos y ciclos.

### Mini aventura
Piensa en una lista como una mochila con bolsillos numerados. Puedes meter cosas, sacarlas, cambiarlas de sitio y contar cuántas hay. Cuando programas, esa mochila te permite llevar “muchas cosas parecidas” sin volverte loca/o creando una variable por cada una.

---

## ¿Qué es una lista?
Una lista es una colección ordenada de elementos. En Python se definen con corchetes `[]` y los elementos se separan con comas.

```python
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Salida:
```
['trek', 'cannondale', 'redline', 'specialized']
```
Python muestra la representación literal, pero normalmente querrás acceder a cada elemento.

### Acceder a los elementos de una lista
Usa el índice (posición) dentro de corchetes para recuperar un elemento:

```python
print(bicycles[0])
print(bicycles[0].title())
```

### Los índices comienzan en 0
El primer elemento está en el índice `0`, el segundo en el `1`, etc. Para el cuarto elemento debes pedir `bicycles[3]`. Los índices negativos recorren desde el final (`-1` es el último, `-2` el penúltimo).

### Usar valores individuales de una lista
Puedes insertar elementos dentro de mensajes usando f-strings:

```python
message = f"Mi primera bicicleta fue una {bicycles[0].title()}."
print(message)
```

### Pruébalo tú (3-1 a 3-3)
1. **3-1 · Nombres**: crea una lista `names` con amistades y muestra cada nombre individualmente.
2. **3-2 · Saludos**: reutiliza la lista anterior pero imprime un saludo personalizado para cada persona.
3. **3-3 · Tu propia lista**: crea una lista de tu medio de transporte favorito y genera frases como “Me gustaría tener una …”.

---

## Modificar, añadir y eliminar elementos
Las listas son dinámicas: puedes ajustar su contenido conforme el programa avanza.

### Modificar elementos de una lista
```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Añadir elementos al final
```python
motorcycles.append('ducati')
print(motorcycles)

# Construir desde cero
equipos = []
equipos.append('frontend')
equipos.append('backend')
print(equipos)
```

### Insertar elementos en una lista
```python
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Eliminar elementos
- `del lista[i]` elimina por posición sin devolver el valor.
- `pop()` extrae el último elemento y lo retorna (acepta un índice opcional).
- `remove(valor)` localiza y elimina el primer elemento igual a `valor`.

```python
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

ultimo = motorcycles.pop()
print(f"Último: {ultimo}")

primero = motorcycles.pop(0)
print(f"Primero: {primero}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Nota: `remove` sólo elimina la primera coincidencia; si necesitas quitar todas, recorre la lista o usa comprensiones más adelante.

### Pruébalo tú (3-4 a 3-7)
1. **3-4 · Guest List**: crea una lista con invitadas/os y envía mensajes personalizados.
2. **3-5 · Changing Guest List**: reemplaza a la persona que cancela y vuelve a imprimir invitaciones.
3. **3-6 · More Guests**: informa que encontraste una mesa más grande; usa `insert` y `append` para añadir tres personas adicionales.
4. **3-7 · Shrinking Guest List**: limita la lista a dos personas usando `pop`; agradece y elimina el resto con `del`.

---

## Organizar una lista
A medida que recibes datos en orden impredecible, necesitarás presentarlos ordenados sin destruir la información original.

### Ordenar permanentemente con `sort()`
```python
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` invierte el orden alfabético y modifica la lista en sitio.

### Ordenar temporalmente con `sorted()`
```python
print(sorted(cars))          # copia ordenada
print(sorted(cars, reverse=True))
print(cars)                  # la lista original no cambió
```

### Mostrar una lista en orden inverso
```python
cars.reverse()
print(cars)
```
`reverse()` invierte el orden actual (no ordena alfabéticamente) y es reversible aplicándolo nuevamente.

### Calcular la longitud de una lista
```python
print(len(cars))
```
Saber la longitud te ayuda a validar índices y mostrar cuántos registros tienes (usuarios invitados, entradas restantes, etc.).

### Pruébalo tú (3-8 a 3-10)
1. **3-8 · Ver el mundo**: crea una lista de lugares y practica `sorted`, `reverse`, `sort` y `len` sin perder el estado original.
2. **3-9 · Invitadas/os a cenar**: a partir de los ejercicios 3-4 a 3-7, usa `len()` para decir cuántas personas invitas.
3. **3-10 · Cada función**: elige cualquier lista (montañas, ciudades, etc.) y usa cada método visto en el capítulo al menos una vez.

---

## Evitar `IndexError` al trabajar con listas
El error más común es pedir un índice fuera de rango:

```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles[3])  # IndexError
```

Consejos para prevenirlo:
- Verifica la longitud antes de acceder (`if len(motorcycles) > 2:`).
- Usa `-1` para el último elemento y evita asumir el tamaño actual.
- Cuando elimines mientras recorres, itera sobre una copia (`for item in lista[:]`).
- Al escribir funciones con índices externos, valida:
  ```python
  def obtener_elemento(lista, posicion):
      if not 0 <= posicion < len(lista):
          raise IndexError("posición fuera de rango")
      return lista[posicion]
  ```
- Si ves un `IndexError`, imprime la lista o `len(lista)` para confirmar su estado real.

### Pruébalo tú (3-11)
Fuerza un `IndexError` a propósito cambiando un índice válido por uno inválido y luego corrígelo. Entenderás mejor el flujo de Python para depurar.

---

## Mini pruebas automáticas
```python
# lists_utils.py
def priorizar_tarea(tareas, nueva):
    if not isinstance(tareas, list):
        raise TypeError("tareas debe ser una lista")
    copia = tareas[:]
    copia.insert(0, nueva)
    return copia

# tests/test_lists_utils.py
import pytest
from lists_utils import priorizar_tarea

def test_priorizar_tarea_agrega_al_inicio():
    original = ["documentar", "refactorizar"]
    resultado = priorizar_tarea(original, "configurar CI")
    assert resultado[0] == "configurar CI"
    assert original[0] == "documentar"  # la copia protege la lista original

def test_priorizar_tarea_rechaza_no_listas():
    with pytest.raises(TypeError):
        priorizar_tarea("no-lista", "algo")
```

---

## Ejemplos progresivos: jugando con los ángulos interesantes
Estos ejemplos suben de dificultad gradualmente para mostrar cómo las listas se comportan en situaciones reales de backend.

### Ejemplo 1 · Checklist interactiva
```python
checklist = ["Crear entorno virtual", "Instalar dependencias", "Correr pruebas"]

for paso in checklist:
    print(f"- [ ] {paso}")

print(f"La checklist tiene {len(checklist)} pasos.")
ultimo = checklist.pop()            # Recuperamos el último paso
print(f"Último paso completado: {ultimo}")
checklist.append("Publicar release")  # Añade una nueva tarea al final
```
- Practicas acceso directo, `len()` y mutaciones básicas (`pop`, `append`).
- Útil para scripts CLI donde los pasos cambian durante la ejecución.

### Ejemplo 2 · Cola de soporte (list as queue)
```python
cola_tickets = ["BUG-101", "BUG-102", "BUG-103"]

def atender_ticket(cola):
    if not cola:
        return None
    return cola.pop(0)  # pop(0) simula una cola FIFO

def registrar_ticket(cola, ticket):
    cola.append(ticket)

ticket_actual = atender_ticket(cola_tickets)
print(f"Atendiendo: {ticket_actual}")
registrar_ticket(cola_tickets, "BUG-200")
print(f"Pendientes: {cola_tickets}")
```
- `pop(0)` tiene un coste mayor pero clarifica la semántica FIFO; más adelante podrás reemplazarlo por `collections.deque`.
- Los métodos quedan listos para conectarse a una vista Django o a un webhook sin depender del almacenamiento todavía.

### Ejemplo 3 · Normalizador de lecturas (validaciones + pruebas)
```python
def normalizar_lecturas(lecturas, *, limite_maximo):
    if not isinstance(lecturas, list):
        raise TypeError("lecturas debe ser lista")
    if not all(isinstance(valor, (int, float)) for valor in lecturas):
        raise ValueError("todas las lecturas deben ser numéricas")
    if not lecturas:
        return {"promedio": 0, "fuera_de_rango": []}

    fuera = [valor for valor in lecturas if valor > limite_maximo]
    promedio = sum(lecturas) / len(lecturas)
    top3 = sorted(lecturas, reverse=True)[:3]
    return {"promedio": promedio, "fuera_de_rango": fuera, "top3": top3}
```

```python
# tests/test_normalizador.py
import pytest
from normalizador import normalizar_lecturas

def test_normalizar_lecturas_detecta_excesos():
    datos = [19.2, 20.1, 22.5, 18.0]
    resultado = normalizar_lecturas(datos, limite_maximo=20)
    assert resultado["fuera_de_rango"] == [22.5]
    assert resultado["top3"][0] == 22.5

def test_normalizar_lecturas_valida_tipos():
    with pytest.raises(ValueError):
        normalizar_lecturas([10, "no-num"], limite_maximo=50)
```
- Reúne slicing (`[:3]`), ordenamiento y validaciones robustas antes de integrar en una API.
- Observa cómo las pruebas describen los ángulos interesantes: detección de outliers y correcta propagación de errores de tipo.

---

## Ejercicios guiados (con TODOs)
1. **G3-1 · Invitaciones Dinámicas**
   ```python
   invitados = ["Ana", "Luis", "Marta"]
   # TODO 1: imprime un mensaje personalizado para cada invitado
   # TODO 2: agrega dos personas nuevas al final usando append
   # TODO 3: elimina al segundo invitado e imprime quién ya no asistirá
   ```
   *Pista*: `append`, `pop` y un bucle `for` bastan.

2. **G3-2 · Lista de Precios**
   ```python
   precios = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: calcula el precio promedio con sum/len
   # TODO 2: crea una lista con los precios más IVA (21%)
   # TODO 3: usa slicing para mostrar sólo los dos precios más altos
   ```
   *Pista*: combina `sorted(precios)` y `[-2:]`.

3. **G3-3 · Sensores y Validaciones**
   ```python
   lecturas = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: escribe funcion fuera_de_rango(lecturas, limite)
   # TODO 2: añade una prueba que confirme False cuando todos estan dentro
   # TODO 3: prueba que lance TypeError si lecturas no es lista
   ```
   *Pista*: usa `any(valor > limite for valor in lecturas)` y el patrón de pruebas anterior.

---

## Errores comunes
- Empezar a contar desde 1 y obtener `IndexError`.
- Modificar una lista mientras se recorre sin copiar antes.
- Confundir `append` (agrega la lista completa como un elemento) con `extend`.
- Cambiar el orden original usando `sort()` cuando necesitabas una copia ordenada (`sorted`).
- Olvidar quitar todas las apariciones de un valor al usar `remove`.

---

## Explicación de soluciones guiadas
1. **G3-1**: los mensajes se generan con un bucle `for`, `append` agrega invitados y `pop(1)` devuelve quién salió para anunciarlo.
2. **G3-2**: el promedio es `sum(precios)/len(precios)`; la lista con IVA se crea con `[precio * 1.21 for precio in precios]`; los dos mayores salen de `sorted(precios)[-2:]`.
3. **G3-3**: `any(valor > limite for valor in lecturas)` detecta desbordes tras confirmar con `isinstance(lecturas, list)`; las pruebas cubren el caso feliz y los errores tipo.

---

## Resumen
En este capítulo definiste listas, accediste a elementos mediante índices positivos y negativos, reutilizaste valores en cadenas, modificaste la lista en tiempo real (agregar, insertar, eliminar), la ordenaste de forma permanente o temporal y empleaste `len()` y `reverse()` para inspeccionarla. También aprendiste a evitar `IndexError` e incluso a escribir pruebas que validan estas operaciones.

## Reflexión final
Dominar listas significa poder manejar colecciones completas de datos con pocas líneas: puedes añadir, quitar, cortar, ordenar y validar información sin duplicar código. En el siguiente capítulo recorreremos listas de forma más eficiente para automatizar tareas repetitivas y preparar el terreno para estructuras más complejas.
