import { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries, HistogramSeries } from 'lightweight-charts';
import type { IChartApi, ISeriesApi, CandlestickData, Time, HistogramData } from 'lightweight-charts';
import { usePriceStore } from '../stores/priceStore';

const BINANCE_KLINE_API = 'https://api.binance.com/api/v3/klines';

interface KlineData {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const TIMEFRAMES = [
  { label: '1m', value: '1m', minutes: 1 },
  { label: '5m', value: '5m', minutes: 5 },
  { label: '15m', value: '15m', minutes: 15 },
  { label: '1h', value: '1h', minutes: 60 },
  { label: '4h', value: '4h', minutes: 240 },
  { label: '1D', value: '1d', minutes: 1440 },
];

async function fetchKlines(symbol: string, timeframe: string, limit = 500): Promise<KlineData[]> {
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
    volume: parseFloat(k[5]),
  }));
}

export function KLineChart() {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  
  const { selectedSymbol } = usePriceStore();
  const [timeframe, setTimeframe] = useState('1h');
  const [loading, setLoading] = useState(false);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#8888a0',
      },
      grid: {
        vertLines: { color: 'rgba(42, 42, 58, 0.5)' },
        horzLines: { color: 'rgba(42, 42, 58, 0.5)' },
      },
      crosshair: {
        mode: 1,
        vertLine: {
          color: '#00d4ff',
          width: 1,
          style: 2,
          labelBackgroundColor: '#00d4ff',
        },
        horzLine: {
          color: '#00d4ff',
          width: 1,
          style: 2,
          labelBackgroundColor: '#00d4ff',
        },
      },
      rightPriceScale: {
        borderColor: '#2a2a3a',
      },
      timeScale: {
        borderColor: '#2a2a3a',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#00e676',
      downColor: '#ff1744',
      borderUpColor: '#00e676',
      borderDownColor: '#ff1744',
      wickUpColor: '#00e676',
      wickDownColor: '#ff1744',
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries as ISeriesApi<'Candlestick'>;
    volumeSeriesRef.current = volumeSeries as ISeriesApi<'Histogram'>;

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, []);

  // Load data when symbol or timeframe changes
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const data = await fetchKlines(selectedSymbol, timeframe);
        
        const candleData: CandlestickData[] = data.map((d) => ({
          time: d.time,
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }));

        const volumeData: HistogramData[] = data.map((d) => ({
          time: d.time,
          value: d.volume,
          color: d.close >= d.open ? 'rgba(0, 230, 118, 0.5)' : 'rgba(255, 23, 68, 0.5)',
        }));

        candleSeriesRef.current?.setData(candleData);
        volumeSeriesRef.current?.setData(volumeData);
        
        chartRef.current?.timeScale().fitContent();
      } catch (error) {
        console.error('Failed to load kline data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedSymbol, timeframe]);

  return (
    <div className="flex flex-col h-full">
      {/* Chart Header */}
      <div className="flex items-center justify-between p-3 border-b border-[var(--border-color)]">
        <div className="flex items-center gap-3">
          <span className="font-display font-semibold">{selectedSymbol}</span>
          <span className="text-xs text-[var(--text-muted)]">K-Line</span>
        </div>
        
        {/* Timeframe Selector */}
        <div className="flex gap-1">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf.value}
              onClick={() => setTimeframe(tf.value)}
              className={`
                px-3 py-1.5 text-xs font-medium rounded transition-colors
                ${timeframe === tf.value 
                  ? 'bg-[var(--accent-primary)] text-white' 
                  : 'bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }
              `}
            >
              {tf.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Container */}
      <div ref={chartContainerRef} className="flex-1 relative">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--bg-primary)]/50 z-10">
            <div className="text-[var(--text-secondary)]">Loading chart...</div>
          </div>
        )}
      </div>
    </div>
  );
}
