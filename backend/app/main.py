import asyncio
import json
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from app.debate.models import CreateDebateRequest, CreateDebateResponse
from app.debate.graph import debate_graph
from app.db.client import get_supabase

app = FastAPI(title="Agora Debate Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory queues: one per active debate, keyed by debate_id.
# Consumed by the SSE stream endpoint; cleaned up after debate_done is sent.
_debate_queues: dict[str, asyncio.Queue] = {}


async def _run_debate(debate_id: str, question: str) -> None:
    queue = _debate_queues.get(debate_id)
    db = get_supabase()
    try:
        await debate_graph.ainvoke(
            {
                "debate_id": debate_id,
                "question": question,
                "pro_argument": None,
                "con_argument": None,
                "verdict": None,
            },
            config={"configurable": {"queue": queue}},
        )
    except Exception:
        db.table("debates").update({"status": "failed"}).eq("id", debate_id).execute()
        if queue:
            await queue.put({"type": "error", "message": "Debate failed"})
            await queue.put({"type": "debate_done"})
        raise
    finally:
        # Give the SSE consumer a moment to drain debate_done before cleanup
        await asyncio.sleep(5)
        _debate_queues.pop(debate_id, None)


@app.post("/debates", response_model=CreateDebateResponse, status_code=201)
async def create_debate(body: CreateDebateRequest, background_tasks: BackgroundTasks):
    db = get_supabase()
    result = db.table("debates").insert({
        "question": body.question,
        "status": "running",
    }).execute()
    debate_id: str = result.data[0]["id"]

    # Create queue before firing background task so the SSE endpoint can find it
    _debate_queues[debate_id] = asyncio.Queue()
    background_tasks.add_task(_run_debate, debate_id, body.question)

    return CreateDebateResponse(debate_id=debate_id)


@app.get("/debates/{debate_id}/stream")
async def stream_debate(debate_id: str):
    db = get_supabase()
    result = db.table("debates").select("status").eq("id", debate_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debate not found")

    status = result.data[0]["status"]

    # Debate already finished — replay full turns from DB
    if status == "completed":
        turns = db.table("debate_turns").select("*").eq("debate_id", debate_id).order("created_at").execute()

        async def replay():
            for turn in turns.data:
                yield f"data: {json.dumps({'type': 'full_turn', 'role': turn['role'], 'content': turn['content']})}\n\n"
            yield f"data: {json.dumps({'type': 'debate_done'})}\n\n"

        return StreamingResponse(replay(), media_type="text/event-stream")

    # Debate in progress — stream from queue
    queue = _debate_queues.get(debate_id)
    if not queue:
        raise HTTPException(status_code=503, detail="Stream not available — debate may have already completed")

    async def generate():
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] == "debate_done":
                break

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/debates/{debate_id}")
async def get_debate(debate_id: str):
    db = get_supabase()
    result = db.table("debates").select("*, debate_turns(*)").eq("id", debate_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debate not found")
    return result.data[0]
