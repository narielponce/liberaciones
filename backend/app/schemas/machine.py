from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.machine import ParamType


# --- Parameter Schemas ---
class MachineParameterBase(BaseModel):
    label: str
    param_type: ParamType
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    order_index: int = 0
    is_required: bool = True


class MachineParameterCreate(MachineParameterBase):
    pass


class MachineParameterResponse(MachineParameterBase):
    id: int
    machine_id: int

    model_config = ConfigDict(from_attributes=True)


# --- Machine Schemas ---
class MachineBase(BaseModel):
    code: str = Field(..., description="Unique code stored in machine QR code")
    name: str
    section: str
    plant: Optional[str] = None
    cell: Optional[str] = None
    sector: Optional[str] = None
    is_active: bool = True


class MachineCreate(MachineBase):
    parameters: List[MachineParameterCreate] = []


class MachineUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    section: Optional[str] = None
    plant: Optional[str] = None
    cell: Optional[str] = None
    sector: Optional[str] = None
    is_active: Optional[bool] = None
    parameters: Optional[List[MachineParameterCreate]] = None


class MachineResponse(MachineBase):
    id: int
    created_at: datetime
    parameters: List[MachineParameterResponse] = []

    model_config = ConfigDict(from_attributes=True)
