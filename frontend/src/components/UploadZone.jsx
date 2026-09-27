import React, { useState } from 'react';
import { uploadDataset } from '../services/api';
import { UploadCloud, FileText, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

export function UploadZone({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [customName, setCustomName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setSuccessMsg(null);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setError(null);
      setSuccessMsg(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const result = await uploadDataset(selectedFile, customName);
      setSuccessMsg(`Dataset "${result.name}" successfully uploaded and registered!`);
      setSelectedFile(null);
      setCustomName('');
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
    } catch (err) {
      setError(err.message || 'Failed to upload dataset.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '2rem' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <UploadCloud size={24} color="#6366f1" /> Dataset Ingestion
      </h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
        Upload your raw dataset file for secure storage and metadata registration. Supported formats: <strong>.csv, .xlsx, .xls</strong> (Max: 50 MB).
      </p>

      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: 'var(--radius-sm)', padding: '0.85rem 1rem', marginBottom: '1.25rem', color: '#fca5a5', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem' }}>
          <AlertCircle size={20} style={{ shrink: 0 }} />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)', borderRadius: 'var(--radius-sm)', padding: '0.85rem 1rem', marginBottom: '1.25rem', color: '#6ee7b7', display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.875rem' }}>
          <CheckCircle size={20} style={{ shrink: 0 }} />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleUpload}>
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${dragActive ? 'var(--accent-primary)' : 'var(--border-color)'}`,
            borderRadius: 'var(--radius-md)',
            padding: '2.5rem 1.5rem',
            textAlign: 'center',
            background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'var(--bg-glass)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            marginBottom: '1.25rem',
          }}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <input
            id="fileInput"
            type="file"
            accept=".csv, .xlsx, .xls"
            style={{ display: 'none' }}
            onChange={handleFileSelect}
            disabled={uploading}
          />

          {selectedFile ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
              <FileText size={32} color="#06b6d4" />
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)' }}>
                  {selectedFile.name}
                </div>
                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                  {formatBytes(selectedFile.size)} • Click to change file
                </div>
              </div>
            </div>
          ) : (
            <div>
              <UploadCloud size={40} color="var(--text-muted)" style={{ marginBottom: '0.75rem' }} />
              <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.25rem' }}>
                Drag & Drop dataset file here, or <span style={{ color: 'var(--accent-primary)' }}>browse</span>
              </div>
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                CSV, XLSX, XLS up to 50 MB
              </div>
            </div>
          )}
        </div>

        {selectedFile && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '1rem', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Custom dataset name (optional)"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              disabled={uploading}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '0.65rem 1rem',
                color: 'var(--text-primary)',
                fontFamily: 'inherit',
                fontSize: '0.875rem',
              }}
            />
            <button
              type="submit"
              className="btn-primary"
              disabled={uploading}
              style={{ opacity: uploading ? 0.7 : 1, padding: '0.65rem 1.5rem' }}
            >
              {uploading ? (
                <>
                  <Loader2 size={16} className="spin" style={{ animation: 'spin 1s linear infinite' }} />
                  Uploading...
                </>
              ) : (
                'Upload Dataset'
              )}
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
