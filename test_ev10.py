"""Pruebas funcionales mínimas EV10."""
from fastapi.testclient import TestClient

from app.main import app

with TestClient(app) as client:
    # 1. Crear usuario
    r = client.post(
        "/users/",
        json={"name": "Test User", "email": "test@device.com", "role": "user", "is_active": True},
    )
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]

    # 2. Crear dispositivo
    r = client.post(
        "/devices/",
        json={
            "name": "Laptop Test",
            "serial_number": "TEST-001",
            "device_type": "laptop",
            "brand": "Lenovo",
            "is_available": True,
        },
    )
    assert r.status_code == 201, r.text
    device_id = r.json()["id"]

    # 3. Crear préstamo
    r = client.post("/loans/", json={"user_id": user_id, "device_id": device_id})
    assert r.status_code == 201, r.text
    loan_id = r.json()["id"]
    assert r.json()["status"] == "active"

    # 4. Dispositivo no disponible -> 409
    r = client.post("/loans/", json={"user_id": user_id, "device_id": device_id})
    assert r.status_code == 409

    # 5. Listar préstamos con detalle (joins)
    r = client.get("/loans/details")
    assert r.status_code == 200
    assert any(item["loan_id"] == loan_id for item in r.json())

    # 6. Filtrar por estado
    r = client.get("/loans/details?status=active")
    assert r.status_code == 200
    assert all(item["status"] == "active" for item in r.json())

    # 7. Filtrar por tipo de dispositivo
    r = client.get("/loans/details?device_type=laptop")
    assert r.status_code == 200

    # 8. Préstamos de usuario
    r = client.get(f"/users/{user_id}/loans")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # 9. Devolver dispositivo
    r = client.patch(f"/loans/{loan_id}/return")
    assert r.status_code == 200
    assert r.json()["status"] == "returned"

    # 10. Dispositivo disponible de nuevo
    r = client.get(f"/devices/{device_id}")
    assert r.status_code == 200
    assert r.json()["is_available"] is True

    # 11. Historial del dispositivo
    r = client.get(f"/devices/{device_id}/loans")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # 12. Filtros devices
    r = client.get("/devices?device_type=laptop&is_available=true")
    assert r.status_code == 200

print("Todas las pruebas EV10 pasaron correctamente.")
