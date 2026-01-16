import React, { useState, useRef } from 'react';

function MessageInput({ onSend, disabled, onAttachClick, showUploadMenu, onFileUpload, loading }) {
  const [input, setInput] = useState('');
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      onFileUpload(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      alert('Image upload feature coming soon!');
      // onFileUpload(file); // Will be implemented when backend supports it
    } else {
      alert('Please upload an image file');
    }
  };

  return (
    <div className="input-wrapper">
      {showUploadMenu && (
        <div className="upload-menu">
          <label className="upload-menu-item">
            <span>📄</span>
            <span>Upload PDF</span>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange}
              ref={fileInputRef}
            />
          </label>
          <label className="upload-menu-item">
            <span>🖼️</span>
            <span>Upload Photo</span>
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleImageChange}
              ref={imageInputRef}
            />
          </label>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="input-form">
        <button 
          type="button" 
          className="attach-btn"
          onClick={onAttachClick}
        >
          +
        </button>
        
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Message MediSense AI..."
          disabled={disabled}
          className="message-input"
        />
        
        <button 
          type="submit" 
          disabled={disabled || !input.trim() || loading}
          className="send-btn"
        >
          {loading ? <span className="loading-spinner"></span> : '↑'}
        </button>
      </form>
    </div>
  );
}

export default MessageInput;
