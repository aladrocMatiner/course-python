# Kapitel 18 · Testning med pytest: gör idéerna säkra

[English](README.md) · [Español](README.es.md) · [Català](README.ca.md) · Svenska (aktuell) · [العربية](README.ar.md)

## Det här ska vi bygga

Vi sätter upp `pytest`, skriver tydliga tester, använder fixtures, parametriserar fall och mäter enkel coverage. Exemplen täcker funktioner, klasser och kod som höjer undantag.

## Lärväg

1. **Varför testa?**
2. **Installation och katalogstruktur**.
3. **Första testet och körning**.
4. **Fixtures**.
5. **Parametrisering**.
6. **Snabb coverage med `--cov`**.

## Lärandemål

- Installera `pytest` i projekt.
- Testa rena funktioner och kontrollerade sidoeffekter.
- Återanvänd testdata med fixtures.
- Köra flera fall i ett parametriserat test.
- Läsa grundläggande coverage-rapporter.

## Varför det spelar roll

Tester låter dig ändra utan rädsla och hittar fel före produktion.

### Miniäventyr

Före en teaterpremiär repeterar alla. Varje test är en liten repetition av rätt replik, så funktionen fungerar när användarna kommer.

### Använd kapitlet i tre steg

1. Skapa exempelfilerna exakt.
2. Kör `pytest` och leta efter `passed`.
3. Ändra medvetet ett tal och se `failed`; det tränar feldetektering.

## Förkunskaper
- Funktioner, klasser, undantag, moduler och virtuella miljöer från kapitel 11–16.
- En aktiverad lokal miljö; installation av `pytest` och `pytest-cov` kräver paketåtkomst en gång.

## Förutsäg innan du kör
Innan du kör det första testet: förutsäg dess status och den minsta kodändring som skulle få det att misslyckas. Kör båda versionerna, observera diagnostiken och återställ det godkända beteendet innan du fortsätter.

---

## 1. Installation och struktur

```bash illustrative
pip install pytest pytest-cov
mkdir tests
```

Lägg tester i `tests/` och döp dem `test_*.py`.

---

## 2. Första testet

`math_utils.py`:

```python runnable
def sumar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

`tests/test_math_utils.py`:

```python illustrative
from math_utils import sumar, dividir

def test_sumar():
    assert sumar(2, 3) == 5

def test_dividir():
    assert dividir(10, 2) == 5
```

Läs `assert` som ”säkerställ att detta är sant”; annars misslyckas testet.

Kör:

```bash illustrative
pytest
```

Kortare nybörjarvänlig utdata:

```bash illustrative
pytest -q
```

När allt stämmer syns exempelvis `2 passed`.

---

## 3. Fixtures

```python illustrative
import pytest

@pytest.fixture
def sample_pedidos():
    return [10, 20, 30]

def test_promedio(sample_pedidos):
    promedio = sum(sample_pedidos) / len(sample_pedidos)
    assert promedio == 20
```

Fixtures tillhandahåller färdig testdata.

---

## 4. Parametrisering

```python illustrative
import pytest
from math_utils import dividir

@pytest.mark.parametrize(
    "a,b,resultado",
    [ (10, 2, 5), (9, 3, 3), (5, 2, 2.5) ]
)
def test_dividir(a, b, resultado):
    assert dividir(a, b) == resultado
```

Samma test körs med flera inputs, som samma teaterstycke med olika skådespelare.

---

## 5. Undantag och `pytest.raises`

```python illustrative
from math_utils import dividir
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 6. Coverage

```bash illustrative
pytest --cov=. --cov-report=term-missing
```

Rapporten visar rader som testerna inte körde.

---

## Vägledda övningar (med TODO)

1. **18-1 · Återanvändbar fixture**

   ```python todo
   # TODO 1: create fixture db_tmp that uses tmp_path to simulate a file
   # TODO 2: use it in two tests
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

2. **18-2 · Parametrisera validering**

   ```python todo
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

3. **18-3 · Coverage**

   ```bash todo
   # TODO 1: run pytest --cov and read the report
   ```
   *Ledtråd*: utgå från närmaste exempel och verifiera ett normalfall, ett gränsfall och återhämtningen innan du läser lösningen.

---

## Vanliga misstag

- Saknat `test_`-prefix gör att pytest inte hittar filen.
- Produktionskod och testkod blandas; håll katalogerna isär.
- Fixtures med sidoeffekter återställs inte; använd `yield` för cleanup.

---

## Förklarade lösningar

1. **db_tmp**: `tmp_path / "db.json"` skapar temporär path utan att smutsa ned repot.
2. **Parametrisering**: `pytest.mark.parametrize` minskar duplicering och synliggör edge cases.
3. **Coverage**: granska saknade rader och avgör om fler tester behövs.

---

## Sammanfattning

`pytest` ger snabb feedback. Fixtures och parametrisering gör tester uttrycksfulla och lättskötta.

## Kontrollpunkt och bedömningsmatris
- **Korrekthet**: resultatet uppfyller enhetens kontrakt.
- **Läsbarhet**: namn och ansvar är tydliga vid första läsningen.
- **Felhantering**: ett normalfall, ett gränsfall och en återhämtning testas.
- **Verifiering**: exempel och övningar körs i en ren miljö.
- **Förklaring**: du kan motivera besluten och deras risker.

## Avslutande reflektion

Gör testning till vana; även små skript tjänar på verifiering före integration i större projekt.
