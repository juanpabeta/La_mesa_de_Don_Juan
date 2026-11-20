import { useMemo, useState, type FormEvent } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Check, MoreHorizontal, Plus, Search, ShieldCheck, UserCheck, UserMinus, Users } from 'lucide-react';
import { api, getApiError, isDemoMode } from '../../core/api/client';
import { resources } from '../../core/api/resources';
import { useResourceQuery } from '../../core/api/query';
import { demoUsers } from '../../core/data/demo';
import type { AppRole, User } from '../../core/types';
import { PageHeader } from '../../shared/components/PageHeader';
import { StatusBadge } from '../../shared/components/StatusBadge';
import { Modal } from '../../shared/components/Modal';
import { useNotify } from '../../shared/components/ToastProvider';
import { ConfirmModal } from '../../shared/components/ConfirmModal';

const roles: AppRole[] = ['Administrador', 'Mesero', 'Cocinero', 'Cajero'];

export function UsersPage() {
  const queryClient = useQueryClient();
  const notify = useNotify();
  const query = useResourceQuery('users', resources.users, demoUsers);
  const users = query.data ?? [];
  const [search, setSearch] = useState('');
  const [activeOnly, setActiveOnly] = useState(true);
  const [editing, setEditing] = useState<User | null | 'new'>(null);
  const [selectedMenu, setSelectedMenu] = useState<number | null>(null);
  const [pendingDeactivation, setPendingDeactivation] = useState<User | null>(null);
  const [deactivationBusy, setDeactivationBusy] = useState(false);
  const visible = useMemo(() => users.filter((user) => (!activeOnly || user.estado) && `${user.nombres} ${user.apellidos} ${user.correo} ${user.roles.join(' ')}`.toLowerCase().includes(search.toLowerCase())), [users, activeOnly, search]);
  const active = users.filter((user) => user.estado).length;
  const roleCounts = roles.map((role) => ({ role, count: users.filter((user) => user.estado && user.roles.includes(role)).length }));

  const saveUser = async (user: User, isNew: boolean, password?: string) => {
    if (!isDemoMode) {
      if (isNew) await api.post('/usuarios', { nombres: user.nombres, apellidos: user.apellidos, correo: user.correo, contraseña: password, roles: user.roles });
      else await resources.updateUser(user.id_usuario, { nombres: user.nombres, apellidos: user.apellidos, correo: user.correo, roles: user.roles });
    }
    queryClient.setQueryData<User[]>(['users'], (current = demoUsers) => isNew ? [...current, user] : current.map((item) => item.id_usuario === user.id_usuario ? user : item));
    setEditing(null);
    notify(isNew ? 'Invitación creada para el nuevo integrante.' : 'Perfil del equipo actualizado.');
  };

  const deactivate = async (user: User) => {
    setDeactivationBusy(true);
    try {
      if (!isDemoMode) await resources.deactivateUser(user.id_usuario);
      queryClient.setQueryData<User[]>(['users'], (current = demoUsers) => current.map((item) => item.id_usuario === user.id_usuario ? { ...item, estado: false } : item));
      setSelectedMenu(null);
      setPendingDeactivation(null);
      notify(`${user.nombres} fue desactivado. Su historial se conserva.`);
    } catch (error) { notify(getApiError(error, 'No se pudo desactivar al usuario.'), 'info'); }
    finally { setDeactivationBusy(false); }
  };

  return <>
    <PageHeader eyebrow="ADMINISTRACIÓN" title="Equipo" description="Administra accesos, roles y actividad de tu equipo." actions={<button className="button button-primary" onClick={() => setEditing('new')}><Plus size={17} /> Agregar empleado</button>} />
    <section className="user-summary-grid">
      <article className="user-summary-main">
        <div className="user-summary-icon"><Users size={18} /></div>
        <div className="user-summary-copy"><strong>{active.toString().padStart(2, '0')}</strong><span>Personas activas</span></div>
        <div className="user-avatar-stack">{users.filter((user) => user.estado).slice(0, 4).map((user, index) => <span className={`stack-avatar avatar-color-${index}`} key={user.id_usuario}>{user.nombres.slice(0, 1)}{user.apellidos.slice(0, 1)}</span>)}</div>
      </article>
      {roleCounts.map(({ role, count }) => <article className="user-role-card" key={role}>
        <div className="user-role-top"><span className="user-role-icon">{role === 'Administrador' ? <ShieldCheck size={16} /> : <UserCheck size={16} />}</span><strong>{count.toString().padStart(2, '0')}</strong></div>
        <span className="user-role-label">{role}</span>
      </article>)}
    </section>
    <section className="panel users-panel"><div className="users-toolbar"><div><h2>Personas y permisos</h2><p>Revisa quién puede acceder a cada parte de la operación.</p></div><div className="users-controls"><div className="table-search"><Search size={16} /><input placeholder="Buscar persona" aria-label="Buscar persona" value={search} onChange={(event) => setSearch(event.target.value)} /></div><button className={`button button-secondary button-small ${!activeOnly ? 'button-toggled' : ''}`} onClick={() => setActiveOnly((value) => !value)}>{activeOnly ? 'Activos' : 'Todos'}<span className="button-caret">▾</span></button></div></div><div className="order-table-wrap"><table className="data-table"><thead><tr><th>INTEGRANTE</th><th>ROL</th><th>ESTADO</th><th>ÚLTIMO ACCESO</th><th /></tr></thead><tbody>{visible.map((user, index) => <tr key={user.id_usuario}><td><div className="user-cell"><span className={`stack-avatar avatar-color-${index % 4}`}>{user.nombres.slice(0, 1)}{user.apellidos.slice(0, 1)}</span><div><strong>{user.nombres} {user.apellidos}</strong><small>{user.correo}</small></div></div></td><td><div className="role-tags">{user.roles.map((role) => <span className={`role-tag ${role === 'Administrador' ? 'role-admin' : ''}`} key={role}>{role}</span>)}</div></td><td><StatusBadge status={user.estado ? 'LIBRE' : 'POR_LIMPIAR'}>{user.estado ? 'Activo' : 'Inactivo'}</StatusBadge></td><td><span>{user.estado ? 'Hoy' : '—'}</span><small className="cell-muted">{user.estado ? 'desde este dispositivo' : 'Acceso desactivado'}</small></td><td><div className="user-menu-wrap"><button className="row-action" aria-label={`Opciones de ${user.nombres}`} onClick={() => setSelectedMenu(selectedMenu === user.id_usuario ? null : user.id_usuario)}><MoreHorizontal size={18} /></button>{selectedMenu === user.id_usuario && <div className="user-popover"><button onClick={() => { setEditing(user); setSelectedMenu(null); }}>Editar permisos</button>{user.estado && <button className="danger-menu-item" onClick={() => { setPendingDeactivation(user); setSelectedMenu(null); }}><UserMinus size={14} /> Desactivar usuario</button>}</div>}</div></td></tr>)}</tbody></table>{visible.length === 0 && <div className="empty-state"><strong>No encontramos personas</strong><p>Ajusta la búsqueda o revisa los filtros.</p></div>}</div><div className="table-footnote">Los usuarios desactivados conservan su historial de actividad.</div></section>
    {pendingDeactivation && <ConfirmModal title="Desactivar usuario" description={`El acceso de ${pendingDeactivation.nombres} ${pendingDeactivation.apellidos} quedará bloqueado. El historial se conservará.`} confirmLabel="Desactivar" busy={deactivationBusy} onConfirm={() => void deactivate(pendingDeactivation)} onClose={() => setPendingDeactivation(null)} />}
    {editing && <UserModal user={editing === 'new' ? null : editing} onClose={() => setEditing(null)} onSave={(user, password) => void saveUser(user, editing === 'new', password)} />}
  </>;
}

function UserModal({ user, onClose, onSave }: { user: User | null; onClose: () => void; onSave: (user: User, password?: string) => void }) {
  const [name, setName] = useState(user?.nombres ?? '');
  const [surname, setSurname] = useState(user?.apellidos ?? '');
  const [email, setEmail] = useState(user?.correo ?? '');
  const [password, setPassword] = useState('');
  const [selectedRoles, setSelectedRoles] = useState<AppRole[]>(user?.roles ?? ['Mesero']);
  const [error, setError] = useState('');
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (selectedRoles.length === 0) { setError('Asigna al menos un rol.'); return; }
    if (!user && password.length < 8) { setError('La contraseña inicial debe tener al menos 8 caracteres.'); return; }
    onSave({ id_usuario: user?.id_usuario ?? Date.now(), nombres: name.trim(), apellidos: surname.trim(), correo: email.trim(), estado: user?.estado ?? true, roles: selectedRoles }, user ? undefined : password);
  };
  return <Modal title={user ? 'Editar integrante' : 'Agregar empleado'} description={user ? 'Actualiza su información y acceso.' : 'Crea el perfil de acceso para tu nuevo integrante.'} onClose={onClose}><form className="modal-body" onSubmit={submit}><div className="form-two-cols"><div><label htmlFor="user-name">Nombre</label><input id="user-name" className="form-input" value={name} onChange={(event) => setName(event.target.value)} required /></div><div><label htmlFor="user-surname">Apellido</label><input id="user-surname" className="form-input" value={surname} onChange={(event) => setSurname(event.target.value)} required /></div></div><label htmlFor="user-email">Correo electrónico</label><input id="user-email" className="form-input" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />{!user && <><label htmlFor="user-password">Contraseña inicial</label><input id="user-password" className="form-input" type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /></>}<fieldset className="role-fieldset"><legend>Roles asignados</legend>{roles.map((role) => <label className="role-option" key={role}><input type="checkbox" checked={selectedRoles.includes(role)} onChange={(event) => setSelectedRoles((current) => event.target.checked ? [...current, role] : current.filter((item) => item !== role))} /><span>{role}</span><small>{roleDescription(role)}</small></label>)}</fieldset>{error && <p className="form-error">{error}</p>}<div className="modal-actions"><button type="button" className="button button-ghost" onClick={onClose}>Cancelar</button><button className="button button-primary"><Check size={15} />{user ? 'Guardar cambios' : 'Crear integrante'}</button></div></form></Modal>;
}

function roleDescription(role: AppRole): string { if (role === 'Administrador') return 'Acceso total y configuración'; if (role === 'Mesero') return 'Mesas, pedidos y atención'; if (role === 'Cocinero') return 'KDS, menú e incidencias'; return 'Pedidos, cobros y reportes'; }
