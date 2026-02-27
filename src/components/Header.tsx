import { useThemeStore } from '../stores/themeStore';
import { useEffect, useState } from 'react';
import { Menu, X, Sun, Moon, TrendingUp } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
}

export function Header({ onToggleSidebar, sidebarOpen }: HeaderProps) {
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
    <header className="h-[60px] bg-[var(--bg-secondary)] border-b border-[var(--border-color)] backdrop-blur-xl sticky top-0 z-50">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left: Menu + Logo */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-blue-600 flex items-center justify-center">
              <TrendingUp size={18} className="text-white" />
            </div>
            <span className="font-display font-semibold text-lg">TradePro</span>
          </div>
        </div>

        {/* Center: Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <a href="#" className="text-[var(--accent-primary)] font-medium">Markets</a>
          <a href="#" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">Trade</a>
          <a href="#" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">Portfolio</a>
          <a href="#" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">News</a>
        </nav>

        {/* Right: Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  );
}
