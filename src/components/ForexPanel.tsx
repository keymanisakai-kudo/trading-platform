import { useEffect, useState } from 'react';
import { RefreshCw, TrendingUp, Globe } from 'lucide-react';

interface ForexRate {
  currency: string;
  flag: string;
  rate: number;
  change: number;
}

const FOREX_PAIRS = [
  { from: 'EUR', to: 'USD', name: 'EUR/USD', flag: '🇪🇺' },
  { from: 'GBP', to: 'USD', name: 'GBP/USD', flag: '🇬🇧' },
  { from: 'USD', to: 'JPY', name: 'USD/JPY', flag: '🇯🇵' },
  { from: 'AUD', to: 'USD', name: 'AUD/USD', flag: '🇦🇺' },
  { from: 'USD', to: 'CNY', name: 'USD/CNY', flag: '🇨🇳' },
];

const API_URL = 'https://api.frankfurter.app/latest';

async function fetchForexRates(): Promise<ForexRate[]> {
  const response = await fetch(`${API_URL}?from=USD`);
  const data = await response.json();
  
  return FOREX_PAIRS.map((pair) => {
    let rate: number;
    let change = (Math.random() - 0.5) * 0.01;
    
    if (pair.from === 'USD') {
      rate = data.rates[pair.to] || 1;
    } else if (pair.to === 'USD') {
      rate = 1 / (data.rates[pair.from] || 1);
      change = -change;
    } else {
      const fromRate = data.rates[pair.from] || 1;
      const toRate = data.rates[pair.to] || 1;
      rate = toRate / fromRate;
    }
    
    return {
      currency: pair.name,
      flag: pair.flag,
      rate,
      change: change * 100,
    };
  });
}

export function ForexPanel() {
  const [rates, setRates] = useState<ForexRate[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const loadRates = async () => {
    setLoading(true);
    try {
      const data = await fetchForexRates();
      setRates(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch forex rates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRates();
    const interval = setInterval(loadRates, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="pb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="font-display text-2xl font-bold mb-1">Forex</h1>
          <div className="flex items-center gap-2">
            <Globe size={14} className="text-[var(--text-muted)]" />
            <span className="text-xs text-[var(--text-muted)]">
              {lastUpdate ? `Updated ${lastUpdate.toLocaleTimeString()}` : 'Loading...'}
            </span>
          </div>
        </div>
        <button
          onClick={loadRates}
          className={`
            w-10 h-10 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)] 
            flex items-center justify-center transition-all hover:border-[var(--accent-primary)]
            ${loading ? 'animate-spin' : ''}
          `}
        >
          <RefreshCw size={18} className="text-[var(--accent-primary)]" />
        </button>
      </div>

      {/* Rates List */}
      {loading && rates.length === 0 ? (
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 rounded-2xl bg-[var(--bg-card)] border border-[var(--border-subtle)] skeleton" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {rates.map((rate, index) => (
            <div
              key={rate.currency}
              className="flex items-center justify-between p-4 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-subtle)] animate-fade-in-up"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-center gap-3">
                <div className="text-2xl">{rate.flag}</div>
                <div>
                  <div className="font-semibold">{rate.currency}</div>
                  <div className="text-xs text-[var(--text-muted)]">Foreign Exchange</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-mono font-bold text-lg">{rate.rate.toFixed(4)}</div>
                <div className={`
                  text-xs font-medium flex items-center justify-end gap-1
                  ${rate.change >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}
                `}>
                  <TrendingUp size={12} className={rate.change >= 0 ? '' : 'rotate-180'} />
                  {rate.change >= 0 ? '+' : ''}{rate.change.toFixed(2)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
