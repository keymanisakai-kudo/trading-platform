import { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';
import type { IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts';

const BINANCE_KLINE_API = 'https://api.binance.com/api/v3/klines';

interface KlineData {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
}

const TIMEFRAMES = [
  { label: '15P', value: '15m' },
  { label: '1H', value: '1h' },
  { label: '4H', value: '4h' },
  { label: '1D', value: '1d' },
];

async function fetchKlines(symbol: string, timeframe: string, limit = 100): Promise<KlineData[]> {
  const response = await fetch(
    `${BINANCE_KLINE_API}?symbol=${symbol}&interval=${timeframe}&limit=${limit}`
  );
  const data = await response.json();
  
  return data.map((k: any[]) => ({
    time: (Math.floor(k[0] / 1000)) as Time,
    open: parseFloat(k[1]),
    high: parseFloat(k[2]),
    low: parseFloat(k[3]),
    close: parseFloat(k[4]),
  }));
}

interface MiniChartProps {
  symbol: string;
}

export function MiniChart({ symbol }: MiniChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const [timeframe, setTimeframe] = useState('1h');

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#718096',
      },
      grid: {
        vertLines: { color: 'rgba(113, 128, 150, 0.1)' },
        horzLines: { color: 'rgba(113, 128, 150, 0.1)' },
      },
      crosshair: { mode: 0 },
      rightPriceScale: { borderColor: 'transparent' },
      timeScale: { borderColor: 'transparent', timeVisible: false },
      handleScroll: false,
      handleScale: false,
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#48bb78',
      downColor: '#f56565',
      borderUpColor: '#48bb78',
      borderDownColor: '#f56565',
      wickUpColor: '#48bb78',
      wickDownColor: '#f56565',
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries as ISeriesApi<'Candlestick'>;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    handleResize();

    return () => {
      chart.remove();
    };
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await fetchKlines(symbol, timeframe);
        
        const candleData: CandlestickData[] = data.map((d) => ({
          time: d.time,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }));

        candleSeriesRef.current?.setData(candleData);
        chartRef.current?.timeScale().fitContent();
      } catch (error) {
        console.error('Failed to load kline:', error);
      }
    };

    loadData();
  }, [symbol, timeframe]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-1 mb-2">
        {TIMEFRAMES.map((tf) => (
          <button
            key={tf.value}
            onClick={() => setTimeframe(tf.value)}
            className={`px-2 py-1 text-[10px] font-medium rounded-lg transition-all ${
              timeframe === tf.value 
                ? 'bg-[var(--accent-primary)] text-white shadow-md' 
                : 'clay-inset text-[var(--text-muted)]'
            }`}
          >
            {tf.label}
          </button>
        ))}
      </div>
      <div ref={chartContainerRef} className="flex-1 min-h-[100px]" />
    </div>
  );
}
