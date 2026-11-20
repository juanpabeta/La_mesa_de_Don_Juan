import { ArrowDownRight, ArrowRight, ArrowUpRight, Clock3, MoreHorizontal, Plus, ShoppingBag, Timer, TrendingUp, Users, ClipboardList } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useResourceQuery } from '../../core/api/query';
import { resources } from '../../core/api/resources';
import { demoIncidents, demoMenu, demoOrders, demoTables } from '../../core/data/demo';
import { useAuth } from '../../core/auth/AuthContext';
import type { Order } from '../../core/types';
import { formatCOP, relativeMinutes, todayLabel } from '../../shared/utils/format';
import { StatusBadge } from '../../shared/components/StatusBadge';
import { PageHeader } from '../../shared/components/PageHeader';

export function DashboardPage() {
  const { user } = useAuth();
  const orders = useResourceQuery('orders', resources.orders).data ?? [];
  const tables = useResourceQuery('tables', resources.tables).data ?? [];
  const menu = useResourceQuery('menu', resources.menu).data ?? [];
  const incidents = useResourceQuery('incidents', resources.incidents).data ?? [];
  const activeOrders = orders.filter((order) => ['PENDIENTE', 'EN_PREPARACION', 'LISTO'].includes(order.estado));
  const today = dateKey(new Date());
  const yesterday = dateKey(new Date(Date.now() - 86_400_000));
  const todayOrders = orders.filter((order) => dateKey(new Date(order.fecha_hora_creacion)) === today && order.estado !== 'CANCELADO');
  const yesterdayOrders = orders.filter((order) => dateKey(new Date(order.fecha_hora_creacion)) === yesterday && order.estado !== 'CANCELADO');
  const grossSales = todayOrders.reduce((sum, order) => sum + orderTotal(order), 0);
  const yesterdaySales = yesterdayOrders.reduce((sum, order) => sum + orderTotal(order), 0);
  const salesChange = yesterdaySales ? `${((grossSales - yesterdaySales) / yesterdaySales * 100).toFixed(1).replace('.', ',')}%` : 'Sin comparación';
  const occupied = tables.filter((table) => table.estado === 'OCUPADA').length;
  const delayed = activeOrders.filter((order) => order.es_retrasado).length;
  const greeting = getGreeting();

  return <>
    <PageHeader eyebrow={todayLabel()} title={`${greeting}, ${user?.nombres ?? 'equipo'}`} description="Consulta el estado de la operación y actúa sobre lo importante." actions={<Link to="/app/pedidos" className="button button-primary"><Plus size={17} /> Nueva comanda</Link>} />
    <section className="metric-grid">
      <Metric icon={ShoppingBag} label="Ventas de hoy" value={formatCOP(grossSales)} change={salesChange} note="vs. ayer" positive={Boolean(yesterdaySales)} />
      <Metric icon={ClipboardList} label="Pedidos activos" value={String(activeOrders.length).padStart(2, '0')} change="4 en cocina" note="ahora mismo" neutral />
      <Metric icon={Users} label="Mesas ocupadas" value={`${occupied} / ${tables.length}`} change="68% ocupación" note="del salón" positive />
      <Metric icon={Timer} label="Tiempo promedio" value="18 min" change="2 min" note="vs. la semana pasada" positive />
    </section>
    <section className="dashboard-grid">
      <article className="panel sales-panel"><div className="panel-heading"><div><div className="panel-kicker">RENDIMIENTO</div><h2>Ventas del día</h2></div><span className="data-source-label">Datos de pedidos</span></div><div className="sales-summary"><strong>{formatCOP(grossSales)}</strong><span className="trend-pill">{yesterdaySales ? <><ArrowUpRight size={14} /> {salesChange}</> : 'Sin ventas ayer'}</span><span>frente a ayer</span></div><SalesChart orders={todayOrders} /><div className="chart-legend"><span><i className="legend-today" /> Pedidos de hoy</span><span className="chart-comparison">{todayOrders.length} pedidos contabilizados</span></div></article>
      <article className="panel kitchen-panel"><div className="panel-heading"><div><div className="panel-kicker">EN TIEMPO REAL <span className="live-dot" /></div><h2>En cocina</h2></div><Link to="/app/cocina" className="quiet-icon-button" aria-label="Ver cocina"><ArrowRight size={17} /></Link></div><div className="kitchen-stats"><div><strong>{activeOrders.length.toString().padStart(2, '0')}</strong><span>en cola</span></div><div className="kitchen-stats-divider" /><div><strong className={delayed ? 'text-orange' : ''}>{delayed.toString().padStart(2, '0')}</strong><span>con demora</span></div><div className="kitchen-stats-divider" /><div><strong>{menu.filter((item) => item.agotado).length.toString().padStart(2, '0')}</strong><span>agotados</span></div></div><div className="queue-list">{activeOrders.slice(0, 3).map((order) => <div className="queue-item" key={order.id_pedido}><div className={`queue-number ${order.es_retrasado ? 'delayed' : ''}`}>#{order.id_pedido.toString().slice(-2)}</div><div className="queue-detail"><strong>Mesa {order.numero_mesa}</strong><span>{order.detalles.reduce((sum, line) => sum + line.cantidad, 0)} productos · {relativeMinutes(order.fecha_hora_creacion)}</span></div><StatusBadge status={order.estado} /></div>)}</div><Link to="/app/cocina" className="panel-link">Ir a pantalla de cocina <ArrowRight size={15} /></Link></article>
      <article className="panel tables-panel"><div className="panel-heading"><div><div className="panel-kicker">PISO</div><h2>Estado de mesas</h2></div><Link to="/app/mesas" className="quiet-icon-button" aria-label="Ver mesas"><ArrowRight size={17} /></Link></div><div className="table-quick-grid">{tables.slice(0, 8).map((table) => <div key={table.id_mesa} className={`table-quick ${table.estado.toLowerCase()}`}><span>{table.numero_mesa.toString().padStart(2, '0')}</span><i /></div>)}</div><div className="table-legend"><span><i className="legend-free" /> Libres <b>{tables.filter((table) => table.estado === 'LIBRE').length}</b></span><span><i className="legend-busy" /> Ocupadas <b>{occupied}</b></span><span><i className="legend-clean" /> Limpieza <b>{tables.filter((table) => table.estado === 'POR_LIMPIAR').length}</b></span></div><Link to="/app/mesas" className="panel-link">Ver mapa de mesas <ArrowRight size={15} /></Link></article>
      <article className="panel activity-panel"><div className="panel-heading"><div><div className="panel-kicker">ACTIVIDAD</div><h2>Últimos movimientos</h2></div><button className="quiet-icon-button" aria-label="Más opciones"><MoreHorizontal size={19} /></button></div><div className="activity-list"><ActivityLine icon="🥗" title="Pedido listo para entregar" detail="Mesa 1 · Pedido #1046" time="Hace 2 min" color="green" /><ActivityLine icon="🧾" title="Nueva comanda recibida" detail="Mesa 3 · Pedido #1048" time="Hace 5 min" color="orange" /><ActivityLine icon="⚠️" title="Incidencia reportada" detail={incidents[0]?.tipo ?? 'Operación'} time="Hace 12 min" color="red" /></div><Link to="/app/incidencias" className="panel-link">Ver toda la actividad <ArrowRight size={15} /></Link></article>
    </section>
    <section className="dashboard-bottom"><div className="bottom-insight"><div className="insight-icon"><TrendingUp size={18} /></div><div><strong>Buen ritmo esta semana</strong><span>Las ventas están <b>8,4% arriba</b> de tu promedio.</span></div><ArrowUpRight size={17} className="insight-arrow" /></div><div className="bottom-insight warm"><div className="insight-icon"><Clock3 size={18} /></div><div><strong>Una oportunidad para hoy</strong><span>Tu hora más movida suele ser entre <b>1 y 2 pm.</b></span></div><ArrowRight size={17} className="insight-arrow" /></div></section>
  </>;
}

function Metric({ icon: Icon, label, value, change, note, positive, neutral }: { icon: LucideIcon; label: string; value: string; change: string; note: string; positive?: boolean; neutral?: boolean }) {
  return <article className="metric-card"><div className="metric-top"><span className="metric-icon"><Icon size={17} /></span><button className="quiet-icon-button" aria-label="Opciones"><MoreHorizontal size={18} /></button></div><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="metric-foot"><span className={`metric-change ${positive ? 'positive' : neutral ? 'neutral' : ''}`}>{positive && <ArrowUpRight size={13} />}{neutral && <ArrowDownRight size={13} />}{change}</span><span>{note}</span></div></article>;
}

function SalesChart({ orders }: { orders: Order[] }) {
  const hours = Array.from({ length: 13 }, (_, index) => index + 9);
  const totals = hours.map((hour) => orders.filter((order) => new Date(order.fecha_hora_creacion).getHours() === hour).reduce((sum, order) => sum + orderTotal(order), 0));
  const max = Math.max(...totals, 1);
  return <div className="sales-chart sales-chart-bars" role="img" aria-label="Ventas por hora de hoy"><div className="sales-bars">{totals.map((total, index) => <div className="sales-bar-group" key={hours[index]}><div className="sales-bar-track"><span style={{ height: `${total ? Math.max(8, total / max * 100) : 3}%` }} title={`${hours[index]}:00 · ${formatCOP(total)}`} /></div><small>{hours[index] % 2 === 1 ? `${hours[index]}h` : ''}</small></div>)}</div></div>;
}

function ActivityLine({ icon, title, detail, time, color }: { icon: string; title: string; detail: string; time: string; color: string }) {
  return <div className="activity-item"><div className={`activity-icon ${color}`}>{icon}</div><div className="activity-description"><strong>{title}</strong><span>{detail}</span></div><small>{time}</small></div>;
}

function orderTotal(order: Order): number {
  return order.detalles.reduce((sum, line) => sum + line.cantidad * line.precio_unitario, 0);
}

function dateKey(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Buenos días';
  if (hour < 19) return 'Buenas tardes';
  return 'Buenas noches';
}

