import React from 'react';

export default function PatternStatistics({ pattern, onClose }) {
  if (!pattern) return null;

  const {
    pattern_type,
    title,
    method,
    sample_size,
    raw_p_value,
    adjusted_p_value,
    effect_size,
    strength,
    significant,
    statistics = {},
    columns = [],
  } = pattern;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(15, 23, 42, 0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px',
    }}>
      <div style={{
        background: '#1e293b',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '650px',
        maxHeight: '90vh',
        overflowY: 'auto',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        color: '#f8fafc',
        padding: '28px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
          <div>
            <div style={{
              display: 'inline-block',
              fontSize: '11px',
              fontWeight: '700',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: '#38bdf8',
              background: 'rgba(56, 189, 248, 0.15)',
              padding: '4px 10px',
              borderRadius: '20px',
              marginBottom: '8px',
            }}>
              {pattern_type.replace('_', ' ')}
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: '700', margin: 0 }}>{title}</h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              fontSize: '24px',
              cursor: 'pointer',
              lineHeight: 1,
            }}
          >
            &times;
          </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px' }}>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '12px' }}>Statistical Method</span>
            <div style={{ fontSize: '15px', fontWeight: '600', marginTop: '4px' }}>{method}</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '12px' }}>Sample Size (N)</span>
            <div style={{ fontSize: '15px', fontWeight: '600', marginTop: '4px' }}>{sample_size.toLocaleString()}</div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '12px' }}>Raw P-Value</span>
            <div style={{ fontSize: '15px', fontWeight: '600', marginTop: '4px' }}>
              {raw_p_value !== null ? (raw_p_value < 0.0001 ? '< 0.0001' : raw_p_value.toFixed(5)) : 'N/A'}
            </div>
          </div>
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px 16px', borderRadius: '8px' }}>
            <span style={{ color: '#94a3b8', fontSize: '12px' }}>FDR Adjusted P-Value</span>
            <div style={{ fontSize: '15px', fontWeight: '600', marginTop: '4px', color: significant ? '#34d399' : '#f8fafc' }}>
              {adjusted_p_value !== null ? (adjusted_p_value < 0.0001 ? '< 0.0001' : adjusted_p_value.toFixed(5)) : 'N/A'}
            </div>
          </div>
        </div>

        <h3 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px', color: '#cbd5e1' }}>
          Detailed Metrics & Evidence
        </h3>
        <div style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '8px', marginBottom: '24px' }}>
          <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '13px', color: '#e2e8f0', whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(statistics, null, 2)}
          </pre>
        </div>

        <div style={{
          background: 'rgba(234, 179, 8, 0.1)',
          borderLeft: '4px solid #eab308',
          padding: '12px 16px',
          borderRadius: '4px',
          fontSize: '12px',
          color: '#fef08a',
          lineHeight: 1.5,
        }}>
          <strong>Statistical Disclaimer:</strong> All pattern results are generated through deterministic mathematical computations. Statistical significance does not imply causation or practical importance. Historical time trends describe observed data only and are not predictive forecasts.
        </div>

        <div style={{ marginTop: '24px', textAlign: 'right' }}>
          <button
            onClick={onClose}
            style={{
              background: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            Close Details
          </button>
        </div>
      </div>
    </div>
  );
}
