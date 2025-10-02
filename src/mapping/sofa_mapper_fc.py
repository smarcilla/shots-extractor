# src/mapping/sofa_mapper_fc.py
from typing import Any, Dict, List
from src.scraper.sofascore_fc import SofaClient

def map_event_to_contract(event: Dict[str, Any]) -> Dict[str, Any]:
    c = SofaClient()
    home, away = c.teams(event)
    event_id = c.event_id(event)
    date_iso = c.start_iso(event) or "1970-01-01T00:00:00Z" #TODO: mejorar fecha por defecto
    raw_shots = c.shots_from_event(event)

    mapped: List[Dict[str, Any]] = []
    for s in raw_shots:
        minute = int(s.get("minute") or s.get("time") or 0)
        # identificar equipo: puede venir como "home"/"away" o ids
        team = s.get("team")
        team_side = "local" if str(team).lower() in ("home", "local", "1") else "visitante"
        player = (
            (s.get("player") or {}).get("name")
            or s.get("playerName")
            or s.get("player_name")
            or "Desconocido"
        )
        xg = float(s.get("xg") or s.get("expectedGoals") or 0.0)
        outcome = (s.get("outcome") or s.get("result") or "otro").lower()

        mapped.append({
            "minuto": minute,
            "equipo": team_side,
            "jugador": player,
            "xG": xg,
            "resultado": outcome,
        })

    return {
        "partido": {
            "id_partido": event_id,
            "fechaISO": date_iso,
            "local": home,
            "visitante": away,
            "marcadorFinal": {"local": 0, "visitante": 0},  # opcional: ajustar si está en event
        },
        "disparos": mapped
    }