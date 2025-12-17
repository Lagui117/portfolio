/**
 * Client API configuré pour PredictWise.
 * Gère axios avec baseURL, intercepteurs JWT et gestion d'erreurs.
 */

import axios from 'axios';

// Base URL depuis les variables d'environnement
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';

// Instance axios configurée
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
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

// Intercepteur pour gérer les erreurs de réponse
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Token expiré ou invalide
    if (error.response && error.response.status === 401) {
      const currentPath = window.location.pathname;
      const publicPaths = ['/', '/login', '/signup'];
      
      // Nettoyer les données d'authentification
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      
      // Rediriger uniquement si on est sur une page protégée
      if (!publicPaths.includes(currentPath)) {
        window.location.href = '/login?session_expired=true';
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
