# Astra AI Workforce Platform — Multi-Agent Orchestrator

A production-ready **multi-agent orchestration backend** for AI-powered 24/7 business
automation — built for AstraVoice's Astra AI Workforce Platform, targeting roofing,
dental, real estate, and solar businesses.

Customer messages (from web chat, SMS, WhatsApp, or voice transcripts) are routed
through an **Orchestrator Agent** that classifies intent and hands off to the right
**specialized agent**, which replies, captures the lead, and queues follow-up tasks —
all logged to a database and visible live on the included dashboard.

## Architecture

```
Customer message
      │
      ▼
┌─────────────────┐
│   Orchestrator   │  ← classifies intent (Claude), routes to the right agent
└────────┬─────────┘
         │
   ┌─────┼─────────────────┬──────────────────┐
   ▼     ▼                 ▼                  ▼
Receptionist  Lead Qualifier   Scheduler   Follow-up Agent
   Agent          Agent          Agent      (10-day sequence)
   │              │               │              │
   └──────────────┴───────────────┴──────────────┘
                        │
                        ▼
              SQLite (conversations, leads, tasks)
                        │
                        ▼
                 Live Dashboard (frontend/index.html)
```

## Agents

| Agent | Responsibility |
|---|---|
| `receptionist_agent` | First point of contact — greets, answers basic Qs, captures name/contact |
| `lead_qualifier_agent` | Asks 1-2 sharp follow-up questions to score urgency/budget |
| `scheduler_agent` | Proposes appointment/inspection time windows and confirms bookings |
| `followup_agent` | Re-engages quiet leads as part of a 10-day nurture sequence |

## Project Structure

```
astra-multiagent-orchestrator/
├── backend/
│   ├── main.py              # FastAPI app + all API routes
│   ├── orchestrator.py      # Intent classification + agent routing
│   ├── models.py            # Pydantic request/response schemas
│   ├── database.py          # SQLite persistence layer
│   ├── config.py            # Env var loading
│   ├── requirements.txt
│   └── agents/
│       ├── base_agent.py         # Shared LLM-calling logic
│       ├── receptionist_agent.py
│       ├── lead_qualifier_agent.py
│       ├── scheduler_agent.py
│       └── followup_agent.py
├── frontend/
│   └── index.html            # Live dashboard (navy/orange Astra brand)
├── .env.example
├── .gitignore
├── run.sh
└── README.md
```

## Setup & Run Locally

```bash
git clone https://github.com/ha03441588567-sketch/astra-multiagent-orchestrator.git
cd astra-multiagent-orchestrator
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY

chmod +x run.sh
./run.sh
```

Then open **http://localhost:8000** for the dashboard (Swagger API docs at
**http://localhost:8000/docs**).

> No API key set? The agents still work — they fall back to a safe canned reply
> and simple keyword-based intent detection so the demo never crashes.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/orchestrate` | Send a customer message, get routed agent reply |
| GET | `/api/leads` | List captured leads (optional `?business_id=`) |
| GET | `/api/tasks` | List queued follow-up tasks |
| GET | `/api/conversations/{id}` | Full transcript of one conversation |
| GET | `/api/stats` | Dashboard summary stats |
| GET | `/api/agents` | List active agents and their roles |
| GET | `/health` | Health check |

### Example request

```bash
curl -X POST http://localhost:8000/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "business_id": "demo-biz-1",
    "niche": "roofing",
    "message": "Hi, I need someone to check my roof after last night storm"
  }'
```

## Deployment

Works out of the box on:
- **Railway** / **Render** — `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Hugging Face Spaces** (Docker SDK) — add a `Dockerfile` wrapping the same start command
- Any VPS with Python 3.10+

## Roadmap

- [ ] Add voice channel integration (Twilio / WhatsApp Business API)
- [ ] Multi-tenant business onboarding UI
- [ ] Per-niche prompt customization from the dashboard
- [ ] Analytics: conversion rate per agent, response time tracking

---
Built by **Karam Hussain Abbasi** — AI/ML & LLM Engineer, part of the
[AstraVoice / Astra AI Workforce Platform](https://github.com/ha03441588567-sketch).
