const copFormatter = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 });

export function formatCOP(value: number): string {
  return copFormatter.format(value);
}

export function formatTime(value: string | Date): string {
  return new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit' }).format(new Date(value));
}

export function elapsedMinutes(value: string): number {
  return Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60_000));
}

export function relativeMinutes(value: string): string {
  const minutes = elapsedMinutes(value);
  return `${minutes} min`;
}

export function todayLabel(): string {
  return new Intl.DateTimeFormat('es-CO', { weekday: 'long', day: 'numeric', month: 'long' }).format(new Date());
}
