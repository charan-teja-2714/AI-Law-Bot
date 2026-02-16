import React, { useState } from 'react';
import EntityView from './EntityView';

function DocumentList({ 
  documents, 
  selectedDocs, 
  onSelectDoc, 
  onDeleteDoc, 
  onAnalyze,
  searchQuery,
  onSearchChange,
  onClose,
  entities,
  onExtractEntities,
  extractingEntities,
  analyzingDocument
}) {
  const [selectAll, setSelectAll] = useState(false);

  const handleSelectAll = () => {
    if (selectAll) {
      onSelectDoc([]);
    } else {
      onSelectDoc(documents.map(doc => doc.document_id));
    }
    setSelectAll(!selectAll);
  };

  const handleSelectDoc = (docId) => {
    if (selectedDocs.includes(docId)) {
      onSelectDoc(selectedDocs.filter(id => id !== docId));
    } else {
      onSelectDoc([...selectedDocs, docId]);
    }
  };

  const handleCardClick = (docId, e) => {
    // Don't toggle if clicking delete button
    if (e.target.closest('.doc-delete-btn')) {
      return;
    }
    handleSelectDoc(docId);
  };

  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return date.toLocaleString();
    } catch {
      return dateStr;
    }
  };

  const getDocIcon = (type) => {
    if (type === 'pdf') return '📄';
    if (type === 'audio') return '🎵';
    if (type === 'video') return '🎬';
    return '📎';
  };

  return (
    <div className="document-modal-overlay" onClick={onClose}>
      <div className="document-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="document-modal-header">
          <h2>📁 Documents ({documents.length})</h2>
          <button className="close-modal-btn" onClick={onClose}>✕</button>
        </div>
        
        <div className="document-list-header">
          <input
            type="text"
            placeholder="🔍 Search documents..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="doc-search-input"
          />
          <div className="doc-actions">
            <label className="select-all-label">
              <input type="checkbox" checked={selectAll} onChange={handleSelectAll} />
              <span>Select All</span>
            </label>
            <button
              className="extract-entities-btn"
              onClick={onExtractEntities}
              disabled={extractingEntities || selectedDocs.length === 0}
            >
              {extractingEntities ? '⏳ Extracting...' : `🔍 Extract Entities (${selectedDocs.length})`}
            </button>
            <button
              className="analyze-selected-btn"
              onClick={onAnalyze}
              disabled={analyzingDocument || selectedDocs.length === 0}
            >
              {analyzingDocument ? '⏳ Analyzing...' : `📊 Analyze (${selectedDocs.length})`}
            </button>
          </div>
        </div>

        <div className="documents-grid">
          {documents.length === 0 ? (
            <div className="no-documents">No documents uploaded</div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.document_id}
                className={`document-card ${selectedDocs.includes(doc.document_id) ? 'selected' : ''}`}
                onClick={(e) => handleCardClick(doc.document_id, e)}
              >
                <div className="doc-card-header">
                  <input
                    type="checkbox"
                    checked={selectedDocs.includes(doc.document_id)}
                    onChange={() => handleSelectDoc(doc.document_id)}
                    className="doc-checkbox"
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span className="doc-icon">{getDocIcon(doc.document_type)}</span>
                </div>
                <div className="doc-card-body">
                  <div className="doc-name" title={doc.document_name}>
                    {doc.document_name}
                  </div>
                  <div className="doc-meta">
                    <span className="doc-type">{doc.document_type.toUpperCase()}</span>
                    <span className="doc-date">{formatDate(doc.uploaded_at)}</span>
                  </div>
                </div>
                <div className="doc-card-footer">
                  <button
                    className="doc-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteDoc(doc.document_id);
                    }}
                    title="Delete document"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
        
        {entities && (
          <div className="entities-section" key={JSON.stringify(selectedDocs)}>
            <h3 className="entities-title">🏷️ Extracted Legal Entities</h3>
            <EntityView entities={entities} />
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentList;
