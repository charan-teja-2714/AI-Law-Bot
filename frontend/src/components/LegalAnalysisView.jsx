import React from 'react';

function LegalAnalysisView({ analysis, onClose }) {
  if (!analysis) return null;

  return (
    <div className="analysis-modal-overlay" onClick={onClose}>
      <div className="analysis-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="legal-analysis-container">
      <div className="analysis-header">
        <h2>Legal Analysis Report</h2>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      <div className="analysis-content">
        {/* Document Type */}
        <div className="analysis-section">
          <div className="section-label">Document Type</div>
          <div className="section-value">{analysis.document_type || 'N/A'}</div>
        </div>

        {/* Case Summary */}
        <div className="analysis-section">
          <div className="section-label">Case Summary</div>
          <div className="section-value summary-text">{analysis.case_summary || 'N/A'}</div>
        </div>

        {/* IPC Sections */}
        {analysis.applicable_ipc_sections && analysis.applicable_ipc_sections.length > 0 && (
          <div className="analysis-section">
            <div className="section-label">Applicable IPC Sections</div>
            <div className="sections-list">
              {analysis.applicable_ipc_sections.map((section, idx) => (
                <div key={idx} className="section-card">
                  <div className="section-number">Section {section.section}</div>
                  <div className="section-desc">{section.description}</div>
                  <div className="section-relevance">
                    <strong>Relevance:</strong> {section.relevance}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CrPC Sections */}
        {analysis.applicable_crpc_sections && analysis.applicable_crpc_sections.length > 0 && (
          <div className="analysis-section">
            <div className="section-label">Applicable CrPC Sections</div>
            <div className="sections-list">
              {analysis.applicable_crpc_sections.map((section, idx) => (
                <div key={idx} className="section-card">
                  <div className="section-number">Section {section.section}</div>
                  <div className="section-desc">{section.description}</div>
                  <div className="section-relevance">
                    <strong>Relevance:</strong> {section.relevance}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* BNS Sections */}
        {analysis.applicable_bns_sections && analysis.applicable_bns_sections.length > 0 && (
          <div className="analysis-section">
            <div className="section-label">Applicable BNS Sections</div>
            <div className="sections-list">
              {analysis.applicable_bns_sections.map((section, idx) => (
                <div key={idx} className="section-card">
                  <div className="section-number">Section {section.section}</div>
                  <div className="section-desc">{section.description}</div>
                  <div className="section-relevance">
                    <strong>Relevance:</strong> {section.relevance}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Legal Consequences */}
        <div className="analysis-section">
          <div className="section-label">Legal Consequences</div>
          <div className="section-value consequence-text">{analysis.legal_consequences || 'N/A'}</div>
        </div>

        {/* Similar Cases */}
        {analysis.similar_cases && analysis.similar_cases.length > 0 && (
          <div className="analysis-section">
            <div className="section-label">Similar Cases</div>
            <ul className="similar-cases-list">
              {analysis.similar_cases.map((caseRef, idx) => (
                <li key={idx}>{caseRef}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Next Steps */}
        {analysis.recommended_next_steps && analysis.recommended_next_steps.length > 0 && (
          <div className="analysis-section">
            <div className="section-label">Recommended Next Steps</div>
            <ol className="next-steps-list">
              {analysis.recommended_next_steps.map((step, idx) => (
                <li key={idx}>{step}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
        </div>
      </div>
    </div>
  );
}

export default LegalAnalysisView;
