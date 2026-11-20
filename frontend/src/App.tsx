import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { queryClient } from './core/api/queryClient';
import { AuthProvider } from './core/auth/AuthContext';
import { ProtectedRoute } from './core/auth/ProtectedRoute';
import { LoginPage } from './features/auth/LoginPage';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { TablesPage } from './features/mesas/TablesPage';
import { MenuPage } from './features/menu/MenuPage';
import { OrdersPage } from './features/pedidos/OrdersPage';
import { KitchenPage } from './features/cocina/KitchenPage';
import { IncidentsPage } from './features/incidencias/IncidentsPage';
import { UsersPage } from './features/usuarios/UsersPage';
import { ReportsPage } from './features/reportes/ReportsPage';
import { AppShell } from './shared/components/AppShell';
import { ToastProvider } from './shared/components/ToastProvider';
import { ThemeProvider } from './shared/components/ThemeProvider';

export function App() {
  return <QueryClientProvider client={queryClient}><BrowserRouter><ThemeProvider><AuthProvider><ToastProvider><Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route element={<ProtectedRoute />}><Route path="/app" element={<AppShell />}>
      <Route index element={<Navigate to="resumen" replace />} />
      <Route path="resumen" element={<DashboardPage />} />
      <Route path="mesas" element={<ProtectedRoute roles={['Administrador', 'Mesero', 'Cajero']}><TablesPage /></ProtectedRoute>} />
      <Route path="pedidos" element={<ProtectedRoute roles={['Administrador', 'Mesero', 'Cajero']}><OrdersPage /></ProtectedRoute>} />
      <Route path="cocina" element={<ProtectedRoute roles={['Administrador', 'Cocina', 'Cocinero']}><KitchenPage /></ProtectedRoute>} />
      <Route path="menu" element={<ProtectedRoute roles={['Administrador', 'Mesero', 'Cocina', 'Cocinero']}><MenuPage /></ProtectedRoute>} />
      <Route path="incidencias" element={<ProtectedRoute roles={['Administrador', 'Mesero', 'Cocina', 'Cocinero', 'Cajero']}><IncidentsPage /></ProtectedRoute>} />
      <Route path="reportes" element={<ProtectedRoute roles={['Administrador', 'Cajero']}><ReportsPage /></ProtectedRoute>} />
      <Route path="usuarios" element={<ProtectedRoute roles={['Administrador']}><UsersPage /></ProtectedRoute>} />
    </Route></Route>
    <Route path="/" element={<Navigate to="/app" replace />} />
    <Route path="*" element={<Navigate to="/app" replace />} />
  </Routes></ToastProvider></AuthProvider></ThemeProvider></BrowserRouter></QueryClientProvider>;
}
