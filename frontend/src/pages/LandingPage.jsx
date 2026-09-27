import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { HealthCard } from '../components/HealthCard';
import { AuthModal } from '../components/AuthModal';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  ArrowRight,
  Database,
  BarChart2,
  TrendingUp,
  AlertTriangle,
  Zap,
  Bot,
  Shield,
  CheckCircle2,
  FileSpreadsheet
} from 'lucide-react';

const workflowSteps = [
  {
    icon: Database,
    name: '1. Ingestion',
    desc: 'Upload CSV or Excel files with automatic structure & type detection.',
    color: '#06b6d4'
  },
  {
    icon: BarChart2,
    name: '2. Profiling & Quality',
    desc: 'Instant quality scores, duplicate checks, missing cell metrics & summary stats.',
    color: '#3b82f6'
  },
  {
    icon: Zap,
    name: '3. Preprocessing',
    desc: 'Automated missing value imputation, outlier handling & normalization.',
    color: '#6366f1'
  },
  {
    icon: TrendingUp,
    name: '4. Visualizations',
    desc: 'Scored chart recommendations with interactive box plots, bars, lines & scatters.',
    color: '#8b5cf6'
  },
  {
    icon: Sparkles,
    name: '5. Pattern Discovery',
    desc: 'Statistical correlations, clustering analysis, and significant trend discovery.',
    color: '#ec4899'
  },
  {
    icon: AlertTriangle,
    name: '6. Anomaly & Prediction',
    desc: 'Robust Z-score & Isolation Forest anomaly detection + predictive ML models.',
    color: '#f59e0b'
  },
  {
    icon: FileSpreadsheet,
    name: '7. AI Insights',
    desc: 'Structured natural-language data stories with statistical evidence backing.',
    color: '#10b981'
  },
  {
    icon: Bot,
    name: '8. Conversational Analyst',
    desc: 'Natural language querying engine for instant conversational dataset answers.',
    color: '#14b8a6'
  }
];

export function LandingPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [authModalOpen, setAuthModalOpen] = useState(false);

  const handleStart = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      setAuthModalOpen(true);
    }
  };

  return (
    <div className="container" style={{ paddingTop: '2rem', paddingBottom: '4rem' }}>
      <section className="hero">
        <div className="badge">
          <Sparkles size={14} />
          VizMind v1.0 • AI-Powered Data Analyst Platform
        </div>
        <h1 className="hero-title">
          Transform Raw Data into Actionable Insights
        </h1>
        <p className="hero-subtitle">
          An end-to-end intelligent platform that handles profiling, automated preprocessing, chart recommendations, pattern discovery, anomaly detection, predictive analytics, and natural-language AI stories.
        </p>

        <div className="hero-actions">
          <button onClick={handleStart} className="btn-primary" style={{ padding: '0.85rem 1.75rem', fontSize: '1rem' }}>
            {isAuthenticated ? 'Open Workspace Dashboard' : 'Get Started Now'} <ArrowRight size={18} />
          </button>
          <a
            href="/api/v1/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary"
            style={{ padding: '0.85rem 1.5rem', fontSize: '1rem' }}
          >
            API Documentation
          </a>
        </div>
      </section>

      {/* Real-time System Status */}
      <HealthCard />

      {/* Workflow & Capabilities Section */}
      <section className="capabilities-section" style={{ marginTop: '3rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
          <h2 className="section-title">Complete Data Analysis Engine</h2>
          <p className="section-subtitle">
            Everything you need to understand, clean, visualize, and question your datasets in one unified workflow.
          </p>
        </div>

        <div className="capabilities-grid">
          {workflowSteps.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={i} className="capability-card" style={{ transition: 'transform 0.2s ease, border-color 0.2s ease' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <div style={{ padding: '0.5rem', borderRadius: 'var(--radius-sm)', background: `${step.color}20`, color: step.color }}>
                    <Icon size={22} />
                  </div>
                  <div className="capability-name" style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>{step.name}</div>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>{step.desc}</p>
                <div style={{ marginTop: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>
                  <CheckCircle2 size={13} /> Active & Ready
                </div>
              </div>
            );
          })}
        </div>

        {/* Call to action card */}
        <div className="glass-card" style={{ marginTop: '3rem', textAlign: 'center', padding: '3rem 2rem', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
          <h3 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.75rem' }}>Ready to Analyze Your Dataset?</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 1.75rem' }}>
            Upload your CSV or Excel file and experience automated profiling, interactive charts, and AI-driven pattern discovery in seconds.
          </p>
          <button onClick={handleStart} className="btn-primary" style={{ padding: '0.85rem 2rem', fontSize: '1rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
            <Database size={18} /> Launch VizMind Workspace
          </button>
        </div>
      </section>

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
    </div>
  );
}
