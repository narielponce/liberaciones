from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.machine import Machine, MachineParameter, ParamType
from app.models.release import MachineRelease, ReleaseValue, ReleaseStatus
from app.schemas.release import ReleaseCreate, ReleaseResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/releases", tags=["Liberaciones de Máquinas"])


@router.post("", response_model=ReleaseResponse, status_code=status.HTTP_201_CREATED)
async def create_machine_release(
    release_in: ReleaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.OPERADOR, UserRole.ADMIN)),
):
    """
    Transactional release submission:
    - Validates machine and machine parameters.
    - Evaluates if numeric values fall outside min/max tolerance boundaries.
    - Evaluates boolean parameters (False = out of range / NOk).
    - Determines overall release status (OK vs REJECTED).
    - Saves MachineRelease and all ReleaseValues atomically in one transaction.
    """
    # 1. Fetch Machine and its parameters
    stmt = (
        select(Machine)
        .where(Machine.id == release_in.machine_id, Machine.is_active == True)
        .options(selectinload(Machine.parameters))
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Máquina no encontrada o inactiva"
        )

    # Map machine parameters by ID for quick lookup
    param_map = {p.id: p for p in machine.parameters}
    submitted_val_map = {v.parameter_id: v for v in release_in.values}

    # Verify that all required parameters are present
    for param in machine.parameters:
        if param.is_required and param.id not in submitted_val_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Falta la respuesta para el parámetro requerido: '{param.label}'"
            )

    has_out_of_range = False
    release_value_objects: List[ReleaseValue] = []

    # 2. Process and evaluate submitted values
    for val_input in release_in.values:
        param = param_map.get(val_input.parameter_id)
        if not param:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El parámetro ID {val_input.parameter_id} no pertenece a esta máquina"
            )

        is_out_of_range = False

        if param.param_type == ParamType.BOOLEAN:
            # For boolean checklist, False = NOk / Out of range
            if val_input.bool_value is False or val_input.bool_value is None:
                is_out_of_range = True
        elif param.param_type == ParamType.NUMERIC:
            num_val = val_input.numeric_value
            if num_val is None:
                is_out_of_range = True
            else:
                if param.min_value is not None and num_val < param.min_value:
                    is_out_of_range = True
                if param.max_value is not None and num_val > param.max_value:
                    is_out_of_range = True

        if is_out_of_range:
            has_out_of_range = True

        db_val = ReleaseValue(
            parameter_id=param.id,
            bool_value=val_input.bool_value,
            numeric_value=val_input.numeric_value,
            is_out_of_range=is_out_of_range,
            notes=val_input.notes,
        )
        release_value_objects.append(db_val)

    # 3. Determine Overall Release Status
    overall_status = ReleaseStatus.REJECTED if has_out_of_range else ReleaseStatus.OK

    # 4. Save Release and Values in Database Transaction
    db_release = MachineRelease(
        machine_id=machine.id,
        operator_id=current_user.id,
        status=overall_status,
        notes=release_in.notes,
        values=release_value_objects,
    )

    db.add(db_release)
    await db.commit()

    # Re-fetch with relationships loaded
    fetch_stmt = (
        select(MachineRelease)
        .where(MachineRelease.id == db_release.id)
        .options(
            selectinload(MachineRelease.operator),
            selectinload(MachineRelease.values).selectinload(ReleaseValue.parameter),
        )
    )
    res = await db.execute(fetch_stmt)
    full_release = res.scalar_one()

    return full_release


@router.get("", response_model=List[ReleaseResponse])
async def list_releases(
    machine_id: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List historical machine releases. Accessible to supervisors, admins, and operators.
    """
    stmt = select(MachineRelease).options(
        selectinload(MachineRelease.operator),
        selectinload(MachineRelease.values).selectinload(ReleaseValue.parameter),
    ).order_by(MachineRelease.timestamp.desc()).limit(limit)

    if machine_id:
        stmt = stmt.where(MachineRelease.machine_id == machine_id)

    result = await db.execute(stmt)
    releases = result.scalars().all()
    return releases


@router.get("/{release_id}", response_model=ReleaseResponse)
async def get_release_by_id(
    release_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed breakdown of a single release record.
    """
    stmt = (
        select(MachineRelease)
        .where(MachineRelease.id == release_id)
        .options(
            selectinload(MachineRelease.operator),
            selectinload(MachineRelease.values).selectinload(ReleaseValue.parameter),
        )
    )
    result = await db.execute(stmt)
    release = result.scalar_one_or_none()

    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de liberación no encontrado"
        )
    return release
