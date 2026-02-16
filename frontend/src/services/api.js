const API_BASE_URL = 'http://localhost:8000/api';

// Helper to get session token
const getSessionToken = () => localStorage.getItem('session_token');

// Helper to add auth header
const getHeaders = (includeContentType = true) => {
  const headers = {};
  const token = getSessionToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (includeContentType) headers['Content-Type'] = 'application/json';
  return headers;
};

export const api = {
  uploadDocument: async (file, sessionId) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/upload-document?session_id=${sessionId}&session_token=${token}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload document');
    }

    return response.json();
  },

  uploadAudioVideo: async (file, sessionId) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-audio-video?session_id=${sessionId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload audio/video');
    }

    return response.json();
  },

  sendMessage: async (sessionId, message, language = 'en', structuredOutput = false) => {
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        message,
        language,
        structured_output: structuredOutput,
        session_token: token
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  },

  analyzeDocument: async (sessionId, documentIds = null) => {
    const body = documentIds ? { document_ids: documentIds } : {};
    const response = await fetch(`${API_BASE_URL}/analyze-document?session_id=${sessionId}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to analyze document');
    }

    const data = await response.json();
    return data.analysis;
  },

  getDocuments: async (sessionId, search = null) => {
    const url = search 
      ? `${API_BASE_URL}/documents/${sessionId}?search=${encodeURIComponent(search)}`
      : `${API_BASE_URL}/documents/${sessionId}`;
    
    const response = await fetch(url, { headers: getHeaders(false) });

    if (!response.ok) {
      throw new Error('Failed to get documents');
    }

    return response.json();
  },

  deleteDocument: async (sessionId, documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${sessionId}/${documentId}`, {
      method: 'DELETE',
      headers: getHeaders(false)
    });

    if (!response.ok) {
      throw new Error('Failed to delete document');
    }

    return response.json();
  },

  extractEntities: async (sessionId, documentIds = null) => {
    const body = documentIds ? { document_ids: documentIds } : {};
    const response = await fetch(`${API_BASE_URL}/extract-entities?session_id=${sessionId}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to extract entities');
    }

    return response.json();
  },

  getHistory: async (sessionId) => {
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/history/${sessionId}?session_token=${token}`, {
      headers: getHeaders(false)
    });

    if (!response.ok) {
      throw new Error('Failed to get history');
    }

    return response.json();
  },

  getAllSessions: async () => {
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/sessions?session_token=${token}`, {
      headers: getHeaders(false)
    });

    if (!response.ok) {
      throw new Error('Failed to get sessions');
    }

    return response.json();
  },

  createNewSession: async () => {
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/sessions/new`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ session_token: token }),
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    return response.json();
  },

  deleteSession: async (sessionId) => {
    const token = getSessionToken();
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}?session_token=${token}`, {
      method: 'DELETE',
      headers: getHeaders(false)
    });

    if (!response.ok) {
      throw new Error('Failed to delete session');
    }

    return response.json();
  },

  translateText: async (text, targetLanguage) => {
    const response = await fetch(`${API_BASE_URL}/translate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        text,
        target_language: targetLanguage
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to translate text');
    }

    return response.json();
  },

  transcribeAudio: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/transcribe-audio`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to transcribe audio');
    }

    return response.json();
  },
};
