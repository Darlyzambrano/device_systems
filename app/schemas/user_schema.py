from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from app.schemas.auth_schema import PASSWORD_PATTERN

ALLOWED_ROLES = Literal["admin", "support", "user"]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único")
    role: ALLOWED_ROLES = Field(..., description="Rol: admin, support o user")
    is_active: bool = Field(default=True, description="Estado activo del usuario")
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Contraseña segura (opcional para creación administrativa)",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if " " in value or "\t" in value:
            raise ValueError("La contraseña no puede contener espacios en blanco")
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "La contraseña debe tener mínimo 8 caracteres, "
                "una mayúscula, una minúscula y un número"
            )
        return value


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único")
    role: ALLOWED_ROLES = Field(..., description="Rol: admin, support o user")
    is_active: bool = Field(..., description="Estado activo del usuario")


class UserPatch(BaseModel):
    name: Optional[str] = Field(None, min_length=3, description="Nombre completo del usuario")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico único")
    role: Optional[ALLOWED_ROLES] = Field(None, description="Rol: admin, support o user")
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
