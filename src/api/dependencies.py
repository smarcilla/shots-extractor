"""FastAPI dependencies wiring external infrastructure for the application."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv
from supabase import Client, create_client

from src.application.publish_shots import ShotsPublisher
from src.infrastructure.supabase import (
    SupabaseMatchesIndexRepository,
    SupabaseStorageAdapter,
)


@dataclass(frozen=True)
class Settings:
    """Configuration required to connect with Supabase services."""

    supabase_url: str
    supabase_service_key: str
    supabase_bucket: str = "shots"

    @staticmethod
    def from_env() -> "Settings":
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        bucket = os.getenv("SUPABASE_BUCKET_SHOTS", "shots")

        missing = [
            name
            for name, value in (
                ("SUPABASE_URL", url),
                ("SUPABASE_SERVICE_KEY", key),
            )
            if not value
        ]
        if missing:
            missing_str = ", ".join(missing)
            raise RuntimeError(f"Faltan variables de entorno requeridas: {missing_str}")

        return Settings(supabase_url=url, supabase_service_key=key, supabase_bucket=bucket)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings to avoid re-reading environment on each request."""

    load_dotenv()
    return Settings.from_env()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Instantiate the Supabase client once per process."""

    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


def get_shots_publisher() -> ShotsPublisher:
    """Provide a configured ShotsPublisher for dependency injection."""

    settings = get_settings()
    client = get_supabase_client()

    storage = SupabaseStorageAdapter(client=client, bucket=settings.supabase_bucket)
    database = SupabaseMatchesIndexRepository(client=client)

    return ShotsPublisher(
        storage=storage,
        database=database,
        bucket=settings.supabase_bucket,
    )
