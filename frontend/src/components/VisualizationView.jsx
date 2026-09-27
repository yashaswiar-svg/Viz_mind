import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  Sparkles,
  RefreshCw,
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  ScatterChart as ScatterIcon,
  BoxSelect,
  AlertCircle,
  CheckCircle2,
} from 'lucide-react';
import { generateVisualizations, getVisualizations, getVisualizationData } from '../services/api';
import BoxPlotChart from './BoxPlotChart';

const CHART_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'];

export default function VisualizationView({ dataset, onNavigateToPreprocessing }) {
  const [recommendations, setRecommendations] = useState([]);
  const [chartDataMap, setChartDataMap] = useState({});
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async (triggerGenerate = false) => {
    try {
      setLoading(true);
      setError(null);
      let recs = [];

      if (triggerGenerate) {
        setGenerating(true);
        const report = await generateVisualizations(dataset.id);
        recs = report.recommendations || [];
      } else {
        recs = await getVisualizations(dataset.id);
      }

      setRecommendations(recs);

      // Fetch aggregated data for each recommendation card asynchronously
      const dataPromises = recs.map(async (rec) => {
        try {
          const dataPayload = await getVisualizationData(dataset.id, rec.id);
          return { id: rec.id, payload: dataPayload };
        } catch (err) {
          console.error(`Failed loading chart data for ${rec.id}:`, err);
          return { id: rec.id, error: err.message };
        }
      });

      const results = await Promise.all(dataPromises);
      const dataMap = {};
      results.forEach((res) => {
        dataMap[res.id] = res;
      });
      setChartDataMap(dataMap);
    } catch (err) {
      console.error('Error fetching visualizations:', err);
      if (err.code === 'PREPROCESSING_REQUIRED') {
        setError('Phase 4 preprocessing is required before generating visualizations.');
      } else {
        setError(err.message || 'Failed to load visualization recommendations.');
      }
    } finally {
      setLoading(false);
      setGenerating(false);
    }
  };

  useEffect(() => {
    if (dataset?.id) {
      fetchRecommendations(false);
    }
  }, [dataset?.id]);

  const renderChart = (rec) => {
    const dataObj = chartDataMap[rec.id];

    if (!dataObj) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500 animate-pulse">
          Loading chart data...
        </div>
      );
    }

    if (dataObj.error) {
      return (
        <div className="h-64 flex flex-col items-center justify-center text-red-400 text-xs text-center p-4">
          <AlertCircle className="w-6 h-6 mb-1" />
          {dataObj.error}
        </div>
      );
    }

    const chartData = dataObj.payload?.data || [];

    if (chartData.length === 0) {
      return (
        <div className="h-64 flex items-center justify-center text-gray-500 italic text-sm">
          No data available for chart rendering
        </div>
      );
    }

    switch (rec.chart_type) {
      case 'histogram':
        return (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="label" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
              <Bar dataKey="count" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="category" stroke="#9CA3AF" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
              <Bar dataKey="value" fill="#10B981" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        );

      case 'count_bar':
        return (
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="category" stroke="#9CA3AF" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
              <Bar dataKey="count" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
              <Line type="monotone" dataKey="value" stroke="#F59E0B" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        );

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={240}>
            <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="x" name={rec.x_column} stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <YAxis dataKey="y" name={rec.y_column} stroke="#9CA3AF" tick={{ fontSize: 10 }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#F3F4F6' }} />
              <Scatter name={rec.title} data={chartData} fill="#EC4899" />
            </ScatterChart>
          </ResponsiveContainer>
        );

      case 'boxplot':
        return <BoxPlotChart data={chartData} title={rec.title} />;

      default:
        return <div className="text-gray-400 text-sm text-center py-8">Unsupported chart type</div>;
    }
  };

  const getChartIcon = (type) => {
    switch (type) {
      case 'histogram':
      case 'bar':
      case 'count_bar':
        return <BarChart3 className="w-4 h-4 text-blue-400" />;
      case 'line':
        return <TrendingUp className="w-4 h-4 text-amber-400" />;
      case 'scatter':
        return <ScatterIcon className="w-4 h-4 text-pink-400" />;
      case 'boxplot':
        return <BoxSelect className="w-4 h-4 text-indigo-400" />;
      default:
        return <PieIcon className="w-4 h-4 text-green-400" />;
    }
  };

  if (loading || generating) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <Sparkles className="w-10 h-10 text-blue-400 animate-spin" />
        <h3 className="text-lg font-semibold text-gray-200">
          {generating ? 'Analyzing dataset & generating smart recommendations...' : 'Loading visualizations...'}
        </h3>
        <p className="text-sm text-gray-400">Classifying column roles, evaluating scores, and preparing aggregated specs</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-900 border border-red-800/50 rounded-xl p-8 text-center max-w-lg mx-auto my-10 space-y-4">
        <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
        <h3 className="text-lg font-semibold text-gray-200">Visualization Engine</h3>
        <p className="text-sm text-gray-400">{error}</p>
        {onNavigateToPreprocessing && (
          <button
            onClick={onNavigateToPreprocessing}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Go to Preprocessing
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold text-gray-100">Smart Visualization Intelligence</h2>
            <span className="px-2.5 py-1 bg-blue-950/60 border border-blue-800/50 text-blue-400 rounded-full text-xs font-semibold flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Phase 5 Ready
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Top {recommendations.length} recommended charts automatically planned and ranked for dataset{' '}
            <span className="text-gray-200 font-mono">{dataset?.name}</span>
          </p>
        </div>

        <button
          onClick={() => fetchRecommendations(true)}
          disabled={generating}
          className="flex items-center space-x-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors shadow-lg shadow-blue-600/20 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
          <span>Regenerate Recommendations</span>
        </button>
      </div>

      {/* Grid of Recommendation Cards */}
      {recommendations.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400 space-y-3">
          <Sparkles className="w-10 h-10 text-gray-600 mx-auto" />
          <p className="text-base font-medium text-gray-300">No visualization candidates found for this dataset.</p>
          <button
            onClick={() => fetchRecommendations(true)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg font-medium"
          >
            Trigger Recommendation Run
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {recommendations.map((rec) => {
            const dataObj = chartDataMap[rec.id];
            const isSampled = dataObj?.payload?.metadata?.sampled;

            return (
              <div
                key={rec.id}
                className="bg-gray-900/90 border border-gray-800 hover:border-gray-700 rounded-xl p-5 flex flex-col justify-between transition-all duration-200 shadow-md"
              >
                {/* Card Header */}
                <div className="space-y-3 mb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="w-7 h-7 bg-blue-950 text-blue-400 border border-blue-800/60 rounded-full text-xs font-bold flex items-center justify-center">
                        #{rec.rank}
                      </span>
                      <div className="flex items-center space-x-1.5 px-2.5 py-1 bg-gray-800/80 rounded-md text-xs font-medium text-gray-300">
                        {getChartIcon(rec.chart_type)}
                        <span className="capitalize">{rec.chart_type.replace('_', ' ')}</span>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      {isSampled && (
                        <span className="text-[10px] bg-amber-950/60 border border-amber-800/50 text-amber-400 px-2 py-0.5 rounded">
                          Sampled (5k)
                        </span>
                      )}
                      <span className="text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-full">
                        {Math.round(rec.score)}% Relevance
                      </span>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-base font-semibold text-gray-100">{rec.title}</h3>
                    <p className="text-xs text-gray-400 mt-1 leading-relaxed">{rec.reason}</p>
                  </div>
                </div>

                {/* Rendered Chart */}
                <div className="bg-gray-950/60 border border-gray-800/60 rounded-lg p-3 my-2">
                  {renderChart(rec)}
                </div>

                {/* Card Footer Details */}
                <div className="mt-3 pt-3 border-t border-gray-800/60 flex items-center justify-between text-xs text-gray-400">
                  <div>
                    <span className="text-gray-500">X-Axis: </span>
                    <span className="font-mono text-gray-300">{rec.x_column}</span>
                  </div>
                  {rec.y_column && (
                    <div>
                      <span className="text-gray-500">Y-Axis: </span>
                      <span className="font-mono text-gray-300">
                        {rec.aggregation ? `${rec.aggregation.toUpperCase()}(${rec.y_column})` : rec.y_column}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
