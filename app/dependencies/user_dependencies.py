from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.device_service import DeviceService
from app.services.loan_service import LoanService
from app.services.user_service import UserService


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


def get_device_service(db: Annotated[Session, Depends(get_db)]) -> DeviceService:
    return DeviceService(db)


def get_loan_service(db: Annotated[Session, Depends(get_db)]) -> LoanService:
    return LoanService(db)


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
