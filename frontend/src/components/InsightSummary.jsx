import React from 'react';

export default function InsightSummary({ run, totalInsights, fallbackActive, disclaimer }) {
  const highCount = run ? run.insight_count : totalInsights;

  return (
    <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-xl p-6 shadow-md mb-6 space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold tracking-tight">AI Insight Dashboard</h2>
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold tracking-wide border ${
                fallbackActive
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              }`}
            >
              {fallbackActive ? 'Deterministic Fallback Active' : 'AI Explanation Mode Active'}
            </span>
          </div>
          <p className="text-slate-300 text-xs mt-1">
            Explainable analytical narratives grounded strictly in pre-computed Phase 3–7 evidence.
          </p>
        </div>

        {/* Metric Badges */}
        <div className="flex items-center space-x-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 text-center border border-white/10">
            <span className="block text-2xl font-extrabold text-white">{totalInsights}</span>
            <span className="text-xs text-slate-300 font-medium">Total Insights</span>
          </div>

          {run && (
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 text-center border border-white/10">
              <span className="block text-2xl font-extrabold text-emerald-400">
                {run.evidence_count}
              </span>
              <span className="text-xs text-slate-300 font-medium">Grounded Evidences</span>
            </div>
          )}

          {run && (
            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-2 text-center border border-white/10">
              <span className="block text-2xl font-extrabold text-indigo-300">
                {run.candidate_count}
              </span>
              <span className="text-xs text-slate-300 font-medium">Candidates Evaluated</span>
            </div>
          )}
        </div>
      </div>

      {/* Product Disclaimer */}
      <div className="bg-white/5 border border-white/10 rounded-lg p-3 text-xs text-slate-300 flex items-start space-x-2">
        <span className="text-amber-400 font-bold text-sm leading-none">ℹ</span>
        <p className="leading-relaxed">
          {disclaimer ||
            "The analytical values shown here come from VizMind's statistical and machine-learning engines. AI is used to explain those computed results and does not independently calculate the underlying statistics."}
        </p>
      </div>
    </div>
  );
}
