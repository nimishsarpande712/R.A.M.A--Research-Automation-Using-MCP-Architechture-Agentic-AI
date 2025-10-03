import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ResearchInterface.css';

const ResearchInterface = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [researchResults, setResearchResults] = useState(null);
  const [workspace, setWorkspace] = useState(null);
  const [mindmap, setMindmap] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:8000/api/research/query', {
        prompt: prompt.trim(),
        include_workspace: true,
        include_mindmap: true,
        include_audio: true
      });

      const data = response.data;
      setResearchResults(data.papers);
      setWorkspace(data.workspace);
      setMindmap(data.mindmap);
      setAudioUrl(data.audio_url);
    } catch (err) {
      console.error('Research query error:', err);
      if (err.response) {
        setError(err.response.data.detail || 'Failed to process research query.');
      } else if (err.request) {
        setError('Unable to connect to server. Please try again later.');
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearResults = () => {
    setResearchResults(null);
    setWorkspace(null);
    setMindmap(null);
    setAudioUrl(null);
    setPrompt('');
    setError('');
  };

  return (
    <div className="research-interface">
      <header className="research-header">
        <h1>RAMA Research Interface</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <div className="research-content">
        <div className="prompt-section">
          <h2>Research Query</h2>
          <form onSubmit={handleSubmit} className="prompt-form">
            <div className="input-group">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your research topic or question... (e.g., 'quantum computing in neural networks', 'neuromorphic computing applications', 'AI for scientific discovery')"
                className="prompt-input"
                rows={4}
                disabled={isLoading}
              />
            </div>
            {error && <div className="error-message">{error}</div>}
            <div className="form-actions">
              <button 
                type="submit" 
                className="search-btn" 
                disabled={isLoading || !prompt.trim()}
              >
                {isLoading ? 'Researching...' : 'Generate Research Workspace'}
              </button>
              {researchResults && (
                <button 
                  type="button" 
                  onClick={clearResults} 
                  className="clear-btn"
                >
                  Clear Results
                </button>
              )}
            </div>
          </form>
        </div>

        {isLoading && (
          <div className="loading-section">
            <div className="loading-spinner"></div>
            <p>Generating research workspace, analyzing papers, and creating mindmap...</p>
          </div>
        )}

        {researchResults && (
          <div className="results-section">
            <div className="results-grid">
              {/* Research Papers */}
              <div className="result-card papers-card">
                <h3>📚 Relevant Research Papers</h3>
                <div className="papers-list">
                  {researchResults.map(paper => (
                    <div key={paper.id} className="paper-item">
                      <div className="paper-header">
                        <h4>{paper.title}</h4>
                        <span className="relevance-score">{paper.relevance_score}% relevant</span>
                      </div>
                      <p className="authors">{paper.authors.join(', ')}</p>
                      <p className="abstract">{paper.abstract}</p>
                      <div className="paper-meta">
                        <span className="journal">{paper.journal} ({paper.year})</span>
                        <span className="citations">{paper.citations} citations</span>
                      </div>
                      <div className="keywords">
                        {paper.keywords.map(keyword => (
                          <span key={keyword} className="keyword-tag">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Workspace */}
              {workspace && (
                <div className="result-card workspace-card">
                  <h3>🔬 Research Workspace</h3>
                  <div className="workspace-info">
                    <h4>{workspace.name}</h4>
                    <p>Created: {new Date(workspace.created_at).toLocaleString()}</p>
                    <p>Collaborators: {workspace.collaborators}</p>
                    <p>Last Activity: {workspace.last_activity}</p>
                  </div>
                  
                  <div className="tools-section">
                    <h5>Research Tools</h5>
                    {workspace.tools.map(tool => (
                      <div key={tool.name} className="tool-item">
                        <span className="tool-name">{tool.name}</span>
                        <div className="tool-status">
                          <span className={`status ${tool.status}`}>{tool.status}</span>
                          <div className="progress-bar">
                            <div 
                              className="progress-fill" 
                              style={{width: `${tool.progress}%`}}
                            ></div>
                          </div>
                          <span className="progress-text">{tool.progress}%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="files-section">
                    <h5>Generated Files</h5>
                    {workspace.files.map(file => (
                      <div key={file.name} className="file-item">
                        <span className="file-name">{file.name}</span>
                        <span className="file-type">{file.type}</span>
                        <span className="file-size">{file.size}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Mindmap */}
              {mindmap && (
                <div className="result-card mindmap-card">
                  <h3>🧠 Research Mindmap</h3>
                  <div className="mindmap-container">
                    <svg width="100%" height="400" viewBox="0 0 600 400">
                      {/* Connections */}
                      {mindmap.connections.map((conn, index) => {
                        const fromNode = mindmap.nodes.find(n => n.id === conn.from_id);
                        const toNode = mindmap.nodes.find(n => n.id === conn.to_id);
                        if (!fromNode || !toNode) return null;
                        return (
                          <line
                            key={index}
                            x1={fromNode.x}
                            y1={fromNode.y}
                            x2={toNode.x}
                            y2={toNode.y}
                            stroke="#6B48FF"
                            strokeWidth="2"
                            opacity="0.6"
                          />
                        );
                      })}
                      
                      {/* Nodes */}
                      {mindmap.nodes.map(node => (
                        <g key={node.id}>
                          <circle
                            cx={node.x}
                            cy={node.y}
                            r={node.type === 'central' ? 30 : node.type === 'main' ? 20 : 15}
                            fill={node.type === 'central' ? '#6B48FF' : node.type === 'main' ? '#00C9A7' : '#3D3D5E'}
                            stroke="#E0E0E0"
                            strokeWidth="2"
                          />
                          <text
                            x={node.x}
                            y={node.y + 5}
                            textAnchor="middle"
                            fill="#E0E0E0"
                            fontSize={node.type === 'central' ? 12 : 10}
                            fontWeight={node.type === 'central' ? 'bold' : 'normal'}
                          >
                            {node.label.length > 12 ? node.label.substring(0, 12) + '...' : node.label}
                          </text>
                        </g>
                      ))}
                    </svg>
                  </div>
                </div>
              )}

              {/* Audio Summary */}
              {audioUrl && (
                <div className="result-card audio-card">
                  <h3>🎧 Audio Summary</h3>
                  <div className="audio-player">
                    <p>Research summary generated as audio</p>
                    <div className="mock-audio-player">
                      <div className="audio-controls">
                        <button className="play-btn">▶️</button>
                        <div className="audio-progress">
                          <div className="progress-track"></div>
                        </div>
                        <span className="audio-time">0:00 / 3:42</span>
                      </div>
                      <p className="audio-description">
                        "Based on your research query about {prompt}, I've found {researchResults.length} relevant papers 
                        with an average relevance score of {Math.round(researchResults.reduce((acc, p) => acc + p.relevance_score, 0) / researchResults.length)}%. 
                        Key themes include quantum computing applications, neural network optimization, and emerging research methodologies..."
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchInterface;
