import React from 'react';

function MessageList({ messages }) {
  const formatMessage = (content) => {
    // Convert **text** to bold
    let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points
    formatted = formatted.replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>');
    
    // Wrap consecutive list items in ul
    formatted = formatted.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
    
    return formatted;
  };

  return (
    <>
      {messages.map((msg, index) => (
        <div 
          key={index} 
          className={msg.role === 'user' ? 'message message-user' : 'message message-assistant'}
        >
          <div className="message-content">
            <div className="message-label">
              {msg.role === 'user' ? 'You' : 'MediSense AI'}
            </div>
            <div 
              className="message-text"
              dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
            />
          </div>
        </div>
      ))}
    </>
  );
}

export default MessageList;
