from pydantic import BaseModel
from typing import List

class SimulateResponse(BaseModel):
    session_id: str
    attack_number: int
    prompt: str
    status: str
    score: float
    explanation: str
    tool_sequence: List[str]
