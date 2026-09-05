import asyncio
import logging
from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.machine import Machine, MachineParameter, ParamType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_data():
    logger.info("Iniciando creación de tablas y datos semilla...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migration patch for schema updates
        await conn.execute(text("ALTER TABLE release_values ADD COLUMN IF NOT EXISTS notes TEXT;"))
        await conn.execute(text("ALTER TABLE machines ADD COLUMN IF NOT EXISTS plant VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE machines ADD COLUMN IF NOT EXISTS cell VARCHAR(100);"))
        await conn.execute(text("ALTER TABLE machines ADD COLUMN IF NOT EXISTS sector VARCHAR(100);"))

    async with AsyncSessionLocal() as session:
        # 1. Seed Users
        users_to_create = [
            {
                "email": "admin@planta.com",
                "password": "admin123",
                "full_name": "Administrador Principal",
                "role": UserRole.ADMIN,
            },
            {
                "email": "operador@planta.com",
                "password": "operador123",
                "full_name": "Juan Pérez (Operador)",
                "role": UserRole.OPERADOR,
            },
            {
                "email": "supervisor@planta.com",
                "password": "supervisor123",
                "full_name": "Carlos Rodríguez (Supervisor)",
                "role": UserRole.SUPERVISOR,
            },
        ]

        for udata in users_to_create:
            stmt = select(User).where(User.email == udata["email"])
            existing_user = (await session.execute(stmt)).scalar_one_or_none()
            if not existing_user:
                user = User(
                    email=udata["email"],
                    hashed_password=get_password_hash(udata["password"]),
                    full_name=udata["full_name"],
                    role=udata["role"],
                    is_active=True,
                )
                session.add(user)
                logger.info(f"Usuario creado: {udata['email']} ({udata['role'].value})")
            else:
                existing_user.hashed_password = get_password_hash(udata["password"])
                existing_user.role = udata["role"]
                existing_user.full_name = udata["full_name"]
                logger.info(f"Usuario actualizado: {udata['email']}")

        # 2. Seed Sample Machines & Parameters
        machines_data = [
            {
                "code": "MACH-CNC-01",
                "name": "Torno CNC Haas ST-20",
                "section": "Mecanizado de Precisión",
                "parameters": [
                    {
                        "label": "Inspección visual de fuga de refrigerante",
                        "param_type": ParamType.BOOLEAN,
                        "order_index": 1,
                        "is_required": True,
                    },
                    {
                        "label": "Presión hidráulica de sujeción de plato",
                        "param_type": ParamType.NUMERIC,
                        "min_value": 25.0,
                        "max_value": 35.0,
                        "unit": "bar",
                        "order_index": 2,
                        "is_required": True,
                    },
                    {
                        "label": "Temperatura del cabezal principal",
                        "param_type": ParamType.NUMERIC,
                        "min_value": 18.0,
                        "max_value": 65.0,
                        "unit": "°C",
                        "order_index": 3,
                        "is_required": True,
                    },
                    {
                        "label": "Parada de emergencia y resguardos operativos",
                        "param_type": ParamType.BOOLEAN,
                        "order_index": 4,
                        "is_required": True,
                    },
                ],
            },
            {
                "code": "MACH-INJ-02",
                "name": "Inyectora Engel Duo 500T",
                "section": "Inyección de Plásticos",
                "parameters": [
                    {
                        "label": "Temperatura de fusión Zona 1",
                        "param_type": ParamType.NUMERIC,
                        "min_value": 210.0,
                        "max_value": 245.0,
                        "unit": "°C",
                        "order_index": 1,
                        "is_required": True,
                    },
                    {
                        "label": "Presión de inyección inicial",
                        "param_type": ParamType.NUMERIC,
                        "min_value": 120.0,
                        "max_value": 160.0,
                        "unit": "bar",
                        "order_index": 2,
                        "is_required": True,
                    },
                    {
                        "label": "Nivel de lubricante centralizado",
                        "param_type": ParamType.BOOLEAN,
                        "order_index": 3,
                        "is_required": True,
                    },
                    {
                        "label": "Tiempo de enfriamiento de molde",
                        "param_type": ParamType.NUMERIC,
                        "min_value": 12.5,
                        "max_value": 18.0,
                        "unit": "seg",
                        "order_index": 4,
                        "is_required": True,
                    },
                ],
            },
        ]

        for mdata in machines_data:
            stmt = select(Machine).where(Machine.code == mdata["code"])
            existing_m = (await session.execute(stmt)).scalar_one_or_none()
            if not existing_m:
                machine = Machine(
                    code=mdata["code"],
                    name=mdata["name"],
                    section=mdata["section"],
                    is_active=True,
                )
                session.add(machine)
                await session.flush()

                for pdata in mdata["parameters"]:
                    param = MachineParameter(
                        machine_id=machine.id,
                        label=pdata["label"],
                        param_type=pdata["param_type"],
                        min_value=pdata.get("min_value"),
                        max_value=pdata.get("max_value"),
                        unit=pdata.get("unit"),
                        order_index=pdata["order_index"],
                        is_required=pdata["is_required"],
                    )
                    session.add(param)
                logger.info(f"Máquina creada: {mdata['code']} - {mdata['name']}")

        await session.commit()
        logger.info("Semilla de base de datos ejecutada con éxito.")


if __name__ == "__main__":
    asyncio.run(seed_data())
