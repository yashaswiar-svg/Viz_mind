import React, { useState, useEffect } from 'react';
import { runPrediction, getLatestPrediction, getDatasetProfile } from '../services/api';
import PredictionSummary from './PredictionSummary';
import PredictionMetrics from './PredictionMetrics';
import PredictionResults from './PredictionResults';

export default function PredictionView({ datasetId }) {
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [eligibleTargets, setEligibleTargets] = useState([]);
  const [selectedTarget, setSelectedTarget] = useState('');
  const [problemType, setProblemType] = useState('AUTO');

  useEffect(() => {
    if (!datasetId) return;

    const loadProfile = async () => {
      try {
        const prof = await getDatasetProfile(datasetId);
        if (prof?.columns) {
          const validCols = prof.columns
            .filter((c) => !c.is_identifier && !c.is_constant && c.semantic_type !== 'IDENTIFIER' && c.semantic_type !== 'FREE_TEXT')
            .map((c) => c.column_name);
          setEligibleTargets(validCols);
          if (validCols.length > 0 && !selectedTarget) {
            setSelectedTarget(validCols[0]);
          }
        }
      } catch (err) {
        console.error('Failed to load dataset profile for targets:', err);
      }
    };

    loadProfile();
  }, [datasetId]);

  const fetchPrediction = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getLatestPrediction(datasetId);
      setRun(data);
    } catch (err) {
      if (err.code === 'PREDICTION_RUN_NOT_FOUND' || err.code === 'NOT_FOUND') {
        setRun(null);
      } else {
        setError(err.message || 'Failed to fetch prediction run.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, [datasetId]);

  const handleRunPrediction = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const targetArg = selectedTarget || null;
      const probTypeArg = problemType !== 'AUTO' ? problemType : null;

      const data = await runPrediction(datasetId, targetArg, probTypeArg);
      setRun(data);
    } catch (err) {
      setError(err.message || 'Prediction execution failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-slate-900/80 p-6 rounded-2xl border border-slate-800">
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-extrabold text-white tracking-tight mb-1">
              Prediction & Forecasting Intelligence
            </h1>
            <p className="text-sm text-slate-400">
              Supervised machine learning pipelines (Linear & Logistic Regression) and Naive Time-Series Forecasting.
            </p>
          </div>
        </div>

        {/* Configuration Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 mb-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Target Column (Outcome)
            </label>
            <select
              value={selectedTarget}
              onChange={(e) => setSelectedTarget(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-emerald-500"
            >
              {eligibleTargets.length === 0 && <option value="">No eligible targets found</option>}
              {eligibleTargets.map((col) => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Problem Type
            </label>
            <select
              value={problemType}
              onChange={(e) => setProblemType(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-emerald-500"
            >
              <option value="AUTO">Auto Detect (Recommended)</option>
              <option value="REGRESSION">Regression (Numerical)</option>
              <option value="CLASSIFICATION">Classification (Categorical/Binary)</option>
              <option value="FORECASTING">Time-Series Forecasting</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRunPrediction}
              disabled={loading || !selectedTarget}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition-all shadow-lg shadow-emerald-900/40"
            >
              {loading ? 'Fitting Pipeline...' : run ? 'Train & Evaluate Model' : 'Start Prediction'}
            </button>
          </div>
        </div>

        {/* Statistical Disclaimer */}
        <div className="bg-amber-950/30 border border-amber-800/40 rounded-xl p-3.5 text-xs text-amber-300">
          <strong>Statistical Disclaimer:</strong> Prediction outputs are historical model estimates based on held-out test data. 
          Predictions do <em>not</em> represent guaranteed future outcomes.
        </div>
      </div>

      {error && (
        <div className="bg-red-950/40 border border-red-800/50 p-4 rounded-xl text-red-300 text-sm">
          <strong>Error:</strong> {error}
        </div>
      )}

      {!run && !loading && !error && (
        <div className="text-center py-16 bg-slate-900/40 border border-slate-800 rounded-2xl">
          <h3 className="text-lg font-semibold text-slate-300 mb-2">No Prediction Model Trained Yet</h3>
          <p className="text-sm text-slate-400 mb-6 max-w-md mx-auto">
            Select a target column and click "Start Prediction" to train a baseline and candidate supervised model.
          </p>
        </div>
      )}

      {run && (
        <>
          <PredictionSummary run={run} />
          <PredictionMetrics run={run} />
          <PredictionResults datasetId={datasetId} runId={run.id} />
        </>
      )}
    </div>
  );
}
