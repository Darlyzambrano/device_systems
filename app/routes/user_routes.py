from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response

from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

fake_db = [
    {"id": 1, "name": "Ana Garcia", "email": "ana@device.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Luis Perez", "email": "luis@device.com", "role": "support", "is_active": True},
    {"id": 3, "name": "Maria Lopez", "email": "maria@device.com", "role": "user", "is_active": False},
    {"id": 4, "name": "Carlos Ruiz", "email": "carlos@device.com", "role": "user", "is_active": True},
]

HEADERS = {"X-App-Name": "device_systems", "X-API-Version": "1.0"}


def _set_headers(response: Response) -> None:
    for key, value in HEADERS.items():
        response.headers[key] = value


@router.get("/", response_model=list[UserResponse])
def list_users(
    response: Response,
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    _set_headers(response)
    result = fake_db.copy()
    if role:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, response: Response):
    _set_headers(response)
    user = next((u for u in fake_db if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail=f"Usuario {user_id} no encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user_data: UserCreate, response: Response):
    _set_headers(response)
    if any(u["email"] == user_data.email for u in fake_db):
        raise HTTPException(status_code=409, detail=f"El correo {user_data.email} ya existe")
    new_user = {"id": max(u["id"] for u in fake_db) + 1, **user_data.model_dump()}
    fake_db.append(new_user)
    return new_user
