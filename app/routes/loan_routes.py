from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.dependencies.user_dependencies import get_loan_service, set_response_headers, verify_api_key
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse
from app.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.get(
    "/details",
    response_model=list[LoanDetailResponse],
    summary="Préstamos con detalle (joins)",
    description="Consulta préstamos con información de usuario y dispositivo usando joins.",
)
def list_loan_details(
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
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
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
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
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.get_loan_detail(loan_id)


@router.post("/", response_model=LoanResponse, status_code=201, summary="Crear préstamo")
def create_loan(
    data: LoanCreate,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.create_loan(data)


@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    summary="Devolver dispositivo",
    description="Marca el préstamo como returned y libera el dispositivo.",
)
def return_loan(
    loan_id: int,
    _: Annotated[dict, Depends(verify_api_key)],
    __: Annotated[None, Depends(set_response_headers)],
    service: Annotated[LoanService, Depends(get_loan_service)],
):
    return service.return_loan(loan_id)
