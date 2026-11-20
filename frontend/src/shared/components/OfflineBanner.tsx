import { WifiOff } from 'lucide-react';
import { useOnlineStatus } from '../../core/hooks/useOnlineStatus';

export function OfflineBanner() {
  const online = useOnlineStatus();
  if (online) return null;
  return <div className="environment-banner offline"><WifiOff size={15} />Sin conexión · Revisa tu red para sincronizar los cambios</div>;
}
