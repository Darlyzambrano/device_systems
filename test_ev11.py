"""Pruebas funcionales mínimas EV11 – Seguridad y autenticación."""
from fastapi.testclient import TestClient

from app.main import app

ADMIN_EMAIL = "ana@device.com"
ADMIN_PASSWORD = "Admin1234"
USER_EMAIL = "carlos@device.com"


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


with TestClient(app) as client:
    print("1. Registro de usuario")
    r = client.post(
        "/auth/register",
        json={
            "name": "Nuevo Usuario",
            "email": "nuevo@device.com",
            "password": "Segura123",
            "role": "user",
        },
    )
    assert r.status_code == 201, r.text
    assert "hashed_password" not in r.text

    print("2. Registro con contraseña débil")
    r = client.post(
        "/auth/register",
        json={
            "name": "Debil",
            "email": "debil@device.com",
            "password": "123",
            "role": "user",
        },
    )
    assert r.status_code == 422

    print("3. Registro con email duplicado")
    r = client.post(
        "/auth/register",
        json={
            "name": "Duplicado",
            "email": "nuevo@device.com",
            "password": "Segura123",
            "role": "user",
        },
    )
    assert r.status_code == 400

    print("4. Login correcto")
    token = login(client, ADMIN_EMAIL, ADMIN_PASSWORD)

    print("5. Login con contraseña incorrecta")
    r = client.post(
        "/auth/login",
        data={"username": ADMIN_EMAIL, "password": "Incorrecta1"},
    )
    assert r.status_code == 401

    print("6. Consulta /auth/me")
    r = client.get("/auth/me", headers=auth_header(token))
    assert r.status_code == 200
    assert r.json()["email"] == ADMIN_EMAIL

    print("7. Acceso a ruta protegida sin token")
    r = client.get("/users/")
    assert r.status_code == 401

    print("8. Acceso con token inválido")
    r = client.get("/users/", headers={"Authorization": "Bearer token-invalido"})
    assert r.status_code == 401

    print("9. Acceso con usuario sin permisos (user intenta DELETE device)")
    user_token = login(client, USER_EMAIL, ADMIN_PASSWORD)
    r = client.delete("/devices/1", headers=auth_header(user_token))
    assert r.status_code == 403

    print("10. Creación de dispositivo con rol permitido (admin)")
    r = client.post(
        "/devices/",
        headers=auth_header(token),
        json={
            "name": "Monitor Dell",
            "serial_number": "DELL-MON-004",
            "device_type": "monitor",
            "brand": "Dell",
            "is_available": True,
        },
    )
    assert r.status_code == 201, r.text
    device_id = r.json()["id"]

    print("11. Eliminación de dispositivo con rol no permitido (user)")
    r = client.delete(f"/devices/{device_id}", headers=auth_header(user_token))
    assert r.status_code == 403

    print("12. Configuración CORS (cabecera presente en preflight)")
    r = client.options(
        "/users/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" in r.headers

    print("13. Cabeceras del middleware")
    r = client.get("/", headers=auth_header(token))
    assert r.headers.get("X-App-Name") == "device_systems"
    assert "X-Process-Time" in r.headers
    assert "X-Request-ID" in r.headers

    print("14. Rate limiting en login")
    blocked = False
    for _ in range(7):
        r = client.post(
            "/auth/login",
            data={"username": "fake@device.com", "password": "Fake1234"},
        )
        if r.status_code == 429:
            blocked = True
            break
    assert blocked, "El rate limiting debería activarse en POST /auth/login"

    print("15. Swagger/OpenAPI disponible")
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "/auth/login" in schema["paths"]
    assert "OAuth2PasswordBearer" in str(schema.get("components", {}))

    print("\nTodas las pruebas EV11 pasaron correctamente.")
