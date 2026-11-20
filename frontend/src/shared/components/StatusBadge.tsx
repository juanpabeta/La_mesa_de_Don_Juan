import type { ReactNode } from 'react';

const statusStyles: Record<string, string> = {
  LIBRE: 'status-green', OCUPADA: 'status-orange', RESERVADA: 'status-violet', POR_LIMPIAR: 'status-gray',
  PENDIENTE: 'status-violet', EN_PREPARACION: 'status-orange', LISTO: 'status-green', ENTREGADO: 'status-gray', CANCELADO: 'status-gray',
  ABIERTA: 'status-violet', EN_REVISION: 'status-orange', RESUELTA: 'status-green',
  ALTA: 'status-red', MEDIA: 'status-orange', BAJA: 'status-gray',
};

const statusLabels: Record<string, string> = {
  LIBRE: 'Disponible', OCUPADA: 'Ocupada', RESERVADA: 'Reservada', POR_LIMPIAR: 'Por limpiar',
  PENDIENTE: 'Pendiente', EN_PREPARACION: 'En preparación', LISTO: 'Listo', ENTREGADO: 'Entregado', CANCELADO: 'Cancelado',
  ABIERTA: 'Abierta', EN_REVISION: 'En revisión', RESUELTA: 'Resuelta', ALTA: 'Alta', MEDIA: 'Media', BAJA: 'Baja',
};

export function StatusBadge({ status, children }: { status: string; children?: ReactNode }) {
  return <span className={`status-badge ${statusStyles[status] ?? 'status-gray'}`}><span className="status-dot" />{children ?? statusLabels[status] ?? status}</span>;
}
