# src/scraper/sofascore_fc.py
from typing import Any, Dict, List, Optional, Tuple

# Nota: los nombres/clases exactas de ScraperFC pueden variar por versión.
# Este wrapper está diseñado para aislar cambios y facilitar tests.
try:
    from ScraperFC.sofascore import Sofascore  # ← clase principal de ScraperFC para SofaScore
except ImportError as e:
    Sofascore = None  # para que los tests unitarios no fallen en import si no está instalado

class SofaClient:
    def __init__(self) -> None:
        if Sofascore is None:
            raise RuntimeError("ScraperFC (Sofascore) no está disponible. Revisa la instalación.")
        self.client = Sofascore()

    def event_from_url(self, match: str) -> Dict[str, Any]:
        """
        Acepta:
          - id numérico (str o int)
          - URL canónica de SofaScore con '#id:<numero>'
        """
        # Caso 1: id numérico directo
        if str(match).isdigit():
            return self.client.get_match_dict(int(match))

        # Caso 2: URL canónica con '#id:'
        if "#id:" in match:
            return self.client.get_match_dict(match)

        # Caso 3: URL sin '#id:' -> no soportado por ScraperFC 3.3.4
        raise ValueError(
            "La URL no contiene '#id:<numero>'. "
            "Pasa el id del partido (p.ej. 1234567) o una URL canónica con '#id:'."
        )        

 
    def shots_from_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae una lista de 'intentos/disparos' desde el dict del evento.
        El nombre de la clave puede diferir ('shots', 'shotmap', 'attempts', etc.).
        """
        # Heurística: busca listas con campos tipo minute/player/xg/outcome
        candidates = []
        for key in ("shots", "shotmap", "attempts", "events", "attacks"):
            v = event.get(key)
            if isinstance(v, list):
                candidates = v
                break
        return candidates

    def event_id(self, event: Dict[str, Any]) -> str:
        for k in ("id", "eventId", "matchId"):
            v = event.get(k)
            if v:
                return str(v)
        return "unknown-id"

    def teams(self, event: Dict[str, Any]) -> Tuple[str, str]:
        home = (event.get("homeTeam") or {}).get("name") or event.get("home", {}).get("name") or "Local"
        away = (event.get("awayTeam") or {}).get("name") or event.get("away", {}).get("name") or "Visitante"
        return home, away

    def start_iso(self, event: Dict[str, Any]) -> Optional[str]:
        for k in ("startDate", "startTime", "startTimestamp", "startIso", "kickoff"):
            v = event.get(k)
            if v:
                return str(v)
        return None

    def final_score(self, event: Dict[str, Any]) -> Tuple[int, int]:
        """
        Extrae el marcador final del dict del evento.
        Orden de preferencia:
        1) homeScore.current / awayScore.current
        2) scores.home / scores.away
        3) estructuras alternativas comunes (home/away con 'score', 'display', etc.)
        Si no se puede resolver, devuelve (0, 0).
        """
        # 1) Estructura Sofascore típica
        try:
            hs = (event.get("homeScore") or {}).get("current")
            as_ = (event.get("awayScore") or {}).get("current")
            if hs is not None and as_ is not None:
                return int(hs), int(as_)
        except Exception:
            pass

        # 2) Variante con dict 'scores'
        try:
            scores = event.get("scores") or {}
            hs = scores.get("home")
            as_ = scores.get("away")
            if hs is not None and as_ is not None:
                return int(hs), int(as_)
        except Exception:
            pass

        # 3) Variantes con 'display' o 'score' anidados
        try:
            hs = (event.get("homeScore") or {}).get("display") or (event.get("home") or {}).get("score")
            as_ = (event.get("awayScore") or {}).get("display") or (event.get("away") or {}).get("score")
            if hs is not None and as_ is not None:
                return int(hs), int(as_)
        except Exception:
            pass

        # 4) Por defecto, 0-0 si no se encuentra nada confiable
        return 0, 0    