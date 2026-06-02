# Agora — Backend

FastAPI service that orchestrates the multi-agent debate using LangGraph.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/debates` | Start a new debate. Body: `{ "question": "..." }`. Returns `{ "debate_id": "..." }`. |
| `GET` | `/debates/{id}` | Fetch a debate with all its turns. |

## Switching LLM Providers

Edit `.env`:

```
# Anthropic (default)
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-6

# Ollama (local)
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2
```

Then add the corresponding case in `app/debate/agents.py::get_llm()` and install the provider package (e.g. `pip install langchain-ollama`).
