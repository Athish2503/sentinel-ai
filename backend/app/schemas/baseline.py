import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BaselineBase(BaseModel):
    model_version: str
    training_runs: int
    threshold: float

class BaselineCreate(BaselineBase):
    pass

class BaselineResponse(BaselineBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
