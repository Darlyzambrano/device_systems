from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.device_model import Device
from app.models.user_model import User
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

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
            for data in SEED_USERS:
                db.add(User(**data))
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


app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para gestión de usuarios, dispositivos y préstamos. "
        "SQLAlchemy, Alembic, relaciones One-to-Many y consultas con joins."
    ),
    version="4.0.0",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device.com",
    },
    lifespan=lifespan,
)

app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


@app.get("/", tags=["General"], summary="Información de la API")
def root():
    return {
        "app": "device_systems",
        "version": "4.0.0",
        "database": "SQLite (device_systems.db)",
        "migrations": "Alembic",
        "docs": "/docs",
        "redoc": "/redoc",
    }
