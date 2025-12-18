import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import dashboardService from '../services/dashboardService'
import AIChatButton from '../components/AIChatButton'
import './Dashboard.css'

// Composant pour les cartes KPI
function KPICard({ title, value, subtitle, icon, color, trend }) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    indigo: 'bg-indigo-500'
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trend.direction === 'up' ? 'text-green-600' : trend.direction === 'down' ? 'text-red-600' : 'text-gray-500'}`}>
              {trend.direction === 'up' && (
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {trend.direction === 'down' && (
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
              <span>{trend.percentage}% vs période précédente</span>
            </div>
          )}
        </div>
        <div className={`${colorClasses[color]} rounded-lg p-4`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

// Composant pour le graphique d'activité simple
function ActivityChart({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400">
        Pas encore d'activité
      </div>
    )
  }

  const entries = Object.entries(data).slice(-14) // 14 derniers jours
  const maxValue = Math.max(...entries.map(([, v]) => v), 1)

  return (
    <div className="flex items-end justify-between h-48 gap-1">
      {entries.map(([date, value]) => (
        <div key={date} className="flex flex-col items-center flex-1">
          <div 
            className="w-full bg-blue-500 rounded-t hover:bg-blue-600 transition-colors"
            style={{ height: `${(value / maxValue) * 100}%`, minHeight: '4px' }}
            title={`${date}: ${value} prédictions`}
          />
          <span className="text-xs text-gray-400 mt-1 transform -rotate-45 origin-top-left">
            {new Date(date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })}
          </span>
        </div>
      ))}
    </div>
  )
}

// Composant pour la répartition par type
function TypeDistribution({ sports, finance }) {
  const total = sports + finance
  if (total === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400">
        Aucune prédiction
      </div>
    )
  }

  const sportsPercent = Math.round((sports / total) * 100)
  const financePercent = 100 - sportsPercent

  return (
    <div className="space-y-4">
      <div className="flex h-6 rounded-full overflow-hidden bg-gray-200">
        <div 
          className="bg-blue-500 transition-all duration-500"
          style={{ width: `${sportsPercent}%` }}
        />
        <div 
          className="bg-green-500 transition-all duration-500"
          style={{ width: `${financePercent}%` }}
        />
      </div>
      <div className="flex justify-between text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded-full mr-2" />
          <span>Sports: {sports} ({sportsPercent}%)</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded-full mr-2" />
          <span>Finance: {finance} ({financePercent}%)</span>
        </div>
      </div>
    </div>
  )
}

// Composant pour les prédictions récentes
function RecentPredictions({ predictions }) {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-gray-400">
        Aucune prédiction récente
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {predictions.map((pred, index) => (
        <div key={pred.id || index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <div className="flex items-center">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${pred.prediction_type === 'sports' ? 'bg-blue-100' : 'bg-green-100'}`}>
              {pred.prediction_type === 'sports' ? (
                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2a8 8 0 100 16 8 8 0 000-16z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5z" />
                </svg>
              )}
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-900">
                {pred.ticker || pred.external_match_id || pred.prediction_type}
              </p>
              <p className="text-xs text-gray-500">
                {pred.prediction_value || 'En cours'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className={`text-sm font-semibold ${pred.confidence >= 0.7 ? 'text-green-600' : pred.confidence >= 0.5 ? 'text-yellow-600' : 'text-red-600'}`}>
              {pred.confidence ? `${Math.round(pred.confidence * 100)}%` : 'N/A'}
            </p>
            <p className="text-xs text-gray-400">
              {pred.created_at ? new Date(pred.created_at).toLocaleDateString('fr-FR') : ''}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

// Composant principal Dashboard
function Dashboard() {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [overview, setOverview] = useState(null)
  const [kpis, setKPIs] = useState(null)
  const [performance, setPerformance] = useState(null)

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Charger toutes les données en parallèle
        const [overviewData, kpisData, perfData] = await Promise.all([
          dashboardService.getOverview(),
          dashboardService.getKPIs(),
          dashboardService.getPerformance({ period: '30d' })
        ])

        setOverview(overviewData)
        setKPIs(kpisData)
        setPerformance(perfData)
      } catch (err) {
        console.error('Erreur chargement dashboard:', err)
        setError('Impossible de charger les données du dashboard')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement du dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const stats = overview?.stats || {}

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Bienvenue, {user?.first_name || user?.username} 👋
          </h1>
          <p className="mt-2 text-gray-600">
            Voici le résumé de votre activité sur PredictWise
          </p>
        </div>

        {/* KPIs Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <KPICard
            title="Prédictions totales"
            value={stats.total_predictions || 0}
            subtitle={`${stats.predictions_this_week || 0} cette semaine`}
            color="blue"
            icon={
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
            trend={performance?.trend}
          />

          <KPICard
            title="Confiance moyenne"
            value={`${stats.avg_confidence || 0}%`}
            subtitle="Score IA moyen"
            color="green"
            icon={
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />

          <KPICard
            title="Score d'activité"
            value={`${kpis?.activity_score || 0}%`}
            subtitle="30 derniers jours"
            color="purple"
            icon={
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            }
          />

          <KPICard
            title="Série actuelle"
            value={`${kpis?.streak || 0} jours`}
            subtitle={kpis?.favorite_domain ? `Domaine favori: ${kpis.favorite_domain}` : ''}
            color="yellow"
            icon={
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
              </svg>
            }
          />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Activité quotidienne */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Activité des 14 derniers jours</h3>
            <ActivityChart data={performance?.daily_activity} />
          </div>

          {/* Répartition par type */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition par domaine</h3>
            <TypeDistribution 
              sports={overview?.type_distribution?.sports || 0}
              finance={overview?.type_distribution?.finance || 0}
            />
            
            {/* Confidence Distribution */}
            <div className="mt-6 pt-6 border-t">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Distribution des confiances</h4>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">{performance?.confidence_distribution?.low || 0}</p>
                  <p className="text-xs text-red-500">{"< 50%"}</p>
                </div>
                <div className="p-3 bg-yellow-50 rounded-lg">
                  <p className="text-2xl font-bold text-yellow-600">{performance?.confidence_distribution?.medium || 0}</p>
                  <p className="text-xs text-yellow-500">50-75%</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{performance?.confidence_distribution?.high || 0}</p>
                  <p className="text-xs text-green-500">{"> 75%"}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Prédictions récentes */}
          <div className="lg:col-span-2 bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Prédictions récentes</h3>
              <Link to="/history" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                Voir tout →
              </Link>
            </div>
            <RecentPredictions predictions={overview?.recent_predictions} />
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h3>
            <div className="space-y-3">
              <Link 
                to="/sports"
                className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <div className="bg-blue-500 rounded-lg p-2 mr-3">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 2a8 8 0 100 16 8 8 0 000-16z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Module Sports</p>
                  <p className="text-sm text-gray-500">Analyser les matchs</p>
                </div>
              </Link>

              <Link 
                to="/finance"
                className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
              >
                <div className="bg-green-500 rounded-lg p-2 mr-3">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5z" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Module Finance</p>
                  <p className="text-sm text-gray-500">Analyser les marchés</p>
                </div>
              </Link>

              <Link 
                to="/history"
                className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <div className="bg-purple-500 rounded-lg p-2 mr-3">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <p className="font-medium text-gray-900">Historique</p>
                  <p className="text-sm text-gray-500">Voir toutes les prédictions</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Copilote IA */}
      <AIChatButton 
        domain="general"
        context={{ 
          page: 'dashboard',
          user: user?.username,
          stats: stats
        }}
      />
    </div>
  )
}

export default Dashboard
