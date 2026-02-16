import React from 'react';

const EntityView = ({ entities, documentName }) => {
  if (!entities) {
    return <div className="no-entities">No entities extracted</div>;
  }

  const { people, legal_sections } = entities;

  return (
    <div className="entity-view">
      {/* Legal Sections */}
      {legal_sections && (
        <div className="entity-section">
          <h3 className="entity-section-title">⚖️ Legal Sections</h3>
          
          {legal_sections.ipc && legal_sections.ipc.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">IPC Sections:</div>
              <div className="entity-tags">
                {legal_sections.ipc.map((section, idx) => (
                  <span key={idx} className="entity-tag ipc-tag">{section}</span>
                ))}
              </div>
            </div>
          )}

          {legal_sections.crpc && legal_sections.crpc.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">CrPC Sections:</div>
              <div className="entity-tags">
                {legal_sections.crpc.map((section, idx) => (
                  <span key={idx} className="entity-tag crpc-tag">{section}</span>
                ))}
              </div>
            </div>
          )}

          {legal_sections.bns && legal_sections.bns.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">BNS Sections:</div>
              <div className="entity-tags">
                {legal_sections.bns.map((section, idx) => (
                  <span key={idx} className="entity-tag bns-tag">{section}</span>
                ))}
              </div>
            </div>
          )}

          {legal_sections.other && legal_sections.other.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Other Sections:</div>
              <div className="entity-tags">
                {legal_sections.other.map((section, idx) => (
                  <span key={idx} className="entity-tag other-tag">{section}</span>
                ))}
              </div>
            </div>
          )}
          
          {(!legal_sections.ipc || legal_sections.ipc.length === 0) &&
           (!legal_sections.crpc || legal_sections.crpc.length === 0) &&
           (!legal_sections.bns || legal_sections.bns.length === 0) &&
           (!legal_sections.other || legal_sections.other.length === 0) && (
            <div className="no-entities" style={{padding: '12px', textAlign: 'center', color: '#7f8c8d'}}>
              No legal sections found in document
            </div>
          )}
        </div>
      )}

      {/* People Section */}
      {people && (
        <div className="entity-section">
          <h3 className="entity-section-title">👥 People Involved</h3>
          
          {people.complainants && people.complainants.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Complainants:</div>
              <ul className="entity-list">
                {people.complainants.map((person, idx) => (
                  <li key={idx}>{person}</li>
                ))}
              </ul>
            </div>
          )}

          {people.accused && people.accused.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Accused:</div>
              <ul className="entity-list">
                {people.accused.map((person, idx) => (
                  <li key={idx}>{person}</li>
                ))}
              </ul>
            </div>
          )}

          {people.witnesses && people.witnesses.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Witnesses:</div>
              <ul className="entity-list">
                {people.witnesses.map((person, idx) => (
                  <li key={idx}>{person}</li>
                ))}
              </ul>
            </div>
          )}

          {people.lawyers && people.lawyers.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Lawyers:</div>
              <ul className="entity-list">
                {people.lawyers.map((person, idx) => (
                  <li key={idx}>{person}</li>
                ))}
              </ul>
            </div>
          )}

          {people.officers && people.officers.length > 0 && (
            <div className="entity-group">
              <div className="entity-label">Officers:</div>
              <ul className="entity-list">
                {people.officers.map((person, idx) => (
                  <li key={idx}>{person}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EntityView;
