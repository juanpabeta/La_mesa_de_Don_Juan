import { useEffect, useState } from 'react'
import { LoaderCircle } from 'lucide-react'
import { pedidosService } from './services/pedidosService'
import { LoginPage } from './features/auth/LoginPage'
import { TicketBoard } from './features/tickets/TicketBoard'
import { ProtectedRoute } from './components/layout/ProtectedRoute'
import type { UserSession } from './types'

export default function App() {
  const [user, setUser] = useState<UserSession | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    pedidosService.sesion().then(setUser).catch(() => setUser(null)).finally(() => setChecking(false))
  }, [])

  async function logout() {
    try { await pedidosService.cerrarSesion() } catch { /* La vista se limpia aunque la sesión ya haya expirado. */ }
    setUser(null)
  }

  if (checking) return <main className="grid min-h-screen place-items-center bg-paper text-stone-500"><span className="flex items-center gap-2 text-sm"><LoaderCircle size={18} className="animate-spin" /> Verificando sesión...</span></main>
  if (!user) return <LoginPage onLogin={setUser} />
  return <ProtectedRoute user={user} allowedRoles={['ADMIN', 'GERENTE', 'COCINA']}><TicketBoard user={user} onLogout={() => void logout()} /></ProtectedRoute>
}
