/**
 * Client API pour PredictWise.
 * Configure axios avec baseURL et intercepteur JWT.
 */

import axios from 'axios';

// Base URL depuis les variables d'environnement
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';

// Instance axios configuree
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 secondes
});

// Intercepteur pour ajouter le token JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gerer les erreurs de reponse
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Token expire ou invalide
    if (error.response && error.response.status === 401) {
      // Supprimer le token et rediriger vers login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      
      // Ne pas rediriger si on est deja sur login/signup
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/signup' && currentPath !== '/') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
