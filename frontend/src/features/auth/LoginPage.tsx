import { useRef, useState, type FormEvent } from 'react';
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, Sparkles } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../core/auth/AuthContext';
import { getApiError } from '../../core/api/client';

export function LoginPage() {
  const { login } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const submitLock = useRef(false);
  const [error, setError] = useState('');
  const nextPath = (location.state as { from?: string } | null)?.from ?? '/app/resumen';

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitLock.current) return;
    submitLock.current = true;
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(nextPath, { replace: true });
    } catch (loginError) {
      setError(getApiError(loginError, 'No pudimos iniciar sesión. Verifica tus datos e intenta de nuevo.'));
    } finally {
      submitLock.current = false;
      setSubmitting(false);
    }
  };

  return <main className="login-screen"><section className="login-aside"><div className="login-aside-inner"><div className="brand-lockup login-brand"><img className="brand-logo" src="/logo.jpg" alt="La mesa de Don Juan" /><div className="brand-name">La mesa de <span>Don Juan</span><small>RESTAURANTE OS</small></div></div><div className="login-quote"><div className="quote-kicker"><Sparkles size={15} /> HECHO PARA FLUIR</div><h1>Una cocina en calma.<br /><em>Un servicio</em> impecable.</h1><p>Todo tu restaurante, conectado en un solo lugar. Menos ruido en la operación, más momentos que importan.</p></div></div></section><section className="login-main"><div className="login-form-wrap"><div className="login-mobile-logo"><img className="brand-logo" src="/logo.jpg" alt="La mesa de Don Juan" /><strong>La mesa de Don Juan</strong></div><div className="form-overline">BIENVENIDO DE VUELTA</div><h2>Inicia sesión</h2><p className="login-subtitle">Ingresa a tu espacio de trabajo para continuar.</p><form onSubmit={(event) => void submit(event)} className="login-form"><label htmlFor="email">Correo electrónico</label><div className="input-with-icon"><Mail size={17} /><input id="email" autoComplete="username" type="email" placeholder="tu@restaurante.com" value={email} onChange={(event) => setEmail(event.target.value)} required /></div><div className="label-row"><label htmlFor="password">Contraseña</label></div><div className="input-with-icon"><LockKeyhole size={17} /><input id="password" autoComplete="current-password" type={showPassword ? 'text' : 'password'} placeholder="Contraseña" value={password} onChange={(event) => setPassword(event.target.value)} required /><button type="button" className="show-password" aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setShowPassword((current) => !current)}>{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div>{error && <div className="form-error" role="alert">{error}</div>}<button className="button button-primary login-submit" type="submit" disabled={submitting}>{submitting ? 'Conectando…' : 'Entrar a La mesa de Don Juan'}<ArrowRight size={17} /></button></form><div className="login-security"><LockKeyhole size={14} /> Sesión protegida mediante cookie HttpOnly.</div></div></section></main>;
}
