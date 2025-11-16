"""Mission Debrief AI backend entrypoint."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .events import FlightEventDetector, compute_flight_summary
from .flight_parser import parse_flight_with_metadata
from .gemini_client import GeminiDebriefGenerator
from .you_client import YoucomSearchClient
from .rules import (
    build_presets,
    build_signal_payload,
    compute_hf_index,
    generate_rule_events,
)

from pydantic import BaseModel
from fastapi import Body

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("mission-debrief-ai")

app = FastAPI(title="navi-gAItor", version="0.1.0", description="Flight analysis backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _build_chart_series(df) -> List[Dict[str, Any]]:
    chart_columns = [
        "time_seconds",
        "alt_msl_ft",
        "airspeed_indicated_kt",
        "vertical_speed_fpm",
        "roll_deg",
        "pitch_deg",
    ]
    available = [col for col in chart_columns if col in df.columns]
    step = max(1, len(df) // settings.max_chart_points)
    return df[available].iloc[::step].to_dict(orient="records")


@app.get("/")
def root() -> Dict[str, Any]:
    return {"service": "navi-gAItor", "status": "ok"}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "healthy"}


@app.post("/analyze")
async def analyze_flight(file: UploadFile = File(...)) -> Dict[str, Any]:
    logger.info("Analyzing file %s", file.filename)
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        df, metadata = parse_flight_with_metadata(file_bytes)
    except Exception as exc:
        logger.exception("Parsing failed")
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {exc}") from exc

    if df.empty:
        raise HTTPException(status_code=400, detail="No telemetry data found")

    df = df.copy()
    df["hf_index"] = compute_hf_index(df)

    detector = FlightEventDetector(df)
    events = detector.detect_all_events()
    summary = compute_flight_summary(df)
    signal_meta, signal_matrix = build_signal_payload(df, metadata.get("detected_aircraft", "CIRRUS_SR20"))
    risk_trace = (
        df[["time_seconds", "hf_index"]]
        .fillna(0)
        .to_dict(orient="records")
        if "hf_index" in df.columns
        else []
    )
    rule_events = generate_rule_events(df)
    presets = build_presets(df)

    references: List[Dict[str, Any]] = []
    try:
        critical_types = [e["type"] for e in events if e.get("severity") in {"critical", "warning"}]
        unique_types = list(dict.fromkeys(critical_types))[: settings.max_reference_event_types]
        if unique_types:
            you_client = YoucomSearchClient()
            for event_type in unique_types:
                first_event = next(e for e in events if e["type"] == event_type)
                references.extend(you_client.search_for_event(event_type, first_event))
    except Exception as exc:
        logger.warning("Reference lookup failed: %s", exc)

    try:
        gemini_client = GeminiDebriefGenerator()
        debrief = gemini_client.generate_debrief(summary, events, references)
    except Exception as exc:
        logger.error("Gemini client error: %s", exc)
        debrief = "Unable to generate AI debrief. Check Gemini credentials."

    response = {
        "success": True,
        "filename": file.filename,
        "metadata": metadata,
        "summary": summary,
        "events": events,
        "events_count": {
            "total": len(events),
            "critical": len([e for e in events if e.get("severity") == "critical"]),
            "warning": len([e for e in events if e.get("severity") == "warning"]),
            "info": len([e for e in events if e.get("severity") == "info"]),
        },
        "references": references,
        "debrief": debrief,
        "series_data": _build_chart_series(df),
        "signal_meta": signal_meta,
        "signal_matrix": signal_matrix,
        "risk_trace": risk_trace,
        "rule_events": rule_events,
        "presets": presets,
    }
    return response


class AiAgentRequest(BaseModel):
    command: str
    window_start: Optional[float] = None
    window_end: Optional[float] = None
    summary: Dict[str, Any]
    rule_events: List[Dict[str, Any]] = []
    context_notes: Optional[str] = None


@app.post("/ai/agent")
async def ai_agent_handler(payload: AiAgentRequest = Body(...)) -> Dict[str, Any]:
    command = payload.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")

    window_text = ""
    if payload.window_start is not None and payload.window_end is not None:
        window_text = f"Time window: {payload.window_start:.1f}s – {payload.window_end:.1f}s.\n"

    rules_text = "\n".join(
        [
            f"- {event['rule']} @ t={event['time_seconds']:.1f}s ({event['severity']}): {event.get('description','')}"
            for event in payload.rule_events[:20]
        ]
    )

    prompt = f"""You are a flight test engineer reviewing telemetry.
{window_text}
Command: {command}

Flight summary: {payload.summary}

Recent rule events:\n{rules_text or 'None'}

Provide your response as structured log lines. Begin with an action verb (e.g., ANALYZE, NOTE, ALERT). Include bullet-style findings, cite signal names with units, and propose checks or comparisons where relevant.
"""

    try:
        gemini_client = GeminiDebriefGenerator()
        response_text = gemini_client.generate_text(prompt)
    except Exception as exc:
        logger.error("Gemini agent error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))

    return {"log": response_text}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
