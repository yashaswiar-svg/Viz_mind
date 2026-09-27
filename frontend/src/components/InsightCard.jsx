import React from 'react';

export default function InsightCard({ insight, onSelect }) {
  if (!insight) return null;

  const getImportanceBadge = (level) => {
    switch (level) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'LOW':
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getStrengthBadge = (strength) => {
    switch (strength) {
      case 'STRONG':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'MODERATE':
        return 'bg-sky-100 text-sky-800 border-sky-200';
      case 'WEAK':
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const isFallback = insight.generation_mode === 'DETERMINISTIC_FALLBACK';

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow flex flex-col justify-between space-y-4">
      <div className="space-y-3">
        {/* Header Badges */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-800 border border-gray-300">
              {insight.insight_type?.replace('_', ' ')}
            </span>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getImportanceBadge(
                insight.importance_level
              )}`}
            >
              {insight.importance_level} Importance ({insight.importance_score?.toFixed(1)})
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStrengthBadge(
                insight.evidence_strength
              )}`}
            >
              {insight.evidence_strength} Evidence
            </span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-mono font-medium ${
                isFallback
                  ? 'bg-amber-50 text-amber-700 border border-amber-200'
                  : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              }`}
            >
              {isFallback ? 'Deterministic Explanation' : 'AI Explanation'}
            </span>
          </div>
        </div>

        {/* Title & Summary */}
        <div>
          <h3 className="text-base font-bold text-gray-900 leading-snug">
            {insight.title}
          </h3>
          <p className="text-sm text-gray-600 mt-1 line-clamp-3 leading-relaxed">
            {insight.summary}
          </p>
        </div>

        {/* Target Columns */}
        {insight.columns && insight.columns.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-xs text-gray-400 font-medium">Columns:</span>
            {insight.columns.map((c) => (
              <span
                key={c}
                className="px-2 py-0.5 bg-gray-100 text-gray-700 rounded text-xs font-mono"
              >
                {c}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Action Footer */}
      <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
        <span className="text-xs text-gray-500 font-mono">
          {insight.evidence_items?.length || 0} grounded evidence items
        </span>
        <button
          onClick={() => onSelect(insight)}
          className="inline-flex items-center px-3 py-1.5 text-xs font-semibold rounded-lg text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
        >
          View Full Narrative & Evidence →
        </button>
      </div>
    </div>
  );
}
