# src/mapping/sofa_mapper_fc.py
from typing import Any, Dict
from src.scraper.sofascore_fc import SofaClient

def map_event_to_contract(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    FASE 0 (D02):
    - Normaliza SOLO los datos del partido.
    - 'disparos' se deja como lista vacía (no se mapean tiros en esta fase).
    """
    c = SofaClient()

    # Datos básicos del partido
    home, away = c.teams(event)
    event_id = str(c.event_id(event))                     # id como string
    date_iso = c.start_iso(event) or "1970-01-01T00:00:00Z"
    home_score, away_score = c.final_score(event)         # intenta resolver marcador

    return {
        "partido": {
            "idPartido": event_id,
            "fechaISO": date_iso,
            "local": home,
            "visitante": away,
            "marcadorFinal": {"local": home_score, "visitante": away_score},
        },
        "disparos": []  # FASE 0: no normalizamos tiros todavía
    }
