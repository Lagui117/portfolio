/**
 * Finance service.
 * 
 * Handles stock data, technical indicators, and predictions.
 */
import apiClient from './apiClient';

const financeService = {
  /**
   * Get stock market data.
   */
  async getStockData(symbol, period = '1mo', interval = '1d') {
    try {
      const response = await apiClient.get(`/finance/stocks/${symbol}`, {
        params: { period, interval },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get technical indicators for a stock.
   */
  async getIndicators(symbol, period = '1mo', indicators = 'MA,RSI,VOLATILITY') {
    try {
      const response = await apiClient.get(`/finance/indicators/${symbol}`, {
        params: { period, indicators },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Predict stock price trend using ML.
   */
  async predictTrend(symbol, period = '1mo') {
    try {
      const response = await apiClient.post('/finance/predict', {
        symbol,
        period,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get user's finance prediction history.
   */
  async getPredictionHistory(limit = 50) {
    try {
      const response = await apiClient.get('/finance/predictions/history', {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get user's watchlist.
   */
  async getWatchlist() {
    try {
      const response = await apiClient.get('/finance/watchlist');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Add symbol to watchlist.
   */
  async addToWatchlist(symbol) {
    try {
      const response = await apiClient.post('/finance/watchlist', { symbol });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default financeService;
