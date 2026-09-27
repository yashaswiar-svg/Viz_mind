import React, { useEffect, useState } from 'react';
import { getDatasetProfile, profileDataset } from '../services/api';
import {
  ArrowLeft,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Info,
  RefreshCw,
  Database,
  BarChart2,
  Layers,
  Sparkles,
  Wand2,
} from 'lucide-react';

export function DatasetProfileView({ dataset, onBack, onSelectPreprocess }) {
  const [profileState, setProfileState] = useState({
    status: 'idle', // idle, loading, ready, not_profiled, failed
    data: null,
    error: null,
  });
  const [activeFilter, setActiveFilter] = useState('all');

  const fetchExistingProfile = async () => {
    setProfileState({ status: 'loading', data: null, error: null });
    try {
      const data = await getDatasetProfile(dataset.id);
      setProfileState({ status: 'ready', data, error: null });
    } catch (err) {
      if (err.code === 'PROFILE_NOT_FOUND') {
        setProfileState({ status: 'not_profiled', data: null, error: null });
      } else {
        setProfileState({ status: 'failed', data: null, error: err.message });
      }
    }
  };

  const handleRunProfile = async () => {
    setProfileState({ status: 'loading', data: null, error: null });
    try {
      const data = await profileDataset(dataset.id);
      setProfileState({ status: 'ready', data, error: null });
    } catch (err) {
      setProfileState({ status: 'failed', data: null, error: err.message });
    }
  };

  useEffect(() => {
    if (dataset) {
      fetchExistingProfile();
    }
  }, [dataset]);

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10b981';
    if (score >= 75) return '#06b6d4';
    if (score >= 50) return '#f59e0b';
    return '#ef4444';
  };

  const { status, data, error } = profileState;

  return (
    <div style={{ paddingBottom: '3rem' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <button className="btn-secondary" onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Back to Datasets
        </button>

        {status === 'ready' && (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            {onSelectPreprocess && (
              <button className="btn-primary" onClick={() => onSelectPreprocess(dataset)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)' }}>
                <Wand2 size={16} /> Preprocess Dataset
              </button>
            )}
            <button className="btn-secondary" onClick={handleRunProfile} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <RefreshCw size={16} /> Recompute Profile
            </button>
          </div>
        )}
      </div>

      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span className="badge">
              <Sparkles size={14} /> Phase 3 Profile Engine
            </span>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.5rem' }}>{dataset.name}</h2>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              {dataset.original_filename} ({dataset.file_type.toUpperCase()})
            </div>
          </div>

          {status === 'ready' && data && (
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.05em' }}>
                Data Quality Score
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: getScoreColor(data.quality.score), lineHeight: 1 }}>
                {data.quality.score}
                <span style={{ fontSize: '1.25rem', color: 'var(--text-muted)' }}>/100</span>
              </div>
              <div style={{ marginTop: '0.25rem' }}>
                <span className="capability-status status-ready" style={{ background: `${getScoreColor(data.quality.score)}20`, color: getScoreColor(data.quality.score), border: `1px solid ${getScoreColor(data.quality.score)}40` }}>
                  {data.quality.level} Quality
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* State: Not Profiled */}
      {status === 'not_profiled' && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <Activity size={48} color="var(--accent-primary)" style={{ marginBottom: '1rem', opacity: 0.8 }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Dataset Not Profiled Yet</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto 1.5rem', fontSize: '0.9375rem' }}>
            Run the read-only profiling engine to analyze data types, missing values, column statistics, and compute the Data Quality Score.
          </p>
          <button className="btn-primary" onClick={handleRunProfile} style={{ padding: '0.75rem 1.75rem', fontSize: '0.9375rem' }}>
            <Sparkles size={18} /> Profile Dataset Now
          </button>
        </div>
      )}

      {/* State: Loading / Profiling */}
      {status === 'loading' && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <RefreshCw size={40} className="spin" style={{ animation: 'spin 1.2s linear infinite', color: 'var(--accent-cyan)', marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Analyzing Dataset Structure...</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Calculating row counts, unique values, missing percentages, statistical metrics, and evaluating quality rules.
          </p>
        </div>
      )}

      {/* State: Failed */}
      {status === 'failed' && (
        <div className="glass-card" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'center', padding: '3rem 2rem' }}>
          <AlertTriangle size={40} color="#ef4444" style={{ marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fca5a5', marginBottom: '0.5rem' }}>Profiling Execution Failed</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.875rem' }}>{error}</p>
          <button className="btn-secondary" onClick={handleRunProfile}>
            Retry Profiling
          </button>
        </div>
      )}

      {/* State: Profile Ready */}
      {status === 'ready' && data && (
        <>
          {/* Overview Cards */}
          <div className="status-grid" style={{ marginTop: 0, marginBottom: '2rem' }}>
            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Dataset Size</span>
                <Database size={18} color="var(--accent-primary)" />
              </div>
              <div className="status-value">{data.overview.rows.toLocaleString()}</div>
              <div className="status-detail">{data.overview.columns} columns {data.overview.sheet_name ? `(${data.overview.sheet_name})` : ''}</div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Missing Cells</span>
                <AlertTriangle size={18} color={data.overview.missing_cell_percentage > 10 ? '#f59e0b' : '#10b981'} />
              </div>
              <div className="status-value">{data.overview.missing_cell_percentage}%</div>
              <div className="status-detail">{data.overview.missing_cells.toLocaleString()} total missing cells</div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Duplicate Rows</span>
                <Layers size={18} color={data.overview.duplicate_row_percentage > 5 ? '#f59e0b' : '#10b981'} />
              </div>
              <div className="status-value">{data.overview.duplicate_row_percentage}%</div>
              <div className="status-detail">{data.overview.duplicate_rows.toLocaleString()} duplicate rows</div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Memory Footprint</span>
                <BarChart2 size={18} color="var(--accent-cyan)" />
              </div>
              <div className="status-value">{formatBytes(data.overview.memory_bytes)}</div>
              <div className="status-detail">In-memory DataFrame size</div>
            </div>
          </div>

          {/* Data Quality Issues Section */}
          <div className="glass-card" style={{ marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertTriangle size={20} color="#f59e0b" /> Data Quality Findings ({data.quality.issues.length})
              </h3>
              <div style={{ display: 'flex', gap: '0.35rem' }}>
                {['all', 'critical', 'warning', 'info'].map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setActiveFilter(sev)}
                    style={{
                      padding: '0.3rem 0.65rem',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      textTransform: 'capitalize',
                      background: activeFilter === sev ? 'var(--accent-primary)' : 'var(--bg-glass)',
                      color: activeFilter === sev ? '#fff' : 'var(--text-muted)',
                      border: '1px solid var(--border-color)',
                      cursor: 'pointer',
                    }}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>

            {data.quality.issues.length === 0 ? (
              <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--status-success)', background: 'rgba(16, 185, 129, 0.1)', borderRadius: 'var(--radius-sm)' }}>
                <CheckCircle2 size={24} style={{ marginBottom: '0.25rem' }} />
                <div>No critical data quality issues detected!</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {data.quality.issues
                  .filter((iss) => activeFilter === 'all' || iss.severity === activeFilter)
                  .map((iss, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '0.85rem 1rem',
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg-glass)',
                        borderLeft: `4px solid ${
                          iss.severity === 'critical' ? '#ef4444' : iss.severity === 'warning' ? '#f59e0b' : '#06b6d4'
                        }`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', fontWeight: 600 }}>
                          <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>[{iss.code}]</span>
                          {iss.column && <span style={{ color: 'var(--accent-cyan)' }}>Column: {iss.column}</span>}
                        </div>
                        <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{iss.message}</div>
                      </div>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontWeight: 600,
                          textTransform: 'uppercase',
                          background: iss.severity === 'critical' ? 'rgba(239, 68, 68, 0.2)' : iss.severity === 'warning' ? 'rgba(245, 158, 11, 0.2)' : 'rgba(6, 182, 212, 0.2)',
                          color: iss.severity === 'critical' ? '#fca5a5' : iss.severity === 'warning' ? '#fcd34d' : '#67e8f9',
                        }}
                      >
                        {iss.severity}
                      </span>
                    </div>
                  ))}
              </div>
            )}
          </div>

          {/* Column Profile Table */}
          <div className="glass-card">
            <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={20} color="#6366f1" /> Column Profile Analysis
            </h3>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>#</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Column Name</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Inferred Type</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Missing %</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Unique %</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Key Statistics</th>
                  </tr>
                </thead>
                <tbody>
                  {data.columns.map((col) => (
                    <tr key={col.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)' }}>
                      <td style={{ padding: '0.85rem 1rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{col.column_index + 1}</td>
                      <td style={{ padding: '0.85rem 1rem', fontWeight: 600 }}>{col.column_name}</td>
                      <td style={{ padding: '0.85rem 1rem' }}>
                        <span
                          style={{
                            fontSize: '0.75rem',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            background: 'var(--bg-glass)',
                            border: '1px solid var(--border-color)',
                            color: col.inferred_type === 'numeric' ? '#6366f1' : col.inferred_type === 'categorical' ? '#06b6d4' : col.inferred_type === 'datetime' ? '#10b981' : '#a855f7',
                          }}
                        >
                          {col.inferred_type}
                        </span>
                      </td>
                      <td style={{ padding: '0.85rem 1rem', color: col.null_percentage > 20 ? '#ef4444' : 'inherit' }}>
                        {col.null_percentage}% ({col.null_count})
                      </td>
                      <td style={{ padding: '0.85rem 1rem' }}>
                        {col.unique_percentage}% ({col.unique_count})
                      </td>
                      <td style={{ padding: '0.85rem 1rem', fontSize: '0.8125rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                        {col.inferred_type === 'numeric' && (
                          <span>
                            Min: {col.min_value ?? 'N/A'} | Max: {col.max_value ?? 'N/A'} | Mean: {col.mean_value ?? 'N/A'} | Median: {col.median_value ?? 'N/A'}
                          </span>
                        )}
                        {col.inferred_type === 'categorical' && col.top_values && (
                          <span>
                            Top: {col.top_values.slice(0, 3).map((t) => `${t.value} (${t.percentage}%)`).join(', ')}
                          </span>
                        )}
                        {col.inferred_type === 'text' && (
                          <span>
                            Len: Min {col.min_length ?? 0}, Max {col.max_length ?? 0}, Avg {col.avg_length ?? 0}
                          </span>
                        )}
                        {col.inferred_type === 'datetime' && (
                          <span>
                            Range: {col.min_datetime ? col.min_datetime.split('T')[0] : 'N/A'} to {col.max_datetime ? col.max_datetime.split('T')[0] : 'N/A'}
                          </span>
                        )}
                        {col.inferred_type === 'boolean' && (
                          <span>
                            True: {col.true_count ?? 0} | False: {col.false_count ?? 0}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
