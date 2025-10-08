import json
from datetime import datetime, timezone
from typing import Any
from unittest.mock import Mock

import pytest

from src.application.publish_shots import (
    PublishResult,
    ShotsPayloadValidationError,
    ShotsPublicationRequest,
    ShotsPublisher,
    TransientStorageError,
)
from src.models.schemas import Disparo, Marcador, Partido, ShotsResponse


def _build_sample_shots(match_id: str = "atl-mad-20240928") -> ShotsResponse:
    return ShotsResponse(
        partido=Partido(
            idPartido=match_id,
            fechaISO="2024-09-28T20:00:00+00:00",
            local="Atletico Madrid",
            visitante="Real Madrid",
            marcadorFinal=Marcador(local=2, visitante=1),
        ),
        disparos=[
            Disparo(
                minuto=12,
                equipo="Atletico Madrid",
                jugador="Alvaro Morata",
                xG=0.32,
                xGOT=0.18,
                situacion="Juego abierto",
                resultado="Gol",
                tipo_disparo="Pie derecho",
            )
        ],
    )


def _build_request(match_id: str = "atl-mad-20240928", storage_path: str | None = None) -> ShotsPublicationRequest:
    return ShotsPublicationRequest(
        match_id=match_id,
        storage_path=storage_path or f"matches/{match_id}.json",
        shots=_build_sample_shots(match_id),
    )


def test_publish_shots_success_uploads_file_and_upserts_index() -> None:
    storage = Mock()
    database = Mock()
    clock = Mock(return_value=datetime(2024, 9, 28, 21, 0, tzinfo=timezone.utc))

    publisher = ShotsPublisher(storage=storage, database=database, clock=clock)
    request = _build_request()

    result = publisher.publish(request)

    serialized = json.dumps(
        request.shots.model_dump(exclude_none=True),
        sort_keys=True,
    ).encode("utf-8")
    storage.upload.assert_called_once_with(
        bucket="shots",
        path=request.storage_path,
        content=serialized,
        content_type="application/json",
    )

    database.upsert_match_index.assert_called_once()
    upsert_payload: dict[str, Any] = database.upsert_match_index.call_args.kwargs["record"]
    assert upsert_payload == {
        "id": request.match_id,
        "date": datetime.fromisoformat(request.shots.partido.fechaISO),
        "home": request.shots.partido.local,
        "away": request.shots.partido.visitante,
        "storage_path": request.storage_path,
        "size_bytes": len(serialized),
        "checksum": result.checksum,
    }

    assert isinstance(result, PublishResult)
    assert result.match_id == request.match_id
    assert result.storage_path == request.storage_path
    assert result.size_bytes == len(serialized)
    assert len(result.checksum) == 64  # sha256 hex length


def test_publish_shots_retries_on_transient_storage_error() -> None:
    storage = Mock()
    database = Mock()
    storage.upload.side_effect = [TransientStorageError("timeout"), None]

    publisher = ShotsPublisher(storage=storage, database=database)
    request = _build_request()

    result = publisher.publish(request)

    assert storage.upload.call_count == 2
    database.upsert_match_index.assert_called_once()
    assert result.storage_path == request.storage_path


def test_publish_shots_raises_validation_error_for_mismatched_ids() -> None:
    storage = Mock()
    database = Mock()
    publisher = ShotsPublisher(storage=storage, database=database)

    shots = _build_sample_shots(match_id="other-id")

    with pytest.raises(ShotsPayloadValidationError):
        publisher.publish(
            ShotsPublicationRequest(
                match_id="atl-mad-20240928",
                storage_path="matches/atl-mad-20240928.json",
                shots=shots,
            )
        )

    storage.upload.assert_not_called()
    database.upsert_match_index.assert_not_called()


def test_publish_shots_raises_validation_error_for_invalid_storage_path() -> None:
    storage = Mock()
    database = Mock()
    publisher = ShotsPublisher(storage=storage, database=database)

    with pytest.raises(ShotsPayloadValidationError):
        publisher.publish(
            ShotsPublicationRequest(
                match_id="atl-mad-20240928",
                storage_path="../../secret.txt",
                shots=_build_sample_shots(),
            )
        )

    storage.upload.assert_not_called()
    database.upsert_match_index.assert_not_called()
