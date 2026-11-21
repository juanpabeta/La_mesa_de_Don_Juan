import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Activity, Bell, BookOpen, ChefHat, ChevronDown, CircleDollarSign, ClipboardList, Grid2X2, LayoutDashboard, LogOut, Menu, Menu as MenuIcon, Search, Settings2, Users, Utensils, X, type LucideIcon } from 'lucide-react';
import { useAuth } from '../../core/auth/AuthContext';
import { useWebSocket } from '../../core/hooks/useWebSocket';
import type { AppRole } from '../../core/types';
import { OfflineBanner } from './OfflineBanner';
import { ThemeToggle } from './ThemeToggle';

interface NavItem { label: string; path: string; icon: LucideIcon; roles?: AppRole[]; group: string }
const navItems: NavItem[] = [
  { label: 'Resumen', path: '/app/resumen', icon: LayoutDashboard, group: 'GENERAL' },
  { label: 'Mesas', path: '/app/mesas', icon: Grid2X2, group: 'OPERACIÓN', roles: ['Administrador', 'Mesero', 'Cajero'] },
  { label: 'Pedidos', path: '/app/pedidos', icon: ClipboardList, group: 'OPERACIÓN', roles: ['Administrador', 'Mesero', 'Cajero'] },
  { label: 'Cocina KDS', path: '/app/cocina', icon: ChefHat, group: 'OPERACIÓN', roles: ['Administrador', 'Cocina', 'Cocinero'] },
  { label: 'Menú', path: '/app/menu', icon: BookOpen, group: 'OPERACIÓN', roles: ['Administrador', 'Mesero', 'Cocina', 'Cocinero'] },
  { label: 'Incidencias', path: '/app/incidencias', icon: Activity, group: 'GESTIÓN', roles: ['Administrador', 'Mesero', 'Cocinero', 'Cajero'] },
  { label: 'Reportes', path: '/app/reportes', icon: CircleDollarSign, group: 'GESTIÓN', roles: ['Administrador', 'Cajero'] },
  { label: 'Usuarios', path: '/app/usuarios', icon: Users, group: 'GESTIÓN', roles: ['Administrador'] },
];
const pageTitles: Record<string, string> = {
  '/app/resumen': 'Resumen', '/app/mesas': 'Mesas', '/app/pedidos': 'Pedidos', '/app/cocina': 'Cocina KDS',
  '/app/menu': 'Menú', '/app/incidencias': 'Incidencias', '/app/reportes': 'Reportes', '/app/usuarios': 'Equipo',
};

export function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const connected = useWebSocket(Boolean(user));
  const roleSet = user?.roles ?? [];
  const items = navItems.filter((item) => !item.roles || item.roles.some((role) => roleSet.includes(role)));
  const groups = [...new Set(items.map((item) => item.group))];
  const title = pageTitles[location.pathname] ?? 'La mesa de Don Juan';

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return <div className="app-layout">
    {mobileOpen && <button className="mobile-scrim" aria-label="Cerrar menú" onClick={() => setMobileOpen(false)} />}
    <aside className={`sidebar ${mobileOpen ? 'sidebar-open' : ''}`}>
      <div className="brand-lockup"><div className="brand-symbol"><Utensils size={19} strokeWidth={2.5} /></div><div className="brand-name">La mesa de <span>Don Juan</span><small>RESTAURANT OS</small></div><button className="mobile-close icon-button" onClick={() => setMobileOpen(false)} aria-label="Cerrar navegación"><X size={18} /></button></div>
      <div className="restaurant-switch"><div className="restaurant-avatar">M</div><div className="restaurant-copy"><strong>Madre Tierra</strong><span>Restaurante principal</span></div><ChevronDown size={15} /></div>
      <nav className="side-nav" aria-label="Navegación principal">{groups.map((group) => <div className="nav-group" key={group}><div className="nav-group-label">{group}</div><div className="nav-group-links">{items.filter((item) => item.group === group).map(({ label, path, icon: Icon }) => <NavLink to={path} key={path} onClick={() => setMobileOpen(false)} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}><Icon size={18} strokeWidth={1.9} /><span>{label}</span>{label === 'Cocina KDS' && <span className="nav-counter">3</span>}</NavLink>)}</div></div>)}</nav>
      <div className="sidebar-bottom"><div className="live-status"><span className={`live-pulse ${connected ? 'connected' : ''}`} /><div><strong>{connected ? 'En vivo' : 'Operación local'}</strong><small>{connected ? 'Conectado al servidor' : 'Actualización activa'}</small></div><Settings2 size={16} /></div><button className="profile-row" onClick={handleLogout}><div className="profile-avatar">{user?.nombres.slice(0, 1)}{user?.apellidos.slice(0, 1)}</div><div className="profile-copy"><strong>{user?.nombres} {user?.apellidos}</strong><small>{user?.roles[0] ?? 'Equipo'}</small></div><LogOut size={16} /></button></div>
    </aside>
    <div className="main-column"><header className="topbar"><button className="mobile-menu icon-button" aria-label="Abrir navegación" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div className="crumb"><span>Madre Tierra</span><span className="crumb-slash">/</span><strong>{title}</strong></div><div className="topbar-actions"><div className="search-shortcut"><Search size={16} /><span>Buscar</span><kbd>⌘ K</kbd></div><ThemeToggle /><button className="notification-button icon-button" aria-label="Notificaciones" onClick={() => navigate('/app/incidencias')}><Bell size={18} /><span /></button><div className="topbar-divider" /><div className="topbar-user"><div className="profile-avatar">{user?.nombres.slice(0, 1)}{user?.apellidos.slice(0, 1)}</div><ChevronDown size={14} /></div></div></header><OfflineBanner /><main className="page-content"><Outlet /></main><footer className="page-footer"><span>La mesa de Don Juan · Operación inteligente</span><span><span className="footer-dot" /> Servicio estable</span></footer></div>
  </div>;
}
