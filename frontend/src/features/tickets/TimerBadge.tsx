import { useEffect, useState } from 'react'
import { Clock3 } from 'lucide-react'
import type { KitchenTicket } from '../../types'

export function TimerBadge({ ticket }: { ticket: KitchenTicket }) {
  const [, setTick] = useState(0)
  useEffect(() => {
    const timer = window.setInterval(() => setTick((value) => value + 1), 15_000)
    return () => window.clearInterval(timer)
  }, [])

  const startedAt = ticket.inicio_preparacion_en || ticket.creado_en
  const elapsed = Math.max(ticket.minutos_transcurridos, Math.floor((Date.now() - new Date(startedAt).getTime()) / 60_000))
  const late = ticket.retrasado || elapsed > ticket.minutos_estimados
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 font-mono text-xs font-bold ${late ? 'bg-red-100 text-red-700' : 'bg-stone-100 text-stone-600'}`}>
      <Clock3 size={14} /> {elapsed} min {late && <span className="font-sans uppercase tracking-wide">· tarde</span>}
    </span>
  )
}
