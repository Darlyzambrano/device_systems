from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.user_dependencies import (
    get_loan_service,
    get_user_or_404,
    get_user_service,
    set_response_headers,
    verify_api_key,
)
from app.models.user_model import User
from app.schemas.loan_schema import LoanDetailResponse
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services.loan_service import LoanService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Lista usuarios desde la base de datos. Filtros por rol y estado. Orden por nombre o fecha.",
    response_description="Lista de usuarios",
)
def list_users(
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    order_by: Optional[str] = Query(
        "created_at",
        description="Ordenar por: name o created_at",
    ),
    sort: Optional[str] = Query("asc", description="asc o desc"),
):
    return service.list_users(
        role=role,
        is_active=is_active,
        order_by=order_by,
        sort=sort or "asc",
    )


@router.get(
    "/{user_id}/loans",
    response_model=list[LoanDetailResponse],
    summary="Préstamos de un usuario",
    description="Consulta dispositivos prestados al usuario con joins.",
)
def get_user_loans(
    user_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.get_user_loans(user_id)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Obtiene un usuario desde la base de datos por su ID.",
    response_description="Datos del usuario",
    responses={404: {"description": "Usuario no encontrado"}},
)
def get_user(
    user: Annotated[User, Depends(get_user_or_404)],
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
):
    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario en la base de datos.",
    response_description="Usuario creado",
    responses={
        400: {"description": "Correo duplicado o rol no permitido"},
        422: {"description": "Datos inválidos"},
    },
)
def create_user(
    user_data: UserCreate,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.create_user(user_data)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los campos del usuario en la base de datos.",
    response_description="Usuario actualizado",
    responses={
        400: {"description": "Correo duplicado o rol no permitido"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Datos inválidos"},
    },
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.update_user(user_id, user_data)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Actualizar usuario parcialmente",
    description="Actualiza campos específicos del usuario en la base de datos.",
    response_description="Usuario actualizado parcialmente",
    responses={
        400: {"description": "Sin campos, correo duplicado o rol no permitido"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Datos inválidos"},
    },
)
def patch_user(
    user_id: int,
    user_data: UserPatch,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    return service.patch_user(user_id, user_data)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Eliminar usuario",
    description="Elimina un usuario de la base de datos.",
    response_description="Usuario eliminado",
    responses={404: {"description": "Usuario no encontrado"}},
)
def delete_user(
    user_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    service.delete_user(user_id)
