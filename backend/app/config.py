"""Application configuration and environment helpers."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env", override=False)
load_dotenv(ROOT_DIR / "apikey.env", override=False)


@dataclass(frozen=True)
class Settings:
    """Strongly-typed configuration for the backend service."""

    environment: str = os.getenv("ENVIRONMENT", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # API keys / auth
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_STUDIO_API_KEY")
    youcom_api_key: Optional[str] = os.getenv("YOUCOM_API_KEY") or os.getenv("YOU_COM_API_KEY")

    # Vertex AI specific configuration
    vertex_project: Optional[str] = os.getenv("VERTEX_PROJECT")
    vertex_location: str = os.getenv("VERTEX_LOCATION", "us-central1")
    vertex_model: str = os.getenv("VERTEX_MODEL", "gemini-2.5-pro")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    # Analysis defaults
    max_chart_points: int = int(os.getenv("MAX_CHART_POINTS", "500"))
    max_reference_event_types: int = int(os.getenv("MAX_REFERENCE_EVENT_TYPES", "3"))

    # Data directories (optional, for local testing)
    general_aviation_dir: Path = ROOT_DIR / "100_flights_avionics_only" / "data_log"
    military_dir: Path = ROOT_DIR / "Defense data" / "Hackathon Defense Data"

    @property
    def use_vertex(self) -> bool:
        """Whether to route Gemini requests through Vertex AI."""
        return bool(self.vertex_project and self.vertex_location)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
