import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export function AnalystChart({ data, columns, operation }) {
  if (!data || data.length === 0 || !columns || columns.length < 2) {
    return null;
  }

  const xKey = columns[0];
  const yKey = columns[1];

  const isTrend = operation === 'TREND';

  return (
    <div style={{ width: '100%', height: 260, marginTop: '1rem', background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
      <ResponsiveContainer width="100%" height="100%">
        {isTrend ? (
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
            <XAxis dataKey={xKey} stroke="var(--text-muted)" fontSize={12} />
            <YAxis stroke="var(--text-muted)" fontSize={12} />
            <Tooltip contentStyle={{ background: '#1e293b', borderColor: 'var(--border-color)', color: '#f8fafc' }} />
            <Line type="monotone" dataKey={yKey} stroke="#06b6d4" strokeWidth={2} dot={{ fill: '#06b6d4' }} />
          </LineChart>
        ) : (
          <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.1)" />
            <XAxis dataKey={xKey} stroke="var(--text-muted)" fontSize={12} />
            <YAxis stroke="var(--text-muted)" fontSize={12} />
            <Tooltip contentStyle={{ background: '#1e293b', borderColor: 'var(--border-color)', color: '#f8fafc' }} />
            <Bar dataKey={yKey} fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
