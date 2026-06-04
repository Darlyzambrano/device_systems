from fastapi import FastAPI

from app.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems API",
    description=(
        "API REST para la gestión de usuarios del sistema device_systems. "
        "CRUD completo, validación con Pydantic, manejo de errores y Dependency Injection."
    ),
    version="2.0.0",
    contact={
        "name": "Equipo device_systems",
        "email": "soporte@device.com",
    },
)

app.include_router(user_router)


@app.get("/", tags=["General"], summary="Información de la API")
def root():
    return {
        "app": "device_systems",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }
