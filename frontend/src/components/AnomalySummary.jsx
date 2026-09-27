import React from 'react';

export default function AnomalySummary({ run, columnFilter, setColumnFilter, severityFilter, setSeverityFilter }) {
  if (!run) return null;

  const {
    total_observations,
    anomaly_count,
    anomaly_percentage,
    results_truncated,
    results,
  } = run;

  const highCount = results.filter((r) => r.severity === 'HIGH').length;
  const medCount = results.filter((r) => r.severity === 'MEDIUM').length;
  const lowCount = results.filter((r) => r.severity === 'LOW').length;

  const uniqueColumns = Array.from(new Set(results.map((r) => r.column_name)));

  return (
    <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">Anomaly Detection Summary</h2>
          <p className="text-xs text-slate-400">
            Univariate statistical outlier identification across numerical features.
          </p>
        </div>
        {results_truncated && (
          <span className="text-xs font-semibold px-3 py-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-full">
            Results Truncated (showing 500 max)
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Total Observations</div>
          <div className="text-2xl font-bold text-white font-mono">{total_observations}</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Anomalies Detected</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            {anomaly_count} <span className="text-xs text-slate-400">({anomaly_percentage}%)</span>
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Severity Breakdown</div>
          <div className="text-xs font-semibold flex items-center gap-2 mt-2">
            <span className="text-red-400">High: {highCount}</span>
            <span className="text-amber-400">Med: {medCount}</span>
            <span className="text-blue-400">Low: {lowCount}</span>
          </div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Detection Methods</div>
          <div className="text-xs font-mono text-slate-300 mt-2">IQR + Robust Z-Score</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-slate-700/60">
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-300">Column:</label>
          <select
            value={columnFilter}
            onChange={(e) => setColumnFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Columns</option>
            {uniqueColumns.map((col) => (
              <option key={col} value={col}>{col}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-300">Severity:</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-emerald-500"
          >
            <option value="ALL">All Severities</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>
      </div>
    </div>
  );
}
