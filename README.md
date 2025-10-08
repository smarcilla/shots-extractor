# Shots Extractor

## Descripcion

Repositorio que guarda la generación de datos base para el proyecto de Simulación de Partidos.

## Tareas Pendientes

## Probar el CLI

### Probar event_cli

```cmd
# Con id
python -m src.match_cli 14083630 --out "data\raw\event_14083630.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.match_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14083630" --out "data\raw\event_14083630.json"
```

### Probar shots_cli

```cmd
# Con id
python -m src.shots_cli 14083630 --out "data\raw\shots_14083630.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.shots_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14083630" --out "data\raw\event_14083630.json"

```

### Probar match_normalize_cli

```cmd
python -m src.event_normalize_cli "data\raw\event_14083630.json" --out-dir "data\matches"

# Windows (py launcher)
py -m src.match_normalize_cli data\raw\event_14083630.json data\raw\shots_14083630.json -o data\matches

# Cross-platform
python -m src.match_normalize_cli "data/raw/event_14083630.json" "data/raw/shots_14083630.json" --out-dir "data/matches"
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

## Ejecutar el servidor FastAPI en local

1. Instala dependencias de runtime si aún no lo hiciste:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Copia el archivo de ejemplo de variables de entorno y personalízalo:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales Supabase (URL y service key)
   ```
3. Arranca el servidor con Uvicorn:
   ```bash
   uvicorn src.api.app:create_app --reload
   ```
   El endpoint quedará disponible en `http://localhost:8000/v1/shots/publish`.

> Nota: `python-dotenv` cargará automáticamente el fichero `.env` al iniciar la app. Asegúrate de que `SUPABASE_URL` y `SUPABASE_SERVICE_KEY` están definidos antes de llamar al endpoint.
