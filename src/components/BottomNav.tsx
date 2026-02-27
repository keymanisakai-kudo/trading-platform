import { BarChart3, Bitcoin, Globe, Wallet } from 'lucide-react';

interface BottomNavProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: 'markets', label: 'Markets', icon: Bitcoin },
  { id: 'trade', label: 'Trade', icon: BarChart3 },
  { id: 'portfolio', label: 'Portfolio', icon: Wallet },
  { id: 'news', label: 'News', icon: Globe },
];

export function BottomNav({ activeTab, onTabChange }: BottomNavProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 h-16 bg-[var(--bg-secondary)] border-t border-[var(--border-color)] z-50 safe-area-pb">
      <div className="flex items-center justify-around h-full">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors
                ${isActive 
                  ? 'text-[var(--accent-primary)]' 
                  : 'text-[var(--text-muted)]'
                }
              `}
            >
              <Icon size={22} />
              <span className="text-[10px] font-medium">{tab.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
