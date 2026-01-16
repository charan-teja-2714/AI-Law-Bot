import React from 'react';

function QuestionsDialog({ questions, onClose }) {
  const formatQuestions = (text) => {
    // Split by lines and filter out empty lines
    const lines = text.split('\n').filter(line => line.trim());
    
    // Convert lines starting with -, *, or • to list items
    const formatted = lines.map(line => {
      const trimmed = line.trim();
      if (trimmed.match(/^[-*•]\s+/)) {
        return trimmed.replace(/^[-*•]\s+/, '');
      }
      return trimmed;
    }).filter(line => line);
    
    return formatted;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>🩺 Questions to Ask Your Doctor</h2>
        <div className="questions-text">
          <ul>
            {formatQuestions(questions).map((question, index) => (
              <li key={index}>{question}</li>
            ))}
          </ul>
        </div>
        <button onClick={onClose} className="modal-close-btn">
          Close
        </button>
      </div>
    </div>
  );
}

export default QuestionsDialog;
