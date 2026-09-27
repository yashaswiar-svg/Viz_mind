import React, { useState, useEffect } from 'react';
import { getPredictionResults } from '../services/api';

export default function PredictionResults({ datasetId, runId }) {
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  const [loading, setLoading] = useState(false);

  const fetchPage = async (newOffset) => {
    if (!datasetId || !runId) return;
    setLoading(true);
    try {
      const data = await getPredictionResults(datasetId, runId, newOffset, limit);
      setResults(data.items || []);
      setTotal(data.total || 0);
      setOffset(newOffset);
    } catch (err) {
      console.error('Failed to fetch prediction results:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPage(0);
  }, [datasetId, runId]);

  const totalPages = Math.ceil(total / limit) || 1;
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white">Prediction & Forecast Output (Paginated)</h3>
        <span className="text-xs text-slate-400 font-mono">
          Showing {results.length} of {total} items
        </span>
      </div>

      <div className="overflow-x-auto mb-4">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-semibold bg-slate-950/60">
              <th className="p-3">Reference</th>
              <th className="p-3">Split</th>
              <th className="p-3">Actual Value</th>
              <th className="p-3">Predicted Value</th>
              <th className="p-3">Error / Residual</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {results.map((res) => (
              <tr key={res.id} className="hover:bg-slate-800/40">
                <td className="p-3 text-slate-300 font-medium">{res.observation_reference}</td>
                <td className="p-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    res.split === 'FUTURE_FORECAST' 
                      ? 'bg-purple-950 text-purple-300 border border-purple-800' 
                      : 'bg-slate-800 text-slate-300'
                  }`}>
                    {res.split}
                  </span>
                </td>
                <td className="p-3 text-slate-200">{res.actual_value !== null ? res.actual_value : '— (Future)'}</td>
                <td className="p-3 font-semibold text-emerald-400">{res.predicted_value}</td>
                <td className="p-3 text-slate-400">{res.prediction_error !== null ? res.prediction_error : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <div>Page {currentPage} of {totalPages}</div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchPage(Math.max(0, offset - limit))}
            disabled={offset === 0 || loading}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 font-medium rounded-lg"
          >
            Previous
          </button>
          <button
            onClick={() => fetchPage(offset + limit)}
            disabled={offset + limit >= total || loading}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 font-medium rounded-lg"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
