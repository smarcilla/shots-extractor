"""FastAPI application wiring the shots publication endpoint."""
from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import Depends, FastAPI, HTTPException, status

from src.api.dependencies import get_shots_publisher
from src.api.schemas import PublishShotsRequest, PublishShotsResponse
from src.application.publish_shots import (
    ShotsPayloadValidationError,
    ShotsPublicationRequest,
    ShotsPublisher,
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create the FastAPI application configured with dependency injection."""

    app = FastAPI(title="Shots Extractor API", version="1.0.0")

    @app.post(
        "/v1/shots/publish",
        response_model=PublishShotsResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Publica un fichero de disparos en Supabase",
    )
    def publish_shots(
        payload: PublishShotsRequest,
        publisher: ShotsPublisher = Depends(get_shots_publisher),
    ) -> PublishShotsResponse:
        """Endpoint que delega en el caso de uso y normaliza respuestas."""

        try:
            result = publisher.publish(
                ShotsPublicationRequest(
                    match_id=payload.match_id,
                    storage_path=payload.storage_path,
                    shots=payload.shots,
                )
            )
        except ShotsPayloadValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Exception as exc:  # pragma: no cover - defensivo
            logger.exception("Error publicando disparos en Supabase", extra={
                "match_id": payload.match_id,
                "storage_path": payload.storage_path,
            })
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Falló la publicación en Supabase",
            ) from exc

        return PublishShotsResponse(**asdict(result))

    return app
