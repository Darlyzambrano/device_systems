from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserPatch, UserUpdate

ALLOWED_ROLES = {"admin", "support", "user"}


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        order_by: Optional[str] = None,
        sort: str = "asc",
    ) -> list[User]:
        query = self.db.query(User)
        if role:
            self._validate_role(role)
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        order_column = User.name if order_by == "name" else User.created_at
        if sort == "desc":
            query = query.order_by(order_column.desc())
        else:
            query = query.order_by(order_column.asc())

        return query.all()

    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_data: UserCreate) -> User:
        self._validate_role(user_data.role)
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )
        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password or "ChangeMe123"),
            role=user_data.role,
            is_active=user_data.is_active,
        )
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        self._validate_role(user_data.role)
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        existing = self.get_user_by_email(user_data.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )

        for field, value in user_data.model_dump().items():
            setattr(user, field, value)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )
        self.db.refresh(user)
        return user

    def patch_user(self, user_id: int, user_data: UserPatch) -> User:
        patch_data = user_data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(
                status_code=400,
                detail="Debe enviar al menos un campo para actualizar",
            )

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if "role" in patch_data:
            self._validate_role(patch_data["role"])
        if "email" in patch_data:
            existing = self.get_user_by_email(patch_data["email"])
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"El correo {patch_data['email']} ya está registrado",
                )

        for field, value in patch_data.items():
            setattr(user, field, value)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            email = patch_data.get("email", user.email)
            raise HTTPException(
                status_code=400,
                detail=f"El correo {email} ya está registrado",
            )
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        self.db.delete(user)
        self.db.commit()

    def _validate_role(self, role: str) -> None:
        if role not in ALLOWED_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Rol no permitido: {role}. Roles válidos: admin, support, user",
            )
