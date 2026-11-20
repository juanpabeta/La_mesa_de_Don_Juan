import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import type { RealtimeEvent } from '../types';

export function useWebSocket(enabled: boolean) {
  const queryClient = useQueryClient();
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!enabled) {
      setConnected(false);
      return;
    }
    let socket: WebSocket | null = null;
    let timer = 0;
    let retry = 0;
    let disposed = false;
    const connect = () => {
      if (disposed) return;
      const url = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/api/v1/ws';
      socket = new WebSocket(url);
      socket.onopen = () => {
        retry = 0;
        setConnected(true);
      };
      socket.onmessage = (message: MessageEvent<string>) => {
        try {
          const event: unknown = JSON.parse(message.data);
          if (!isRealtimeEvent(event)) return;
          const resource = event.type.startsWith('order') ? 'orders'
            : event.type.startsWith('menu') ? 'menu'
              : event.type.startsWith('table') ? 'tables' : 'incidents';
          void queryClient.invalidateQueries({ queryKey: [resource] });
        } catch {
          // Ignore malformed frames; the next valid event will still be processed.
        }
      };
      socket.onclose = () => {
        setConnected(false);
        if (!disposed) {
          const delay = Math.min(30_000, 800 * 2 ** retry);
          retry += 1;
          timer = window.setTimeout(connect, delay + Math.random() * 300);
        }
      };
      socket.onerror = () => socket?.close();
    };
    connect();
    return () => {
      disposed = true;
      window.clearTimeout(timer);
      socket?.close();
      setConnected(false);
    };
  }, [enabled, queryClient]);

  return connected;
}

function isRealtimeEvent(value: unknown): value is RealtimeEvent {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Partial<RealtimeEvent>;
  return typeof candidate.type === 'string' && typeof candidate.payload === 'object' && candidate.payload !== null;
}
