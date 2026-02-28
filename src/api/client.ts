import axios, { type AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Load tokens from localStorage
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }

    // Request interceptor
    this.client.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`;
      }
      return config;
    });

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401 && this.refreshToken) {
          try {
            await this.refreshAccessToken();
            // Retry the original request
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${this.accessToken}`;
              return this.client(error.config);
            }
          } catch {
            this.logout();
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async register(email: string, username: string, password: string) {
    const response = await this.client.post('/auth/register', {
      email,
      username,
      password,
    });
    this.setTokens(response.data);
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
    });
    this.setTokens(response.data);
    return response.data;
  }

  async logout() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async refreshAccessToken() {
    const response = await this.client.post('/auth/refresh', {
      refresh_token: this.refreshToken,
    });
    this.setTokens(response.data);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  private setTokens(data: { access_token: string; refresh_token: string }) {
    this.accessToken = data.access_token;
    this.refreshToken = data.refresh_token;
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
  }

  // Wallet methods
  async getBalance() {
    const response = await this.client.get('/wallet/balance');
    return response.data;
  }

  async getDepositAddress(currency: string = 'USDT', network: string = 'TRC20') {
    const response = await this.client.get('/wallet/deposit/address', {
      params: { currency, network },
    });
    return response.data;
  }

  async withdraw(currency: string, address: string, amount: number, network: string) {
    const response = await this.client.post('/wallet/withdraw', {
      currency,
      address,
      amount,
      network,
    });
    return response.data;
  }

  async getTransactions(limit: number = 50, offset: number = 0) {
    const response = await this.client.get('/wallet/transactions', {
      params: { limit, offset },
    });
    return response.data;
  }

  // Order methods
  async getOrders(params?: { symbol?: string; status?: string; limit?: number; offset?: number }) {
    const response = await this.client.get('/orders/', { params });
    return response.data;
  }

  async placeLimitOrder(symbol: string, side: string, amount: number, price: number) {
    const response = await this.client.post('/orders/limit', {
      symbol,
      side,
      order_type: 'limit',
      amount,
      price,
    });
    return response.data;
  }

  async placeMarketOrder(symbol: string, side: string, amount: number) {
    const response = await this.client.post('/orders/market', {
      symbol,
      side,
      order_type: 'market',
      amount,
    });
    return response.data;
  }

  async cancelOrder(orderId: string) {
    const response = await this.client.delete(`/orders/${orderId}`);
    return response.data;
  }

  async getOrderTrades(orderId: string) {
    const response = await this.client.get(`/orders/${orderId}/trades`);
    return response.data;
  }

  // Check if authenticated
  isAuthenticated(): boolean {
    return !!this.accessToken;
  }
}

export const api = new ApiClient();
export default api;
