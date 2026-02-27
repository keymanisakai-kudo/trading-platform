import { useState } from 'react';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { MobileMarkets } from './components/MobileMarkets';
import { ForexPanel } from './components/ForexPanel';

function App() {
  const [activeTab, setActiveTab] = useState('markets');

  const renderContent = () => {
    switch (activeTab) {
      case 'markets':
        return <MobileMarkets />;
      case 'forex':
        return <ForexPanel />;
      default:
        return (
          <div className="flex items-center justify-center h-[50vh] text-[var(--text-secondary)]">
            <p>{activeTab} - Coming soon</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] pb-16">
      <Header />
      <div className="p-4">
        {renderContent()}
      </div>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}

export default App;
