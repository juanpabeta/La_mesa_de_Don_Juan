import { useState, type FormEvent } from 'react'
import type { IncidentPayload, KitchenTicket } from '../../types'
import { getApiError } from '../../services/api'

export function IncidentDialog({ ticket, onClose, onSubmit }: { ticket: KitchenTicket; onClose: () => void; onSubmit: (payload: IncidentPayload) => Promise<void> }) {
  const [type, setType] = useState<IncidentPayload['tipo']>('OTRA')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      await onSubmit({ pedido_id: ticket.id, tipo: type, descripcion: description })
    } catch (reason) {
      setError(getApiError(reason))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="fixed inset-0 z-40 grid place-items-center bg-ink/50 p-4" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <form onSubmit={(event) => void submit(event)} className="w-full max-w-md rounded-2xl bg-white p-6 shadow-card">
        <div className="flex items-start justify-between">
          <div><p className="text-xs font-bold uppercase tracking-widest text-kitchen">Pedido #{ticket.id}</p><h2 className="mt-1 text-xl font-black">Registrar incidencia</h2></div>
          <button type="button" onClick={onClose} className="rounded-lg px-2 py-1 text-stone-400 hover:bg-stone-100" aria-label="Cerrar">✕</button>
        </div>
        <label className="mt-5 block text-sm font-bold">Tipo
          <select value={type} onChange={(event) => setType(event.target.value as IncidentPayload['tipo'])} className="mt-2 h-11 w-full rounded-xl border border-stone-200 px-3">
            {['PERDIDA', 'ENTREGA_ERRONEA', 'DEMORA', 'CANCELACION', 'MESA_EQUIVOCADA', 'OTRA'].map((item) => <option key={item}>{item}</option>)}
          </select>
        </label>
        <label className="mt-4 block text-sm font-bold">Descripción
          <textarea required minLength={5} maxLength={4000} value={description} onChange={(event) => setDescription(event.target.value)} className="mt-2 min-h-28 w-full rounded-xl border border-stone-200 p-3 text-sm outline-none focus:border-kitchen" placeholder="Describe brevemente qué ocurrió..." />
        </label>
        {error && <p role="alert" className="mt-3 text-sm text-red-700">{error}</p>}
        <button disabled={busy} className="mt-5 h-11 w-full rounded-xl bg-ink text-sm font-bold text-white hover:bg-kitchen disabled:opacity-50">{busy ? 'Guardando...' : 'Guardar incidencia'}</button>
      </form>
    </div>
  )
}
