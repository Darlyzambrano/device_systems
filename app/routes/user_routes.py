from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response

from app.dependencies.user_dependencies import (
    get_user_or_404,
    get_user_service,
    set_response_headers,
    verify_api_key,
)
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Listar usuarios",
    description="Obtiene la lista de usuarios. Permite filtrar por rol y estado activo.",
    response_description="Lista de usuarios del sistema",
)
def list_users(
    response: Response,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
    role: Optional[str] = Query(None, description="Filtrar por rol: admin, support o user"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo"),
):
    return service.list_users(role=role, is_active=is_active)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Consultar usuario por ID",
    description="Obtiene la información de un usuario mediante su identificador.",
    response_description="Datos del usuario solicitado",
    responses={404: {"description": "Usuario no encontrado"}},
)
def get_user(
    user: Annotated[dict, Depends(get_user_or_404)],
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
):
    return user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=201,
    summary="Crear usuario",
    description="Registra un nuevo usuario con validación de datos.",
    response_description="Usuario creado exitosamente",
    responses={
        400: {"description": "Correo duplicado o rol no permitido"},
        422: {"description": "Datos de entrada inválidos"},
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
    description="Reemplaza completamente la información de un usuario existente.",
    response_description="Usuario actualizado exitosamente",
    responses={
        400: {"description": "Correo duplicado o rol no permitido"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Datos de entrada inválidos"},
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
    description="Modifica uno o más campos de un usuario existente.",
    response_description="Usuario actualizado parcialmente",
    responses={
        400: {"description": "Sin campos, correo duplicado o rol no permitido"},
        404: {"description": "Usuario no encontrado"},
        422: {"description": "Datos de entrada inválidos"},
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
    description="Elimina un usuario existente del sistema.",
    response_description="Usuario eliminado (sin contenido en la respuesta)",
    responses={404: {"description": "Usuario no encontrado"}},
)
def delete_user(
    user_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[UserService, Depends(get_user_service)],
):
    service.delete_user(user_id)
