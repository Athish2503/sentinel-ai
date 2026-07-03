import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.schemas.tool_call import ToolCallResponse
from app.schemas.alert import AlertResponse

class SessionBase(BaseModel):
    prompt: str

class SessionCreate(SessionBase):
    pass

class SessionUpdate(BaseModel):
    anomaly_score: Optional[float] = None
    status: Optional[str] = None

class SessionResponse(SessionBase):
    id: uuid.UUID
    created_at: datetime
    anomaly_score: float
    status: str
    tool_calls: List[ToolCallResponse] = []
    alerts: List[AlertResponse] = []

    model_config = ConfigDict(from_attributes=True)
