import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import LanguageSelector from './LanguageSelector';
import Toast from './Toast';
import LegalAnalysisView from './LegalAnalysisView';
import DocumentList from './DocumentList';
import { api } from '../services/api';

function ChatInterface() {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [originalMessages, setOriginalMessages] = useState([]); // Store original untranslated messages
  const [language, setLanguage] = useState('en');
  const [translating, setTranslating] = useState(false);
  const [documentUploaded, setDocumentUploaded] = useState(false);
  const [documentName, setDocumentName] = useState('');
  const [documents, setDocuments] = useState([]);
  const [selectedDocs, setSelectedDocs] = useState([]);
  const [docSearchQuery, setDocSearchQuery] = useState('');
  const [showDocuments, setShowDocuments] = useState(false);
  const [entities, setEntities] = useState(null);
  const [extractingEntities, setExtractingEntities] = useState(false);
  const [loading, setLoading] = useState(false);
  const [documentLoading, setDocumentLoading] = useState(false);
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [toast, setToast] = useState(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [legalAnalysis, setLegalAnalysis] = useState(null);
  const [analyzingDocument, setAnalyzingDocument] = useState(false);
  const messagesEndRef = useRef(null);
  const isInitialMount = useRef(true);

  // Load existing sessions or create new one on startup
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      
      // First, try to load existing sessions
      api.getAllSessions().then(data => {
        const existingSessions = data.sessions || [];
        setSessions(existingSessions);
        
        if (existingSessions.length > 0) {
          // Load the most recent session
          setSessionId(existingSessions[0].session_id);
        } else {
          // No sessions exist, create a new one
          api.createNewSession().then(response => {
            setSessionId(response.session_id);
            setSessions([{
              session_id: response.session_id,
              created_at: new Date().toISOString(),
              last_activity: new Date().toISOString(),
              message_count: 0,
              preview: 'New conversation'
            }]);
          }).catch(error => {
            console.error('Failed to create initial session:', error);
          });
        }
      }).catch(error => {
        console.error('Failed to load sessions:', error);
      });
    }
  }, []);

  // Load chat history for current session
  useEffect(() => {
    if (sessionId && !isInitialMount.current) {
      loadChatHistory(sessionId);
      loadDocuments(sessionId);
    }
  }, [sessionId]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Translate messages when language changes
  useEffect(() => {
    const translateMessages = async () => {
      if (messages.length === 0) return;
      if (language === 'en' && originalMessages.length === 0) {
        // English is default, store as original
        setOriginalMessages([...messages]);
        return;
      }

      setTranslating(true);
      try {
        // If we have originals, translate from those. Otherwise use current messages.
        const messagesToTranslate = originalMessages.length > 0 ? originalMessages : messages;

        if (language === 'en') {
          // Going back to English, use originals
          setMessages(messagesToTranslate);
        } else {
          // Translate all messages to target language
          const translatedMessages = await Promise.all(
            messagesToTranslate.map(async (msg) => {
              try {
                const result = await api.translateText(msg.content, language);
                return {
                  role: msg.role,
                  content: result.translated_text
                };
              } catch (error) {
                console.error('Translation error:', error);
                return msg; // Return original if translation fails
              }
            })
          );
          setMessages(translatedMessages);

          // Store originals if we haven't yet
          if (originalMessages.length === 0) {
            setOriginalMessages(messagesToTranslate);
          }
        }
      } catch (error) {
        console.error('Failed to translate messages:', error);
        setToast({ message: 'Translation failed. Using original language.', type: 'error' });
      }
      setTranslating(false);
    };

    translateMessages();
  }, [language]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadChatHistory = async (sid) => {
    try {
      const history = await api.getHistory(sid);
      if (history.messages && history.messages.length > 0) {
        setMessages(history.messages.map(msg => ({
          role: msg.role,
          content: msg.content
        })));
      } else {
        setMessages([]);
      }
    } catch (error) {
      console.log('No history for this session');
      setMessages([]);
    }
  };

  const loadAllSessions = async () => {
    try {
      const data = await api.getAllSessions();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const loadDocuments = async (sid) => {
    try {
      const data = await api.getDocuments(sid, docSearchQuery || null);
      setDocuments(data.documents || []);
      setDocumentUploaded(data.documents && data.documents.length > 0);
      setSelectedDocs([]); // Clear selection when loading documents
      setEntities(null); // Clear entities when loading documents
    } catch (error) {
      console.error('Failed to load documents:', error);
      setDocuments([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const response = await api.createNewSession();
      setSessionId(response.session_id);
      setMessages([]);
      setOriginalMessages([]);
      setDocumentUploaded(false);
      setDocumentName('');
      setDocuments([]);
      setSelectedDocs([]);
      loadAllSessions();
    } catch (error) {
      console.error('Failed to create new session:', error);
    }
  };

  const handleLoadSession = (sid) => {
    if (sid === sessionId) return;

    setSessionId(sid);
    setMessages([]);
    setOriginalMessages([]);
    setDocumentUploaded(false);
    setDocumentName('');
    setDocuments([]);
    setSelectedDocs([]);
  };

  const handleDocumentUpload = async (file) => {
    setDocumentLoading(true);
    setEntities(null); // Clear old entities
    try {
      await api.uploadDocument(file, sessionId);
      setToast({ message: `Document "${file.name}" uploaded successfully!`, type: 'success' });
      const data = await api.getDocuments(sessionId, null);
      const docs = data.documents || [];
      setDocuments(docs);
      setDocumentUploaded(docs.length > 0);
      loadAllSessions();
      
      // Auto-extract entities from all documents
      if (docs.length > 0) {
        const allDocIds = docs.map(d => d.document_id);
        setSelectedDocs(allDocIds);
        setShowDocuments(true);
        setTimeout(async () => {
          setExtractingEntities(true);
          try {
            const result = await api.extractEntities(sessionId, allDocIds);
            setEntities(result.entities);
          } catch (error) {
            setToast({ message: 'Error extracting entities: ' + error.message, type: 'error' });
          }
          setExtractingEntities(false);
        }, 500);
      }
    } catch (error) {
      setToast({ message: 'Error uploading document: ' + error.message, type: 'error' });
    }
    setDocumentLoading(false);
    setShowUploadMenu(false);
  };

  const handleAudioVideoUpload = async (file) => {
    setDocumentLoading(true);
    try {
      const response = await api.uploadAudioVideo(file, sessionId);
      setToast({ message: `Audio/Video "${file.name}" transcribed successfully!`, type: 'success' });
      const transcriptionMsg = {
        role: 'assistant',
        content: `📝 **Transcription:**\n\n${response.transcription}`
      };
      setMessages((prev) => [...prev, transcriptionMsg]);
      loadDocuments(sessionId);
      loadAllSessions();
    } catch (error) {
      setToast({ message: 'Error processing audio/video: ' + error.message, type: 'error' });
    }
    setDocumentLoading(false);
    setShowUploadMenu(false);
  };

  const handleAudioInput = async (file) => {
    try {
      const result = await api.transcribeAudio(file);
      console.log('Transcription API result:', result);
      return result;
    } catch (error) {
      setToast({ message: 'Error transcribing audio: ' + error.message, type: 'error' });
      throw error;
    }
  };

  const handleSendMessage = async (message) => {
    // Show user message immediately (in original language for now)
    const userMessage = { role: 'user', content: message };
    setMessages((prev) => [...prev, userMessage]);

    setLoading(true);
    try {
      const response = await api.sendMessage(
        sessionId,
        message,
        language,
        false // No structured mode
      );

      // AI response should already be translated by backend
      const aiMessage = { role: 'assistant', content: response.response };
      setMessages((prev) => [...prev, aiMessage]);

      loadAllSessions(); // Refresh to update preview
    } catch (error) {
      const errorMsg = {
        role: 'assistant',
        content: `⚠️ **Error:** ${error.message}\n\nPlease try again or rephrase your question.`
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
    setLoading(false);
  };

  const handleAnalyzeDocument = async () => {
    if (selectedDocs.length === 0) {
      setToast({ message: 'Please select documents to analyze', type: 'error' });
      return;
    }

    setAnalyzingDocument(true);
    try {
      const analysis = await api.analyzeDocument(sessionId, selectedDocs);
      setLegalAnalysis(analysis);
      setShowAnalysis(true);
    } catch (error) {
      setToast({ message: 'Error analyzing document: ' + error.message, type: 'error' });
    }
    setAnalyzingDocument(false);
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await api.deleteDocument(sessionId, documentId);
      setToast({ message: 'Document deleted successfully', type: 'success' });
      loadDocuments(sessionId);
      setSelectedDocs(selectedDocs.filter(id => id !== documentId));
      setEntities(null); // Clear entities when document deleted
    } catch (error) {
      setToast({ message: 'Error deleting document: ' + error.message, type: 'error' });
    }
  };

  const handleExtractEntities = async () => {
    if (selectedDocs.length === 0) {
      setToast({ message: 'Please select documents to extract entities', type: 'error' });
      return;
    }
    
    console.log('[EXTRACT] Selected docs:', selectedDocs);
    setExtractingEntities(true);
    setEntities(null); // Clear old entities before extracting
    try {
      const result = await api.extractEntities(sessionId, selectedDocs);
      console.log('[EXTRACT] Result:', result);
      setEntities(result.entities);
    } catch (error) {
      setToast({ message: 'Error extracting entities: ' + error.message, type: 'error' });
    }
    setExtractingEntities(false);
  };

  const handleDeleteSession = async (sid, event) => {
    event.stopPropagation(); // Prevent triggering handleLoadSession

    try {
      await api.deleteSession(sid);

      // Reload sessions first to get updated list
      const data = await api.getAllSessions();
      const remainingSessions = data.sessions || [];
      setSessions(remainingSessions);

      // If deleting current session
      if (sid === sessionId) {
        if (remainingSessions.length > 0) {
          // Switch to the first remaining session
          const nextSession = remainingSessions[0];
          setSessionId(nextSession.session_id);
          setMessages([]);
          setOriginalMessages([]);
          setDocumentUploaded(false);
          setDocumentName('');
        } else {
          // No sessions left, create a new one
          handleNewChat();
        }
      }

      setToast({ message: 'Session deleted successfully', type: 'success' });
    } catch (error) {
      setToast({ message: 'Error deleting session: ' + error.message, type: 'error' });
    }
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      const now = new Date();
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Recently';
      }
      
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays === 1) return 'Yesterday';
      if (diffDays < 7) return `${diffDays}d ago`;
      return date.toLocaleDateString();
    } catch (error) {
      return 'Recently';
    }
  };

  return (
    <>
      {/* Sidebar */}
      <div className={`sidebar ${!sidebarOpen ? 'closed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            ⚖️ AI Law Bot
          </div>

          <button className="new-chat-btn" onClick={handleNewChat} disabled={loading || documentLoading}>
            <span>+</span> New Chat
          </button>
        </div>

        <div className="sidebar-content">
          {/* Chat History */}
          <div className="sidebar-section">
            <div className="sidebar-section-title">Chat History</div>
            <div className="sessions-list">
              {sessions.length === 0 ? (
                <div className="no-sessions">No previous chats</div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`session-item ${session.session_id === sessionId ? 'active' : ''}`}
                    onClick={() => handleLoadSession(session.session_id)}
                  >
                    <div className="session-content">
                      <div className="session-preview">{session.preview}</div>
                      <div className="session-meta">
                        <span className="session-time">{formatDate(session.last_activity)}</span>
                      </div>
                    </div>
                    <button
                      className="delete-session-btn"
                      onClick={(e) => handleDeleteSession(session.session_id, e)}
                      title="Delete session"
                    >
                      🗑️
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Language Selector */}
          <div className="sidebar-section">
            <div className="sidebar-section-title">Language</div>
            <LanguageSelector language={language} onChange={setLanguage} />
          </div>

          {/* Current Session Info */}
          <div className="sidebar-section">
            <div className="sidebar-section-title">Documents ({documents.length})</div>
            <div className="session-info">
              {documentUploaded ? (
                <button
                  className="action-btn"
                  onClick={() => setShowDocuments(!showDocuments)}
                >
                  {showDocuments ? '▼ Hide Documents' : '▶ Show Documents'}
                </button>
              ) : (
                <div className="no-doc">No documents uploaded</div>
              )}
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="sidebar-info">
            AI Law Bot v2.0<br />
            Indian Legal Assistant
          </div>
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
          <div className="header-title">
            <h1>AI Law Bot</h1>
            <p className="header-subtitle">Indian Legal RAG Assistant</p>
          </div>
        </div>

        {documentLoading && (
          <div className="upload-loading-banner">
            <div className="loading-spinner"></div>
            <span>Processing document, please wait...</span>
          </div>
        )}

        {translating && (
          <div className="upload-loading-banner" style={{ background: '#80b7df' }}>
            <div className="loading-spinner"></div>
            <span>Translating messages...</span>
          </div>
        )}

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">⚖️</div>
              <div className="empty-state-text">
                Welcome to AI Law Bot - Indian Legal Assistant
              </div>
              <div className="empty-state-subtext">
                Ask legal questions or upload documents (PDF, audio, video) for analysis
              </div>
            </div>
          ) : (
            <>
              <MessageList messages={messages} isLoading={loading} />
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="input-container">
          <MessageInput
            onSend={handleSendMessage}
            disabled={loading || documentLoading}
            onAttachClick={() => setShowUploadMenu(!showUploadMenu)}
            showUploadMenu={showUploadMenu}
            onDocumentUpload={handleDocumentUpload}
            onAudioVideoUpload={handleAudioVideoUpload}
            onAudioInput={handleAudioInput}
            loading={loading || documentLoading}
            language={language}
            onCloseUploadMenu={() => setShowUploadMenu(false)}
          />
        </div>
      </div>

      {/* Document Management Modal */}
      {showDocuments && documentUploaded && (
        <DocumentList
          documents={documents}
          selectedDocs={selectedDocs}
          onSelectDoc={(docs) => {
            setSelectedDocs(docs);
            setEntities(null); // Clear entities when selection changes
          }}
          onDeleteDoc={handleDeleteDocument}
          onAnalyze={handleAnalyzeDocument}
          searchQuery={docSearchQuery}
          onSearchChange={(query) => {
            setDocSearchQuery(query);
            loadDocuments(sessionId);
          }}
          onClose={() => setShowDocuments(false)}
          entities={entities}
          onExtractEntities={handleExtractEntities}
          extractingEntities={extractingEntities}
        />
      )}

      {/* Toast Notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Legal Analysis View */}
      {showAnalysis && legalAnalysis && (
        <LegalAnalysisView
          analysis={legalAnalysis}
          onClose={() => setShowAnalysis(false)}
        />
      )}
    </>
  );
}

export default ChatInterface;
