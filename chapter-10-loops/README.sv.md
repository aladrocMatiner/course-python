# Kapitel 10 · Loopar, effektivitet och iteration

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi studerar `for` och `while`, enumeration, ackumulering och tidigt avslut. Sedan tar vi första steget mot tidskomplexitet och kostnaden för upprepning, med listor, dictionaries, nästlade loopar och enkel mätning.

## Lärväg

1. **Mental modell**: kontrollerad upprepning.
2. **`for` över iterables**: listor, ranges och dictionaries.
3. **`while` och villkor** tills något ändras.
4. **Räknare och ackumulatorer**.
5. **Nästlade loopar** och deras kostnad.
6. **Komplexitetsintuition**: O(n), O(n²) och mätning.
7. **Grundoptimering**: tidigt avslut och rätt struktur.

## Lärandemål

- Skriva läsbara `for`- och `while`-loopar.
- Ackumulera summor och samlingar och styra med `break`/`continue`.
- Uppskatta antal iterationer och tillväxtordning.
- Känna igen dyra nästlade loopar och söka alternativ.
- Testa loopbeteende.

## Förkunskaper och valfria förhandsblickar

Repetera [listor](../chapter-03-lists/README.sv.md), [dictionaries](../chapter-04-dictionaries/README.sv.md), [sets](../chapter-05-sets/README.sv.md) och [villkor](../chapter-08-conditionals/README.sv.md) innan du börjar. Du ska kunna läsa en samling och avgöra vilken gren en `if`-sats tar.

Kapitlet ger korta förhandsblickar på [funktioner](../chapter-11-functions/README.sv.md) och [testning med pytest](../chapter-18-testing/README.sv.md). De delarna är valfria vid första genomgången: du behöver bara veta att en funktion grupperar instruktioner och att ett test jämför faktiskt och förväntat beteende.

## Välj en väg

- **Grundväg · 60–80 min:** avsnitt 1–3, övning 10-0, återhämtningen och grundkontrollen. Resultat: iterera säkert, ackumulera värden och använda `break`/`continue`. Direkta satser och utskrifter är bevis; funktioner, pytest, tidmätning och komplexitetsnotation krävs inte.
- **Mellanväg · 35–45 min:** avsnitt 4–5. Resultat: räkna nästlat arbete och förklara enkel tillväxt utan prestandalöften.
- **Valfri professionell väg · 30–45 min:** avsnitt 6 och funktion/test-utökningar efter [kapitel 11](../chapter-11-functions/README.sv.md) och [kapitel 18](../chapter-18-testing/README.sv.md).

## Varför det spelar roll

Loopar bearbetar hela samlingar men kan bli flaskhalsar. Förståelse för beteendet hjälper dig att skala och hitta optimering innan produktion.

### Miniäventyr

En loop liknar idrottsträning: upprepa tills rörelsen sitter. För många onödiga repetitioner slösar dock tid, särskilt i nästlade loopar.

## Förutsäg först

Förutsäg de tre utskrivna raderna och hur många gånger loopkroppen körs innan du provar det första exemplet. Svara sedan: ingår `8` i `range(2, 8, 2)`, och hur många värden skapas? Skriv svaren först, kör exemplen och förklara varje skillnad. Då blir körningen bevis i stället för en gissning.

---

## 1. `for` över iterables

```python runnable
tareas = ["instalar dependencias", "correr tests", "hacer deploy"]
for indice, tarea in enumerate(tareas, start=1):
    print(f"{indice}. {tarea}")
```

- `enumerate` lägger till räknare utan manuell bokföring.
- Det fungerar även med strängar, dictionaries via `items()`, oordnade sets och generators.

### Kontrollerade ranges

```python runnable
for numero in range(5):  # 0 to 4
    print(numero)
```

---

## 2. `while` när antalet iterationer är okänt

```python runnable
contador = 0
while contador < 3:
    print(f"Intento {contador}")
    contador += 1
```

Definiera ett tydligt villkor och uppdatera variablerna för att undvika oändliga loopar.

### `break` och `continue`

```python runnable
for intento in range(5):
    if intento == 3:
        break  # stops the loop completely
    if intento % 2 == 0:
        continue  # jumps to the next iteration
    print(intento)
```

---

## 3. Ackumulatorer och omvandlingar

```python runnable
numeros = [1, 2, 3, 4]
acumulado = 0
for n in numeros:
    acumulado += n
print(acumulado)
```

### Skapa nya samlingar

```python illustrative
cuadrados = []
for n in numeros:
    cuadrados.append(n**2)
```

Det är användbart när logiken är större än vad en tydlig list comprehension klarar.

---

## 4. Nästlade loopar och kostnad

```python runnable
datos = [[1, 2], [3, 4, 5]]
for fila in datos:
    for valor in fila:
        print(valor)
```

- Om yttre loopen går `n` och inre `m` gånger blir totalen `n * m`.
- När `n ≈ m` är det O(n²): rimligt för små tabeller men dyrt när de växer.

### Exempel med kontroll

```python runnable
usuarios = ["noor", "frej", "taha"]
permisos = ["ver", "editar", "borrar"]
combinaciones = []
for usuario in usuarios:
    for permiso in permisos:
        combinaciones.append((usuario, permiso))
print(len(combinaciones))  # 9, cartesian product
```

---

## 5. Uppskatta komplexitet intuitivt

| Mönster | Iterationer | Ungefärlig ordning |
| --- | --- | --- |
| En genomgång av lista | n | O(n) |
| Två sekventiella loopar | n + m | O(n + m) |
| Nästlade loopar | n * m | O(n·m) |
| Linjär sökning | n | O(n) |

- O(n) växer proportionellt med indatans storlek.
- O(n²) växer snabbare; dubbelt n ger ungefär fyra gånger fler iterationer.

### Mät med `time.perf_counter()`

```python runnable
import time

datos = list(range(100000))
start = time.perf_counter()
suma = 0
for valor in datos:
    suma += valor
end = time.perf_counter()
print(f"Loop O(n) took {end - start:.4f}s")
```

---

## 6. Grundläggande optimering

- Undvik nästlade loopar när en snabbare struktur finns; medlemskap i `set` är O(1) i genomsnitt.
- Använd `break` så snart resultatet hittats.
- Flytta konstant arbete utanför loopen.

### Exempel: effektiv sökning

```python runnable
def contiene(lista, objetivo):
    for elemento in lista:
        if elemento == objetivo:
            return True
    return False
```

Komplexiteten är O(n); ett set kan ge O(1) i genomsnitt.

---

## Grundövning och återhämtning

### 10-0 · Begränsad genomgång

Förutsäg accepterade värden och summan; kör sedan normal- och gränsbeteendet i en begränsad loop:

```python runnable
values = [3, -1, 4, 0, 9]
accepted = []
total = 0

for value in values:
    if value < 0:
        continue
    if value == 0:
        break
    accepted.append(value)
    total += value

print(accepted)
print(total)
```

Nästa block försöker avsiktligt iterera ett heltal; `TypeError` är den förväntade diagnostiken:

<!-- bookcheck: expect-error="TypeError" -->
```python expected-error
for item in 3:
    print(item)
```

Återhämta dig genom att ange en iterable och verifiera de tre begränsade iterationerna:

```python runnable
for item in range(3):
    print(item)
```

Dokumentera normalutskriften, gränsen med tom lista och den återhämtade utskriften. Stanna här på grundvägen.

## Vägledda övningar (med TODO)

1. **10-1 · Vokalräknare**

   ```python todo
   texto = "Hola mundo"
   # TODO 1: iterate the text and count how many vowels exist
   # TODO 2: use a dict to count each vowel separately
   # TODO 3: explain the complexity
   ```

   *Ledtråd*: en `for` ger O(n).

2. **10-2 · Multiplikationstabell**

   ```python todo
   # TODO 1: generate a 10x10 table using nested loops
   # TODO 2: print only results greater than 50 using continue
   # TODO 3: describe how many total iterations run
   ```

   *Ledtråd*: 10 rader × 10 kolumner = 100 iterationer.

3. **10-3 · Tidig sökning**

   ```python todo
   usuarios = ["ana", "bruno", "carla", "diego"]
   # TODO 1: create buscar_usuario(nombre)
   # TODO 2: use break to stop once you find it
   # TODO 3: add a test for the “not found” case
   ```

   *Ledtråd*: returnera `True` vid träff och `False` efter loopen.

---

## Vanliga misstag

- Inte uppdatera räknaren i `while`, vilket ger oändlig loop.
- Ändra listan som itereras och hoppa över element; använd kopia.
- Nästla utan att uppskatta storlek och få exploderande körtid.
- Göra tungt arbete varje varv när det kan göras en gång.

---

## Förklarade lösningar

1. **Vokaler**: en `for` per tecken och `vocales[letra] = vocales.get(letra, 0) + 1`; O(n).
2. **Tabell**: två loopar med tio varv ger 100 iterationer, eller O(n²) när n växer; `continue` hoppar över små utskrifter.
3. **Sökning**: returnera `True` vid match och `False` när loopen slutar; testa båda vägarna.

---

## Kontrollpunkt och bedömningsmatris

Anpassa 10-0 som direkta satser för tre separata listor: utan nolla, nolla först och negativa före nollan. Skriv accepterade värden och summa för varje körning; återskapa och rätta sedan `TypeError` för ett icke-itererbart objekt. Lägg inte koden i en funktion eller ett pytest-test.

Ge en poäng per kriterium: **korrekthet** (alla tre fall fungerar), **läsbarhet** (tydliga namn och en fokuserad loop), **kontrollflöde** (`continue`/`break` följer reglerna), **återhämtning** (förväntat fel följs av begränsad fungerande kod) och **bevis** (förutsägelser och utskrifter dokumenteras). 4/5 betyder att du kan fortsätta; annars repetera avsnitt 1–3. Komplexitet, mätning, funktioner och pytest är valfria bevis.

---

## Sammanfattning

Du har konkreta mönster för iteration, avslut och kostnadsuppskattning. Du ser hur nästling ökar kostnad och när tidigt avslut eller annan struktur hjälper.

## Avslutande reflektion

Loopar gör stora datamängder hanterbara och låter dig förutse konsekvenserna av designval. Den intuitionen behövs för avancerade strukturer och algoritmer.
