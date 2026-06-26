from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.auth_service import AuthService
from app.auth.security import create_access_token
from app.database.connection import get_db
from app.dependencies.auth_dependency import get_current_active_user
from app.limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import AuthUserResponse, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_service(db: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=201,
    summary="Registrar usuario",
    description="Crea un usuario con contraseña hasheada. Valida email único y contraseña segura.",
    responses={
        400: {"description": "Email duplicado o rol no permitido"},
        422: {"description": "Contraseña débil o datos inválidos"},
        429: {"description": "Demasiadas solicitudes"},
    },
)
@limiter.limit("3/minute")
def register(
    request: Request,
    user_data: UserRegister,
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    return service.register(user_data)


@router.post(
    "/login",
    response_model=Token,
    summary="Iniciar sesión",
    description="Autentica con email y contraseña. Retorna token JWT OAuth2.",
    responses={
        401: {"description": "Credenciales incorrectas"},
        403: {"description": "Usuario inactivo"},
        429: {"description": "Demasiadas solicitudes"},
    },
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[AuthService, Depends(get_auth_service)],
):
    user = service.authenticate(form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=AuthUserResponse,
    summary="Usuario autenticado",
    description="Retorna los datos del usuario autenticado mediante Bearer token.",
    responses={
        401: {"description": "Token inválido o ausente"},
        403: {"description": "Usuario inactivo"},
    },
)
def read_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
