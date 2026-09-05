import enum
from typing import List, Optional
from sqlalchemy import String, Boolean, Float, Integer, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ParamType(str, enum.Enum):
    BOOLEAN = "BOOLEAN"
    NUMERIC = "NUMERIC"


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    section: Mapped[str] = mapped_column(String(100), nullable=False)
    plant: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cell: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parameters: Mapped[List["MachineParameter"]] = relationship(
        "MachineParameter", back_populates="machine", cascade="all, delete-orphan", order_by="MachineParameter.order_index"
    )
    releases: Mapped[List["MachineRelease"]] = relationship("MachineRelease", back_populates="machine")


class MachineParameter(Base):
    __tablename__ = "machine_parameters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    param_type: Mapped[ParamType] = mapped_column(
        SQLEnum(ParamType, name="param_type_enum"), nullable=False
    )
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    machine: Mapped["Machine"] = relationship("Machine", back_populates="parameters")
    release_values: Mapped[List["ReleaseValue"]] = relationship("ReleaseValue", back_populates="parameter")
