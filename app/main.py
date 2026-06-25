from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal, init_db
from app.models.user_model import User
from app.routes.user_routes import router as user_router

SEED_USERS = [
    {"name": "Ana Garcia", "email": "ana@device.com", "role": "admin", "is_active": True},
    {"name": "Luis Perez", "email": "luis@device.com", "role": "support", "is_active": True},
    {"name": "Maria Lopez", "email": "maria@device.com", "role": "user", "is_active": False},
    {"name": "Carlos Ruiz", "email": "carlos@device.com", "role": "user", "is_active": True},
]


def seed_users() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            for data in SEED_USERS:
                db.add(User(**data))
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_users()
    yield


app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para gestión de usuarios con persistencia en base de datos SQLite "
        "mediante SQLAlchemy. CRUD completo, validación Pydantic y documentación OpenAPI."
    ),
    version="3.0.0",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device.com",
    },
    lifespan=lifespan,
)

app.include_router(user_router)


@app.get("/", tags=["General"], summary="Información de la API")
def root():
    return {
        "app": "device_systems",
        "version": "3.0.0",
        "database": "SQLite (device_systems.db)",
        "docs": "/docs",
        "redoc": "/redoc",
    }
