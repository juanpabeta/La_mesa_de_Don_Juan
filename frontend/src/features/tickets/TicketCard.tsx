import { Printer, ArrowRight, TriangleAlert } from 'lucide-react'
import type { KitchenTicket, OrderStatus } from '../../types'
import { StatusPill } from '../../components/ui/StatusPill'
import { TicketPrint } from './TicketPrint'
import { formatDateTime } from './ticketUtils'
import { TimerBadge } from './TimerBadge'

interface TicketCardProps {
  ticket: KitchenTicket
  busy: boolean
  onAdvance: (ticket: KitchenTicket, next: OrderStatus) => void
  onIncident?: (ticket: KitchenTicket) => void
}

const nextState: Partial<Record<OrderStatus, OrderStatus>> = {
  PENDIENTE: 'EN_PREPARACION',
  EN_PREPARACION: 'LISTO',
  LISTO: 'ENTREGADO',
}
const actionText: Partial<Record<OrderStatus, string>> = {
  PENDIENTE: 'Pasar a preparación',
  EN_PREPARACION: 'Marcar como listo',
  LISTO: 'Despachar pedido',
}

export function TicketCard({ ticket, busy, onAdvance, onIncident }: TicketCardProps) {
  const print = () => {
    const card = document.getElementById(`ticket-${ticket.id}`)
    card?.classList.add('print-target')
    window.print()
    window.setTimeout(() => card?.classList.remove('print-target'), 500)
  }

  return (
    <article id={`ticket-${ticket.id}`} className={`ticket-shell overflow-hidden rounded-2xl border bg-white shadow-card ${ticket.retrasado ? 'border-red-300' : 'border-stone-200'}`}>
      <header className="flex items-start justify-between border-b border-dashed border-stone-200 px-5 py-4">
        <div><div className="font-mono text-3xl font-black tracking-tight">#{ticket.id}</div><p className="mt-1 text-sm font-bold">Mesa N.º {ticket.numero_mesa}</p><p className="mt-0.5 text-xs text-stone-500">Zona no informada · Usuario #{ticket.creado_por_id}</p></div>
        <div className="flex flex-col items-end gap-2"><StatusPill status={ticket.estado} /><TimerBadge ticket={ticket} /></div>
      </header>
      <div className="px-5 py-4">
        <div className="mb-3 flex items-center justify-between font-mono text-[11px] text-stone-500"><span>CREADO {formatDateTime(ticket.creado_en)}</span><span>OBJETIVO {ticket.minutos_estimados} MIN</span></div>
        {ticket.notas && <div className="mb-4 rounded-lg border-l-4 border-kitchen bg-orange-50 px-3 py-2 text-sm font-semibold"><span className="mb-1 block text-[10px] font-black uppercase tracking-widest text-orange-800">Nota general</span>{ticket.notas}</div>}
        <div className="divide-y divide-dashed divide-stone-200">
          {ticket.detalles.map((detail) => <div key={detail.id} className="py-3 first:pt-1 last:pb-1"><div className="flex items-start gap-3"><span className="grid h-9 min-w-9 place-items-center rounded-lg bg-ink font-mono text-lg font-black text-white">{detail.cantidad}</span><h3 className="pt-1 text-[15px] font-extrabold leading-5">{detail.nombre_plato}</h3></div>{detail.notas && <p className="ml-12 mt-2 rounded-md border border-orange-200 bg-orange-50 px-3 py-2 text-sm font-bold text-orange-950"><span className="mr-1 text-kitchen">↳</span>{detail.notas}</p>}</div>)}
        </div>
      </div>
      <footer className="space-y-2 border-t border-stone-100 bg-stone-50 p-4">
        {nextState[ticket.estado] && <button disabled={busy} onClick={() => onAdvance(ticket, nextState[ticket.estado]!)} className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-ink px-4 text-sm font-bold text-white transition hover:bg-kitchen disabled:opacity-50">{actionText[ticket.estado]}<ArrowRight size={16} /></button>}
        <div className="flex gap-2"><button onClick={print} className="flex h-10 flex-1 items-center justify-center gap-2 rounded-xl border border-stone-300 bg-white text-sm font-bold hover:border-ink"><Printer size={16} /> Imprimir ticket</button>{onIncident && <button onClick={() => onIncident(ticket)} title="Registrar incidencia" className="grid h-10 w-11 place-items-center rounded-xl border border-stone-300 bg-white text-stone-600 hover:border-red-300 hover:text-red-700"><TriangleAlert size={17} /></button>}</div>
      </footer>
      <div className="print-only"><TicketPrint ticket={ticket} /></div>
    </article>
  )
}
