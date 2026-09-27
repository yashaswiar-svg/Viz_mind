import React, { useState, useEffect } from 'react';
import { discoverPatterns, getPatterns } from '../services/api';
import PatternSummary from './PatternSummary';
import PatternCard from './PatternCard';
import PatternStatistics from './PatternStatistics';

export default function PatternDiscoveryView({ datasetId }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [patterns, setPatterns] = useState([]);
  const [selectedPattern, setSelectedPattern] = useState(null);

  const [activeFilter, setActiveFilter] = useState('ALL');
  const [significantOnly, setSignificantOnly] = useState(false);

  const fetchPatternData = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getPatterns(datasetId);
      setSummaryData(res);
      setPatterns(res?.patterns || []);
    } catch (err) {
      console.error("Failed to fetch pattern discovery results:", err);
      setError(err.message || "Failed to load pattern discovery results.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatternData();
  }, [datasetId]);

  const handleRunDiscovery = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await discoverPatterns(datasetId);
      setSummaryData(res);
      setPatterns(res?.patterns || []);
    } catch (err) {
      console.error("Pattern discovery failed:", err);
      setError(err.message || "Pattern discovery execution failed.");
    } finally {
      setLoading(false);
    }
  };

  // Filter pattern list
  const filteredPatterns = patterns.filter((p) => {
    if (activeFilter !== 'ALL' && p.pattern_type.toUpperCase() !== activeFilter) {
      return false;
    }
    if (significantOnly && !p.significant) {
      return false;
    }
    return true;
  });

  const isNotStarted = !summaryData?.run?.status || summaryData.run.status === 'NOT_STARTED';

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', margin: 0, color: '#f8fafc' }}>
            Pattern Discovery Intelligence
          </h1>
          <p style={{ fontSize: '14px', color: '#94a3b8', margin: '4px 0 0 0' }}>
            Statistically supported correlations, group differences, categorical associations, and temporal trends.
          </p>
        </div>

        <button
          onClick={handleRunDiscovery}
          disabled={loading}
          style={{
            background: loading ? '#475569' : '#38bdf8',
            color: '#0f172a',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '10px',
            fontWeight: '700',
            fontSize: '14px',
            cursor: loading ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 14px rgba(56, 189, 248, 0.3)',
            transition: 'all 0.2s ease',
          }}
        >
          {loading ? 'Analyzing Data...' : 'Discover Patterns'}
        </button>
      </div>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#fca5a5',
          padding: '16px',
          borderRadius: '10px',
          marginBottom: '24px',
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {!isNotStarted && summaryData && (
        <PatternSummary
          totalPatterns={summaryData.total_patterns}
          significantPatterns={summaryData.significant_patterns}
          strongPatterns={summaryData.strong_patterns}
          runInfo={summaryData.run}
        />
      )}

      {/* Filter Bar */}
      {!isNotStarted && (
        <div style={{
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '24px',
          background: 'rgba(255, 255, 255, 0.03)',
          padding: '12px 16px',
          borderRadius: '12px',
        }}>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {['ALL', 'CORRELATION', 'GROUP_DIFFERENCE', 'CATEGORICAL_ASSOCIATION', 'TIME_TREND', 'DISTRIBUTION'].map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                style={{
                  background: activeFilter === filter ? '#38bdf8' : 'rgba(255, 255, 255, 0.05)',
                  color: activeFilter === filter ? '#0f172a' : '#94a3b8',
                  border: 'none',
                  padding: '6px 14px',
                  borderRadius: '20px',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                }}
              >
                {filter === 'ALL' ? 'All Types' : filter.replace('_', ' ')}
              </button>
            ))}
          </div>

          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '13px', color: '#cbd5e1' }}>
            <input
              type="checkbox"
              checked={significantOnly}
              onChange={(e) => setSignificantOnly(e.target.checked)}
              style={{ accentColor: '#38bdf8' }}
            />
            Statistically Significant Only
          </label>
        </div>
      )}

      {/* Main Content State */}
      {isNotStarted ? (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px dashed rgba(255, 255, 255, 0.1)',
          borderRadius: '16px',
        }}>
          <h3 style={{ fontSize: '18px', color: '#e2e8f0', marginBottom: '8px' }}>
            No Pattern Discovery Analysis Run Yet
          </h3>
          <p style={{ color: '#94a3b8', fontSize: '14px', maxWidth: '500px', margin: '0 auto 20px auto' }}>
            Click "Discover Patterns" to run deterministic statistical algorithms (correlation, ANOVA, Chi-square, trend detection) on your preprocessed dataset.
          </p>
          <button
            onClick={handleRunDiscovery}
            disabled={loading}
            style={{
              background: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer',
            }}
          >
            Run Pattern Discovery Engine
          </button>
        </div>
      ) : filteredPatterns.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: '12px',
          color: '#94a3b8',
        }}>
          No patterns match the selected filter criteria.
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
          gap: '20px',
        }}>
          {filteredPatterns.map((pat) => (
            <PatternCard
              key={pat.id}
              pattern={pat}
              onOpenDetails={(p) => setSelectedPattern(p)}
            />
          ))}
        </div>
      )}

      {/* Detailed Statistics Modal */}
      {selectedPattern && (
        <PatternStatistics
          pattern={selectedPattern}
          onClose={() => setSelectedPattern(null)}
        />
      )}
    </div>
  );
}
