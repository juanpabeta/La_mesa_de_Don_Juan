import { Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const nextTheme = theme === 'light' ? 'oscuro' : 'claro';

  return <button
    className="theme-toggle"
    type="button"
    onClick={toggleTheme}
    aria-label={`Cambiar a modo ${nextTheme}`}
    title={`Cambiar a modo ${nextTheme}`}
  >
    <span className={theme === 'light' ? 'theme-option active' : 'theme-option'}><Sun size={15} /></span>
    <span className={theme === 'dark' ? 'theme-option active' : 'theme-option'}><Moon size={15} /></span>
  </button>;
}
