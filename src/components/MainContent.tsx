import { PriceList } from './PriceList';
import { KLineChart } from './KLineChart';
import { OrderBook } from './OrderBook';
import { ForexPanel } from './ForexPanel';
import { usePriceStore } from '../stores/priceStore';
import { TrendingUp } from 'lucide-react';

interface MainContentProps {
  sidebarOpen: boolean;
  activeTab: string;
}

export function MainContent({ sidebarOpen, activeTab }: MainContentProps) {
  const { tickers, selectedSymbol } = usePriceStore();
  const currentTicker = tickers[selectedSymbol];

  if (activeTab === 'forex') {
    return (
      <main
        className={`
          flex-1 min-h-[calc(100vh-60px)] transition-all duration-300
          ${sidebarOpen ? 'ml-[280px]' : 'ml-0'}
        `}
      >
        <div className="p-4 h-[calc(100vh-60px)]">
          <div className="h-full max-w-4xl mx-auto">
            <ForexPanel />
          </div>
        </div>
      </main>
    );
  }

  return (
    <main
      className={`
        flex-1 min-h-[calc(100vh-60px)] transition-all duration-300
        ${sidebarOpen ? 'ml-[280px]' : 'ml-0'}
      `}
    >
      {/* Price Ticker Bar */}
      <div className="h-10 bg-[var(--bg-secondary)] border-b border-[var(--border-color)] overflow-hidden">
        <div className="flex items-center h-full animate-marquee whitespace-nowrap">
          {Object.values(tickers).slice(0, 10).map((ticker) => {
            const change = parseFloat(ticker.priceChangePercent);
            const isPositive = change >= 0;
            return (
              <div key={ticker.symbol} className="flex items-center gap-2 px-4">
                <span className="font-mono text-sm">{ticker.symbol.replace('USDT', '')}</span>
                <span className="font-mono text-sm">${parseFloat(ticker.price).toFixed(2)}</span>
                <span className={`text-xs ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                  {isPositive ? '+' : ''}{change.toFixed(2)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="p-4 h-[calc(100vh-100px)]">
        {/* Selected Symbol Header */}
        {currentTicker && (
          <div className="flex items-center gap-4 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-sm font-bold text-white">
                {selectedSymbol.replace('USDT', '').slice(0, 2)}
              </div>
              <div>
                <h1 className="font-display text-2xl font-semibold">{selectedSymbol.replace('USDT', '')}/USDT</h1>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xl">${parseFloat(currentTicker.price).toFixed(2)}</span>
                  <span className={`flex items-center gap-1 text-sm ${parseFloat(currentTicker.priceChangePercent) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                    <TrendingUp size={14} className={parseFloat(currentTicker.priceChangePercent) < 0 ? 'rotate-180' : ''} />
                    {parseFloat(currentTicker.priceChangePercent) >= 0 ? '+' : ''}{parseFloat(currentTicker.priceChangePercent).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-4 h-[calc(100%-80px)]">
          {/* Left: Price List */}
          <div className="col-span-3 h-full overflow-auto rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="p-3 border-b border-[var(--border-color)] sticky top-0 bg-[var(--bg-card)] z-10">
              <span className="font-medium">Markets</span>
            </div>
            <PriceList limit={20} />
          </div>

          {/* Center: K-Line Chart */}
          <div className="col-span-6 h-full rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] overflow-hidden">
            <KLineChart />
          </div>

          {/* Right: Order Book */}
          <div className="col-span-3 h-full rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)] overflow-hidden">
            <OrderBook />
          </div>
        </div>
      </div>
    </main>
  );
}
