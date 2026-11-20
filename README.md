# KitchenFlow

KitchenFlow es un sistema para restaurantes, diseñado para coordinar mesas, pedidos, cocina, incidencias, empleados y reportes en tiempo real.

## Tecnologías

- Frontend: React 18, TypeScript, Vite y Tailwind CSS
- Backend: FastAPI, SQLAlchemy Async, Pydantic y PostgreSQL
- Tiempo real: WebSockets
- Autenticación: JWT almacenado en cookie `HttpOnly`
- Pruebas: Pytest, Cypress y Vitest
- Contenedores: Docker y Docker Compose
- CI: GitHub Actions

## Funcionalidades

- Autenticación por roles y rutas protegidas
- Administración de empleados con desactivación lógica
- Gestión de mesas, zonas y transferencia de comandas
- Catálogo de platos y estado agotado
- Flujo de pedidos: pendiente, preparación, listo y entregado
- Pantalla KDS y sincronización mediante WebSockets
- Incidencias con trazabilidad y auditoría
- Reportes por periodo y exportación CSV/JSON
- Importación y persistencia en PostgreSQL

## Arquitectura

```text
proyecto-restaurantes/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   └── modules/
│   ├── alembic/
│   ├── tests/
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   └── cypress/
└── .github/workflows/
```

## Requisitos

- Python 3.14 o compatible
- Node.js 20 o superior
- PostgreSQL 18
- Docker Desktop opcional

## Configuración local

### 1. Backend

```powershell
cd backend
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Completa `.env` con una URL PostgreSQL válida, una clave JWT segura y la configuración de cookie.

```env
DATABASE_URL=postgresql+asyncpg://postgres:tu-password@127.0.0.1:5433/kitchen_flow
JWT_SECRET_KEY=una-clave-segura-de-al-menos-32-caracteres
COOKIE_SECURE=false
```

Inicia PostgreSQL:

```powershell
docker compose up -d db
```

Ejecuta las migraciones y el servidor:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Documentación interactiva:

- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 2. Frontend

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Aplicación: http://127.0.0.1:5173

## Ejecutar con Docker Compose

Desde `backend/`:

```powershell
docker compose up --build
```

El backend estará disponible en http://127.0.0.1:8000 y PostgreSQL en el puerto 5433.

## Pruebas

### Backend

```powershell
cd backend
python -m pytest -q
```

La suite cubre autenticación, RBAC, usuarios, mesas, menú, pedidos, cocina, incidencias, reportes y WebSockets.

### Frontend unitario

```powershell
cd frontend
npm test
npm run build
```

### Cypress E2E

Con backend y frontend activos:

```powershell
cd frontend
npm run cy:open
```

O ejecución encabezada:

```powershell
npm run cy:run
```

## GitHub Actions

- `backend-ci.yml`: instala el backend, valida pip y ejecuta Pytest.
- `frontend-ci.yml`: instala dependencias, ejecuta Vitest y compila Vite.
- Ambos workflows se ejecutan en pull requests y pushes a `main`.

## Seguridad

- Nunca subas `.env`, claves JWT ni credenciales de PostgreSQL.
- Usa secretos de GitHub Actions para valores sensibles.
- Mantén `COOKIE_SECURE=true` en HTTPS.
- Cambia las claves y contraseñas antes de publicar el proyecto.

## Variables principales

### Backend

| Variable                        | Descripción                       |
| ------------------------------- | ---------------------------------- |
| `DATABASE_URL`                | Conexión asyncpg a PostgreSQL     |
| `JWT_SECRET_KEY`              | Clave de firma JWT                 |
| `COOKIE_SECURE`               | Cookie segura únicamente en HTTPS |
| `JWT_ALGORITHM`               | Algoritmo JWT, normalmente HS256   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración de la sesión            |

### Frontend

| Variable         | Descripción        |
| ---------------- | ------------------- |
| `VITE_API_URL` | URL base de FastAPI |
| `VITE_WS_URL`  | URL del WebSocket   |

## API principal

- `/api/v1/auth`
- `/api/v1/usuarios`
- `/api/v1/mesas`
- `/api/v1/menu`
- `/api/v1/pedidos`
- `/api/v1/incidencias`
- `/api/v1/reportes`
- `/api/v1/ws`
