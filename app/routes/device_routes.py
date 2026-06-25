from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies.user_dependencies import (
    get_device_or_404,
    get_device_service,
    get_loan_service,
    set_response_headers,
    verify_api_key,
)
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceResponse, DeviceUpdate
from app.schemas.loan_schema import LoanDetailResponse
from app.services.device_service import DeviceService
from app.services.loan_service import LoanService

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.get("/", response_model=list[DeviceResponse], summary="Listar dispositivos")
def list_devices(
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[DeviceService, Depends(get_device_service)],
    device_type: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    brand: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Buscar por nombre, serie o marca"),
):
    return service.list_devices(
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
    )


@router.get(
    "/{device_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Préstamos de un dispositivo",
    description="Historial de préstamos del dispositivo con joins a usuario.",
)
def get_device_loans(
    device_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.get_device_loans(device_id)


@router.get("/{device_id}", response_model=DeviceResponse, summary="Consultar dispositivo")
def get_device(
    device: Annotated[Device, Depends(get_device_or_404)],
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
):
    return device


@router.post("/", response_model=DeviceResponse, status_code=201, summary="Crear dispositivo")
def create_device(
    data: DeviceCreate,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[DeviceService, Depends(get_device_service)],
):
    return service.create_device(data)


@router.put("/{device_id}", response_model=DeviceResponse, summary="Actualizar dispositivo completo")
def update_device(
    device_id: int,
    data: DeviceUpdate,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[DeviceService, Depends(get_device_service)],
):
    return service.update_device(device_id, data)


@router.patch("/{device_id}", response_model=DeviceResponse, summary="Actualizar dispositivo parcial")
def patch_device(
    device_id: int,
    data: DevicePatch,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[DeviceService, Depends(get_device_service)],
):
    return service.patch_device(device_id, data)


@router.delete("/{device_id}", status_code=204, summary="Eliminar dispositivo")
def delete_device(
    device_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[DeviceService, Depends(get_device_service)],
):
    service.delete_device(device_id)
