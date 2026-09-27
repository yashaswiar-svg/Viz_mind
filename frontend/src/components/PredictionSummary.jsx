import React from 'react';

export default function PredictionSummary({ run }) {
  if (!run) return null;

  const {
    target_column,
    problem_type,
    model_name,
    training_rows,
    validation_rows,
    test_rows,
    feature_columns,
    metrics,
  } = run;

  const improvement = metrics?.improvement || {};

  return (
    <div className="bg-slate-800/90 border border-slate-700/80 rounded-2xl p-6 mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-bold font-mono px-2.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
              {problem_type}
            </span>
            <span className="text-xs text-slate-400 font-mono">Model: {model_name}</span>
          </div>
          <h2 className="text-xl font-bold text-white">Target: <span className="text-emerald-400">{target_column}</span></h2>
        </div>

        {improvement.is_better && (
          <div className="bg-emerald-950/60 border border-emerald-700/60 px-4 py-2 rounded-xl text-right">
            <div className="text-[11px] text-emerald-400 font-medium">Outperformed Naive Baseline</div>
            <div className="text-sm font-bold text-white font-mono">
              {problem_type === 'CLASSIFICATION'
                ? `+${improvement.accuracy_gain_pct}% Accuracy`
                : `${improvement.mae_reduction_pct}% MAE Reduction`}
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Train Split (60%)</div>
          <div className="text-lg font-bold text-white font-mono">{training_rows} rows</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Validation Split (20%)</div>
          <div className="text-lg font-bold text-white font-mono">{validation_rows} rows</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Test Split (20%)</div>
          <div className="text-lg font-bold text-emerald-400 font-mono">{test_rows} rows</div>
        </div>
        <div className="bg-slate-900/60 border border-slate-800 p-3.5 rounded-xl">
          <div className="text-xs text-slate-400">Features Selected</div>
          <div className="text-lg font-bold text-white font-mono">{feature_columns?.length || 0}</div>
        </div>
      </div>

      <div className="text-xs text-slate-400">
        <strong className="text-slate-300">Feature Predictors:</strong> {feature_columns?.join(', ')}
      </div>
    </div>
  );
}
