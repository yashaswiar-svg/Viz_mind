import React, { useState, useEffect } from 'react';
import { generateInsights, getInsights } from '../services/api';
import InsightSummary from './InsightSummary';
import InsightCard from './InsightCard';
import InsightDetail from './InsightDetail';

export default function InsightView({ datasetId }) {
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [insightData, setInsightData] = useState(null);
  const [selectedInsight, setSelectedInsight] = useState(null);

  // Filters
  const [filterType, setFilterType] = useState('ALL');
  const [filterImportance, setFilterImportance] = useState('ALL');

  useEffect(() => {
    if (datasetId) {
      loadInsights();
    }
  }, [datasetId]);

  async function loadInsights() {
    setLoading(true);
    setError(null);
    try {
      const data = await getInsights(datasetId);
      setInsightData(data);
    } catch (err) {
      console.error('Error fetching insights:', err);
      setError(err.message || 'Failed to load insights.');
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      const data = await generateInsights(datasetId);
      setInsightData(data);
    } catch (err) {
      console.error('Error generating insights:', err);
      setError(err.message || 'Failed to generate AI insights.');
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 space-y-4">
        <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-sm font-medium text-gray-600">Loading AI Insight Engine...</p>
      </div>
    );
  }

  const hasRun = insightData && insightData.latest_run;
  const insights = insightData?.insights || [];

  // Filter insights
  const filteredInsights = insights.filter((item) => {
    if (filterType !== 'ALL' && item.insight_type !== filterType) return false;
    if (filterImportance !== 'ALL' && item.importance_level !== filterImportance) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      {hasRun && (
        <InsightSummary
          run={insightData.latest_run}
          totalInsights={insightData.total_insights}
          fallbackActive={insightData.fallback_active}
          disclaimer={insightData.disclaimer}
        />
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-800 text-sm flex items-center justify-between">
          <div>
            <strong className="font-semibold">Insight Engine Notice:</strong> {error}
          </div>
          <button
            onClick={handleGenerate}
            className="px-3 py-1 bg-red-600 text-white rounded-lg text-xs font-semibold hover:bg-red-700 transition-colors"
          >
            Retry Generation
          </button>
        </div>
      )}

      {/* Initial Empty State / Generate Trigger */}
      {!hasRun && !generating && (
        <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm max-w-xl mx-auto space-y-4 my-8">
          <div className="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto text-2xl font-bold">
            ✨
          </div>
          <h3 className="text-xl font-bold text-gray-900">AI Insight Engine</h3>
          <p className="text-sm text-gray-600 leading-relaxed">
            Generate explainable, evidence-grounded analytical narratives based on pre-computed Phase 3–7 profiles, visualizations, patterns, anomalies, and predictions.
          </p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl text-sm shadow-md transition-all inline-flex items-center space-x-2"
          >
            <span>Generate AI Insights</span>
            <span>→</span>
          </button>
        </div>
      )}

      {/* Generating State */}
      {generating && (
        <div className="bg-white rounded-2xl border border-indigo-100 p-12 text-center shadow-sm max-w-xl mx-auto space-y-4 my-8">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <h3 className="text-lg font-bold text-gray-900">Generating AI Insights...</h3>
          <p className="text-xs text-gray-500">
            Aggregating analytical evidence, generating candidates, scoring importance, and building grounded explanations.
          </p>
        </div>
      )}

      {/* Main Content Area */}
      {hasRun && !generating && (
        <div className="space-y-4">
          {/* Controls Bar */}
          <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-3">
              {/* Insight Type Filter */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="font-semibold text-gray-500">Type:</span>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  className="bg-gray-50 border border-gray-300 text-gray-800 rounded-lg px-2.5 py-1 focus:ring-indigo-500 font-medium"
                >
                  <option value="ALL">All Types ({insights.length})</option>
                  <option value="DATA_QUALITY">Data Quality</option>
                  <option value="CORRELATION">Correlation</option>
                  <option value="GROUP_DIFFERENCE">Group Difference</option>
                  <option value="CATEGORICAL_ASSOCIATION">Categorical Association</option>
                  <option value="TREND">Trend</option>
                  <option value="DISTRIBUTION">Distribution</option>
                  <option value="ANOMALY">Anomaly</option>
                  <option value="PREDICTION">Prediction</option>
                  <option value="FORECAST">Forecast</option>
                  <option value="VISUALIZATION">Visualization</option>
                  <option value="CROSS_MODULE">Cross Module</option>
                </select>
              </div>

              {/* Importance Filter */}
              <div className="flex items-center space-x-2 text-xs">
                <span className="font-semibold text-gray-500">Importance:</span>
                <select
                  value={filterImportance}
                  onChange={(e) => setFilterImportance(e.target.value)}
                  className="bg-gray-50 border border-gray-300 text-gray-800 rounded-lg px-2.5 py-1 focus:ring-indigo-500 font-medium"
                >
                  <option value="ALL">All Levels</option>
                  <option value="HIGH">High Importance</option>
                  <option value="MEDIUM">Medium Importance</option>
                  <option value="LOW">Low Importance</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors flex items-center space-x-1.5"
            >
              <span>↻ Regenerate Insights</span>
            </button>
          </div>

          {/* Insights Grid */}
          {filteredInsights.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredInsights.map((ins) => (
                <InsightCard
                  key={ins.id}
                  insight={ins}
                  onSelect={setSelectedInsight}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-500 text-sm">
              No insights match the selected filter criteria.
            </div>
          )}
        </div>
      )}

      {/* Insight Detail Modal */}
      {selectedInsight && (
        <InsightDetail
          insight={selectedInsight}
          onClose={() => setSelectedInsight(null)}
        />
      )}
    </div>
  );
}
