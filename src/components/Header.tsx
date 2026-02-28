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
    <header className="h-16 glass sticky top-0 z-50 px-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#ff6b6b] to-[#ffa502] flex items-center justify-center shadow-lg animate-float">
          <Zap size={22} className="text-white" fill="currentColor" />
        </div>
        <span className="font-display font-bold text-xl tracking-tight">TradeClay</span>
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="w-12 h-12 rounded-2xl clay-card-sm flex items-center justify-center transition-all hover:scale-105"
      >
        {theme === 'dark' ? (
          <Sun size={20} className="text-amber-500" />
        ) : (
          <Moon size={20} className="text-indigo-500" />
        )}
      </button>
    </header>
  );
}
