/**
 * Sparkline - Ligne ultra-compacte pour mini tendances
 */

import React from 'react';
import './Sparkline.css';

function Sparkline({ data = [], width = 80, height = 24, color = 'var(--color-neon-blue)', trend = 'neutral' }) {
  if (!data || data.length < 2) {
    return <div className="sparkline-empty" style={{ width, height }} />;
  }

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const trendColor = trend === 'up' ? 'var(--color-success)' : 
                     trend === 'down' ? 'var(--color-danger)' : color;

  return (
    <svg width={width} height={height} className="sparkline">
      <polyline
        points={points}
        fill="none"
        stroke={trendColor}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default Sparkline;
