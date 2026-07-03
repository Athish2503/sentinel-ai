import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
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
    statistics: Optional[Dict[str, Any]] = None
    feature_vectors: Optional[List[BaselineFeatureVectorResponse]] = None

    model_config = ConfigDict(from_attributes=True)

class BaselineTrainRequest(BaseModel):
    num_runs: int = 25
    use_real_agent: bool = False

class BaselineFeatureVectorBase(BaseModel):
    prompt: str
    sequence: List[str]
    tool_frequency: Dict[str, int]
    execution_order: List[str]
    execution_count: int
    average_execution_time: float
    parameter_length: int

class BaselineFeatureVectorResponse(BaselineFeatureVectorBase):
    id: uuid.UUID
    baseline_id: uuid.UUID
    session_id: Optional[uuid.UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BaselineTrainResponse(BaseModel):
    baseline_id: uuid.UUID
    model_version: str
    training_runs: int
    threshold: float
    created_at: datetime
    statistics: Dict[str, Any]
    feature_vectors: List[BaselineFeatureVectorResponse]

    model_config = ConfigDict(from_attributes=True)

