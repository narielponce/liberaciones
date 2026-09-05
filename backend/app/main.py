from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_v1_router
from app.seed import seed_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicación y configurando base de datos...")
    # Retry connecting and seeding DB with backoff for container startup readiness
    max_retries = 10
    retry_delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Intento {attempt}/{max_retries}: Ejecutando migración y semilla de base de datos...")
            await seed_data()
            logger.info("Base de datos y datos semilla listos.")
            break
        except Exception as e:
            logger.warning(f"Intento {attempt}/{max_retries} falló: {e}")
            if attempt == max_retries:
                logger.error("No se pudo conectar a la base de datos tras múltiples intentos.")
            else:
                import asyncio
                await asyncio.sleep(retry_delay)
    yield
    logger.info("Cerrando conexiones de base de datos...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Estado"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0-mvp",
    }
