import { BarChart3, Bitcoin, Globe, Layers, Settings, Star } from 'lucide-react';

interface SidebarProps {
  open: boolean;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'crypto', label: 'Crypto', icon: Bitcoin },
  { id: 'forex', label: 'Forex', icon: Globe },
  { id: 'watchlist', label: 'Watchlist', icon: Star },
  { id: 'portfolio', label: 'Portfolio', icon: Layers },
  { id: 'orders', label: 'Orders', icon: BarChart3 },
];

export function Sidebar({ open, activeTab, onTabChange }: SidebarProps) {
  return (
    <aside
      className={`
        fixed left-0 top-[60px] h-[calc(100vh-60px)] bg-[var(--bg-secondary)] border-r border-[var(--border-color)]
        transition-all duration-300 z-40
        ${open ? 'w-[280px] translate-x-0' : 'w-0 -translate-x-full overflow-hidden'}
      `}
    >
      <div className="w-[280px] h-full flex flex-col p-3">
        <div className="flex-1 flex flex-col gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150
                  ${isActive 
                    ? 'bg-[var(--accent-glow)] text-[var(--accent-primary)]' 
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                  }
                `}
              >
                <Icon size={20} />
                <span className="font-medium">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Settings at bottom */}
        <div className="border-t border-[var(--border-color)] pt-3 mt-3">
          <button className="flex items-center gap-3 px-4 py-3 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)] transition-colors w-full">
            <Settings size={20} />
            <span className="font-medium">Settings</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
