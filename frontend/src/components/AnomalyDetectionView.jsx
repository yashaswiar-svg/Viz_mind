import React, { useState, useEffect } from 'react';
import { runAnomalyDetection, getLatestAnomalies } from '../services/api';
import AnomalySummary from './AnomalySummary';
import AnomalyCard from './AnomalyCard';

export default function AnomalyDetectionView({ datasetId }) {
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [columnFilter, setColumnFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const fetchAnomalies = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getLatestAnomalies(datasetId);
      setRun(data);
    } catch (err) {
      if (err.code === 'ANOMALY_RUN_NOT_FOUND' || err.code === 'NOT_FOUND') {
        setRun(null);
      } else {
        setError(err.message || 'Failed to fetch anomaly detection run.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomalies();
  }, [datasetId]);

  const handleRunDetection = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await runAnomalyDetection(datasetId);
      setRun(data);
    } catch (err) {
      setError(err.message || 'Anomaly detection analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  const filteredResults = (run?.results || []).filter((item) => {
    if (columnFilter !== 'ALL' && item.column_name !== columnFilter) return false;
    if (severityFilter !== 'ALL' && item.severity !== severityFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight mb-1">
            Anomaly Detection Intelligence
          </h1>
          <p className="text-sm text-slate-400">
            Automated IQR & Robust Z-Score outlier detection with statistical evidence.
          </p>
        </div>
        <button
          onClick={handleRunDetection}
          disabled={loading}
          className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-emerald-900/40 flex items-center gap-2"
        >
          {loading ? 'Analyzing...' : run ? 'Rerun Anomaly Detection' : 'Run Anomaly Detection'}
        </button>
      </div>

      {/* Analytical Disclaimer */}
      <div className="bg-amber-950/30 border border-amber-800/40 rounded-xl p-4 text-xs text-amber-300">
        <strong>Statistical Disclaimer:</strong> Anomaly detection identifies statistically unusual observations. 
        An anomaly does <em>not</em> automatically imply data entry error, fraud, or causation.
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/50 p-4 rounded-xl text-red-300 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {!run && !loading && !error && (
        <div className="text-center py-16 bg-slate-900/40 border border-slate-800 rounded-2xl">
          <h3 className="text-lg font-semibold text-slate-300 mb-2">Not Analyzed Yet</h3>
          <p className="text-sm text-slate-400 mb-6 max-w-md mx-auto">
            Click the button above to run univariate statistical anomaly detection on your preprocessed dataset.
          </p>
          <button
            onClick={handleRunDetection}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-all"
          >
            Run Anomaly Detection
          </button>
        </div>
      )}

      {run && (
        <>
          <AnomalySummary
            run={run}
            columnFilter={columnFilter}
            setColumnFilter={setColumnFilter}
            severityFilter={severityFilter}
            setSeverityFilter={setSeverityFilter}
          />

          {filteredResults.length === 0 ? (
            <div className="text-center py-12 bg-slate-900/40 border border-slate-800 rounded-xl text-slate-400 text-sm">
              No anomalies match the selected filters.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredResults.map((anomaly) => (
                <AnomalyCard key={anomaly.id} anomaly={anomaly} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
