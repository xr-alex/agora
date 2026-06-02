# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agora is a multi-agent debate engine. A user submits a proposition; two AI agents argue in parallel (Pro / Con); a Judge agent synthesizes a verdict. All agent output is persisted in Supabase (PostgreSQL) and streamed live to a React frontend via Supabase Realtime.

## Running the App

**Backend** (Python 3.11, FastAPI):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

**Frontend** (React + Vite):
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

## Environment Setup

Both services need a `.env` file. Copy from `.env.example` and fill in values.

- `backend/.env` — requires `ANTHROPIC_API_KEY` (Supabase values are pre-filled in dev)
- `frontend/.env` — Supabase values are pre-filled in dev

## Database

Migrations live in `supabase/migrations/`. Run `001_initial.sql` once in the Supabase SQL editor before first use.

Two tables: `debates` (question, status) and `debate_turns` (role: pro/con/judge, content). Realtime is enabled on both.

## Architecture

```
frontend/src/
  components/
    DebateForm.tsx    — question input, POSTs to /debates
    DebateView.tsx    — subscribes to Supabase Realtime, renders live turns
    AgentCard.tsx     — single agent output panel (loading skeleton → content)
  lib/supabase.ts     — Supabase client (reads VITE_SUPABASE_* env vars)
  App.tsx             — routes between form and debate view

backend/app/
  main.py             — FastAPI app, POST /debates endpoint, background task trigger
  config.py           — pydantic-settings; swap LLM provider/model here
  debate/
    agents.py         — Pro, Con, Judge LangChain chains; get_llm() factory
    graph.py          — LangGraph state machine: debate_node (parallel) → judge_node → END
    models.py         — Pydantic request/response models + DebateState TypedDict
  db/client.py        — Supabase singleton client
```

## Key Patterns

**Swapping LLM providers:** Change `LLM_PROVIDER` and `LLM_MODEL` in `backend/.env`. Add new provider support in `agents.py::get_llm()`. Ollama example: `from langchain_ollama import ChatOllama`.

**Debate flow:** `POST /debates` creates a DB row and fires a `BackgroundTask`. The LangGraph graph runs `debate_node` (asyncio.gather on pro + con agents) then `judge_node`. Each node writes completed turns to Supabase. The frontend's Realtime subscription picks them up as they land.

**Adding debate rounds:** Extend `DebateState` with round tracking and add nodes/edges to the graph in `graph.py`.
