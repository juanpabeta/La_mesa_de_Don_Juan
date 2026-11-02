import { useState, type FormEvent } from 'react'
import { ChefHat, LoaderCircle, LockKeyhole, Mail } from 'lucide-react'
import { getApiError } from '../../services/api'
import { pedidosService } from '../../services/pedidosService'
import type { UserSession } from '../../types'

export function LoginPage({ onLogin }: { onLogin: (user: UserSession) => void }) {
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      onLogin(await pedidosService.iniciarSesion(correo, contrasena))
    } catch (reason) {
      setError(getApiError(reason))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="grid min-h-screen bg-paper lg:grid-cols-[1.08fr_.92fr]">
      <section className="relative hidden overflow-hidden bg-ink p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-28 -top-28 h-[32rem] w-[32rem] rounded-full border border-white/10" />
        <div className="absolute -right-12 -top-12 h-[22rem] w-[22rem] rounded-full border border-white/10" />
        <div className="relative flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-2xl bg-kitchen"><ChefHat /></span><span className="text-xl font-black tracking-tight">MesaSync</span></div>
        <div className="relative max-w-xl pb-10">
          <p className="mb-5 font-mono text-xs uppercase tracking-[.3em] text-orange-300">La cocina, en sincronía</p>
          <h1 className="text-6xl font-black leading-[1.03] tracking-tight">Cada pedido.<br /><span className="text-orange-300">En su punto.</span></h1>
          <p className="mt-7 max-w-md text-lg leading-8 text-white/60">Comandas claras, tiempos visibles y un equipo conectado desde la mesa hasta la cocina.</p>
        </div>
        <p className="relative text-xs text-white/35">MESA SYNC · OPERACIÓN DE COCINA</p>
      </section>
      <section className="flex items-center justify-center px-6 py-12">
        <form onSubmit={submit} className="w-full max-w-md">
          <div className="mb-10 flex items-center gap-3 lg:hidden"><span className="grid h-11 w-11 place-items-center rounded-2xl bg-kitchen text-white"><ChefHat /></span><span className="text-xl font-black">MesaSync</span></div>
          <p className="mb-3 text-xs font-bold uppercase tracking-[.22em] text-kitchen">Acceso al equipo</p>
          <h2 className="text-4xl font-black tracking-tight">Bienvenido</h2>
          <p className="mt-3 text-sm leading-6 text-stone-500">Ingresa con tu cuenta para ver las comandas activas.</p>
          <label className="mt-9 block text-sm font-bold" htmlFor="email">Correo electrónico</label>
          <div className="mt-2 flex items-center gap-3 rounded-xl border border-stone-200 bg-white px-4 focus-within:border-kitchen"><Mail size={18} className="text-stone-400" /><input id="email" type="email" autoComplete="username" required value={correo} onChange={(e) => setCorreo(e.target.value)} className="h-12 w-full bg-transparent text-sm outline-none" placeholder="tu@restaurante.com" /></div>
          <label className="mt-5 block text-sm font-bold" htmlFor="password">Contraseña</label>
          <div className="mt-2 flex items-center gap-3 rounded-xl border border-stone-200 bg-white px-4 focus-within:border-kitchen"><LockKeyhole size={18} className="text-stone-400" /><input id="password" type="password" autoComplete="current-password" required value={contrasena} onChange={(e) => setContrasena(e.target.value)} className="h-12 w-full bg-transparent text-sm outline-none" placeholder="••••••••••" /></div>
          {error && <p role="alert" className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}
          <button disabled={loading} className="mt-7 flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-ink text-sm font-bold text-white transition hover:bg-kitchen disabled:cursor-wait disabled:opacity-70">{loading && <LoaderCircle size={17} className="animate-spin" />} Entrar a cocina</button>
          <p className="mt-6 text-center text-xs text-stone-400">Tu sesión se mantiene protegida por una cookie segura del servidor.</p>
        </form>
      </section>
    </main>
  )
}
