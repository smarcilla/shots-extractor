## Probar el CLI

### Probar event_cli

```cmd
# Con id
python -m src.match_cli 14566650 --out "data\raw\event_14566650.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.match_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14566650" --out "data\raw\event_14566650.json"
```

### Probar event_normalize_cli

```cmd
python -m src.event_normalize_cli "data\raw\event_14566650.json" --out-dir "data\matches"
```

## Probar los tests

```cmd
python -m pip install -r requirements-dev.txt


REM 1) Activa tu venv (si no lo está)
.\.venv\Scripts\activate

REM 2) Asegúrate de que el repo raíz está en PYTHONPATH (evita el 'No module named src')
set PYTHONPATH=.

REM 3) Ejecuta todos los tests
python -m pytest -q

```
