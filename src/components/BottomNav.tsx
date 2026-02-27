import { BarChart3, Home, Wallet } from 'lucide-react';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'markets', label: 'Markets', icon: BarChart3 },
  { id: 'trade', label: 'Trade', icon: BarChart3 },
  { id: 'portfolio', label: 'Portfolio', icon: Wallet },
];

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-[var(--bg-secondary)]/90 backdrop-blur-2xl border-t border-[var(--border-subtle)] z-50 safe-area-pb">
      <div className="flex items-center justify-around h-full px-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                relative flex flex-col items-center justify-center gap-0.5 flex-1 h-12 transition-all duration-300
                ${isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)]'}
              `}
            >
              {/* Active indicator */}
              <div className={`
                absolute -top-0.5 left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full
                transition-all duration-300
                ${isActive 
                  ? 'bg-[var(--accent-primary)] shadow-[0_0_10px_var(--accent-primary)]' 
                  : 'bg-transparent'
                }
              `} />
              
              <div className={`
                p-1.5 rounded-xl transition-all duration-300
                ${isActive 
                  ? 'bg-[var(--accent-subtle)]' 
                  : ''
                }
              `}>
                <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
              </div>
              <span className={`text-[10px] font-medium transition-all ${isActive ? 'opacity-100' : 'opacity-60'}`}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
