from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, UserBrief, DeviceBrief

ALLOWED_STATUSES = {"active", "returned", "overdue"}


class LoanService:
    def __init__(self, db: Session):
        self.db = db

    def list_loans(
        self,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        device_id: Optional[int] = None,
        user_email: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> list[Loan]:
        query = self.db.query(Loan)
        if status:
            self._validate_status(status)
            query = query.filter(Loan.status == status)
        if user_id:
            query = query.filter(Loan.user_id == user_id)
        if device_id:
            query = query.filter(Loan.device_id == device_id)
        if user_email or device_type:
            query = query.join(User).join(Device)
            if user_email:
                query = query.filter(User.email.ilike(f"%{user_email}%"))
            if device_type:
                query = query.filter(Device.device_type == device_type)
        return query.order_by(Loan.loan_date.desc()).all()

    def list_loan_details(
        self,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        device_id: Optional[int] = None,
        user_email: Optional[str] = None,
        device_type: Optional[str] = None,
    ) -> list[LoanDetailResponse]:
        query = (
            self.db.query(Loan)
            .join(User, Loan.user_id == User.id)
            .join(Device, Loan.device_id == Device.id)
            .options(joinedload(Loan.user), joinedload(Loan.device))
        )
        filters = []
        if status:
            self._validate_status(status)
            filters.append(Loan.status == status)
        if user_id:
            filters.append(Loan.user_id == user_id)
        if device_id:
            filters.append(Loan.device_id == device_id)
        if user_email:
            filters.append(User.email.ilike(f"%{user_email}%"))
        if device_type:
            filters.append(Device.device_type == device_type)
        if filters:
            query = query.filter(and_(*filters))
        loans = query.order_by(Loan.loan_date.desc()).all()
        return [self._to_detail(loan) for loan in loans]

    def get_loan(self, loan_id: int) -> Loan:
        loan = self.db.query(Loan).filter(Loan.id == loan_id).first()
        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return loan

    def get_loan_detail(self, loan_id: int) -> LoanDetailResponse:
        loan = (
            self.db.query(Loan)
            .options(joinedload(Loan.user), joinedload(Loan.device))
            .filter(Loan.id == loan_id)
            .first()
        )
        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        return self._to_detail(loan)

    def get_user_loans(self, user_id: int) -> list[LoanDetailResponse]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return self.list_loan_details(user_id=user_id)

    def get_device_loans(self, device_id: int) -> list[LoanDetailResponse]:
        device = self.db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        return self.list_loan_details(device_id=device_id)

    def create_loan(self, data: LoanCreate) -> Loan:
        user = self.db.query(User).filter(User.id == data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        device = self.db.query(Device).filter(Device.id == data.device_id).first()
        if not device:
            raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
        if not device.is_available:
            raise HTTPException(status_code=409, detail="El dispositivo no está disponible")

        loan = Loan(user_id=data.user_id, device_id=data.device_id, status="active")
        device.is_available = False
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def return_loan(self, loan_id: int) -> Loan:
        loan = (
            self.db.query(Loan)
            .options(joinedload(Loan.device))
            .filter(Loan.id == loan_id)
            .first()
        )
        if not loan:
            raise HTTPException(status_code=404, detail="Préstamo no encontrado")
        if loan.status == "returned":
            raise HTTPException(status_code=409, detail="El préstamo ya fue devuelto")

        loan.status = "returned"
        loan.return_date = datetime.utcnow()
        loan.device.is_available = True
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def _to_detail(self, loan: Loan) -> LoanDetailResponse:
        return LoanDetailResponse(
            loan_id=loan.id,
            status=loan.status,
            loan_date=loan.loan_date,
            return_date=loan.return_date,
            user=UserBrief.model_validate(loan.user),
            device=DeviceBrief.model_validate(loan.device),
        )

    def _validate_status(self, status: str) -> None:
        if status not in ALLOWED_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Estado no válido: {status}. Válidos: active, returned, overdue",
            )
