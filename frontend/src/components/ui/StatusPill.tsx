import type { OrderStatus } from '../../types'

const labels: Record<OrderStatus, string> = {
  PENDIENTE: 'Nuevo',
  EN_PREPARACION: 'En cocina',
  LISTO: 'Para entregar',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
}

const styles: Record<OrderStatus, string> = {
  PENDIENTE: 'bg-orange-100 text-orange-800',
  EN_PREPARACION: 'bg-blue-100 text-blue-800',
  LISTO: 'bg-emerald-100 text-emerald-800',
  ENTREGADO: 'bg-stone-100 text-stone-600',
  CANCELADO: 'bg-red-100 text-red-700',
}

export function StatusPill({ status }: { status: OrderStatus }) {
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-bold ${styles[status]}`}>{labels[status]}</span>
}
