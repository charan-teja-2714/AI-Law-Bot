const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  uploadPDF: async (file, sessionId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    
    const response = await fetch(`${API_BASE_URL}/upload-pdf?session_id=${sessionId}`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  sendMessage: async (sessionId, message, role) => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message, role }),
    });
    return response.json();
  },

  generateQuestions: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/generate-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    });
    return response.json();
  },

  getHistory: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/history/${sessionId}`);
    return response.json();
  },
};
