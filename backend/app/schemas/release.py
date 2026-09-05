from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.release import ReleaseStatus
from app.schemas.machine import MachineParameterResponse
from app.schemas.user import UserResponse


# Input for submitting individual parameter value
class ReleaseValueInput(BaseModel):
    parameter_id: int
    bool_value: Optional[bool] = None
    numeric_value: Optional[float] = None
    notes: Optional[str] = None


# Output response for parameter value
class ReleaseValueResponse(BaseModel):
    id: int
    release_id: int
    parameter_id: int
    bool_value: Optional[bool] = None
    numeric_value: Optional[float] = None
    is_out_of_range: bool
    notes: Optional[str] = None
    parameter: Optional[MachineParameterResponse] = None

    model_config = ConfigDict(from_attributes=True)


# Payload when submitting a machine release form
class ReleaseCreate(BaseModel):
    machine_id: int
    notes: Optional[str] = None
    values: List[ReleaseValueInput]


# Response returned after creating/reading a release
class ReleaseResponse(BaseModel):
    id: int
    machine_id: int
    operator_id: int
    timestamp: datetime
    status: ReleaseStatus
    notes: Optional[str] = None
    values: List[ReleaseValueResponse] = []
    operator: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
