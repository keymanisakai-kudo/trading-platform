import { useEffect, useState } from 'react';
import { usePriceStore } from '../stores/priceStore';

interface OrderBookLevel {
  price: string;
  quantity: string;
  total: number;
}

interface OrderBookData {
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  spread: number;
  spreadPercent: number;
}

async function fetchOrderBook(symbol: string): Promise<OrderBookData> {
  const response = await fetch(
    `https://api.binance.com/api/v3/depth?symbol=${symbol}&limit=20`
  );
  const data = await response.json();

  let bidTotal = 0;
  const bids = data.bids.map(([price, qty]: [string, string]) => {
    bidTotal += parseFloat(qty);
    return { price, quantity: qty, total: bidTotal };
  });

  let askTotal = 0;
  const asks = data.asks.map(([price, qty]: [string, string]) => {
    askTotal += parseFloat(qty);
    return { price, quantity: qty, total: askTotal };
  });

  const bestBid = parseFloat(bids[0]?.price || '0');
  const bestAsk = parseFloat(asks[0]?.price || '0');
  const spread = bestAsk - bestBid;
  const spreadPercent = bestBid > 0 ? (spread / bestBid) * 100 : 0;

  return { bids, asks, spread, spreadPercent };
}

function formatNumber(num: string | number, decimals = 4): string {
  const n = parseFloat(num as string);
  return n.toFixed(decimals);
}

export function OrderBook() {
  const { selectedSymbol } = usePriceStore();
  const [orderBook, setOrderBook] = useState<OrderBookData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadOrderBook = async () => {
      setLoading(true);
      try {
        const data = await fetchOrderBook(selectedSymbol);
        setOrderBook(data);
      } catch (error) {
        console.error('Failed to load order book:', error);
      } finally {
        setLoading(false);
      }
    };

    loadOrderBook();
    const interval = setInterval(loadOrderBook, 2000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  if (loading || !orderBook) {
    return (
      <div className="h-full flex items-center justify-center text-[var(--text-secondary)]">
        Loading order book...
      </div>
    );
  }

  const maxTotal = Math.max(
    orderBook.bids[orderBook.bids.length - 1]?.total || 0,
    orderBook.asks[orderBook.asks.length - 1]?.total || 0
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-[var(--border-color)]">
        <div className="flex items-center justify-between">
          <span className="font-medium">Order Book</span>
          <span className="text-xs text-[var(--text-muted)]">
            Spread: {orderBook.spread.toFixed(2)} ({orderBook.spreadPercent.toFixed(3)}%)
          </span>
        </div>
      </div>

      {/* Column Headers */}
      <div className="grid grid-cols-3 gap-2 px-3 py-2 text-xs text-[var(--text-muted)] border-b border-[var(--border-color)]">
        <span>Price (USDT)</span>
        <span className="text-right">Amount</span>
        <span className="text-right">Total</span>
      </div>

      {/* Asks (Sells) - reversed to show highest at top */}
      <div className="flex-1 overflow-hidden flex flex-col justify-end">
        {orderBook.asks.slice(0, 10).reverse().map((ask, i) => (
          <div key={`ask-${i}`} className="grid grid-cols-3 gap-2 px-3 py-1 text-xs relative">
            <div 
              className="absolute inset-0 bg-[var(--danger-bg)]"
              style={{ width: `${(ask.total / maxTotal) * 100}%`, right: 0, left: 'auto' }}
            />
            <span className="text-[var(--danger)] font-mono relative z-10">{formatNumber(ask.price)}</span>
            <span className="text-right font-mono relative z-10">{formatNumber(ask.quantity)}</span>
            <span className="text-right text-[var(--text-muted)] font-mono relative z-10">{formatNumber(ask.total)}</span>
          </div>
        ))}
      </div>

      {/* Spread Indicator */}
      <div className="px-3 py-2 bg-[var(--bg-hover)] border-y border-[var(--border-color)]">
        <div className="text-center font-mono font-medium text-[var(--accent-primary)]">
          {formatNumber(orderBook.bids[0]?.price || 0)}
        </div>
      </div>

      {/* Bids (Buys) */}
      <div className="flex-1 overflow-hidden">
        {orderBook.bids.slice(0, 10).map((bid, i) => (
          <div key={`bid-${i}`} className="grid grid-cols-3 gap-2 px-3 py-1 text-xs relative">
            <div 
              className="absolute inset-0 bg-[var(--success-bg)]"
              style={{ width: `${(bid.total / maxTotal) * 100}%` }}
            />
            <span className="text-[var(--success)] font-mono relative z-10">{formatNumber(bid.price)}</span>
            <span className="text-right font-mono relative z-10">{formatNumber(bid.quantity)}</span>
            <span className="text-right text-[var(--text-muted)] font-mono relative z-10">{formatNumber(bid.total)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
