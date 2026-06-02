import asyncio
from typing import Optional
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from app.debate.models import DebateState
from app.debate.agents import run_pro_agent, run_con_agent, run_judge_agent
from app.db.client import get_supabase


def _get_queue(config: RunnableConfig) -> Optional[asyncio.Queue]:
    return config.get("configurable", {}).get("queue")


async def _run_and_signal(coro, queue: Optional[asyncio.Queue], role: str) -> str:
    """Run an agent coroutine, then push a turn_done event when it finishes."""
    result = await coro
    if queue:
        await queue.put({"type": "turn_done", "role": role})
    return result


async def debate_node(state: DebateState, config: RunnableConfig) -> DebateState:
    queue = _get_queue(config)
    pro, con = await asyncio.gather(
        _run_and_signal(run_pro_agent(state["question"], queue), queue, "pro"),
        _run_and_signal(run_con_agent(state["question"], queue), queue, "con"),
    )

    db = get_supabase()
    db.table("debate_turns").insert([
        {"debate_id": state["debate_id"], "role": "pro", "content": pro},
        {"debate_id": state["debate_id"], "role": "con", "content": con},
    ]).execute()

    return {**state, "pro_argument": pro, "con_argument": con}


async def judge_node(state: DebateState, config: RunnableConfig) -> DebateState:
    queue = _get_queue(config)
    verdict = await _run_and_signal(
        run_judge_agent(
            state["question"],
            state["pro_argument"],  # type: ignore[arg-type]
            state["con_argument"],  # type: ignore[arg-type]
            queue,
        ),
        queue,
        "judge",
    )

    db = get_supabase()
    db.table("debate_turns").insert(
        {"debate_id": state["debate_id"], "role": "judge", "content": verdict}
    ).execute()
    db.table("debates").update({"status": "completed"}).eq("id", state["debate_id"]).execute()

    if queue:
        await queue.put({"type": "debate_done"})

    return {**state, "verdict": verdict}


def build_graph():
    g = StateGraph(DebateState)
    g.add_node("debate", debate_node)
    g.add_node("judge", judge_node)
    g.set_entry_point("debate")
    g.add_edge("debate", "judge")
    g.add_edge("judge", END)
    return g.compile()


debate_graph = build_graph()
