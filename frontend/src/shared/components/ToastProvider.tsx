import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Check, Info, X } from 'lucide-react';

type ToastKind = 'success' | 'info';
interface ToastItem { id: number; message: string; kind: ToastKind }
interface ToastContextValue { notify: (message: string, kind?: ToastKind) => void }

const ToastContext = createContext<ToastContextValue | null>(null);
let nextToastId = 0;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const notify = useCallback((message: string, kind: ToastKind = 'success') => {
    const id = nextToastId++;
    setToasts((items) => [...items, { id, message, kind }]);
    window.setTimeout(() => setToasts((items) => items.filter((item) => item.id !== id)), 3800);
  }, []);
  useEffect(() => {
    const onForbidden = () => notify('No tienes permisos para realizar esta acción.', 'info');
    window.addEventListener('kitchenflow:forbidden', onForbidden);
    return () => window.removeEventListener('kitchenflow:forbidden', onForbidden);
  }, [notify]);
  const value = useMemo(() => ({ notify }), [notify]);
  return <ToastContext.Provider value={value}>{children}<div className="toast-stack" aria-live="polite">{toasts.map((toast) => <div className="toast" key={toast.id}><span className={`toast-icon ${toast.kind}`}>{toast.kind === 'success' ? <Check size={15} /> : <Info size={15} />}</span><span>{toast.message}</span><button onClick={() => setToasts((items) => items.filter((item) => item.id !== toast.id))} aria-label="Cerrar aviso"><X size={15} /></button></div>)}</div></ToastContext.Provider>;
}

export function useNotify() {
  const value = useContext(ToastContext);
  if (!value) throw new Error('useNotify debe usarse dentro de ToastProvider.');
  return value.notify;
}
