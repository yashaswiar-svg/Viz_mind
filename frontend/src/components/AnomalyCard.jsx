import React from 'react';

export default function AnomalyCard({ anomaly }) {
  const {
    column_name,
    observation_reference,
    value,
    anomaly_score,
    severity,
    methods_detected,
    expected_range,
    evidence,
  } = anomaly;

  const severityColors = {
    HIGH: 'bg-red-500/20 text-red-400 border-red-500/40',
    MEDIUM: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
    LOW: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
    NORMAL: 'bg-slate-500/20 text-slate-400 border-slate-500/40',
  };

  const badgeStyle = severityColors[severity] || severityColors.NORMAL;

  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 hover:border-slate-600 transition-all duration-200">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-semibold text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded border border-emerald-800/50">
            {column_name}
          </span>
          <span className="text-xs text-slate-400 font-mono">
            {observation_reference}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Score: <strong className="text-white">{anomaly_score}</strong></span>
          <span className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${badgeStyle}`}>
            {severity}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3 text-sm bg-slate-900/60 p-3 rounded-lg border border-slate-800">
        <div>
          <div className="text-xs text-slate-400">Observed Value</div>
          <div className="font-mono font-medium text-white text-base">
            {value !== null && value !== undefined ? value.toLocaleString() : 'N/A'}
          </div>
        </div>
        <div>
          <div className="text-xs text-slate-400">Expected Range</div>
          <div className="font-mono text-slate-300 text-sm">
            {expected_range ? `[${expected_range.lower_bound?.toFixed(2)}, ${expected_range.upper_bound?.toFixed(2)}]` : 'N/A'}
          </div>
        </div>
      </div>

      <div className="text-xs text-slate-400 space-y-1">
        <div><strong className="text-slate-300">Methods Detected:</strong> {methods_detected?.join(', ')}</div>
        {evidence && Object.keys(evidence).map((m) => (
          <div key={m} className="font-mono text-slate-400 text-[11px] truncate">
            {m}: {JSON.stringify(evidence[m])}
          </div>
        ))}
      </div>
    </div>
  );
}
