import type { KitchenTicket } from '../../types'
import { formatDateTime } from './ticketUtils'

export function TicketPrint({ ticket }: { ticket: KitchenTicket }) {
  return (
    <div className="ticket-paper mx-auto w-full max-w-[360px] bg-white p-5 text-ink shadow-card">
      <div className="text-center font-mono text-[11px] uppercase tracking-[.18em]">MesaSync · Cocina</div>
      <div className="my-3 border-t border-dashed border-stone-500" />
      <div className="flex items-start justify-between gap-2 font-mono">
        <strong className="text-3xl">#{ticket.id}</strong>
        <span className="rounded border border-ink px-2 py-1 text-xs font-bold">{ticket.estado.replace('_', ' ')}</span>
      </div>
      <div className="mt-2 text-sm font-bold">MESA N.º {ticket.numero_mesa}</div>
      <div className="text-xs text-stone-600">Zona no informada · Usuario #{ticket.creado_por_id}</div>
      <div className="mt-2 flex justify-between gap-3 font-mono text-[10px] text-stone-600"><span>{formatDateTime(ticket.creado_en)}</span><span>{ticket.minutos_transcurridos} min</span></div>
      <div className="my-3 border-t border-dashed border-stone-500" />
      <div className="space-y-3">
        {ticket.detalles.map((detail) => (
          <div key={detail.id}>
            <div className="flex items-start gap-3"><strong className="min-w-7 font-mono text-2xl leading-none">{detail.cantidad}×</strong><span className="text-sm font-black uppercase leading-snug">{detail.nombre_plato}</span></div>
            {detail.notas && <div className="ml-10 mt-1 border-l-2 border-kitchen bg-orange-50 px-2 py-1 text-xs font-bold">↳ {detail.notas}</div>}
          </div>
        ))}
      </div>
      {ticket.notas && <div className="mt-4 border-2 border-dashed border-kitchen bg-orange-50 p-2 text-xs font-bold"><span className="mb-1 block font-mono uppercase tracking-wider">Nota de comanda</span>{ticket.notas}</div>}
      <div className="my-3 border-t border-dashed border-stone-500" />
      <p className="text-center font-mono text-[10px] uppercase tracking-widest">— Fin de comanda —</p>
    </div>
  )
}
