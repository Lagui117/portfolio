/**
 * Service pour les analyses sportives.
 */

import apiClient from './apiClient';

/**
 * Obtient une prédiction pour un match.
 */
export async function getSportsPrediction(matchId) {
  const response = await apiClient.get(`/sports/predict/${matchId}`);
  return response.data;
}

/**
 * Récupère la liste des matchs disponibles.
 */
export async function getMatches(options = {}) {
  const response = await apiClient.get('/sports/matches', { params: options });
  return response.data;
}

/**
 * Récupère l'historique des prédictions sports.
 */
export async function getSportsPredictionsHistory(options = {}) {
  const response = await apiClient.get('/sports/predictions/history', { params: options });
  return response.data;
}

/**
 * Liste des matchs de exemple.
 */
export const DEMO_MATCHES = [
  { id: '1', label: 'Manchester United vs Liverpool' },
  { id: '2', label: 'Real Madrid vs Barcelona' },
  { id: '3', label: 'PSG vs Lyon' },
];
