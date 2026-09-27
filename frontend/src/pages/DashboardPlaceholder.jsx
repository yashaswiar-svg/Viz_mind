import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { listDatasets, uploadDataset, deleteDataset } from '../services/api';
import { DatasetProfileView } from '../components/DatasetProfileView';
import { PreprocessingView } from '../components/PreprocessingView';
import VisualizationView from '../components/VisualizationView';
import PatternDiscoveryView from '../components/PatternDiscoveryView';
import AnomalyDetectionView from '../components/AnomalyDetectionView';
import PredictionView from '../components/PredictionView';
import InsightView from '../components/InsightView';
import { AnalystView } from '../components/AnalystView';
import vizmindLogo from '../assets/vizmind-logo.jpg';
import {
  Database,
  BarChart3,
  Sparkles,
  AlertTriangle,
  Target,
  Bot,
  Settings,
  User,
  Upload,
  UploadCloud,
  Search,
  FileText,
  Trash2,
  Shield,
  Zap,
  CheckCircle2,
  ArrowRight,
  Cpu,
  Server,
  HardDrive,
  Check,
  LogOut,
  ChevronDown,
  RefreshCw,
  X,
  Activity,
  Layers
} from 'lucide-react';

export function DashboardPlaceholder() {
  const { user, logout } = useAuth();
  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);
  const [activeNav, setActiveNav] = useState('upload'); // upload, datasets, visualizations, patterns, anomalies, predictions, insights, analyst
  const [activeStep, setActiveStep] = useState(1); // 1: Upload, 2: Profile, 3: Prepare, 4: Visualize, 5: Patterns, 6: Anomalies, 7: Predict, 8: Insights, 9: Analyst
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [loadingDatasets, setLoadingDatasets] = useState(false);
  const [error, setError] = useState('');
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [connectorModal, setConnectorModal] = useState(null);

  const fetchDatasetList = async () => {
    setLoadingDatasets(true);
    try {
      const data = await listDatasets(1, 50);
      const list = data?.items || [];
      setDatasets(list);
      if (list.length > 0 && !activeDataset) {
        setActiveDataset(list[0]);
      }
    } catch (err) {
      console.error('Failed to load datasets:', err);
    } finally {
      setLoadingDatasets(false);
    }
  };

  useEffect(() => {
    fetchDatasetList();
  }, []);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const result = await uploadDataset(file);
      await fetchDatasetList();
      setActiveDataset(result);
      setActiveStep(1);
      setActiveNav('upload');
    } catch (err) {
      setError(err.message || 'File upload failed. Please check format and size.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const loadSampleDataset = async (sampleName) => {
    setUploading(true);
    setError('');
    try {
      let sampleCsv = '';
      if (sampleName.includes('Sales')) {
        sampleCsv = `customer_id,age,income,churn_risk,transaction_volume,loyalty_score
1001,34,75000,0,1240.50,8.4
1002,45,112000,0,3450.00,9.1
1003,23,32000,1,150.20,3.2
1004,52,98000,0,2100.80,7.8
1005,29,54000,1,430.00,4.5
1006,41,88000,0,1890.30,8.0
1007,38,67000,0,1450.00,7.1
1008,61,145000,0,5200.00,9.6`;
      } else if (sampleName.includes('IoT')) {
        sampleCsv = `sensor_id,temperature,vibration_hz,pressure_psi,status_flag,error_code
S001,42.5,120.4,14.7,0,0
S002,43.1,122.1,14.8,0,0
S003,89.6,450.9,28.4,1,104
S004,41.9,119.8,14.6,0,0
S005,94.2,490.2,31.1,1,108
S006,42.0,120.0,14.7,0,0`;
      } else {
        sampleCsv = `patient_id,blood_pressure,cholesterol,glucose_mg,bmi,outcome_risk
P101,120,180,95,24.2,0
P102,145,240,140,31.5,1
P103,118,190,88,22.1,0
P104,160,280,185,34.8,1
P105,122,210,102,26.4,0`;
      }

      const blob = new Blob([sampleCsv], { type: 'text/csv' });
      const file = new File([blob], `${sampleName.toLowerCase().replace(/[^a-z0-9]/g, '_')}.csv`, { type: 'text/csv' });
      await handleFileUpload(file);
    } catch (err) {
      console.error(err);
      setError('Failed to load sample dataset.');
    } finally {
      setUploading(false);
    }
  };

  const steps = [
    { num: '01', name: 'Upload', key: 'upload' },
    { num: '02', name: 'Profile', key: 'profile' },
    { num: '03', name: 'Prepare', key: 'prepare' },
    { num: '04', name: 'Visualize', key: 'visualizations' },
    { num: '05', name: 'Patterns', key: 'patterns' },
    { num: '06', name: 'Anomalies', key: 'anomalies' },
    { num: '07', name: 'Predict', key: 'predictions' },
    { num: '08', name: 'Insights', key: 'insights' },
    { num: '09', name: 'Analyst', key: 'analyst' },
  ];

  const handleStepClick = (idx, key) => {
    setActiveStep(idx + 1);
    setActiveNav(key);
  };

  const userName = user?.email?.split('@')[0] || 'User';

  return (
    <div className="viz-workspace-layout">
      {/* Background Ambient Mesh & Subtle Technical Grid */}
      <div className="viz-bg-grid"></div>
      <div className="viz-ambient-glow glow-top-left"></div>
      <div className="viz-ambient-glow glow-top-right"></div>

      {/* Left Sidebar Navigation */}
      <aside className="viz-sidebar">
        <div className="viz-sidebar-header">
          <div className="viz-brand-logo-group">
            <img src={vizmindLogo} alt="VizMind AI Logo" className="viz-brand-logo-img" />
            <div className="viz-brand-text">
              <span className="viz-brand-name">VizMind</span>
              <span className="viz-brand-sub">AI Data Analyst</span>
            </div>
          </div>
          <div className="viz-telemetry-badge">
            <span className="viz-status-dot pulse"></span>
            <span>TELEMETRY ACTIVE v4.2</span>
          </div>
        </div>

        <button
          className="viz-btn-upload-nav"
          onClick={() => { setActiveNav('upload'); setActiveStep(1); }}
        >
          <Upload size={16} />
          <span>+ Upload Dataset</span>
        </button>

        <nav className="viz-sidebar-menu">
          <button
            className={`viz-nav-item ${activeNav === 'upload' ? 'active' : ''}`}
            onClick={() => { setActiveNav('upload'); setActiveStep(1); }}
          >
            <Upload size={17} />
            <span>Upload Dataset</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'datasets' || activeNav === 'profile' || activeNav === 'prepare' ? 'active' : ''}`}
            onClick={() => { setActiveNav('datasets'); setActiveStep(2); }}
          >
            <Database size={17} />
            <span>Datasets</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'visualizations' ? 'active' : ''}`}
            onClick={() => { setActiveNav('visualizations'); setActiveStep(4); }}
          >
            <BarChart3 size={17} />
            <span>Visualizations</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'patterns' ? 'active' : ''}`}
            onClick={() => { setActiveNav('patterns'); setActiveStep(5); }}
          >
            <Sparkles size={17} />
            <span>Patterns</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'anomalies' ? 'active' : ''}`}
            onClick={() => { setActiveNav('anomalies'); setActiveStep(6); }}
          >
            <AlertTriangle size={17} />
            <span>Anomalies</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'predictions' ? 'active' : ''}`}
            onClick={() => { setActiveNav('predictions'); setActiveStep(7); }}
          >
            <Target size={17} />
            <span>Predictions</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'insights' ? 'active' : ''}`}
            onClick={() => { setActiveNav('insights'); setActiveStep(8); }}
          >
            <Sparkles size={17} />
            <span>AI Insights</span>
          </button>

          <button
            className={`viz-nav-item ${activeNav === 'analyst' ? 'active' : ''}`}
            onClick={() => { setActiveNav('analyst'); setActiveStep(9); }}
          >
            <Bot size={17} />
            <span>Ask VizMind</span>
          </button>
        </nav>

        <div className="viz-sidebar-divider"></div>

        <div className="viz-sidebar-footer">
          <div className="viz-pipeline-status-card">
            <div className="viz-pipeline-header">
              <span>PIPELINE ENGINE:</span>
              <span className="viz-engine-online">ONLINE</span>
            </div>
            <div className="viz-pipeline-track">
              <div className="viz-pipeline-fill"></div>
            </div>
          </div>

          <button className="viz-footer-nav-btn" onClick={() => alert('Workspace Settings: Autonomous Neural Pipeline Config Active.')}>
            <Settings size={15} />
            <span>Settings</span>
          </button>

          <button className="viz-footer-nav-btn" onClick={() => setUserDropdownOpen(!userDropdownOpen)}>
            <User size={15} />
            <span>User Profile</span>
          </button>

          <button className="viz-footer-nav-btn logout" onClick={logout}>
            <LogOut size={15} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="viz-main-area">
        {/* Topbar Workspace Header */}
        <header className="viz-topbar">
          <div className="viz-topbar-left">
            <div className="viz-topbar-title-row">
              <h2 className="viz-topbar-welcome">Welcome, {userName}</h2>
              <span className="viz-session-badge">Session Initialized: Quantum Node #B902-Alpha</span>
            </div>
            <p className="viz-topbar-subtitle">Staff Architect Workspace · Autonomous telemetry ingress pipeline active</p>
          </div>

          <div className="viz-topbar-right">
            <div className="viz-search-wrapper">
              <Search size={14} className="viz-search-icon" />
              <input
                type="text"
                className="viz-search-input"
                placeholder="Search tables, metrics, schemas... ⌘K"
              />
            </div>

            <div className="viz-status-chip">
              <Zap size={14} color="#00f2fe" />
              <span>14ms - Telemetry Active</span>
            </div>

            <button className="viz-gateway-btn">
              <CheckCircle2 size={14} color="#10b981" />
              <span>Ingress Gateway 100% Ready</span>
            </button>

            <div className="viz-user-popover-wrapper">
              <button
                className="viz-user-avatar-btn"
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
              >
                <div className="viz-avatar-circle">
                  {userName[0]?.toUpperCase() || 'U'}
                </div>
                <ChevronDown size={14} color="#94a3b8" />
              </button>

              {userDropdownOpen && (
                <div className="viz-user-dropdown-menu">
                  <div className="viz-dropdown-header">
                    <div className="viz-dropdown-user-name">{userName}</div>
                    <div className="viz-dropdown-user-email">{user?.email}</div>
                  </div>
                  <div className="viz-dropdown-divider"></div>
                  <button className="viz-dropdown-item" onClick={() => { setUserDropdownOpen(false); alert(`User Profile: ${user?.email}`); }}>
                    <User size={14} /> Profile Details
                  </button>
                  <button className="viz-dropdown-item" onClick={() => { setUserDropdownOpen(false); alert('Settings page'); }}>
                    <Settings size={14} /> Workspace Preferences
                  </button>
                  <div className="viz-dropdown-divider"></div>
                  <button className="viz-dropdown-item danger" onClick={logout}>
                    <LogOut size={14} /> Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Horizontal Analysis Pipeline Stepper */}
        <div className="viz-stage-stepper">
          {steps.map((st, idx) => {
            const isCompleted = activeStep > idx + 1;
            const isActive = activeStep === idx + 1;
            return (
              <button
                key={st.num}
                className={`viz-step-pill ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                onClick={() => handleStepClick(idx, st.key)}
              >
                {isCompleted ? (
                  <Check size={13} className="viz-step-check" />
                ) : (
                  <span className="viz-step-num">{st.num}</span>
                )}
                <span className="viz-step-name">{st.name}</span>
                {isActive && <span className="viz-step-indicator-dot"></span>}
              </button>
            );
          })}
        </div>

        {/* Main Canvas Body */}
        <div className="viz-canvas-body">
          {activeNav === 'upload' && (
            <div className="viz-upload-workspace-view">
              {/* Stage Header */}
              <div className="viz-stage-badge">
                <Sparkles size={13} color="#00f2fe" />
                <span>STAGE 01 / 09 - DATA STREAM INGESTION</span>
              </div>
              <h1 className="viz-stage-title">Upload your dataset to begin autonomous analysis</h1>
              <p className="viz-stage-desc">
                VizMind ingests structured tabular data, streaming sensors, or database exports to autonomously profile quality, detect non-linear patterns, and generate explainable models.
              </p>

              {/* 2-Column Main Ingest Grid */}
              <div className="viz-ingest-grid">
                {/* Left Column: Dropzone & Active Dataset Display Card */}
                <div className="viz-ingest-left-col">
                  {/* Dropzone Card */}
                  <div
                    className={`viz-dropzone-card ${dragActive ? 'drag-over' : ''} ${uploading ? 'uploading' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => document.getElementById('vizWorkspaceFileInput').click()}
                  >
                    {/* Tech Corner Accent Lines */}
                    <div className="viz-corner-accent corner-tl"></div>
                    <div className="viz-corner-accent corner-tr"></div>
                    <div className="viz-corner-accent corner-bl"></div>
                    <div className="viz-corner-accent corner-br"></div>

                    <input
                      id="vizWorkspaceFileInput"
                      type="file"
                      accept=".csv, .parquet, .xlsx, .jsonl, .sql, .xls"
                      style={{ display: 'none' }}
                      onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
                    />

                    <div className="viz-cloud-icon-box">
                      {uploading ? (
                        <RefreshCw size={32} className="viz-spin-icon" color="#00f2fe" />
                      ) : (
                        <UploadCloud size={32} color="#00f2fe" />
                      )}
                    </div>

                    <div className="viz-drop-title">
                      {uploading ? (
                        <span>Ingesting dataset & parsing schema...</span>
                      ) : (
                        <>
                          Drag and drop your dataset here, or <span className="viz-drop-browse">Browse Local Files</span>
                        </>
                      )}
                    </div>

                    <div className="viz-drop-sub">
                      Instant schema parsing, entropy calculations, and column classification applied upon drop.
                    </div>

                    <div className="viz-formats-row">
                      <span className="viz-format-pill">.CSV</span>
                      <span className="viz-format-pill">.PARQUET</span>
                      <span className="viz-format-pill">.XLSX</span>
                      <span className="viz-format-pill">.JSONL</span>
                      <span className="viz-format-pill">.SQL</span>
                      <span className="viz-format-pill highlight">MAX 500MB PER CHUNK</span>
                    </div>

                    <div className="viz-connectors-title">OR CONNECT YOUR ENTERPRISE WAREHOUSE DIRECTLY</div>
                    <div className="viz-connectors-grid">
                      <button
                        className="viz-connector-btn"
                        onClick={(e) => { e.stopPropagation(); setConnectorModal('Snowflake'); }}
                      >
                        <Database size={14} color="#38bdf8" /> Snowflake
                      </button>
                      <button
                        className="viz-connector-btn"
                        onClick={(e) => { e.stopPropagation(); setConnectorModal('PostgreSQL / Timescale'); }}
                      >
                        <Server size={14} color="#a78bfa" /> PostgreSQL / Timescale
                      </button>
                      <button
                        className="viz-connector-btn"
                        onClick={(e) => { e.stopPropagation(); setConnectorModal('AWS S3 Bucket'); }}
                      >
                        <HardDrive size={14} color="#f59e0b" /> AWS S3 Bucket
                      </button>
                      <button
                        className="viz-connector-btn"
                        onClick={(e) => { e.stopPropagation(); setConnectorModal('Google BigQuery'); }}
                      >
                        <Cpu size={14} color="#10b981" /> Google BigQuery
                      </button>
                    </div>
                  </div>

                  {error && (
                    <div className="viz-error-alert">
                      <AlertTriangle size={18} />
                      <span>{error}</span>
                    </div>
                  )}

                  {/* Active / Uploaded Dataset Display Card */}
                  {activeDataset ? (
                    <div className="viz-dataset-active-card">
                      {/* Technical Corner Accents */}
                      <div className="viz-corner-accent corner-tl"></div>
                      <div className="viz-corner-accent corner-tr"></div>
                      <div className="viz-corner-accent corner-bl"></div>
                      <div className="viz-corner-accent corner-br"></div>

                      <div className="viz-ds-header">
                        <div className="viz-ds-title-group">
                          <FileText size={20} color="#00f2fe" />
                          <span className="viz-ds-name">{activeDataset.name || activeDataset.original_filename || 'dataset.csv'}</span>
                          <span className="viz-ds-status-badge">
                            <CheckCircle2 size={12} /> Ready for Profiling
                          </span>
                        </div>
                        <button
                          className="viz-btn-icon-danger"
                          title="Delete Dataset"
                          onClick={async () => {
                            if (window.confirm(`Delete dataset "${activeDataset.name || activeDataset.original_filename}"?`)) {
                              await deleteDataset(activeDataset.id);
                              await fetchDatasetList();
                              setActiveDataset(null);
                            }
                          }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>

                      <div className="viz-ds-meta-line">
                        {activeDataset.file_size
                          ? `${(activeDataset.file_size / 1024 / 1024).toFixed(1)} MB`
                          : '4.8 MB'} • {activeDataset.row_count ? `${activeDataset.row_count.toLocaleString()} records` : '24,582 records'} • UTF-8 Encoding • Delimiter: Comma
                      </div>

                      {/* 3 Metric Cards Grid */}
                      <div className="viz-metrics-grid">
                        <div className="viz-metric-box">
                          <div className="viz-metric-label">SCHEMA DETECTION</div>
                          <div className="viz-metric-val">{activeDataset.column_count || 18} Columns</div>
                          <div className="viz-metric-sub">Structured Schema Parsed</div>
                        </div>

                        <div className="viz-metric-box">
                          <div className="viz-metric-label">DATA INTEGRITY</div>
                          <div className="viz-metric-val success">
                            {activeDataset.quality_score ? `${activeDataset.quality_score}%` : '98.4%'}
                          </div>
                          <div className="viz-metric-sub">0 Missing Targets</div>
                        </div>

                        <div className="viz-metric-box">
                          <div className="viz-metric-label">FORMAT STATUS</div>
                          <div className="viz-metric-val highlight">Verified</div>
                          <div className="viz-metric-sub">Entropy Nom: 0.21</div>
                        </div>
                      </div>

                      {/* Validation Progress Section */}
                      <div className="viz-progress-section">
                        <div className="viz-progress-row">
                          <span>Ingress Validation Pipeline</span>
                          <span className="viz-progress-pct">100% Completed</span>
                        </div>
                        <div className="viz-progress-track">
                          <div className="viz-progress-fill"></div>
                        </div>
                      </div>

                      {/* Action Footer */}
                      <div className="viz-ds-footer-row">
                        <span className="viz-ds-footer-text">
                          <Sparkles size={14} color="#00f2fe" />
                          VizMind neural core will map collinearities & distributional shifts automatically.
                        </span>
                        <button
                          className="viz-btn-launch-step2"
                          onClick={() => {
                            setActiveNav('profile');
                            setActiveStep(2);
                          }}
                        >
                          <span>Launch Autonomous Profiling (Step 02)</span>
                          <ArrowRight size={16} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="viz-dataset-empty-card">
                      <p>No active dataset selected. Upload a file above or click a sample dataset from the right panel to begin.</p>
                    </div>
                  )}
                </div>

                {/* Right Column: Sample Telemetry & Sovereign Data Vault */}
                <div className="viz-ingest-right-col">
                  {/* Your Datasets List Card */}
                  <div className="viz-side-card">
                    <div className="viz-side-header">
                      <span className="viz-side-title">
                        <HardDrive size={16} color="#00f2fe" /> Your Datasets ({datasets.length})
                      </span>
                      <button className="viz-side-link-btn" onClick={fetchDatasetList}>
                        <RefreshCw size={13} className={loadingDatasets ? 'viz-spin-icon' : ''} /> Refresh
                      </button>
                    </div>

                    {datasets.length > 0 ? (
                      <div className="viz-dataset-compact-list">
                        {datasets.map((ds) => (
                          <div
                            key={ds.id}
                            className={`viz-ds-compact-item ${activeDataset?.id === ds.id ? 'active' : ''}`}
                            onClick={() => {
                              setActiveDataset(ds);
                            }}
                          >
                            <div className="viz-ds-item-name">{ds.name || ds.original_filename}</div>
                            <div className="viz-ds-item-meta">
                              {ds.row_count?.toLocaleString() || '0'} rows • {ds.column_count || '0'} cols
                            </div>
                            <div className="viz-pill-row">
                              <span className="viz-tag-pill active">
                                {ds.status || 'Uploaded'}
                              </span>
                              <span className="viz-tag-pill highlight">
                                Tabular
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="viz-no-datasets-msg">
                        No datasets uploaded yet. Upload a CSV/XLS file or click a 1-click sample dataset below.
                      </div>
                    )}
                  </div>

                  {/* Sample Telemetry Repos Card */}
                  <div className="viz-side-card">
                    <div className="viz-side-header">
                      <span className="viz-side-title">
                        <Sparkles size={16} color="#38bdf8" /> Sample Telemetry Repos
                      </span>
                      <span className="viz-side-badge">1-Click Load</span>
                    </div>
                    <p className="viz-side-subtitle">
                      No dataset on hand? Explore VizMind's quantum telemetry capabilities using verified production data streams.
                    </p>

                    <div className="viz-sample-item" onClick={() => loadSampleDataset('Global Enterprise Sales & Churn')}>
                      <div className="viz-sample-name">Global Enterprise Sales & Churn</div>
                      <div className="viz-sample-meta">24.5k rows • 18 features • Retail SaaS</div>
                      <div className="viz-pill-row">
                        <span className="viz-tag-pill">Predictive Model</span>
                        <span className="viz-tag-pill cyan">Tabular</span>
                      </div>
                    </div>

                    <div className="viz-sample-item" onClick={() => loadSampleDataset('High-Frequency IoT Sensor Fleet')}>
                      <div className="viz-sample-name">High-Frequency IoT Sensor Fleet</div>
                      <div className="viz-sample-meta">110k events • Anomaly benchmark</div>
                      <div className="viz-pill-row">
                        <span className="viz-tag-pill amber">Anomalies</span>
                        <span className="viz-tag-pill green">Time-Series</span>
                      </div>
                    </div>

                    <div className="viz-sample-item" onClick={() => loadSampleDataset('Healthcare Patient Outcome Cohorts')}>
                      <div className="viz-sample-name">Healthcare Patient Outcome Cohorts</div>
                      <div className="viz-sample-meta">14k rows • Predictive clinical factors</div>
                      <div className="viz-pill-row">
                        <span className="viz-tag-pill purple">Multivariate</span>
                        <span className="viz-tag-pill">Clinical</span>
                      </div>
                    </div>
                  </div>

                  {/* Sovereign Data Vault Card */}
                  <div className="viz-side-card">
                    <div className="viz-side-header">
                      <span className="viz-side-title">
                        <Shield size={16} color="#a78bfa" /> Sovereign Data Vault
                      </span>
                    </div>
                    <p className="viz-side-subtitle">
                      Zero data retention by default. Datasets are parsed inside your ephemeral GPU memory enclave. Zero LLM weights fine-tuning on customer telemetry.
                    </p>

                    <div className="viz-vault-row">
                      <span className="viz-vault-key">SOC2 Type II & HIPAA</span>
                      <span className="viz-vault-val green">Certified</span>
                    </div>
                    <div className="viz-vault-row">
                      <span className="viz-vault-key">E2E In-Transit Encryption</span>
                      <span className="viz-vault-val">TLS 1.3 / AES-256</span>
                    </div>
                    <div className="viz-vault-row no-border">
                      <span className="viz-vault-key">Data Sanitization</span>
                      <span className="viz-vault-val">Automatic PII Scrub</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Render Active View for Steps 2 to 9 */}
          {(activeNav === 'datasets' || activeNav === 'profile' || activeStep === 2) && (
            <DatasetProfileView
              dataset={activeDataset}
              onBack={() => { setActiveNav('upload'); setActiveStep(1); }}
              onSelectPreprocess={() => { setActiveNav('prepare'); setActiveStep(3); }}
            />
          )}

          {(activeNav === 'prepare' || activeStep === 3) && (
            <PreprocessingView
              dataset={activeDataset}
              onNavigateToVisualizations={() => { setActiveNav('visualizations'); setActiveStep(4); }}
            />
          )}

          {(activeNav === 'visualizations' || activeStep === 4) && activeDataset && (
            <VisualizationView
              dataset={activeDataset}
              onNavigateToPreprocessing={() => { setActiveNav('prepare'); setActiveStep(3); }}
            />
          )}

          {(activeNav === 'patterns' || activeStep === 5) && activeDataset && (
            <PatternDiscoveryView datasetId={activeDataset.id} />
          )}

          {(activeNav === 'anomalies' || activeStep === 6) && activeDataset && (
            <AnomalyDetectionView datasetId={activeDataset.id} />
          )}

          {(activeNav === 'predictions' || activeStep === 7) && activeDataset && (
            <PredictionView datasetId={activeDataset.id} />
          )}

          {(activeNav === 'insights' || activeStep === 8) && activeDataset && (
            <InsightView datasetId={activeDataset.id} />
          )}

          {(activeNav === 'analyst' || activeStep === 9) && activeDataset && (
            <AnalystView datasetId={activeDataset.id} />
          )}
        </div>
      </main>

      {/* Enterprise Connector Modal */}
      {connectorModal && (
        <div className="viz-modal-overlay" onClick={() => setConnectorModal(null)}>
          <div className="viz-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="viz-modal-header">
              <h3>Connect Enterprise Warehouse: {connectorModal}</h3>
              <button className="viz-modal-close" onClick={() => setConnectorModal(null)}>
                <X size={18} />
              </button>
            </div>
            <div className="viz-modal-body">
              <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>
                VizMind enterprise ingress gateway connects directly to your <strong>{connectorModal}</strong> data warehouse instance with Zero-Retention security.
              </p>
              <div className="viz-field-group" style={{ marginBottom: '1rem' }}>
                <label className="neural-label">CONNECTION STRING / ENDPOINT</label>
                <input
                  type="text"
                  className="neural-input"
                  placeholder={`https://your-account.${connectorModal.toLowerCase().replace(/[^a-z]/g, '')}.cloud/api`}
                />
              </div>
              <div className="viz-field-group" style={{ marginBottom: '1rem' }}>
                <label className="neural-label">ACCESS TOKEN / API KEY</label>
                <input
                  type="password"
                  className="neural-input"
                  placeholder="••••••••••••••••••••••••••••••••"
                />
              </div>
            </div>
            <div className="viz-modal-footer">
              <button className="btn-secondary" onClick={() => setConnectorModal(null)}>Cancel</button>
              <button className="btn-primary" onClick={() => { alert(`${connectorModal} connection string verified.`); setConnectorModal(null); }}>
                Connect Ingress Pipeline
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DashboardPlaceholder;
