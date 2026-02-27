import { useEffect, useState } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { ChevronRight } from 'lucide-react';

function formatPrice(price: string): string {
  const p = parseFloat(price);
  if (p >= 1000) return p.toFixed(2);
  if (p >= 1) return p.toFixed(4);
  return p.toFixed(6);
}

interface PriceRowProps {
  ticker: Ticker;
  onClick: () => void;
}

function PriceRow({ ticker, onClick }: PriceRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between p-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] mb-2"
    >
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-sm font-bold text-white">
          {ticker.symbol.replace('USDT', '').slice(0, 2)}
        </div>
        <div className="text-left">
          <div className="font-semibold">{ticker.symbol.replace('USDT', '')}</div>
          <div className="text-xs text-[var(--text-muted)]">USDT</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="font-mono font-semibold">${formatPrice(ticker.price)}</div>
          <div className={`text-xs flex items-center gap-1 justify-end ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
        <ChevronRight size={18} className="text-[var(--text-muted)]" />
      </div>
    </button>
  );
}

export function MobileMarkets() {
  const { tickers, selectedSymbol, setSelectedSymbol, setTickers, setLoading, setError } = usePriceStore();
  const [showChart, setShowChart] = useState(false);
  
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

  const currentTicker = tickers[selectedSymbol];

  if (showChart && currentTicker) {
    return (
      <div className="flex flex-col h-[calc(100vh-140px)]">
        {/* Chart View */}
        <button 
          onClick={() => setShowChart(false)}
          className="mb-2 text-[var(--accent-primary)] text-sm"
        >
          ← Back to list
        </button>
        
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-lg font-bold text-white">
            {selectedSymbol.replace('USDT', '').slice(0, 2)}
          </div>
          <div>
            <h2 className="font-display text-xl font-semibold">{selectedSymbol.replace('USDT', '')}/USDT</h2>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg">${formatPrice(currentTicker.price)}</span>
              <span className={`text-sm ${parseFloat(currentTicker.priceChangePercent) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                {parseFloat(currentTicker.priceChangePercent) >= 0 ? '+' : ''}{parseFloat(currentTicker.priceChangePercent).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        {/* Placeholder for chart - would integrate KLineChart here */}
        <div className="flex-1 bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] flex items-center justify-center">
          <p className="text-[var(--text-secondary)]">Chart coming soon</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-display text-xl font-semibold mb-4">Markets</h1>
      
      {/* Tabs */}
      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
        <button className="px-4 py-2 rounded-full bg-[var(--accent-primary)] text-white text-sm font-medium whitespace-nowrap">
          Crypto
        </button>
        <button className="px-4 py-2 rounded-full bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-secondary)] text-sm font-medium whitespace-nowrap">
          Forex
        </button>
      </div>

      {/* Price List */}
      {tickerList.length === 0 ? (
        <div className="text-center text-[var(--text-secondary)] py-8">
          Loading market data...
        </div>
      ) : (
        tickerList.map((ticker) => (
          <PriceRow
            key={ticker.symbol}
            ticker={ticker}
            onClick={() => {
              setSelectedSymbol(ticker.symbol);
              setShowChart(true);
            }}
          />
        ))
      )}
    </div>
  );
}
