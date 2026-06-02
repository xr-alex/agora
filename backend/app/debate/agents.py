import asyncio
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings


def get_llm():
    if settings.llm_provider == "anthropic":
        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
        )
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=settings.llm_model, base_url=settings.ollama_base_url)
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


_PRO_SYSTEM = """You are a skilled debater arguing IN FAVOR of the proposition.
Build the strongest possible affirmative case in 3–4 concise, logical points.
Do not acknowledge counterarguments."""

_CON_SYSTEM = """You are a skilled debater arguing AGAINST the proposition.
Build the strongest possible opposing case in 3–4 concise, logical points.
Do not acknowledge counterarguments."""

_JUDGE_SYSTEM = """You are an impartial judge evaluating a debate.
Given arguments from both sides:
1. Identify the strongest point on each side.
2. Note any logical weaknesses.
3. Deliver a reasoned verdict — which case was more compelling and why.
Be concise and fair."""


async def _stream_agent(
    role: str,
    messages: list,
    queue: Optional[asyncio.Queue],
) -> str:
    llm = get_llm()
    full_response = ""
    async for chunk in llm.astream(messages):
        token = str(chunk.content)
        if token:
            full_response += token
            if queue:
                await queue.put({"type": "token", "role": role, "content": token})
    return full_response


async def run_pro_agent(question: str, queue: Optional[asyncio.Queue] = None) -> str:
    return await _stream_agent("pro", [
        SystemMessage(content=_PRO_SYSTEM),
        HumanMessage(content=f"Proposition: {question}\n\nMake your case."),
    ], queue)


async def run_con_agent(question: str, queue: Optional[asyncio.Queue] = None) -> str:
    return await _stream_agent("con", [
        SystemMessage(content=_CON_SYSTEM),
        HumanMessage(content=f"Proposition: {question}\n\nMake your case."),
    ], queue)


async def run_judge_agent(
    question: str,
    pro: str,
    con: str,
    queue: Optional[asyncio.Queue] = None,
) -> str:
    return await _stream_agent("judge", [
        SystemMessage(content=_JUDGE_SYSTEM),
        HumanMessage(content=(
            f"Proposition: {question}\n\n"
            f"PRO ARGUMENT:\n{pro}\n\n"
            f"CON ARGUMENT:\n{con}\n\n"
            "Evaluate and deliver your verdict."
        )),
    ], queue)
