# src/mapping/sofa_mapper_fc.py
from typing import Any, Dict, List
from src.scraper.sofascore_fc import SofaClient

def map_event_to_contract(event: Dict[str, Any]) -> Dict[str, Any]:
    c = SofaClient()
    home, away = c.teams(event)
    event_id = str(c.event_id(event))  # el test espera string
    date_iso = c.start_iso(event) or "1970-01-01T00:00:00Z"
    raw_shots = c.shots_from_event(event)

    mapped: List[Dict[str, Any]] = []
    for s in raw_shots:
        minute = int(s.get("minute") or s.get("time") or 0)

        # identificar equipo y mapear a nombre
        team = s.get("team")
        team_str = str(team).lower()
        if team_str in ("home", "local", "1"):
            team_name = home
        elif team_str in ("away", "visitante", "2"):
            team_name = away
        else:
            # fallback por si llega id numérico o nombre ya resuelto
            team_name = home if str(team) in ("home", home, "1") else (away if str(team) in ("away", away, "2") else str(team))

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
            "equipo": team_name,
            "jugador": player,
            "xG": xg,
            "resultado": outcome,
        })

    return {
        "partido": {
            "idPartido": event_id,
            "fechaISO": date_iso,
            "local": home,
            "visitante": away,
            "marcadorFinal": {"local": 0, "visitante": 0},  # TODO: rellenar si el event lo trae
        },
        "disparos": mapped
    }
