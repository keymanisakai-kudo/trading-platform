import { create } from 'zustand';
import api from '../api/client';

interface Balance {
  currency: string;
  available: number;
  locked: number;
  total: number;
}

interface Transaction {
  id: string;
  type: string;
  amount: number;
  fee: number;
  status: string;
  tx_hash: string | null;
  address: string | null;
  created_at: string;
}

interface WalletState {
  balances: Balance[];
  totalUsdtValue: number;
  transactions: Transaction[];
  depositAddress: string | null;
  isLoading: boolean;
  error: string | null;
  
  fetchBalance: () => Promise<void>;
  fetchTransactions: () => Promise<void>;
  fetchDepositAddress: (currency?: string, network?: string) => Promise<void>;
  withdraw: (currency: string, address: string, amount: number, network: string) => Promise<void>;
}

export const useWalletStore = create<WalletState>((set) => ({
  balances: [],
  totalUsdtValue: 0,
  transactions: [],
  depositAddress: null,
  isLoading: false,
  error: null,

  fetchBalance: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getBalance();
      set({ 
        balances: data.balances, 
        totalUsdtValue: data.total_usdt_value,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to fetch balance' 
      });
    }
  },

  fetchTransactions: async () => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getTransactions();
      set({ transactions: data, isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to fetch transactions' 
      });
    }
  },

  fetchDepositAddress: async (currency = 'USDT', network = 'TRC20') => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.getDepositAddress(currency, network);
      set({ depositAddress: data.address, isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Failed to fetch deposit address' 
      });
    }
  },

  withdraw: async (currency: string, address: string, amount: number, network: string) => {
    set({ isLoading: true, error: null });
    try {
      await api.withdraw(currency, address, amount, network);
      // Refresh balance after withdrawal
      await api.getBalance();
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        isLoading: false, 
        error: error.response?.data?.detail || 'Withdrawal failed' 
      });
      throw error;
    }
  },
}));
