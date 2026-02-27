import { useEffect, useRef, useCallback } from 'react';
import { usePriceStore } from '../stores/priceStore';

const WS_URL = 'wss://stream.binance.com:9443/ws';

export function useBinanceWebSocket(symbols: string[]) {
  const wsRef = useRef<WebSocket | null>(null);
  const updateTicker = usePriceStore((state) => state.updateTicker);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }

    // Create stream URL for multiple symbols
    const streams = symbols.map((s) => `${s.toLowerCase()}@ticker`).join('/');
    const ws = new WebSocket(`${WS_URL}/${streams}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.s) {
        updateTicker(data.s, {
          price: data.c,
          priceChange: data.p,
          priceChangePercent: data.P,
          volume: data.v,
          quoteVolume: data.q,
        });
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      // Reconnect after 5 seconds
      setTimeout(connect, 5000);
    };

    wsRef.current = ws;
  }, [symbols, updateTicker]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return wsRef;
}
