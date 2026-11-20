import type { ReactNode } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';
import type { AppRole } from '../types';

export function ProtectedRoute({ roles, children }: { roles?: AppRole[]; children?: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <div className="screen-loader"><span className="loader-dot" /> Preparando tu espacio de trabajo…</div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !user.roles.some((role) => roles.includes(role))) return <Navigate to="/app/resumen" replace />;
  return children ?? <Outlet />;
}
