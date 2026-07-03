import uuid
from typing import List
from pydantic import BaseModel

class DetectRequest(BaseModel):
    session_id: uuid.UUID

class DetectResponse(BaseModel):
    score: float
    status: str
    reasons: List[str]
