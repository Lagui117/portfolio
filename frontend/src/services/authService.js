/**
 * Authentication service.
 * 
 * Handles user registration, login, logout, and profile management.
 */
import apiClient from './apiClient';

const authService = {
  /**
   * Register a new user.
   */
  async register(username, email, password) {
    try {
      const response = await apiClient.post('/auth/register', {
        username,
        email,
        password,
      });
      
      // Store token and user
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { user, token: access_token };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Login existing user.
   */
  async login(email, password) {
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      });
      
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      return { user, token: access_token };
    } catch (error) {
      throw error;
    }
  },

  /**
   * Logout current user.
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  /**
   * Get current user profile.
   */
  async getProfile() {
    try {
      const response = await apiClient.get('/auth/me');
      const user = response.data.user;
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update user profile.
   */
  async updateProfile(updates) {
    try {
      const response = await apiClient.put('/auth/me', updates);
      const user = response.data.user;
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get current user from local storage.
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is authenticated.
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  /**
   * Get auth token.
   */
  getToken() {
    return localStorage.getItem('token');
  },
};

export default authService;
