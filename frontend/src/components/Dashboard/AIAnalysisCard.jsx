/**
 * AIAnalysisCard - Carte premium pour résumés IA et analyses GPT
 */

import React from 'react';
import './AIAnalysisCard.css';

const mockAIInsight = {
  summary: "Tendance haussière confirmée sur les marchés tech",
  analysis: [
    "Les indices tech montrent une consolidation positive avec un momentum fort sur les valeurs FAANG.",
    "Le sentiment du marché s'améliore grâce aux résultats Q4 dépassant les attentes.",
    "Attention aux prises de bénéfices possibles après la récente hausse de 12%."
  ],
  confidence: 0.75,
  lastUpdate: new Date().toISOString(),
  model: "GPT-4 Turbo + ML Hybrid",
};

function AIAnalysisCard() {
  return (
    <section className="ai-analysis-section">
      <div className="section-header">
        <h2 className="section-title">🤖 Analyse IA Avancée</h2>
        <span className="section-subtitle">Powered by GPT-4 + Machine Learning</span>
      </div>

      <div className="ai-card card-premium glow-effect">
        <div className="ai-header">
          <div className="ai-badge">
            <span className="badge-icon">✨</span>
            <span className="badge-text">Analyse Automatique</span>
          </div>
          <span className="ai-timestamp">
            Mise à jour : {new Date(mockAIInsight.lastUpdate).toLocaleTimeString('fr-FR')}
          </span>
        </div>

        <div className="ai-summary">
          <h3 className="summary-title gradient-text">{mockAIInsight.summary}</h3>
        </div>

        <div className="ai-analysis">
          <h4 className="analysis-subtitle">Points clés</h4>
          <ul className="analysis-list">
            {mockAIInsight.analysis.map((point, index) => (
              <li key={index} className="analysis-item">
                <span className="item-bullet">→</span>
                <span className="item-text">{point}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="ai-confidence">
          <div className="confidence-header">
            <span className="confidence-label">Niveau de confiance</span>
            <span className="confidence-percentage">
              {(mockAIInsight.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="confidence-track">
            <div
              className="confidence-progress"
              style={{ width: `${mockAIInsight.confidence * 100}%` }}
            />
          </div>
        </div>

        <div className="ai-footer">
          <div className="model-info">
            <span className="model-icon">🔬</span>
            <span className="model-name">{mockAIInsight.model}</span>
          </div>
          <button className="full-analysis-btn">
            Voir l'analyse complète →
          </button>
        </div>

        <div className="ai-disclaimer">
          <span className="disclaimer-icon">⚡</span>
          <span className="disclaimer-text">
            <strong>GPT-4 Analysis</strong> — Signal généré avec niveau de confiance
          </span>
        </div>
      </div>
    </section>
  );
}

export default AIAnalysisCard;
