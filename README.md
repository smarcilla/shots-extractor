# Shots Extractor

## Descripcion

Repositorio que guarda la generación de datos base para el proyecto de Simulación de Partidos.

## Tareas Pendientes

## Probar el CLI

### Probar event_cli

```cmd
# Con id
python -m src.match_cli 14566650 --out "data\raw\event_14566650.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.match_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14566650" --out "data\raw\event_14566650.json"
```

### Probar shots_cli

```cmd
# Con id
python -m src.shots_cli 14566650 --out "data\raw\shots_14566650.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.shots_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14566650" --out "data\raw\event_14566650.json"

```

### Probar match_normalize_cli

```cmd
python -m src.event_normalize_cli "data\raw\event_14566650.json" --out-dir "data\matches"

# Windows (py launcher)
py -m src.match_normalize_cli data\raw\event_14566650.json data\raw\shots_14566650.json -o data\matches

# Cross-platform
python -m src.match_normalize_cli "data/raw/event_14566650.json" "data/raw/shots_14566650.json" --out-dir "data/matches"
```

###

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
