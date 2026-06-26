from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister

ALLOWED_ROLES = {"admin", "support", "user"}


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserRegister) -> User:
        self._validate_role(user_data.role)
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )

        user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
            is_active=True,
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

    def authenticate(self, email: str, password: str) -> User:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Usuario inactivo")
        return user

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def _validate_role(self, role: str) -> None:
        if role not in ALLOWED_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Rol no permitido: {role}. Roles válidos: admin, support, user",
            )
