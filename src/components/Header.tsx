import { useEffect, useState } from 'react';
import { useThemeStore } from '../stores/themeStore';
import { Sun, Moon, TrendingUp } from 'lucide-react';

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
    <header className="h-14 bg-[var(--bg-secondary)] border-b border-[var(--border-color)] backdrop-blur-xl sticky top-0 z-50 px-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-blue-600 flex items-center justify-center">
          <TrendingUp size={18} className="text-white" />
        </div>
        <span className="font-display font-semibold text-lg">TradePro</span>
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
      >
        {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
      </button>
    </header>
  );
}
