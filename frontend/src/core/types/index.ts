export type AppRole = 'Administrador' | 'Mesero' | 'Cocina' | 'Cocinero' | 'Cajero';

export interface User {
  id_usuario: number;
  nombres: string;
  apellidos: string;
  correo: string;
  estado: boolean;
  roles: AppRole[];
}

export interface Table {
  id_mesa: number;
  numero_mesa: number;
  zona: string;
  capacidad: number;
  estado: 'LIBRE' | 'OCUPADA' | 'RESERVADA' | 'POR_LIMPIAR' | 'Disponible' | 'Ocupada' | 'Reservada' | 'Por limpiar' | string;
  activa: boolean;
  tiempo?: string;
  total?: number;
}

export interface MenuItem {
  id_plato: number;
  nombre: string;
  categoria: string;
  precio: number;
  tiempo_estimado_min: number;
  activo: boolean;
  agotado?: boolean;
  descripcion?: string;
  emoji?: string;
}

export type OrderStatus = 'PENDIENTE' | 'EN_PREPARACION' | 'LISTO' | 'ENTREGADO' | 'CANCELADO';

export interface OrderLine {
  id_detalle: number;
  id_plato: number;
  nombre: string;
  cantidad: number;
  precio_unitario: number;
  observaciones?: string;
}

export interface Order {
  id_pedido: number;
  id_mesa: number;
  numero_mesa: number;
  id_usuario?: number;
  mesero?: string;
  estado: OrderStatus;
  fecha_hora_creacion: string;
  fecha_hora_entrega?: string | null;
  es_retrasado: boolean;
  detalles: OrderLine[];
  propina?: number;
}

export interface Incident {
  id_incidencia: number;
  id_pedido: number;
  id_usuario: number;
  tipo_error: string;
  descripcion: string;
  creado_por?: string;
  fecha_registro: string;
  fecha_hora?: string;
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA';
  estado: 'ABIERTA' | 'EN_REVISION' | 'RESUELTA' | 'ELIMINADA';
  tipo?: string;
}

export interface TimingReport {
  pedidos_entregados: number;
  promedio_segundos: number;
  pedidos_retrasados: number;
}

export interface ApiEnvelope<T> {
  data: T;
}

export interface RealtimeEvent {
  type: 'order.created' | 'order.updated' | 'menu.updated' | 'table.updated' | 'incident.created' | 'incident.updated';
  payload: Record<string, unknown>;
  occurred_at?: string;
}

export type QueryKeyName = 'tables' | 'menu' | 'orders' | 'incidents' | 'users';
