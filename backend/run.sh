#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [ -d "venv" ]; then
  source venv/bin/activate
fi
if [ -f "../.env" ]; then
  export $(grep -v '^#' ../.env | xargs)
fi
if [ -f "../apikey.env" ]; then
  export $(grep -v '^#' ../apikey.env | xargs)
fi
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
