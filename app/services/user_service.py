from typing import Optional

from fastapi import HTTPException

from app.data import users_db
from app.schemas.user_schema import UserCreate, UserPatch, UserUpdate

ALLOWED_ROLES = {"admin", "support", "user"}


class UserService:
    def list_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> list[dict]:
        users = users_db.get_all()
        if role:
            self._validate_role(role)
            users = [user for user in users if user["role"] == role]
        if is_active is not None:
            users = [user for user in users if user["is_active"] == is_active]
        return users

    def get_user(self, user_id: int) -> dict:
        user = users_db.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def create_user(self, user_data: UserCreate) -> dict:
        self._validate_role(user_data.role)
        if users_db.email_exists(user_data.email):
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )
        return users_db.create(user_data.model_dump())

    def update_user(self, user_id: int, user_data: UserUpdate) -> dict:
        self._validate_role(user_data.role)
        if not users_db.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if users_db.email_exists(user_data.email, exclude_id=user_id):
            raise HTTPException(
                status_code=400,
                detail=f"El correo {user_data.email} ya está registrado",
            )
        return users_db.update(user_id, user_data.model_dump())

    def patch_user(self, user_id: int, user_data: UserPatch) -> dict:
        patch_data = user_data.model_dump(exclude_unset=True)
        if not patch_data:
            raise HTTPException(
                status_code=400,
                detail="Debe enviar al menos un campo para actualizar",
            )
        if not users_db.get_by_id(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if "role" in patch_data:
            self._validate_role(patch_data["role"])
        if "email" in patch_data and users_db.email_exists(
            patch_data["email"], exclude_id=user_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"El correo {patch_data['email']} ya está registrado",
            )
        return users_db.partial_update(user_id, patch_data)

    def delete_user(self, user_id: int) -> None:
        if not users_db.delete(user_id):
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

    def _validate_role(self, role: str) -> None:
        if role not in ALLOWED_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Rol no permitido: {role}. Roles válidos: admin, support, user",
            )
