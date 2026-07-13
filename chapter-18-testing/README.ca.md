# Capítol 18 · Proves amb pytest: protegeix les teves idees

[English](README.md) · [Español](README.es.md) · Català · [Svenska](README.sv.md) · [العربية](README.ar.md)

## Què construirem
Prepararem un entorn de proves amb `pytest`, aprendrem a escriure tests clars, utilitzarem fixtures, parametritzarem casos i mesurarem una cobertura bàsica. Veuràs exemples per a funcions, classes i codi que llança excepcions.

## Itinerari d'aprenentatge
1. **Per què fem proves?**
2. **Instal·lació i estructura de carpetes**.
3. **Primera prova i com executar-la**.
4. **Fixtures**.
5. **Parametrització**.
6. **Cobertura ràpida amb `--cov`**.

## Objectius d'aprenentatge
- Configurar `pytest` als teus projectes.
- Escriure proves per a funcions pures i efectes secundaris controlats.
- Reutilitzar dades de prova amb fixtures.
- Parametritzar llistes de casos en una sola prova.
- Llegir informes bàsics de cobertura.

## Per què és important
Les proves et permeten modificar el codi sense por i trobar errors abans que arribin a producció.

### Miniaventura
Abans d'estrenar una obra es fa un assaig general. Imagina cada test com un petit assaig: comproves que cada personatge digui la frase correcta. Quan arriba el públic, és a dir, les persones usuàries, la funció actua sense pànic d'última hora.

### Com utilitzar aquest capítol en tres passos
1. Crea els fitxers d'exemple exactament com es mostren.
2. Executa `pytest` i busca `passed`.
3. Canvia expressament un número per veure un `failed`; és normal, estàs aprenent a detectar errors.

## Prerequisits
Capítols previs recomanats: 11, 12, 14, 16.
Usa CPython 3.11+ en un entorn local d’un sol ús i mantén les dades, els secrets i els serveis fora de sistemes reals.

---

## 1. Instal·lació i estructura

```bash illustrative
pip install pytest pytest-cov
mkdir tests
```

- Desa els tests a `tests/` i anomena els fitxers `test_*.py`.

---

## 2. Primera prova
`math_utils.py`
```python runnable
def sumar(a, b):
    return a + b

def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir entre cero")
    return a / b
```

`tests/test_math_utils.py`
```python illustrative
from math_utils import sumar, dividir

def test_sumar():
    assert sumar(2, 3) == 5

def test_dividir():
    assert dividir(10, 2) == 5
```

Llegeix `assert` com «assegura't que això sigui cert». Si no ho és, el test falla.

Executa:
```bash illustrative
pytest
```

Per obtenir una sortida més curta i còmoda al principi:
```bash illustrative
pytest -q
```

Quan tot va bé, veuràs alguna cosa com `2 passed`.

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

- Les fixtures són funcions que proporcionen dades de prova llestes per utilitzar.

---

## 4. Parametrització

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

- Una sola prova s'executa diverses vegades amb entrades diferents.
- Pensa-hi com una llista d'assaig: el mateix guió amb intèrprets diferents.

---

## 5. Excepcions i `pytest.raises`

```python illustrative
from math_utils import dividir
import pytest

def test_dividir_por_cero():
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)
```

---

## 6. Cobertura

```bash illustrative
pytest --cov=. --cov-report=term-missing
```

- Mostra quines línies no han estat executades pels tests.

---

## Exercicis guiats (amb TODO)
1. **18-1 · Fixture reutilitzable**
   ```python todo
   # TODO 1: create fixture db_tmp that uses tmp_path to simulate a file
   # TODO 2: use it in two tests
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

2. **18-2 · Parametritzar validacions**
   ```python todo
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

3. **18-3 · Cobertura**
   ```bash todo
   # TODO 1: run pytest --cov and read the report
   ```
   *Pista*: comença per l’exemple més proper i verifica un cas vàlid, un límit i la recuperació abans de mirar la solució.

---

## Errors habituals
- Oblidar el prefix `test_`, de manera que pytest no detecta el fitxer.
- Barrejar el codi de producció amb el de prova; mantén carpetes separades.
- Crear fixtures amb efectes secundaris que no es restauren; utilitza `yield` per fer cleanup.

---

## Solucions explicades
1. **Fixture `db_tmp`**: `tmp_path / "db.json"` crea rutes temporals sense embrutar el repositori.
2. **Parametrització**: `pytest.mark.parametrize` redueix duplicació i t'obliga a pensar en casos límit.
3. **Cobertura**: mira les línies que falten i decideix si calen més proves.

---

## Resum
`pytest` et dona un bucle de feedback ràpid per validar cada mòdul. Amb fixtures i parametrització, els tests són expressius i fàcils de mantenir.

## Punt de control i rúbrica
- **Correcció**: el resultat compleix el contracte de la unitat.
- **Llegibilitat**: els noms i les responsabilitats s’entenen a la primera.
- **Errors**: es proven un cas vàlid, un límit i una recuperació.
- **Verificació**: els exemples i els exercicis s’executen en un entorn net.
- **Explicació**: pots justificar les decisions i els riscos.

## Reflexió final
Converteix les proves en un hàbit: fins i tot els scripts petits es beneficien de verificar el comportament abans d'integrar-los en projectes més grans.
