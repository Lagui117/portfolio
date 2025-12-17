import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as authService from '../../services/authService';
import apiClient from '../../services/apiClient';

vi.mock('../../services/apiClient');

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('signup', () => {
    it('calls POST /auth/register with user data', async () => {
      const mockResponse = {
        data: {
          access_token: 'token123',
          user: { id: 1, email: 'test@example.com' }
        }
      };
      
      apiClient.post.mockResolvedValue(mockResponse);
      
      const userData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'Pass123!'
      };
      
      const result = await authService.signup(userData);
      
      expect(apiClient.post).toHaveBeenCalledWith('/auth/register', userData);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('login', () => {
    it('calls POST /auth/login with credentials', async () => {
      const mockResponse = {
        data: {
          access_token: 'token123',
          user: { id: 1, email: 'test@example.com' }
        }
      };
      
      apiClient.post.mockResolvedValue(mockResponse);
      
      const credentials = {
        email: 'test@example.com',
        password: 'Pass123!'
      };
      
      const result = await authService.login(credentials);
      
      expect(apiClient.post).toHaveBeenCalledWith('/auth/login', credentials);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getMe', () => {
    it('calls GET /auth/me', async () => {
      const mockResponse = {
        data: {
          user: { id: 1, email: 'test@example.com', username: 'testuser' }
        }
      };
      
      apiClient.get.mockResolvedValue(mockResponse);
      
      const result = await authService.getMe();
      
      expect(apiClient.get).toHaveBeenCalledWith('/auth/me', { params: {} });
      expect(result).toEqual(mockResponse.data);
    });

    it('includes stats parameter when requested', async () => {
      apiClient.get.mockResolvedValue({ data: {} });
      
      await authService.getMe(true);
      
      expect(apiClient.get).toHaveBeenCalledWith('/auth/me', { params: { stats: 'true' } });
    });
  });

  describe('logout', () => {
    it('removes access_token from localStorage', () => {
      localStorage.setItem('access_token', 'token123');
      
      authService.logout();
      
      expect(localStorage.getItem('access_token')).toBeFalsy();
    });
  });

  describe('isAuthenticated', () => {
    it('returns true when access_token exists', async () => {
      // Utiliser directement window.localStorage pour s'assurer de la cohérence
      window.localStorage.setItem('access_token', 'token123');
      
      // La fonction isAuthenticated utilise localStorage globalement
      const result = !!window.localStorage.getItem('access_token');
      expect(result).toBe(true);
      
      // Tester aussi via la fonction du service
      expect(authService.isAuthenticated()).toBe(result);
    });

    it('returns false when access_token does not exist', () => {
      localStorage.removeItem('access_token');
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});
