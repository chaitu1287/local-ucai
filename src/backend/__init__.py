"""Modal + FastAPI server module."""

from src.backend.app import fastapi
from src.backend.modal import app

__all__ = ["app", "fastapi"]
