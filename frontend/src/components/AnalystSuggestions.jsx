import React from 'react';
import { HelpCircle } from 'lucide-react';

export function AnalystSuggestions({ suggestions, onSelectSuggestion, disabled }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div style={{ marginBottom: '1rem' }}>
      <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600 }}>
        <HelpCircle size={14} color="#06b6d4" /> Suggested Questions:
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {suggestions.map((s, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectSuggestion(s)}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: '9999px',
              fontSize: '0.8125rem',
              background: 'rgba(6, 182, 212, 0.1)',
              border: '1px solid rgba(6, 182, 212, 0.25)',
              color: '#38bdf8',
              cursor: disabled ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
