# navi-gAItor

Single-flight debug platform with oscilloscope-style telemetry scrubbing, rule-based event detection, and an AI-powered flight instructor (NavigAGENT) that analyzes flight data using Gemini intelligence and You.com FAA regulatory references. Upload Garmin G1000 or T-38C CSV logs to get instant risk scoring, interactive signal strips, and conversational follow-up queries.

## Repository Map
```
backend/                FastAPI service
  app/                  Parsers, events, API clients
  requirements.txt      Python deps (3.9+)
  run.sh                Local launcher (loads .env/apikey.env)
frontend/               Vite + React + TS UI
  src/components/       Animated cockpit UI widgets
  src/hooks/            Upload/analysis hook
  src/lib/api.ts        Axios helper for /analyze
  .env.example          Frontend API base URL template
apikey.env             Sample Gemini + You.com keys (do **not** commit)
```

## Prerequisites
- Python 3.9+
- Node.js 18+
- Access to the attached datasets already present in this repo
- API keys:
  - `GEMINI_API_KEY` (Google AI Studio key from [aistudio.google.com](https://aistudio.google.com))
  - `YOUCOM_API_KEY` (You.com Search API key from [api.you.com](https://api.you.com) — **not** the Agents beta key)
  - Optional: `VERTEX_PROJECT`, `VERTEX_LOCATION`, `VERTEX_MODEL` if using Vertex AI

Create an `apikey.env` file in the repo root (or export in your shell):
```env
GOOGLE_AI_STUDIO_API_KEY="AIza..."
YOU_COM_API_KEY="ydc-sk-..."
VERTEX_PROJECT=optional-gcp-project
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-pro
GEMINI_MODEL=gemini-2.5-pro
```
`backend/run.sh` automatically sources `.env` **and** `apikey.env` if present.

## Backend Setup & Usage
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Run locally:
```bash
./run.sh
# FastAPI available at http://localhost:8000
# Open http://localhost:8000/docs for Swagger UI
# /ai/agent handles the new console commands (POST with {command, window_start, window_end, summary, rule_events})
```

Test with a provided CSV:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@../100_flights_avionics_only/data_log/log_231113_191632_KSQL.csv"
```
The response contains summary stats, event list, reference snippets, Gemini debrief text, and downsampled series data ready for visualization.

## Frontend Setup & Usage
```bash
cd frontend
cp .env.example .env.local   # optional if using non-default backend URL
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
Visit `http://127.0.0.1:5173` to access the animated cockpit UI:
1. Drag-and-drop or browse for a CSV log.
2. Watch upload/analysis progress overlays inspired by ChatGPT.
3. Scrub the new signal strip (altitude, airspeed, AoA, Nz, etc.) with zoomable windows and a risk trace.
4. Use the rule panel (HF_RISK_HIGH, LOW_ALTITUDE_BANK, AOA_MARGIN_LOW…) to jump to interesting timestamps.
5. Ask the AI console engineering-style questions (“Explain HF spike between t=120–135”) and review structured log output.
6. Review the summary grid, classic charts, timeline, Gemini debrief, and You.com citations.

For production builds:
```bash
npm run build
```
The output lives under `frontend/dist/` and can be served via any static host (or the Dockerfile referenced in `COMPLETE_BUILD_PROMPT.md`).

## Data Notes
- **General Aviation dataset**: `100_flights_avionics_only/data_log/` (Cirrus SR20, Garmin G1000, ~1 Hz). Many logs are ground tests—filter for >500 ft altitude changes + >50 kt IAS for real flights.
- **Military dataset**: `Defense data/Hackathon Defense Data/AirForce_Sortie_Aeromod.csv` (T-38C, 20 Hz, 110 columns). Parser auto-detects via `IRIG_TIME` column.

## Tech Highlights
- **Parser**: Intelligent header trimming, aircraft auto-detection, numeric coercion, and metadata extraction.
- **Events**: Takeoff/Landing phases, steep turns, stalls, overspeed, and G-limit exceedances with dynamic severity tagging (critical/warning/info based on actual values).
- **Rule Engine**: Computes human-factor risk index (0–100) from vertical speed, bank angle, and G-loads; fires lenient thresholds for HF_RISK_HIGH, LOW_ALTITUDE_BANK, and AOA_MARGIN_LOW.
- **References**: You.com Search API v1 (`https://api.ydc-index.io/v1/search`) with `X-API-Key` authentication, constrained to trusted aviation domains (faa.gov, boldmethod.com, skybrary.aero, etc.). Results attached for top 3 event types (prioritized by severity).
- **AI Debrief**: Gemini client supports both Google AI Studio (via `google-genai`) and Vertex AI (via `google-cloud-aiplatform`). Generates initial CFI-style debrief and powers NavigAGENT interactive console with structured log responses.
- **Frontend**: Vite + React + TypeScript + Recharts + Framer Motion for a ChatGPT-inspired, aviation-themed UI with oscilloscope signal strips, zoom brush, cursor scrubbing, and preset windows.

## Local Stack Validation
Executed during this build:
1. `npm run build` in `frontend/` – ensures TypeScript + Vite bundle clean.
2. `uvicorn app.main:app --host 127.0.0.1 --port 8000` (with dummy API keys) – verified `/health` OK.
3. `npm run dev -- --host 127.0.0.1 --port 5173` – verified dev server responds (headers inspected via curl).

## You.com API Integration Details

The backend uses You.com's **Search API v1** (not the Agents beta):

- **Endpoint**: `https://api.ydc-index.io/v1/search`
- **Method**: `GET` with query parameters (`?query=...&count=...`)
- **Authentication**: `X-API-Key` header (not Bearer token)
- **Response format**: JSON with `hits` array containing `{title, url, description}`
- **Domain filtering**: Queries are constrained to aviation-specific domains via backend logic

Get your Search API key from [api.you.com](https://api.you.com) (API Management → API Keys). The key format is `ydc-sk-...`.

## Next Suggestions
- Add backend unit tests under `backend/tests/` with fixture CSV slices.
- Implement auth & persistence for multi-pilot histories.
- Enhance charts with 3D ground tracks (Mapbox) and envelope overlays.
- Package both services with Docker/Compose for Cloud Run deployment per `COMPLETE_BUILD_PROMPT.md`.
