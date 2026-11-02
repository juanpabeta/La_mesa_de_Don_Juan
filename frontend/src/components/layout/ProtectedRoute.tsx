import type { ReactNode } from 'react'
import type { UserSession } from '../../types'

export function ProtectedRoute({ user, allowedRoles, children }: { user: UserSession | null; allowedRoles: string[]; children: ReactNode }) {
  if (!user) return null
  const permitted = user.roles.some((role) => allowedRoles.includes(role.toUpperCase()))
  if (!permitted) return <main className="grid min-h-screen place-items-center bg-paper p-6 text-center"><div><h1 className="text-2xl font-black">Sin acceso a cocina</h1><p className="mt-2 text-sm text-stone-500">Tu usuario no tiene un rol autorizado para ver los tickets.</p></div></main>
  return children
}
