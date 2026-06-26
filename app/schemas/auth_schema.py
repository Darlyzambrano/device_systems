import re
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ALLOWED_ROLES = Literal["admin", "support", "user"]
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)\S{8,}$")


class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único")
    password: str = Field(..., min_length=8, description="Contraseña segura")
    role: ALLOWED_ROLES = Field(default="user", description="Rol: admin, support o user")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if " " in value or "\t" in value:
            raise ValueError("La contraseña no puede contener espacios en blanco")
        if not PASSWORD_PATTERN.match(value):
            raise ValueError(
                "La contraseña debe tener mínimo 8 caracteres, "
                "una mayúscula, una minúscula y un número"
            )
        return value


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=1, description="Contraseña")


class Token(BaseModel):
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token OAuth2")


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class AuthUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
