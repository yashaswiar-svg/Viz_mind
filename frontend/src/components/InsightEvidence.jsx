import React from 'react';

export default function InsightEvidence({ evidenceItems = [] }) {
  if (!evidenceItems || evidenceItems.length === 0) {
    return (
      <div className="text-gray-500 italic text-sm py-2">
        No linked evidence items recorded.
      </div>
    );
  }

  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'PHASE3_PROFILE':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'PHASE5_VISUALIZATION':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'PHASE6_PATTERN':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'PHASE7_ANOMALY':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'PHASE7_PREDICTION':
        return 'bg-teal-100 text-teal-800 border-teal-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="space-y-3 mt-2">
      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Grounded Evidence ({evidenceItems.length})
      </h4>
      <div className="grid grid-cols-1 gap-2">
        {evidenceItems.map((ev) => (
          <div
            key={ev.id || ev.evidence_id}
            className="p-3 bg-gray-50 rounded-lg border border-gray-200 text-sm space-y-1"
          >
            <div className="flex items-center justify-between">
              <span className="font-mono font-semibold text-xs text-gray-700">
                {ev.evidence_id}
              </span>
              <span
                className={`text-xs px-2 py-0.5 rounded border font-medium ${getPhaseColor(
                  ev.source_phase
                )}`}
              >
                {ev.source_phase?.replace('PHASE', 'Phase ')} — {ev.source_type}
              </span>
            </div>
            <p className="text-gray-800 font-medium text-xs leading-relaxed">
              {ev.description}
            </p>
            {ev.metrics && Object.keys(ev.metrics).length > 0 && (
              <div className="mt-1 pt-1 border-t border-gray-200 text-xs text-gray-600 font-mono flex flex-wrap gap-x-3 gap-y-1">
                {Object.entries(ev.metrics).map(([k, v]) => {
                  if (typeof v === 'object' && v !== null) return null;
                  return (
                    <span key={k}>
                      <strong className="text-gray-700">{k}:</strong>{' '}
                      {typeof v === 'number' ? v.toFixed(4) : String(v)}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
