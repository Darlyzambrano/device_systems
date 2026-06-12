from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field

ALLOWED_ROLES = Literal["admin", "support", "user"]


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, description="Nombre completo del usuario")
    email: EmailStr = Field(..., description="Correo electrónico único")
    role: ALLOWED_ROLES = Field(..., description="Rol: admin, support o user")
    is_active: bool = Field(default=True, description="Estado activo del usuario")


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

    model_config = {"from_attributes": True}
