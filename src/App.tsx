import { useState } from 'react';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { MobileMarkets } from './components/MobileMarkets';
import { Portfolio } from './components/Portfolio';

function App() {
  const [activeTab, setActiveTab] = useState('markets');

  const renderContent = () => {
    switch (activeTab) {
      case 'markets':
      case 'trade':
        return <MobileMarkets />;
      case 'portfolio':
        return <Portfolio />;
      default:
        return (
          <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4">
            <div className="w-20 h-20 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-subtle)] flex items-center justify-center mb-4">
              <span className="text-4xl">🚧</span>
            </div>
            <h2 className="font-display text-xl font-semibold mb-2 capitalize">{activeTab}</h2>
            <p className="text-[var(--text-secondary)] text-sm">Coming soon...</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] pb-16">
      <Header />
      <main className="px-4 pt-4">
        {renderContent()}
      </main>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}

export default App;
