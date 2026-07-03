import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ToolCallBase(BaseModel):
    tool_name: str
    tool_arguments: dict
    execution_order: int
    execution_time: float

class ToolCallCreate(ToolCallBase):
    session_id: uuid.UUID

class ToolCallResponse(ToolCallBase):
    id: uuid.UUID
    session_id: uuid.UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
