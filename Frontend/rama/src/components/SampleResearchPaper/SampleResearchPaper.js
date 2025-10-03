import React, { useState } from 'react';
import './SampleResearchPaper.css';

const SampleResearchPaper = ({ paperData, onDownload, onExport }) => {
  const [viewMode, setViewMode] = useState('preview'); // 'preview', 'outline', 'full'
  const [selectedSection, setSelectedSection] = useState('introduction');

  if (!paperData) {
    return (
      <div className="paper-placeholder">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Generating Sample Research Paper...</p>
        </div>
      </div>
    );
  }

  const handleDownloadPdf = () => {
    if (onDownload) {
      onDownload('pdf');
    }
    // In a real implementation, this would generate and download a PDF
    console.log('Downloading PDF...');
  };

  const handleDownloadWord = () => {
    if (onDownload) {
      onDownload('docx');
    }
    // In a real implementation, this would generate and download a Word document
    console.log('Downloading Word document...');
  };

  const handleExportLatex = () => {
    if (onExport) {
      onExport('latex');
    }
    // In a real implementation, this would export to LaTeX format
    console.log('Exporting to LaTeX...');
  };

  const sections = [
    { id: 'abstract', title: 'Abstract', icon: '📄' },
    { id: 'introduction', title: 'Introduction', icon: '🚀' },
    { id: 'literature_review', title: 'Literature Review', icon: '📚' },
    { id: 'methodology', title: 'Methodology', icon: '⚙️' },
    { id: 'results', title: 'Results', icon: '📊' },
    { id: 'discussion', title: 'Discussion', icon: '💭' },
    { id: 'conclusion', title: 'Conclusion', icon: '🎯' },
    { id: 'references', title: 'References', icon: '🔗' }
  ];

  const renderSection = (section) => {
    if (!section) return null;

    return (
      <div className="paper-section">
        <h3 className="section-title">{section.title}</h3>
        <div className="section-content">
          {section.content && <p>{section.content}</p>}
          {section.subsections && section.subsections.map((subsection, index) => (
            <div key={index} className="subsection">
              <h4 className="subsection-title">{subsection.title}</h4>
              <p>{subsection.content}</p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderFullPaper = () => (
    <div className="full-paper">
      <div className="paper-header">
        <h1 className="paper-title">{paperData.title}</h1>
        <div className="paper-meta">
          <div className="meta-item">
            <strong>Word Count:</strong> {paperData.word_count || 'N/A'}
          </div>
          <div className="meta-item">
            <strong>Generated:</strong> {new Date(paperData.generated_at).toLocaleDateString()}
          </div>
        </div>
        <div className="keywords">
          <strong>Keywords:</strong> {paperData.keywords?.join(', ')}
        </div>
      </div>

      <div className="abstract-section">
        <h2>Abstract</h2>
        <p>{paperData.abstract}</p>
      </div>

      {renderSection(paperData.introduction)}
      {renderSection(paperData.literature_review)}
      {renderSection(paperData.methodology)}
      {paperData.results && renderSection(paperData.results)}
      {paperData.discussion && renderSection(paperData.discussion)}
      {renderSection(paperData.conclusion)}

      <div className="references-section">
        <h2>References</h2>
        <ol className="references-list">
          {paperData.references?.map((reference, index) => (
            <li key={index} className="reference-item">
              {reference}
            </li>
          ))}
        </ol>
      </div>
    </div>
  );

  const renderOutline = () => (
    <div className="paper-outline">
      <h3>📋 Paper Structure Outline</h3>
      <div className="outline-tree">
        <div className="outline-item">
          <span className="outline-title">📄 {paperData.title}</span>
          <div className="outline-meta">Total: {paperData.word_count} words</div>
        </div>
        
        <div className="outline-section">
          <span className="section-indicator">📄 Abstract</span>
          <div className="word-count">{paperData.abstract?.length || 0} chars</div>
        </div>

        {paperData.introduction && (
          <div className="outline-section">
            <span className="section-indicator">🚀 Introduction</span>
            <div className="word-count">~{Math.floor((paperData.introduction.content?.length || 0) / 5)} words</div>
            {paperData.introduction.subsections && (
              <div className="outline-subsections">
                {paperData.introduction.subsections.map((sub, index) => (
                  <div key={index} className="outline-subsection">
                    <span>▸ {sub.title}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {paperData.literature_review && (
          <div className="outline-section">
            <span className="section-indicator">📚 Literature Review</span>
            <div className="word-count">~{Math.floor((paperData.literature_review.content?.length || 0) / 5)} words</div>
            {paperData.literature_review.subsections && (
              <div className="outline-subsections">
                {paperData.literature_review.subsections.map((sub, index) => (
                  <div key={index} className="outline-subsection">
                    <span>▸ {sub.title}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {paperData.methodology && (
          <div className="outline-section">
            <span className="section-indicator">⚙️ Methodology</span>
            <div className="word-count">~{Math.floor((paperData.methodology.content?.length || 0) / 5)} words</div>
            {paperData.methodology.subsections && (
              <div className="outline-subsections">
                {paperData.methodology.subsections.map((sub, index) => (
                  <div key={index} className="outline-subsection">
                    <span>▸ {sub.title}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="outline-section">
          <span className="section-indicator">🎯 Conclusion</span>
          <div className="word-count">~{Math.floor((paperData.conclusion?.content?.length || 0) / 5)} words</div>
        </div>

        <div className="outline-section">
          <span className="section-indicator">🔗 References</span>
          <div className="word-count">{paperData.references?.length || 0} refs</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="sample-research-paper-container">
      <div className="paper-header-controls">
        <div className="paper-info">
          <h2>📄 Sample Research Paper</h2>
          <div className="paper-stats">
            <span className="stat">
              📝 {paperData.word_count} words
            </span>
            <span className="stat">
              📚 {paperData.references?.length || 0} references
            </span>
            <span className="stat">
              🏷️ {paperData.keywords?.length || 0} keywords
            </span>
          </div>
        </div>

        <div className="view-controls">
          <div className="view-mode-selector">
            <button
              className={`mode-btn ${viewMode === 'outline' ? 'active' : ''}`}
              onClick={() => setViewMode('outline')}
            >
              📋 Outline
            </button>
            <button
              className={`mode-btn ${viewMode === 'preview' ? 'active' : ''}`}
              onClick={() => setViewMode('preview')}
            >
              👁️ Preview
            </button>
            <button
              className={`mode-btn ${viewMode === 'full' ? 'active' : ''}`}
              onClick={() => setViewMode('full')}
            >
              📄 Full Paper
            </button>
          </div>

          <div className="export-controls">
            <button className="export-btn pdf" onClick={handleDownloadPdf}>
              📄 Download PDF
            </button>
            <button className="export-btn word" onClick={handleDownloadWord}>
              📝 Download Word
            </button>
            <button className="export-btn latex" onClick={handleExportLatex}>
              🔧 Export LaTeX
            </button>
          </div>
        </div>
      </div>

      <div className="paper-content">
        {viewMode === 'outline' && renderOutline()}

        {viewMode === 'preview' && (
          <div className="paper-preview">
            <div className="section-navigator">
              <h4>Navigate Sections</h4>
              <div className="nav-buttons">
                {sections.map(section => (
                  <button
                    key={section.id}
                    className={`nav-btn ${selectedSection === section.id ? 'active' : ''}`}
                    onClick={() => setSelectedSection(section.id)}
                  >
                    <span className="nav-icon">{section.icon}</span>
                    {section.title}
                  </button>
                ))}
              </div>
            </div>

            <div className="section-preview">
              {selectedSection === 'abstract' && (
                <div className="preview-section">
                  <h3>📄 Abstract</h3>
                  <div className="section-content">
                    <p>{paperData.abstract}</p>
                  </div>
                </div>
              )}

              {selectedSection === 'introduction' && paperData.introduction && (
                <div className="preview-section">
                  {renderSection(paperData.introduction)}
                </div>
              )}

              {selectedSection === 'literature_review' && paperData.literature_review && (
                <div className="preview-section">
                  {renderSection(paperData.literature_review)}
                </div>
              )}

              {selectedSection === 'methodology' && paperData.methodology && (
                <div className="preview-section">
                  {renderSection(paperData.methodology)}
                </div>
              )}

              {selectedSection === 'conclusion' && paperData.conclusion && (
                <div className="preview-section">
                  {renderSection(paperData.conclusion)}
                </div>
              )}

              {selectedSection === 'references' && (
                <div className="preview-section">
                  <h3>🔗 References</h3>
                  <ol className="references-list">
                    {paperData.references?.map((reference, index) => (
                      <li key={index} className="reference-item">
                        {reference}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>
          </div>
        )}

        {viewMode === 'full' && (
          <div className="paper-full-view">
            {renderFullPaper()}
          </div>
        )}
      </div>

      <div className="paper-footer">
        <div className="paper-quality-indicators">
          <div className="quality-item">
            <span className="indicator-icon">✅</span>
            <span>Academic Structure</span>
          </div>
          <div className="quality-item">
            <span className="indicator-icon">📊</span>
            <span>Proper Citations</span>
          </div>
          <div className="quality-item">
            <span className="indicator-icon">🎯</span>
            <span>Research Methodology</span>
          </div>
          <div className="quality-item">
            <span className="indicator-icon">📝</span>
            <span>Complete Sections</span>
          </div>
        </div>
        
        <div className="generation-info">
          <p>
            <strong>Generated:</strong> {new Date(paperData.generated_at).toLocaleString()}
          </p>
          <p className="disclaimer">
            This is a sample research paper generated for demonstration purposes. 
            Use as a template and customize with your actual research content.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SampleResearchPaper;
