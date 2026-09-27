import React, { useEffect, useState } from 'react';
import { listDatasets, deleteDataset } from '../services/api';
import { DatasetMetadataModal } from './DatasetMetadataModal';
import { Database, Eye, Trash2, ChevronLeft, ChevronRight, RefreshCw, Activity, Sparkles, Bot } from 'lucide-react';

export function DatasetList({ refreshTrigger, onRefresh, onSelectDatasetForProfile, onSelectDatasetForPatterns, onSelectDatasetForAnomalies, onSelectDatasetForPredictions, onSelectDatasetForInsights, onSelectDatasetForAnalyst }) {


  const [datasets, setDatasets] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState(null);

  const fetchDatasets = async (currentPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await listDatasets(currentPage, pageSize);
      setDatasets(data.items || []);
      setTotal(data.total || 0);
      setPage(data.page || 1);
    } catch (err) {
      setError(err.message || 'Failed to load dataset list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets(page);
  }, [page, refreshTrigger]);

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete dataset "${name}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deleteDataset(id);
      fetchDatasets(page);
      if (onRefresh) onRefresh();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Database size={22} color="#06b6d4" /> Registered Datasets ({total})
        </h3>
        <button
          className="btn-secondary"
          onClick={() => fetchDatasets(page)}
          style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
        >
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {error && (
        <div style={{ color: '#fca5a5', padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius-sm)', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading dataset inventory...
        </div>
      ) : datasets.length === 0 ? (
        <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', background: 'var(--bg-glass)', borderRadius: 'var(--radius-sm)' }}>
          <Database size={36} style={{ marginBottom: '0.5rem', opacity: 0.4 }} />
          <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.25rem' }}>No datasets uploaded yet</div>
          <div style={{ fontSize: '0.8125rem' }}>Upload your first CSV or Excel file above to begin.</div>
        </div>
      ) : (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Name</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Original Filename</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Format</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Size</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Created</th>
                  <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((ds) => (
                  <tr key={ds.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                    <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>{ds.name}</td>
                    <td style={{ padding: '0.85rem 1rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                      {ds.original_filename}
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <span style={{ textTransform: 'uppercase', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                        {ds.file_type}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-secondary)' }}>
                      {formatBytes(ds.file_size)}
                    </td>
                    <td style={{ padding: '0.85rem 1rem' }}>
                      <span className="capability-status status-ready">{ds.status}</span>
                    </td>
                    <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                      {new Date(ds.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem' }}>
                        {onSelectDatasetForProfile && (
                          <button
                            className="btn-primary"
                            onClick={() => onSelectDatasetForProfile(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                            title="Profile & Analyze Dataset"
                          >
                            <Activity size={14} /> Profile
                          </button>
                        )}
                        {onSelectDatasetForPatterns && (
                          <button
                            className="btn-secondary"
                            onClick={() => onSelectDatasetForPatterns(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#38bdf8', borderColor: 'rgba(56, 189, 248, 0.4)' }}
                            title="Pattern Discovery Intelligence"
                          >
                            <Sparkles size={14} /> Patterns
                          </button>
                        )}
                        {onSelectDatasetForAnomalies && (
                          <button
                            className="btn-secondary"
                            onClick={() => onSelectDatasetForAnomalies(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#f59e0b', borderColor: 'rgba(245, 158, 11, 0.4)' }}
                            title="Anomaly Detection Intelligence"
                          >
                            Anomalies
                          </button>
                        )}
                        {onSelectDatasetForPredictions && (
                          <button
                            className="btn-secondary"
                            onClick={() => onSelectDatasetForPredictions(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#10b981', borderColor: 'rgba(16, 185, 129, 0.4)' }}
                            title="Prediction & Forecasting Intelligence"
                          >
                            Prediction
                          </button>
                        )}
                        {onSelectDatasetForInsights && (
                          <button
                            className="btn-secondary"
                            onClick={() => onSelectDatasetForInsights(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#a855f7', borderColor: 'rgba(168, 85, 247, 0.4)' }}
                            title="AI Insight Engine"
                          >
                            <Sparkles size={14} /> AI Insights
                          </button>
                        )}
                        {onSelectDatasetForAnalyst && (
                          <button
                            className="btn-secondary"
                            onClick={() => onSelectDatasetForAnalyst(ds)}
                            style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', color: '#06b6d4', borderColor: 'rgba(6, 182, 212, 0.4)' }}
                            title="Natural Language Analyst Chat"
                          >
                            <Bot size={14} /> Analyst Chat
                          </button>
                        )}


                        <button
                          className="btn-secondary"
                          onClick={() => setSelectedDataset(ds)}
                          style={{ padding: '0.35rem 0.6rem' }}
                          title="View Metadata"
                        >
                          <Eye size={15} />
                        </button>
                        <button
                          onClick={() => handleDelete(ds.id, ds.name)}
                          style={{
                            background: 'rgba(239, 68, 68, 0.15)',
                            color: '#ef4444',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            padding: '0.35rem 0.6rem',
                            borderRadius: 'var(--radius-sm)',
                            cursor: 'pointer',
                          }}
                          title="Delete Dataset"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              Page {page} of {totalPages} ({total} total datasets)
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                className="btn-secondary"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                style={{ opacity: page <= 1 ? 0.5 : 1, padding: '0.4rem 0.75rem' }}
              >
                <ChevronLeft size={16} /> Prev
              </button>
              <button
                className="btn-secondary"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                style={{ opacity: page >= totalPages ? 0.5 : 1, padding: '0.4rem 0.75rem' }}
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </>
      )}

      <DatasetMetadataModal
        dataset={selectedDataset}
        onClose={() => setSelectedDataset(null)}
      />
    </div>
  );
}
