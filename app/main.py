import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

from app.auth.auth_routes import router as auth_router
from app.auth.security import get_password_hash
from app.core.config import get_settings
from app.database.connection import SessionLocal
from app.limiter import limiter
from app.middlewares.request_middleware import RequestMiddleware
from app.models.device_model import Device
from app.models.user_model import User
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

logging.basicConfig(level=logging.INFO)

SEED_PASSWORD = "Admin1234"

SEED_USERS = [
    {"name": "Ana Garcia", "email": "ana@device.com", "role": "admin", "is_active": True},
    {"name": "Luis Perez", "email": "luis@device.com", "role": "support", "is_active": True},
    {"name": "Maria Lopez", "email": "maria@device.com", "role": "user", "is_active": False},
    {"name": "Carlos Ruiz", "email": "carlos@device.com", "role": "user", "is_active": True},
]

SEED_DEVICES = [
    {
        "name": "Laptop Lenovo ThinkPad",
        "serial_number": "LEN-2024-001",
        "device_type": "laptop",
        "brand": "Lenovo",
        "is_available": True,
    },
    {
        "name": "Tablet Samsung Galaxy",
        "serial_number": "SAM-TAB-002",
        "device_type": "tablet",
        "brand": "Samsung",
        "is_available": True,
    },
    {
        "name": "Proyector Epson",
        "serial_number": "EPS-PRO-003",
        "device_type": "proyector",
        "brand": "Epson",
        "is_available": True,
    },
]


def seed_data() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            hashed = get_password_hash(SEED_PASSWORD)
            for data in SEED_USERS:
                db.add(User(**data, hashed_password=hashed))
        if db.query(Device).count() == 0:
            for data in SEED_DEVICES:
                db.add(Device(**data))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_data()
    yield


settings = get_settings()

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST segura para gestión de usuarios, dispositivos y préstamos. "
        "OAuth2, JWT, CORS, middleware, rate limiting y validaciones Pydantic v2."
    ),
    version=settings.app_version,
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device.com",
    },
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestMiddleware)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


@app.get("/", tags=["General"], summary="Información de la API")
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "SQLite (device_systems.db)",
        "migrations": "Alembic",
        "security": "OAuth2 + JWT + Rate Limiting",
        "docs": "/docs",
        "redoc": "/redoc",
    }
