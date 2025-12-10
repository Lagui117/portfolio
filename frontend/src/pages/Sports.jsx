import { useState, useEffect } from 'react'
import sportsService from '../services/sportsService'

function Sports() {
  const [matches, setMatches] = useState([])
  const [teamStats, setTeamStats] = useState(null)
  const [searchTeam, setSearchTeam] = useState('')
  const [prediction, setPrediction] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [selectedMatch, setSelectedMatch] = useState(null)

  useEffect(() => {
    fetchMatches()
    fetchHistory()
  }, [])

  const fetchMatches = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await sportsService.getUpcomingMatches()
      setMatches(data.matches || [])
    } catch (err) {
      setError(err.message || 'Erreur lors du chargement des matchs')
    } finally {
      setLoading(false)
    }
  }

  const fetchTeamStats = async () => {
    if (!searchTeam.trim()) return
    
    setLoading(true)
    setError('')
    try {
      const data = await sportsService.getTeamStatistics(searchTeam)
      setTeamStats(data)
    } catch (err) {
      setError(err.message || 'Équipe non trouvée')
      setTeamStats(null)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async (match) => {
    setLoading(true)
    setError('')
    setSelectedMatch(match)
    try {
      const data = await sportsService.predictMatch(
        match.home_team,
        match.away_team,
        match.league
      )
      setPrediction(data.prediction)
    } catch (err) {
      setError(err.message || 'Erreur lors de la prédiction')
      setPrediction(null)
    } finally {
      setLoading(false)
    }
  }

  const fetchHistory = async () => {
    try {
      const data = await sportsService.getPredictionHistory(10)
      setHistory(data.predictions || [])
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  const getOutcomeColor = (outcome) => {
    switch(outcome) {
      case 'HOME_WIN': return 'text-blue-600'
      case 'AWAY_WIN': return 'text-red-600'
      case 'DRAW': return 'text-gray-600'
      default: return 'text-gray-900'
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Module Sports</h1>
        <p className="mt-2 text-gray-600">Prédictions ML pour les matchs sportifs</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Team Statistics Search */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Statistiques d'équipe</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Nom de l'équipe..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            value={searchTeam}
            onChange={(e) => setSearchTeam(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchTeamStats()}
          />
          <button
            onClick={fetchTeamStats}
            disabled={loading || !searchTeam.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Rechercher
          </button>
        </div>

        {teamStats && (
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded">
              <p className="text-sm text-gray-600">Matchs joués</p>
              <p className="text-2xl font-bold text-blue-600">{teamStats.statistics?.matches_played || 0}</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded">
              <p className="text-sm text-gray-600">Victoires</p>
              <p className="text-2xl font-bold text-green-600">{teamStats.statistics?.wins || 0}</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded">
              <p className="text-sm text-gray-600">Taux de victoire</p>
              <p className="text-2xl font-bold text-yellow-600">
                {((teamStats.statistics?.win_rate || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded">
              <p className="text-sm text-gray-600">Buts moyens</p>
              <p className="text-2xl font-bold text-purple-600">
                {(teamStats.statistics?.avg_goals_scored || 0).toFixed(2)}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Upcoming Matches */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Matchs à venir</h2>
        
        {loading && matches.length === 0 ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.slice(0, 10).map((match, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4">
                      <div className="text-right flex-1">
                        <p className="font-semibold text-gray-900">{match.home_team}</p>
                      </div>
                      <div className="text-center px-4">
                        <p className="text-sm text-gray-500">vs</p>
                      </div>
                      <div className="text-left flex-1">
                        <p className="font-semibold text-gray-900">{match.away_team}</p>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">{match.league} • {match.match_date}</p>
                    {match.home_odds && (
                      <div className="flex gap-4 mt-2 text-sm">
                        <span className="text-gray-600">Cotes: </span>
                        <span className="font-medium text-blue-600">{match.home_odds.toFixed(2)}</span>
                        <span className="font-medium text-gray-600">{match.draw_odds.toFixed(2)}</span>
                        <span className="font-medium text-red-600">{match.away_odds.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => handlePredict(match)}
                    disabled={loading}
                    className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    Prédire
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Prediction Result */}
      {prediction && selectedMatch && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Résultat de la prédiction</h2>
          <div className="bg-white rounded-lg p-6">
            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Match</p>
              <p className="text-lg font-bold">{selectedMatch.home_team} vs {selectedMatch.away_team}</p>
            </div>
            
            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Prédiction</p>
              <p className={`text-3xl font-bold ${getOutcomeColor(prediction.outcome)}`}>
                {prediction.outcome === 'HOME_WIN' && `Victoire ${selectedMatch.home_team}`}
                {prediction.outcome === 'AWAY_WIN' && `Victoire ${selectedMatch.away_team}`}
                {prediction.outcome === 'DRAW' && 'Match nul'}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Confiance: <span className="font-semibold">{(prediction.confidence * 100).toFixed(1)}%</span>
              </p>
            </div>

            {prediction.probabilities && (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700 mb-3">Probabilités:</p>
                {Object.entries(prediction.probabilities).map(([outcome, prob]) => (
                  <div key={outcome} className="flex items-center gap-2">
                    <span className="text-sm w-24">{outcome}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${
                          outcome === 'HOME_WIN' ? 'bg-blue-500' :
                          outcome === 'AWAY_WIN' ? 'bg-red-500' : 'bg-gray-500'
                        }`}
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium w-16 text-right">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Historique des prédictions</h2>
          <div className="space-y-2">
            {history.map((pred) => {
              const input = pred.input_details || {}
              return (
                <div key={pred.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <p className="font-medium text-sm">
                      {input.home_team} vs {input.away_team}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(pred.created_at).toLocaleDateString('fr-FR')}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-semibold text-sm ${getOutcomeColor(pred.prediction_result)}`}>
                      {pred.prediction_result}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(pred.confidence_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default Sports
