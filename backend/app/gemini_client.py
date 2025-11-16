"""Gemini AI integration via Google AI Studio or Vertex AI."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from google import genai

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

try:
    # Vertex AI is optional; import lazily when configured
    from vertexai import init as vertex_init
    from vertexai.preview.generative_models import GenerativeModel
except Exception:  # pragma: no cover - vertex may not be installed/configured
    vertex_init = None
    GenerativeModel = None


class GeminiDebriefGenerator:
    def __init__(self, *, model: Optional[str] = None):
        default_model = settings.vertex_model if settings.use_vertex else settings.gemini_model
        self.model_name = model or default_model
        self._use_vertex = settings.use_vertex and vertex_init and GenerativeModel

        if self._use_vertex:
            logger.info("Using Vertex AI model: %s", self.model_name)
            vertex_init(project=settings.vertex_project, location=settings.vertex_location)
            self.vertex_model = GenerativeModel(self.model_name)
            self.client: Optional[genai.Client] = None
        else:
            api_key = settings.gemini_api_key
            if not api_key:
                raise ValueError("Gemini API key not configured")
            logger.info("Using Google AI Studio key with model: %s", self.model_name)
            self.client = genai.Client(api_key=api_key)
            self.vertex_model = None

    def generate_text(self, prompt: str) -> str:
        try:
            if self._use_vertex and self.vertex_model:
                response = self.vertex_model.generate_content(prompt)
                return response.text or ""
            assert self.client is not None
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
            )
            parts = response.candidates[0].content.parts
            return "".join(part.text or "" for part in parts)
        except Exception as exc:  # pragma: no cover - network
            logger.error("Gemini generation failed: %s", exc)
            return f"Error generating debrief: {exc}"

    def generate_debrief(self, flight_summary: Dict[str, Any], events: List[Dict[str, Any]], references: List[Dict[str, Any]]) -> str:
        prompt = self._build_prompt(flight_summary, events, references)
        return self.generate_text(prompt)

    def _build_prompt(self, flight_summary: Dict[str, Any], events: List[Dict[str, Any]], references: List[Dict[str, Any]]) -> str:
        critical = [e for e in events if e.get("severity") == "critical"]
        warning = [e for e in events if e.get("severity") == "warning"]
        info = [e for e in events if e.get("severity") == "info"]

        refs_text = "\n\nRegulatory References:\n"
        if references:
            for ref in references:
                refs_text += f"- {ref.get('title')} ({ref.get('url')})\n  {ref.get('snippet', '')}\n"
        else:
            refs_text += "- None provided\n"

        prompt = f"""You are a Certified Flight Instructor (CFI) creating a post-flight debrief.

Flight Summary:
- Duration: {flight_summary.get('total_duration_minutes', 0)} minutes
- Max Altitude: {flight_summary.get('max_altitude_ft', 0):.0f} ft MSL
- Max Airspeed: {flight_summary.get('max_airspeed_kt', 0):.0f} kt
- Max Bank Angle: {flight_summary.get('max_bank_angle_deg', 0):.1f}°
- Max Positive G: {flight_summary.get('max_positive_g', 1.0):.2f}G
- Fuel Consumed: {flight_summary.get('fuel_consumed_gal', 0):.1f} gallons

Critical Events ({len(critical)}):
{self._format_events(critical)}

Warning Events ({len(warning)}):
{self._format_events(warning)}

Flight Phases ({len(info)}):
{self._format_events(info)}

{refs_text}

Instructions:
1. Provide a concise flight overview.
2. Highlight 2-3 things that went well.
3. Discuss each critical/warning event with actionable guidance citing references when available.
4. Offer three training recommendations for the next sortie.
5. Close with safety notes and tone that is professional yet encouraging.
Target length: 300-400 words.
"""
        return prompt

    @staticmethod
    def _format_events(events: List[Dict[str, Any]]) -> str:
        if not events:
            return "- None"
        lines = []
        for event in events[:10]:
            desc = event.get("description", "")
            t = event.get("time_seconds", 0)
            lines.append(f"- {desc} (t+{t:.0f}s)")
        return "\n".join(lines)
