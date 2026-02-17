import React, { useState } from 'react';

function MessageList({ messages, isLoading }) {
  const [expandedCases, setExpandedCases] = useState({});
  const highlightLegalTerms = (text) => {
    if (!text) return text;

    // Highlight IPC, BNS, CrPC sections with bold only
    text = text.replace(
      /\b(IPC|BNS|CrPC)\s+(Section\s+)?(\d+[A-Z]?)/gi,
      '<strong>$1 Section $3</strong>'
    );

    // Highlight case numbers with bold only
    text = text.replace(
      /\b(FIR|Case)\s+(No\.|Number)?:?\s*([A-Z0-9\-\/]+)/gi,
      '<strong>$1 $3</strong>'
    );

    // Highlight important legal terms with bold only
    const legalTerms = [
      'cognizable', 'non-cognizable', 'bailable', 'non-bailable',
      'compoundable', 'punishment', 'imprisonment', 'fine',
      'complainant', 'accused', 'witness', 'jurisdiction'
    ];

    legalTerms.forEach(term => {
      const regex = new RegExp(`\\b(${term})\\b`, 'gi');
      text = text.replace(regex, '<strong>$1</strong>');
    });

    return text;
  };

  const formatMessage = (content) => {
    if (!content) return '';

    let formatted = content;

    // Convert **text** to bold
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Remove duplicate headings (e.g., "🔹 Similar Landmark Cases" appearing twice)
    formatted = formatted.replace(/(🔹\s*[^\n]+)\n+\1/g, '$1');
    
    // Convert 🔹 headings to styled headings
    formatted = formatted.replace(/🔹\s*(.+)/g, '<h3 class="section-heading">$1</h3>');

    // Apply legal term highlighting
    formatted = highlightLegalTerms(formatted);

    // Split into lines for processing
    const lines = formatted.split('\n');
    const htmlLines = [];
    let inList = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();

      if (!line) {
        // Empty line = paragraph break
        if (inList) {
          htmlLines.push('</ul>');
          inList = false;
        }
        htmlLines.push('<div class="paragraph-break"></div>');
        continue;
      }

      // Bullet points
      if (/^[•\-\*]\s+/.test(line)) {
        if (!inList) {
          htmlLines.push('<ul>');
          inList = true;
        }
        htmlLines.push('<li>' + line.replace(/^[•\-\*]\s+/, '') + '</li>');
        continue;
      }

      // Numbered lists (1. 2. 3. etc)
      if (/^\d+\.\s+/.test(line)) {
        if (!inList) {
          htmlLines.push('<ul class="numbered-list">');
          inList = true;
        }
        htmlLines.push('<li>' + line.replace(/^\d+\.\s+/, '') + '</li>');
        continue;
      }

      // Close any open list
      if (inList) {
        htmlLines.push('</ul>');
        inList = false;
      }

      // Regular line - just wrap in a div
      htmlLines.push('<div class="text-line">' + line + '</div>');
    }

    // Close any remaining list
    if (inList) {
      htmlLines.push('</ul>');
    }

    return htmlLines.join('');
  };

  return (
    <div className="message-list">
      {messages.map((msg, index) => {
        if (msg.role === 'assistant') {
          // console.log(`[MSG ${index}] similar_cases:`, msg.similar_cases);
        }
        return (
        <div
          key={index}
          className={`message-row ${msg.role === 'user' ? 'message-row-user' : 'message-row-assistant'}`}
        >
          {msg.role === 'assistant' && (
            <div className="message-avatar ai-avatar">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
              </svg>
            </div>
          )}

          <div className={`message-bubble ${msg.role === 'user' ? 'message-bubble-user' : 'message-bubble-assistant'}`}>
            <div
              className="message-text"
              dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
            />
            
            {msg.role === 'assistant' && msg.similar_cases && (
              <div className="similar-cases-section">
                <button 
                  className="view-cases-btn"
                  onClick={() => setExpandedCases(prev => ({...prev, [index]: !prev[index]}))}
                >
                  {expandedCases[index] ? '▼ Hide Similar Cases' : '▶ View Similar Cases'}
                </button>
                
                {expandedCases[index] && (
                  <div 
                    className="similar-cases-content"
                    dangerouslySetInnerHTML={{ __html: formatMessage(msg.similar_cases) }}
                  />
                )}
              </div>
            )}
          </div>

          {msg.role === 'user' && (
            <div className="message-avatar user-avatar">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
          )}
        </div>
      );})}

      {isLoading && (
        <div className="message-row message-row-assistant">
          <div className="message-avatar ai-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
            </svg>
          </div>

          <div className="message-bubble message-bubble-assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MessageList;
