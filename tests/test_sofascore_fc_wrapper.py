# tests/test_sofascore_fc_wrapper.py
from src.scraper.sofascore_fc import SofaClient

class DummyClient(SofaClient):
    def __init__(self):  # evita dependencia real en import
        self.client = object()

def test_wrapper_shots_and_fields():
    c = DummyClient()
    fake_event = {
        "id": 42,
        "homeTeam": {"name": "Atlético"},
        "awayTeam": {"name": "Real Madrid"},
        "startDate": "2025-09-27T20:00:00Z",
        "shots": [
            {"minute": 5, "player": {"name": "Griezmann"}, "team": "home", "xg": 0.1, "outcome": "Goal"}
        ],
    }
    shots = c.shots_from_event(fake_event)
    assert len(shots) == 1
    assert c.event_id(fake_event) == "42"
    assert c.teams(fake_event) == ("Atlético", "Real Madrid")
    assert c.start_iso(fake_event) == "2025-09-27T20:00:00Z"