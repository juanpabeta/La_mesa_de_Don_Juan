# Backend de Gestión de Pedidos para Restaurantes

API backend para administrar usuarios, roles, mesas, menú, pedidos, incidencias y reportes de un restaurante.

Está construido con **FastAPI**, **SQLAlchemy 2**, **PostgreSQL**, **Alembic** y **Pydantic Settings**.

## Contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Configuración](#configuración)
- [Ejecución local](#ejecución-local)
- [Ejecución con Docker](#ejecución-con-docker)
- [Migraciones](#migraciones)
- [Crear el primer administrador](#crear-el-primer-administrador)
- [Autenticación y roles](#autenticación-y-roles)
- [Módulos y endpoints](#módulos-y-endpoints)
- [Pruebas](#pruebas)
- [Health checks](#health-checks)
- [Solución de problemas](#solución-de-problemas)
- [Despliegue](#despliegue)

## Características

- Autenticación con JWT almacenado en cookie `HttpOnly`.
- Sesiones persistidas en PostgreSQL y revocación de sesiones al cerrar sesión.
- Control de acceso por roles.
- Gestión de mesas y estados de disponibilidad.
- Gestión de platos y disponibilidad del menú.
- Creación de pedidos con reserva atómica de mesa.
- Máquina de estados para pedidos.
- Marcado de pedidos retrasados.
- Registro auditable de incidencias.
- Eliminación lógica de pedidos e incidencias.
- Reportes de tiempos de preparación y exportación CSV.
- Migraciones versionadas con Alembic.
- Ejecución en Docker con usuario no root.

## Arquitectura

```text
backend/
├── app/
│   ├── core/
│   │   ├── bootstrap.py       # Crea el primer usuario ADMIN
│   │   ├── config.py          # Configuración por variables de entorno
│   │   ├── database.py        # Motor y sesiones SQLAlchemy
│   │   ├── dependencies.py    # Autenticación y autorización
│   │   ├── exceptions.py      # Errores HTTP de la aplicación
│   │   └── security.py        # Bcrypt y JWT
│   ├── modules/
│   │   ├── auth/              # Login, logout y sesión actual
│   │   ├── usuarios/          # Usuarios y roles
│   │   ├── mesas/             # Mesas y estados
│   │   ├── menu/              # Platos y disponibilidad
│   │   ├── pedidos/           # Pedidos, detalles y estados
│   │   ├── incidencias/       # Incidencias auditables
│   │   └── reportes/          # Estadísticas y exportaciones
│   └── main.py                # Aplicación FastAPI y routers
├── alembic/
│   ├── env.py
│   └── versions/              # Migraciones de base de datos
├── tests/                     # Pruebas automatizadas
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── requirements-dev.txt
```

Cada módulo separa normalmente:

- `routes.py`: endpoints HTTP.
- `schemas.py`: validación de entrada y salida.
- `services.py`: reglas de negocio.
- `repositories.py`: consultas y persistencia.
- `models.py`: modelos SQLAlchemy.

## Requisitos

Para ejecutar localmente:

- Python 3.13.
- PostgreSQL 16 o superior.
- Un entorno virtual de Python.

Para ejecutar con Docker:

- Docker Desktop iniciado.
- Docker Compose disponible.

## Configuración

1. Copia el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

2. Edita `.env` y configura las variables necesarias.

### Variables principales

| Variable                    | Uso                                                  |
| --------------------------- | ---------------------------------------------------- |
| `APP_ENV`                 | Entorno: `development`, `test` o `production`. |
| `API_V1_PREFIX`           | Prefijo de la API, normalmente `/api/v1`.          |
| `DATABASE_URL`            | Conexión PostgreSQL para ejecución local.          |
| `SECRET_KEY`              | Clave usada para firmar JWT.                         |
| `JWT_ALGORITHM`           | Algoritmo JWT, actualmente `HS256`.                |
| `ACCESS_TOKEN_MINUTES`    | Duración de la sesión.                             |
| `AUTH_COOKIE_NAME`        | Nombre de la cookie de autenticación.               |
| `COOKIE_SECURE`           | Debe ser `true` cuando se usa HTTPS.               |
| `COOKIE_SAMESITE`         | Política de cookie: `lax`, `strict` o `none`. |
| `CORS_ORIGINS`            | Lista JSON de orígenes permitidos.                  |
| `ENABLE_DELAY_MONITOR`    | Activa el monitor interno de pedidos retrasados.     |
| `DB_POOL_SIZE`            | Tamaño base del pool de conexiones.                 |
| `DB_MAX_OVERFLOW`         | Conexiones adicionales permitidas.                   |
| `DB_POOL_TIMEOUT_SECONDS` | Tiempo máximo esperando una conexión.              |

Para Docker Compose también se necesitan:

```env
POSTGRES_DB=restaurantes
POSTGRES_USER=restaurantes_app
POSTGRES_PASSWORD=una-contraseña-segura
```

`POSTGRES_PASSWORD` es la contraseña del usuario de PostgreSQL. No es la contraseña del administrador de la aplicación.

En Railway no copies estas tres variables manualmente desde el entorno local. Configura `DATABASE_URL` como referencia a la variable `DATABASE_URL` del servicio PostgreSQL del mismo proyecto y entorno.

El archivo `.env` contiene configuración local y no debe subirse al repositorio. Usa `.env.example` como plantilla sin secretos.

## Ejecución local

Desde la carpeta `backend`:

### Windows PowerShell

```powershell
py -m venv .venv
\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Configura `DATABASE_URL` para que apunte a PostgreSQL en tu máquina, por ejemplo:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/restaurantes
```

Aplica las migraciones:

```powershell
alembic upgrade head
```

Inicia la API:

```powershell
uvicorn app.main:app --reload
```

La API quedará disponible en:

- `http://localhost:8000/health`
- `http://localhost:8000/ready`
- `http://localhost:8000/docs` en desarrollo

## Ejecución con Docker

Desde la carpeta `backend` y con Docker Desktop iniciado:

```powershell
docker compose up -d db
```

Ejecuta las migraciones como paso separado:

```powershell
docker compose run --rm api alembic upgrade head
```

Inicia la API:

```powershell
docker compose up -d api
```

Consulta los logs:

```powershell
docker compose logs api --tail=100
```

La API estará disponible en `http://localhost:8000`.

## Variables de Railway

Configura estas variables en el servicio de la API:

| Variable | Tipo | Valor |
|---|---|---|
| `APP_ENV` | Variable | `production` |
| `DATABASE_URL` | Referencia | `${{Postgres.DATABASE_URL}}`, usando el nombre real del servicio PostgreSQL |
| `SECRET_KEY` | Secret | Una clave aleatoria segura de mínimo 32 caracteres |
| `JWT_ALGORITHM` | Variable | `HS256` |
| `ACCESS_TOKEN_MINUTES` | Variable | `60` |
| `AUTH_COOKIE_NAME` | Variable | `access_token` |
| `COOKIE_SECURE` | Variable | `true` |
| `COOKIE_SAMESITE` | Variable | `lax` |
| `CORS_ORIGINS` | Variable | `["https://tu-frontend.com"]` |
| `ENABLE_DELAY_MONITOR` | Variable | `true` si se usa una sola réplica |
| `DB_POOL_SIZE` | Variable | `5` |
| `DB_MAX_OVERFLOW` | Variable | `10` |
| `DB_POOL_TIMEOUT_SECONDS` | Variable | `30` |

Railway proporciona `PORT` automáticamente. No es necesario crearla manualmente.

Configura además:

- Directorio raíz del servicio: `/backend`.
- Pre-deploy command: `alembic upgrade head`.
- Healthcheck path: `/ready`.
- Start command: el `CMD` del Dockerfile, que usa `${PORT:-8000}`.

## Migraciones

Consultar la versión actual:

```powershell
alembic current
```

Aplicar todas las migraciones pendientes:

```powershell
alembic upgrade head
```

Crear una nueva migración después de modificar modelos:

```powershell
alembic revision --autogenerate -m "describe el cambio"
```

Revisar siempre la migración generada antes de aplicarla. Las migraciones existentes son:

| Migración                      | Descripción                              |
| ------------------------------- | ----------------------------------------- |
| `0001_initial_schema`         | Crea el esquema inicial y los roles base. |
| `0002_usuario_ultimo_ingreso` | Agrega el último ingreso del usuario.    |
| `0003_auditable_deletions`    | Agrega eliminación lógica y auditoría. |

## Crear el primer administrador

Después de aplicar las migraciones, ejecuta:

```powershell
python -m app.core.bootstrap
```

El comando solicitará:

- Correo electrónico.
- Contraseña de mínimo 10 caracteres.
- Confirmación de contraseña.
- Nombre completo.

La contraseña se almacena usando bcrypt. No se guarda en `.env`.

Con Docker puedes usar:

```powershell
docker compose run --rm api python -m app.core.bootstrap
```

## Autenticación y roles

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "correo": "admin@example.com",
  "contrasena": "tu-contraseña"
}
```

El token se entrega en una cookie `HttpOnly`. El cuerpo de respuesta no contiene el JWT.

### Sesión actual

```http
GET /api/v1/auth/me
```

### Logout

```http
POST /api/v1/auth/logout
```

### Roles disponibles

| Rol         | Responsabilidad principal              |
| ----------- | -------------------------------------- |
| `ADMIN`   | Administración completa.              |
| `GERENTE` | Operación y consulta de información. |
| `MESERO`  | Registro y seguimiento de pedidos.     |
| `COCINA`  | Gestión de preparación y tickets.    |

Las rutas validan los roles en el backend. Ocultar botones en el frontend no reemplaza esta autorización.

## Módulos y endpoints

Todas las rutas funcionales usan el prefijo `/api/v1`.

### Autenticación

| Método  | Ruta             | Descripción                    |
| -------- | ---------------- | ------------------------------- |
| `POST` | `/auth/login`  | Iniciar sesión.                |
| `POST` | `/auth/logout` | Revocar la sesión actual.      |
| `GET`  | `/auth/me`     | Obtener el usuario autenticado. |

### Usuarios

| Método    | Ruta                          | Descripción        |
| ---------- | ----------------------------- | ------------------- |
| `GET`    | `/usuarios`                 | Listar usuarios.    |
| `POST`   | `/usuarios`                 | Crear usuario.      |
| `PUT`    | `/usuarios/{user_id}`       | Actualizar usuario. |
| `PUT`    | `/usuarios/{user_id}/roles` | Actualizar roles.   |
| `DELETE` | `/usuarios/{user_id}`       | Desactivar usuario. |

### Mesas

| Método    | Ruta                 | Descripción               |
| ---------- | -------------------- | -------------------------- |
| `GET`    | `/mesas`           | Listar mesas.              |
| `POST`   | `/mesas`           | Crear mesa.                |
| `PATCH`  | `/mesas/{mesa_id}` | Cambiar estado permitido.  |
| `DELETE` | `/mesas/{mesa_id}` | Marcar mesa como inactiva. |

### Menú

| Método    | Ruta                | Descripción               |
| ---------- | ------------------- | -------------------------- |
| `GET`    | `/menu`           | Listar platos disponibles. |
| `POST`   | `/menu`           | Crear plato.               |
| `PUT`    | `/menu/{dish_id}` | Actualizar plato.          |
| `DELETE` | `/menu/{dish_id}` | Desactivar plato.          |

### Pedidos

| Método    | Ruta                            | Descripción                                  |
| ---------- | ------------------------------- | --------------------------------------------- |
| `POST`   | `/pedidos`                    | Crear pedido y ocupar mesa.                   |
| `GET`    | `/pedidos/tickets`            | Listar pedidos para cocina.                   |
| `GET`    | `/pedidos/{pedido_id}`        | Consultar pedido.                             |
| `PATCH`  | `/pedidos/{pedido_id}/estado` | Cambiar estado del pedido.                    |
| `DELETE` | `/pedidos/{pedido_id}`        | Retirar pedido mediante eliminación lógica. |

Estados válidos:

```text
PENDIENTE → EN_PREPARACION → LISTO → ENTREGADO
PENDIENTE → CANCELADO
EN_PREPARACION → CANCELADO
LISTO → CANCELADO
```

### Incidencias

| Método    | Ruta                             | Descripción                         |
| ---------- | -------------------------------- | ------------------------------------ |
| `POST`   | `/incidencias`                 | Registrar incidencia.                |
| `GET`    | `/incidencias`                 | Consultar incidencias.               |
| `DELETE` | `/incidencias/{incidencia_id}` | Retirar incidencia de las consultas. |

### Reportes

| Método | Ruta                                                    | Descripción                   |
| ------- | ------------------------------------------------------- | ------------------------------ |
| `GET` | `/reportes/tiempos?desde=YYYY-MM-DD&hasta=YYYY-MM-DD` | Tiempos de pedidos entregados. |
| `GET` | `/reportes/exportar`                                  | Exportar incidencias en CSV.   |

## Pruebas

Instala las dependencias de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
```

Ejecuta todas las pruebas:

```powershell
python -m pytest tests -q
```

Las pruebas utilizan una base SQLite aislada y no modifican la base PostgreSQL configurada en `.env`.

## Health checks

### Liveness

```http
GET /health
```

Indica que el proceso de la API está activo. No comprueba PostgreSQL.

Respuesta esperada:

```json
{"status": "ok"}
```

### Readiness

```http
GET /ready
```

Comprueba que la API puede ejecutar una consulta en PostgreSQL. Devuelve `503` si la base no está disponible.

Respuesta esperada:

```json
{"status": "ready"}
```

## Despliegue

Antes de producción:

1. Configura `APP_ENV=production`.
2. Usa una `SECRET_KEY` segura.
3. Usa HTTPS.
4. Define `COOKIE_SECURE=true`.
5. Configura únicamente los orígenes HTTPS reales en `CORS_ORIGINS`.
6. Configura PostgreSQL con credenciales propias.
7. Haz un backup antes de las migraciones.
8. Ejecuta las migraciones como paso separado:

```powershell
docker compose up -d db
docker compose run --rm api alembic upgrade head
docker compose up -d api
```

9. Comprueba `/health`, `/ready` y los logs.

El archivo `Dockerfile` inicia únicamente Uvicorn. Las migraciones no se ejecutan automáticamente al arrancar la API para evitar carreras cuando existen varias réplicas.
