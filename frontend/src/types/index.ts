export type OrderStatus =
  | 'PENDIENTE'
  | 'EN_PREPARACION'
  | 'LISTO'
  | 'ENTREGADO'
  | 'CANCELADO'

export type TicketFilter = Extract<OrderStatus, 'PENDIENTE' | 'EN_PREPARACION' | 'LISTO'>

export interface OrderDetail {
  id: number
  plato_id: number
  nombre_plato: string
  cantidad: number
  precio_unitario: string | number
  tiempo_preparacion_minutos: number
  notas: string | null
}

export interface KitchenTicket {
  id: number
  mesa_id: number
  creado_por_id: number
  estado: OrderStatus
  creado_en: string
  inicio_preparacion_en: string | null
  listo_en: string | null
  entregado_en: string | null
  cancelado_en: string | null
  retrasado: boolean
  retraso_marcado_en: string | null
  notas: string | null
  detalles: OrderDetail[]
  numero_mesa: number
  minutos_estimados: number
  minutos_transcurridos: number
}

export interface UserSession {
  id: number
  nombre_completo: string
  email: string
  roles: string[]
}

export interface LoginPayload {
  correo: string
  contrasena: string
}

export interface IncidentPayload {
  pedido_id: number | null
  tipo: 'PERDIDA' | 'ENTREGA_ERRONEA' | 'DEMORA' | 'CANCELACION' | 'MESA_EQUIVOCADA' | 'OTRA'
  descripcion: string
}
