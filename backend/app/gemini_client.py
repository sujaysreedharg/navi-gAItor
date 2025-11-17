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

        refs_text = "\n\nRegulatory References (CITE THESE IN YOUR DEBRIEF):\n"
        if references:
            for i, ref in enumerate(references, 1):
                refs_text += f"[{i}] {ref.get('event_type', 'GENERAL').replace('_', ' ')} - {ref.get('title')}\n"
                refs_text += f"    Source: {ref.get('domain', 'faa.gov')}\n"
                refs_text += f"    Key Point: {ref.get('snippet', '')[:200]}...\n\n"
        else:
            refs_text += "- None available\n"

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

Info Events ({len(info)}):
{self._format_events(info)}

{refs_text}

Instructions:
1. Flight Overview: Brief summary of the flight profile.
2. What Went Well: Highlight 2-3 positive aspects with specifics.
3. Event Analysis: For each critical/warning/info event, explain the concern and **cite the relevant regulatory reference by number** (e.g., "According to [1], steep turns require..."). Use the snippets to provide authoritative guidance.
4. Training Recommendations: Three concrete, actionable items for next flight.
5. Closing: Professional yet encouraging safety notes.

IMPORTANT: Actively reference and cite the regulatory sources provided above using [1], [2], etc. notation. Make the citations feel natural and educational.

Target length: 350-450 words.
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
