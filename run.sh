#!/usr/bin/env bash
# Quick start script for local development
set -e
cd "$(dirname "$0")/backend"

if [ ! -d "../.venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv ../.venv
fi

source ../.venv/bin/activate
pip install -r requirements.txt --quiet

echo "Starting Astra Multi-Agent Orchestrator on http://localhost:8000"
uvicorn main:app --reload --port 8000
