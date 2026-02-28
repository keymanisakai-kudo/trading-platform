import { useState, useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { ChevronRight, Wallet, Plus, ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react';

const mockPortfolio = [
  { symbol: 'BTC', name: 'Bitcoin', amount: 0.5, avgPrice: 42000 },
  { symbol: 'ETH', name: 'Ethereum', amount: 5.2, avgPrice: 2200 },
  { symbol: 'BNB', name: 'Binance', amount: 20, avgPrice: 310 },
  { symbol: 'SOL', name: 'Solana', amount: 50, avgPrice: 95 },
  { symbol: 'XRP', name: 'Ripple', amount: 5000, avgPrice: 0.52 },
];

function formatNumber(num: number): string {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
  return num.toFixed(2);
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

  const iconColors: Record<string, string> = {
    BTC: 'from-orange-400 to-pink-500',
    ETH: 'from-purple-400 to-indigo-600',
    BNB: 'from-yellow-400 to-orange-600',
    SOL: 'from-pink-400 to-rose-600',
    XRP: 'from-blue-400 to-cyan-600',
  };

  return (
    <div className="flex items-center justify-between p-4 clay-card-sm mb-3">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${iconColors[asset.symbol] || 'from-gray-400 to-gray-600'} flex items-center justify-center text-white font-bold shadow-md`}>
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
          <div className={`text-sm flex items-center justify-end gap-1 ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
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

  useEffect(() => {
    if (Object.keys(tickers).length === 0) {
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
    }
  }, []);

  const symbols = Object.keys(tickers).slice(0, 20);
  useBinanceWebSocket(symbols);

  const portfolioWithPrices = mockPortfolio.map(asset => ({
    ...asset,
    currentPrice: parseFloat(tickers[asset.symbol + 'USDT']?.price || asset.avgPrice.toString()),
  }));

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
          className={`w-10 h-10 clay-card-sm flex items-center justify-center ${refreshing ? 'animate-spin' : ''}`}
        >
          <RefreshCw size={18} className="text-[var(--accent-primary)]" />
        </button>
      </div>

      {/* Balance Card */}
      <div className="clay-card p-6 mb-6 relative overflow-hidden">
        <div className="absolute -right-10 -top-10 w-40 h-40 bg-gradient-to-br from-[#ff6b6b] to-[#ffa502] rounded-full opacity-10" />
        
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-2">
            <Wallet size={20} className="text-[var(--accent-primary)]" />
            <span className="text-[var(--text-secondary)]">Total Balance</span>
          </div>
          <div className="font-mono text-4xl font-bold mb-2">
            ${formatNumber(totalValue)}
          </div>
          <div className={`flex items-center gap-2 text-sm ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            <span>{isPositive ? '+' : ''}${formatNumber(Math.abs(totalPnl))} ({isPositive ? '+' : ''}{totalPnlPercent.toFixed(2)}%)</span>
            <span className="text-[var(--text-muted)]">all time</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        <button className="flex-1 clay-btn clay-btn-success flex items-center justify-center gap-2">
          <Plus size={18} />
          Deposit
        </button>
        <button className="flex-1 clay-btn flex items-center justify-center gap-2">
          <ArrowUpRight size={18} className="text-[var(--danger)]" />
          Withdraw
        </button>
      </div>

      {/* Assets */}
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

      <button className="w-full py-4 mt-2 clay-card-sm flex items-center justify-center gap-2 text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors">
        <Plus size={18} />
        Add more assets
      </button>
    </div>
  );
}
