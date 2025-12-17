/**
 * Service d'authentification.
 * Gère l'inscription, la connexion et la récupération du profil.
 */

import apiClient from './apiClient';

/**
 * Inscrit un nouvel utilisateur.
 */
export async function signup(userData) {
  const response = await apiClient.post('/auth/register', userData);
  return response.data;
}

/**
 * Connecte un utilisateur.
 */
export async function login(credentials) {
  const response = await apiClient.post('/auth/login', credentials);
  return response.data;
}

/**
 * Récupère les informations de l'utilisateur connecté.
 */
export async function getMe(includeStats = false) {
  const params = includeStats ? { stats: 'true' } : {};
  const response = await apiClient.get('/auth/me', { params });
  return response.data;
}

/**
 * Déconnecte l'utilisateur (côté client).
 */
export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

/**
 * Vérifie si l'utilisateur est connecté.
 */
export function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

/**
 * Stocke le token et les infos utilisateur.
 */
export function storeAuthData(token, user) {
  localStorage.setItem('access_token', token);
  if (user) {
    localStorage.setItem('user', JSON.stringify(user));
  }
}

/**
 * Récupère l'utilisateur stocké localement.
 */
export function getStoredUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

/**
 * Extrait le message d'erreur d'une réponse API.
 */
export function extractErrorMessage(error) {
  if (error.response?.data?.error) {
    const errorData = error.response.data.error;
    
    // Format standardisé {error: {type, message, details}}
    if (typeof errorData === 'object' && errorData.message) {
      return errorData.message;
    }
    
    // Format simple {error: "message"}
    if (typeof errorData === 'string') {
      return errorData;
    }
  }
  
  // Fallback
  return error.response?.data?.message || error.message || 'Une erreur est survenue';
}
