import React from 'react';
import InsightEvidence from './InsightEvidence';

export default function InsightDetail({ insight, onClose }) {
  if (!insight) return null;

  const isFallback = insight.generation_mode === 'DETERMINISTIC_FALLBACK';

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-3xl w-full shadow-2xl border border-gray-200 overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-start justify-between bg-slate-900 text-white">
          <div className="space-y-1 pr-4">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">
                {insight.insight_type?.replace('_', ' ')}
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                  isFallback
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                }`}
              >
                {isFallback ? 'Deterministic Fallback Explanation' : 'AI Explanation'}
              </span>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-white leading-snug">
              {insight.title}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg transition-colors text-lg font-bold"
          >
            ✕
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1 text-gray-800">
          {/* Executive Summary */}
          <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
            <h3 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-1">
              Executive Summary
            </h3>
            <p className="text-sm text-indigo-950 font-medium leading-relaxed">
              {insight.summary}
            </p>
          </div>

          {/* Detailed Narrative */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">
              Why this insight was generated
            </h3>
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 text-sm text-gray-800 leading-relaxed whitespace-pre-line">
              {insight.explanation}
            </div>
          </div>

          {/* Grounded Evidence Items */}
          <InsightEvidence evidenceItems={insight.evidence_items} />

          {/* Limitations */}
          {insight.limitations && insight.limitations.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-amber-800 uppercase tracking-wider">
                Analytical Limitations & Scope
              </h3>
              <ul className="list-disc list-inside space-y-1 bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900">
                {insight.limitations.map((lim, idx) => (
                  <li key={idx} className="leading-relaxed">
                    {lim}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Validation Status: <strong className="text-gray-700">{insight.validation_status}</strong>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            Close Detail
          </button>
        </div>
      </div>
    </div>
  );
}
