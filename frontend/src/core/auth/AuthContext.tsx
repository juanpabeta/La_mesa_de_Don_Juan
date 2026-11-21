import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api } from '../api/client';
import type { User } from '../types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);
function isUser(value: unknown): value is User {
  if (typeof value !== 'object' || value === null) return false;
  const candidate = value as Partial<User>;
  return typeof candidate.id_usuario === 'number'
    && typeof candidate.nombres === 'string'
    && typeof candidate.apellidos === 'string'
    && typeof candidate.correo === 'string'
    && Array.isArray(candidate.roles);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const hydrate = async () => {
      try {
        const response = await api.get<User>('/auth/me');
        if (active && isUser(response.data)) setUser(response.data);
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    };
    void hydrate();
    const onUnauthorized = () => {
      setUser(null);
    };
    window.addEventListener('lamesadedonjuan:unauthorized', onUnauthorized);
    return () => {
      active = false;
      window.removeEventListener('lamesadedonjuan:unauthorized', onUnauthorized);
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    await api.post('/auth/login', { correo: email, contraseña: password });
    const response = await api.get<User>('/auth/me');
    if (!isUser(response.data)) throw new Error('El servidor devolvió un perfil de usuario inválido.');
    setUser(response.data);
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // Clearing local UI state is still safe if the API has no logout endpoint.
    }
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth debe usarse dentro de AuthProvider.');
  return value;
}
