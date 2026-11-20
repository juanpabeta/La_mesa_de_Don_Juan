import { useEffect, useRef, useState } from 'react';

import { BellRing, Check, ChefHat, Clock3, MoreHorizontal, Printer, Volume2 } from 'lucide-react';
import { isDemoMode, getApiError } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';

import type { Order, OrderStatus } from '../../core/types';
import { formatTime } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { useAudioAlert } from '../../core/hooks/useAudioAlert';
import { useNotify } from '../../shared/components/ToastProvider';
import { StatusBadge } from '../../shared/components/StatusBadge';

const columns: Array<{ title: string; status: OrderStatus; hint: string }> = [
  { title: 'Nueva comanda', status: 'PENDIENTE', hint: 'En espera' },
  { title: 'En preparación', status: 'EN_PREPARACION', hint: 'En estación' },
  { title: 'Listo para servir', status: 'LISTO', hint: 'Recoger pedido' },
];

export function KitchenPage() {
  const notify = useNotify();
  const playAlert = useAudioAlert();
  const [now, setNow] = useState(() => Date.now());
  const [printingOrderId, setPrintingOrderId] = useState<number | null>(null);
  const [printFailureOrderId, setPrintFailureOrderId] = useState<number | null>(null);
  const busyOrders = useRef(new Set<number>());
  const query = useResourceQuery('orders', resources.orders);
  const orders = query.data ?? [];
  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 1_000);
    return () => window.clearInterval(interval);
  }, []);
  const active = orders.filter((order) => ['PENDIENTE', 'EN_PREPARACION', 'LISTO'].includes(order.estado));

  const update = async (order: Order, status: OrderStatus) => {
    if (busyOrders.current.has(order.id_pedido)) return;
    busyOrders.current.add(order.id_pedido);
    try {
      if (!isDemoMode) await resources.updateOrder(order.id_pedido, { estado: status });
      await query.refetch();
      if (status === 'LISTO') playAlert();
      notify(`Pedido #${order.id_pedido}: ${status === 'LISTO' ? 'listo para servir' : 'estado actualizado'}.`);
    } catch (error) { notify(getApiError(error, 'No se pudo actualizar el pedido.'), 'info'); }
    finally { busyOrders.current.delete(order.id_pedido); }
  };

  const reprint = async (order: Order) => {
    if (busyOrders.current.has(order.id_pedido)) return;
    busyOrders.current.add(order.id_pedido);
    setPrintingOrderId(order.id_pedido);
    setPrintFailureOrderId(null);
    try {
      if (!isDemoMode) await resources.reprintOrder(order.id_pedido);
      notify(`Ticket #${order.id_pedido} enviado a impresión.`);
    } catch (error) {
      setPrintFailureOrderId(order.id_pedido);
      window.setTimeout(() => setPrintFailureOrderId(null), 2600);
      notify(getApiError(error, 'No se pudo reimprimir el ticket.'), 'info');
    } finally {
      setPrintingOrderId(null);
      busyOrders.current.delete(order.id_pedido);
    }
  };

  return <>
    <PageHeader eyebrow="PANTALLA DE PRODUCCIÓN" title="Cocina" description="El equipo de salón y cocina, siempre en la misma página." actions={<div className="kds-clock tabular-nums"><span className="live-dot" />{new Date(now).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}<button className="button button-secondary button-small" onClick={playAlert}><Volume2 size={15} /> Probar sonido</button></div>} />
    <section className="kds-summary">
      <div className="kds-summary-icon"><ChefHat size={20} /></div>
      <div className="kds-summary-copy"><strong>{active.length}</strong><span>Pedidos activos</span><small>La estación está al día con las comandas del salón.</small></div>
      <div className="kds-summary-right"><span className="kds-legend"><i className="kds-legend-dot green" /> Dentro de tiempo</span><span className="kds-legend"><i className="kds-legend-dot orange" /> Revisar tiempo</span><button className="quiet-icon-button" title="Actualizar" onClick={() => void query.refetch()}><MoreHorizontal size={18} /></button></div>
    </section>
    <section className="kds-board">{columns.map((column) => {
      const columnOrders = active.filter((order) => order.estado === column.status).sort((a, b) => Number(b.es_retrasado) - Number(a.es_retrasado) || new Date(a.fecha_hora_creacion).getTime() - new Date(b.fecha_hora_creacion).getTime());
      return <div className="kds-column" key={column.status}><div className="kds-column-head"><div className={`kds-column-icon ${column.status.toLowerCase()}`}>{column.status === 'PENDIENTE' ? <BellRing size={17} /> : column.status === 'EN_PREPARACION' ? <ChefHat size={17} /> : <Check size={17} />}</div><div><h2>{column.title}</h2><span>{column.hint}</span></div><span className="kds-count">{columnOrders.length}</span></div><div className="kds-tickets">{columnOrders.map((order) => <KitchenTicket key={order.id_pedido} order={order} elapsed={Math.max(0, Math.floor((now - new Date(order.fecha_hora_creacion).getTime()) / 60_000))} onAdvance={() => void update(order, nextKitchenStatus(order.estado))} onReprint={() => void reprint(order)} printing={printingOrderId === order.id_pedido} printFailed={printFailureOrderId === order.id_pedido} />)}{columnOrders.length === 0 && <div className="kds-empty"><span className="kds-empty-icon">✨</span><strong>Todo tranquilo</strong><small>Las nuevas comandas aparecerán aquí.</small></div>}</div></div>;
    })}</section>
    <div className="kds-footer"><span className="tabular-nums">Actualizado a las {new Date(now).toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span><span>Las comandas se sincronizan automáticamente <span className="live-dot" /></span></div>
  </>;
}

function KitchenTicket({ order, elapsed, onAdvance, onReprint, printing, printFailed }: { order: Order; elapsed: number; onAdvance: () => void; onReprint: () => void; printing: boolean; printFailed: boolean }) {
  const late = order.es_retrasado || elapsed > 20;
  return <article className={`kds-ticket ${late ? 'ticket-late' : ''}`}><div className="ticket-top"><div className="ticket-number">#{order.id_pedido}</div><div className={`ticket-timer tabular-nums ${late ? 'late' : ''}`}><Clock3 size={13} /> {elapsed} min</div></div><div className="ticket-meta"><span className="ticket-table">Mesa {order.numero_mesa}</span><span>·</span><span>{formatTime(order.fecha_hora_creacion)}</span><span>·</span><span>{(order.mesero ?? 'Equipo').split(' ')[0]}</span></div><div className="ticket-divider" /><div className="ticket-lines">{order.detalles.map((line) => <div className="ticket-line" key={line.id_detalle}><span className="ticket-qty">{line.cantidad}</span><div><strong>{line.nombre}</strong>{line.observaciones && <small>{line.observaciones}</small>}</div></div>)}</div><button className={`ticket-action ${order.estado === 'LISTO' ? 'ticket-action-ready' : ''}`} onClick={onAdvance}>{order.estado === 'PENDIENTE' ? <>Comenzar preparación <ChefHat size={15} /></> : order.estado === 'EN_PREPARACION' ? <>Marcar pedido listo <Check size={15} /></> : <>Marcar entregado <Check size={15} /></>}</button><button type="button" className={`ticket-reprint ${printing ? 'is-printing' : ''} ${printFailed ? 'print-failed' : ''}`} onClick={onReprint} disabled={printing} aria-live="polite">{printing ? <><Printer size={15} className="printer-spin" /> Conectando con la impresora…</> : printFailed ? <><Printer size={15} /> Impresora no disponible · Reintentar</> : <><Printer size={15} /> Reimprimir ticket</>}</button>{late && <div className="ticket-late-note">Revisar tiempo de preparación</div>}</article>;
}

function nextKitchenStatus(status: OrderStatus): OrderStatus { if (status === 'PENDIENTE') return 'EN_PREPARACION'; if (status === 'EN_PREPARACION') return 'LISTO'; return 'ENTREGADO'; }
