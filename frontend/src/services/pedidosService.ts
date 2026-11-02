import { api } from './api'
import type { IncidentPayload, KitchenTicket, OrderStatus, UserSession } from '../types'

export const pedidosService = {
  async tickets() {
    const { data } = await api.get<KitchenTicket[]>('/pedidos/tickets')
    return data
  },
  async cambiarEstado(pedidoId: number, estado: OrderStatus) {
    const { data } = await api.patch(`/pedidos/${pedidoId}/estado`, { estado })
    return data
  },
  async registrarIncidencia(payload: IncidentPayload) {
    const { data } = await api.post('/incidencias', payload)
    return data
  },
  async sesion() {
    const { data } = await api.get<UserSession>('/auth/me')
    return data
  },
  async iniciarSesion(correo: string, contrasena: string) {
    await api.post('/auth/login', { correo, contrasena })
    return this.sesion()
  },
  async cerrarSesion() {
    await api.post('/auth/logout')
  },
}
