import React, { useState } from 'react';
import './IEEECitations.css';

const IEEECitations = ({ citationsData, onCitationCopy }) => {
  const [selectedFormat, setSelectedFormat] = useState('ieee');
  const [copiedCitation, setCopiedCitation] = useState(null);

  if (!citationsData) {
    return (
      <div className="citations-placeholder">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Generating IEEE Citations...</p>
        </div>
      </div>
    );
  }

  const handleCopyToClipboard = async (text, citationId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCitation(citationId);
      setTimeout(() => setCopiedCitation(null), 2000);
      
      if (onCitationCopy) {
        onCitationCopy(text, citationId);
      }
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const handleDownloadBibliography = () => {
    const content = citationsData.formatted_bibliography;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bibliography.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadBibtex = () => {
    const bibtexContent = citationsData.bibliography
      ?.map(entry => entry.bibtex_format)
      .join('\n\n') || '';
    
    const blob = new Blob([bibtexContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'references.bib';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatOptions = [
    { value: 'ieee', label: 'IEEE', icon: '📄' },
    { value: 'apa', label: 'APA', icon: '📋' },
    { value: 'mla', label: 'MLA', icon: '📑' },
    { value: 'bibtex', label: 'BibTeX', icon: '🔧' }
  ];

  const getCitationText = (entry) => {
    switch (selectedFormat) {
      case 'ieee':
        return entry.ieee_format;
      case 'apa':
        return entry.apa_format;
      case 'mla':
        return entry.mla_format;
      case 'bibtex':
        return entry.bibtex_format;
      default:
        return entry.ieee_format;
    }
  };

  return (
    <div className="ieee-citations-container">
      <div className="citations-header">
        <div className="header-content">
          <h2>📚 Automated IEEE Citations & Bibliography</h2>
          <div className="citations-stats">
            <div className="stat-item">
              <span className="stat-number">{citationsData.citation_count}</span>
              <span className="stat-label">Citations</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{citationsData.bibliography?.length || 0}</span>
              <span className="stat-label">References</span>
            </div>
          </div>
        </div>
        
        <div className="format-selector">
          <label>Citation Format:</label>
          <div className="format-buttons">
            {formatOptions.map(option => (
              <button
                key={option.value}
                className={`format-btn ${selectedFormat === option.value ? 'active' : ''}`}
                onClick={() => setSelectedFormat(option.value)}
              >
                <span className="format-icon">{option.icon}</span>
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="citations-content">
        <div className="citations-section">
          <div className="section-header">
            <h3>📖 Individual Citations</h3>
            <div className="section-actions">
              <button 
                className="action-btn primary"
                onClick={handleDownloadBibliography}
              >
                📥 Download Bibliography
              </button>
              {selectedFormat === 'bibtex' && (
                <button 
                  className="action-btn secondary"
                  onClick={handleDownloadBibtex}
                >
                  📥 Download .bib File
                </button>
              )}
            </div>
          </div>
          
          <div className="citations-list">
            {citationsData.bibliography?.map((entry, index) => (
              <div key={entry.id} className="citation-card">
                <div className="citation-header">
                  <div className="citation-number">
                    [{entry.id}]
                  </div>
                  <div className="citation-meta">
                    <span className="paper-id">Paper ID: {entry.paper_id}</span>
                    <span className="format-badge">{selectedFormat.toUpperCase()}</span>
                  </div>
                </div>
                
                <div className="citation-content">
                  <div className="citation-text">
                    {getCitationText(entry)}
                  </div>
                  
                  <div className="citation-actions">
                    <button
                      className={`copy-btn ${copiedCitation === entry.id ? 'copied' : ''}`}
                      onClick={() => handleCopyToClipboard(getCitationText(entry), entry.id)}
                    >
                      {copiedCitation === entry.id ? (
                        <>
                          <span>✓</span> Copied!
                        </>
                      ) : (
                        <>
                          <span>📋</span> Copy
                        </>
                      )}
                    </button>
                  </div>
                </div>
                
                {selectedFormat !== 'bibtex' && (
                  <div className="in-text-preview">
                    <label>In-text citation:</label>
                    <code className="in-text-code">
                      {citationsData.ieee_citations?.find(c => c.paper_id === entry.paper_id)?.in_text_format || `[${entry.id}]`}
                    </code>
                    <button
                      className="copy-inline-btn"
                      onClick={() => handleCopyToClipboard(
                        citationsData.ieee_citations?.find(c => c.paper_id === entry.paper_id)?.in_text_format || `[${entry.id}]`,
                        `inline-${entry.id}`
                      )}
                    >
                      📋
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="bibliography-section">
          <div className="section-header">
            <h3>📄 Complete Bibliography</h3>
            <button
              className="copy-all-btn"
              onClick={() => handleCopyToClipboard(citationsData.formatted_bibliography, 'bibliography')}
            >
              {copiedCitation === 'bibliography' ? '✓ Copied!' : '📋 Copy All'}
            </button>
          </div>
          
          <div className="bibliography-content">
            <div className="bibliography-text">
              <pre>{citationsData.formatted_bibliography}</pre>
            </div>
          </div>
        </div>

        <div className="citation-guidelines">
          <h3>📝 Citation Guidelines</h3>
          <div className="guidelines-grid">
            <div className="guideline-card">
              <h4>IEEE Format</h4>
              <p>IEEE citations use numbered references in square brackets. Author names are listed as "FirstName LastName".</p>
              <div className="example">
                <strong>Example:</strong><br />
                [1] J. Smith and M. Johnson, "Title of paper," Journal Name, vol. 1, no. 1, pp. 1-10, 2024.
              </div>
            </div>
            
            <div className="guideline-card">
              <h4>APA Format</h4>
              <p>APA uses author-date citation style with hanging indents for the reference list.</p>
              <div className="example">
                <strong>Example:</strong><br />
                Smith, J., & Johnson, M. (2024). Title of paper. Journal Name, 1(1), 1-10.
              </div>
            </div>
            
            <div className="guideline-card">
              <h4>MLA Format</h4>
              <p>MLA uses author-page citation style with hanging indents for the Works Cited page.</p>
              <div className="example">
                <strong>Example:</strong><br />
                Smith, John, and Mary Johnson. "Title of Paper." Journal Name, vol. 1, no. 1, 2024, pp. 1-10.
              </div>
            </div>
            
            <div className="guideline-card">
              <h4>BibTeX Format</h4>
              <p>BibTeX is a reference management format used with LaTeX. Each entry has a specific structure.</p>
              <div className="example">
                <strong>Example:</strong><br />
                @article{"{"}smith2024,<br />
                &nbsp;&nbsp;title={"{"}Title of Paper{"}"},<br />
                &nbsp;&nbsp;author={"{"}Smith, John and Johnson, Mary{"}"},<br />
                &nbsp;&nbsp;year={"{"}2024{"}"}<br />
                {"}"}
              </div>
            </div>
          </div>
        </div>

        <div className="export-options">
          <h3>💾 Export Options</h3>
          <div className="export-buttons">
            <button 
              className="export-btn txt"
              onClick={handleDownloadBibliography}
            >
              <span>📄</span>
              <div>
                <strong>Text File</strong>
                <small>Plain text bibliography</small>
              </div>
            </button>
            
            <button 
              className="export-btn bib"
              onClick={handleDownloadBibtex}
            >
              <span>🔧</span>
              <div>
                <strong>BibTeX File</strong>
                <small>For LaTeX documents</small>
              </div>
            </button>
            
            <button 
              className="export-btn json"
              onClick={() => {
                const jsonData = JSON.stringify(citationsData, null, 2);
                handleCopyToClipboard(jsonData, 'json');
              }}
            >
              <span>📊</span>
              <div>
                <strong>JSON Data</strong>
                <small>Structured data format</small>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IEEECitations;
