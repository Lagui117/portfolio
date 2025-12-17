/**
 * MiniLineChart - Graphique linéaire compact pour tendances
 */

import React from 'react';
import './MiniLineChart.css';

function MiniLineChart({ data = [], width = 200, height = 60, color = 'var(--color-neon-blue)' }) {
  if (!data || data.length === 0) {
    return <div className="mini-chart-empty" style={{ width, height }}>No data</div>;
  }

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  // Points for area fill
  const areaPoints = `0,${height} ${points} ${width},${height}`;

  return (
    <div className="mini-line-chart" style={{ width, height }}>
      <svg width={width} height={height} className="chart-svg">
        {/* Area gradient */}
        <defs>
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        
        {/* Area fill */}
        <polygon
          points={areaPoints}
          fill="url(#areaGradient)"
        />
        
        {/* Line */}
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="chart-line"
        />
        
        {/* Points */}
        {data.map((value, index) => {
          const x = (index / (data.length - 1)) * width;
          const y = height - ((value - min) / range) * height;
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="3"
              fill={color}
              className="chart-point"
            />
          );
        })}
      </svg>
    </div>
  );
}

export default MiniLineChart;
