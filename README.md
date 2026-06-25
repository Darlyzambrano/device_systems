# device_systems API

**Actividad:** GA1-220501096-01-AA1-EV10 – FastAPI Avanzado: Migraciones con Alembic, Asociaciones de Modelos y Consultas con Joins

**Rama:** `device_systems_alembic_relaciones`

API REST con **FastAPI**, **SQLAlchemy**, **Alembic** y **SQLite** para gestionar **usuarios**, **dispositivos** y **préstamos** con relaciones One-to-Many, integridad referencial y consultas con joins.

---

## Descripción

`device_systems` evoluciona desde un CRUD de una sola tabla hacia un sistema relacional completo:

- Migraciones de base de datos controladas con **Alembic**
- Modelos `User`, `Device` y `Loan` con `ForeignKey()` y `relationship()`
- CRUD de usuarios y dispositivos con filtros avanzados
- Gestión de préstamos (crear, devolver, validaciones de negocio)
- Consultas con `join()`, `where()`, `ilike()`, `and_()` / `or_()`
- Documentación Swagger/OpenAPI por tags: **Users**, **Devices**, **Loans**

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| FastAPI | API REST |
| SQLAlchemy | ORM y relaciones |
| Alembic | Migraciones de BD |
| SQLite | Base de datos local |
| Pydantic v2 | Validación entrada/salida |
| Uvicorn | Servidor |

---

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── device_routes.py
│   │   └── loan_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   └── dependencies/
│       ├── database_dependency.py
│       └── user_dependencies.py
├── alembic/
│   └── versions/
│       └── 3281b01a7b06_create_devices_and_loans_tables.py
├── alembic.ini
├── device_systems.db          # Generada con Alembic (no subir a git)
├── requirements.txt
└── README.md
```

---

## Relaciones entre modelos

| Relación | Tipo | Descripción |
|----------|------|-------------|
| User → Loan | One-to-Many | Un usuario puede tener muchos préstamos |
| Device → Loan | One-to-Many | Un dispositivo puede aparecer en varios préstamos históricos |
| Loan → User, Device | Many-to-One | Cada préstamo pertenece a un usuario y un dispositivo |

---

## Instalación y ejecución

```bash
git checkout device_systems_alembic_relaciones
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Migraciones con Alembic

```bash
# Inicializar (ya incluido en el repo)
python -m alembic init alembic

# Generar migración
python -m alembic revision --autogenerate -m "create devices and loans tables"

# Aplicar migraciones
python -m alembic upgrade head

# Ver historial
python -m alembic history
```

> **Nota:** Si la base de datos ya existe de una versión anterior, elimina `device_systems.db` antes de `upgrade head` para aplicar la migración inicial desde cero.

```bash
python -m uvicorn app.main:app --reload
```

| Recurso | URL |
|---------|-----|
| API | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

Al iniciar se insertan usuarios y dispositivos de ejemplo si las tablas están vacías.

---

## Endpoints

### Users (`/users`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users` | Listar con filtros `role`, `is_active`, orden |
| GET | `/users/{user_id}` | Consultar por ID |
| GET | `/users/{user_id}/loans` | Préstamos del usuario (joins) |
| POST | `/users` | Crear usuario |
| PUT | `/users/{user_id}` | Actualizar completo |
| PATCH | `/users/{user_id}` | Actualizar parcial |
| DELETE | `/users/{user_id}` | Eliminar |

### Devices (`/devices`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/devices` | Listar con filtros |
| GET | `/devices?device_type=laptop` | Filtrar por tipo |
| GET | `/devices?is_available=true` | Filtrar disponibilidad |
| GET | `/devices?brand=lenovo` | Filtrar por marca |
| GET | `/devices?search=thinkpad` | Búsqueda por nombre/serie/marca |
| GET | `/devices/{device_id}` | Consultar por ID |
| GET | `/devices/{device_id}/loans` | Historial de préstamos |
| POST | `/devices` | Crear dispositivo |
| PUT/PATCH | `/devices/{device_id}` | Actualizar |
| DELETE | `/devices/{device_id}` | Eliminar |

### Loans (`/loans`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/loans` | Listar préstamos |
| GET | `/loans/details` | Préstamos con usuario y dispositivo (joins) |
| GET | `/loans?status=active` | Filtrar por estado |
| GET | `/loans?user_email=aprendiz@sena.edu.co` | Filtrar por email |
| GET | `/loans?device_type=laptop` | Filtrar por tipo de dispositivo |
| GET | `/loans/{loan_id}` | Detalle con joins |
| POST | `/loans` | Crear préstamo |
| PATCH | `/loans/{loan_id}/return` | Devolver dispositivo |

### Ejemplo de respuesta con joins

```json
{
  "loan_id": 1,
  "status": "active",
  "loan_date": "2026-06-24T21:00:00",
  "return_date": null,
  "user": {
    "id": 1,
    "name": "Ana Garcia",
    "email": "ana@device.com"
  },
  "device": {
    "id": 1,
    "name": "Laptop Lenovo ThinkPad",
    "serial_number": "LEN-2024-001",
    "device_type": "laptop"
  }
}
```

---

## Códigos de respuesta

| Caso | Código |
|------|--------|
| Registro creado | 201 Created |
| Consulta / devolución exitosa | 200 OK |
| Eliminación exitosa | 204 No Content |
| Recurso no encontrado | 404 Not Found |
| Dato duplicado (serie, email) | 400 Bad Request |
| Dispositivo no disponible / préstamo ya devuelto | 409 Conflict |
| Validación Pydantic | 422 Unprocessable Entity |

---

## Pruebas funcionales

Ejecutar el script de pruebas incluido:

```bash
python test_ev10.py
```

Escenarios cubiertos:

1. Ejecutar migraciones con Alembic
2. Crear usuario
3. Crear dispositivo
4. Crear préstamo
5. Intentar prestar dispositivo no disponible (409)
6. Listar préstamos con joins (`/loans/details`)
7. Filtrar préstamos por estado
8. Filtrar por tipo de dispositivo
9. Consultar préstamos de un usuario
10. Devolver dispositivo
11. Validar dispositivo disponible de nuevo
12. Consultar historial de préstamos del dispositivo

---

## Capturas (evidencias)

> Agrega tus capturas en `docs/imagenes/` con los nombres sugeridos.

### Alembic

| Evidencia | Archivo sugerido |
|-----------|------------------|
| `alembic init alembic` | `alembic_init_ev10.png` |
| `alembic revision --autogenerate` | `alembic_revision_ev10.png` |
| `alembic upgrade head` | `alembic_upgrade_ev10.png` |
| `alembic history` | `alembic_history_ev10.png` |
| Estructura de tablas (users, devices, loans) | `tablas_bd_ev10.png` |

### Swagger UI v4.0.0

| Evidencia | Archivo sugerido |
|-----------|------------------|
| Vista general con tags Users, Devices, Loans | `swagger_vista_general_ev10.png` |
| POST /loans – crear préstamo | `swagger_post_loan_ev10.png` |
| GET /loans/details – joins | `swagger_loans_details_ev10.png` |
| Filtros en /devices y /loans | `swagger_filtros_ev10.png` |
| PATCH /loans/{id}/return | `swagger_return_loan_ev10.png` |
| Error 409 dispositivo no disponible | `swagger_error_409_ev10.png` |

---

## Ramas

| Rama | Contenido |
|------|-----------|
| `main` | EV07 – GET/POST |
| `ev08` | CRUD en memoria |
| `ev09` | SQLAlchemy + SQLite (solo users) |
| `device_systems_alembic_relaciones` | EV10 – Alembic, Device, Loan, joins |

---

## Reflexión

**Migraciones con Alembic** permiten versionar cambios estructurales de la base de datos de forma controlada, evitando inconsistencias entre entornos y facilitando el trabajo en equipo.

**Relaciones entre modelos** (`ForeignKey`, `relationship`, `back_populates`) garantizan integridad referencial: un préstamo siempre pertenece a un usuario y dispositivo existentes.

**Consultas con joins y filtros** permiten obtener información relacionada en una sola petición, reduciendo llamadas a la API y mejorando la experiencia del cliente.

---

## Video

