import React, { useState, useRef, useEffect } from 'react';
import AudioRecorder from './AudioRecorder';

function MessageInput({
  onSend,
  disabled,
  onAttachClick,
  showUploadMenu,
  onDocumentUpload,
  onAudioVideoUpload,
  onAudioInput,
  loading,
  language,
  onCloseUploadMenu,
  transcribedText,
  onTranscriptionComplete
}) {
  const [input, setInput] = useState('');
  const [transcribing, setTranscribing] = useState(false);
  const pdfInputRef = useRef(null);
  const audioVideoInputRef = useRef(null);
  const uploadMenuRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSend(input);
      setInput('');
      if (onTranscriptionComplete) {
        onTranscriptionComplete();
      }
    }
  };

  useEffect(() => {
    if (transcribedText) {
      setInput(transcribedText);
    }
  }, [transcribedText]);

  const handleAudioRecordingComplete = async (file) => {
    setTranscribing(true);
    try {
      // console.log('Starting transcription...');
      const result = await onAudioInput(file, language);
      // console.log('Transcription result:', result);
      if (result && result.text && result.text.trim()) {
        setInput(result.text.trim());
        // console.log('Text set to input:', result.text);
      } else {
        // console.warn('No text in result:', result);
        alert('Could not transcribe audio. Please speak clearly and try again, or ensure your microphone is working properly.');
      }
    } catch (error) {
      // console.error('Transcription error:', error);
      alert('Transcription failed. Please try again.');
    } finally {
      setTranscribing(false);
    }
  };

  const handlePDFChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'application/pdf') {
      onDocumentUpload(file);
    } else {
      alert('Please upload a PDF file');
    }
    e.target.value = '';
  };

  const handleAudioVideoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const validTypes = [
        'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/m4a', 'audio/ogg',
        'video/mp4', 'video/avi', 'video/quicktime', 'video/webm', 'video/x-matroska'
      ];

      const validExtensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4', '.avi', '.mov', '.mkv', '.webm'];
      const fileExt = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

      if (validTypes.includes(file.type) || validExtensions.includes(fileExt)) {
        onAudioVideoUpload(file);
      } else {
        alert('Please upload a valid audio or video file');
      }
    }
    e.target.value = '';
  };

  const placeholderText = {
    en: 'Ask a legal question...',
    hi: 'कानूनी सवाल पूछें...',
    te: 'చట్టపరమైన ప్రశ్న అడగండి...',
    ta: 'சட்ட கேள்வி கேளுங்கள்...'
  };

  // Close upload menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (uploadMenuRef.current && !uploadMenuRef.current.contains(event.target)) {
        // Check if click is not on the attach button
        const attachBtn = event.target.closest('.attach-btn');
        if (!attachBtn) {
          onCloseUploadMenu();
        }
      }
    };

    if (showUploadMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUploadMenu, onCloseUploadMenu]);

  return (
    <div className="input-wrapper">
      {showUploadMenu && (
        <div className="upload-menu" ref={uploadMenuRef}>
          <label className="upload-menu-item">
            <span>📄</span>
            <span>Upload PDF</span>
            <input
              type="file"
              accept=".pdf"
              onChange={handlePDFChange}
              ref={pdfInputRef}
              style={{ display: 'none' }}
            />
          </label>
          <label className="upload-menu-item">
            <span>🎤</span>
            <span>Upload Audio/Video</span>
            <input
              type="file"
              accept=".mp3,.wav,.m4a,.flac,.ogg,.mp4,.avi,.mov,.mkv,.webm"
              onChange={handleAudioVideoChange}
              ref={audioVideoInputRef}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      )}

      <form onSubmit={handleSubmit} className="input-form">
        <button
          type="button"
          className="attach-btn"
          onClick={onAttachClick}
          title="Upload document or audio/video"
        >
          📎
        </button>

        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={transcribing ? 'Transcribing...' : (placeholderText[language] || placeholderText.en)}
          disabled={disabled || transcribing}
          className="message-input"
        />

        <AudioRecorder
          onRecordingComplete={handleAudioRecordingComplete}
          disabled={disabled || loading || transcribing}
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
