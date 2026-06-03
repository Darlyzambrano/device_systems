from typing import Optional

fake_db: list[dict] = [
    {"id": 1, "name": "Ana Garcia", "email": "ana@device.com", "role": "admin", "is_active": True},
    {"id": 2, "name": "Luis Perez", "email": "luis@device.com", "role": "support", "is_active": True},
    {"id": 3, "name": "Maria Lopez", "email": "maria@device.com", "role": "user", "is_active": False},
    {"id": 4, "name": "Carlos Ruiz", "email": "carlos@device.com", "role": "user", "is_active": True},
]


def get_all() -> list[dict]:
    return fake_db.copy()


def get_by_id(user_id: int) -> Optional[dict]:
    return next((user for user in fake_db if user["id"] == user_id), None)


def email_exists(email: str, exclude_id: Optional[int] = None) -> bool:
    return any(
        user["email"] == email and user["id"] != exclude_id
        for user in fake_db
    )


def create(user_data: dict) -> dict:
    new_id = max(user["id"] for user in fake_db) + 1 if fake_db else 1
    new_user = {"id": new_id, **user_data}
    fake_db.append(new_user)
    return new_user


def update(user_id: int, user_data: dict) -> Optional[dict]:
    for index, user in enumerate(fake_db):
        if user["id"] == user_id:
            updated_user = {"id": user_id, **user_data}
            fake_db[index] = updated_user
            return updated_user
    return None


def partial_update(user_id: int, user_data: dict) -> Optional[dict]:
    user = get_by_id(user_id)
    if not user:
        return None
    updated_user = {**user, **user_data}
    for index, item in enumerate(fake_db):
        if item["id"] == user_id:
            fake_db[index] = updated_user
            return updated_user
    return None


def delete(user_id: int) -> bool:
    for index, user in enumerate(fake_db):
        if user["id"] == user_id:
            fake_db.pop(index)
            return True
    return False
