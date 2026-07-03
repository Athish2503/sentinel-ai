import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AlertBase(BaseModel):
    score: float
    reason: str

class AlertCreate(AlertBase):
    session_id: uuid.UUID

class AlertResponse(AlertBase):
    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
