import { create } from 'zustand';
import api from '../api/client';

interface Order {
  id: string;
  symbol: string;
  side: string;
  order_type: string;
  price: number | null;
  amount: number;
  filled_amount: number;
  status: string;
  created_at: string;
}

interface Trade {
  id: string;
  order_id: string;
  symbol: string;
  side: string;
  price: number;
  amount: number;
  fee: number;
  created_at: string;
}

interface OrderState {
  orders: Order[];
  currentOrder: Order | null;
  trades: Trade[];
  total: number;
  isLoading: boolean;
  error: string | null;
  
  fetchOrders: (params?: { symbol?: string; status?: string; limit?: number; offset?: number }) => Promise<void>;
  placeLimitOrder: (symbol: string, side: string, amount: number, price: number) => Promise<Order>;
  placeMarketOrder: (symbol: string, side: string, amount: number) => Promise<Order>;
  cancelOrder: (orderId: string) => Promise<void>;
  fetchOrderTrades: (orderId: string) => Promise<void>;
}

export const useOrderStore = create<OrderState>((set) => ({
  orders: [],
  currentOrder: null,
  trades: [],
  total: 0,
  isLoading: false,
  error: null,

  fetchOrders: async (params) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getOrders(params);
      set({ 
        orders: data.orders, 
        total: data.total,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to fetch orders' 
      });
    }
  },

  placeLimitOrder: async (symbol: string, side: string, amount: number, price: number) => {
    set({ isLoading: true, error: null });
    try {
      const order = await api.placeLimitOrder(symbol, side, amount, price);
      set((state) => ({ 
        orders: [order, ...state.orders],
        isLoading: false 
      }));
      return order;
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to place order' 
      });
      throw error;
    }
  },

  placeMarketOrder: async (symbol: string, side: string, amount: number) => {
    set({ isLoading: true, error: null });
    try {
      const order = await api.placeMarketOrder(symbol, side, amount);
      set((state) => ({ 
        orders: [order, ...state.orders],
        isLoading: false 
      }));
      return order;
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to place order' 
      });
      throw error;
    }
  },

  cancelOrder: async (orderId: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.cancelOrder(orderId);
      set((state) => ({ 
        orders: state.orders.map(o => 
          o.id === orderId ? { ...o, status: 'cancelled' } : o
        ),
        isLoading: false 
      }));
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to cancel order' 
      });
      throw error;
    }
  },

  fetchOrderTrades: async (orderId: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getOrderTrades(orderId);
      set({ trades: data, isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to fetch trades' 
      });
    }
  },
}));
