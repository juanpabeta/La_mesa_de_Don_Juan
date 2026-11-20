import { useMemo, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AlertCircle, ArrowUpRight, ClipboardCheck, Filter, Plus, Search, ShieldAlert } from 'lucide-react';
import { getApiError, isDemoMode } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import { demoIncidents } from '../../core/data/demo';
import type { Incident } from '../../core/types';
import { formatTime } from '../../shared/utils/format';
import { PageHeader } from '../../shared/components/PageHeader';
import { StatusBadge } from '../../shared/components/StatusBadge';
import { Modal } from '../../shared/components/Modal';
import { useNotify } from '../../shared/components/ToastProvider';

const incidentFilters = ['Todas', 'ABIERTA', 'EN_REVISION', 'RESUELTA'] as const;

export function IncidentsPage() {
  const queryClient = useQueryClient();
  const notify = useNotify();
  const query = useResourceQuery('incidents', resources.incidents, demoIncidents);
  const incidents = query.data ?? [];
  const [filter, setFilter] = useState<(typeof incidentFilters)[number]>('Todas');
  const [search, setSearch] = useState('');
  const [creating, setCreating] = useState(false);
  const visible = useMemo(() => incidents.filter((incident) => (filter === 'Todas' || incident.estado === filter) && `${incident.tipo} ${incident.descripcion} ${incident.creado_por}`.toLowerCase().includes(search.toLowerCase())), [incidents, filter, search]);
  const openCount = incidents.filter((incident) => incident.estado !== 'RESUELTA').length;
  const urgent = incidents.filter((incident) => incident.prioridad === 'ALTA' && incident.estado !== 'RESUELTA').length;

  const createIncident = async (payload: { id_pedido: number; tipo_error: string; descripcion: string; prioridad: Incident['prioridad'] }) => {
    let incident: Incident;
    if (!isDemoMode) incident = await resources.createIncident(payload);
    else incident = { id_incidencia: Math.max(0, ...incidents.map((item) => item.id_incidencia)) + 1, id_pedido: payload.id_pedido, id_usuario: 1, tipo_error: payload.tipo_error, tipo: payload.tipo_error, descripcion: payload.descripcion, prioridad: payload.prioridad, estado: 'ABIERTA', creado_por: 'Mariana Gómez', fecha_hora: new Date().toISOString(), fecha_registro: new Date().toISOString() };
    queryClient.setQueryData<Incident[]>(['incidents'], (current = demoIncidents) => [incident, ...current]);
    setCreating(false);
    notify('Incidencia registrada y agregada a la auditoría.');
  };

  return <>
    <PageHeader eyebrow="TRAZABILIDAD OPERATIVA" title="Incidencias" description="Registra novedades, asígnales prioridad y da seguimiento hasta resolverlas." actions={<button className="button button-primary" onClick={() => setCreating(true)}><Plus size={17} /> Reportar incidencia</button>} />
    <section className="incident-summary">
      <article className="incident-summary-card">
        <div className="incident-summary-top"><div className="incident-summary-copy"><strong className="summary-number">{openCount.toString().padStart(2, '0')}</strong><span>Incidencias abiertas</span></div><span className="incident-summary-icon warm"><AlertCircle size={18} /></span></div>
        <span className="summary-trend">En seguimiento</span>
      </article>
      <article className="incident-summary-card">
        <div className="incident-summary-top"><div className="incident-summary-copy"><strong className="summary-number">{urgent.toString().padStart(2, '0')}</strong><span>Prioridad alta</span></div><span className="incident-summary-icon red"><ShieldAlert size={18} /></span></div>
        <span className="summary-trend urgent">Requiere atención</span>
      </article>
      <article className="incident-summary-card">
        <div className="incident-summary-top"><div className="incident-summary-copy"><strong className="summary-number">{incidents.filter((incident) => incident.estado === 'RESUELTA').length.toString().padStart(2, '0')}</strong><span>Resueltas hoy</span></div><span className="incident-summary-icon green"><ClipboardCheck size={18} /></span></div>
        <span className="summary-trend">Buen trabajo</span>
      </article>
    </section>
    <section className="panel incidents-panel"><div className="incident-toolbar"><div className="filter-tabs">{incidentFilters.map((item) => <button className={`filter-tab ${filter === item ? 'selected' : ''}`} key={item} onClick={() => setFilter(item)}>{item === 'Todas' ? item : item === 'EN_REVISION' ? 'En revisión' : item === 'ABIERTA' ? 'Abiertas' : 'Resueltas'}<span className="filter-count">{item === 'Todas' ? incidents.length : incidents.filter((incident) => incident.estado === item).length}</span></button>)}</div><div className="incident-tools"><div className="table-search"><Search size={16} /><input placeholder="Buscar incidencia" aria-label="Buscar incidencia" value={search} onChange={(event) => setSearch(event.target.value)} /></div><button className="icon-button filter-button" title="Filtros"><Filter size={17} /></button></div></div><div className="order-table-wrap"><table className="data-table"><thead><tr><th>INCIDENCIA</th><th>CATEGORÍA</th><th>REPORTADA POR</th><th>FECHA</th><th>PRIORIDAD</th><th>ESTADO</th><th /></tr></thead><tbody>{visible.map((incident) => <tr key={incident.id_incidencia}><td><strong className="incident-title">{incident.descripcion}</strong><small className="cell-muted">INC-{incident.id_incidencia.toString().padStart(4, '0')}</small></td><td><span className="incident-category"><span>{categoryIcon(incident.tipo ?? incident.tipo_error)}</span>{incident.tipo ?? incident.tipo_error}</span></td><td>{incident.creado_por ?? 'Equipo'}</td><td><span>{formatTime(incident.fecha_hora ?? incident.fecha_registro)}</span><small className="cell-muted">Hoy</small></td><td><StatusBadge status={incident.prioridad} /></td><td><StatusBadge status={incident.estado} /></td><td><button className="row-action" aria-label={`Ver incidencia ${incident.id_incidencia}`}><ArrowUpRight size={16} /></button></td></tr>)}</tbody></table>{visible.length === 0 && <div className="empty-state"><span className="empty-emoji">🧾</span><strong>Sin incidencias para mostrar</strong><p>Los resultados aparecerán aquí cuando haya reportes.</p></div>}</div><div className="table-footnote">Registro de auditoría · {visible.length} resultados</div></section>
    {creating && <IncidentModal onClose={() => setCreating(false)} onSubmit={createIncident} />}
  </>;
}

function IncidentModal({ onClose, onSubmit }: { onClose: () => void; onSubmit: (payload: { id_pedido: number; tipo_error: string; descripcion: string; prioridad: Incident['prioridad'] }) => Promise<void> }) {
  const [orderId, setOrderId] = useState('');
  const [type, setType] = useState('Equipo');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Incident['prioridad']>('MEDIA');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!orderId) { setError('Selecciona el pedido relacionado.'); return; }
    setBusy(true); setError('');
    try { await onSubmit({ id_pedido: Number(orderId), tipo_error: type, descripcion: description, prioridad: priority }); }
    catch (requestError) { setError(getApiError(requestError, 'No se pudo registrar la incidencia.')); }
    finally { setBusy(false); }
  };
  return <Modal title="Reportar incidencia" description="Deja una nota para que el equipo pueda darle seguimiento." onClose={onClose}><form className="modal-body" onSubmit={(event) => void submit(event)}><label htmlFor="incident-order">Pedido relacionado</label><input id="incident-order" className="form-input" type="number" min="1" value={orderId} onChange={(event) => setOrderId(event.target.value)} required /><label htmlFor="incident-type">Categoría</label><select id="incident-type" className="form-input" value={type} onChange={(event) => setType(event.target.value)}><option>Equipo</option><option>Inventario</option><option>Servicio</option><option>Seguridad</option><option>Infraestructura</option><option>Otro</option></select><label htmlFor="incident-description">¿Qué ocurrió?</label><textarea id="incident-description" className="form-textarea" minLength={8} placeholder="Describe el problema y dónde ocurrió…" value={description} onChange={(event) => setDescription(event.target.value)} required /><label htmlFor="incident-priority">Prioridad</label><select id="incident-priority" className="form-input" value={priority} onChange={(event) => setPriority(event.target.value as Incident['prioridad'])}><option value="BAJA">Baja · puede esperar</option><option value="MEDIA">Media · atender pronto</option><option value="ALTA">Alta · afecta la operación</option></select>{error && <p className="form-error">{error}</p>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Cancelar</button><button className="button button-primary" disabled={busy || description.trim().length < 8}>{busy ? 'Guardando…' : 'Registrar incidencia'}<ArrowUpRight size={15} /></button></div></form></Modal>;
}

function categoryIcon(type: string): string { if (type === 'Equipo') return '⚙️'; if (type === 'Inventario') return '📦'; if (type === 'Servicio') return '🛎️'; if (type === 'Seguridad') return '🛡️'; return '📋'; }
