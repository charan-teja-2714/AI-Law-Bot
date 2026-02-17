import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Login from './components/Login';
import Register from './components/Register';
import { api } from './services/api';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showRegister, setShowRegister] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('session_token');
    const user = localStorage.getItem('username');
    
    if (token && user) {
      api.verifySession(token)
        .then(data => {
          if (data) {
            setSessionToken(token);
            setUsername(user);
            setIsAuthenticated(true);
          } else {
            localStorage.removeItem('session_token');
            localStorage.removeItem('username');
          }
        })
        .catch(() => {
          localStorage.removeItem('session_token');
          localStorage.removeItem('username');
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLoginSuccess = (token, user) => {
    setSessionToken(token);
    setUsername(user);
    setIsAuthenticated(true);
    localStorage.setItem('needs_new_session', 'true');
  };

  const handleLogout = async () => {
    try {
      await api.logout(sessionToken);
    } catch (err) {
      console.error('Logout error:', err);
    }
    
    localStorage.removeItem('session_token');
    localStorage.removeItem('username');
    localStorage.removeItem('needs_new_session');
    setSessionToken(null);
    setUsername(null);
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="App" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="App">
      {isAuthenticated ? (
        <ChatInterface 
          sessionToken={sessionToken} 
          username={username} 
          onLogout={handleLogout}
        />
      ) : showRegister ? (
        <Register 
          onRegisterSuccess={handleLoginSuccess}
          onSwitchToLogin={() => setShowRegister(false)}
        />
      ) : (
        <Login 
          onLoginSuccess={handleLoginSuccess}
          onSwitchToRegister={() => setShowRegister(true)}
        />
      )}
    </div>
  );
}

export default App;
