import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';

export function AnalystInput({ onSend, loading, disabled }) {
  const [text, setText] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || loading || disabled) return;
    onSend(text.trim());
    setText('');
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
      <input
        type="text"
        placeholder="Ask a natural language question about your dataset..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={loading || disabled}
        style={{
          flex: 1,
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid var(--border-color)',
          color: '#f8fafc',
          fontSize: '0.9375rem',
          outline: 'none',
        }}
      />
      <button
        type="submit"
        className="btn-primary"
        disabled={!text.trim() || loading || disabled}
        style={{ padding: '0.75rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
      >
        {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        Ask
      </button>
    </form>
  );
}
