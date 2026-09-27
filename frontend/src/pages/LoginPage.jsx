import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Key, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import vizmindLogo from '../assets/vizmind-logo.jpg';

export function LoginPage() {
  const { login, register } = useAuth();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await register(email, password);
      } else {
        await login(email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="neural-login-wrapper">
      {/* Ambient background glows & mesh */}
      <div className="neural-bg-glow glow-top-left"></div>
      <div className="neural-bg-glow glow-top-right"></div>
      <div className="neural-bg-glow glow-bottom-right"></div>
      <div className="neural-grid-overlay"></div>

      <div className="neural-login-container">
        {/* Brand Header with Uploaded Logo */}
        <div className="neural-brand-header">
          <div className="neural-logo-wrapper">
            <img src={vizmindLogo} alt="VizMind AI" className="neural-brand-logo-img" />
          </div>
          <p className="neural-brand-tagline">Understand Your Data Instantly.</p>
        </div>

        {/* Main Auth Card */}
        <div className="neural-card">
          {/* Tabs */}
          <div className="neural-tabs-bar">
            <button
              type="button"
              className={`neural-tab ${!isRegister ? 'active' : ''}`}
              onClick={() => { setIsRegister(false); setError(''); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`neural-tab ${isRegister ? 'active' : ''}`}
              onClick={() => { setIsRegister(true); setError(''); }}
            >
              Create Account
            </button>
          </div>

          {error && <div className="neural-error-box">{error}</div>}

          {/* Form */}
          <form onSubmit={handleSubmit} className="neural-form">
            {/* Field 1: Email */}
            <div className="neural-field-group">
              <label className="neural-label">EMAIL</label>
              <div className="neural-input-wrapper">
                <User size={18} className="neural-input-icon" />
                <input
                  type="email"
                  className="neural-input"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                />
              </div>
            </div>

            {/* Field 2: Password */}
            <div className="neural-field-group">
              <label className="neural-label">PASSWORD</label>
              <div className="neural-input-wrapper">
                <Key size={18} className="neural-input-icon" />
                <input
                  type="password"
                  className="neural-input"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="neural-submit-btn"
              disabled={loading}
            >
              <span>
                {loading
                  ? 'Processing...'
                  : isRegister
                  ? 'Create VizMind Account'
                  : 'Enter Workspace'}
              </span>
              <ArrowRight size={18} className="neural-btn-arrow" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
