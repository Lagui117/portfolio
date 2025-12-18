/**
 * Service IA - Communication avec les endpoints AI de PredictWise.
 * 
 * Fournit:
 * - Chat conversationnel avec contexte
 * - Analyse ponctuelle de données
 * - Vérification de l'état du service IA
 */

import apiClient from './apiClient';

const aiService = {
  /**
   * Envoie un message au chat IA.
   * @param {string} message - Message de l'utilisateur
   * @param {object} context - Contexte optionnel
   * @param {string} conversationId - ID de conversation pour continuité
   * @returns {Promise<object>} Réponse formatée
   */
  async chat(message, context = {}, conversationId = null) {
    try {
      const response = await apiClient.post('/ai/chat', {
        message,
        context,
        conversation_id: conversationId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur AI Chat:', error);
      throw error;
    }
  },

  /**
   * Analyse des données Sports ou Finance.
   * @param {string} type - 'sports' ou 'finance'
   * @param {object} data - Données à analyser (format normalisé)
   * @param {string} question - Question spécifique optionnelle
   * @returns {Promise<object>} Analyse avec recommandations
   */
  async analyze(type, data, question = null) {
    try {
      const payload = { type, data };
      if (question) {
        payload.question = question;
      }
      
      const response = await apiClient.post('/ai/analyze', payload);
      return response.data;
    } catch (error) {
      console.error('Erreur AI Analyze:', error);
      throw error;
    }
  },

  /**
   * Vérifie le status du service IA.
   * @returns {Promise<object>} Status du service
   */
  async health() {
    try {
      const response = await apiClient.get('/ai/health');
      return response.data;
    } catch (error) {
      console.error('Erreur AI Health:', error);
      return {
        status: 'error',
        openai_configured: false,
        error: error.message
      };
    }
  },

  /**
   * Analyse un match sportif avec contexte.
   * @param {object} match - Données du match
   * @returns {Promise<object>} Analyse du match
   */
  async analyzeMatch(match) {
    return this.analyze('sports', {
      home_team: match.home_team,
      away_team: match.away_team,
      competition: match.competition,
      odds_home: match.odds_home,
      odds_draw: match.odds_draw,
      odds_away: match.odds_away,
      status: match.status,
      prediction: match.prediction,
      confidence: match.confidence
    });
  },

  /**
   * Analyse un actif financier avec contexte.
   * @param {object} asset - Données de l'actif
   * @returns {Promise<object>} Analyse de l'actif
   */
  async analyzeAsset(asset) {
    return this.analyze('finance', {
      symbol: asset.symbol,
      name: asset.name,
      current_price: asset.current_price || asset.price,
      change_percent: asset.change_percent,
      indicators: asset.indicators,
      sector: asset.sector,
      prediction: asset.prediction,
      confidence: asset.confidence
    });
  },

  /**
   * Envoie un message au chat avec le contexte de la page actuelle.
   * @param {string} message - Message
   * @param {object} currentAnalysis - Analyse en cours (match ou asset)
   * @param {string} page - Page courante
   * @returns {Promise<object>} Réponse
   */
  async chatWithContext(message, currentAnalysis = null, page = 'general') {
    const context = { page };
    
    if (currentAnalysis) {
      context.current_analysis = currentAnalysis;
    }
    
    return this.chat(message, context);
  }
};

export default aiService;
