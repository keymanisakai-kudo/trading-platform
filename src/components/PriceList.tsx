import { useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { TrendingUp, TrendingDown } from 'lucide-react';


function formatPrice(price: string): string {
  const p = parseFloat(price);
  if (p >= 1000) return p.toFixed(2);
  if (p >= 1) return p.toFixed(4);
  return p.toFixed(6);
}

interface PriceRowProps {
  ticker: Ticker;
  isSelected: boolean;
  onClick: () => void;
}

function PriceRow({ ticker, isSelected, onClick }: PriceRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;

  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-150
        ${isSelected 
          ? 'bg-[var(--accent-glow)] border border-[var(--accent-primary)]' 
          : 'hover:bg-[var(--bg-hover)] border border-transparent'
        }
      `}
    >
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-xs font-bold text-white">
          {ticker.symbol.replace('USDT', '').slice(0, 2)}
        </div>
        <div className="text-left">
          <div className="font-medium font-mono">{ticker.symbol.replace('USDT', '')}</div>
          <div className="text-xs text-[var(--text-muted)]">USDT</div>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="text-right">
          <div className="font-mono font-medium">${formatPrice(ticker.price)}</div>
          <div className={`text-xs flex items-center gap-1 justify-end ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
      </div>
    </button>
  );
}

interface PriceListProps {
  limit?: number;
}

export function PriceList({ limit = 20 }: PriceListProps) {
  const { tickers, selectedSymbol, setSelectedSymbol, setTickers, setLoading, setError } = usePriceStore();

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
  const symbols = Object.keys(tickers).slice(0, limit);
  useBinanceWebSocket(symbols);

  const tickerList = Object.values(tickers)
    .sort((a, b) => parseFloat(b.quoteVolume) - parseFloat(a.quoteVolume))
    .slice(0, limit);

  if (tickerList.length === 0) {
    return (
      <div className="p-4 text-center text-[var(--text-secondary)]">
        Loading market data...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      {tickerList.map((ticker) => (
        <PriceRow
          key={ticker.symbol}
          ticker={ticker}
          isSelected={selectedSymbol === ticker.symbol}
          onClick={() => setSelectedSymbol(ticker.symbol)}
        />
      ))}
    </div>
  );
}
