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
- Funcions, classes, excepcions, mòduls i entorns virtuals dels capítols 11–16.
- Un entorn local activat; instal·lar `pytest` i `pytest-cov` requereix accés als paquets una vegada.

## Prediu abans d'executar
Abans d'executar la primera prova, prediu-ne l'estat i el canvi de codi més petit que faria que fallés. Executa totes dues versions, observa el diagnòstic i restaura el comportament correcte abans de continuar.

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
   *Pista*: escriu mitjançant `tmp_path / "db.json"`; pytest elimina el directori temporal després de la prova.

2. **18-2 · Parametritzar validacions**
   ```python todo
   # TODO 1: create test validacion_payload with multiple valid/invalid inputs
   ```
   *Pista*: parametritza parells `(payload, expected)` i assigna ids llegibles als casos no vàlids.

3. **18-3 · Cobertura**
   ```bash todo
   # TODO 1: run pytest --cov and read the report
   ```
   *Pista*: tracta les línies sense cobrir com a preguntes sobre el comportament, no com un percentatge objectiu per si sol.

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
- **Correcció**: les proves cobreixen el comportament normal, els límits i les excepcions.
- **Llegibilitat**: els noms indiquen el comportament i la fallada que es protegeixen.
- **Gestió d'errors**: els fixtures netegen els efectes secundaris fins i tot quan falla una asserció.
- **Verificació**: executa `pytest -q` des d'un entorn net i inspecciona una fallada intencional.
- **Explicació**: explica què demostra cada prova més enllà de la seva línia de cobertura.

## Reflexió final
Converteix les proves en un hàbit: fins i tot els scripts petits es beneficien de verificar el comportament abans d'integrar-los en projectes més grans.
