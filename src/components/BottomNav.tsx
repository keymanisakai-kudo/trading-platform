import { Home, BarChart2, Wallet, Newspaper } from 'lucide-react';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'markets', label: 'Markets', icon: BarChart2 },
  { id: 'trade', label: 'Trade', icon: BarChart2 },
  { id: 'portfolio', label: 'Portfolio', icon: Wallet },
  { id: 'news', label: 'News', icon: Newspaper },
];

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-20 glass border-t border-[var(--border-subtle)] z-50 safe-area-pb">
      <div className="flex items-center justify-around h-full px-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                relative flex flex-col items-center justify-center gap-1 flex-1 h-14 transition-all duration-300
                ${isActive ? 'scale-110' : 'scale-100'}
              `}
            >
              {/* Active background */}
              <div className={`
                absolute inset-0 rounded-2xl transition-all duration-300
                ${isActive 
                  ? 'bg-[var(--accent-subtle)] shadow-lg' 
                  : 'bg-transparent'
                }
              `} />
              
              <Icon 
                size={22} 
                strokeWidth={isActive ? 2.5 : 2}
                className={`
                  relative z-10 transition-colors duration-300
                  ${isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)]'}
                `}
              />
              <span className={`
                relative z-10 text-[10px] font-medium transition-all duration-300
                ${isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)]'}
              `}>
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
