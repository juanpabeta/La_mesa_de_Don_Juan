import { useMemo, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { ArrowRightLeft, Check, Plus, Search, Users } from 'lucide-react';
import { api, isDemoMode, getApiError } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import { demoOrders, demoTables } from '../../core/data/demo';
import { useAuth } from '../../core/auth/AuthContext';
import type { Order, Table } from '../../core/types';
import { formatCOP } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { StatusBadge } from '../../shared/components/StatusBadge';
import { Modal } from '../../shared/components/Modal';
import { useNotify } from '../../shared/components/ToastProvider';

const zones = ['Todas', 'Salón', 'Terraza', 'Barra'];

export function TablesPage() {
  const queryClient = useQueryClient();
  const notify = useNotify();
  const { user } = useAuth();
  const query = useResourceQuery('tables', resources.tables, demoTables);
  const tables = query.data ?? [];
  const [zone, setZone] = useState('Todas');
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<Table | null>(null);
  const [creating, setCreating] = useState(false);
  const visible = useMemo(() => tables.filter((table) => (zone === 'Todas' || table.zona === zone) && String(table.numero_mesa).includes(search)), [tables, zone, search]);
  const free = tables.filter((table) => table.estado === 'LIBRE' || table.estado === 'Disponible').length;
  const occupied = tables.filter((table) => table.estado === 'OCUPADA' || table.estado === 'Ocupada').length;
  const reserved = tables.filter((table) => table.estado === 'RESERVADA').length;

  const markClean = async (table: Table) => {
    const next: Table['estado'] = table.estado === 'POR_LIMPIAR' ? 'Disponible' : 'POR_LIMPIAR';
    try {
      if (!isDemoMode) await api.patch(`/mesas/${table.id_mesa}`, { estado: next });
      queryClient.setQueryData<Table[]>(['tables'], (current = demoTables) => current.map((item) => item.id_mesa === table.id_mesa ? { ...item, estado: next } : item));
      setSelected({ ...table, estado: next });
      notify(next === 'LIBRE' ? `Mesa ${table.numero_mesa} lista para recibir clientes.` : `Mesa ${table.numero_mesa} marcada para limpieza.`);
    } catch (error) { notify(getApiError(error, 'No se pudo actualizar la mesa.'), 'info'); }
  };

  return <>
    <PageHeader eyebrow="PLANO DEL RESTAURANTE" title="Mesas" description="Un vistazo claro a cada espacio de tu restaurante." actions={<>{user?.roles.includes('Administrador') && <button className="button button-secondary" onClick={() => setCreating(true)}><Plus size={16} /> Agregar mesa</button>}<button className="button button-primary" onClick={() => setSelected(tables.find((table) => table.estado === 'LIBRE') ?? tables[0] ?? null)}><Plus size={17} /> Abrir mesa</button></>} />
    <section className="table-stats">
      <Stat label="Disponibles" count={free} color="green" icon={<Check size={16} />} />
      <Stat label="Ocupadas" count={occupied} color="orange" icon={<Users size={16} />} />
      <Stat label="Reservadas" count={reserved} color="blue" icon={<Search size={16} />} />
      <div className="table-stats-total"><strong>{tables.length.toString().padStart(2, '0')}</strong><span>Mesas activas</span></div>
    </section>
    <section className="panel floor-panel"><div className="floor-toolbar"><div className="filter-tabs zone-tabs">{zones.map((item) => <button key={item} className={`filter-tab ${zone === item ? 'selected' : ''}`} onClick={() => setZone(item)}>{item}</button>)}</div><div className="table-search"><Search size={16} /><input placeholder="Buscar mesa" aria-label="Buscar mesa" value={search} onChange={(event) => setSearch(event.target.value)} /></div></div><div className="floor-section-title"><div><span className="floor-section-mark" />{zone === 'Todas' ? 'Piso principal' : zone}<small>{visible.length} espacios</small></div><span className="floor-hint">Selecciona una mesa para ver sus detalles</span></div><div className="floor-grid">{visible.map((table) => <button key={table.id_mesa} className={`floor-table ${table.estado.toLowerCase()}`} onClick={() => setSelected(table)}><span className="floor-chair chair-top" /><span className="floor-chair chair-right" /><span className="floor-chair chair-bottom" /><span className="floor-chair chair-left" /><span className="floor-table-face"><strong>{table.numero_mesa.toString().padStart(2, '0')}</strong><small>{table.capacidad} puestos</small></span><span className="floor-table-meta"><StatusBadge status={table.estado} />{table.tiempo && <span className="table-elapsed">{table.tiempo}</span>}{table.total && <strong className="floor-total">{formatCOP(table.total)}</strong>}</span></button>)}</div><div className="floor-legend"><span><i className="legend-free" /> Disponible</span><span><i className="legend-busy" /> Ocupada</span><span><i className="legend-reserved" /> Reservada</span><span><i className="legend-clean" /> Por limpiar</span></div></section>
    {selected && <TableModal table={selected} tables={tables} onClose={() => setSelected(null)} onMarkClean={() => void markClean(selected)} onChanged={() => { queryClient.invalidateQueries({ queryKey: ['tables'] }); setSelected(null); }} />}
    {creating && <CreateTableModal onClose={() => setCreating(false)} onCreated={(table) => { queryClient.setQueryData<Table[]>(['tables'], (current = demoTables) => [...current, table]); setCreating(false); notify(`Mesa ${table.numero_mesa} agregada.`); }} />}
  </>;
}

function Stat({ label, count, color, icon }: { label: string; count: number; color: string; icon: React.ReactNode }) {
  return <article className="table-stat"><div className="table-stat-copy"><strong>{count.toString().padStart(2, '0')}</strong><span>{label}</span></div><span className={`stat-status ${color}`}>{icon}</span></article>;
}

function TableModal({ table, tables, onClose, onMarkClean, onChanged }: { table: Table; tables: Table[]; onClose: () => void; onMarkClean: () => void; onChanged: () => void }) {
  const { user } = useAuth();
  const notify = useNotify();
  const queryClient = useQueryClient();
  const orders = queryClient.getQueryData<Order[]>(['orders']) ?? [];
  const order = orders.find((item) => item.id_mesa === table.id_mesa && !['ENTREGADO', 'CANCELADO'].includes(item.estado));
  const [transfer, setTransfer] = useState(false);
  const [destination, setDestination] = useState<number | ''>('');
  const [busy, setBusy] = useState(false);
  const transferOrder = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!order || destination === '') return;
    setBusy(true);
    try {
      if (!isDemoMode) await api.post(`/mesas/${table.id_mesa}/transferir`, { id_mesa_destino: destination });
      const target = tables.find((item) => item.id_mesa === destination);
      queryClient.setQueryData<Order[]>(['orders'], (current = demoOrders) => current.map((item) => item.id_pedido === order.id_pedido ? { ...item, id_mesa: destination, numero_mesa: target?.numero_mesa ?? Number(destination) } : item));
      queryClient.setQueryData<Table[]>(['tables'], (current = demoTables) => current.map((item) => item.id_mesa === table.id_mesa ? { ...item, estado: 'LIBRE' } : item.id_mesa === destination ? { ...item, estado: 'OCUPADA' } : item));
      notify(`Comanda transferida a la mesa ${target?.numero_mesa ?? destination}.`);
      onChanged();
    } catch (error) { notify(getApiError(error, 'No se pudo transferir la mesa.'), 'info'); }
    finally { setBusy(false); }
  };
  return <Modal title={`Mesa ${table.numero_mesa}`} description={`${table.zona} · ${table.capacidad} puestos`} onClose={onClose}><div className="modal-body"><div className="detail-status-row"><StatusBadge status={table.estado} />{table.tiempo && <span>Ocupada hace {table.tiempo}</span>}</div>{order ? <div className="table-active-order"><div className="active-order-top"><div><span>COMANDA ACTIVA</span><strong>#{order.id_pedido}</strong></div><StatusBadge status={order.estado} /></div><div className="active-order-lines">{order.detalles.map((line) => <div key={line.id_detalle}><span>{line.cantidad} × {line.nombre}</span><strong>{formatCOP(line.cantidad * line.precio_unitario)}</strong></div>)}</div><div className="active-order-total"><span>Total actual</span><strong>{formatCOP(order.detalles.reduce((sum, line) => sum + line.cantidad * line.precio_unitario, 0))}</strong></div></div> : <div className="table-no-order"><span>{table.estado === 'LIBRE' ? '🪑' : table.estado === 'RESERVADA' ? '📅' : '🧽'}</span><strong>{table.estado === 'LIBRE' ? 'Lista para recibir clientes' : table.estado === 'RESERVADA' ? 'Mesa reservada' : 'Pendiente de atención'}</strong><p>{table.estado === 'LIBRE' ? 'Puedes abrir una nueva comanda desde aquí.' : 'Consulta el estado de la mesa en el plano del salón.'}</p></div>}{transfer && order && <form className="transfer-form" onSubmit={(event) => void transferOrder(event)}><label htmlFor="transfer-table">Transferir comanda a</label><select id="transfer-table" value={destination} onChange={(event) => setDestination(event.target.value ? Number(event.target.value) : '')} required><option value="">Seleccionar mesa disponible</option>{tables.filter((item) => item.estado === 'LIBRE' && item.id_mesa !== table.id_mesa).map((item) => <option key={item.id_mesa} value={item.id_mesa}>Mesa {item.numero_mesa} · {item.zona}</option>)}</select><button className="button button-primary button-small" disabled={busy}>{busy ? 'Transfiriendo…' : 'Confirmar transferencia'}</button></form>}<div className="modal-actions">{user?.roles.includes('Administrador') && table.estado === 'POR_LIMPIAR' && <button className="button button-secondary" onClick={onMarkClean}><Check size={15} /> Marcar limpia</button>}{order && <button className="button button-secondary" onClick={() => setTransfer((value) => !value)}><ArrowRightLeft size={15} /> Transferir</button>}{!order && table.estado === 'LIBRE' && <button className="button button-primary" onClick={() => { onClose(); window.location.assign('/app/pedidos'); }}>Abrir comanda <Check size={15} /></button>}<button className="button button-ghost" onClick={onClose}>Cerrar</button></div></div></Modal>;
}

function CreateTableModal({ onClose, onCreated }: { onClose: () => void; onCreated: (table: Table) => void }) {
  const [number, setNumber] = useState('');
  const [capacity, setCapacity] = useState('4');
  const [zone, setZone] = useState('Salón');
  const [error, setError] = useState('');
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const newTable: Table = { id_mesa: Date.now(), numero_mesa: Number(number), capacidad: Number(capacity), zona: zone, estado: 'LIBRE', activa: true };
    try {
      if (!isDemoMode) await api.post('/mesas', { numero_mesa: newTable.numero_mesa, capacidad: newTable.capacidad, zona: zone });
      onCreated(newTable);
    } catch (requestError) { setError(getApiError(requestError, 'No se pudo crear la mesa.')); }
  };
  return <Modal title="Agregar mesa" description="Incluye un nuevo espacio en el plano." onClose={onClose}><form onSubmit={(event) => void submit(event)} className="modal-body"><label>Número de mesa<input className="form-input" type="number" min="1" value={number} onChange={(event) => setNumber(event.target.value)} required /></label><label>Capacidad<input className="form-input" type="number" min="1" max="20" value={capacity} onChange={(event) => setCapacity(event.target.value)} required /></label><label>Zona<select className="form-input" value={zone} onChange={(event) => setZone(event.target.value)}><option>Salón</option><option>Terraza</option><option>Barra</option></select></label>{error && <p className="form-error">{error}</p>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Cancelar</button><button className="button button-primary"><Plus size={15} /> Guardar mesa</button></div></form></Modal>;
}
