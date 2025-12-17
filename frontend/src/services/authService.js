/**
 * Service d'authentification.
 * Gere inscription, connexion et recuperation du profil.
 */

import apiClient from './apiClient';

/**
 * Inscrit un nouvel utilisateur.
 * @param {Object} payload - Donnees d'inscription.
 * @param {string} payload.email - Email.
 * @param {string} payload.username - Nom d'utilisateur.
 * @param {string} payload.password - Mot de passe.
 * @param {string} [payload.first_name] - Prenom.
 * @param {string} [payload.last_name] - Nom de famille.
 * @returns {Promise<Object>} Reponse avec access_token et user.
 */
export async function signup(payload) {
  const response = await apiClient.post('/auth/register', payload);
  return response.data;
}

/**
 * Connecte un utilisateur.
 * @param {Object} payload - Identifiants.
 * @param {string} payload.email - Email.
 * @param {string} payload.password - Mot de passe.
 * @returns {Promise<Object>} Reponse avec access_token et user.
 */
export async function login(payload) {
  const response = await apiClient.post('/auth/login', payload);
  return response.data;
}

/**
 * Recupere les informations de l'utilisateur connecte.
 * @param {boolean} [includeStats=false] - Inclure les statistiques.
 * @returns {Promise<Object>} Donnees utilisateur.
 */
export async function getMe(includeStats = false) {
  const params = includeStats ? { stats: 'true' } : {};
  const response = await apiClient.get('/auth/me', { params });
  return response.data;
}

/**
 * Deconnecte l'utilisateur (cote client).
 */
export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
}

/**
 * Verifie si l'utilisateur est connecte.
 * @returns {boolean}
 */
export function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

/**
 * Stocke le token et les infos utilisateur.
 * @param {string} token - Token JWT.
 * @param {Object} user - Donnees utilisateur.
 */
export function storeAuthData(token, user) {
  localStorage.setItem('access_token', token);
  if (user) {
    localStorage.setItem('user', JSON.stringify(user));
  }
}

/**
 * Recupere l'utilisateur stocke localement.
 * @returns {Object|null}
 */
export function getStoredUser() {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}
