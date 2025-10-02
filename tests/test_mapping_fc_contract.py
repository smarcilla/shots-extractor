# tests/test_mapping_fc_contract.py
from src.mapping.sofa_mapper_fc import map_event_to_contract
from src.models.schemas import ShotsResponse

def test_map_event_produces_valid_contract():
    event = {
        "id": 99,
        "homeTeam": {"name": "Oviedo"},
        "awayTeam": {"name": "Barcelona"},
        "startDate": "2025-09-26T19:00:00Z",
        "homeScore": {"current": 1},
        "awayScore": {"current": 2},
    }
    norm = map_event_to_contract(event)
    model = ShotsResponse.model_validate(norm)
    assert model.partido.idPartido == "99"
    assert model.partido.local == "Oviedo"
    assert model.partido.visitante == "Barcelona"
    assert model.partido.fechaISO == "2025-09-26T19:00:00Z"
    assert model.partido.marcadorFinal.local == 1
    assert model.partido.marcadorFinal.visitante == 2