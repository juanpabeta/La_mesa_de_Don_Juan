import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { BellRing, ChefHat, CircleAlert, LoaderCircle, RefreshCw, Search, Volume2, VolumeX } from 'lucide-react'
import type { IncidentPayload, KitchenTicket, TicketFilter, UserSession } from '../../types'
import { getApiError } from '../../services/api'
import { pedidosService } from '../../services/pedidosService'
import { TicketCard } from './TicketCard'
import { IncidentDialog } from '../incidencias/IncidentDialog'

const filters: { id: TicketFilter; label: string; mark: string }[] = [
  { id: 'PENDIENTE', label: 'Nuevos', mark: 'bg-orange-500' },
  { id: 'EN_PREPARACION', label: 'En cocina', mark: 'bg-blue-500' },
  { id: 'LISTO', label: 'Para entregar', mark: 'bg-emerald-500' },
]

export function TicketBoard({ user, onLogout }: { user: UserSession; onLogout: () => void }) {
  const [tickets, setTickets] = useState<KitchenTicket[]>([])
  const [filter, setFilter] = useState<TicketFilter>('PENDIENTE')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [sound, setSound] = useState(false)
  const [newTicketId, setNewTicketId] = useState<number | null>(null)
  const [incidentTicket, setIncidentTicket] = useState<KitchenTicket | null>(null)
  const knownIds = useRef<Set<number> | null>(null)
  const canLogIncident = user.roles.some((role) => role.toUpperCase() === 'ADMIN')

  const loadTickets = useCallback(async (quiet = false) => {
    if (quiet) setRefreshing(true)
    else setLoading(true)
    try {
      const incoming = await pedidosService.tickets()
      const activeIds = new Set(incoming.map((ticket) => ticket.id))
      const previous = knownIds.current
      if (previous) {
        const newest = incoming.find((ticket) => !previous.has(ticket.id))
        if (newest) {
          setNewTicketId(newest.id)
          window.setTimeout(() => setNewTicketId(null), 5000)
          if (sound) {
            try {
              const context = new AudioContext()
              const oscillator = context.createOscillator()
              const gain = context.createGain()
              oscillator.connect(gain)
              gain.connect(context.destination)
              oscillator.frequency.value = 880
              gain.gain.value = 0.08
              oscillator.start()
              oscillator.stop(context.currentTime + 0.16)
              oscillator.onended = () => void context.close()
            } catch { /* Audio is an optional browser capability. */ }
          }
        }
      }
      knownIds.current = activeIds
      setTickets(incoming)
      setError('')
    } catch (reason) {
      setError(getApiError(reason))
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [sound])

  useEffect(() => {
    void loadTickets()
    const interval = window.setInterval(() => void loadTickets(true), 15_000)
    return () => window.clearInterval(interval)
  }, [loadTickets])

  const counts = useMemo(() => ({
    PENDIENTE: tickets.filter((ticket) => ticket.estado === 'PENDIENTE').length,
    EN_PREPARACION: tickets.filter((ticket) => ticket.estado === 'EN_PREPARACION').length,
    LISTO: tickets.filter((ticket) => ticket.estado === 'LISTO').length,
  }), [tickets])

  const visibleTickets = useMemo(() => tickets
    .filter((ticket) => ticket.estado === filter)
    .filter((ticket) => !search || `#${ticket.id} ${ticket.numero_mesa} ${ticket.detalles.map((item) => item.nombre_plato).join(' ')}`.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => new Date(a.creado_en).getTime() - new Date(b.creado_en).getTime()), [tickets, filter, search])

  async function advance(ticket: KitchenTicket, estado: KitchenTicket['estado']) {
    setBusyId(ticket.id)
    try {
      await pedidosService.cambiarEstado(ticket.id, estado)
      await loadTickets(true)
    } catch (reason) {
      setError(getApiError(reason))
    } finally {
      setBusyId(null)
    }
  }

  async function reportIncident(payload: IncidentPayload) {
    await pedidosService.registrarIncidencia(payload)
    setIncidentTicket(null)
  }

  const delayedCount = tickets.filter((ticket) => ticket.retrasado || ticket.minutos_transcurridos > ticket.minutos_estimados).length

  return (
    <div className="min-h-screen bg-paper">
      <header className="sticky top-0 z-20 border-b border-stone-200 bg-paper/95 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-4 px-4 py-3 sm:px-7">
          <div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-ink text-white"><ChefHat size={21} /></span><div><div className="text-lg font-black tracking-tight">MesaSync<span className="text-kitchen">.</span></div><div className="text-[10px] font-bold uppercase tracking-[.18em] text-stone-400">Comandería de cocina</div></div></div>
          <div className="flex items-center gap-2 sm:gap-3"><div className="hidden text-right sm:block"><div className="text-sm font-bold">{user.nombre_completo}</div><div className="text-[10px] uppercase tracking-wider text-stone-400">{user.roles.join(' · ')}</div></div><button onClick={() => setSound((value) => !value)} title={sound ? 'Silenciar avisos' : 'Activar avisos'} className={`grid h-10 w-10 place-items-center rounded-xl border ${sound ? 'border-orange-300 bg-orange-50 text-kitchen' : 'border-stone-200 bg-white text-stone-500'}`}>{sound ? <Volume2 size={18} /> : <VolumeX size={18} />}</button><button onClick={() => void loadTickets(true)} disabled={refreshing} aria-label="Actualizar tickets" className="grid h-10 w-10 place-items-center rounded-xl border border-stone-200 bg-white text-stone-600 hover:text-kitchen">{refreshing ? <LoaderCircle size={17} className="animate-spin" /> : <RefreshCw size={17} />}</button><button onClick={onLogout} className="rounded-xl px-3 py-2 text-xs font-bold text-stone-500 hover:bg-stone-200">Salir</button></div>
        </div>
      </header>

      <main className="mx-auto max-w-[1600px] px-4 py-7 sm:px-7 sm:py-10">
        <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end"><div><p className="mb-2 text-xs font-black uppercase tracking-[.22em] text-kitchen">Servicio en vivo</p><h1 className="text-3xl font-black tracking-tight sm:text-4xl">Tira de comandas</h1><p className="mt-2 text-sm text-stone-500">Tickets de cocina ordenados por antigüedad.</p></div><div className="flex gap-2 rounded-2xl border border-stone-200 bg-white p-3 shadow-sm"><div className="pr-4"><div className="font-mono text-xl font-black">{tickets.length}</div><div className="text-[10px] font-bold uppercase tracking-wider text-stone-400">Activos</div></div><div className="border-l border-stone-200 pl-4"><div className={`font-mono text-xl font-black ${delayedCount ? 'text-red-600' : ''}`}>{delayedCount}</div><div className="text-[10px] font-bold uppercase tracking-wider text-stone-400">Con retraso</div></div></div></div>

        {newTicketId && <div className="mt-6 flex items-center gap-3 rounded-xl border border-orange-200 bg-orange-50 px-4 py-3 text-sm font-bold text-orange-900"><BellRing size={18} className="text-kitchen" /> Nueva comanda #{newTicketId} en la cola</div>}
        {error && <div role="alert" className="mt-6 flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-800"><CircleAlert size={18} />{error}</div>}

        <div className="mt-7 flex flex-col justify-between gap-3 lg:flex-row lg:items-center">
          <nav aria-label="Filtrar por estado" className="flex w-full gap-1 overflow-x-auto rounded-xl border border-stone-200 bg-white p-1 lg:w-auto">{filters.map((item) => <button key={item.id} onClick={() => setFilter(item.id)} className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2.5 text-sm font-bold transition sm:px-4 ${filter === item.id ? 'bg-ink text-white' : 'text-stone-500 hover:bg-stone-100'}`}><span className={`h-2 w-2 rounded-full ${item.mark}`} />{item.label}<span className={`rounded-md px-1.5 py-0.5 font-mono text-xs ${filter === item.id ? 'bg-white/15 text-white' : 'bg-stone-100 text-stone-500'}`}>{counts[item.id]}</span></button>)}</nav>
          <label className="flex h-11 items-center gap-2 rounded-xl border border-stone-200 bg-white px-3 text-stone-400 lg:w-72"><Search size={16} /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar pedido, mesa o plato" className="w-full bg-transparent text-sm text-ink outline-none placeholder:text-stone-400" /></label>
        </div>

        {loading ? <div className="grid min-h-64 place-items-center text-sm text-stone-500"><span className="flex items-center gap-2"><LoaderCircle className="animate-spin" size={18} /> Cargando comandas...</span></div> : visibleTickets.length === 0 ? <div className="mt-8 rounded-2xl border border-dashed border-stone-300 bg-white/60 px-6 py-16 text-center"><span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-sage text-ink"><ChefHat /></span><h2 className="mt-4 text-lg font-black">{search ? 'No encontramos resultados' : 'Todo al día por aquí'}</h2><p className="mt-1 text-sm text-stone-500">{search ? 'Prueba con otro número o nombre de plato.' : 'Cuando llegue una comanda nueva, aparecerá en esta tira.'}</p></div> : <section aria-label="Tickets de cocina" className="ticket-rail mt-7 grid grid-cols-1 items-start gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">{visibleTickets.map((ticket) => <div key={ticket.id} className={newTicketId === ticket.id ? 'new-ticket' : ''}><TicketCard ticket={ticket} busy={busyId === ticket.id} onAdvance={(selected, next) => void advance(selected, next)} onIncident={canLogIncident ? setIncidentTicket : undefined} /></div>)}</section>}
        <footer className="mt-12 flex flex-wrap items-center justify-between gap-2 border-t border-stone-200 pt-4 text-xs text-stone-400"><span>Actualización automática cada 15 segundos</span><span>Las observaciones de cocina se resaltan en naranja</span></footer>
      </main>
      {incidentTicket && <IncidentDialog ticket={incidentTicket} onClose={() => setIncidentTicket(null)} onSubmit={reportIncident} />}
    </div>
  )
}
