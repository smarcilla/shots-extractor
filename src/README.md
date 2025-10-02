## Probar el CLI

```cmd
python -m src.cli "https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14566650" --out "data\raw_event.json"

python -m src.cli 14566650 --out "data\raw_event.json"

python -m src.cli event 14566650 --out "data\raw\event_14566650.json"

# Con id
python -m src.match_cli 14566650 --out "data\raw\event_14566650.json"

# Con URL canónica que contenga '#id:<num>'
python -m src.match_cli ""https://www.sofascore.com/es/football/match/barcelona-paris-saint-germain/UHsrgb#id:14566650" --out "data\raw\event_14566650.json"



```
