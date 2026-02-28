import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { BottomNav } from './components/BottomNav';
import { HomeScreen } from './components/HomeScreen';
import { MobileMarkets } from './components/MobileMarkets';
import { Portfolio } from './components/Portfolio';
import { NewsScreen } from './components/NewsScreen';
import { AuthScreen } from './components/AuthScreen';
import { useAuthStore } from './stores/authStore';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const { isAuthenticated, checkAuth, isLoading } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  // Show loading while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-[var(--text-secondary)]">Loading...</p>
        </div>
      </div>
    );
  }

  // Show auth screen if not authenticated
  if (!isAuthenticated) {
    return <AuthScreen />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <HomeScreen onNavigate={setActiveTab} />;
      case 'markets':
      case 'trade':
        return <MobileMarkets />;
      case 'portfolio':
        return <Portfolio />;
      case 'news':
        return <NewsScreen />;
      default:
        return (
          <div className="flex flex-col items-center justify-center h-[60vh] text-center px-4">
            <div className="w-20 h-20 clay-card flex items-center justify-center mb-4">
              <span className="text-4xl">🚧</span>
            </div>
            <h2 className="font-display text-xl font-semibold mb-2 capitalize">{activeTab}</h2>
            <p className="text-[var(--text-secondary)] text-sm">Coming soon...</p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen pb-20">
      <Header />
      <main className="px-4 pt-4">
        {renderContent()}
      </main>
      <BottomNav activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}

export default App;
