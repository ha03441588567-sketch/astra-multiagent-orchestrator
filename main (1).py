"""
Astra AI Workforce Platform — Multi-Agent Orchestrator
FastAPI backend entry point.

Run locally:
    uvicorn main:app --reload --port 8000

Docs available at /docs (Swagger UI).
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

import database as db
from models import IncomingMessage, OrchestratorResponse
from orchestrator import run_orchestrator

app = FastAPI(
    title="Astra AI Workforce Platform — Multi-Agent Orchestrator",
    description="Routes customer messages across specialized AI agents "
                 "(Receptionist, Lead Qualifier, Scheduler, Follow-up) for "
                 "24/7 business automation across roofing, dental, real "
                 "estate, and solar niches.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    db.init_db()


@app.get("/health")
def health():
    return {"status": "ok", "service": "astra-multiagent-orchestrator"}


@app.post("/api/orchestrate", response_model=OrchestratorResponse)
def orchestrate(payload: IncomingMessage):
    try:
        result = run_orchestrator(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads")
def list_leads(business_id: str | None = None):
    return db.get_leads(business_id)


@app.get("/api/tasks")
def list_tasks(business_id: str | None = None):
    return db.get_tasks(business_id)


@app.get("/api/conversations/{conversation_id}")
def conversation(conversation_id: str):
    return db.get_conversation(conversation_id)


@app.get("/api/stats")
def stats():
    return db.get_stats()


@app.get("/api/agents")
def list_agents():
    return {
        "agents": [
            {"name": "receptionist_agent", "role": "First point of contact, greets & captures leads"},
            {"name": "lead_qualifier_agent", "role": "Asks qualifying questions, scores urgency"},
            {"name": "scheduler_agent", "role": "Books appointments / inspections / consultations"},
            {"name": "followup_agent", "role": "Runs the 10-day re-engagement sequence"},
        ]
    }


# --- Serve the dashboard frontend as static files ---
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def dashboard():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
