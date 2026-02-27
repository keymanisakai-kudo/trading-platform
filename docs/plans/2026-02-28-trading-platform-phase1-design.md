# Trading Platform Phase 1 Design Document

**Date**: 2026-02-28
**Phase**: Phase 1 - Real-time Market Dashboard + K-Line Charts
**Status**: Approved

---

## 1. Overview

**Purpose**: Build a professional cryptocurrency and forex trading dashboard with real-time market data visualization.

**Target Users**: Individual retail investors interested in crypto and forex trading.

**Tech Stack**:
- React 18 + Vite
- TypeScript
- TailwindCSS
- TradingView Lightweight Charts (for K-line)
- Binance WebSocket API (crypto real-time data)
- Frankfurter API (forex rates)

---

## 2. UI/UX Design

### 2.1 Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ HEADER (60px) - Logo | Navigation | Theme Toggle               │
├───────────────┬─────────────────────────────────────────────────┤
│               │                                                 │
│   SIDEBAR     │              MAIN CONTENT                      │
│   (280px)     │                                                 │
│               │  ┌─────────────────────────────────────────┐  │
│  - Markets    │  │         K-LINE CHART AREA                │  │
│  - Crypto     │  │         (TradingView Charts)             │  │
│  - Forex      │  │         Height: 60% viewport             │  │
│               │  └─────────────────────────────────────────┘  │
│               │                                                 │
│               │  ┌──────────────────┬──────────────────────┐   │
│               │  │  MARKET LIST     │    ORDER BOOK        │   │
│               │  │  (Price Table)   │    (Depth Chart)     │   │
│               │  │                  │                      │   │
│               │  └──────────────────┴──────────────────────┘   │
│               │                                                 │
└───────────────┴─────────────────────────────────────────────────┘
```

**Responsive Breakpoints**:
- Desktop: ≥1280px (full layout)
- Tablet: 768px-1279px (collapsible sidebar)
- Mobile: <768px (bottom navigation, stacked layout)

### 2.2 Visual Design

**Color Palette (Dark Theme)**:
```css
--bg-primary: #0a0a0f;
--bg-secondary: #12121a;
--bg-card: #16161f;
--border-color: #2a2a3a;
--text-primary: #e8e8e8;
--text-secondary: #8888a0;
--accent-primary: #00d4ff;
--accent-hover: #00b8e0;
--success: #00e676;
--danger: #ff1744;
--warning: #ffab00;
```

**Color Palette (Light Theme)**:
```css
--bg-primary: #f8f9fc;
--bg-secondary: #ffffff;
--bg-card: #ffffff;
--border-color: #e2e4ea;
--text-primary: #1a1a2e;
--text-secondary: #6b7084;
--accent-primary: #0066ff;
--accent-hover: #0052cc;
```

**Typography**:
- **Display/Numbers**: JetBrains Mono (monospace for prices)
- **Headings**: Sora (600 weight)
- **Body**: DM Sans (400/500 weight)

**Spacing System**: 4px base unit (4, 8, 12, 16, 24, 32, 48, 64)

**Visual Effects**:
- Card shadow: `0 4px 24px rgba(0, 0, 0, 0.12)`
- Glassmorphism on header: `backdrop-filter: blur(12px)`
- Border radius: 8px (cards), 6px (buttons), 4px (inputs)
- Hover transitions: 150ms ease-out

### 2.3 Components

| Component | States | Behavior |
|-----------|--------|----------|
| PriceCard | default, hover, selected, up, down | Click to select, color change on price movement |
| KLineChart | loading, ready, error | Zoom, pan, timeframe selector (1m/5m/15m/1h/4h/1d) |
| OrderBook | default, loading | Real-time depth visualization |
| MarketTicker | scrolling | Horizontal marquee of top prices |
| TabNav | default, active | Switch between Crypto/Forex |
| ThemeToggle | dark, light | Smooth transition animation |

---

## 3. Functionality Specification

### 3.1 Core Features

1. **Real-time Crypto Prices**
   - Fetch from Binance REST API
   - WebSocket for live updates
   - Display: symbol, price, 24h change %, 24h volume
   - Top 20 trading pairs by volume

2. **K-Line Chart**
   - TradingView Lightweight Charts library
   - Timeframes: 1m, 5m, 15m, 1h, 4h, 1D
   - Candlestick style
   - Volume histogram below
   - Crosshair with price/time tooltip

3. **Order Book (Depth)**
   - Bid/Ask levels (top 20)
   - Visual depth bars
   - Spread indicator

4. **Forex Rates**
   - Fetch from Frankfurter API
   - Supported pairs: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CNY
   - Refresh every 60 seconds

5. **Market Ticker**
   - Horizontal scrolling marquee
   - Top 10 crypto prices
   - Smooth infinite scroll animation

### 3.2 User Interactions

| Action | Response |
|--------|----------|
| Click price in list | Load K-line for that symbol |
| Hover price | Highlight row, show tooltip |
| Click timeframe button | Reload chart with new interval |
| Click theme toggle | Smooth transition to other theme |
| Click tab (Crypto/Forex) | Switch data source |
| Resize window | Responsive layout adjustment |

### 3.3 Data Flow

```
Binance API ─────┬──> PriceStore (Zustand) ──> PriceCard
                │                                │
WebSocket ──────┤                                ▼
                │                          KLineChart
                │                                │
                │                                ▼
                └────> OrderBook Store ─────> OrderBook

Frankfurter API ─────> ForexStore ─────> ForexPanel
```

### 3.4 Error Handling

- API failure: Show cached data with "stale" indicator
- WebSocket disconnect: Auto-reconnect with exponential backoff
- Empty state: Skeleton loaders during fetch

---

## 4. Acceptance Criteria

### 4.1 Success Conditions

- [ ] App loads without errors
- [ ] Crypto price list displays 20+ pairs with real-time updates
- [ ] K-line chart renders with candlesticks
- [ ] Timeframe switching works (1m/5m/15m/1h/4h/1D)
- [ ] Order book shows bid/ask with visual depth
- [ ] Forex rates display 5+ currency pairs
- [ ] Dark/Light theme toggle works smoothly
- [ ] Responsive layout works on tablet/mobile
- [ ] No console errors in production build

### 4.2 Visual Checkpoints

1. **Header**: Logo left, nav center, theme toggle right
2. **Sidebar**: Collapsible, icons + labels, active state
3. **K-line**: Full-width chart, timeframe buttons visible
4. **Price List**: Alternating row colors, green/red for price changes
5. **Theme**: All colors transition smoothly

---

## 5. Technical Notes

### 5.1 Dependencies

```json
{
  "dependencies": {
    "@tradingview/lightweight-charts": "^4.1.0",
    "zustand": "^4.5.0",
    "lucide-react": "^0.400.0"
  }
}
```

### 5.2 API Endpoints

**Binance**:
- REST: `https://api.binance.com/api/v3/ticker/24hr`
- K-line: `https://api.binance.com/api/v3/klines`
- WebSocket: `wss://stream.binance.com:9443/ws`

**Frankfurter**:
- `https://api.frankfurter.app/latest?from=USD`

---

## 6. Next Steps

After Phase 1 approval → Transition to **Phase 2: Writing Plans**

- Break down into implementable tasks
- Each task: 2-5 minutes (test → implement → verify → commit)
