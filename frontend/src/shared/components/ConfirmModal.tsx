import { AlertTriangle } from 'lucide-react';
import { Modal } from './Modal';

interface ConfirmModalProps {
  title: string;
  description: string;
  confirmLabel: string;
  busy?: boolean;
  onConfirm: () => void;
  onClose: () => void;
}

export function ConfirmModal({
  title,
  description,
  confirmLabel,
  busy = false,
  onConfirm,
  onClose,
}: ConfirmModalProps) {
  return <Modal title={title} description={description} onClose={onClose}>
    <div className="modal-body confirm-modal-body">
      <div className="confirm-modal-symbol" aria-hidden="true">
        <AlertTriangle size={22} />
      </div>
      <p>{description}</p>
      <div className="modal-actions">
        <button type="button" className="button button-ghost" onClick={onClose} disabled={busy}>Cancelar</button>
        <button type="button" className="button button-danger" onClick={onConfirm} disabled={busy}>
          {busy ? 'Procesando...' : confirmLabel}
        </button>
      </div>
    </div>
  </Modal>;
}
