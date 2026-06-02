import asyncio
from langgraph.graph import StateGraph, END
from app.debate.models import DebateState
from app.debate.agents import run_pro_agent, run_con_agent, run_judge_agent
from app.db.client import get_supabase


async def debate_node(state: DebateState) -> DebateState:
    """Run pro and con agents in parallel, then persist both turns."""
    pro, con = await asyncio.gather(
        run_pro_agent(state["question"]),
        run_con_agent(state["question"]),
    )

    db = get_supabase()
    db.table("debate_turns").insert([
        {"debate_id": state["debate_id"], "role": "pro", "content": pro},
        {"debate_id": state["debate_id"], "role": "con", "content": con},
    ]).execute()

    return {**state, "pro_argument": pro, "con_argument": con}


async def judge_node(state: DebateState) -> DebateState:
    """Run the judge agent after both sides have argued."""
    verdict = await run_judge_agent(
        state["question"],
        state["pro_argument"],  # type: ignore[arg-type]
        state["con_argument"],  # type: ignore[arg-type]
    )

    db = get_supabase()
    db.table("debate_turns").insert(
        {"debate_id": state["debate_id"], "role": "judge", "content": verdict}
    ).execute()
    db.table("debates").update({"status": "completed"}).eq("id", state["debate_id"]).execute()

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
