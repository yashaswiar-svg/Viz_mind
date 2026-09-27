import React from 'react';

export default function BoxPlotChart({ data, title }) {
  if (!data || data.length === 0) {
    return <div className="text-gray-400 text-sm italic py-8 text-center">No boxplot data available</div>;
  }

  const bp = data[0];
  const { min, q1, median, q3, max, outliers = [] } = bp;

  if (min === undefined || max === undefined || min === max) {
    return <div className="text-gray-400 text-sm italic py-8 text-center">Constant or insufficient range for boxplot</div>;
  }

  const allVals = [min, max, ...outliers].filter((v) => v !== null && v !== undefined);
  const dataMin = Math.min(...allVals);
  const dataMax = Math.max(...allVals);
  const padding = (dataMax - dataMin) * 0.1 || 1;

  const domainMin = dataMin - padding;
  const domainMax = dataMax + padding;
  const range = domainMax - domainMin;

  const scaleX = (val) => {
    return ((val - domainMin) / range) * 480 + 60;
  };

  const xMin = scaleX(min);
  const xQ1 = scaleX(q1);
  const xMed = scaleX(median);
  const xQ3 = scaleX(q3);
  const xMax = scaleX(max);

  return (
    <div className="w-full flex flex-col items-center justify-center py-4">
      {title && <h4 className="text-sm font-semibold text-gray-200 mb-2">{title}</h4>}
      <svg viewBox="0 0 600 160" className="w-full h-44 bg-gray-900/50 rounded-lg p-2 border border-gray-800">
        {/* Horizontal Axis */}
        <line x1="50" y1="120" x2="550" y2="120" stroke="#4B5563" strokeWidth="1" />

        {/* Min tick & max tick labels */}
        <text x="60" y="140" fill="#9CA3AF" fontSize="11" textAnchor="start">{domainMin.toFixed(1)}</text>
        <text x="540" y="140" fill="#9CA3AF" fontSize="11" textAnchor="end">{domainMax.toFixed(1)}</text>

        {/* Whisker Line (Min to Max) */}
        <line x1={xMin} y1="60" x2={xMax} y2="60" stroke="#3B82F6" strokeWidth="2" strokeDasharray="4 4" />

        {/* Min vertical cap */}
        <line x1={xMin} y1="45" x2={xMin} y2="75" stroke="#3B82F6" strokeWidth="2" />
        {/* Max vertical cap */}
        <line x1={xMax} y1="45" x2={xMax} y2="75" stroke="#3B82F6" strokeWidth="2" />

        {/* IQR Box (Q1 to Q3) */}
        <rect
          x={xQ1}
          y="35"
          width={Math.max(2, xQ3 - xQ1)}
          height="50"
          fill="#1E3A8A"
          fillOpacity="0.6"
          stroke="#60A5FA"
          strokeWidth="2"
          rx="4"
        />

        {/* Median Line */}
        <line x1={xMed} y1="35" x2={xMed} y2="85" stroke="#F59E0B" strokeWidth="3" />

        {/* Outliers */}
        {outliers.map((val, idx) => {
          const cx = scaleX(val);
          return (
            <circle
              key={idx}
              cx={cx}
              cy="60"
              r="4"
              fill="#EF4444"
              stroke="#991B1B"
              strokeWidth="1"
            >
              <title>{`Outlier: ${val}`}</title>
            </circle>
          );
        })}

        {/* Value annotations */}
        <text x={xMin} y="30" fill="#9CA3AF" fontSize="10" textAnchor="middle">Min: {min}</text>
        <text x={xQ1} y="100" fill="#9CA3AF" fontSize="10" textAnchor="middle">Q1: {q1}</text>
        <text x={xMed} y="30" fill="#F59E0B" fontSize="10" fontWeight="bold" textAnchor="middle">Med: {median}</text>
        <text x={xQ3} y="100" fill="#9CA3AF" fontSize="10" textAnchor="middle">Q3: {q3}</text>
        <text x={xMax} y="30" fill="#9CA3AF" fontSize="10" textAnchor="middle">Max: {max}</text>
      </svg>
    </div>
  );
}
