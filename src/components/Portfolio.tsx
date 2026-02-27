import { useState, useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { ChevronRight, Wallet, Plus, ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react';



// Mock portfolio data
const mockPortfolio = [
  { symbol: 'BTC', name: 'Bitcoin', amount: 0.5, avgPrice: 42000, currentPrice: 0 },
  { symbol: 'ETH', name: 'Ethereum', amount: 5.2, avgPrice: 2200, currentPrice: 0 },
  { symbol: 'BNB', name: 'Binance Coin', amount: 20, avgPrice: 310, currentPrice: 0 },
  { symbol: 'SOL', name: 'Solana', amount: 50, avgPrice: 95, currentPrice: 0 },
  { symbol: 'XRP', name: 'Ripple', amount: 5000, avgPrice: 0.52, currentPrice: 0 },
];

function formatNumber(num: number, decimals = 2): string {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(decimals);
}

interface AssetRowProps {
  asset: typeof mockPortfolio[0];
  currentPrice: number;
}

function AssetRow({ asset, currentPrice }: AssetRowProps) {
  const value = asset.amount * currentPrice;
  const cost = asset.amount * asset.avgPrice;
  const pnl = value - cost;
  const pnlPercent = cost > 0 ? (pnl / cost) * 100 : 0;
  const isPositive = pnl >= 0;

  // Crypto icon colors
  const iconColors: Record<string, string> = {
    BTC: 'from-orange-400 to-orange-600',
    ETH: 'from-purple-400 to-purple-600',
    BNB: 'from-yellow-400 to-yellow-600',
    SOL: 'from-purple-400 to-pink-600',
    XRP: 'from-blue-400 to-blue-600',
  };

  return (
    <div className="flex items-center justify-between p-4 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] mb-2">
      <div className="flex items-center gap-3">
        <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${iconColors[asset.symbol] || 'from-gray-400 to-gray-600'} flex items-center justify-center text-sm font-bold text-white`}>
          {asset.symbol.slice(0, 2)}
        </div>
        <div>
          <div className="font-semibold">{asset.symbol}</div>
          <div className="text-xs text-[var(--text-muted)]">{asset.amount} {asset.symbol}</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="font-mono font-semibold">${formatNumber(value)}</div>
          <div className={`text-xs font-medium flex items-center justify-end gap-1 ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isPositive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {isPositive ? '+' : ''}{pnlPercent.toFixed(2)}%
          </div>
        </div>
        <ChevronRight size={18} className="text-[var(--text-muted)]" />
      </div>
    </div>
  );
}

export function Portfolio() {
  const { tickers, setTickers, setLoading, setError } = usePriceStore();
  const [refreshing, setRefreshing] = useState(false);

  // Update portfolio prices from tickers
  useEffect(() => {
    if (Object.keys(tickers).length === 0) {
      // Load tickers if not loaded
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
    }
  }, []);

  const symbols = Object.keys(tickers).slice(0, 20);
  useBinanceWebSocket(symbols);

  // Update portfolio with current prices
  const portfolioWithPrices = mockPortfolio.map(asset => {
    const ticker = tickers[asset.symbol + 'USDT'];
    return {
      ...asset,
      currentPrice: ticker ? parseFloat(ticker.price) : asset.currentPrice || asset.avgPrice,
    };
  });

  const totalValue = portfolioWithPrices.reduce((acc, a) => acc + a.amount * a.currentPrice, 0);
  const totalCost = portfolioWithPrices.reduce((acc, a) => acc + a.amount * a.avgPrice, 0);
  const totalPnl = totalValue - totalCost;
  const totalPnlPercent = totalCost > 0 ? (totalPnl / totalCost) * 100 : 0;
  const isPositive = totalPnl >= 0;

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  return (
    <div className="pb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <h1 className="font-display text-2xl font-bold">Portfolio</h1>
        <button 
          onClick={handleRefresh}
          className={`p-2 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] ${refreshing ? 'animate-spin' : ''}`}
        >
          <RefreshCw size={18} className="text-[var(--accent-primary)]" />
        </button>
      </div>

      {/* Total Balance Card */}
      <div className="bg-gradient-to-br from-[var(--accent-primary)] to-[var(--success)] rounded-3xl p-5 mb-5 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full -translate-y-1/2 translate-x-1/2" />
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white opacity-10 rounded-full translate-y-1/2 -translate-x-1/2" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Wallet size={18} className="text-black/60" />
            <span className="text-black/60 text-sm">Total Balance</span>
          </div>
          <div className="font-mono text-4xl font-bold text-black mb-2">
            ${formatNumber(totalValue)}
          </div>
          <div className={`flex items-center gap-2 text-sm font-medium ${isPositive ? 'text-black/80' : 'text-red-600'}`}>
            {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            <span>{isPositive ? '+' : ''}${formatNumber(Math.abs(totalPnl))} ({isPositive ? '+' : ''}{totalPnlPercent.toFixed(2)}%)</span>
            <span className="text-black/60">all time</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-3 mb-5">
        <button className="flex-1 flex items-center justify-center gap-2 py-3 bg-[var(--success)] text-black rounded-xl font-semibold">
          <Plus size={18} />
          Deposit
        </button>
        <button className="flex-1 flex items-center justify-center gap-2 py-3 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl font-medium">
          <ArrowUpRight size={18} className="text-[var(--danger)]" />
          Withdraw
        </button>
      </div>

      {/* Assets List */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-[var(--text-muted)]">Your Assets</span>
        <span className="text-xs text-[var(--text-muted)]">{portfolioWithPrices.length} assets</span>
      </div>

      {portfolioWithPrices.map((asset) => (
        <AssetRow 
          key={asset.symbol} 
          asset={asset} 
          currentPrice={asset.currentPrice} 
        />
      ))}

      {/* Empty State / Add More */}
      <button className="w-full flex items-center justify-center gap-2 p-4 mt-2 border-2 border-dashed border-[var(--border-subtle)] rounded-2xl text-[var(--text-muted)] hover:border-[var(--accent-primary)] hover:text-[var(--accent-primary)] transition-colors">
        <Plus size={18} />
        Add more assets
      </button>
    </div>
  );
}
