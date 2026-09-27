import React from 'react';
import { X, FileText, Database, ShieldCheck, Clock } from 'lucide-react';

export function DatasetMetadataModal({ dataset, onClose }) {
  if (!dataset) return null;

  const formatBytes = (bytes) => {
    if (!bytes) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(4px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '600px',
          background: '#121824',
          border: '1px solid var(--border-color)',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FileText size={24} color="#6366f1" />
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Dataset Metadata</h3>
          </div>
          <button
            onClick={onClose}
            style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.25rem', fontSize: '0.875rem' }}>
          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Dataset Name</div>
            <div style={{ fontWeight: 600, marginTop: '0.25rem' }}>{dataset.name}</div>
          </div>

          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Status</div>
            <div style={{ marginTop: '0.25rem' }}>
              <span className="capability-status status-ready">{dataset.status}</span>
            </div>
          </div>

          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Original Filename</div>
            <div style={{ fontFamily: 'var(--font-mono)', marginTop: '0.25rem' }}>{dataset.original_filename}</div>
          </div>

          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>File Type & Size</div>
            <div style={{ marginTop: '0.25rem' }}>
              <span style={{ textTransform: 'uppercase', fontWeight: 600, color: 'var(--accent-cyan)' }}>{dataset.file_type}</span> ({formatBytes(dataset.file_size)})
            </div>
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Dataset ID (UUID)</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.25rem', wordBreak: 'break-all' }}>
              {dataset.id}
            </div>
          </div>

          <div style={{ gridColumn: 'span 2' }}>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>SHA-256 Checksum</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem', wordBreak: 'break-all', background: 'var(--bg-glass)', padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}>
              {dataset.checksum || 'N/A'}
            </div>
          </div>

          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Created At</div>
            <div style={{ fontSize: '0.8125rem', marginTop: '0.25rem' }}>{new Date(dataset.created_at).toLocaleString()}</div>
          </div>

          <div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Updated At</div>
            <div style={{ fontSize: '0.8125rem', marginTop: '0.25rem' }}>{new Date(dataset.updated_at).toLocaleString()}</div>
          </div>
        </div>

        <div style={{ marginTop: '2rem', textAlign: 'right' }}>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
