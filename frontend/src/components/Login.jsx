import React, { useState } from 'react';
import { api } from '../services/api';

function Login({ onLoginSuccess, onSwitchToRegister }) {
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.login(loginId, password);
      localStorage.setItem('session_token', response.session_token);
      localStorage.setItem('username', response.username);
      onLoginSuccess(response.session_token, response.username);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>AI Law Bot</h1>
        <p className="auth-subtitle">Indian Legal Assistant</p>
        <div className="auth-divider" />

        <form onSubmit={handleSubmit} className="auth-form">
          <input
            type="text"
            placeholder="Username or Email"
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
            required
            disabled={loading}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={loading}
          />

          {error && <div className="auth-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Sign In'}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account?{' '}
          <span onClick={onSwitchToRegister}>Create one</span>
        </p>
      </div>
    </div>
  );
}

export default Login;
