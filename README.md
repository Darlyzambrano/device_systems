# device_systems API

**Actividad:** GA1-220501096-01-AA1-EV11 – FastAPI Seguridad: Autenticación, Middleware, CORS, Rate Limiting y Validación Avanzada

**Rama:** `device_systems_security`

API REST segura para gestión de **usuarios**, **dispositivos** y **préstamos**.

Esta versión incluye:

- Autenticación **OAuth2** con **JWT**
- Hash seguro de contraseñas con **passlib[bcrypt]**
- Rutas protegidas por token y **roles** (`admin`, `support`, `user`)
- Validaciones avanzadas con **Pydantic v2**
- **Middleware** personalizado para trazabilidad y cabeceras
- **CORS** configurado para orígenes autorizados
- **Rate limiting** con **slowapi**
- Migraciones de Alembic para campos de autenticación

---

## Índice

1. [Descripción](#descripción)
2. [Tecnologías](#tecnologías)
3. [Estructura del proyecto](#estructura-del-proyecto)
4. [Instalación](#instalación)
5. [Configuración de entorno](#configuración-de-entorno)
6. [Migraciones](#migraciones)
7. [Ejecución](#ejecución)
8. [Endpoints principales](#endpoints-principales)
9. [Autenticación y autorización](#autenticación-y-autorización)
10. [Validaciones de seguridad](#validaciones-de-seguridad)
11. [CORS](#cors)
12. [Middleware personalizado](#middleware-personalizado)
13. [Rate limiting](#rate-limiting)
14. [Datos de prueba](#datos-de-prueba)
15. [Documentación y evidencia](#documentación-y-evidencia)
16. [Buenas prácticas aplicadas](#buenas-prácticas-aplicadas)

---

## Descripción

`device_systems` se actualiza a una API segura, preparada para frontend, con protección de rutas, validaciones robustas y registro de actividad.

Mantiene la gestión de usuarios, dispositivos y préstamos, agregando una capa de seguridad profesional.

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| FastAPI | API REST, OpenAPI y autenticación OAuth2 |
| SQLAlchemy | ORM y relaciones entre modelos |
| Alembic | Migraciones de base de datos |
| Pydantic v2 | Validaciones avanzadas de schemas |
| passlib[bcrypt] | Hash seguro de contraseñas |
| python-jose | Creación y verificación de JWT |
| slowapi | Rate limiting |
| python-dotenv | Variables de entorno |
| SQLite | Base de datos local |
| Uvicorn | Servidor ASGI |

---

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py
│   ├── limiter.py
│   ├── core/
│   │   └── config.py
│   ├── auth/
│   │   ├── auth_routes.py
│   │   ├── auth_service.py
│   │   └── security.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   ├── loan_schema.py
│   │   └── auth_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── dependencies/
│   │   ├── database_dependency.py
│   │   ├── auth_dependency.py
│   │   └── user_dependencies.py
│   └── middlewares/
│       └── request_middleware.py
├── alembic/
│   └── versions/
│       ├── 3281b01a7b06_create_devices_and_loans_tables.py
│       └── f7a2c9e1b4d0_add_authentication_fields_to_users.py
├── .env.example
├── alembic.ini
├── requirements.txt
├── test_ev11.py
└── README.md
```

---

## Instalación

```bash
git checkout device_systems_security
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

---

## Configuración de entorno

Copia `.env.example` a `.env` y ajusta los valores:

```env
DATABASE_URL=sqlite:///./device_systems.db
SECRET_KEY=cambia-esta-clave-secreta-en-producción
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Migraciones

Actualizar la base de datos:

```bash
python -m alembic upgrade head
```

Generar migración nueva si es necesario:

```bash
python -m alembic revision --autogenerate -m "add authentication fields to users"
python -m alembic upgrade head
```

---

## Ejecución

```bash
python -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Endpoints principales

- `/auth` — Autenticación y usuario actual
- `/users` — Gestión de usuarios
- `/devices` — Gestión de dispositivos
- `/loans` — Gestión de préstamos

---

## Autenticación y autorización

| Método | Ruta | Descripción | Límite |
|--------|------|-------------|--------|
| POST | `/auth/register` | Registra usuario con contraseña segura | 3/min |
| POST | `/auth/login` | Login y token JWT | 5/min |
| GET | `/auth/me` | Datos del usuario autenticado | — |

### Registro

Ejemplo `POST /auth/register`:

```json
{
  "name": "Juan Aprendiz",
  "email": "juan@sena.edu.co",
  "password": "Segura123",
  "role": "user"
}
```

### Login

Enviar como `application/x-www-form-urlencoded`:

```
username=juan@sena.edu.co&password=Segura123
```

Respuesta esperada:

```json
{
  "access_token": "<token_jwt>",
  "token_type": "bearer"
}
```

### Uso del token

```
Authorization: Bearer <access_token>
```

---

## Protección de rutas y permisos

| Ruta | Protección |
|------|------------|
| GET `/users` | Usuario autenticado |
| GET `/users/{user_id}` | Usuario autenticado |
| POST `/devices` | Admin o support |
| PUT `/devices/{device_id}` | Admin o support |
| DELETE `/devices/{device_id}` | Admin |
| POST `/loans` | Usuario autenticado |
| PATCH `/loans/{loan_id}/return` | Admin o support |
| GET `/loans/details` | Admin o support |

### Respuestas de seguridad

- `401 Unauthorized` — Token ausente o inválido
- `403 Forbidden` — Usuario sin permisos suficientes
- `429 Too Many Requests` — Límite de peticiones excedido

---

## Validaciones de seguridad

Las contraseñas deben cumplir con los siguientes requisitos:

- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número
- Sin espacios en blanco

El campo `hashed_password` no se retorna en los modelos de respuesta.

---

## CORS

La API utiliza CORS en `app.main` con:

- `allow_origins` desde `CORS_ORIGINS`
- `allow_credentials=True`
- `allow_methods=["*"]`
- `allow_headers=["*"]`

### Nota importante

No es seguro usar `allow_origins=["*"]` en producción cuando `allow_credentials=True`. Esto permite que cualquier dominio envíe peticiones con credenciales, lo que puede exponer la API a ataques CSRF y sesiones maliciosas. En producción se deben autorizar solo los dominios del frontend confiable.

---

## Middleware personalizado

Cada respuesta incluye cabeceras adicionales:

- `X-App-Name: device_systems`
- `X-Process-Time` (tiempo de respuesta en segundos)
- `X-Request-ID` (id de petición)

Además, el middleware registra método, ruta, estado y tiempo de ejecución.

---

## Rate limiting

Reglas configuradas:

- `POST /auth/login` → 5 solicitudes por minuto
- `POST /auth/register` → 3 solicitudes por minuto
- `GET /users` → 30 solicitudes por minuto
- `POST /loans` → 10 solicitudes por minuto

Cuando se supera el límite, la API devuelve `429 Too Many Requests`.

---

## Datos de prueba

Contraseña de seed para usuarios iniciales:

- `Admin1234`

Usuarios de ejemplo creados automáticamente:

- `ana@device.com` → `admin`
- `luis@device.com` → `support`
- `carlos@device.com` → `user`

---

## Documentación y evidencia

- Swagger/OpenAPI: `/docs`
- ReDoc: `/redoc`
- Imágenes y capturas: `docs/imagenes/EV11`

---

## Buenas prácticas aplicadas

- Hash seguro de contraseñas con `passlib[bcrypt]`
- Autenticación OAuth2 con JWT
- Rutas protegidas con dependencias de seguridad
- Validaciones robustas con Pydantic v2
- CORS limitado a orígenes autorizados
- Rate limiting para endpoints sensibles
- Separación clara entre `routes`, `services`, `schemas`, `dependencies` y `middlewares`

---

## Resumen

Esta entrega muestra una API `device_systems` segura y lista para frontend: autenticación, autorización por roles, middleware personalizado, CORS ajustado, rate limiting y validaciones avanzadas.

---

## Validación de contraseña (Pydantic v2)

- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Sin espacios en blanco

El campo `hashed_password` **nunca** se expone en los schemas de respuesta.

---

## CORS

Configurado en `main.py` para desarrollo:

```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

### ¿Por qué no usar `"*"` en producción con credenciales?

Cuando `allow_credentials=True`, el navegador envía cookies y cabeceras de autorización. Si `allow_origins` es `"*"`, cualquier sitio web podría hacer peticiones autenticadas a la API desde el navegador del usuario (ataques CSRF cross-origin). En producción se deben listar **explícitamente** los dominios del frontend autorizados.

---

## Middleware personalizado

Cada respuesta incluye:

| Cabecera | Ejemplo |
|----------|---------|
| `X-App-Name` | `device_systems` |
| `X-Process-Time` | `0.0042` |
| `X-Request-ID` | `8f42e9c1` |

También registra en log: método, ruta, código HTTP y tiempo de procesamiento.

---

## Rate limiting

| Endpoint | Límite |
|----------|--------|
| POST `/auth/login` | 5/min |
| POST `/auth/register` | 3/min |
| GET `/users` | 30/min |
| POST `/loans` | 10/min |

Respuesta al exceder límite: **429 Too Many Requests**

---

## Variables de entorno (`.env`)

```env
DATABASE_URL=sqlite:///./device_systems.db
SECRET_KEY=cambia-esta-clave-secreta-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Pruebas funcionales

```bash
pip install httpx
python test_ev11.py
```

Escenarios cubiertos:

1. Registro de usuario
2. Registro con contraseña débil (422)
3. Registro con email duplicado (400)
4. Login correcto
5. Login con contraseña incorrecta (401)
6. Consulta `/auth/me`
7. Acceso sin token (401)
8. Acceso con token inválido (401)
9. Usuario sin permisos (403)
10. Creación de dispositivo con rol permitido
11. Eliminación con rol no permitido (403)
12. CORS preflight
13. Cabeceras del middleware
14. Activación de rate limiting (429)
15. Swagger/OpenAPI con OAuth2

---

## Capturas (evidencias)

> Agrega tus capturas en `docs/imagenes/` con los nombres sugeridos.

| Evidencia | Archivo sugerido |
|-----------|------------------|
| Estructura del proyecto | `estructura_proyecto_ev11.png` |
| Migración Alembic aplicada | `alembic_upgrade_ev11.png` |
| Registro de usuario | `auth_register_ev11.png` |
| Login y token JWT | `auth_login_ev11.png` |
| GET `/auth/me` | `auth_me_ev11.png` |
| Acceso sin token (401) | `auth_sin_token_ev11.png` |
| Acceso sin permisos (403) | `auth_sin_rol_ev11.png` |
| Swagger con OAuth2 | `swagger_oauth2_ev11.png` |
| Cabeceras middleware | `middleware_headers_ev11.png` |
| Rate limiting (429) | `rate_limit_ev11.png` |

---

## Ramas

| Rama | Contenido |
|------|-----------|
| `main` | EV07 – GET/POST |
| `ev08` | CRUD en memoria |
| `ev09` | SQLAlchemy + SQLite |
| `device_systems_alembic_relaciones` | EV10 – Alembic, relaciones, joins |
| `device_systems_security` | EV11 – OAuth2, JWT, CORS, rate limiting |

---

## Reflexión final

La seguridad en APIs REST no es opcional: proteger credenciales con hash, validar tokens JWT, restringir operaciones por rol, limitar peticiones abusivas y configurar CORS de forma explícita son prácticas fundamentales antes de exponer una API a clientes frontend o servicios externos. Esta actividad transforma `device_systems` de una API funcional a una API **profesional y protegida**.

---

## Video

[Enlace al video de YouTube – explicación funcional y de seguridad]
