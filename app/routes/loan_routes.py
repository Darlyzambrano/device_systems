from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Request

from app.dependencies.auth_dependency import get_current_active_user, require_admin_or_support
from app.dependencies.user_dependencies import get_loan_service
from app.limiter import limiter
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Préstamos con detalle (joins)",
    description="Consulta préstamos con información de usuario y dispositivo. Requiere admin o support.",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere rol admin o support"},
    },
)
def list_loan_details(
    _: Annotated[User, Depends(require_admin_or_support)],
    service: Annotated[LoanService, Depends(get_loan_service)],
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    device_id: Optional[int] = Query(None),
    user_email: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
):
    return service.list_loan_details(
        status=status,
        user_id=user_id,
        device_id=device_id,
        user_email=user_email,
        device_type=device_type,
    )


@router.get("/", response_model=list[LoanResponse], summary="Listar préstamos")
def list_loans(
    _: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[LoanService, Depends(get_loan_service)],
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    device_id: Optional[int] = Query(None),
    user_email: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
):
    return service.list_loans(
        status=status,
        user_id=user_id,
        device_id=device_id,
        user_email=user_email,
        device_type=device_type,
    )


@router.get("/{loan_id}", response_model=LoanDetailResponse, summary="Consultar préstamo con detalle")
def get_loan(
    loan_id: int,
    _: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.get_loan_detail(loan_id)


@router.post(
    "/",
    response_model=LoanResponse,
    status_code=201,
    summary="Crear préstamo",
    responses={
        401: {"description": "No autenticado"},
        429: {"description": "Demasiadas solicitudes"},
    },
)
@limiter.limit("10/minute")
def create_loan(
    request: Request,
    data: LoanCreate,
    _: Annotated[User, Depends(get_current_active_user)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.create_loan(data)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver dispositivo",
    description="Marca el préstamo como returned y libera el dispositivo. Requiere admin o support.",
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Se requiere rol admin o support"},
    },
)
def return_loan(
    loan_id: int,
    _: Annotated[User, Depends(require_admin_or_support)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.return_loan(loan_id)
