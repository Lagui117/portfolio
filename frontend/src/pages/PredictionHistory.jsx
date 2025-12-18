import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import dashboardService from '../services/dashboardService'
import AIChatButton from '../components/AIChatButton'

function PredictionHistory() {
  const [predictions, setPredictions] = useState([])
  const [pagination, setPagination] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    type: 'all',
    confidence_min: null,
    confidence_max: null,
    sort: 'date',
    order: 'desc',
    page: 1
  })

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const data = await dashboardService.getHistory({
        ...filters,
        per_page: 20
      })
      setPredictions(data.predictions || [])
      setPagination(data.pagination)
    } catch (error) {
      console.error('Erreur chargement historique:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [filters])

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset page on filter change
    }))
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.75) return 'bg-green-100 text-green-800'
    if (confidence >= 0.5) return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  const getTypeColor = (type) => {
    return type === 'sports' 
      ? 'bg-blue-100 text-blue-800' 
      : 'bg-emerald-100 text-emerald-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Historique des prédictions</h1>
              <p className="mt-2 text-gray-600">
                Consultez et analysez toutes vos prédictions passées
              </p>
            </div>
            <Link 
              to="/dashboard"
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              ← Retour au dashboard
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filtres</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Type filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">Tous</option>
                <option value="sports">Sports</option>
                <option value="finance">Finance</option>
              </select>
            </div>

            {/* Confidence min */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confiance min.</label>
              <select
                value={filters.confidence_min || ''}
                onChange={(e) => handleFilterChange('confidence_min', e.target.value ? parseFloat(e.target.value) : null)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Aucun</option>
                <option value="0.5">≥ 50%</option>
                <option value="0.6">≥ 60%</option>
                <option value="0.7">≥ 70%</option>
                <option value="0.8">≥ 80%</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Trier par</label>
              <select
                value={filters.sort}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="date">Date</option>
                <option value="confidence">Confiance</option>
              </select>
            </div>

            {/* Order */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Ordre</label>
              <select
                value={filters.order}
                onChange={(e) => handleFilterChange('order', e.target.value)}
                className="w-full rounded-lg border-gray-300 shadow-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="desc">Décroissant</option>
                <option value="asc">Croissant</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : predictions.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <svg className="w-16 h-16 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p className="text-lg font-medium">Aucune prédiction trouvée</p>
              <p className="text-sm">Commencez par analyser un match ou un actif</p>
            </div>
          ) : (
            <>
              {/* Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Sujet
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Prédiction
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Confiance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {predictions.map((pred, index) => (
                      <tr key={pred.id || index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(pred.prediction_type)}`}>
                            {pred.prediction_type === 'sports' ? '⚽ Sports' : '📈 Finance'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {pred.ticker || pred.external_match_id || 'N/A'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {pred.prediction_value || 'En cours'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {pred.confidence ? (
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getConfidenceColor(pred.confidence)}`}>
                              {Math.round(pred.confidence * 100)}%
                            </span>
                          ) : (
                            <span className="text-gray-400">N/A</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {pred.created_at ? new Date(pred.created_at).toLocaleString('fr-FR') : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {pagination && pagination.pages > 1 && (
                <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() => handleFilterChange('page', filters.page - 1)}
                      disabled={!pagination.has_prev}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Précédent
                    </button>
                    <button
                      onClick={() => handleFilterChange('page', filters.page + 1)}
                      disabled={!pagination.has_next}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Suivant
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Page <span className="font-medium">{pagination.page}</span> sur{' '}
                        <span className="font-medium">{pagination.pages}</span> ({pagination.total} résultats)
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleFilterChange('page', filters.page - 1)}
                        disabled={!pagination.has_prev}
                        className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        ←
                      </button>
                      <button
                        onClick={() => handleFilterChange('page', filters.page + 1)}
                        disabled={!pagination.has_next}
                        className="relative inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        →
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* AI Chat */}
      <AIChatButton 
        domain="general"
        context={{ page: 'history', filters }}
      />
    </div>
  )
}

export default PredictionHistory
