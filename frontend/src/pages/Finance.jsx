import { useState, useEffect } from 'react'
import financeService from '../services/financeService'

function Finance() {
  const [symbol, setSymbol] = useState('AAPL')
  const [stockData, setStockData] = useState(null)
  const [indicators, setIndicators] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [period, setPeriod] = useState('1mo')

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const data = await financeService.getPredictionHistory(10)
      setHistory(data.predictions || [])
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!symbol.trim()) return

    setLoading(true)
    setError('')
    
    try {
      // Fetch stock data and indicators
      const [stockResponse, indicatorsResponse] = await Promise.all([
        financeService.getStockData(symbol.toUpperCase(), period),
        financeService.getIndicators(symbol.toUpperCase(), period, 'MA,RSI,VOLATILITY,MACD')
      ])
      
      setStockData(stockResponse)
      setIndicators(indicatorsResponse.indicators)
    } catch (err) {
      setError(err.message || 'Erreur lors de l\'analyse')
      setStockData(null)
      setIndicators(null)
    } finally {
      setLoading(false)
    }
  }

  const handlePredict = async () => {
    setLoading(true)
    setError('')
    
    try {
      const data = await financeService.predictTrend(symbol.toUpperCase(), period)
      setPrediction(data.prediction)
      await fetchHistory() // Refresh history
    } catch (err) {
      setError(err.message || 'Erreur lors de la prédiction')
      setPrediction(null)
    } finally {
      setLoading(false)
    }
  }

  const getTrendColor = (trend) => {
    return trend === 'UP' ? 'text-green-600' : 'text-red-600'
  }

  const getTrendIcon = (trend) => {
    return trend === 'UP' ? '↗' : '↘'
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Module Finance</h1>
        <p className="mt-2 text-gray-600">Analyse technique et prédictions ML pour les actions</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-bold mb-4">Analyser une action</h2>
        <form onSubmit={handleAnalyze}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbole boursier
              </label>
              <input
                type="text"
                placeholder="AAPL, GOOGL, TSLA..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent uppercase"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Période
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
              >
                <option value="1d">1 jour</option>
                <option value="5d">5 jours</option>
                <option value="1mo">1 mois</option>
                <option value="3mo">3 mois</option>
                <option value="6mo">6 mois</option>
                <option value="1y">1 an</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                type="submit"
                disabled={loading || !symbol.trim()}
                className="w-full px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Chargement...' : 'Analyser'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Stock Data */}
      {stockData && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Données de {stockData.symbol}</h2>
            <button
              onClick={handlePredict}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
            >
              Prédire la tendance
            </button>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded">
              <p className="text-sm text-gray-600">Période</p>
              <p className="text-lg font-bold text-blue-600">{stockData.period}</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded">
              <p className="text-sm text-gray-600">Points de données</p>
              <p className="text-lg font-bold text-green-600">{stockData.count || 0}</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded">
              <p className="text-sm text-gray-600">Intervalle</p>
              <p className="text-lg font-bold text-purple-600">{stockData.interval}</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded">
              <p className="text-sm text-gray-600">Prix actuel</p>
              <p className="text-lg font-bold text-yellow-600">
                ${stockData.data?.[stockData.data.length - 1]?.close?.toFixed(2) || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Technical Indicators */}
      {indicators && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Indicateurs techniques</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Moving Averages */}
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="font-semibold text-gray-700 mb-3">Moyennes mobiles</h3>
              <div className="space-y-2">
                {indicators.MA_5 && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">MA 5:</span>
                    <span className="font-medium">${indicators.MA_5.toFixed(2)}</span>
                  </div>
                )}
                {indicators.MA_20 && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">MA 20:</span>
                    <span className="font-medium">${indicators.MA_20.toFixed(2)}</span>
                  </div>
                )}
                {indicators.MA_50 && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">MA 50:</span>
                    <span className="font-medium">${indicators.MA_50.toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Momentum */}
            <div className="border-l-4 border-green-500 pl-4">
              <h3 className="font-semibold text-gray-700 mb-3">Momentum</h3>
              <div className="space-y-2">
                {indicators.RSI !== undefined && (
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">RSI:</span>
                      <span className={`font-medium ${
                        indicators.RSI > 70 ? 'text-red-600' : 
                        indicators.RSI < 30 ? 'text-green-600' : 'text-gray-900'
                      }`}>
                        {indicators.RSI.toFixed(2)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          indicators.RSI > 70 ? 'bg-red-500' :
                          indicators.RSI < 30 ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${indicators.RSI}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Survendu (30)</span>
                      <span>Suracheté (70)</span>
                    </div>
                  </div>
                )}
                {indicators.MACD && (
                  <div className="mt-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">MACD:</span>
                      <span className="font-medium">{indicators.MACD.macd_line?.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Signal:</span>
                      <span className="font-medium">{indicators.MACD.signal_line?.toFixed(3)}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Volatility */}
            <div className="border-l-4 border-purple-500 pl-4">
              <h3 className="font-semibold text-gray-700 mb-3">Volatilité</h3>
              <div className="space-y-2">
                {indicators.volatility_daily !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Quotidienne:</span>
                    <span className="font-medium">{(indicators.volatility_daily * 100).toFixed(2)}%</span>
                  </div>
                )}
                {indicators.volatility_annual !== undefined && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Annualisée:</span>
                    <span className="font-medium">{(indicators.volatility_annual * 100).toFixed(2)}%</span>
                  </div>
                )}
                {indicators.current_price !== undefined && (
                  <div className="flex justify-between mt-4 pt-4 border-t">
                    <span className="text-sm text-gray-600">Prix actuel:</span>
                    <span className="font-bold text-lg">${indicators.current_price.toFixed(2)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Prediction Result */}
      {prediction && (
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Prédiction ML</h2>
          <div className="bg-white rounded-lg p-6">
            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Symbole</p>
              <p className="text-2xl font-bold text-gray-900">{prediction.symbol}</p>
            </div>

            <div className="text-center mb-6">
              <p className="text-sm text-gray-600 mb-2">Tendance prédite</p>
              <div className="flex items-center justify-center gap-2">
                <span className={`text-5xl font-bold ${getTrendColor(prediction.trend)}`}>
                  {getTrendIcon(prediction.trend)}
                </span>
                <p className={`text-3xl font-bold ${getTrendColor(prediction.trend)}`}>
                  {prediction.trend === 'UP' ? 'HAUSSE' : 'BAISSE'}
                </p>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Confiance: <span className="font-semibold text-lg">{(prediction.confidence * 100).toFixed(1)}%</span>
              </p>
            </div>

            {prediction.probabilities && (
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700 text-center mb-4">Probabilités:</p>
                {Object.entries(prediction.probabilities).map(([trend, prob]) => (
                  <div key={trend} className="flex items-center gap-3">
                    <span className={`text-sm font-medium w-20 ${getTrendColor(trend)}`}>
                      {trend} {getTrendIcon(trend)}
                    </span>
                    <div className="flex-1 bg-gray-200 rounded-full h-6">
                      <div
                        className={`h-6 rounded-full ${
                          trend === 'UP' ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${prob * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold w-16 text-right">
                      {(prob * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            )}

            {prediction.model_version && (
              <p className="text-center text-xs text-gray-500 mt-6">
                Modèle: {prediction.model_version}
              </p>
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
                <div key={pred.id} className="flex items-center justify-between p-3 bg-gray-50 rounded hover:bg-gray-100 transition">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{input.symbol || 'N/A'}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(pred.created_at).toLocaleDateString('fr-FR')} •{' '}
                      {pred.model_version}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold text-lg ${getTrendColor(pred.prediction_result)}`}>
                      {pred.prediction_result} {getTrendIcon(pred.prediction_result)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(pred.confidence_score * 100).toFixed(0)}% confiance
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

export default Finance
