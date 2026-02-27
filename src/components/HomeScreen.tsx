import { useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { TrendingUp, TrendingDown, Flame, Sparkles, Bitcoin, Search, Bell, ArrowUpRight, ArrowDownRight } from 'lucide-react';

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

const featuredTokens = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'PEPE'];

interface TokenCardProps {
  ticker: Ticker;
}

function TokenCard({ ticker }: TokenCardProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  const gradients: Record<string, string> = {
    BTC: 'from-orange-400 to-pink-500',
    ETH: 'from-purple-400 to-indigo-600',
    SOL: 'from-pink-400 to-rose-600',
    BNB: 'from-yellow-400 to-orange-600',
    XRP: 'from-blue-400 to-cyan-600',
    PEPE: 'from-green-400 to-emerald-600',
  };

  return (
    <div className="flex-shrink-0 w-32 p-4 clay-card-sm flex flex-col items-center gap-3">
      <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${gradients[symbol] || 'from-gray-400 to-gray-600'} flex items-center justify-center text-white font-bold shadow-lg`}>
        {symbol.slice(0, 2)}
      </div>
      <div className="text-center">
        <div className="font-semibold">{symbol}</div>
        <div className={`text-sm font-mono ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
          {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
        </div>
      </div>
    </div>
  );
}

interface MarketRowProps {
  ticker: Ticker;
}

function MarketRow({ ticker }: MarketRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  return (
    <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)] last:border-0">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-sm font-bold text-gray-600">
          {symbol.slice(0, 2)}
        </div>
        <div>
          <div className="font-medium">{symbol}</div>
          <div className="text-xs text-[var(--text-muted)]">${formatVolume(ticker.quoteVolume)}</div>
        </div>
      </div>
      <div className="text-right">
        <div className="font-mono font-medium">${formatPrice(ticker.price)}</div>
        <div className={`text-sm flex items-center justify-end gap-1 ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
          {isPositive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
          {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
        </div>
      </div>
    </div>
  );
}

interface HomeScreenProps {
  onNavigate: (tab: string) => void;
}

export function HomeScreen({ }: HomeScreenProps) {
  const { tickers, setTickers, setLoading, setError } = usePriceStore();
  
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchTickers();
        setTickers(data);
        setError(null);
      } catch (err) {
        setError('Failed');
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

  const featuredTickers = featuredTokens
    .map(symbol => tickerList.find(t => t.symbol === `${symbol}USDT`))
    .filter(Boolean) as Ticker[];

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
      {/* Search */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex-1 clay-inset flex items-center gap-3 px-4 py-3">
          <Search size={20} className="text-[var(--text-muted)]" />
          <input 
            type="text" 
            placeholder="Search tokens..." 
            className="flex-1 bg-transparent text-sm outline-none"
          />
        </div>
        <button className="w-12 h-12 clay-card-sm flex items-center justify-center">
          <Bell size={20} className="text-[var(--text-secondary)]" />
        </button>
      </div>

      {/* Featured */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={18} className="text-[var(--accent-primary)]" />
          <span className="font-semibold">Featured</span>
        </div>
        <div className="flex gap-4 overflow-x-auto scrollbar-hide pb-2 -mx-4 px-4">
          {featuredTickers.map((ticker) => (
            <TokenCard key={ticker.symbol} ticker={ticker} />
          ))}
        </div>
      </div>

      {/* Crypto Card */}
      <div className="clay-card p-5 mb-6 relative overflow-hidden">
        <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-[#ff6b6b] to-[#ffa502] rounded-full opacity-20" />
        <div className="absolute -left-4 -bottom-4 w-20 h-20 bg-gradient-to-br from-[#ffa502] to-[#ff6b6b] rounded-full opacity-20" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-3">
            <Bitcoin size={24} className="text-[#ff6b6b]" />
            <span className="font-semibold">Crypto Card</span>
          </div>
          <div className="text-3xl font-bold font-mono mb-1">5%</div>
          <div className="text-sm text-[var(--text-secondary)] mb-4">USDT rebate on every trade</div>
          <button className="clay-btn text-sm py-2 px-4">
            Learn More →
          </button>
        </div>
      </div>

      {/* Gainers */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp size={18} className="text-[var(--success)]" />
            <span className="font-semibold">Top Gainers</span>
          </div>
        </div>
        <div className="clay-card overflow-hidden">
          {gainers.map((ticker) => (
            <MarketRow key={ticker.symbol} ticker={ticker} />
          ))}
        </div>
      </div>

      {/* Losers */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingDown size={18} className="text-[var(--danger)]" />
            <span className="font-semibold">Top Losers</span>
          </div>
        </div>
        <div className="clay-card overflow-hidden">
          {losers.map((ticker) => (
            <MarketRow key={ticker.symbol} ticker={ticker} />
          ))}
        </div>
      </div>

      {/* Popular */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Flame size={18} className="text-[var(--warning)]" />
          <span className="font-semibold">Popular</span>
        </div>
        <div className="clay-card overflow-hidden">
          {tickerList.slice(0, 10).map((ticker) => (
            <MarketRow key={ticker.symbol} ticker={ticker} />
          ))}
        </div>
      </div>
    </div>
  );
}
