import { useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';

export function Modal({ title, description, onClose, children, size = 'normal' }: {
  title: string;
  description?: string;
  onClose: () => void;
  children: ReactNode;
  size?: 'normal' | 'wide';
}) {
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [onClose]);
  return <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <section className={`modal-card ${size === 'wide' ? 'modal-wide' : ''}`} role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <header className="modal-header"><div><h2 id="modal-title">{title}</h2>{description && <p>{description}</p>}</div><button className="icon-button" aria-label="Cerrar" onClick={onClose}><X size={19} /></button></header>
      {children}
    </section>
  </div>;
}
