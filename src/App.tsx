import { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { MainContent } from './components/MainContent';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('crypto');

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <Header 
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
        sidebarOpen={sidebarOpen} 
      />
      <div className="flex">
        <Sidebar 
          open={sidebarOpen} 
          activeTab={activeTab}
          onTabChange={setActiveTab}
        />
        <MainContent sidebarOpen={sidebarOpen} activeTab={activeTab} />
      </div>
    </div>
  );
}

export default App;
