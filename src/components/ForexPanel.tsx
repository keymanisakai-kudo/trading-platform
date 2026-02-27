import { useEffect, useState } from 'react';
import { RefreshCw } from 'lucide-react';

interface ForexRate {
  currency: string;
  rate: number;
  change: number;
}

const FOREX_PAIRS = [
  { from: 'EUR', to: 'USD', name: 'EUR/USD' },
  { from: 'GBP', to: 'USD', name: 'GBP/USD' },
  { from: 'USD', to: 'JPY', name: 'USD/JPY' },
  { from: 'AUD', to: 'USD', name: 'AUD/USD' },
  { from: 'USD', to: 'CNY', name: 'USD/CNY' },
];

const API_URL = 'https://api.frankfurter.app/latest';

async function fetchForexRates(): Promise<ForexRate[]> {
  const response = await fetch(`${API_URL}?from=USD`);
  const data = await response.json();
  
  return FOREX_PAIRS.map((pair) => {
    let rate: number;
    let change = (Math.random() - 0.5) * 0.01; // Simulate daily change
    
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
    const interval = setInterval(loadRates, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b border-[var(--border-color)] flex items-center justify-between">
        <div>
          <span className="font-medium">Forex Rates</span>
          {lastUpdate && (
            <span className="ml-2 text-xs text-[var(--text-muted)]">
              Updated {lastUpdate.toLocaleTimeString()}
            </span>
          )}
        </div>
        <button
          onClick={loadRates}
          className="p-1.5 rounded hover:bg-[var(--bg-hover)] transition-colors"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Rates List */}
      <div className="flex-1 overflow-auto p-3">
        {loading && rates.length === 0 ? (
          <div className="text-center text-[var(--text-secondary)] py-8">
            Loading forex rates...
          </div>
        ) : (
          <div className="grid gap-2">
            {rates.map((rate) => (
              <div
                key={rate.currency}
                className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]"
              >
                <div>
                  <div className="font-medium font-mono">{rate.currency}</div>
                  <div className="text-xs text-[var(--text-muted)]">Foreign Exchange</div>
                </div>
                <div className="text-right">
                  <div className="font-mono font-medium">{rate.rate.toFixed(4)}</div>
                  <div className={`text-xs ${rate.change >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                    {rate.change >= 0 ? '+' : ''}{rate.change.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
