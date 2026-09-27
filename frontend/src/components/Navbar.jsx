import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { AuthModal } from './AuthModal';
import vizmindLogo from '../assets/vizmind-logo.jpg';

export function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useAuth();
  const [authModalOpen, setAuthModalOpen] = useState(false);

  const handleDashboardClick = (e) => {
    e.preventDefault();
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  };

  return (
    <header className="navbar">
      <div className="container navbar-content">
        <Link to="/" className="brand">
          <img src={vizmindLogo} alt="VizMind AI" className="navbar-brand-logo" />
        </Link>
        <nav className="nav-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Home
          </Link>
          <a
            href="/dashboard"
            onClick={handleDashboardClick}
            className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
          >
            Dashboard
          </a>
          
          {isAuthenticated ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div className="user-badge">
                <div className="user-avatar">{user?.email?.[0]?.toUpperCase() || 'U'}</div>
                <span>{user?.email}</span>
              </div>
              <button onClick={logout} className="btn-secondary" title="Sign Out" style={{ padding: '0.4rem 0.8rem' }}>
                <LogOut size={16} /> Sign Out
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center' }}>
              <User size={16} style={{ marginRight: '0.4rem' }} />
              Sign In / Register
            </Link>
          )}

          <button onClick={handleDashboardClick} className="btn-primary">
            <LayoutDashboard size={16} />
            Workspace Dashboard
          </button>
        </nav>
      </div>

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
    </header>
  );
}
