import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  timeout: 12_000,
});

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401)
        window.dispatchEvent(new CustomEvent('kitchenflow:unauthorized'));
      if (error.response?.status === 403)
        window.dispatchEvent(new CustomEvent('kitchenflow:forbidden'));
    }
    return Promise.reject(error);
  },
);

export function getApiError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const detail: unknown = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (error.code === 'ERR_NETWORK') return 'No fue posible conectar con el servidor.';
  }
  return fallback;
}

export const isDemoMode = false;
