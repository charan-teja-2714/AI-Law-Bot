import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Auth from './components/Auth';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('session_token');
    const user = localStorage.getItem('username');
    
    if (token && user) {
      // Verify session is still valid
      fetch(`http://localhost:8000/api/verify-session?session_token=${token}`)
        .then(res => {
          if (res.ok) {
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

  const handleLogin = (token, user) => {
    setSessionToken(token);
    setUsername(user);
    setIsAuthenticated(true);
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:8000/api/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token: sessionToken })
      });
    } catch (err) {
      console.error('Logout error:', err);
    }
    
    localStorage.removeItem('session_token');
    localStorage.removeItem('username');
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
      ) : (
        <Auth onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;
