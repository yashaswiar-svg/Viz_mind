import React from 'react';
import { Database, Sparkles, AlertTriangle, ShieldCheck } from 'lucide-react';

export function AnalystEvidence({ references }) {
  if (!references || references.length === 0) return null;

  return (
    <div style={{ marginTop: '0.75rem', display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Evidence Grounding:</span>
      {references.map((ref, idx) => {
        const type = ref.source_type || 'COMPUTATION';
        let color = '#38bdf8';
        let Icon = Database;

        if (type.includes('PATTERNS')) {
          color = '#a855f7';
          Icon = Sparkles;
        } else if (type.includes('ANOMALIES')) {
          color = '#f59e0b';
          Icon = AlertTriangle;
        } else if (type.includes('INSIGHTS')) {
          color = '#10b981';
          Icon = ShieldCheck;
        }

        return (
          <span
            key={idx}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.2rem 0.5rem',
              borderRadius: '9999px',
              fontSize: '0.75rem',
              fontWeight: 500,
              background: 'rgba(255, 255, 255, 0.05)',
              border: `1px solid ${color}40`,
              color: color,
            }}
          >
            <Icon size={12} />
            {type.replace(/_/g, ' ')} ({ref.execution_path})
          </span>
        );
      })}
    </div>
  );
}
