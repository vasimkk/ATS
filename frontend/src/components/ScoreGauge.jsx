import React, { useEffect, useState } from 'react';

export default function ScoreGauge({ score, grade, label, size = 200 }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = score / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= score) {
        setAnimatedScore(score);
        clearInterval(timer);
      } else {
        setAnimatedScore(Math.round(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;

  let strokeColor = '#10b981'; // Emerald
  let badgeBg = 'rgba(16, 185, 129, 0.15)';
  let badgeBorder = 'rgba(16, 185, 129, 0.3)';
  let badgeColor = '#34d399';

  if (score < 50) {
    strokeColor = '#f43f5e'; // Rose
    badgeBg = 'rgba(244, 63, 94, 0.15)';
    badgeBorder = 'rgba(244, 63, 94, 0.3)';
    badgeColor = '#fb7185';
  } else if (score < 75) {
    strokeColor = '#f59e0b'; // Amber
    badgeBg = 'rgba(245, 158, 11, 0.15)';
    badgeBorder = 'rgba(245, 158, 11, 0.3)';
    badgeColor = '#fbbf24';
  }

  return (
    <div className="gauge-wrapper" style={{ width: size, height: size }}>
      <svg className="gauge-svg" viewBox="0 0 200 200">
        <circle
          className="gauge-bg"
          cx="100"
          cy="100"
          r={radius}
        />
        <circle
          className="gauge-progress"
          cx="100"
          cy="100"
          r={radius}
          stroke={strokeColor}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
        />
      </svg>
      <div className="gauge-content">
        <div style={{ display: 'flex', alignItems: 'baseline', color: strokeColor }}>
          <span className="gauge-val">{animatedScore}</span>
          <span className="gauge-unit">%</span>
        </div>
        {grade && (
          <div
            className="gauge-badge"
            style={{
              backgroundColor: badgeBg,
              border: `1px solid ${badgeBorder}`,
              color: badgeColor,
            }}
          >
            {grade} • {label}
          </div>
        )}
      </div>
    </div>
  );
}
