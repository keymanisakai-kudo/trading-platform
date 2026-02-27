import { useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { TrendingUp, TrendingDown, Flame, Sparkles, Bitcoin, Search, Bell } from 'lucide-react';

function formatPrice(price: string): string {
  const p = parseFloat(price);
  if (p >= 1000) return p.toFixed(2);
  if (p >= 1) return p.toFixed(4);
  return p.toFixed(6);
}

function formatVolume(volume: string): string {
  const v = parseFloat(volume);
  if (v >= 1e9) return (v / 1e9).toFixed(1) + 'B';
  if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
  return (v / 1e3).toFixed(1) + 'K';
}


// Featured tokens for Home screen
const featuredTokens = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'PEPE'];

interface TokenCardProps {
  ticker: Ticker;
  onClick: () => void;
}

function TokenCard({ ticker, onClick }: TokenCardProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  // Different gradient for featured tokens
  const gradients: Record<string, string> = {
    BTC: 'from-orange-400 to-orange-600',
    ETH: 'from-purple-400 to-purple-600',
    SOL: 'from-purple-400 to-pink-500',
    BNB: 'from-yellow-400 to-yellow-600',
    XRP: 'from-blue-400 to-blue-600',
    PEPE: 'from-green-400 to-green-600',
  };

  return (
    <button
      onClick={onClick}
      className="flex-shrink-0 w-28 p-3 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] flex flex-col items-center gap-2"
    >
      <div className={`w-10 h-10 rounded-full bg-gradient-to-br ${gradients[symbol] || 'from-gray-400 to-gray-600'} flex items-center justify-center text-white font-bold text-sm`}>
        {symbol.slice(0, 2)}
      </div>
      <div className="font-semibold text-sm">{symbol}</div>
      <div className={`text-xs font-mono ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
        {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
      </div>
    </button>
  );
}

interface MarketRowProps {
  ticker: Ticker;
  onClick: () => void;
}

function MarketRow({ ticker, onClick }: MarketRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  return (
    <button
      onClick={onClick}
      className="flex items-center justify-between py-3 border-b border-[var(--border-subtle)]"
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-[var(--bg-elevated)] flex items-center justify-center text-xs font-bold">
          {symbol.slice(0, 2)}
        </div>
        <div>
          <div className="font-medium text-sm">{symbol}/USDT</div>
          <div className="text-xs text-[var(--text-muted)]">Vol: ${formatVolume(ticker.quoteVolume)}</div>
        </div>
      </div>
      <div className="text-right">
        <div className="font-mono text-sm">${formatPrice(ticker.price)}</div>
        <div className={`text-xs font-medium ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
          {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
        </div>
      </div>
    </button>
  );
}

interface HomeScreenProps {
  onNavigate: (tab: string) => void;
}

export function HomeScreen({ onNavigate }: HomeScreenProps) {
  const { tickers, setTickers, setLoading, setError } = usePriceStore();
  
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchTickers();
        setTickers(data);
        setError(null);
      } catch (err) {
        setError('Failed to load');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const symbols = Object.keys(tickers).slice(0, 20);
  useBinanceWebSocket(symbols);

  const tickerList = Object.values(tickers)
    .sort((a, b) => parseFloat(b.quoteVolume) - parseFloat(a.quoteVolume))
    .slice(0, 30);

  // Get featured tickers
  const featuredTickers = featuredTokens
    .map(symbol => tickerList.find(t => t.symbol === `${symbol}USDT`))
    .filter(Boolean) as Ticker[];

  // Top gainers and losers
  const gainers = [...tickerList]
    .filter(t => parseFloat(t.priceChangePercent) > 0)
    .sort((a, b) => parseFloat(b.priceChangePercent) - parseFloat(a.priceChangePercent))
    .slice(0, 5);

  const losers = [...tickerList]
    .filter(t => parseFloat(t.priceChangePercent) < 0)
    .sort((a, b) => parseFloat(a.priceChangePercent) - parseFloat(b.priceChangePercent))
    .slice(0, 5);

  return (
    <div className="pb-4">
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex-1 flex items-center gap-2 px-3 py-2.5 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)]">
          <Search size={18} className="text-[var(--text-muted)]" />
          <input 
            type="text" 
            placeholder="Search tokens..." 
            className="flex-1 bg-transparent text-sm focus:outline-none"
          />
        </div>
        <button className="ml-2 p-2.5 bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)]">
          <Bell size={20} className="text-[var(--text-secondary)]" />
        </button>
      </div>

      {/* Crypto Card Banner */}
      <div className="bg-gradient-to-r from-[var(--accent-primary)] to-[#00ffa3] rounded-2xl p-4 mb-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-white opacity-10 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-1">
            <Bitcoin size={20} className="text-black" />
            <span className="text-black/70 text-sm font-medium">Crypto Card</span>
          </div>
          <div className="text-black text-xs mb-2">Get 5% USDT rebate</div>
          <button className="px-3 py-1.5 bg-black text-white text-xs font-medium rounded-lg">
            Learn More →
          </button>
        </div>
      </div>

      {/* Featured Tokens */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={16} className="text-[var(--accent-primary)]" />
          <span className="font-semibold">Featured</span>
        </div>
        <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4">
          {featuredTickers.map((ticker) => (
            <TokenCard 
              key={ticker.symbol} 
              ticker={ticker} 
              onClick={() => onNavigate('trade')}
            />
          ))}
        </div>
      </div>

      {/* Top Gainers */}
      <div className="mb-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <TrendingUp size={16} className="text-[var(--success)]" />
            <span className="font-semibold">Top Gainers</span>
          </div>
          <button 
            onClick={() => onNavigate('markets')}
            className="text-xs text-[var(--accent-primary)]"
          >
            See All →
          </button>
        </div>
        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] overflow-hidden">
          {gainers.map((ticker) => (
            <MarketRow 
              key={ticker.symbol} 
              ticker={ticker} 
              onClick={() => onNavigate('trade')}
            />
          ))}
        </div>
      </div>

      {/* Top Losers */}
      <div className="mb-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <TrendingDown size={16} className="text-[var(--danger)]" />
            <span className="font-semibold">Top Losers</span>
          </div>
        </div>
        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] overflow-hidden">
          {losers.map((ticker) => (
            <MarketRow 
              key={ticker.symbol} 
              ticker={ticker} 
              onClick={() => onNavigate('trade')}
            />
          ))}
        </div>
      </div>

      {/* Popular Pairs */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Flame size={16} className="text-[var(--warning)]" />
          <span className="font-semibold">Popular</span>
        </div>
        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] overflow-hidden">
          {tickerList.slice(0, 10).map((ticker) => (
            <MarketRow 
              key={ticker.symbol} 
              ticker={ticker} 
              onClick={() => onNavigate('trade')}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
