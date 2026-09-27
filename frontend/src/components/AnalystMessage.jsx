import React from 'react';
import { User, Bot, HelpCircle } from 'lucide-react';
import { AnalystEvidence } from './AnalystEvidence';
import { AnalystChart } from './AnalystChart';

export function AnalystMessage({ message, onOptionSelect }) {
  const isUser = message.role === 'USER';
  const summary = message.query_result_summary;
  const isClarification = message.intent === 'CLARIFICATION' || (summary && summary.execution_path === 'CLARIFICATION');

  return (
    <div
      style={{
        display: 'flex',
        gap: '0.85rem',
        marginBottom: '1.25rem',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      {!isUser && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            flexShrink: 0,
          }}
        >
          <Bot size={20} />
        </div>
      )}

      <div
        style={{
          maxWidth: '85%',
          background: isUser ? 'rgba(59, 130, 246, 0.15)' : 'rgba(30, 41, 59, 0.7)',
          border: isUser ? '1px solid rgba(59, 130, 246, 0.3)' : '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          padding: '1rem 1.25rem',
          color: '#f8fafc',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
          <span style={{ fontWeight: 600, fontSize: '0.8125rem', color: isUser ? '#60a5fa' : '#38bdf8' }}>
            {isUser ? 'You' : 'VizMind Analyst'}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {new Date(message.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>

        <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.9375rem' }}>
          {message.content}
        </div>

        {/* Clarification prompt options if present */}
        {isClarification && message.query_plan?.clarification_options && (
          <div style={{ marginTop: '1rem', background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)', padding: '0.85rem', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.8125rem', color: '#fbbf24', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <HelpCircle size={14} /> Clarification Needed:
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {message.query_plan.clarification_options.map((opt, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => onOptionSelect && onOptionSelect(opt)}
                  style={{
                    padding: '0.35rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8125rem',
                    background: '#1e293b',
                    border: '1px solid #f59e0b',
                    color: '#fef3c7',
                    cursor: 'pointer',
                  }}
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Result Table if present */}
        {summary && summary.data && summary.data.length > 0 && (
          <div style={{ marginTop: '1rem', overflowX: 'auto', background: 'rgba(15, 23, 42, 0.5)', padding: '0.5rem', borderRadius: 'var(--radius-sm)' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8125rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                  {Object.keys(summary.data[0]).map((col) => (
                    <th key={col} style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {summary.data.map((row, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                    {Object.values(row).map((val, cidx) => (
                      <td key={cidx} style={{ padding: '0.5rem 0.75rem' }}>{val !== null ? String(val) : '—'}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Inline Chart if numerical breakdown/trend */}
        {summary && summary.data && summary.data.length > 1 && (
          <AnalystChart
            data={summary.data}
            columns={Object.keys(summary.data[0])}
            operation={summary.operation}
          />
        )}

        {/* Grounded Evidence Badges */}
        {!isUser && message.source_references && (
          <AnalystEvidence references={message.source_references} />
        )}
      </div>

      {isUser && (
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'rgba(59, 130, 246, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#60a5fa',
            flexShrink: 0,
          }}
        >
          <User size={20} />
        </div>
      )}
    </div>
  );
}
