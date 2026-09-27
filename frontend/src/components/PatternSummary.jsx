import React from 'react';

export default function PatternSummary({ totalPatterns, significantPatterns, strongPatterns, runInfo }) {
  const completedAt = runInfo?.completed_at
    ? new Date(runInfo.completed_at).toLocaleString()
    : 'N/A';

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '16px',
      marginBottom: '24px',
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '20px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Total Patterns Discovered
        </div>
        <div style={{ fontSize: '32px', fontWeight: '700', color: '#38bdf8' }}>
          {totalPatterns}
        </div>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '20px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Statistically Significant
        </div>
        <div style={{ fontSize: '32px', fontWeight: '700', color: '#34d399' }}>
          {significantPatterns}
        </div>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '20px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Strong Effect Patterns
        </div>
        <div style={{ fontSize: '32px', fontWeight: '700', color: '#a78bfa' }}>
          {strongPatterns}
        </div>
      </div>

      <div style={{
        background: 'rgba(255, 255, 255, 0.05)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '12px',
        padding: '20px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Last Analysis Run
        </div>
        <div style={{ fontSize: '14px', fontWeight: '600', color: '#e2e8f0', marginTop: '10px' }}>
          {completedAt}
        </div>
      </div>
    </div>
  );
}
