import React from 'react';

export default function PatternCard({ pattern, onOpenDetails }) {
  const {
    pattern_type,
    rank,
    score,
    title,
    description,
    columns = [],
    strength = 'WEAK',
    significant = false,
    adjusted_p_value,
    effect_size,
    method,
  } = pattern;

  const strengthColor =
    strength.toUpperCase() === 'STRONG'
      ? '#a78bfa'
      : strength.toUpperCase() === 'MODERATE'
      ? '#38bdf8'
      : '#94a3b8';

  const sigColor = significant ? '#34d399' : '#94a3b8';

  return (
    <div style={{
      background: 'rgba(30, 41, 59, 0.7)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '14px',
      padding: '20px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      transition: 'transform 0.2s ease, border-color 0.2s ease',
      cursor: 'default',
    }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span style={{
              background: 'rgba(255,255,255,0.08)',
              color: '#94a3b8',
              fontSize: '11px',
              fontWeight: '700',
              padding: '3px 8px',
              borderRadius: '6px',
            }}>
              #{rank}
            </span>
            <span style={{
              background: 'rgba(56, 189, 248, 0.12)',
              color: '#38bdf8',
              fontSize: '11px',
              fontWeight: '700',
              padding: '3px 8px',
              borderRadius: '6px',
              textTransform: 'uppercase',
            }}>
              {pattern_type.replace('_', ' ')}
            </span>
          </div>

          <div style={{
            background: `rgba(${strength.toUpperCase() === 'STRONG' ? '167, 139, 250' : '56, 189, 248'}, 0.15)`,
            color: strengthColor,
            fontSize: '11px',
            fontWeight: '700',
            padding: '3px 10px',
            borderRadius: '20px',
            border: `1px solid ${strengthColor}40`,
          }}>
            {strength}
          </div>
        </div>

        <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#f8fafc', margin: '0 0 8px 0', lineHeight: 1.4 }}>
          {title}
        </h3>

        <p style={{ fontSize: '13px', color: '#94a3b8', margin: '0 0 16px 0', lineHeight: 1.5 }}>
          {description}
        </p>
      </div>

      <div>
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px',
          background: 'rgba(0, 0, 0, 0.2)',
          padding: '10px 12px',
          borderRadius: '8px',
          fontSize: '12px',
          marginBottom: '16px',
        }}>
          <div>
            <span style={{ color: '#64748b' }}>FDR p-adj: </span>
            <span style={{ color: sigColor, fontWeight: '600' }}>
              {adjusted_p_value !== null && adjusted_p_value !== undefined
                ? (adjusted_p_value < 0.0001 ? '< 0.0001' : adjusted_p_value.toFixed(4))
                : 'N/A'}
            </span>
          </div>
          <div>
            <span style={{ color: '#64748b' }}>Effect Size: </span>
            <span style={{ color: '#e2e8f0', fontWeight: '600' }}>
              {effect_size !== null && effect_size !== undefined ? effect_size.toFixed(3) : 'N/A'}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '12px', color: '#64748b' }}>
            Score: <strong style={{ color: '#38bdf8' }}>{score.toFixed(1)}/100</strong>
          </div>
          <button
            onClick={() => onOpenDetails(pattern)}
            style={{
              background: 'transparent',
              border: '1px solid rgba(255,255,255,0.2)',
              color: '#f8fafc',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            View Evidence
          </button>
        </div>
      </div>
    </div>
  );
}
