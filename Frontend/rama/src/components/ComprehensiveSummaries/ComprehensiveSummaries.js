import React, { useState } from 'react';
import './ComprehensiveSummaries.css';

const ComprehensiveSummaries = ({ summariesData, onDocumentSelect }) => {
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  if (!summariesData) {
    return (
      <div className="summaries-placeholder">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Generating Comprehensive Summaries...</p>
        </div>
      </div>
    );
  }

  const handleDocumentClick = (document) => {
    setSelectedDocument(document);
    if (onDocumentSelect) {
      onDocumentSelect(document);
    }
  };

  return (
    <div className="comprehensive-summaries-container">
      <div className="summaries-header">
        <h2>📚 Comprehensive Research Summaries</h2>
        <div className="tab-navigation">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Topic Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            Document Summaries
          </button>
          <button 
            className={`tab-btn ${activeTab === 'synthesis' ? 'active' : ''}`}
            onClick={() => setActiveTab('synthesis')}
          >
            Synthesis & Gaps
          </button>
        </div>
      </div>

      <div className="summaries-content">
        {activeTab === 'overview' && summariesData.topic_overview && (
          <div className="topic-overview-section">
            <div className="overview-header">
              <h3>{summariesData.topic_overview.topic}</h3>
              <span className="topic-badge">Research Topic</span>
            </div>
            
            <div className="overview-content">
              <div className="overview-description">
                <p>{summariesData.topic_overview.overview}</p>
              </div>
              
              <div className="overview-grid">
                <div className="overview-card">
                  <h4>🔑 Key Concepts</h4>
                  <ul>
                    {summariesData.topic_overview.key_concepts?.map((concept, index) => (
                      <li key={index}>{concept}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="overview-card">
                  <h4>⚡ Current Trends</h4>
                  <ul>
                    {summariesData.topic_overview.current_trends?.map((trend, index) => (
                      <li key={index}>{trend}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="overview-card">
                  <h4>🚧 Main Challenges</h4>
                  <ul>
                    {summariesData.topic_overview.main_challenges?.map((challenge, index) => (
                      <li key={index}>{challenge}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="overview-card">
                  <h4>🚀 Future Directions</h4>
                  <ul>
                    {summariesData.topic_overview.future_directions?.map((direction, index) => (
                      <li key={index}>{direction}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {summariesData.topic_overview.related_fields && (
                <div className="related-fields">
                  <h4>🔗 Related Fields</h4>
                  <div className="fields-tags">
                    {summariesData.topic_overview.related_fields.map((field, index) => (
                      <span key={index} className="field-tag">{field}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'documents' && summariesData.document_summaries && (
          <div className="document-summaries-section">
            <div className="documents-grid">
              {summariesData.document_summaries.map((document, index) => (
                <div 
                  key={index} 
                  className={`document-card ${selectedDocument?.paper_id === document.paper_id ? 'selected' : ''}`}
                  onClick={() => handleDocumentClick(document)}
                >
                  <div className="document-header">
                    <h4>{document.title}</h4>
                    <span className="paper-id">ID: {document.paper_id}</span>
                  </div>
                  
                  <div className="document-summary">
                    <p>{document.summary}</p>
                  </div>
                  
                  <div className="document-details">
                    <div className="key-findings">
                      <h5>📈 Key Findings</h5>
                      <ul>
                        {document.key_findings?.slice(0, 2).map((finding, fidx) => (
                          <li key={fidx}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="methodology-preview">
                      <h5>⚙️ Methodology</h5>
                      <p>{document.methodology?.substring(0, 100)}...</p>
                    </div>
                  </div>
                  
                  <div className="document-footer">
                    <span className="significance-badge">
                      {document.significance ? 'High Impact' : 'Standard Impact'}
                    </span>
                    <button className="view-details-btn">
                      View Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            {selectedDocument && (
              <div className="selected-document-details">
                <h3>📄 Document Details: {selectedDocument.title}</h3>
                
                <div className="details-sections">
                  <div className="detail-section">
                    <h4>Complete Summary</h4>
                    <p>{selectedDocument.summary}</p>
                  </div>
                  
                  <div className="detail-section">
                    <h4>All Key Findings</h4>
                    <ul>
                      {selectedDocument.key_findings?.map((finding, index) => (
                        <li key={index}>{finding}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="detail-section">
                    <h4>Methodology</h4>
                    <p>{selectedDocument.methodology}</p>
                  </div>
                  
                  {selectedDocument.limitations && (
                    <div className="detail-section">
                      <h4>Limitations</h4>
                      <ul>
                        {selectedDocument.limitations.map((limitation, index) => (
                          <li key={index}>{limitation}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="detail-section">
                    <h4>Research Significance</h4>
                    <p>{selectedDocument.significance}</p>
                  </div>
                </div>
                
                <button 
                  className="close-details-btn"
                  onClick={() => setSelectedDocument(null)}
                >
                  Close Details
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'synthesis' && (
          <div className="synthesis-section">
            <div className="synthesis-content">
              <div className="synthesis-overview">
                <h3>🔬 Research Synthesis</h3>
                <div className="synthesis-text">
                  <p>{summariesData.synthesis}</p>
                </div>
              </div>
              
              <div className="research-gaps">
                <h3>🔍 Identified Research Gaps</h3>
                <div className="gaps-grid">
                  {summariesData.research_gaps?.map((gap, index) => (
                    <div key={index} className="gap-card">
                      <div className="gap-icon">⚠️</div>
                      <div className="gap-content">
                        <p>{gap}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="recommendations">
                <h3>💡 Research Recommendations</h3>
                <div className="recommendations-list">
                  <div className="recommendation-item">
                    <h4>📊 Methodological Improvements</h4>
                    <p>Focus on developing standardized evaluation metrics and cross-domain validation studies.</p>
                  </div>
                  <div className="recommendation-item">
                    <h4>🌐 Interdisciplinary Collaboration</h4>
                    <p>Encourage collaboration between different research domains to address complex challenges.</p>
                  </div>
                  <div className="recommendation-item">
                    <h4>📈 Longitudinal Studies</h4>
                    <p>Implement long-term validation studies to assess real-world impact and sustainability.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComprehensiveSummaries;
