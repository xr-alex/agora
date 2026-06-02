from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
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


async def _run_debate(debate_id: str, question: str) -> None:
    db = get_supabase()
    try:
        await debate_graph.ainvoke({
            "debate_id": debate_id,
            "question": question,
            "pro_argument": None,
            "con_argument": None,
            "verdict": None,
        })
    except Exception:
        db.table("debates").update({"status": "failed"}).eq("id", debate_id).execute()
        raise


@app.post("/debates", response_model=CreateDebateResponse, status_code=201)
async def create_debate(body: CreateDebateRequest, background_tasks: BackgroundTasks):
    db = get_supabase()
    result = db.table("debates").insert({
        "question": body.question,
        "status": "running",
    }).execute()
    debate_id: str = result.data[0]["id"]
    background_tasks.add_task(_run_debate, debate_id, body.question)
    return CreateDebateResponse(debate_id=debate_id)


@app.get("/debates/{debate_id}")
async def get_debate(debate_id: str):
    db = get_supabase()
    result = db.table("debates").select("*, debate_turns(*)").eq("id", debate_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Debate not found")
    return result.data[0]
