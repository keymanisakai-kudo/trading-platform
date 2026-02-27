import { create } from 'zustand';

export interface Ticker {
  symbol: string;
  price: string;
  priceChange: string;
  priceChangePercent: string;
  high: string;
  low: string;
  volume: string;
  quoteVolume: string;
  lastUpdate: number;
}

interface PriceStore {
  tickers: Record<string, Ticker>;
  selectedSymbol: string;
  loading: boolean;
  error: string | null;
  
  setTickers: (tickers: Record<string, Ticker>) => void;
  updateTicker: (symbol: string, ticker: Partial<Ticker>) => void;
  setSelectedSymbol: (symbol: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const usePriceStore = create<PriceStore>((set) => ({
  tickers: {},
  selectedSymbol: 'BTCUSDT',
  loading: false,
  error: null,
  
  setTickers: (tickers) => set({ tickers }),
  
  updateTicker: (symbol, ticker) => set((state) => ({
    tickers: {
      ...state.tickers,
      [symbol]: {
        ...state.tickers[symbol],
        ...ticker,
        lastUpdate: Date.now(),
      } as Ticker,
    },
  })),
  
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));

// Fetch initial ticker data from Binance
export async function fetchTickers(): Promise<Record<string, Ticker>> {
  try {
    const response = await fetch('https://api.binance.com/api/v3/ticker/24hr');
    if (!response.ok) throw new Error('Failed to fetch tickers');
    
    const data = await response.json();
    
    // Filter to only include USDT pairs and take top 30
    const usdtPairs = data
      .filter((t: any) => t.symbol.endsWith('USDT') && !t.symbol.includes('UP') && !t.symbol.includes('DOWN'))
      .slice(0, 30)
      .reduce((acc: Record<string, Ticker>, t: any) => {
        acc[t.symbol] = {
          symbol: t.symbol,
          price: t.lastPrice,
          priceChange: t.priceChange,
          priceChangePercent: t.priceChangePercent,
          high: t.highPrice,
          low: t.lowPrice,
          volume: t.volume,
          quoteVolume: t.quoteVolume,
          lastUpdate: Date.now(),
        };
        return acc;
      }, {});
    
    return usdtPairs;
  } catch (error) {
    console.error('Error fetching tickers:', error);
    throw error;
  }
}
