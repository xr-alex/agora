from pydantic import BaseModel
from typing import Literal, Optional
from typing_extensions import TypedDict


class CreateDebateRequest(BaseModel):
    question: str


class CreateDebateResponse(BaseModel):
    debate_id: str


# LangGraph state — all fields must be present; use None for unset values
class DebateState(TypedDict):
    debate_id: str
    question: str
    pro_argument: Optional[str]
    con_argument: Optional[str]
    verdict: Optional[str]


DebateRole = Literal["pro", "con", "judge"]
DebateStatus = Literal["pending", "running", "completed", "failed"]
