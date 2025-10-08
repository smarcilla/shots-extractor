"""Infrastructure adapters for interacting with Supabase services."""
from __future__ import annotations

import logging
from typing import Any

import httpx
from supabase import Client

try:  # pragma: no cover - supabase puede no exponer StorageException
    from supabase.storage import StorageException
except ImportError:  # pragma: no cover
    StorageException = Exception  # type: ignore[assignment]

from src.application.publish_shots import TransientStorageError


logger = logging.getLogger(__name__)


class SupabaseStorageAdapter:
    """Adapter that uploads binary objects to Supabase Storage."""

    def __init__(self, *, client: Client, bucket: str) -> None:
        self._client = client
        self._bucket = bucket

    def upload(self, *, bucket: str, path: str, content: bytes, content_type: str) -> None:
        if bucket != self._bucket:
            raise ValueError("El bucket solicitado no coincide con la configuración del adaptador")

        try:
            self._client.storage.from_(self._bucket).upload(
                path=path,
                file=content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "max-age=31536000",
                    "upsert": "true",  # el SDK espera valores string en cabeceras
                },
            )
        except (StorageException, httpx.RequestError, TimeoutError) as exc:  # pragma: no cover - depende de supabase
            logger.exception(
                "Error subiendo fichero a Supabase Storage",
                extra={
                    "bucket": bucket,
                    "path": path,
                },
            )
            raise TransientStorageError("Fallo temporal al subir a Supabase Storage") from exc


class SupabaseMatchesIndexRepository:
    """Adapter that persists metadata in the matches_index table."""

    def __init__(self, *, client: Client) -> None:
        self._client = client

    def upsert_match_index(self, *, record: dict[str, Any]) -> None:
        try:
            serializable_record = {
                **record,
                "date": record["date"].isoformat(),
            }
            (
                self._client.table("matches_index")
                .upsert(serializable_record, on_conflict="id")
                .execute()
            )
        except httpx.RequestError as exc:  # pragma: no cover - depende de supabase
            logger.exception(
                "Error temporal al acceder a matches_index",
                extra={"match_id": record.get("id")},
            )
            raise TransientStorageError("Fallo temporal al acceder a Supabase Database") from exc
        except Exception as exc:  # pragma: no cover - defensivo
            logger.exception(
                "Fallo no recuperable al registrar el índice",
                extra={"match_id": record.get("id")},
            )
            raise RuntimeError("No se pudo registrar el índice de partido") from exc
