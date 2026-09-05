import enum
from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Boolean, Float, Text, ForeignKey, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ReleaseStatus(str, enum.Enum):
    OK = "OK"
    REJECTED = "REJECTED"


class MachineRelease(Base):
    __tablename__ = "machine_releases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), nullable=False)
    operator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[ReleaseStatus] = mapped_column(
        SQLEnum(ReleaseStatus, name="release_status_enum"), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    machine = relationship("Machine", back_populates="releases")
    operator = relationship("User", back_populates="releases")
    values: Mapped[List["ReleaseValue"]] = relationship(
        "ReleaseValue", back_populates="release", cascade="all, delete-orphan"
    )


class ReleaseValue(Base):
    __tablename__ = "release_values"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    release_id: Mapped[int] = mapped_column(ForeignKey("machine_releases.id", ondelete="CASCADE"), nullable=False)
    parameter_id: Mapped[int] = mapped_column(ForeignKey("machine_parameters.id"), nullable=False)
    bool_value: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    numeric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_out_of_range: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    release = relationship("MachineRelease", back_populates="values")
    parameter = relationship("MachineParameter", back_populates="release_values")
