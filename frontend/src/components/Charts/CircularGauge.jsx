/**
 * CircularGauge - Jauge circulaire pour afficher des pourcentages
 */

import React from 'react';
import './CircularGauge.css';

function CircularGauge({ value = 0, max = 100, label = '', size = 120, color = 'var(--color-neon-blue)' }) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));
  const strokeWidth = 8;
  const radius = (size / 2) - (strokeWidth / 2);
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="circular-gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="gauge-svg">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--color-border)"
          strokeWidth={strokeWidth}
        />
        
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="gauge-progress"
          style={{ filter: `drop-shadow(0 0 8px ${color})` }}
        />
      </svg>
      
      <div className="gauge-content">
        <div className="gauge-value">{Math.round(percentage)}%</div>
        {label && <div className="gauge-label">{label}</div>}
      </div>
    </div>
  );
}

export default CircularGauge;
