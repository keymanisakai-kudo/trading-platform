import { useEffect, useState } from 'react';
import { useThemeStore } from '../stores/themeStore';
import { Sun, Moon, Zap } from 'lucide-react';

export function Header() {
  const { theme, toggleTheme } = useThemeStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      document.documentElement.setAttribute('data-theme', theme);
    }
  }, [theme, mounted]);

  return (
    <header className="h-14 bg-[var(--bg-secondary)]/80 backdrop-blur-xl border-b border-[var(--border-subtle)] sticky top-0 z-50">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--accent-primary)] to-[var(--success)] flex items-center justify-center">
              <Zap size={20} className="text-black" fill="currentColor" />
            </div>
            <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-br from-[var(--accent-primary)] to-[var(--success)] opacity-30 blur-sm" />
          </div>
          <span className="font-display font-bold text-lg tracking-tight">TradePro</span>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="w-10 h-10 rounded-xl bg-[var(--bg-card)] border border-[var(--border-default)] flex items-center justify-center transition-all hover:border-[var(--accent-primary)] hover:shadow-glow"
        >
          {theme === 'dark' ? (
            <Sun size={18} className="text-amber-400" />
          ) : (
            <Moon size={18} className="text-[var(--accent-primary)]" />
          )}
        </button>
      </div>
    </header>
  );
}
