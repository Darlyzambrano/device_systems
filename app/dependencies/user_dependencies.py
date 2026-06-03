from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Response

from app.data import users_db
from app.services.user_service import UserService

ALLOWED_ROLES = {"admin", "support", "user"}


def get_api_config() -> dict:
    return {
        "app_name": "device_systems",
        "version": "2.0.0",
        "headers": {
            "X-App-Name": "device_systems",
            "X-API-Version": "2.0",
        },
    }


def get_user_service() -> UserService:
    return UserService()


def set_response_headers(
    response: Response,
    config: Annotated[dict, Depends(get_api_config)],
) -> None:
    for key, value in config["headers"].items():
        response.headers[key] = value


def get_user_or_404(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> dict:
    return service.get_user(user_id)


def validate_email_not_exists(
    email: str,
    exclude_id: Optional[int] = None,
) -> None:
    if users_db.email_exists(email, exclude_id=exclude_id):
        raise HTTPException(
            status_code=400,
            detail=f"El correo {email} ya está registrado",
        )


def validate_role(role: str) -> None:
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Rol no permitido: {role}. Roles válidos: admin, support, user",
        )


def verify_api_key(
    config: Annotated[dict, Depends(get_api_config)],
    x_api_key: Annotated[Optional[str], Header()] = None,
) -> dict:
    if x_api_key is None:
        return config
    if x_api_key != "device-systems-key":
        raise HTTPException(status_code=401, detail="Clave de API inválida")
    return config
