const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  uploadDocument: async (file, sessionId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    const response = await fetch(`${API_BASE_URL}/upload-document?session_id=${sessionId}`, {
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
    formData.append('session_id', sessionId);

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
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message,
        language,
        structured_output: structuredOutput
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
      headers: { 'Content-Type': 'application/json' },
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
    
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error('Failed to get documents');
    }

    return response.json();
  },

  deleteDocument: async (sessionId, documentId) => {
    const response = await fetch(`${API_BASE_URL}/documents/${sessionId}/${documentId}`, {
      method: 'DELETE',
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
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to extract entities');
    }

    return response.json();
  },

  getHistory: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/history/${sessionId}`);

    if (!response.ok) {
      throw new Error('Failed to get history');
    }

    return response.json();
  },

  getAllSessions: async () => {
    const response = await fetch(`${API_BASE_URL}/sessions`);

    if (!response.ok) {
      throw new Error('Failed to get sessions');
    }

    return response.json();
  },

  createNewSession: async () => {
    const response = await fetch(`${API_BASE_URL}/sessions/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    return response.json();
  },

  deleteSession: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete session');
    }

    return response.json();
  },

  translateText: async (text, targetLanguage) => {
    const response = await fetch(`${API_BASE_URL}/translate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
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
