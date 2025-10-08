"""Use case for publishing normalized shots data into Supabase Storage and index."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Callable, Protocol

from pydantic import ValidationError

from src.models.schemas import ShotsResponse


class ShotsStorage(Protocol):
    """Port representing the storage service responsible for binary uploads."""

    def upload(self, *, bucket: str, path: str, content: bytes, content_type: str) -> None:  # pragma: no cover - protocol
        ...


class MatchesIndexRepository(Protocol):
    """Port to persist metadata for published matches."""

    def upsert_match_index(self, *, record: dict[str, Any]) -> None:  # pragma: no cover - protocol
        ...


class ShotsPayloadValidationError(ValueError):
    """Raised when the publication request payload fails validation rules."""


class TransientStorageError(RuntimeError):
    """Raised when the storage backend reports a recoverable error."""


Clock = Callable[[], datetime]


@dataclass(frozen=True)
class ShotsPublicationRequest:
    """Input DTO for the shots publication use case."""

    match_id: str
    storage_path: str
    shots: ShotsResponse


@dataclass(frozen=True)
class PublishResult:
    """Output DTO returned after a successful publication."""

    match_id: str
    storage_path: str
    checksum: str
    size_bytes: int
    uploaded_at: datetime


class ShotsPublisher:
    """Application service that handles validation, upload and indexing workflow."""

    DEFAULT_BUCKET = "shots"

    def __init__(
        self,
        *,
        storage: ShotsStorage,
        database: MatchesIndexRepository,
        bucket: str | None = None,
        max_retries: int = 3,
        clock: Clock | None = None,
    ) -> None:
        self._storage = storage
        self._database = database
        self._bucket = bucket or self.DEFAULT_BUCKET
        self._max_retries = max(1, max_retries)
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def publish(self, request: ShotsPublicationRequest) -> PublishResult:
        self._validate_request(request)
        payload_bytes = self._serialize(request.shots)
        checksum = sha256(payload_bytes).hexdigest()
        size_bytes = len(payload_bytes)

        self._upload_with_retry(path=request.storage_path, content=payload_bytes)
        uploaded_at = self._clock()

        record = self._build_index_record(
            request=request,
            checksum=checksum,
            size_bytes=size_bytes,
        )
        self._database.upsert_match_index(record=record)

        return PublishResult(
            match_id=request.match_id,
            storage_path=request.storage_path,
            checksum=checksum,
            size_bytes=size_bytes,
            uploaded_at=uploaded_at,
        )

    def _validate_request(self, request: ShotsPublicationRequest) -> None:
        if request.match_id != request.shots.partido.idPartido:
            raise ShotsPayloadValidationError(
                "El identificador del partido no coincide con el payload de disparos",
            )

        if not self._is_storage_path_secure(request.storage_path):
            raise ShotsPayloadValidationError("La ruta de almacenamiento no es válida")

    @staticmethod
    def _serialize(shots: ShotsResponse) -> bytes:
        try:
            payload = shots.model_dump(exclude_none=True)
        except ValidationError as exc:  # pragma: no cover - defensive; ShotsResponse ya valida
            raise ShotsPayloadValidationError("El payload de disparos es inválido") from exc

        return json.dumps(payload, sort_keys=True).encode("utf-8")

    def _upload_with_retry(self, *, path: str, content: bytes) -> None:
        attempts = 0
        while True:
            try:
                self._storage.upload(
                    bucket=self._bucket,
                    path=path,
                    content=content,
                    content_type="application/json",
                )
                return
            except TransientStorageError:
                attempts += 1
                if attempts >= self._max_retries:
                    raise

    @staticmethod
    def _build_index_record(
        *,
        request: ShotsPublicationRequest,
        checksum: str,
        size_bytes: int,
    ) -> dict[str, Any]:
        return {
            "id": request.match_id,
            "date": ShotsPublisher._parse_match_date(request.shots.partido.fechaISO),
            "home": request.shots.partido.local,
            "away": request.shots.partido.visitante,
            "storage_path": request.storage_path,
            "size_bytes": size_bytes,
            "checksum": checksum,
        }

    @staticmethod
    def _parse_match_date(raw_date: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(raw_date)
        except ValueError as exc:  # pragma: no cover - defensive
            raise ShotsPayloadValidationError("La fecha del partido es inválida") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    @staticmethod
    def _is_storage_path_secure(path: str) -> bool:
        if not path or path.startswith("/") or "\\" in path:
            return False
        if ".." in path.split("/"):
            return False
        return path.endswith(".json")
