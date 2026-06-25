from typing import Annotated, Optional

from fastapi import Depends, Header, HTTPException, Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.device_service import DeviceService
from app.services.loan_service import LoanService
from app.services.user_service import UserService


def get_api_config() -> dict:
    return {
        "app_name": "device_systems",
        "version": "4.0.0",
        "headers": {
            "X-App-Name": "device_systems",
            "X-API-Version": "4.0",
        },
    }


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


def get_device_service(db: Annotated[Session, Depends(get_db)]) -> DeviceService:
    return DeviceService(db)


def get_loan_service(db: Annotated[Session, Depends(get_db)]) -> LoanService:
    return LoanService(db)


def set_response_headers(
    response: Response,
    config: Annotated[dict, Depends(get_api_config)],
) -> None:
    for key, value in config["headers"].items():
        response.headers[key] = value


def get_user_or_404(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.get_user(user_id)


def get_device_or_404(
    device_id: int,
    service: Annotated[DeviceService, Depends(get_device_service)],
):
    return service.get_device(device_id)


def verify_api_key(
    config: Annotated[dict, Depends(get_api_config)],
    x_api_key: Annotated[Optional[str], Header()] = None,
) -> dict:
    if x_api_key is None:
        return config
    if x_api_key != "device-systems-key":
        raise HTTPException(status_code=401, detail="Clave de API inválida")
    return config
