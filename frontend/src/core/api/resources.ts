import { api } from './client';
import type { Incident, MenuItem, Order, Table, TimingReport, User } from '../types';

export const resources = {
  tables: async () => (await api.get<Table[]>('/mesas')).data,
  menu: async () => (await api.get<MenuItem[]>('/menu')).data,
  orders: async () => (await api.get<Order[]>('/pedidos')).data,
  kitchenOrders: async () => (await api.get<Order[]>('/pedidos/tickets')).data,
  incidents: async () => (await api.get<Incident[]>('/incidencias')).data,
  users: async () => (await api.get<User[]>('/usuarios')).data,
  reportTiming: async () => (await api.get<TimingReport>('/reportes/tiempos')).data,
  createOrder: async (payload: { id_mesa: number; detalles: Array<{ id_plato: number; cantidad: number; observaciones?: string }> }) =>
    (await api.post<Order>('/pedidos', payload)).data,
  updateOrder: async (id: number, payload: Order['estado'] | { estado: Order['estado']; causa?: string }) => {
    const body = typeof payload === 'string' ? { estado: payload } : payload;
    return (await api.patch<Order>(`/pedidos/${id}/estado`, body)).data;
  },
  replaceOrder: async (id: number, detalles: Array<{ id_plato: number; cantidad: number; observaciones?: string }>) =>
    (await api.put<Order>(`/pedidos/${id}`, { detalles })).data,
  cancelOrder: async (id: number, causa: string) =>
    (await api.patch<Order>(`/pedidos/${id}/estado`, { estado: 'CANCELADO', causa })).data,
  updateTip: async (id: number, propina: number) =>
    (await api.patch<Order>(`/pedidos/${id}/propina`, { propina })).data,
  reprintOrder: async (id: number) => (await api.post<Order>(`/pedidos/${id}/reimprimir`)).data,
  updateDishAvailability: async (id: number, agotado: boolean) =>
    (await api.patch<MenuItem>(`/menu/${id}/agotado`, { agotado })).data,
  createDish: async (payload: Omit<MenuItem, 'id_plato' | 'agotado'>) =>
    (await api.post<MenuItem>('/menu', payload)).data,
  updateDish: async (id: number, payload: Partial<Omit<MenuItem, 'id_plato' | 'agotado'>>) =>
    (await api.put<MenuItem>(`/menu/${id}`, payload)).data,
  createIncident: async (payload: { id_pedido: number; tipo_error: string; descripcion: string; prioridad: 'BAJA' | 'MEDIA' | 'ALTA' }) =>
    (await api.post<Incident>('/incidencias', payload)).data,
  updateUser: async (id: number, payload: Partial<User>) =>
    (await api.put<User>(`/usuarios/${id}`, payload)).data,
  deactivateUser: async (id: number) => api.delete(`/usuarios/${id}`),
};
