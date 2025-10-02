# src/scraper/sofascore_fc.py
from typing import Any, Dict, List, Optional, Tuple

# Nota: los nombres/clases exactas de ScraperFC pueden variar por versión.
# Este wrapper está diseñado para aislar cambios y facilitar tests.
try:
    from scraperfc import Sofascore  # ← clase principal de ScraperFC para SofaScore
except Exception as e:
    Sofascore = None  # para que los tests unitarios no fallen en import si no está instalado

class SofaClient:
    def __init__(self) -> None:
        if Sofascore is None:
            raise RuntimeError("ScraperFC (Sofascore) no está disponible. Revisa la instalación.")
        self.client = Sofascore()

    def event_from_url(self, url: str) -> Dict[str, Any]:
        """
        Devuelve un diccionario con información del partido a partir de la URL.
        La estructura exacta depende de ScraperFC; este método actúa como fachada.
        """
        # Ejemplo típico: parsear ID y pedir el evento.
        # Algunas versiones de ScraperFC exponen métodos como:
        #   self.client.get_match(url)  ó  self.client.event(event_id)
        # Ajusta a la API real si difiere.
        data = self.client.get_match(url)  # <-- adapta si tu versión usa otro nombre
        return data

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