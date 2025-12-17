/**
 * OverviewSection - Section principale avec statistiques globales
 */

import React from 'react';
import CircularGauge from '../Charts/CircularGauge';
import MiniLineChart from '../Charts/MiniLineChart';
import './OverviewSection.css';

// Mock data
const mockAnalyticsData = {
  totalAnalyses: 247,
  sportsAnalyses: 138,
  financeAnalyses: 109,
  avgAccuracy: 78.5,
  weeklyTrend: [45, 52, 48, 61, 58, 67, 72],
};

function OverviewSection() {
  return (
    <section className="overview-section">
      <div className="section-header">
        <h2 className="section-title">Vue d'ensemble</h2>
        <span className="section-subtitle">Statistiques des 30 derniers jours</span>
      </div>

      <div className="stats-grid">
        {/* Total Analyses */}
        <div className="stat-card card-premium">
          <div className="stat-header">
            <span className="stat-icon">📊</span>
            <span className="stat-label">Analyses totales</span>
          </div>
          <div className="stat-value gradient-text">{mockAnalyticsData.totalAnalyses}</div>
          <div className="stat-footer">
            <MiniLineChart 
              data={mockAnalyticsData.weeklyTrend} 
              width={180} 
              height={50}
              color="var(--color-neon-blue)"
            />
            <span className="stat-change positive">+12% cette semaine</span>
          </div>
        </div>

        {/* Précision IA */}
        <div className="stat-card card-premium">
          <div className="stat-header">
            <span className="stat-icon">🎯</span>
            <span className="stat-label">Précision moyenne</span>
          </div>
          <div className="gauge-container">
            <CircularGauge 
              value={mockAnalyticsData.avgAccuracy} 
              max={100}
              label="Fiabilité"
              size={140}
              color="var(--color-neon-purple)"
            />
          </div>
          <div className="stat-footer center">
            <span className="stat-note">Basé sur {mockAnalyticsData.totalAnalyses} prédictions</span>
          </div>
        </div>

        {/* Sports vs Finance */}
        <div className="stat-card card-premium">
          <div className="stat-header">
            <span className="stat-icon">⚽</span>
            <span className="stat-label">Analyses sportives</span>
          </div>
          <div className="stat-value">{mockAnalyticsData.sportsAnalyses}</div>
          <div className="progress-bar">
            <div 
              className="progress-fill sports"
              style={{ width: `${(mockAnalyticsData.sportsAnalyses / mockAnalyticsData.totalAnalyses) * 100}%` }}
            />
          </div>
          <div className="stat-footer">
            <span className="stat-percentage">
              {Math.round((mockAnalyticsData.sportsAnalyses / mockAnalyticsData.totalAnalyses) * 100)}% du total
            </span>
          </div>
        </div>

        <div className="stat-card card-premium">
          <div className="stat-header">
            <span className="stat-icon">📈</span>
            <span className="stat-label">Analyses financières</span>
          </div>
          <div className="stat-value">{mockAnalyticsData.financeAnalyses}</div>
          <div className="progress-bar">
            <div 
              className="progress-fill finance"
              style={{ width: `${(mockAnalyticsData.financeAnalyses / mockAnalyticsData.totalAnalyses) * 100}%` }}
            />
          </div>
          <div className="stat-footer">
            <span className="stat-percentage">
              {Math.round((mockAnalyticsData.financeAnalyses / mockAnalyticsData.totalAnalyses) * 100)}% du total
            </span>
          </div>
        </div>
      </div>

      {/* Call-to-Action Buttons */}
      <div className="cta-grid">
        <button className="cta-btn primary glow-effect">
          <span className="cta-icon">⚽</span>
          <div className="cta-content">
            <span className="cta-title">Analyser un match</span>
            <span className="cta-subtitle">Football, Basketball, Tennis...</span>
          </div>
        </button>

        <button className="cta-btn secondary glow-effect">
          <span className="cta-icon">📈</span>
          <div className="cta-content">
            <span className="cta-title">Analyser un actif</span>
            <span className="cta-subtitle">Actions, Crypto, Forex...</span>
          </div>
        </button>

        <button className="cta-btn tertiary">
          <span className="cta-icon">📂</span>
          <div className="cta-content">
            <span className="cta-title">Importer des données</span>
            <span className="cta-subtitle">CSV, JSON, Excel...</span>
          </div>
        </button>

        <button className="cta-btn tertiary">
          <span className="cta-icon">📜</span>
          <div className="cta-content">
            <span className="cta-title">Historique</span>
            <span className="cta-subtitle">Voir toutes les prédictions</span>
          </div>
        </button>
      </div>
    </section>
  );
}

export default OverviewSection;
