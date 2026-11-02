import { CircleAlert, CircleCheck, X } from 'lucide-react'

export interface ToastMessage {
  id: number
  text: string
  kind: 'success' | 'error' | 'info'
}

export function Toast({ message, onClose }: { message: ToastMessage; onClose: () => void }) {
  const icon = message.kind === 'error' ? <CircleAlert size={18} /> : <CircleCheck size={18} />
  const tone = message.kind === 'error' ? 'bg-red-900' : message.kind === 'success' ? 'bg-ink' : 'bg-blue-900'
  return (
    <div role="status" className={`fixed bottom-5 right-5 z-50 flex max-w-sm items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium text-white shadow-card ${tone}`}>
      {icon}<span>{message.text}</span>
      <button onClick={onClose} aria-label="Cerrar aviso" className="ml-2 rounded p-1 hover:bg-white/15"><X size={16} /></button>
    </div>
  )
}
