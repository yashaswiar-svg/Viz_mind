import React, { useEffect, useState } from 'react';
import { getAppHealth, getDbHealth } from '../services/api';
import { Server, Database, RefreshCw } from 'lucide-react';

export function HealthCard() {
  const [appStatus, setAppStatus] = useState({ loading: true, data: null, error: null });
  const [dbStatus, setDbStatus] = useState({ loading: true, data: null, error: null });

  const fetchHealth = async () => {
    setAppStatus({ loading: true, data: null, error: null });
    setDbStatus({ loading: true, data: null, error: null });

    try {
      const appRes = await getAppHealth();
      setAppStatus({ loading: false, data: appRes, error: null });
    } catch (err) {
      setAppStatus({ loading: false, data: null, error: err.message });
    }

    try {
      const dbRes = await getDbHealth();
      setDbStatus({ loading: false, data: dbRes, error: null });
    } catch (err) {
      setDbStatus({ loading: false, data: null, error: err.message });
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="status-grid">
      {/* Backend API Health Card */}
      <div className="glass-card">
        <div className="status-card-header">
          <span className="status-card-title">Backend Service</span>
          <span
            className={`status-dot ${
              appStatus.data?.status === 'healthy' ? 'healthy' : 'error'
            }`}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Server size={24} color="#6366f1" />
          <div className="status-value">
            {appStatus.loading
              ? 'Checking...'
              : appStatus.data?.status === 'healthy'
              ? 'Online'
              : 'Offline'}
          </div>
        </div>
        <div className="status-detail">
          {appStatus.data
            ? `${appStatus.data.service} v${appStatus.data.version}`
            : appStatus.error || 'Connecting to FastAPI...'}
        </div>
      </div>

      {/* Database Connectivity Card */}
      <div className="glass-card">
        <div className="status-card-header">
          <span className="status-card-title">PostgreSQL Database</span>
          <span
            className={`status-dot ${
              dbStatus.data?.status === 'healthy' ? 'healthy' : 'error'
            }`}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Database size={24} color="#06b6d4" />
          <div className="status-value">
            {dbStatus.loading
              ? 'Checking...'
              : dbStatus.data?.status === 'healthy'
              ? 'Connected'
              : 'Disconnected'}
          </div>
        </div>
        <div className="status-detail">
          {dbStatus.data
            ? `PostgreSQL (${dbStatus.data.database})`
            : dbStatus.error || 'Testing query SELECT 1...'}
        </div>
      </div>
    </div>
  );
}
