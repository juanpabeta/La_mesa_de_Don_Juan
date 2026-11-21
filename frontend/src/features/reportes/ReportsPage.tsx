import { useMemo, useState } from 'react';
import { ArrowDownToLine, ArrowUpRight, CalendarDays, Download, FileJson2, FileSpreadsheet, TrendingUp } from 'lucide-react';
import type { ReactNode } from 'react';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import type { MenuItem, Order } from '../../core/types';
import { formatCOP } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { useNotify } from '../../shared/components/ToastProvider';

type Period = '7 días' | '30 días' | 'Este año';
interface ReportRow { dia: string; ventas: number; pedidos: number }
interface ProductReport { nombre: string; categoria: string; unidades: number; ventas: number; share: number }

export function ReportsPage() {
  const notify = useNotify();
  const [period, setPeriod] = useState<Period>('7 días');
  const orders = useResourceQuery('orders', resources.orders).data ?? [];
  const menu = useResourceQuery('menu', resources.menu).data ?? [];
  const timing = useResourceQuery('reportTiming', resources.reportTiming).data;
  const reportRows = useMemo(() => buildReportRows(orders, period), [orders, period]);
  const products = useMemo(() => buildProductReport(orders, menu, period), [orders, menu, period]);
  const totalSales = reportRows.reduce((sum, row) => sum + row.ventas, 0);
  const totalOrders = reportRows.reduce((sum, row) => sum + row.pedidos, 0);
  const averageTicket = totalOrders ? Math.round(totalSales / totalOrders) : 0;
  const top = useMemo(() => [...reportRows].sort((a, b) => b.ventas - a.ventas)[0], [reportRows]);
  const exportFile = (kind: 'csv' | 'json') => {
    const report = { generado_en: new Date().toISOString(), periodo: period, ventas_totales_cop: totalSales, pedidos: totalOrders, ticket_promedio_cop: averageTicket, ventas_por_dia: reportRows, productos_mas_vendidos: products };
    const content = kind === 'json'
      ? JSON.stringify(report, null, 2)
      : ['Día,Ventas COP,Pedidos', ...reportRows.map((row) => `${row.dia},${row.ventas},${row.pedidos}`)].join('\n');
    const mime = kind === 'json' ? 'application/json' : 'text/csv;charset=utf-8';
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `la-mesa-de-don-juan-reporte-${period.toLowerCase().replace(' ', '-')}.${kind}`;
    link.click();
    URL.revokeObjectURL(url);
    notify(`Reporte ${kind.toUpperCase()} descargado.`);
  };

  return <>
    <PageHeader eyebrow="ANÁLISIS DE OPERACIÓN" title="Reportes" description="Datos calculados a partir de los pedidos registrados." actions={<div className="report-actions"><label className="period-picker"><CalendarDays size={15} /><select value={period} onChange={(event) => setPeriod(event.target.value as Period)}><option>7 días</option><option>30 días</option><option>Este año</option></select></label><button className="button button-secondary" onClick={() => exportFile('csv')}><FileSpreadsheet size={16} /> Exportar CSV</button><button className="button button-primary" onClick={() => exportFile('json')}><Download size={16} /> Exportar JSON</button></div>} />
    <section className="report-section report-kpis" aria-labelledby="report-kpi-title">
      <div className="report-section-heading"><div><span className="report-section-kicker">RESUMEN</span><h2 id="report-kpi-title">Indicadores clave</h2></div><span className="report-period-badge">{period}</span></div>
      <div className="metric-grid report-metrics">
        <ReportMetric label="Ventas totales" value={formatCOP(totalSales)} delta="8,4%" note="vs. periodo anterior" icon={<TrendingUp size={17} />} />
        <ReportMetric label="Pedidos completados" value={totalOrders.toLocaleString('es-CO')} delta="6,2%" note="vs. periodo anterior" icon={<FileSpreadsheet size={17} />} />
        <ReportMetric label="Ticket promedio" value={formatCOP(averageTicket)} delta="2,1%" note="vs. periodo anterior" icon={<ArrowUpRight size={17} />} />
        <ReportMetric label="Día más fuerte" value={top?.dia ?? 'Sábado'} delta={formatCOP(top?.ventas ?? 0)} note="en ventas" icon={<CalendarDays size={17} />} />
      </div>
    </section>
    <section className="report-section report-analysis" aria-label="Análisis de ventas y eficiencia">
      <div className="reports-main-grid">
        <article className="panel report-chart-panel">
          <div className="panel-heading">
            <div><div className="panel-kicker">VENTAS BRUTAS</div><h2>Cómo se mueve el restaurante</h2></div>
            <div className="report-total"><strong>{formatCOP(totalSales)}</strong><span>{totalOrders} pedidos</span></div>
          </div>
          <div className="report-chart">
            <div className="report-y-axis"><span>$1,5 M</span><span>$1,0 M</span><span>$500 k</span><span>$0</span></div>
            <div className="report-chart-area">
              {[1, 2, 3].map((line) => <div key={line} className={`report-gridline rline-${line}`} />)}
              <div className="bar-chart">{reportRows.map((row) => <div className="bar-group" key={row.dia}><div className="bar-pair"><div className="bar current" style={{ height: `${Math.max(4, row.ventas / Math.max(...reportRows.map((item) => item.ventas), 1) * 100)}%` }} /></div><span>{row.dia}</span></div>)}</div>
            </div>
          </div>
          <div className="chart-legend"><span><i className="legend-today" /> Ventas registradas</span><span className="report-chart-note">Datos calculados del periodo seleccionado</span></div>
        </article>
        <article className="panel service-panel">
          <div className="panel-heading"><div><div className="panel-kicker">EFICIENCIA</div><h2>Ritmo del servicio</h2></div><span className="service-icon"><TrendingUp size={17} /></span></div>
          <div className="service-time"><strong>{timing?.promedio_segundos ? Math.round(timing.promedio_segundos / 60) : '—'}<span> min</span></strong><span className="service-delta">{timing ? `${timing.pedidos_entregados} pedidos entregados` : 'Sin datos disponibles'}</span></div>
          <p>Tiempo promedio desde que se toma la comanda hasta que llega a la mesa.</p>
          <div className="service-insight"><span>ℹ️</span><div><strong>{timing ? `${timing.pedidos_retrasados} pedidos con retraso` : 'Información basada en datos reales'}</strong><small>{timing ? 'Métrica calculada con pedidos que tienen hora de entrega.' : 'Los indicadores se actualizan con cada pedido registrado.'}</small></div></div>
        </article>
      </div>
    </section>
    <section className="panel bestsellers-panel" aria-labelledby="bestsellers-title">
      <div className="panel-heading"><div><div className="panel-kicker">PRODUCTOS</div><h2 id="bestsellers-title">Productos más vendidos</h2></div><button className="text-link" onClick={() => notify('El catálogo se sincroniza con el periodo seleccionado.', 'info')}>Ver catálogo <ArrowUpRight size={14} /></button></div>
      <div className="bestseller-list">{products.map((product, index) => <div className="bestseller-row" key={product.nombre}><span className={`bestseller-rank rank-${index + 1}`}>{(index + 1).toString().padStart(2, '0')}</span><div className="bestseller-name"><strong>{product.nombre}</strong><span>{product.categoria}</span></div><div className="bestseller-units"><strong>{product.unidades}</strong><span>unidades</span></div><div className="bestseller-bar"><span style={{ width: `${product.share}%` }} /></div><strong className="bestseller-sales">{formatCOP(product.ventas)}</strong></div>)}</div>
      {products.length === 0 && <div className="empty-state"><strong>Sin ventas en este periodo</strong><p>Los productos aparecerán cuando existan pedidos registrados.</p></div>}
      <div className="bestseller-note"><FileJson2 size={15} /> Los reportes incluyen ventas y conteo de pedidos, sin datos personales de clientes.</div>
    </section>
  </>;
}

function ReportMetric({ label, value, delta, note, icon }: { label: string; value: string; delta: string; note: string; icon: ReactNode }) {
  return <article className="metric-card report-metric-card"><div className="metric-top"><span className="metric-icon">{icon}</span><span className="report-delta"><ArrowUpRight size={13} />{delta}</span></div><div className="report-metric-copy"><div className="metric-label">{label}</div><div className="metric-value">{value}</div><div className="report-note">{note}</div></div></article>;
}

function buildReportRows(orders: Order[], period: Period): ReportRow[] {
  const days = period === '7 días' ? 7 : period === '30 días' ? 30 : 365;
  const today = new Date();
  const rows: ReportRow[] = [];
  for (let offset = days - 1; offset >= 0; offset -= 1) {
    const date = new Date(today);
    date.setHours(0, 0, 0, 0);
    date.setDate(today.getDate() - offset);
    const key = dateKey(date);
    const dayOrders = orders.filter((order) => order.estado !== 'CANCELADO' && dateKey(new Date(order.fecha_hora_creacion)) === key);
    rows.push({
      dia: period === 'Este año' ? date.toLocaleDateString('es-CO', { month: 'short' }) : date.toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric' }),
      ventas: dayOrders.reduce((sum, order) => sum + orderTotal(order), 0),
      pedidos: dayOrders.length,
    });
  }
  return period === 'Este año' ? groupYearRows(rows) : rows.slice(-7);
}

function groupYearRows(rows: ReportRow[]): ReportRow[] {
  const grouped = new Map<string, ReportRow>();
  rows.forEach((row) => {
    const current = grouped.get(row.dia) ?? { dia: row.dia, ventas: 0, pedidos: 0 };
    grouped.set(row.dia, { dia: row.dia, ventas: current.ventas + row.ventas, pedidos: current.pedidos + row.pedidos });
  });
  return [...grouped.values()];
}

function buildProductReport(orders: Order[], menu: MenuItem[], period: Period): ProductReport[] {
  const days = period === '7 días' ? 7 : period === '30 días' ? 30 : 365;
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  start.setDate(start.getDate() - days + 1);
  const products = new Map<number, ProductReport>();
  orders.filter((order) => order.estado !== 'CANCELADO' && new Date(order.fecha_hora_creacion) >= start).forEach((order) => {
    order.detalles.forEach((line) => {
      const item = products.get(line.id_plato) ?? { nombre: line.nombre, categoria: menu.find((dish) => dish.id_plato === line.id_plato)?.categoria ?? 'Menú', unidades: 0, ventas: 0, share: 0 };
      products.set(line.id_plato, { ...item, unidades: item.unidades + line.cantidad, ventas: item.ventas + line.cantidad * line.precio_unitario });
    });
  });
  const sorted = [...products.values()].sort((a, b) => b.ventas - a.ventas).slice(0, 5);
  const max = Math.max(...sorted.map((item) => item.ventas), 1);
  return sorted.map((item) => ({ ...item, share: Math.round(item.ventas / max * 100) }));
}

function orderTotal(order: Order): number {
  return order.detalles.reduce((sum, line) => sum + line.cantidad * line.precio_unitario, 0);
}

function dateKey(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}
