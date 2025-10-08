from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.api.dependencies import get_shots_publisher
from src.application.publish_shots import (
    PublishResult,
    ShotsPayloadValidationError,
    ShotsPublicationRequest,
)


@pytest.fixture()
def api_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def _build_request_payload(match_id: str = "atl-mad-20240928") -> dict[str, Any]:
    return {
        "match_id": match_id,
        "storage_path": f"matches/{match_id}.json",
        "shots": {
            "partido": {
                "idPartido": match_id,
                "fechaISO": "2024-09-28T20:00:00+00:00",
                "local": "Atletico Madrid",
                "visitante": "Real Madrid",
                "marcadorFinal": {"local": 2, "visitante": 1},
            },
            "disparos": [
                {
                    "minuto": 12,
                    "equipo": "Atletico Madrid",
                    "jugador": "Alvaro Morata",
                    "xG": 0.32,
                    "resultado": "Gol",
                }
            ],
        },
    }


def test_publish_endpoint_returns_created(api_client: TestClient) -> None:
    publisher = Mock()
    publish_result = PublishResult(
        match_id="atl-mad-20240928",
        storage_path="matches/atl-mad-20240928.json",
        checksum="a" * 64,
        size_bytes=1234,
        uploaded_at=datetime(2024, 9, 28, 21, 0, tzinfo=timezone.utc),
    )
    publisher.publish.return_value = publish_result

    api_client.app.dependency_overrides[get_shots_publisher] = lambda: publisher

    response = api_client.post("/v1/shots/publish", json=_build_request_payload())

    assert response.status_code == 201
    expected_uploaded_at = publish_result.uploaded_at.isoformat().replace("+00:00", "Z")

    assert response.json() == {
        "match_id": publish_result.match_id,
        "storage_path": publish_result.storage_path,
        "checksum": publish_result.checksum,
        "size_bytes": publish_result.size_bytes,
        "uploaded_at": expected_uploaded_at,
    }

    publisher.publish.assert_called_once()
    (request_obj,), _ = publisher.publish.call_args
    assert isinstance(request_obj, ShotsPublicationRequest)

    api_client.app.dependency_overrides.clear()


def test_publish_endpoint_returns_400_on_validation_error(api_client: TestClient) -> None:
    def _raise_validation(_: Any) -> None:
        raise ShotsPayloadValidationError("invalid payload")

    api_client.app.dependency_overrides[get_shots_publisher] = lambda: Mock(publish=_raise_validation)

    response = api_client.post("/v1/shots/publish", json=_build_request_payload(match_id="bad id"))

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid payload"

    api_client.app.dependency_overrides.clear()


def test_publish_endpoint_returns_502_on_unexpected_error(api_client: TestClient) -> None:
    def _raise_error(_: Any) -> None:
        raise RuntimeError("supabase down")

    api_client.app.dependency_overrides[get_shots_publisher] = lambda: Mock(publish=_raise_error)

    response = api_client.post("/v1/shots/publish", json=_build_request_payload())

    assert response.status_code == 502
    assert response.json()["detail"] == "Falló la publicación en Supabase"

    api_client.app.dependency_overrides.clear()


def test_publish_endpoint_rejects_malformed_json(api_client: TestClient) -> None:
    response = api_client.post(
        "/v1/shots/publish",
        content="not a json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
