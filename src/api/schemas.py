"""Pydantic schemas for the public HTTP API."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from src.models.schemas import ShotsResponse


class PublishShotsRequest(BaseModel):
    """Request body for publishing a shots JSON file."""

    match_id: str = Field(..., description="Identificador único del partido")
    storage_path: str = Field(..., description="Ruta destino en Supabase Storage")
    shots: ShotsResponse = Field(..., description="Payload normalizado de disparos")


class PublishShotsResponse(BaseModel):
    """Response returned after storing the shots file in Supabase."""

    match_id: str
    storage_path: str
    checksum: str
    size_bytes: int
    uploaded_at: datetime
