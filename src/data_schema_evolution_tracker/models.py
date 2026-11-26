from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

class SchemaContract(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    schema_id: str
    version: int
    fields: Dict[str, str]  # Field name -> Type string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ValidationResult(BaseModel):
    is_valid: bool
    drift_score: float
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class DriftReport(BaseModel):
    schema_id: str
    previous_version: int
    current_version: int
    drift_metrics: Dict[str, float]
    is_breaking: bool