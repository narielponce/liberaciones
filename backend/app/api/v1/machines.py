from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.machine import Machine, MachineParameter
from app.schemas.machine import (
    MachineCreate,
    MachineResponse,
    MachineUpdate,
    MachineParameterCreate,
    MachineParameterResponse,
)
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/machines", tags=["Máquinas y Parámetros"])


@router.get("", response_model=List[MachineResponse])
async def list_machines(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all machines with their inspection parameters.
    Administrators can optionally request inactive machines.
    """
    stmt = select(Machine).options(selectinload(Machine.parameters)).order_by(Machine.name)
    if not include_inactive:
        stmt = stmt.where(Machine.is_active == True)

    result = await db.execute(stmt)
    machines = result.scalars().all()
    return machines


@router.get("/code/{code}", response_model=MachineResponse)
async def get_machine_by_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve machine details and parameter checklist using unique machine QR code.
    Accessible to operators during plant inspections.
    """
    stmt = (
        select(Machine)
        .where(Machine.code == code, Machine.is_active == True)
        .options(selectinload(Machine.parameters))
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Máquina con código '{code}' no encontrada o inactiva"
        )
    return machine


@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine_by_id(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get machine by database ID.
    """
    stmt = (
        select(Machine)
        .where(Machine.id == machine_id)
        .options(selectinload(Machine.parameters))
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Máquina no encontrada"
        )
    return machine


@router.post("", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    machine_in: MachineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Create a new machine along with its common attributes and inspection parameters. Admin only.
    """
    # Check code uniqueness
    existing_stmt = select(Machine).where(Machine.code == machine_in.code)
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una máquina registrada con el código '{machine_in.code}'"
        )

    db_machine = Machine(
        code=machine_in.code,
        name=machine_in.name,
        section=machine_in.section,
        plant=machine_in.plant,
        cell=machine_in.cell,
        sector=machine_in.sector,
        is_active=machine_in.is_active,
    )
    db.add(db_machine)
    await db.flush()  # populate machine.id

    for idx, param in enumerate(machine_in.parameters):
        db_param = MachineParameter(
            machine_id=db_machine.id,
            label=param.label,
            param_type=param.param_type,
            min_value=param.min_value,
            max_value=param.max_value,
            unit=param.unit,
            order_index=param.order_index or (idx + 1),
            is_required=param.is_required,
        )
        db.add(db_param)

    await db.commit()

    # Re-query with parameters loaded
    stmt = (
        select(Machine)
        .where(Machine.id == db_machine.id)
        .options(selectinload(Machine.parameters))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(
    machine_id: int,
    machine_in: MachineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Update machine attributes and optionally replace/synchronize parameter definitions. Admin only.
    """
    stmt = (
        select(Machine)
        .where(Machine.id == machine_id)
        .options(selectinload(Machine.parameters))
    )
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    # If code is being updated, verify uniqueness
    if machine_in.code and machine_in.code != machine.code:
        existing_stmt = select(Machine).where(Machine.code == machine_in.code)
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe otra máquina con el código '{machine_in.code}'"
            )
        machine.code = machine_in.code

    if machine_in.name is not None:
        machine.name = machine_in.name
    if machine_in.section is not None:
        machine.section = machine_in.section
    if machine_in.plant is not None:
        machine.plant = machine_in.plant
    if machine_in.cell is not None:
        machine.cell = machine_in.cell
    if machine_in.sector is not None:
        machine.sector = machine_in.sector
    if machine_in.is_active is not None:
        machine.is_active = machine_in.is_active

    # If parameters array is provided, update parameter list
    if machine_in.parameters is not None:
        # Clear existing parameters
        await db.execute(delete(MachineParameter).where(MachineParameter.machine_id == machine.id))
        await db.flush()

        for idx, param in enumerate(machine_in.parameters):
            db_param = MachineParameter(
                machine_id=machine.id,
                label=param.label,
                param_type=param.param_type,
                min_value=param.min_value,
                max_value=param.max_value,
                unit=param.unit,
                order_index=param.order_index or (idx + 1),
                is_required=param.is_required,
            )
            db.add(db_param)

    await db.commit()

    # Re-fetch updated machine
    fetch_stmt = (
        select(Machine)
        .where(Machine.id == machine.id)
        .options(selectinload(Machine.parameters))
    )
    updated_res = await db.execute(fetch_stmt)
    return updated_res.scalar_one()


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete a machine. Admin only.
    """
    stmt = select(Machine).where(Machine.id == machine_id)
    result = await db.execute(stmt)
    machine = result.scalar_one_or_none()

    if not machine:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    await db.delete(machine)
    await db.commit()
    return None


@router.delete("/parameters/{param_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parameter(
    param_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """
    Delete an individual machine parameter. Admin only.
    """
    stmt = select(MachineParameter).where(MachineParameter.id == param_id)
    result = await db.execute(stmt)
    param = result.scalar_one_or_none()

    if not param:
        raise HTTPException(status_code=404, detail="Parámetro no encontrado")

    await db.delete(param)
    await db.commit()
    return None
