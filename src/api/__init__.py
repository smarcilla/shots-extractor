"""API package exposing the FastAPI application entrypoints."""

from .app import create_app

__all__ = ["create_app"]
