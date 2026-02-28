import { useState, useEffect } from 'react';
import { TrendingUp, Clock, ExternalLink, RefreshCw } from 'lucide-react';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  time: string;
  url: string;
}

const mockNews: NewsItem[] = [
  { id: '1', title: 'Bitcoin Surges Past $95K as Institutional Demand Continues', source: 'CoinDesk', time: '2h ago', url: '#' },
  { id: '2', title: 'Ethereum Layer 2 Solutions See Record Transaction Volume', source: 'The Block', time: '3h ago', url: '#' },
  { id: '3', title: 'Solana DeFi TVL Reaches New All-Time High', source: 'Decrypt', time: '4h ago', url: '#' },
  { id: '4', title: 'SEC Approves Multiple Crypto ETF Applications', source: 'Bloomberg', time: '5h ago', url: '#' },
  { id: '5', title: 'Major Banks Enter Crypto Custody Market', source: 'Reuters', time: '6h ago', url: '#' },
  { id: '6', title: 'DeFi Protocol Launches Cross-Chain Bridge', source: 'CoinGecko', time: '7h ago', url: '#' },
];

const categories = ['All', 'Crypto', 'DeFi', 'Regulation', 'NFT', 'Tech'];

export function NewsScreen() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('All');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    setTimeout(() => {
      setNews(mockNews);
      setLoading(false);
    }, 1000);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  return (
    <div className="pb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h1 className="font-display text-2xl font-bold">News</h1>
        <button 
          onClick={handleRefresh}
          className={`w-10 h-10 clay-card-sm flex items-center justify-center ${refreshing ? 'animate-spin' : ''}`}
        >
          <RefreshCw size={18} className="text-[var(--accent-primary)]" />
        </button>
      </div>

      {/* Categories */}
      <div className="flex gap-2 mb-5 overflow-x-auto scrollbar-hide -mx-4 px-4 pb-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`
              px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all
              ${activeCategory === cat 
                ? 'bg-gradient-to-r from-[#ff6b6b] to-[#ffa502] text-white shadow-lg' 
                : 'clay-card-sm text-[var(--text-secondary)]'
              }
            `}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Trending */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp size={16} className="text-[var(--accent-primary)]" />
          <span className="font-semibold">Trending</span>
        </div>
        <div className="flex gap-2 overflow-x-auto scrollbar-hide -mx-4 px-4 pb-2">
          {['#Bitcoin', '#ETH', '#SOL', '#DeFi', '#ETF'].map((tag) => (
            <button
              key={tag}
              className="flex-shrink-0 px-4 py-2 clay-card-sm text-sm"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* News List */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 clay-card-sm skeleton" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {news.map((item, index) => (
            <a
              key={item.id}
              href={item.url}
              className="block p-4 clay-card-sm hover:scale-[1.02] transition-all animate-fade-in-up"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-medium text-sm mb-2 line-clamp-2">{item.title}</h3>
                  <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <span className="font-medium">{item.source}</span>
                    <span>•</span>
                    <div className="flex items-center gap-1">
                      <Clock size={12} />
                      {item.time}
                    </div>
                  </div>
                </div>
                <ExternalLink size={16} className="text-[var(--text-muted)] flex-shrink-0 mt-1" />
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
