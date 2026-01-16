import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import RoleToggle from './RoleToggle';
import QuestionsDialog from './QuestionsDialog';
import { api } from '../services/api';

function ChatInterface() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([]);
  const [role, setRole] = useState('patient');
  const [pdfUploaded, setPdfUploaded] = useState(false);
  const [pdfName, setPdfName] = useState('');
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState(null);
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [darkMode, setDarkMode] = useState(true);

  // Toggle theme
  const toggleTheme = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle('light-mode');
  };

  // Close sidebar on mobile when clicking overlay
  const handleOverlayClick = () => {
    if (window.innerWidth <= 768) {
      setSidebarOpen(false);
    }
  };

  const handlePDFUpload = async (file) => {
    setLoading(true);
    try {
      await api.uploadPDF(file, sessionId);
      setPdfUploaded(true);
      setPdfName(file.name);
    } catch (error) {
      alert('Error uploading PDF');
    }
    setLoading(false);
    setShowUploadMenu(false);
  };

  const handleSendMessage = async (message) => {
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);
    
    setLoading(true);
    try {
      const response = await api.sendMessage(sessionId, message, role);
      const aiMessage = { role: 'assistant', content: response.response };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      alert('Error sending message');
    }
    setLoading(false);
  };

  const handleGenerateQuestions = async () => {
    setLoading(true);
    try {
      const response = await api.generateQuestions(sessionId);
      setQuestions(response.questions);
    } catch (error) {
      alert('Error generating questions');
    }
    setLoading(false);
  };

  return (
    <>
      {/* Sidebar Overlay for Mobile */}
      <div 
        className={`sidebar-overlay ${sidebarOpen && window.innerWidth <= 768 ? 'active' : ''}`}
        onClick={handleOverlayClick}
      />
      
      {/* Sidebar */}
      <div className={`sidebar ${!sidebarOpen ? 'closed' : ''}`}>
        <div className="sidebar-header">
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', marginBottom: '6px', color: '#8e8ea0' }}>
              Explanation Mode
            </div>
            <RoleToggle role={role} onChange={setRole} />
          </div>
          
          <button className="new-chat-btn" onClick={() => window.location.reload()}>
            <span>+</span> New Chat
          </button>
        </div>
        
        <div className="sidebar-content">
          <div className="sidebar-section">
            <div className="sidebar-section-title">Recent Chats</div>
            <div className="chat-history-item active">
              💬 Current Session
            </div>
          </div>
        </div>
        
        <div className="sidebar-footer">
          {pdfUploaded && (
            <button 
              onClick={handleGenerateQuestions} 
              disabled={loading}
              className="generate-questions-btn"
            >
              {loading ? <span className="loading-spinner"></span> : '📝'} Generate Questions
            </button>
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-container">
        <div className="chat-header">
          <button 
            className="sidebar-toggle-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            title="Toggle sidebar"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
          <button 
            className="hamburger-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <h1>🩺 MediSense AI</h1>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            {pdfUploaded && (
              <div className="pdf-status">
                ✓ {pdfName}
              </div>
            )}
            <button 
              className="theme-toggle-btn"
              onClick={toggleTheme}
              title="Toggle theme"
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
        
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">💬</div>
              <div className="empty-state-text">
                Start asking questions about your medical report
              </div>
            </div>
          ) : (
            <MessageList messages={messages} />
          )}
        </div>
        
        <div className="input-container">
          <MessageInput 
            onSend={handleSendMessage} 
            disabled={loading}
            onAttachClick={() => setShowUploadMenu(!showUploadMenu)}
            showUploadMenu={showUploadMenu}
            onFileUpload={handlePDFUpload}
            loading={loading}
          />
        </div>
      </div>
      
      {questions && (
        <QuestionsDialog 
          questions={questions} 
          onClose={() => setQuestions(null)} 
        />
      )}
    </>
  );
}

export default ChatInterface;
