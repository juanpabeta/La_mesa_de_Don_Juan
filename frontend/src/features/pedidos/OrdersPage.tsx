import { useMemo, useRef, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRight, Check, ChevronDown, CircleDollarSign, Clock3, Plus, Search, Users, X } from 'lucide-react';
import { api, isDemoMode, getApiError } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import { demoMenu, demoOrders, demoTables } from '../../core/data/demo';
import type { MenuItem, Order, OrderLine, OrderStatus } from '../../core/types';
import { formatCOP, formatTime, relativeMinutes } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { StatusBadge } from '../../shared/components/StatusBadge';
import { Modal } from '../../shared/components/Modal';
import { useNotify } from '../../shared/components/ToastProvider';

const filters: Array<{ label: string; value: 'TODOS' | OrderStatus }> = [
  { label: 'Todos', value: 'TODOS' }, { label: 'Pendientes', value: 'PENDIENTE' },
  { label: 'En preparación', value: 'EN_PREPARACION' }, { label: 'Listos', value: 'LISTO' }, { label: 'Entregados', value: 'ENTREGADO' },
];

export function OrdersPage() {
  const queryClient = useQueryClient();
  const notify = useNotify();
  const ordersQuery = useResourceQuery('orders', resources.orders, demoOrders);
  const orders = ordersQuery.data ?? [];
  const [filter, setFilter] = useState<(typeof filters)[number]['value']>('TODOS');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Order | null>(null);
  const [newOrderOpen, setNewOrderOpen] = useState(false);
  const visible = useMemo(() => orders.filter((order) => (filter === 'TODOS' || order.estado === filter) && (`${order.id_pedido} ${order.numero_mesa} ${order.mesero}`.toLowerCase().includes(search.toLowerCase()))), [orders, filter, search]);

  const changeStatus = async (order: Order, status: OrderStatus) => {
    try {
      if (!isDemoMode) await resources.updateOrder(order.id_pedido, { estado: status });
      queryClient.setQueryData<Order[]>(['orders'], (current = demoOrders) => current.map((item) => item.id_pedido === order.id_pedido ? { ...item, estado: status } : item));
      setSelected((current) => current?.id_pedido === order.id_pedido ? { ...current, estado: status } : current);
      notify(`Pedido #${order.id_pedido} actualizado.`);
    } catch (error) { notify(getApiError(error, 'No se pudo actualizar el pedido.'), 'info'); }
  };

  return <>
    <PageHeader eyebrow="OPERACIÓN · SALÓN" title="Pedidos" description="Toma, sigue y entrega cada comanda de tu restaurante." actions={<button className="button button-primary" onClick={() => setNewOrderOpen(true)}><Plus size={17} /> Nueva comanda</button>} />
    <section className="orders-overview"><div className="orders-count"><span className="orders-count-mark"><CircleDollarSign size={18} /></span><div><strong>{orders.filter((order) => order.estado !== 'ENTREGADO' && order.estado !== 'CANCELADO').length}</strong><span>pedidos por atender</span></div></div><div className="orders-count-divider" /><div className="orders-count"><span className="orders-count-mark warm"><Clock3 size={18} /></span><div><strong>{orders.filter((order) => order.es_retrasado).length}</strong><span>requieren atención</span></div></div><div className="orders-snapshot"><span>Ventas activas hoy</span><strong>{formatCOP(orders.filter((order) => order.estado !== 'CANCELADO').reduce((sum, order) => sum + orderTotal(order), 0))}</strong></div></section>
    <section className="panel orders-panel"><div className="orders-toolbar"><div className="filter-tabs">{filters.map((item) => <button key={item.value} onClick={() => setFilter(item.value)} className={`filter-tab ${filter === item.value ? 'selected' : ''}`}>{item.label}<span>{item.value === 'TODOS' ? orders.length : orders.filter((order) => order.estado === item.value).length}</span></button>)}</div><div className="table-search"><Search size={16} /><input aria-label="Buscar pedidos" placeholder="Buscar pedido o mesa" value={search} onChange={(event) => setSearch(event.target.value)} /></div></div><div className="order-table-wrap"><table className="data-table order-table"><thead><tr><th>COMANDA</th><th>MESA</th><th>PRODUCTOS</th><th>MESERO</th><th>HORA</th><th>ESTADO</th><th>TOTAL</th><th /></tr></thead><tbody>{visible.map((order) => <tr key={order.id_pedido} onClick={() => setSelected(order)} className="clickable-row"><td><strong className="order-id">#{order.id_pedido}</strong></td><td><span className="table-chip">{order.numero_mesa}</span></td><td><span className="order-products">{order.detalles.reduce((sum, line) => sum + line.cantidad, 0)} productos</span><small className="cell-muted">{order.detalles.map((line) => line.nombre).join(', ')}</small></td><td>{order.mesero}</td><td><span>{formatTime(order.fecha_hora_creacion)}</span><small className={`cell-muted ${order.es_retrasado ? 'text-orange' : ''}`}>{relativeMinutes(order.fecha_hora_creacion)}</small></td><td><StatusBadge status={order.estado} /></td><td className="money-cell">{formatCOP(orderTotal(order))}</td><td><button className="row-action" aria-label={`Abrir pedido ${order.id_pedido}`}><ArrowRight size={16} /></button></td></tr>)}</tbody></table>{visible.length === 0 && <div className="empty-state"><span className="empty-emoji">🔎</span><strong>No encontramos pedidos</strong><p>Prueba con otro filtro o término de búsqueda.</p></div>}</div><div className="table-footnote">Mostrando {visible.length} de {orders.length} pedidos</div></section>
    {selected && <OrderDetails order={selected} onClose={() => setSelected(null)} onChangeStatus={(status) => void changeStatus(selected, status)} />}
    {newOrderOpen && <NewOrderModal onClose={() => setNewOrderOpen(false)} onCreated={(order) => { queryClient.setQueryData<Order[]>(['orders'], (current = demoOrders) => [order, ...current]); setNewOrderOpen(false); notify(`Comanda #${order.id_pedido} creada.`); }} />}
  </>;
}

function OrderDetails({ order, onClose, onChangeStatus }: { order: Order; onClose: () => void; onChangeStatus: (status: OrderStatus) => void }) {
  const [tip, setTip] = useState(order.propina ?? 0);
  const [splitCount, setSplitCount] = useState(2);
  const [pin, setPin] = useState('');
  const [cancelError, setCancelError] = useState('');
  const [showCancel, setShowCancel] = useState(false);
  const notify = useNotify();
  const queryClient = useQueryClient();
  const subtotal = orderTotal(order);
  const updateTip = async () => {
    try {
      if (!isDemoMode) await resources.updateTip(order.id_pedido, tip);
      queryClient.setQueryData<Order[]>(['orders'], (current = demoOrders) => current.map((item) => item.id_pedido === order.id_pedido ? { ...item, propina: tip } : item));
      notify(`Propina de ${formatCOP(tip)} agregada.`);
    } catch (error) { notify(getApiError(error, 'No se pudo guardar la propina.'), 'info'); }
  };
  const cancelOrder = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setCancelError('');
    if (!pin.trim()) { setCancelError('Ingresa la causa de la anulación.'); return; }
    try {
      if (!isDemoMode) await resources.cancelOrder(order.id_pedido, pin.trim());
      queryClient.setQueryData<Order[]>(['orders'], (current = demoOrders) => current.map((item) => item.id_pedido === order.id_pedido ? { ...item, estado: 'CANCELADO' } : item));
      notify(`Pedido #${order.id_pedido} anulado.`);
      onClose();
    } catch (error) { setCancelError(getApiError(error, 'No se pudo anular el pedido.')); }
  };
  return <Modal title={`Comanda #${order.id_pedido}`} description={`Mesa ${order.numero_mesa} · ${order.mesero} · ${formatTime(order.fecha_hora_creacion)}`} onClose={onClose}>
    <div className="modal-body"><div className="detail-status-row"><StatusBadge status={order.estado} /><span>Hace {relativeMinutes(order.fecha_hora_creacion)}</span></div><div className="detail-lines">{order.detalles.map((line) => <div className="detail-line" key={line.id_detalle}><span className="detail-quantity">{line.cantidad}×</span><div><strong>{line.nombre}</strong>{line.observaciones && <small>{line.observaciones}</small>}</div><b>{formatCOP(line.cantidad * line.precio_unitario)}</b></div>)}</div><div className="bill-summary"><span>Subtotal</span><strong>{formatCOP(subtotal)}</strong></div><div className="tip-entry"><label htmlFor="tip">Propina voluntaria</label><div><input id="tip" type="number" min="0" value={tip} onChange={(event) => setTip(Number(event.target.value))} /><button className="button button-secondary button-small" onClick={updateTip}>Guardar</button></div></div><div className="split-preview"><div><Users size={16} /><span>Dividir cuenta</span></div><div className="split-control"><button onClick={() => setSplitCount((count) => Math.max(2, count - 1))} aria-label="Menos personas">−</button><span>{splitCount} personas</span><button onClick={() => setSplitCount((count) => Math.min(12, count + 1))} aria-label="Más personas">+</button></div><strong>{formatCOP(Math.ceil((subtotal + tip) / splitCount))}<small> por persona</small></strong></div>{showCancel && <form className="cancel-form" onSubmit={(event) => void cancelOrder(event)}><label htmlFor="pin">PIN de autorización</label><div className="cancel-fields"><input id="pin" inputMode="numeric" type="password" maxLength={8} placeholder="Ingresa tu PIN" value={pin} onChange={(event) => setPin(event.target.value)} required /><button className="button button-danger button-small">Confirmar anulación</button></div><small>Esta acción queda registrada en la auditoría.</small>{cancelError && <p className="form-error">{cancelError}</p>}</form>}<div className="modal-actions"><button className="button button-ghost" onClick={() => setShowCancel((value) => !value)}><X size={15} /> Anular pedido</button>{nextStatus(order.estado) && <button className="button button-primary" onClick={() => { onChangeStatus(nextStatus(order.estado) as OrderStatus); onClose(); }}>{statusAction(order.estado)} <ArrowRight size={15} /></button>}</div></div>
  </Modal>;
}

function NewOrderModal({ onClose, onCreated }: { onClose: () => void; onCreated: (order: Order) => void }) {
  const tables = useResourceQuery('tables', resources.tables).data ?? [];
  const menu = useResourceQuery('menu', resources.menu).data ?? [];
  const [tableId, setTableId] = useState(tables[0]?.id_mesa ?? 1);
  const [counts, setCounts] = useState<Record<number, number>>({});
  const [notes, setNotes] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const submitLock = useRef(false);
  const subtotal = menu.reduce((sum, dish) => sum + dish.precio * (counts[dish.id_plato] ?? 0), 0);
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitLock.current) return;
    submitLock.current = true;
    const lines = menu.filter((dish) => (counts[dish.id_plato] ?? 0) > 0);
    if (!lines.length) { setError('Agrega al menos un producto a la comanda.'); return; }
    setBusy(true); setError('');
    const detalles: OrderLine[] = lines.map((dish, index) => ({ id_detalle: Date.now() + index, id_plato: dish.id_plato, nombre: dish.nombre, cantidad: counts[dish.id_plato] ?? 1, precio_unitario: dish.precio, ...(notes ? { observaciones: notes } : {}) }));
    try {
      let created: Order;
      if (isDemoMode) {
        created = { id_pedido: Math.max(0, ...demoOrders.map((order) => order.id_pedido)) + Date.now() % 100, id_mesa: tableId, numero_mesa: tables.find((table) => table.id_mesa === tableId)?.numero_mesa ?? tableId, mesero: 'Mariana Gómez', estado: 'PENDIENTE', fecha_hora_creacion: new Date().toISOString(), es_retrasado: false, detalles };
      } else {
        const data = await resources.createOrder({ id_mesa: tableId, detalles: detalles.map(({ id_plato, cantidad, observaciones }) => ({ id_plato, cantidad, ...(observaciones ? { observaciones } : {}) })) });
        created = { ...data, numero_mesa: tables.find((table) => table.id_mesa === tableId)?.numero_mesa ?? tableId, mesero: 'Equipo', detalles };
      }
      onCreated(created);
    } catch (requestError) { setError(getApiError(requestError, 'No se pudo crear la comanda.')); }
    finally { submitLock.current = false; setBusy(false); }
  };
  return <Modal title="Nueva comanda" description="Agrega los productos y asígnalos a una mesa." onClose={onClose} size="wide"><form onSubmit={(event) => void submit(event)}><div className="modal-body new-order-body"><label htmlFor="table-select">Mesa</label><div className="select-with-icon"><select id="table-select" value={tableId} onChange={(event) => setTableId(Number(event.target.value))}>{tables.filter((table) => table.activa && table.estado !== 'POR_LIMPIAR').map((table) => <option key={table.id_mesa} value={table.id_mesa}>Mesa {table.numero_mesa} · {table.zona}</option>)}</select><ChevronDown size={16} /></div><div className="new-order-section-label">PRODUCTOS DEL MENÚ</div><div className="new-order-items">{menu.filter((dish) => dish.activo && !dish.agotado).map((dish) => <div className="new-order-item" key={dish.id_plato}><span className="dish-emoji">{dish.emoji ?? '🍽️'}</span><div><strong>{dish.nombre}</strong><small>{formatCOP(dish.precio)}</small></div><div className="quantity-stepper"><button type="button" onClick={() => setCounts((current) => ({ ...current, [dish.id_plato]: Math.max(0, (current[dish.id_plato] ?? 0) - 1) }))}>−</button><span>{counts[dish.id_plato] ?? 0}</span><button type="button" onClick={() => setCounts((current) => ({ ...current, [dish.id_plato]: (current[dish.id_plato] ?? 0) + 1 }))}>+</button></div></div>)}</div><label htmlFor="order-notes">Nota para cocina <span className="optional-label">OPCIONAL</span></label><textarea id="order-notes" className="form-textarea" placeholder="Ej. sin cebolla, término medio…" value={notes} onChange={(event) => setNotes(event.target.value)} /><div className="new-order-total"><span>Total de la comanda</span><strong>{formatCOP(subtotal)}</strong></div>{error && <p className="form-error">{error}</p>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Cancelar</button><button className="button button-primary" disabled={busy || subtotal === 0}>{busy ? 'Creando…' : 'Enviar a cocina'} <ArrowRight size={15} /></button></div></div></form></Modal>;
}

function orderTotal(order: Order): number { return order.detalles.reduce((sum, line) => sum + line.cantidad * line.precio_unitario, 0); }
function nextStatus(status: OrderStatus): OrderStatus | null { if (status === 'PENDIENTE') return 'EN_PREPARACION'; if (status === 'EN_PREPARACION') return 'LISTO'; if (status === 'LISTO') return 'ENTREGADO'; return null; }
function statusAction(status: OrderStatus): string { if (status === 'PENDIENTE') return 'Enviar a preparación'; if (status === 'EN_PREPARACION') return 'Marcar como listo'; return 'Marcar entregado'; }
