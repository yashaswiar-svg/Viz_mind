import React from 'react';

export default function PredictionMetrics({ run }) {
  if (!run) return null;

  const { problem_type, metrics, baseline_metrics } = run;

  if (problem_type === 'REGRESSION' || problem_type === 'FORECASTING') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Mean Absolute Error (MAE)</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-bold text-white font-mono">{metrics?.mae}</span>
            <span className="text-xs text-slate-400 font-mono">Baseline: {baseline_metrics?.mae}</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Root Mean Squared Error (RMSE)</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-bold text-white font-mono">{metrics?.rmse}</span>
            <span className="text-xs text-slate-400 font-mono">Baseline: {baseline_metrics?.rmse}</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">R² Variance Explained</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-bold text-emerald-400 font-mono">
              {metrics?.r2 !== undefined ? metrics.r2 : 'N/A'}
            </span>
            <span className="text-xs text-slate-400 font-mono">
              Baseline: {baseline_metrics?.r2 !== undefined ? baseline_metrics.r2 : '0.0'}
            </span>
          </div>
        </div>
      </div>
    );
  }

  if (problem_type === 'CLASSIFICATION') {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Accuracy</div>
          <div className="flex items-baseline justify-between mt-1">
            <span className="text-2xl font-bold text-white font-mono">{metrics?.accuracy}</span>
            <span className="text-xs text-slate-400 font-mono">Base: {baseline_metrics?.accuracy}</span>
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Precision</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">{metrics?.precision}</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">Recall</div>
          <div className="text-2xl font-bold text-white font-mono mt-1">{metrics?.recall}</div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl">
          <div className="text-xs text-slate-400">F1 Score</div>
          <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">{metrics?.f1}</div>
        </div>
      </div>
    );
  }

  return null;
}
