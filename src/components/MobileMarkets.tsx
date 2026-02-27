import { useEffect, useState } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { ChevronRight, Activity, TrendingUp, Zap } from 'lucide-react';

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
  if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
  return v.toFixed(0);
}

interface PriceRowProps {
  ticker: Ticker;
  index: number;
  onClick: () => void;
}

function PriceRow({ ticker, index, onClick }: PriceRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center justify-between p-4 
        bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)]
        mb-2 transition-all duration-200 animate-fade-in-up
        hover:border-[var(--border-active)] hover:translate-y-[-2px]
        active:scale-[0.99]
      `}
      style={{ animationDelay: `${index * 0.03}s` }}
    >
      <div className="flex items-center gap-3">
        {/* Crypto Icon */}
        <div className={`
          w-11 h-11 rounded-xl flex items-center justify-center text-sm font-bold
          ${['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX'].includes(symbol) 
            ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white' 
            : 'bg-[var(--bg-elevated)] text-[var(--text-secondary)] border border-[var(--border-subtle)]'
          }
        `}>
          {symbol.slice(0, 2)}
        </div>
        
        <div className="text-left">
          <div className="font-semibold text-[var(--text-primary)]">{symbol}</div>
          <div className="text-xs text-[var(--text-muted)]">Vol: ${formatVolume(ticker.quoteVolume)}</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="font-mono font-semibold text-[var(--text-primary)]">${formatPrice(ticker.price)}</div>
          <div className={`
            text-xs font-medium flex items-center justify-end gap-1
            ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}
          `}>
            <TrendingUp size={12} className={isPositive ? '' : 'rotate-180'} />
            {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
        <ChevronRight size={18} className="text-[var(--text-muted)]" />
      </div>
    </button>
  );
}

export function MobileMarkets() {
  const { tickers, setTickers, setLoading, setError } = usePriceStore();
  const [activeCategory, setActiveCategory] = useState('all');
  
  // Fetch initial data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchTickers();
        setTickers(data);
        setError(null);
      } catch (err) {
        setError('Failed to load market data');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Connect to WebSocket for real-time updates
  const symbols = Object.keys(tickers).slice(0, 20);
  useBinanceWebSocket(symbols);

  const tickerList = Object.values(tickers)
    .sort((a, b) => parseFloat(b.quoteVolume) - parseFloat(a.quoteVolume))
    .slice(0, 20);

  const categories = [
    { id: 'all', label: 'All' },
    { id: 'favorites', label: 'Favorites' },
    { id: 'gainers', label: 'Gainers' },
    { id: 'losers', label: 'Losers' },
  ];

  const filteredList = tickerList.filter((ticker) => {
    if (activeCategory === 'gainers') return parseFloat(ticker.priceChangePercent) > 0;
    if (activeCategory === 'losers') return parseFloat(ticker.priceChangePercent) < 0;
    return true;
  });

  // Calculate market stats
  const totalVolume = tickerList.reduce((acc, t) => acc + parseFloat(t.quoteVolume), 0);
  const gainers = tickerList.filter(t => parseFloat(t.priceChangePercent) > 0).length;

  return (
    <div className="pb-4">
      {/* Header Stats */}
      <div className="mb-5">
        <h1 className="font-display text-2xl font-bold mb-4">Markets</h1>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-3 mb-5">
          <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Activity size={14} className="text-[var(--accent-primary)]" />
              <span className="text-xs text-[var(--text-muted)]">Assets</span>
            </div>
            <div className="font-mono font-bold text-lg">{tickerList.length}</div>
          </div>
          
          <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <TrendingUp size={14} className="text-[var(--success)]" />
              <span className="text-xs text-[var(--text-muted)]">Gainers</span>
            </div>
            <div className="font-mono font-bold text-lg text-[var(--success)]">{gainers}</div>
          </div>
          
          <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-subtle)] p-3">
            <div className="flex items-center gap-1.5 mb-1">
              <Zap size={14} className="text-[var(--warning)]" />
              <span className="text-xs text-[var(--text-muted)]">24h Vol</span>
            </div>
            <div className="font-mono font-bold text-lg">${formatVolume(totalVolume.toString())}</div>
          </div>
        </div>
        
        {/* Category Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              className={`
                px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200
                ${activeCategory === cat.id 
                  ? 'bg-[var(--accent-primary)] text-black shadow-[0_0_20px_var(--accent-glow)]' 
                  : 'bg-[var(--bg-card)] border border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--border-active)]'
                }
              `}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Price List */}
      {filteredList.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-subtle)] flex items-center justify-center">
            <Activity size={32} className="text-[var(--text-muted)]" />
          </div>
          <p className="text-[var(--text-secondary)]">Loading market data...</p>
        </div>
      ) : (
        filteredList.map((ticker, index) => (
          <PriceRow
            key={ticker.symbol}
            ticker={ticker}
            index={index}
            onClick={() => console.log('Selected:', ticker.symbol)}
          />
        ))
      )}
    </div>
  );
}
