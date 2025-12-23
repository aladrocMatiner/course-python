# Capítol 3 · Introducció a les llistes

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
En aquest capítol aprendràs què és una llista, com accedir a cada element i com modificar-los, ordenar-los i protegir-te d’errors comuns. També practicarem mètodes essencials (`append`, `insert`, `pop`, `remove`, `sort`) i escriurem mini proves perquè les nostres funcions facin el que toca.

## Ordre pedagògic
1. **Introducció**: model mental d’una llista i per què els claudàtors (`[]`) importen.
2. **Accés i ús**: índexos, `-1` per anar al final i com reutilitzar valors en missatges.
3. **Modificar/afegir/treure**: `append`, `insert`, `del`, `pop`, `remove` i quan triar cada un.
4. **Organitzar**: `sort`, `sorted`, `reverse`, `len` i comprovacions ràpides.
5. **Evitar errors**: detectar `IndexError` i prevenir-lo.
6. **Proves i exercicis guiats**: per fer les llistes segures.

## Objectius d’aprenentatge
- Definir una llista i accedir als elements amb índexos positius i negatius.
- Modificar elements i afegir/treure dades segons el context.
- Reordenar llistes de forma temporal o permanent i mesurar la longitud.
- Evitar `IndexError` validant índexos i usant bé `len()` i `-1`.
- Escriure proves petites per comprovar que una funció no modifica dades “sense voler”.

## Per què importa
Sense llistes, només podríem guardar un valor per variable. Les llistes permeten tenir catàlegs, usuaris, comandes o lectures en un contenidor ordenat i dinàmic. Dominar això obre la porta a processar centenars (o milers) d’elements amb pocs mètodes i bucles.

### Mini aventura
Imagina una llista com una motxilla amb butxaques numerades. Pots posar coses, treure-les, canviar-les de lloc i comptar quantes n’hi ha. Programant, aquesta motxilla t’evita crear una variable per a cada cosa.

---

## Què és una llista?
Una llista és una col·lecció ordenada d’elements. En Python es defineixen amb `[]` i els elements se separen amb comes.

```python
# bicycles.py
bicycles = ["trek", "cannondale", "redline", "specialized"]
print(bicycles)
```

Sortida:
```
['trek', 'cannondale', 'redline', 'specialized']
```
Python mostra la representació literal, però normalment voldràs accedir a cada element.

### Accedir als elements d’una llista
Usa l’índex (posició) dins dels claudàtors per recuperar un element:

```python
print(bicycles[0])
print(bicycles[0].title())
```

### Els índexos comencen en 0
El primer element és a l’índex `0`, el segon a l’`1`, etc. Per al quart element has de demanar `bicycles[3]`. Els índexos negatius compten des del final (`-1` és l’últim, `-2` el penúltim).

### Usar valors individuals d’una llista
Pots inserir elements dins d’un missatge amb f-strings:

```python
message = f"La meva primera bicicleta va ser una {bicycles[0].title()}."
print(message)
```

Exemple amb persones:
```python
names = ["Noor", "Frej", "Taha"]
print(names[0])
print(f"Hola, {names[1]}!")
```

### Prova-ho tu (3-1 a 3-3)
1. **3-1 · Noms**: crea una llista `names` i mostra cada nom.
2. **3-2 · Salutacions**: reutilitza la llista i imprimeix una salutació personalitzada.
3. **3-3 · La teva llista**: crea una llista del teu transport favorit i fes frases com “M’agradaria tenir una …”.

---

## Modificar, afegir i eliminar elements
Les llistes són dinàmiques: pots ajustar el contingut mentre el programa funciona.

### Modificar elements d’una llista
```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles)

motorcycles[0] = 'ducati'
print(motorcycles)
```

### Afegir elements al final
```python
motorcycles.append('ducati')
print(motorcycles)

# Construir des de zero
equipos = []
equipos.append('frontend')
equipos.append('backend')
print(equipos)
```

### Inserir elements
```python
motorcycles.insert(0, 'victory')
print(motorcycles)
```

### Eliminar elements
- `del lista[i]` elimina per posició sense retornar el valor.
- `pop()` extreu l’últim element i el retorna (accepta un índex opcional).
- `remove(valor)` localitza i elimina el primer element igual a `valor`.

```python
motorcycles = ['honda', 'yamaha', 'suzuki', 'ducati']

ultimo = motorcycles.pop()
print(f"Último: {ultimo}")

primero = motorcycles.pop(0)
print(f"Primero: {primero}")

motorcycles.remove('yamaha')
print(motorcycles)
```

> Nota: `remove` només elimina la primera coincidència. Més endavant aprendrem a eliminar-ne totes.

### Prova-ho tu (3-4 a 3-7)
1. **3-4 · Guest List**: crea una llista d’invitats i envia missatges.
2. **3-5 · Changing Guest List**: reemplaça algú que cancel·la i reimprimeix invitacions.
3. **3-6 · More Guests**: anuncia una taula més gran i afegeix tres persones amb `insert` i `append`.
4. **3-7 · Shrinking Guest List**: redueix a dues persones amb `pop` i elimina la resta amb `del`.

---

## Organitzar una llista
Quan les dades arriben en un ordre imprevisible, sovint cal presentar-les ordenades sense destruir l’ordre original.

### Ordenar permanentment amb `sort()`
```python
cars = ['bmw', 'audi', 'toyota', 'subaru']
cars.sort()
print(cars)  # ['audi', 'bmw', 'subaru', 'toyota']
```
`cars.sort(reverse=True)` inverteix l’ordre alfabètic i modifica la llista.

### Ordenar temporalment amb `sorted()`
```python
print(sorted(cars))          # còpia ordenada
print(sorted(cars, reverse=True))
print(cars)                  # l’original no ha canviat
```

### Mostrar en ordre invers
```python
cars.reverse()
print(cars)
```
`reverse()` inverteix l’ordre actual (no ordena alfabèticament) i és reversible si el tornes a aplicar.

### Longitud d’una llista
```python
print(len(cars))
```
La longitud t’ajuda a validar índexos i a mostrar quants elements tens.

### Prova-ho tu (3-8 a 3-10)
1. **3-8 · Veure el món**: practica `sorted`, `reverse`, `sort` i `len` sense perdre l’estat original.
2. **3-9 · Invitats a sopar**: usa `len()` per dir quanta gent invites.
3. **3-10 · Cada funció**: crea qualsevol llista i usa cada mètode del capítol com a mínim un cop.

---

## Evitar `IndexError` treballant amb llistes
L’error més comú és demanar un índex fora de rang:

```python
motorcycles = ['honda', 'yamaha', 'suzuki']
print(motorcycles[3])  # IndexError
```

Consells per prevenir-ho:
- Comprova la longitud abans d’accedir (`if len(motorcycles) > 2:`).
- Usa `-1` per a l’últim element i evita assumir la mida.
- Si elimines mentre iteres, recorre una còpia (`for item in lista[:]`).
- Si una funció rep un índex extern, valida’l:
  ```python
  def obtener_elemento(lista, posicion):
      if not 0 <= posicion < len(lista):
          raise IndexError("posición fuera de rango")
      return lista[posicion]
  ```
- Si tens un `IndexError`, imprimeix la llista o `len(lista)` per confirmar l’estat real.

### Prova-ho tu (3-11)
Força un `IndexError` a propòsit canviant un índex vàlid per un d’invàlid i després corregeix-lo.

---

## Mini proves automàtiques
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

## Exemples progressius: jugant amb angles interessants
Aquests exemples pugen de dificultat i mostren com es comporten les llistes en situacions més reals.

### Exemple 1 · Checklist interactiva
```python
checklist = ["Crear entorno virtual", "Instalar dependencias", "Correr pruebas"]

for paso in checklist:
    print(f"- [ ] {paso}")

print(f"La checklist tiene {len(checklist)} pasos.")
ultimo = checklist.pop()            # Recuperamos el último paso
print(f"Último paso completado: {ultimo}")
checklist.append("Publicar release")  # Añade una nueva tarea al final
```
- Practiques `len()` i mutacions bàsiques (`pop`, `append`).

### Exemple 2 · Cua de suport (list as queue)
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
- `pop(0)` és més car, però fa clara la semàntica FIFO; més endavant el canviaràs per `collections.deque`.

### Exemple 3 · Normalitzador de lectures (validacions + proves)
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

---

## Exercicis guiats (amb TODOs)
1. **G3-1 · Invitacions dinàmiques**
   ```python
   invitados = ["Noor", "Luis", "Marta"]
   # TODO 1: imprimeix un missatge personalitzat per a cada convidat
   # TODO 2: afegeix dues persones al final amb append
   # TODO 3: elimina el segon convidat i imprimeix qui ja no vindrà
   ```
   *Pista*: amb `append`, `pop` i un `for` n’hi ha prou.

2. **G3-2 · Llista de preus**
   ```python
   precios = [12.5, 9.99, 3.5, 18.0]
   # TODO 1: calcula el preu mitjà amb sum/len
   # TODO 2: crea una llista amb els preus amb IVA (21%)
   # TODO 3: usa slicing per mostrar només els dos preus més alts
   ```
   *Pista*: combina `sorted(precios)` i `[-2:]`.

3. **G3-3 · Sensors i validacions**
   ```python
   lecturas = [19.2, 20.1, 21.3, 18.9]
   # TODO 1: escriu funció fuera_de_rango(lecturas, limite)
   # TODO 2: afegeix una prova que confirmi False quan tot és dins
   # TODO 3: prova que llanci TypeError si lecturas no és una llista
   ```
   *Pista*: usa `any(valor > limite for valor in lecturas)`.

---

## Errors comuns
- Començar a comptar des d’1 i obtenir `IndexError`.
- Modificar una llista mentre la recorres sense copiar abans.
- Confondre `append` (afegeix la llista com a element) amb `extend`.
- Canviar l’ordre original amb `sort()` quan necessitaves una còpia (`sorted`).
- Oblidar que `remove` només elimina la primera aparició.

---

## Explicació de solucions guiades
1. **G3-1**: missatges amb `for`, `append` per afegir, `pop(1)` per treure i anunciar.
2. **G3-2**: mitjana `sum(precios)/len(precios)`; IVA amb `[precio * 1.21 for precio in precios]`; top2 amb `sorted(precios)[-2:]`.
3. **G3-3**: `any(...)` detecta fora de rang després de validar el tipus amb `isinstance`.

---

## Resum
Has definit llistes, has accedit a elements amb índexos positius i negatius, has reutilitzat valors en cadenes, has modificat la llista en temps real, l’has ordenat i has fet servir `len()` i `reverse()`. També has après a evitar `IndexError` i a escriure proves.

## Reflexió final
Dominar llistes és poder manejar col·leccions completes amb poques línies: afegir, treure, tallar, ordenar i validar dades sense duplicar codi. Al següent capítol entrarem en `dict` (diccionaris), que és la base de JSON i de moltes APIs.
