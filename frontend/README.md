# MesaSync · Frontend de cocina

Frontend inicial en React 18, TypeScript, Vite y Tailwind CSS. Presenta los pedidos activos como tickets térmicos, permite avanzar estados, registrar incidencias para roles autorizados y autentica usando la cookie HttpOnly que establece FastAPI.

## Requisitos

- Node.js 20 o superior.
- Backend ejecutándose en `http://127.0.0.1:8000` para desarrollo local.

## Desarrollo local

Desde esta carpeta, copia `.env.example` a `.env.local` si el backend no está en la dirección predeterminada. Luego instala y arranca:

```powershell
npm install
npm run dev
```

Abre la URL que muestra Vite (por defecto `http://localhost:5173`). El proxy de Vite reenvía `/api/*` al backend y permite que la cookie de sesión funcione en el mismo origen del navegador.

## Contrato que consume

El código usa el contrato de la API real: `GET /api/v1/pedidos/tickets`, `PATCH /api/v1/pedidos/{id}/estado`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout` y `POST /api/v1/incidencias`.

El ticket real entrega `id`, `mesa_id`, `creado_por_id`, `creado_en`, `detalles[].nombre_plato`, `detalles[].notas`, `retrasado`, `numero_mesa`, `minutos_estimados` y `minutos_transcurridos`. No entrega `zona` ni nombres del mesero, así que la interfaz indica “Zona no informada” y el ID de usuario. No se modificó el backend.

## Compilar

```powershell
npm run build
```

Para una API en otro origen, establece `VITE_API_BASE_URL` con la URL completa que incluya `/api/v1`. El servidor de API debe permitir credenciales por CORS y la configuración de cookies debe ser compatible con los dominios de frontend y backend.
