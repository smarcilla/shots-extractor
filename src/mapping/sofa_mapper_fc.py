# src/mapping/sofa_mapper_fc.py
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
import math
from src.scraper.sofascore_fc import SofaClient

def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except Exception:
        return default

def _safe_int(v: Any, default: int = 0) -> int:
    try:
        # Algunos campos vienen como float (p.ej. 3.0)
        i = int(round(float(v)))
        return i
    except Exception:
        return default

_SITUATION_MAP = {
    "assisted": "Asistencia",
    "corner": "Córner",
    "free-kick": "Tiro libre",
    "set-piece": "Balón parado",
    "fast-break": "Contraataque",
    "regular": "Juego abierto",
    "penalty": "Penalti",
    "throw-in": "Saque de banda",
}
_RESULTADO_MAP = {
    "goal": "Gol",
    "save": "Parada",
    "block": "Bloqueo",
    "miss": "Fallado",
    "post": "Poste",
}
_BODY_MAP = {
    "left-foot": "Zurdo",
    "right-foot": "Diestro",
    "head": "Cabeza",
}

def _norm_situation(s: Optional[str]) -> str:
    if not s:
        return "Desconocida"
    s = str(s).strip().lower()
    return _SITUATION_MAP.get(s, s.capitalize())

def _norm_resultado(s: Optional[str]) -> str:
    if not s:
        return "Desconocido"
    s = str(s).strip().lower()
    return _RESULTADO_MAP.get(s, s.capitalize())

def _norm_bodypart(s: Optional[str]) -> str:
    if not s:
        return "Otro"
    s = str(s).strip().lower()
    return _BODY_MAP.get(s, "Otro")

def _minute(time_val: Any, added_time_val: Any) -> int:
    base = _safe_int(time_val, 0)
    # addedTime puede ser float/NaN; solo sumar si es número válido
    try:
        at = float(added_time_val)
        if math.isnan(at) or math.isinf(at):
            at = 0.0
    except Exception:
        at = 0.0
    return _safe_int(base + at, base)

def _shots_array(shots: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Acepta:
      - Lista de disparos
      - Dict con clave 'shots' (u otra variante en el futuro)
    """
    if isinstance(shots, list):
        return shots
    if isinstance(shots, dict):
        # soporte común: shots / attempts / items
        for key in ("shots", "attempts", "items"):
            v = shots.get(key)
            if isinstance(v, list):
                return v
    return []

def _map_one_shot(raw: Dict[str, Any], home_name: str, away_name: str) -> Dict[str, Any]:
    player = raw.get("player") or {}
    jugador = player.get("name") or player.get("shortName") or "Anónimo"

    is_home = bool(raw.get("isHome"))
    equipo = home_name if is_home else away_name

    minuto = _minute(raw.get("time"), raw.get("addedTime"))
    xg = _safe_float(raw.get("xg"), 0.0)
    xgot = _safe_float(raw.get("xgot"), 0.0)

    situacion = _norm_situation(raw.get("situation"))
    resultado = _norm_resultado(raw.get("shotType"))
    tipo_disparo = _norm_bodypart(raw.get("bodyPart"))

    return {
        "minuto": minuto,
        "equipo": equipo,
        "jugador": jugador,
        "xG": xg,
        "xGOT": xgot,
        "situacion": situacion,
        "resultado": resultado,
        "tipo_disparo": tipo_disparo,
    }

def _to_iso8601(v: str) -> str:
    if v is None:
        return "1970-01-01T00:00:00Z"
    s = str(v).strip()
    if s.isdigit():  # epoch seconds o millis
        ts = int(s)
        if len(s) == 13:  # millis
            ts = ts / 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    return s  # asumimos ya viene en ISO

def map_event_to_contract(
    event: Dict[str, Any],
    shots: Union[List[Dict[str, Any]], Dict[str, Any], None] = None,
) -> Dict[str, Any]:
    """
    Normaliza datos del partido y los disparos al contrato ShotsResponse.
    """
    c = SofaClient()

    # ---- Partido
    home, away = c.teams(event)
    event_id = str(c.event_id(event))
    date_iso_raw = c.start_iso(event) or "1970-01-01T00:00:00Z"
    date_iso = _to_iso8601(date_iso_raw)
    home_score, away_score = c.final_score(event)

    # ---- Disparos
    arr = _shots_array(shots or [])
    disparos = [_map_one_shot(s, home, away) for s in arr]

    return {
        "partido": {
            "idPartido": event_id,
            "fechaISO": date_iso,
            "local": home,
            "visitante": away,
            "marcadorFinal": {"local": home_score, "visitante": away_score},
        },
        "disparos": disparos,
    }
