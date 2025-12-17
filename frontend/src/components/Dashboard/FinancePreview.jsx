/**
 * FinancePreview - Aperçu rapide des actifs financiers
 */

import React from 'react';
import Sparkline from '../Charts/Sparkline';
import './FinancePreview.css';

const mockAssets = [
  {
    ticker: 'AAPL',
    name: 'Apple Inc.',
    price: 195.42,
    change: 2.34,
    changePercent: 1.21,
    trend: 'up',
    data: [190, 192, 189, 193, 191, 194, 195.42],
    prediction: 'UP',
    confidence: 0.72,
  },
  {
    ticker: 'TSLA',
    name: 'Tesla Inc.',
    price: 248.15,
    change: -5.67,
    changePercent: -2.23,
    trend: 'down',
    data: [260, 258, 255, 252, 250, 249, 248.15],
    prediction: 'DOWN',
    confidence: 0.68,
  },
  {
    ticker: 'BTC-USD',
    name: 'Bitcoin',
    price: 42350.25,
    change: 1250.80,
    changePercent: 3.04,
    trend: 'up',
    data: [40500, 41000, 40800, 41500, 42000, 42200, 42350.25],
    prediction: 'UP',
    confidence: 0.65,
  },
  {
    ticker: 'EUR/USD',
    name: 'Euro / Dollar',
    price: 1.0875,
    change: 0.0012,
    changePercent: 0.11,
    trend: 'neutral',
    data: [1.086, 1.087, 1.086, 1.088, 1.087, 1.088, 1.0875],
    prediction: 'NEUTRAL',
    confidence: 0.55,
  },
  {
    ticker: 'AMZN',
    name: 'Amazon.com Inc.',
    price: 152.89,
    change: 3.12,
    changePercent: 2.08,
    trend: 'up',
    data: [148, 149, 150, 151, 150, 152, 152.89],
    prediction: 'UP',
    confidence: 0.70,
  },
];

function FinancePreview() {
  return (
    <section className="finance-preview">
      <div className="section-header">
        <div>
          <h2 className="section-title">📈 Actifs surveillés</h2>
          <span className="section-subtitle">Analyse en temps réel</span>
        </div>
        <button className="view-all-btn">Voir tous les actifs →</button>
      </div>

      <div className="assets-table">
        <div className="table-header">
          <div className="col-ticker">Actif</div>
          <div className="col-price">Prix</div>
          <div className="col-change">Variation</div>
          <div className="col-chart">Tendance (7j)</div>
          <div className="col-prediction">Prédiction IA</div>
          <div className="col-action">Action</div>
        </div>

        <div className="table-body">
          {mockAssets.map(asset => (
            <div key={asset.ticker} className="asset-row">
              <div className="col-ticker">
                <div className="asset-info">
                  <span className="asset-ticker">{asset.ticker}</span>
                  <span className="asset-name">{asset.name}</span>
                </div>
              </div>

              <div className="col-price">
                <span className="asset-price">
                  ${asset.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </div>

              <div className="col-change">
                <span className={`asset-change ${asset.changePercent >= 0 ? 'positive' : 'negative'}`}>
                  {asset.changePercent >= 0 ? '+' : ''}{asset.changePercent.toFixed(2)}%
                </span>
                <span className="asset-change-value">
                  {asset.change >= 0 ? '+' : ''}{asset.change.toFixed(2)}
                </span>
              </div>

              <div className="col-chart">
                <Sparkline 
                  data={asset.data} 
                  width={100} 
                  height={32}
                  trend={asset.trend}
                />
              </div>

              <div className="col-prediction">
                <div className="prediction-badge">
                  <span className={`prediction-label ${asset.prediction.toLowerCase()}`}>
                    {asset.prediction}
                  </span>
                  <div className="confidence-mini">
                    <div 
                      className="confidence-bar"
                      style={{ width: `${asset.confidence * 100}%` }}
                    />
                  </div>
                  <span className="confidence-value">
                    {(asset.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="col-action">
                <button className="study-btn">
                  Étudier
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default FinancePreview;
