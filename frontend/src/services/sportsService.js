/**
 * Sports service.
 * 
 * Handles sports matches, statistics, and predictions.
 */
import apiClient from './apiClient';

const sportsService = {
  /**
   * Get upcoming matches.
   */
  async getUpcomingMatches(league = null, limit = 20) {
    try {
      const params = {};
      if (league) params.league = league;
      if (limit) params.limit = limit;
      
      const response = await apiClient.get('/sports/matches', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get team statistics.
   */
  async getTeamStatistics(teamName) {
    try {
      const response = await apiClient.get(`/sports/statistics/${teamName}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Predict match outcome using ML.
   */
  async predictMatch(homeTeam, awayTeam, league = 'Unknown') {
    try {
      const response = await apiClient.post('/sports/predict', {
        home_team: homeTeam,
        away_team: awayTeam,
        league,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get user's prediction history.
   */
  async getPredictionHistory(limit = 50) {
    try {
      const response = await apiClient.get('/sports/history', {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default sportsService;
