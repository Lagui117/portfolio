import apiClient from './apiClient'

/**
 * Service pour récupérer les suggestions et analyses IA
 */

/**
 * Récupère la suggestion IA du jour
 * @returns {Promise<Object>} Suggestion IA avec title et text
 */
export const getDailySuggestion = async () => {
  try {
    // TODO: À connecter à l'endpoint GPT backend quand disponible
    // const response = await apiClient.get('/ai/daily-suggestion')
    // return response.data
    
    // Pour l'instant, retourne des données mock variées
    const suggestions = [
      {
        title: 'Suggestion IA du jour',
        text: 'Sur les derniers matchs, plusieurs équipes montrent une forte variabilité de performance, tandis que certains titres boursiers évoluent dans une zone de volatilité modérée. Utilisez ces informations uniquement à des fins éducatives.'
      },
      {
        title: 'Analyse de tendance',
        text: 'Les données récentes suggèrent une corrélation intéressante entre les performances sportives en mi-temps et les résultats finaux. Sur le marché financier, les indicateurs techniques montrent des signaux mixtes nécessitant une analyse approfondie.'
      },
      {
        title: 'Insight hebdomadaire',
        text: 'Cette semaine, les équipes à domicile ont montré une performance supérieure de 12% en moyenne. Les actifs technologiques présentent une volatilité accrue avec des opportunités d\'apprentissage intéressantes pour les analystes.'
      }
    ]
    
    // Sélection aléatoire basée sur le jour
    const dayOfYear = Math.floor((new Date() - new Date(new Date().getFullYear(), 0, 0)) / 86400000)
    const index = dayOfYear % suggestions.length
    
    return suggestions[index]
  } catch (error) {
    console.error('Erreur lors de la récupération de la suggestion IA:', error)
    return {
      title: 'Suggestion IA du jour',
      text: 'Explorez les analyses sportives et financières pour découvrir des insights générés par IA.'
    }
  }
}

/**
 * Récupère les statistiques utilisateur pour le hub
 * @returns {Promise<Object>} Statistiques utilisateur
 */
export const getUserStats = async () => {
  try {
    const response = await apiClient.get('/users/stats')
    return response.data
  } catch (error) {
    console.error('Erreur lors de la récupération des stats:', error)
    return {
      total_predictions: 0,
      sports_predictions: 0,
      finance_predictions: 0,
      total_consultations: 0
    }
  }
}

export default {
  getDailySuggestion,
  getUserStats
}
