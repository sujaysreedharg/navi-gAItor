"""You.com Search API client focusing on aviation references."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

import requests

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class YoucomResult:
    title: str
    url: str
    snippet: str
    domain: str
    event_type: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "domain": self.domain,
            "event_type": self.event_type,
        }


class YoucomSearchClient:
    API_URL = "https://api.ydc-index.io/v1/search"

    AVIATION_DOMAINS = [
        "faa.gov",
        "boldmethod.com",
        "skybrary.aero",
        "aopa.org",
        "aviationweather.gov",
        "cirrusaircraft.com",
    ]

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.youcom_api_key
        if not self.api_key:
            raise ValueError("You.com API key not configured")

    def search(self, query: str, *, num_results: int = 3, include_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        headers = {
            "X-API-Key": self.api_key,
        }
        params = {
            "query": query,
            "count": num_results,
        }
        try:
            response = requests.get(self.API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            logger.warning("You.com search failed: %s", exc)
            return {"hits": [], "error": str(exc)}

    def search_for_event(self, event_type: str, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        queries = {
            "STEEP_TURN": "FAA steep turn tolerances ACS",
            "OVERSPEED": "FAA Vne never exceed speed guidance",
            "HIGH_G_LOAD": "FAA load factor normal category",
            "STALL_WARNING": "FAA stall recovery procedure",
            "LANDING": "FAA stabilized approach criteria",
            "TAKEOFF": "FAA takeoff performance planning",
        }
        query = queries.get(event_type, f"FAA {event_type} regulation")
        results = self.search(query, num_results=2)
        snippets: List[Dict[str, Any]] = []
        for item in results.get("hits", [])[:2]:
            snippets.append(
                YoucomResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    domain=item.get("url", "").split("/")[2] if item.get("url") else "",
                    event_type=event_type,
                ).as_dict()
            )
        return snippets
