# Agora

A multi-agent debate and reasoning engine. Submit a proposition and two AI agents argue for and against it in parallel — then a judge synthesizes a verdict.

## How it works

1. You enter a proposition ("Should I use TypeScript for my project?")
2. A **Pro** agent and a **Con** agent reason independently and simultaneously
3. A **Judge** agent evaluates both arguments and delivers a verdict
4. Responses stream token-by-token to the UI as they're generated

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, LangGraph, LangChain |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| Database | PostgreSQL (Supabase) |
| Streaming | Server-Sent Events (SSE) |
| Default LLM | Ollama (local) — swappable |

## Prerequisites

- Node.js 18+
- Python 3.11+
- [Ollama](https://ollama.com) with `llama3.2` pulled (`ollama pull llama3.2`)
- A [Supabase](https://supabase.com) project

## Setup

**1. Database**

Run `supabase/migrations/001_initial.sql` in the Supabase SQL Editor.

**2. Backend**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Supabase URL and key
```

See [`backend/README.md`](backend/README.md) for LLM provider options.

**3. Frontend**

```bash
cd frontend
npm install
cp .env.example .env   # fill in your Supabase URL and key
```

## Running

Start Ollama, then open two terminals:

```bash
# Terminal 1 — backend (http://localhost:8000)
cd backend && source .venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 — frontend (http://localhost:5173)
cd frontend
npm run dev -- --host
```

## Project structure

```
agora/
├── backend/          FastAPI app + LangGraph debate engine
├── frontend/         React UI with SSE streaming
└── supabase/
    └── migrations/   Database schema
```
