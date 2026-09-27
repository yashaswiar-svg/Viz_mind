import React, { useEffect, useState } from 'react';
import { getPreprocessingReport, preprocessDataset } from '../services/api';
import {
  ArrowLeft,
  Wand2,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Database,
  Layers,
  Sparkles,
  FileCheck,
  Check,
  ShieldCheck,
} from 'lucide-react';

export function PreprocessingView({ dataset, onBack }) {
  const [prepState, setPrepState] = useState({
    status: 'idle', // idle, loading, ready, not_preprocessed, failed
    report: null,
    error: null,
  });

  const fetchReport = async () => {
    setPrepState({ status: 'loading', report: null, error: null });
    try {
      const data = await getPreprocessingReport(dataset.id);
      setPrepState({ status: 'ready', report: data, error: null });
    } catch (err) {
      if (err.code === 'PREPROCESSING_NOT_FOUND') {
        setPrepState({ status: 'not_preprocessed', report: null, error: null });
      } else {
        setPrepState({ status: 'failed', report: null, error: err.message });
      }
    }
  };

  const handleRunPreprocessing = async () => {
    setPrepState({ status: 'loading', report: null, error: null });
    try {
      const data = await preprocessDataset(dataset.id);
      setPrepState({ status: 'ready', report: data, error: null });
    } catch (err) {
      setPrepState({ status: 'failed', report: null, error: err.message });
    }
  };

  useEffect(() => {
    if (dataset) {
      fetchReport();
    }
  }, [dataset]);

  const formatBytes = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const { status, report, error } = prepState;

  return (
    <div style={{ paddingBottom: '3rem' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <button className="btn-secondary" onClick={onBack} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ArrowLeft size={16} /> Back to Dataset Profile
        </button>

        {status === 'ready' && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {onSelectVisualizations && (
              <button className="btn-primary" onClick={() => onSelectVisualizations(dataset)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: '#3B82F6' }}>
                <Sparkles size={16} /> View Smart Visualizations
              </button>
            )}
            <button className="btn-secondary" onClick={handleRunPreprocessing} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <RefreshCw size={16} /> Re-run Preprocessing
            </button>
          </div>
        )}
      </div>

      <div className="glass-card" style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span className="badge">
              <Wand2 size={14} /> Phase 4 Preprocessing Engine
            </span>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginTop: '0.5rem' }}>{dataset.name}</h2>
            <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>
              Source SHA-256: {dataset.checksum ? `${dataset.checksum.slice(0, 16)}...` : 'N/A'} (Source file immutable)
            </div>
          </div>

          {status === 'ready' && report && (
            <div style={{ textAlign: 'right' }}>
              <span className="capability-status status-ready" style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '0.4rem 0.85rem' }}>
                <ShieldCheck size={14} style={{ display: 'inline', marginRight: '0.35rem' }} />
                Analysis-Ready Derived Dataset
              </span>
            </div>
          )}
        </div>
      </div>

      {/* State: Not Preprocessed */}
      {status === 'not_preprocessed' && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <Wand2 size={48} color="var(--accent-primary)" style={{ marginBottom: '1rem', opacity: 0.8 }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Dataset Not Preprocessed Yet</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '540px', margin: '0 auto 1.5rem', fontSize: '0.9375rem' }}>
            Run the Phase 4 deterministic preprocessing pipeline to handle missing values, drop empty/constant columns, remove duplicate rows, normalize text, and generate a derived analysis-ready dataset.
          </p>
          <button className="btn-primary" onClick={handleRunPreprocessing} style={{ padding: '0.75rem 1.75rem', fontSize: '0.9375rem' }}>
            <Sparkles size={18} /> Run Preprocessing Pipeline
          </button>
        </div>
      )}

      {/* State: Loading */}
      {status === 'loading' && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
          <RefreshCw size={40} className="spin" style={{ animation: 'spin 1.2s linear infinite', color: 'var(--accent-cyan)', marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Executing Preprocessing Transformations...</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
            Applying deterministic rules, imputing missing cells, verifying source checksum integrity, and storing derived dataset.
          </p>
        </div>
      )}

      {/* State: Failed */}
      {status === 'failed' && (
        <div className="glass-card" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', textAlign: 'center', padding: '3rem 2rem' }}>
          <AlertTriangle size={40} color="#ef4444" style={{ marginBottom: '1rem' }} />
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fca5a5', marginBottom: '0.5rem' }}>Preprocessing Execution Failed</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.875rem' }}>{error}</p>
          <button className="btn-secondary" onClick={handleRunPreprocessing}>
            Retry Preprocessing
          </button>
        </div>
      )}

      {/* State: Preprocessing Complete */}
      {status === 'ready' && report && (
        <>
          {/* Before vs After Overview Cards */}
          <div className="status-grid" style={{ marginTop: 0, marginBottom: '2rem' }}>
            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Row Count</span>
                <Database size={18} color="var(--accent-primary)" />
              </div>
              <div className="status-value">
                {report.job.rows_after.toLocaleString()}
              </div>
              <div className="status-detail">
                Before: {report.job.rows_before.toLocaleString()} ({report.job.rows_before - report.job.rows_after} removed)
              </div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Columns Count</span>
                <Layers size={18} color="var(--accent-cyan)" />
              </div>
              <div className="status-value">
                {report.job.columns_after.toLocaleString()}
              </div>
              <div className="status-detail">
                Before: {report.job.columns_before.toLocaleString()} ({report.job.columns_after - report.job.columns_before >= 0 ? `+${report.job.columns_after - report.job.columns_before}` : report.job.columns_after - report.job.columns_before})
              </div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Missing Cells</span>
                <AlertTriangle size={18} color={report.job.missing_cells_after === 0 ? '#10b981' : '#f59e0b'} />
              </div>
              <div className="status-value">
                {report.job.missing_cells_after.toLocaleString()}
              </div>
              <div className="status-detail">
                Before: {report.job.missing_cells_before.toLocaleString()} ({report.job.missing_cells_before - report.job.missing_cells_after} imputed)
              </div>
            </div>

            <div className="glass-card">
              <div className="status-card-header">
                <span className="status-card-title">Duplicate Rows</span>
                <CheckCircle2 size={18} color="#10b981" />
              </div>
              <div className="status-value">
                {report.job.duplicate_rows_after.toLocaleString()}
              </div>
              <div className="status-detail">
                Before: {report.job.duplicate_rows_before.toLocaleString()} ({report.job.duplicate_rows_before - report.job.duplicate_rows_after} removed)
              </div>
            </div>
          </div>

          {/* Derived Dataset Info Card */}
          {report.processed_dataset && (
            <div className="glass-card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--accent-primary)' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileCheck size={20} color="var(--accent-primary)" /> Derived Processed Dataset Metadata
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', fontSize: '0.875rem' }}>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Dataset Name</div>
                  <div style={{ fontWeight: 600, marginTop: '0.2rem' }}>{report.processed_dataset.name}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Dataset Kind</div>
                  <div style={{ fontWeight: 600, marginTop: '0.2rem', color: 'var(--accent-cyan)' }}>{report.processed_dataset.dataset_kind}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>File Size</div>
                  <div style={{ fontWeight: 600, marginTop: '0.2rem' }}>{formatBytes(report.processed_dataset.file_size)}</div>
                </div>
                <div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Processed SHA-256</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', marginTop: '0.2rem' }}>
                    {report.processed_dataset.checksum ? `${report.processed_dataset.checksum.slice(0, 16)}...` : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Transformation Timeline */}
          <div className="glass-card">
            <h3 style={{ fontSize: '1.125rem', fontWeight: 700, marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={20} color="#6366f1" /> Preprocessing Transformation Audit Log ({report.transformations.length})
            </h3>

            {report.transformations.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                No transformation steps were required for this dataset.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {report.transformations.map((trans) => (
                  <div
                    key={trans.step_order}
                    style={{
                      padding: '1rem 1.25rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'var(--bg-glass)',
                      border: '1px solid var(--border-color)',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '1rem',
                    }}
                  >
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: 'var(--accent-primary)',
                        color: '#fff',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '0.8125rem',
                        fontWeight: 700,
                        flexShrink: 0,
                      }}
                    >
                      {trans.step_order}
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <span
                          style={{
                            fontSize: '0.75rem',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            background: 'rgba(99, 102, 241, 0.2)',
                            color: '#818cf8',
                            border: '1px solid rgba(99, 102, 241, 0.3)',
                          }}
                        >
                          {trans.transformation_type}
                        </span>
                        {trans.column_name && (
                          <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--accent-cyan)' }}>
                            Column: {trans.column_name}
                          </span>
                        )}
                      </div>

                      <div style={{ fontSize: '0.875rem', color: 'var(--text-primary)', marginTop: '0.35rem' }}>
                        {trans.description}
                      </div>

                      {(trans.rows_affected > 0 || trans.values_affected > 0) && (
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                          Impact: {trans.values_affected > 0 ? `${trans.values_affected} values affected` : ''}{' '}
                          {trans.rows_affected > 0 ? `(${trans.rows_affected} rows affected)` : ''}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
