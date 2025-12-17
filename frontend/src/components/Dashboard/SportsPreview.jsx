/**
 * SportsPreview - Aperçu rapide des matchs du jour
 */

import React from 'react';
import './SportsPreview.css';

const mockMatches = [
  {
    id: 1,
    homeTeam: 'Paris SG',
    awayTeam: 'Marseille',
    competition: 'Ligue 1',
    date: '2025-12-17T20:00:00',
    homeProbability: 0.65,
    awayProbability: 0.20,
    drawProbability: 0.15,
    homeForm: [1, 1, 0, 1, 1], // W W D W W
    awayForm: [1, 0, 0, 1, 0], // W L L W L
  },
  {
    id: 2,
    homeTeam: 'Real Madrid',
    awayTeam: 'Barcelona',
    competition: 'La Liga',
    date: '2025-12-17T21:00:00',
    homeProbability: 0.48,
    awayProbability: 0.35,
    drawProbability: 0.17,
    homeForm: [1, 1, 1, 0, 1],
    awayForm: [1, 1, 0, 1, 1],
  },
  {
    id: 3,
    homeTeam: 'Man City',
    awayTeam: 'Liverpool',
    competition: 'Premier League',
    date: '2025-12-17T17:30:00',
    homeProbability: 0.52,
    awayProbability: 0.30,
    drawProbability: 0.18,
    homeForm: [1, 1, 1, 1, 0],
    awayForm: [1, 0, 1, 1, 1],
  },
];

function SportsPreview() {
  const renderForm = (form) => {
    return form.map((result, index) => (
      <span
        key={index}
        className={`form-indicator ${result === 1 ? 'win' : result === 0.5 ? 'draw' : 'loss'}`}
      >
        {result === 1 ? 'V' : result === 0.5 ? 'N' : 'D'}
      </span>
    ));
  };

  return (
    <section className="sports-preview">
      <div className="section-header">
        <div>
          <h2 className="section-title">⚽ Matchs du jour</h2>
          <span className="section-subtitle">Prédictions disponibles</span>
        </div>
        <button className="view-all-btn">Voir tous les matchs →</button>
      </div>

      <div className="matches-grid">
        {mockMatches.map(match => (
          <div key={match.id} className="match-card card-premium">
            <div className="match-header">
              <span className="match-competition">{match.competition}</span>
              <span className="match-time">
                {new Date(match.date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            <div className="match-teams">
              <div className="team home">
                <span className="team-name">{match.homeTeam}</span>
                <div className="team-form">{renderForm(match.homeForm)}</div>
              </div>

              <div className="match-vs">VS</div>

              <div className="team away">
                <span className="team-name">{match.awayTeam}</span>
                <div className="team-form">{renderForm(match.awayForm)}</div>
              </div>
            </div>

            <div className="match-predictions">
              <div className="prediction-item">
                <span className="prediction-label">Victoire {match.homeTeam}</span>
                <div className="prediction-bar">
                  <div
                    className="prediction-fill home"
                    style={{ width: `${match.homeProbability * 100}%` }}
                  />
                  <span className="prediction-value">{(match.homeProbability * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="prediction-item">
                <span className="prediction-label">Match nul</span>
                <div className="prediction-bar">
                  <div
                    className="prediction-fill draw"
                    style={{ width: `${match.drawProbability * 100}%` }}
                  />
                  <span className="prediction-value">{(match.drawProbability * 100).toFixed(0)}%</span>
                </div>
              </div>

              <div className="prediction-item">
                <span className="prediction-label">Victoire {match.awayTeam}</span>
                <div className="prediction-bar">
                  <div
                    className="prediction-fill away"
                    style={{ width: `${match.awayProbability * 100}%` }}
                  />
                  <span className="prediction-value">{(match.awayProbability * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>

            <button className="analyze-btn glow-effect">
              Analyser ce match
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

export default SportsPreview;
