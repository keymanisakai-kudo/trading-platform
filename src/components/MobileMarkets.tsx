import { useState, useEffect } from 'react';
import { usePriceStore, fetchTickers } from '../stores/priceStore';
import type { Ticker } from '../stores/priceStore';
import { useBinanceWebSocket } from '../hooks/useBinanceWebSocket';
import { ChevronRight, TrendingUp, Zap, Clock, ArrowLeft } from 'lucide-react';
import { MiniChart } from './MiniChart';

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

interface PriceRowProps {
  ticker: Ticker;
  onClick: () => void;
}

function PriceRow({ ticker, onClick }: PriceRowProps) {
  const priceChange = parseFloat(ticker.priceChangePercent);
  const isPositive = priceChange >= 0;
  const symbol = ticker.symbol.replace('USDT', '');

  return (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between p-4 clay-card-sm mb-3 transition-all hover:scale-[1.02]"
    >
      <div className="flex items-center gap-3">
        <div className={`
          w-12 h-12 rounded-2xl flex items-center justify-center text-sm font-bold shadow-md
          ${['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX'].includes(symbol) 
            ? 'bg-gradient-to-br from-orange-400 to-pink-500 text-white' 
            : 'bg-gray-100 text-gray-600'
          }
        `}>
          {symbol.slice(0, 2)}
        </div>
        <div className="text-left">
          <div className="font-semibold">{symbol}</div>
          <div className="text-xs text-[var(--text-muted)]">${formatVolume(ticker.quoteVolume)}</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="font-mono font-semibold">${formatPrice(ticker.price)}</div>
          <div className={`text-sm flex items-center justify-end gap-1 ${isPositive ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            <TrendingUp size={12} className={isPositive ? '' : 'rotate-180'} />
            {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
        <ChevronRight size={18} className="text-[var(--text-muted)]" />
      </div>
    </button>
  );
}

// Trade Screen
interface TradeScreenProps {
  ticker: Ticker | null;
  onBack: () => void;
}

function TradeScreen({ ticker, onBack }: TradeScreenProps) {
  const [orderType, setOrderType] = useState<'market' | 'limit'>('limit');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [price, setPrice] = useState('');
  const [amount, setAmount] = useState('');
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    if (ticker) {
      setPrice(formatPrice(ticker.price));
    }
  }, [ticker]);

  if (!ticker) return null;

  const symbol = ticker.symbol.replace('USDT', '');
  const currentPrice = parseFloat(ticker.price);
  const orderPrice = orderType === 'market' ? currentPrice : parseFloat(price || '0');
  const orderAmount = parseFloat(amount || '0');
  const total = orderPrice * orderAmount;
  const available = 10000;

  return (
    <div className="animate-fade-in-up">
      <button onClick={onBack} className="flex items-center gap-2 text-[var(--accent-primary)] mb-4">
        <ArrowLeft size={18} />
        Back
      </button>

      {/* Token Info */}
      <div className="clay-card p-5 mb-5">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-orange-400 to-pink-500 flex items-center justify-center text-xl font-bold text-white shadow-lg">
            {symbol.slice(0, 2)}
          </div>
          <div>
            <h2 className="font-display text-xl font-bold">{symbol}/USDT</h2>
            <div className="flex items-center gap-2">
              <span className="font-mono text-lg">${formatPrice(ticker.price)}</span>
              <span className={`text-sm ${parseFloat(ticker.priceChangePercent) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                {parseFloat(ticker.priceChangePercent) >= 0 ? '+' : ''}{parseFloat(ticker.priceChangePercent).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>

        {/* Mini Chart */}
        <div className="h-[160px] rounded-xl overflow-hidden">
          <MiniChart symbol={ticker.symbol} />
        </div>
      </div>

      {/* Buy/Sell */}
      <div className="flex gap-3 mb-5">
        <button
          onClick={() => setSide('buy')}
          className={`flex-1 py-4 rounded-2xl font-semibold text-lg transition-all shadow-lg ${
            side === 'buy' 
              ? 'bg-[var(--success)] text-white' 
              : 'clay-card-sm text-[var(--text-secondary)]'
          }`}
        >
          Buy
        </button>
        <button
          onClick={() => setSide('sell')}
          className={`flex-1 py-4 rounded-2xl font-semibold text-lg transition-all shadow-lg ${
            side === 'sell' 
              ? 'bg-[var(--danger)] text-white' 
              : 'clay-card-sm text-[var(--text-secondary)]'
          }`}
        >
          Sell
        </button>
      </div>

      {/* Order Type */}
      <div className="flex gap-2 mb-5">
        <button
          onClick={() => setOrderType('limit')}
          className={`flex-1 py-3 rounded-xl font-medium transition-all ${
            orderType === 'limit' 
              ? 'bg-[var(--accent-subtle)] text-[var(--accent-primary)]' 
              : 'clay-inset text-[var(--text-secondary)]'
          }`}
        >
          <Zap size={14} className="inline mr-1" />
          Limit
        </button>
        <button
          onClick={() => setOrderType('market')}
          className={`flex-1 py-3 rounded-xl font-medium transition-all ${
            orderType === 'market' 
              ? 'bg-[var(--accent-subtle)] text-[var(--accent-primary)]' 
              : 'clay-inset text-[var(--text-secondary)]'
          }`}
        >
          <Clock size={14} className="inline mr-1" />
          Market
        </button>
      </div>

      {/* Form */}
      <div className="clay-card p-5 mb-5">
        {orderType === 'limit' && (
          <div className="mb-5">
            <label className="block text-sm text-[var(--text-muted)] mb-2">Price (USDT)</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="0.00"
              className="clay-input font-mono"
            />
          </div>
        )}

        <div className="mb-5">
          <label className="block text-sm text-[var(--text-muted)] mb-2">Amount ({symbol})</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            className="clay-input font-mono"
          />
        </div>

        <div className="flex justify-between py-3 border-t border-[var(--border-subtle)]">
          <span className="text-[var(--text-muted)]">Total</span>
          <span className="font-mono font-semibold">{total.toFixed(2)} USDT</span>
        </div>

        <div className="flex justify-between">
          <span className="text-[var(--text-muted)]">Available</span>
          <span className="font-mono text-[var(--text-secondary)]">{available.toFixed(2)} USDT</span>
        </div>
      </div>

      <button
        onClick={() => setShowConfirm(true)}
        disabled={!amount || total <= 0}
        className={`w-full py-4 rounded-2xl font-semibold text-lg transition-all shadow-lg ${
          side === 'buy' ? 'bg-[var(--success)] text-white' : 'bg-[var(--danger)] text-white'
        } disabled:opacity-50 disabled:cursor-not-allowed`}
      >
        {side === 'buy' ? 'Buy' : 'Sell'} {symbol}
      </button>

      {/* Confirm Modal */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-end justify-center z-50">
          <div className="clay-card w-full rounded-t-3xl p-6 animate-fade-in-up">
            <h3 className="font-bold text-xl mb-5">Confirm Order</h3>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between">
                <span className="text-[var(--text-muted)]">Type</span>
                <span className="capitalize">{orderType}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-muted)]">Side</span>
                <span className={side === 'buy' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}>
                  {side.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-muted)]">Price</span>
                <span className="font-mono">{orderPrice.toFixed(4)} USDT</span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--text-muted)]">Amount</span>
                <span className="font-mono">{orderAmount} {symbol}</span>
              </div>
              <div className="flex justify-between font-bold pt-3 border-t border-[var(--border-subtle)]">
                <span>Total</span>
                <span className="font-mono">{total.toFixed(2)} USDT</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowConfirm(false)}
                className="flex-1 py-3 rounded-xl clay-inset font-medium"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowConfirm(false);
                  setAmount('');
                  alert(`${side === 'buy' ? 'Buy' : 'Sell'} order placed!`);
                }}
                className={`flex-1 py-3 rounded-xl font-semibold text-white ${
                  side === 'buy' ? 'bg-[var(--success)]' : 'bg-[var(--danger)]'
                }`}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function MobileMarkets() {
  const { tickers, setTickers, setLoading, setError } = usePriceStore();
  const [selectedTicker, setSelectedTicker] = useState<Ticker | null>(null);
  
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
    .slice(0, 20);

  if (selectedTicker) {
    return (
      <TradeScreen 
        ticker={tickers[selectedTicker.symbol] || selectedTicker} 
        onBack={() => setSelectedTicker(null)} 
      />
    );
  }

  return (
    <div className="pb-4">
      <h1 className="font-display text-2xl font-bold mb-5">Markets</h1>
      
      <div className="grid grid-cols-3 gap-3 mb-5">
        <div className="clay-card-sm p-3 text-center">
          <div className="text-xs text-[var(--text-muted)] mb-1">Assets</div>
          <div className="font-mono font-bold text-lg">{tickerList.length}</div>
        </div>
        <div className="clay-card-sm p-3 text-center">
          <div className="text-xs text-[var(--text-muted)] mb-1">Gainers</div>
          <div className="font-mono font-bold text-lg text-[var(--success)]">
            {tickerList.filter(t => parseFloat(t.priceChangePercent) > 0).length}
          </div>
        </div>
        <div className="clay-card-sm p-3 text-center">
          <div className="text-xs text-[var(--text-muted)] mb-1">24h Vol</div>
          <div className="font-mono font-bold text-lg">
            ${formatVolume(tickerList.reduce((acc, t) => acc + parseFloat(t.quoteVolume), 0).toString())}
          </div>
        </div>
      </div>

      {tickerList.length === 0 ? (
        <div className="text-center py-12 text-[var(--text-secondary)]">Loading...</div>
      ) : (
        tickerList.map((ticker) => (
          <PriceRow
            key={ticker.symbol}
            ticker={ticker}
            onClick={() => setSelectedTicker(ticker)}
          />
        ))
      )}
    </div>
  );
}
